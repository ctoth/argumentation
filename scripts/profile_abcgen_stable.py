"""Per-solve profile of the sparse-narrow stable solver on one ABA instance.

Committed variant of the exp-5 scout's scratchpad probe
(`scratchpad/abcgen_stable_profile.py`): runs the exact hot path
(`_NativeSparseNarrowStableSolver(framework).stable_extension()`) with a
daemon thread snapshotting the solver's own telemetry, so growing per-solve
CDCL times are visible even if the run is killed at the budget.

Usage:
    uv run scripts/profile_abcgen_stable.py <instance.aba> [budget_seconds]

Exit codes: 0 = solved within budget, 3 = budget exceeded (hard exit).
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

from argumentation.interop.iccma import parse_aba
from argumentation.structured.aba.aba_sat import _NativeSparseNarrowStableSolver

SNAPSHOT_SECONDS = 5.0


def _snapshot_line(solver: _NativeSparseNarrowStableSolver, elapsed: float) -> str:
    telemetry = solver.telemetry
    solve_times = list(telemetry["native_sparse_narrow_solve_times_ms"])
    return (
        f"[{elapsed:8.1f}s] checks={telemetry['native_sparse_narrow_solver_checks']}"
        f" loop_formulas={telemetry['native_sparse_narrow_loop_formulas']}"
        f" edge_cycle_clauses={telemetry.get('native_sparse_narrow_edge_cycle_clauses', 'n/a')}"
        f" solve_times_ms={solve_times}"
    )


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    instance = Path(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0

    parse_started = time.perf_counter()
    framework = parse_aba(instance.read_text(encoding="utf-8"))
    parse_seconds = time.perf_counter() - parse_started
    print(
        f"instance={instance.name} assumptions={len(framework.assumptions)}"
        f" language={len(framework.language)} rules={len(framework.rules)}"
        f" parse={parse_seconds:.2f}s",
        flush=True,
    )

    build_started = time.perf_counter()
    solver = _NativeSparseNarrowStableSolver(framework)
    build_seconds = time.perf_counter() - build_started
    print(f"build={build_seconds:.2f}s", flush=True)
    for key, value in sorted(solver.telemetry.items()):
        if key.startswith("native_sparse_narrow_acyc"):
            print(f"  {key}={value}", flush=True)

    solve_started = time.perf_counter()

    def watch() -> None:
        while True:
            time.sleep(SNAPSHOT_SECONDS)
            elapsed = time.perf_counter() - solve_started
            print(_snapshot_line(solver, elapsed), flush=True)
            if elapsed > budget:
                print(f"BUDGET EXCEEDED ({budget}s) — hard exit", flush=True)
                os._exit(3)

    threading.Thread(target=watch, daemon=True).start()

    extension = solver.stable_extension()
    total = time.perf_counter() - solve_started
    print(_snapshot_line(solver, total), flush=True)
    witness = "none" if extension is None else len(extension)
    print(f"DONE total_solve={total:.2f}s witness_size={witness}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
