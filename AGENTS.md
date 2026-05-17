# Argumentation Repo Agent Instructions

## Performance-Contract-Before-Research Rule

- Before starting or salvaging solver, routing, optimization, benchmark, or
  performance research in this repository, first encode the expected
  operational learning as executable contracts.
- Semantic correctness properties alone are not enough for solver-performance
  work. Add at least one operational contract that can fail before the full
  benchmark gate: bounded solver calls, route selection, residual-size
  reduction, skipped bad path, calibrated wall-clock budget, or another
  measurable shape invariant.
- Use calibrated/local performance helpers when available instead of raw
  hardcoded timing guesses. Wall-clock contracts must be opt-in or calibrated;
  deterministic telemetry and route contracts should run normally.
- A benchmark gate may remain the final proof, but it must not be the first
  executable signal that an implementation is operationally hopeless.
- If salvaging old research, import only assets that satisfy or help enforce
  these contracts: tests, telemetry, route predicates, calibration helpers,
  benchmark runner fixes, page-image citations, and failure records. Do not
  revive failed production paths merely because they passed semantic tests.
- If no such operational contract can be stated yet, the next task is to write
  the contract or gather the evidence needed to write it, not to implement
  another solver variant.
