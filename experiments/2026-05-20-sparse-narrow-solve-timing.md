# Sparse narrow solve timing telemetry

Date: 2026-05-20

Status: measured on experiment branch; source change should be promoted.

Experiment branch: `exp/aba-sparse-narrow-solve-timing`.

Evidence commit:
- `63d98f8` Record sparse narrow solve timing telemetry.

Changed paths:
- `src/argumentation/aba_sat.py`
- `tests/test_aba_sparse_narrow_native_sat.py`

Hypothesis: per-solve timing telemetry would identify whether the sparse/narrow
hard row is dominated by the first completion-SAT solve or by later lazy-loop
refinement solves.

Single variable: add `native_sparse_narrow_solve_times_ms` telemetry around
each `_NativeSparseNarrowStableSolver.solver.solve(...)` call.

Fast contracts:
- `uv run pytest -q tests\test_aba_sparse_narrow_native_sat.py`
  - result: 3 passed.
- `uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py`
  - result: 8 passed.

Metric command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --output-json data\iccma\2025\runs\solve-timing-glucose4-hard-row.json --output-csv data\iccma\2025\runs\solve-timing-glucose4-hard-row.csv
```

Metric result:
- Row: `ABAs/abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba`, `SE-ST`.
- Status: solved.
- Elapsed: 169.94663060002495 seconds.
- Witness size: 148.
- Validation: valid.
- Solver checks: 5.
- Candidate models: 5.
- Loop formulas: 344.
- Learned clauses: 33033.
- Clingo calls: 0.
- Solve times: `[3298, 4056, 5318, 53180, 102730]` ms.

Outcome: positive instrumentation result.

Decision: promote the telemetry. It identifies the bottleneck shape without
changing semantics or routing. The first solve is not the problem: the final
two refinement solves dominate the run, especially the fifth solve at about
102.7 seconds.

Recommendation: choose the next solver experiment to reduce late-refinement
search after loop clauses have been learned. A no-op/minimal `cadical195`
IPASIR-UP callback-overhead probe is still the next feasibility check before
building a real user propagator, but the target is now clear: it must improve
late CDCL search after the lazy loop-refinement clauses, not first-model
discovery.

Generated diagnostics:
- `data\iccma\2025\runs\solve-timing-glucose4-hard-row.json`
- `data\iccma\2025\runs\solve-timing-glucose4-hard-row.csv`

These generated diagnostics were not committed.
