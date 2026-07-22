from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from unittest.mock import patch

from argumentation.interop.iccma import parse_aba
from argumentation.structured.aba import aba_sat


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure the stable ABA CNF before acyclicity constraints."
    )
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()

    framework = parse_aba(args.instance.read_text(encoding="utf-8"))
    build_started = time.perf_counter()
    with patch.object(aba_sat, "_enumerate_elementary_edge_cycles", return_value=[]):
        solver = aba_sat._NativeSparseNarrowStableSolver(framework)
    build_seconds = time.perf_counter() - build_started

    solve_started = time.perf_counter()
    satisfiable = solver.solver.solve()
    solve_seconds = time.perf_counter() - solve_started

    print(
        json.dumps(
            {
                "instance": str(args.instance),
                "atoms": len(framework.language),
                "assumptions": len(framework.assumptions),
                "rules": len(framework.rules),
                "base_formula_status": "sat" if satisfiable else "unsat",
                "build_seconds": build_seconds,
                "solve_seconds": solve_seconds,
                "variables": solver.solver.nof_vars(),
                "clauses": solver.solver.nof_clauses(),
                "recursive_rules": solver.telemetry[
                    "native_sparse_narrow_acyc_recursive_rules"
                ],
                "dependency_edges": solver.telemetry["native_sparse_narrow_acyc_edges"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
