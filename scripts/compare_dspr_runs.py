"""Compare two ICCMA run row files for the af-dspr-cdas experiment.

Usage:
    uv run scripts/compare_dspr_runs.py <baseline_rows.json> <candidate_rows.json>

Reports, for the kill criteria of the af-dspr-cdas experiment:
- per-run status counts (solved / timeout / error) and total wall time,
- total wall time restricted to baseline-solved rows for both runs and the
  percentage change (kill threshold: candidate > +10%),
- rows that were solved in baseline but not in candidate (kill: any),
- answer mismatches on rows solved in both runs (differential sanity check).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = f"{row.get('track')}::{row.get('subtrack')}::{row.get('instance')}"
        indexed[key] = row
    return indexed


def status_counts(rows: dict[str, dict[str, Any]]) -> Counter[str]:
    return Counter(str(row.get("status")) for row in rows.values())


def row_seconds(row: dict[str, Any]) -> float:
    value = row.get("elapsed_seconds")
    return float(value) if value is not None else 0.0


def total_seconds(rows: dict[str, dict[str, Any]]) -> float:
    return sum(row_seconds(row) for row in rows.values())


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    baseline_path = Path(argv[1])
    candidate_path = Path(argv[2])
    baseline = load_rows(baseline_path)
    candidate = load_rows(candidate_path)

    print(f"baseline: {baseline_path}")
    print(f"  rows={len(baseline)} statuses={dict(status_counts(baseline))}")
    print(f"  total_elapsed_seconds={total_seconds(baseline):.3f}")
    print(f"candidate: {candidate_path}")
    print(f"  rows={len(candidate)} statuses={dict(status_counts(candidate))}")
    print(f"  total_elapsed_seconds={total_seconds(candidate):.3f}")

    if set(baseline) != set(candidate):
        only_base = sorted(set(baseline) - set(candidate))
        only_cand = sorted(set(candidate) - set(baseline))
        print(f"ROW SET MISMATCH: only_baseline={only_base} only_candidate={only_cand}")

    shared = sorted(set(baseline) & set(candidate))
    baseline_solved = [key for key in shared if baseline[key].get("status") == "solved"]

    lost = [key for key in baseline_solved if candidate[key].get("status") != "solved"]
    gained = [
        key
        for key in shared
        if baseline[key].get("status") != "solved"
        and candidate[key].get("status") == "solved"
    ]
    base_time = sum(row_seconds(baseline[key]) for key in baseline_solved)
    cand_time = sum(row_seconds(candidate[key]) for key in baseline_solved)
    pct = ((cand_time - base_time) / base_time * 100.0) if base_time else float("nan")

    print(f"baseline-solved rows: {len(baseline_solved)}")
    print(f"  baseline time on those rows: {base_time:.3f}s")
    print(f"  candidate time on those rows: {cand_time:.3f}s ({pct:+.2f}%)")
    print(f"solved in baseline but NOT solved in candidate: {len(lost)}")
    for key in lost:
        print(f"  LOST {key} -> {candidate[key].get('status')}")
    print(f"newly solved in candidate: {len(gained)}")
    for key in gained:
        print(f"  GAINED {key} (was {baseline[key].get('status')})")

    mismatches = [
        key
        for key in baseline_solved
        if candidate[key].get("status") == "solved"
        and baseline[key].get("answer") != candidate[key].get("answer")
    ]
    print(f"answer mismatches on rows solved in both: {len(mismatches)}")
    for key in mismatches:
        print(
            f"  MISMATCH {key}: baseline={baseline[key].get('answer')} "
            f"candidate={candidate[key].get('answer')}"
        )

    kill = bool(lost) or (base_time > 0 and pct > 10.0) or bool(mismatches)
    print(f"kill_criteria_triggered={kill}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
