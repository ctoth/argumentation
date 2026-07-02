"""Compare the af-sststg-shortcuts SST run against the af-sststg-baseline run.

Usage:
    uv run scripts/compare_af_sststg_runs.py BASELINE_JSON CANDIDATE_JSON [DATA_ROOT]

Prints status tables, solved-set deltas, answer mismatches on commonly-solved
rows, total elapsed time on commonly-solved rows with percent delta,
per-subtrack solved counts, the named recalibration target rows
(ER_300_50_8 / ER_200_20_3 / crusti DS-SST family), and — when DATA_ROOT is
given — verifies every commonly-solved SE row whose witness changed by
checking the new witness is conflict-free with full range (i.e. a stable
extension, hence a valid semi-stable witness).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

NAMED_ROW_PATTERNS = ("ER_300_50_8", "ER_200_20_3", "crusti")


def load_rows(path: Path) -> dict[tuple[str, str, str], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    keyed = {}
    for row in rows:
        key = (str(row["track"]), str(row["subtrack"]), str(row["instance"]))
        keyed[key] = row
    if len(keyed) != len(rows):
        raise SystemExit(f"duplicate row keys in {path}")
    return keyed


def row_line(row: dict) -> str:
    return (
        f"status={row['status']} answer={row.get('answer')} "
        f"elapsed={float(row['elapsed_seconds']):.3f}s reason={row.get('reason')}"
    )


def parse_framework(root: Path, instance: str):
    from argumentation.interop.iccma import parse_af, parse_apx, parse_tgf

    candidates = sorted(root.glob(f"extracted/**/{instance}"))
    if not candidates:
        return None
    path = candidates[0]
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".apx":
        return parse_apx(text)
    if path.suffix == ".tgf":
        return parse_tgf(text)
    return parse_af(text)


def witness_is_stable(framework, witness_text: str | None) -> bool | None:
    """True iff the witness is conflict-free with full range (a stable ext)."""
    if framework is None or witness_text is None:
        return None
    witness = frozenset(witness_text.split())
    if not witness <= framework.arguments:
        return False
    conflicts = framework.attacks if framework.attacks is not None else framework.defeats
    if any(a in witness and b in witness for a, b in conflicts):
        return False
    attacked = {target for source, target in framework.defeats if source in witness}
    return witness | attacked == framework.arguments


def main() -> None:
    baseline_path = Path(sys.argv[1])
    candidate_path = Path(sys.argv[2])
    data_root = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    baseline = load_rows(baseline_path)
    candidate = load_rows(candidate_path)

    print(f"baseline rows: {len(baseline)}  candidate rows: {len(candidate)}")
    common_keys = sorted(set(baseline) & set(candidate))
    print(f"common keys: {len(common_keys)}")
    only_base = sorted(set(baseline) - set(candidate))
    only_cand = sorted(set(candidate) - set(baseline))
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
        print(f"  {key} -> candidate {row_line(candidate[key])}")
    print(f"gained ({len(gained)}):")
    for key in gained:
        print(f"  {key} <- baseline {row_line(baseline[key])}")

    for name, solved in (("baseline", base_solved), ("candidate", cand_solved)):
        by_subtrack = Counter(key[1] for key in solved)
        print(f"{name} solved by subtrack: {dict(sorted(by_subtrack.items()))}")

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

    print("named target rows (recalibration):")
    for key in common_keys:
        track, subtrack, instance = key
        if subtrack != "DS-SST":
            continue
        if not any(pattern in instance for pattern in NAMED_ROW_PATTERNS):
            continue
        print(f"  {key}")
        print(f"    baseline:  {row_line(baseline[key])}")
        print(f"    candidate: {row_line(candidate[key])}")

    se_witness_changed = [
        key
        for key in common_solved
        if key[1].startswith("SE-")
        and baseline[key].get("witness") != candidate[key].get("witness")
    ]
    print(f"SE rows with changed witness: {len(se_witness_changed)}")
    if data_root is not None:
        unverified = []
        stable_count = 0
        for key in se_witness_changed:
            framework = parse_framework(data_root, key[2])
            verdict = witness_is_stable(framework, candidate[key].get("witness"))
            if verdict is True:
                stable_count += 1
            else:
                unverified.append((key, verdict))
        print(
            f"  changed SE witnesses verified stable (=> valid SST witness): "
            f"{stable_count}/{len(se_witness_changed)}"
        )
        for key, verdict in unverified:
            print(f"  NOT verified stable ({verdict}): {key}")


if __name__ == "__main__":
    main()
