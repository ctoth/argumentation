from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.iccma2025_run_native import DATA_ROOT, RunConfig, run_native


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the ABA sparse/narrow 10 timeout + 10 solved fixture."
    )
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=DATA_ROOT)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--backend", choices=["auto", "native", "iccma"], default="auto")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--event-log-path", type=Path, default=None)
    args = parser.parse_args(argv)

    fixture = _load_fixture(args.fixture)
    rows = fixture["rows"]
    max_aba_assumptions = max(int(row["manifest"]["assumptions"]) for row in rows)
    if args.event_log_path is not None:
        args.event_log_path.parent.mkdir(parents=True, exist_ok=True)
        args.event_log_path.write_text("", encoding="utf-8")

    print(
        json.dumps(
            {
                "event": "aba_10x10_fixture_start",
                "rows": len(rows),
                "instances": len({str(row["relative_path"]) for row in rows}),
                "subtracks": sorted({str(row["subtrack"]) for row in rows}),
                "timeout_seconds": args.timeout_seconds,
            },
            sort_keys=True,
        ),
        file=sys.stderr,
        flush=True,
    )
    actual_rows: list[dict[str, Any]] = []
    for index, fixture_row in enumerate(rows, start=1):
        print(
            json.dumps(
                {
                    "event": "aba_10x10_fixture_row",
                    "index": index,
                    "total": len(rows),
                    "instance": fixture_row["relative_path"],
                    "subtrack": fixture_row["subtrack"],
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        config = RunConfig(
            root=args.root,
            backend=args.backend,
            iccma_binary=None,
            max_af_arguments=-1,
            max_aba_assumptions=max_aba_assumptions,
            timeout_seconds=args.timeout_seconds,
            progress=True,
            event_log_path=args.event_log_path,
            only_instances=frozenset({str(fixture_row["relative_path"])}),
            only_subtracks=frozenset({str(fixture_row["subtrack"])}),
        )
        row_batch = run_native(config)
        if len(row_batch) != 1:
            raise RuntimeError(
                "fixture row did not map to exactly one runner row: "
                f"{fixture_row['relative_path']} {fixture_row['subtrack']} -> {len(row_batch)}"
            )
        actual_rows.append(row_batch[0])
    summary = summarize(actual_rows)
    payload = {
        "fixture": str(args.fixture),
        "root": str(args.root),
        "backend": args.backend,
        "timeout_seconds": args.timeout_seconds,
        "summary": summary,
        "rows": actual_rows,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "aba_10x10_fixture_complete", **summary}, sort_keys=True))
    return 0


def _load_fixture(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError(f"expected fixture with exactly 20 rows: {path}")
    return payload


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(str(row["status"]) for row in rows)
    routed_native_sat = 0
    clingo_solver_calls = 0
    for row in rows:
        metadata = row.get("solver_metadata")
        if isinstance(metadata, str) and metadata:
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {}
        if not isinstance(metadata, dict):
            metadata = {}
        if metadata.get("algorithm") == "native_sparse_narrow_sat":
            routed_native_sat += 1
        if metadata.get("solver") == "clingo_multishot":
            clingo_solver_calls += int(metadata.get("solver_calls", 0) or 0)
        else:
            clingo_solver_calls += int(metadata.get("clingo_solver_calls", 0) or 0)
    return {
        "row_count": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "routed_native_sat": routed_native_sat,
        "clingo_solver_calls": clingo_solver_calls,
    }


if __name__ == "__main__":
    raise SystemExit(main())
