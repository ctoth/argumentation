from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


def compare_runs(
    *,
    before_rows: Path,
    after_rows: Path,
    before_events: Path | None = None,
    after_events: Path | None = None,
) -> dict[str, Any]:
    before_status = _status_counts(_load_rows(before_rows))
    after_status = _status_counts(_load_rows(after_rows))
    before_utilities = _utility_counts(before_events)
    after_utilities = _utility_counts(after_events)

    return {
        "before_status": dict(sorted(before_status.items())),
        "after_status": dict(sorted(after_status.items())),
        "status_delta": _delta(before_status, after_status),
        "before_utilities": dict(sorted(before_utilities.items())),
        "after_utilities": dict(sorted(after_utilities.items())),
        "utility_delta": _delta(before_utilities, after_utilities),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare ICCMA run row summaries and streamed SAT utility events."
    )
    parser.add_argument("--before-rows", type=Path, required=True)
    parser.add_argument("--after-rows", type=Path, required=True)
    parser.add_argument("--before-events", type=Path)
    parser.add_argument("--after-events", type=Path)
    args = parser.parse_args(argv)

    comparison = compare_runs(
        before_rows=args.before_rows,
        after_rows=args.after_rows,
        before_events=args.before_events,
        after_events=args.after_events,
    )
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


def _load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        rows = json.load(handle)
    if not isinstance(rows, list):
        raise ValueError(f"expected list of run rows in {path}")
    return rows


def _status_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(row.get("status", "unknown")) for row in rows)


def _utility_counts(path: Path | None) -> Counter[str]:
    counts: Counter[str] = Counter()
    if path is None:
        return counts
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event") != "sat_check":
                continue
            utility_name = event.get("utility_name")
            if utility_name is not None:
                counts[str(utility_name)] += 1
    return counts


def _delta(before: Counter[str], after: Counter[str]) -> dict[str, int]:
    keys = set(before) | set(after)
    return {
        key: after.get(key, 0) - before.get(key, 0)
        for key in sorted(keys)
        if after.get(key, 0) - before.get(key, 0) != 0
    }


if __name__ == "__main__":
    raise SystemExit(main())
