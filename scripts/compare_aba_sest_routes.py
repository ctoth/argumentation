"""Compare the aba-sest-route-fixed SE-ST run against aba-sest-route-baseline.

Usage:
    uv run scripts/compare_aba_sest_routes.py BASELINE_JSON FIXED_JSON [DATA_ROOT]

Prints status tables, solved-set deltas (lost rows are a kill criterion),
answer/witness mismatches on commonly-solved rows, per-row and total elapsed
time on baseline-solved rows with the >10% regression kill check, the named
target rows (aba_2000_0.1_5_5_1 / _6), every abcgen SE-ST row, and — when
DATA_ROOT is given — natively verifies each gained or witness-changed solved
SE-ST ABA row's witness as a stable extension (flat ABA: closure-based check).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

NAMED_ROWS = ("aba_2000_0.1_5_5_1.aba", "aba_2000_0.1_5_5_6.aba")


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
    elapsed = row.get("elapsed_seconds")
    elapsed_text = f"{float(elapsed):.3f}s" if elapsed is not None else "n/a"
    return (
        f"status={row['status']} answer={row.get('answer')} "
        f"witness_size={row.get('witness_size')} elapsed={elapsed_text} "
        f"reason={row.get('reason')}"
    )


def is_aba(row: dict) -> bool:
    return str(row.get("kind", "")).startswith("aba") or str(row["instance"]).endswith(".aba")


def parse_aba_framework(root: Path, instance: str):
    from argumentation.interop.iccma import parse_aba

    candidates = sorted(root.glob(f"extracted/**/{instance}"))
    if not candidates:
        return None
    return parse_aba(candidates[0].read_text(encoding="utf-8"))


def witness_is_stable_flat(framework, witness_text: str | None) -> bool | None:
    """Closure-based stable check for flat ABA.

    W is stable iff W is conflict-free (no contrary of a member of W is
    derivable from W) and every assumption outside W is attacked (its contrary
    is derivable from W). Flat ABA guarantees closedness (assumptions are
    never rule heads; enforced by ABAFramework.__post_init__).
    """
    if framework is None or witness_text is None:
        return None
    names = {repr(literal): literal for literal in framework.language}
    tokens = witness_text.split()
    if any(token not in names for token in tokens):
        return False
    witness = frozenset(names[token] for token in tokens)
    if not witness <= framework.assumptions:
        return False
    derived = set(witness)
    changed = True
    rules = tuple(framework.rules)
    while changed:
        changed = False
        for rule in rules:
            if rule.consequent not in derived and all(
                antecedent in derived for antecedent in rule.antecedents
            ):
                derived.add(rule.consequent)
                changed = True
    if any(framework.contrary[assumption] in derived for assumption in witness):
        return False
    return all(
        framework.contrary[assumption] in derived
        for assumption in framework.assumptions - witness
    )


def main() -> None:
    baseline_path = Path(sys.argv[1])
    fixed_path = Path(sys.argv[2])
    data_root = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    baseline = load_rows(baseline_path)
    fixed = load_rows(fixed_path)

    print(f"baseline rows: {len(baseline)}  fixed rows: {len(fixed)}")
    common_keys = sorted(set(baseline) & set(fixed))
    print(f"common keys: {len(common_keys)}")
    for label, only in (
        ("baseline-only", sorted(set(baseline) - set(fixed))),
        ("fixed-only", sorted(set(fixed) - set(baseline))),
    ):
        if only:
            print(f"keys {label}: {len(only)}")
            for key in only:
                print(f"  {key}")

    for name, keyed in (("baseline", baseline), ("fixed", fixed)):
        counts = Counter(row["status"] for row in keyed.values())
        aba_counts = Counter(
            row["status"] for row in keyed.values() if is_aba(row)
        )
        print(f"{name} status counts (all): {dict(sorted(counts.items()))}")
        print(f"{name} status counts (ABA): {dict(sorted(aba_counts.items()))}")

    base_solved = {k for k in common_keys if baseline[k]["status"] == "solved"}
    fixed_solved = {k for k in common_keys if fixed[k]["status"] == "solved"}
    lost = sorted(base_solved - fixed_solved)
    gained = sorted(fixed_solved - base_solved)
    print(f"solved baseline={len(base_solved)} fixed={len(fixed_solved)}")
    print(f"LOST ({len(lost)}) [kill criterion if > 0]:")
    for key in lost:
        print(f"  {key} -> fixed {row_line(fixed[key])}")
    print(f"gained ({len(gained)}):")
    for key in gained:
        print(f"  {key[2]}")
        print(f"    baseline: {row_line(baseline[key])}")
        print(f"    fixed:    {row_line(fixed[key])}")

    common_solved = sorted(base_solved & fixed_solved)
    answer_mismatches = [
        key
        for key in common_solved
        if baseline[key].get("answer") != fixed[key].get("answer")
    ]
    print(
        f"commonly solved: {len(common_solved)}  "
        f"answer mismatches: {len(answer_mismatches)} [kill criterion if > 0]"
    )
    for key in answer_mismatches:
        print(
            f"  {key}: baseline={baseline[key].get('answer')} "
            f"fixed={fixed[key].get('answer')}"
        )

    base_time = sum(float(baseline[key]["elapsed_seconds"]) for key in common_solved)
    fixed_time = sum(float(fixed[key]["elapsed_seconds"]) for key in common_solved)
    delta_pct = ((fixed_time - base_time) / base_time * 100) if base_time else 0.0
    print(
        f"commonly-solved elapsed: baseline={base_time:.2f}s "
        f"fixed={fixed_time:.2f}s delta={delta_pct:+.2f}% "
        f"[kill criterion if > +10%]"
    )
    regressions = []
    for key in common_solved:
        base_elapsed = float(baseline[key]["elapsed_seconds"])
        fixed_elapsed = float(fixed[key]["elapsed_seconds"])
        if base_elapsed > 0 and (fixed_elapsed - base_elapsed) / base_elapsed > 0.10:
            regressions.append((key, base_elapsed, fixed_elapsed))
    print(f"per-row >10% regressions on commonly-solved rows: {len(regressions)}")
    for key, base_elapsed, fixed_elapsed in regressions:
        print(f"  {key[2]}: {base_elapsed:.3f}s -> {fixed_elapsed:.3f}s")

    print("named target rows:")
    for key in common_keys:
        if key[2].split("/")[-1] in NAMED_ROWS or any(
            key[2].endswith(name) for name in NAMED_ROWS
        ):
            print(f"  {key[2]}")
            print(f"    baseline: {row_line(baseline[key])}")
            print(f"    fixed:    {row_line(fixed[key])}")

    print("abcgen SE-ST rows:")
    for key in common_keys:
        if "abcgen" in key[2]:
            print(f"  {key[2]}")
            print(f"    baseline: {row_line(baseline[key])}")
            print(f"    fixed:    {row_line(fixed[key])}")

    to_verify = sorted(
        set(gained)
        | {
            key
            for key in common_solved
            if baseline[key].get("witness") != fixed[key].get("witness")
        }
    )
    to_verify = [key for key in to_verify if is_aba(fixed[key])]
    print(f"solved ABA rows needing native witness verification: {len(to_verify)}")
    if data_root is not None:
        verified = 0
        failures = []
        for key in to_verify:
            framework = parse_aba_framework(data_root, key[2])
            verdict = witness_is_stable_flat(framework, fixed[key].get("witness"))
            if verdict is True:
                verified += 1
            else:
                failures.append((key, verdict))
        print(f"  natively verified stable: {verified}/{len(to_verify)}")
        for key, verdict in failures:
            print(f"  NOT verified ({verdict}): {key}")


if __name__ == "__main__":
    main()
