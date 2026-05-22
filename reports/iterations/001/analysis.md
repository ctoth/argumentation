# Iteration 001 Analysis

Starting gate:

`uv run pytest -q --timeout=600`

Result:

- `5 failed`
- `2829 passed`
- `3 skipped`
- `1 xfailed`

Failure clusters:

1. Benchmark test stub drift: `test_benchmark_rows_emit_paper_route_features`
   monkeypatch does not accept the current `clingo_control_args` and
   `collect_clingo_statistics` keyword arguments.
2. Import boundary drift: `aba_sat.py` imports `pysat.solvers`, but the boundary
   allowlist does not include `pysat`.
3. ABA SAT preferred-support regressions:
   - required assumptions not preserved;
   - preferred stable shortcut not running before preprocessing;
   - native CNF candidate block bound too tight for a generated counterexample.

Plan:

- Fix the benchmark stub drift first because it is local and mechanical.
- Fix the import boundary allowlist if the dependency is declared.
- Then inspect `aba_sat.py` for the preferred-support regressions as one solver
  cluster.
