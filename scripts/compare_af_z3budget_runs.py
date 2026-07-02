"""Compare the af-z3budget DS-PR run against the af-dspr-cdas-variantB baseline.

Usage:
    uv run scripts/compare_af_z3budget_runs.py BASELINE_JSON CANDIDATE_JSON

Prints status tables, solved-set deltas, answer mismatches on commonly-solved
rows, and total elapsed time on commonly-solved rows with percent delta.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def load_rows(path: Path) -> dict[tuple[str, str, str], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    keyed = {}
    for row in rows:
        key = (str(row["track"]), str(row["subtrack"]), str(row["instance"]))
        keyed[key] = row
    if len(keyed) != len(rows):
        raise SystemExit(f"duplicate row keys in {path}")
    return keyed


def main() -> None:
    baseline_path = Path(sys.argv[1])
    candidate_path = Path(sys.argv[2])
    baseline = load_rows(baseline_path)
    candidate = load_rows(candidate_path)

    print(f"baseline rows: {len(baseline)}  candidate rows: {len(candidate)}")
    common_keys = sorted(set(baseline) & set(candidate))
    print(f"common keys: {len(common_keys)}")
    only_base = set(baseline) - set(candidate)
    only_cand = set(candidate) - set(baseline)
    if only_base:
        print(f"keys only in baseline: {len(only_base)}")
    if only_cand:
        print(f"keys only in candidate: {len(only_cand)}")

    for name, keyed in (("baseline", baseline), ("candidate", candidate)):
        counts = Counter(row["status"] for row in keyed.values())
        print(f"{name} status counts: {dict(sorted(counts.items()))}")

    base_solved = {k for k in common_keys if baseline[k]["status"] == "solved"}
    cand_solved = {k for k in common_keys if candidate[k]["status"] == "solved"}
    lost = sorted(base_solved - cand_solved)
    gained = sorted(cand_solved - base_solved)
    print(f"solved baseline={len(base_solved)} candidate={len(cand_solved)}")
    print(f"lost ({len(lost)}):")
    for key in lost:
        print(f"  {key} -> candidate status {candidate[key]['status']}")
    print(f"gained ({len(gained)}):")
    for key in gained:
        print(f"  {key} <- baseline status {baseline[key]['status']}")

    common_solved = sorted(base_solved & cand_solved)
    mismatches = [
        key
        for key in common_solved
        if baseline[key].get("answer") != candidate[key].get("answer")
    ]
    print(f"commonly solved: {len(common_solved)}  answer mismatches: {len(mismatches)}")
    for key in mismatches:
        print(
            f"  {key}: baseline={baseline[key].get('answer')} "
            f"candidate={candidate[key].get('answer')}"
        )

    base_time = sum(float(baseline[key]["elapsed_seconds"]) for key in common_solved)
    cand_time = sum(float(candidate[key]["elapsed_seconds"]) for key in common_solved)
    delta_pct = ((cand_time - base_time) / base_time * 100) if base_time else 0.0
    print(
        f"commonly-solved elapsed: baseline={base_time:.2f}s "
        f"candidate={cand_time:.2f}s delta={delta_pct:+.2f}%"
    )


if __name__ == "__main__":
    main()
