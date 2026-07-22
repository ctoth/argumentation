"""Replay the frozen frontier-v1 manifest and report pass rates per recal class.

The frontier-v1 manifest (tests/manifests/iccma2025-frontier-v1.json) freezes a
30-cell stratified sample of the 2025 uncapped run's timeout rows, each cell
tagged with its recalibration class ("hard", "boundary_melt", "melt").  This
script reruns exactly those (relative_path, subtrack) cells at an uncapped
size budget and emits solved/timeout counts per class plus deviations from the
frozen expectations.

Run all 30 rows:

    uv run scripts/run_frontier_v1.py --label frontier-v1-main-57da538 \
        --root C:/Users/Q/code/argumentation/data/iccma/2025

Chunk by subtrack (each chunk writes its own output file):

    uv run scripts/run_frontier_v1.py --label frontier-v1-main-57da538 \
        --subtrack DS-PR --root ...

Aggregate chunk outputs into one summary:

    uv run scripts/run_frontier_v1.py --aggregate out1.json out2.json ...

Rows are dispatched to a worker pool (``--jobs``, default min(8, cpu-2));
each row still runs in its own subprocess with its own wall-clock timeout,
and the output file lists rows in manifest order regardless of completion
order.  The scoreboard tolerates the CPU-contention noise this adds to
per-row elapsed times, but timing-sensitive gates should pass ``--jobs 1``
for contention-free serial timings.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.iccma_run_selected import run_selected  # noqa: E402

DEFAULT_MANIFEST = ROOT / "tests" / "manifests" / "iccma2025-frontier-v1.json"
DEFAULT_DATA_ROOT = ROOT / "data" / "iccma" / "2025"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "iccma" / "2025" / "runs"
CLASS_EXPECTED_STATUS = {
    "hard": "timeout",
    "boundary_melt": "solved",
    "melt": "solved",
}


def select_rows(
    rows: list[dict[str, Any]],
    *,
    subtracks: set[str] | None,
) -> list[dict[str, Any]]:
    return [
        row for row in rows if subtracks is None or str(row["subtrack"]) in subtracks
    ]


def default_jobs() -> int:
    return max(1, min(8, (os.cpu_count() or 1) - 2))


def run_rows(
    rows: list[dict[str, Any]],
    *,
    timeout_seconds: float,
    backend: str,
    data_root: Path,
    jobs: int = 1,
) -> list[dict[str, Any]]:
    total = len(rows)

    def run_row(index: int, row: dict[str, Any]) -> dict[str, Any]:
        result = run_selected(
            root=data_root,
            relative_path=str(row["relative_path"]).replace("/", "\\"),
            kind=str(row["instance_kind"]),
            subtrack=str(row["subtrack"]),
            backend=backend,
            timeout_seconds=timeout_seconds,
            arguments_or_atoms=row.get("arguments_or_atoms"),
            track=str(row["track"]),
            instance_kind=str(row["instance_kind"]),
        )
        _print_row_event(index=index, total=total, row=row, result=result)
        return {"source": row, "result": result}

    if jobs <= 1:
        return [run_row(index, row) for index, row in enumerate(rows, start=1)]
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        # Collect futures in submit order so the output keeps manifest
        # order no matter which rows finish first.
        futures = [
            pool.submit(run_row, index, row) for index, row in enumerate(rows, start=1)
        ]
        return [future.result() for future in futures]


def _print_row_event(
    *, index: int, total: int, row: dict[str, Any], result: dict[str, Any]
) -> None:
    print(
        json.dumps(
            {
                "event": "frontier_row",
                "index": index,
                "total": total,
                "subtrack": row["subtrack"],
                "relative_path": row["relative_path"],
                "recal_class": row.get("recal_class"),
                "status": result.get("status"),
                "answer": result.get("answer"),
                "reason": result.get("reason"),
            },
            sort_keys=True,
        ),
        file=sys.stderr,
        flush=True,
    )


def summarize_by_class(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = _empty_bucket()
    by_class: dict[str, dict[str, int]] = {}
    deviations: list[dict[str, Any]] = []
    for item in results:
        source = item["source"]
        status = str(item["result"].get("status"))
        recal_class = str(source["recal_class"])
        bucket = by_class.setdefault(recal_class, _empty_bucket())
        for target in (total, bucket):
            target["rows"] += 1
            target[_status_key(status)] += 1
        if status != CLASS_EXPECTED_STATUS.get(recal_class, status):
            deviations.append(
                {
                    "relative_path": source["relative_path"],
                    "subtrack": source["subtrack"],
                    "recal_class": recal_class,
                    "status": status,
                }
            )
    return {"total": total, "by_class": by_class, "deviations": deviations}


def _empty_bucket() -> dict[str, int]:
    return {"rows": 0, "solved": 0, "timeout": 0, "other": 0}


def _status_key(status: str) -> str:
    return status if status in ("solved", "timeout") else "other"


def aggregate_outputs(paths: list[Path]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        results.extend(payload["results"])
    return summarize_by_class(results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the frozen frontier-v1 manifest rows and summarize per recal class."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--backend", default="auto")
    parser.add_argument("--label", help="Run label, e.g. frontier-v1-main-57da538.")
    parser.add_argument(
        "--subtrack",
        action="append",
        default=[],
        help="Only run this subtrack; repeat to run multiple (for chunking).",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--jobs",
        type=int,
        default=default_jobs(),
        help=(
            "Rows to run concurrently (each in its own subprocess); "
            "use 1 for contention-free serial timings."
        ),
    )
    parser.add_argument(
        "--aggregate",
        type=Path,
        nargs="+",
        help="Skip running; combine these run outputs into one summary.",
    )
    args = parser.parse_args(argv)

    if args.aggregate:
        print(json.dumps(aggregate_outputs(args.aggregate), indent=2, sort_keys=True))
        return 0

    if not args.label:
        parser.error("--label is required unless --aggregate is used")

    rows = json.loads(args.manifest.read_text(encoding="utf-8"))
    subtracks = set(args.subtrack) if args.subtrack else None
    selected = select_rows(rows, subtracks=subtracks)
    results = run_rows(
        selected,
        timeout_seconds=args.timeout_seconds,
        backend=args.backend,
        data_root=args.root,
        jobs=args.jobs,
    )
    summary = summarize_by_class(results)
    payload = {
        "label": args.label,
        "root": str(args.root),
        "backend": args.backend,
        "timeout_seconds": args.timeout_seconds,
        "subtracks": sorted(subtracks) if subtracks else None,
        "summary": summary,
        "results": results,
    }
    chunk = "-".join(sorted(subtracks)) if subtracks else "all"
    output_path = args.output_dir / f"iccma-2025-{args.label}-{chunk}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {output_path}")
    if args.jobs > 1:
        print(
            f"caveat: {args.jobs} rows ran concurrently; per-row elapsed times "
            "include CPU contention noise (use --jobs 1 for timing-sensitive gates)"
        )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
