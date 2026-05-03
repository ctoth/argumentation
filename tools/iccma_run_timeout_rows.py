from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.iccma_run_selected import run_selected


def selected_timeout_rows(
    rows: list[dict[str, Any]],
    *,
    years: set[int] | None,
    subtrack: str | None,
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if (years is None or row.get("year") in years)
        and (subtrack is None or row.get("subtrack") == subtrack)
    ]


def run_timeout_rows(
    rows: list[dict[str, Any]],
    *,
    timeout_seconds: float,
    backend: str,
    data_root: Path,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    total = len(rows)
    for index, row in enumerate(rows, start=1):
        year = int(row["year"])
        result = run_selected(
            root=data_root / str(year),
            relative_path=str(row["instance"]).replace("/", "\\"),
            kind=str(row["instance_kind"]),
            subtrack=str(row["subtrack"]),
            backend=backend,
            timeout_seconds=timeout_seconds,
            arguments_or_atoms=row.get("arguments_or_atoms"),
            track=str(row["track"]),
            instance_kind=str(row["instance_kind"]),
        )
        materialized = {"source": row, "result": result}
        results.append(materialized)
        print(
            json.dumps(
                {
                    "event": "timeout_row",
                    "index": index,
                    "total": total,
                    "year": year,
                    "subtrack": row["subtrack"],
                    "instance": row["instance"],
                    "status": result.get("status"),
                    "answer": result.get("answer"),
                    "reason": result.get("reason"),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
    return results


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    for item in results:
        status = str(item["result"].get("status"))
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "total": len(results),
        "by_status": dict(sorted(by_status.items())),
        "timeouts": [
            item["source"]["instance"]
            for item in results
            if item["result"].get("status") == "timeout"
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run selected rows from an ICCMA timeout fixture.")
    parser.add_argument("--timeouts", type=Path, required=True)
    parser.add_argument("--year", type=int, action="append")
    parser.add_argument("--subtrack")
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--backend", default="auto")
    parser.add_argument("--data-root", type=Path, default=Path("data") / "iccma")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    rows = json.loads(args.timeouts.read_text(encoding="utf-8"))
    selected = selected_timeout_rows(
        rows,
        years=None if args.year is None else set(args.year),
        subtrack=args.subtrack,
    )
    results = run_timeout_rows(
        selected,
        timeout_seconds=args.timeout_seconds,
        backend=args.backend,
        data_root=args.data_root,
    )
    payload = {
        "summary": summarize_results(results),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
