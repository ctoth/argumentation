"""Verify changed SE-SST witnesses are genuine semi-stable extensions.

Usage:
    uv run scripts/verify_sststg_se_witnesses.py BASELINE_JSON CANDIDATE_JSON DATA_ROOT

For every commonly-solved SE row whose witness differs between the runs,
checks BOTH witnesses independently:

1. conflict-free w.r.t. the conflict relation (polynomial),
2. complete extension (polynomial: admissible + all defended arguments in),
3. range-maximal among complete extensions (one SAT call: does a complete
   extension exist whose range strictly contains the witness range?).

A witness passing all three is a semi-stable extension by definition.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_rows(path: Path) -> dict[tuple[str, str, str], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {
        (str(row["track"]), str(row["subtrack"]), str(row["instance"])): row
        for row in rows
    }


def parse_framework(root: Path, instance: str):
    from argumentation.interop.iccma import parse_af, parse_apx, parse_tgf

    candidates = sorted(root.glob(f"extracted/**/{instance}"))
    if not candidates:
        raise SystemExit(f"instance not found under {root}: {instance}")
    path = candidates[0]
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".apx":
        return parse_apx(text)
    if path.suffix == ".tgf":
        return parse_tgf(text)
    return parse_af(text)


def parse_witness(witness_text: str) -> frozenset[str]:
    # extension_to_text serializes each argument with repr(); strip quotes.
    return frozenset(token.strip("'\"") for token in witness_text.split())


def is_semi_stable(framework, witness: frozenset[str]) -> tuple[bool, str]:
    from argumentation.core.dung import range_of
    from argumentation.core.finite import predecessors_index
    from argumentation.solving.af_sat import AfSatKernel

    if not witness <= framework.arguments:
        return False, "unknown arguments in witness"
    conflicts = (
        framework.attacks if framework.attacks is not None else framework.defeats
    )
    if any(a in witness and b in witness for a, b in conflicts):
        return False, "not conflict-free"
    attackers_index = predecessors_index(framework.defeats)
    attacked_by_witness = {
        target for source, target in framework.defeats if source in witness
    }

    def defended(argument: str) -> bool:
        return all(
            attacker in attacked_by_witness
            for attacker in attackers_index.get(argument, frozenset())
        )

    if not all(defended(argument) for argument in witness):
        return False, "not admissible"
    defended_set = {
        argument for argument in framework.arguments if defended(argument)
    }
    if defended_set != set(witness):
        return False, "not complete (defended set differs)"

    witness_range = range_of(witness, framework.defeats)
    outside = framework.arguments - witness_range
    if not outside:
        return True, "stable (full range)"
    kernel = AfSatKernel(framework)
    kernel.add_complete_labelling()
    kernel.add_range_definition()
    kernel.require_range(witness_range)
    kernel.require_any_range(outside)
    if kernel.check("verify_range_maximality") == "sat":
        return False, "range not maximal"
    return True, "complete + range-maximal"


def main() -> None:
    baseline = load_rows(Path(sys.argv[1]))
    candidate = load_rows(Path(sys.argv[2]))
    root = Path(sys.argv[3])

    changed = [
        key
        for key in sorted(set(baseline) & set(candidate))
        if key[1].startswith("SE-")
        and baseline[key]["status"] == "solved"
        and candidate[key]["status"] == "solved"
        and baseline[key].get("witness") != candidate[key].get("witness")
    ]
    print(f"changed SE witnesses: {len(changed)}")
    failures = 0
    for key in changed:
        framework = parse_framework(root, key[2])
        for side, rows in (("baseline", baseline), ("candidate", candidate)):
            witness = parse_witness(rows[key]["witness"])
            ok, reason = is_semi_stable(framework, witness)
            if not ok:
                failures += 1
            print(f"  {key} {side}: {'OK' if ok else 'FAIL'} ({reason})")
    print(f"failures: {failures}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
