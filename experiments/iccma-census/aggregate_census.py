"""Aggregate the per-subtrack census-600s run outputs into a per-stratum table.

Reads data/iccma/2025/runs/iccma-2025-census-600s-<ST>.json for each subtrack
in the frozen sample, classifies each result row's family, and reports
solved@600 vs still-timeout per (family, subtrack) stratum, plus totals.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

RUNS = Path("C:/Users/Q/code/argumentation/data/iccma/2025/runs")
MANIFEST = Path(
    "C:/Users/Q/AppData/Local/Temp/claude/C--Users-Q-code-argumentation/"
    "e531f1d6-db52-4333-8cee-1726098fa014/scratchpad/census-wt/experiments/"
    "iccma-census/sample-timeout-600s.json"
)

FAMILY_PREFIXES = {
    "crusti_g2io": "crusti_g",
    "scc": "scc_",
    "ER": "ER_",
    "mainkwt": "mainkwt_",
    "abcgen": "abcgen_c",
    "aba": "aba_",
}


def classify_family(relative_path: str) -> str:
    base = relative_path.replace("\\", "/").rsplit("/", 1)[-1]
    for fam, pre in FAMILY_PREFIXES.items():
        if base.startswith(pre):
            return fam
    return "other"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    subtracks = sorted({e["subtrack"] for e in manifest["entries"]})

    # (family, subtrack) -> Counter of status
    cells: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    missing = []
    for st in subtracks:
        path = RUNS / f"iccma-2025-census-600s-{st}.json"
        if not path.exists():
            missing.append(st)
            continue
        for row in json.loads(path.read_text(encoding="utf-8")):
            fam = classify_family(row["instance"])
            cells[(fam, st)][row["status"]] += 1

    print(f"subtracks: {subtracks}")
    if missing:
        print(f"MISSING run outputs for: {missing}")
    print(f"\n{'family':12} {'subtrack':8} {'solved':>6} {'timeout':>7} {'other':>6}")
    tot = defaultdict(int)
    for (fam, st) in sorted(cells):
        c = cells[(fam, st)]
        solved = c.get("solved", 0)
        timeout = c.get("timeout", 0)
        other = sum(v for k, v in c.items() if k not in ("solved", "timeout"))
        othertxt = "" if not other else " ".join(f"{k}={v}" for k, v in c.items() if k not in ("solved", "timeout"))
        print(f"{fam:12} {st:8} {solved:>6} {timeout:>7} {other:>6}  {othertxt}")
        tot["solved"] += solved
        tot["timeout"] += timeout
        tot["other"] += other
    total_rows = tot["solved"] + tot["timeout"] + tot["other"]
    print(f"\nTOTAL rows={total_rows} solved={tot['solved']} timeout={tot['timeout']} other={tot['other']}")
    if total_rows:
        frac = tot["solved"] / total_rows
        print(f"budget-artifact fraction (solved@600 / sampled timeouts) = {tot['solved']}/{total_rows} = {frac:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
