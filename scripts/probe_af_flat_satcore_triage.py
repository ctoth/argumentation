"""Triage probe (kill test) for flat sat-core routing: reproduce the two
off-gate TO->solved flips on current main. One (stem, op, engine) per process.

    python scripts/probe_af_flat_satcore_triage.py <stem> <op> <engine>

op in {dc_co, se_pr}; engine in {smt, sat-core}. Prints answer + seconds.
Flat whole-graph paths (these instances are single-SCC so cone==graph).
"""

from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter

from argumentation.interop.iccma import parse_af
from argumentation.solving import af_sat

ROOT = Path("C:/Users/Q/code/argumentation/data/iccma/2025")
CHECK_BUDGET_SECONDS = 120.0


def _load(stem: str):
    afp = ROOT / "extracted" / "instances" / "AFs" / f"{stem}.af"
    query = (ROOT / "extracted" / "instances" / "AFs" / f"{stem}.af.arg").read_text().strip()
    return parse_af(afp.read_text(encoding="utf-8", errors="ignore")), query


def _run(framework, query, op, engine):
    if op == "dc_co":
        ext = af_sat.find_complete_extension(
            framework, require_in=query, check_budget_seconds=CHECK_BUDGET_SECONDS, engine=engine
        )
        return ext is not None  # credulous complete = witness exists
    if op == "se_pr":
        prepared = af_sat._prepare(framework, "preferred", simplify=True, require_in=None, require_out=None)
        if prepared is None:
            return None
        problem = af_sat.AfSatKernel(prepared.residual, check_budget_seconds=CHECK_BUDGET_SECONDS, engine=engine)
        problem.add_complete_labelling()
        result = af_sat._find_preferred_extension_body(
            problem, prepared.residual, prepared.required_in, prepared.required_out
        )
        ext = prepared.lift(result)
        return None if ext is None else len(ext)
    raise SystemExit(f"unknown op {op}")


def main() -> int:
    stem, op, engine = sys.argv[1], sys.argv[2], sys.argv[3]
    framework, query = _load(stem)
    print(f"{stem} {op} engine={engine}: {len(framework.arguments)} args / {len(framework.defeats)} defeats", flush=True)
    t = perf_counter()
    try:
        answer = _run(framework, query, op, engine)
        print(f"RESULT answer={answer} time={perf_counter()-t:.2f}s", flush=True)
    except af_sat.AfSatCheckTimeout:
        print(f"TIMEOUT (check budget {CHECK_BUDGET_SECONDS}s) time={perf_counter()-t:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
