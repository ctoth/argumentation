# ABA clingo timeout diagnostics

Date: 2026-05-22

Status: passed diagnostic gate on experiment branch.

Experiment branch: `exp/aba-clingo-timeout-diagnostics`

## Hypothesis

The remaining sparse/narrow `SE-ST` timeout cohort cannot be improved
principledly while clingo statistics disappear at the parent worker timeout.
If the worker gives clingo a slightly smaller internal diagnostic budget and
returns an interrupted result with sanitized statistics, the next encoding
experiment can use deterministic search-shape evidence instead of only
`py-spy` samples and timeout counts.

## Contract

When `collect_clingo_statistics` is enabled for an ABA `SE-ST` single-extension
job, the worker must pass an internal clingo solve timeout below the parent
worker timeout. If clingo is interrupted by that internal budget, the worker
must return a structured timeout result that includes:

- `solver_metadata.solver = clingo_multishot`;
- `solver_metadata.algorithm = first-model-witness`;
- `solver_metadata.clingo_control_args`;
- `solver_metadata.clingo_timeout_seconds`;
- sanitized `solver_metadata.clingo_statistics`.

Normal non-diagnostic solves must keep existing blocking clingo behavior.

## Metric Gate

Run the exact five-row remaining `SE-ST` timeout cohort from
`experiments/2026-05-20-aba-se-st-clingo-stats-option-sweep.md` with
`--collect-clingo-statistics`. Passing diagnostic behavior means timeout rows
return timeout status with clingo statistics instead of parent-kill timeouts
with no solver metadata.

Promotion is not automatic. This experiment only promotes if the diagnostic
surface is correct and does not change default production route behavior.

## Evidence

Focused contracts:

```powershell
uv run pytest -q tests\test_aba_multishot.py -k "diagnostic_timeout or clingo_timeout_metadata"
uv run pytest -q tests\test_iccma_runner.py -k clingo_diagnostics
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py::test_auto_single_extension_sparse_narrow_stable_uses_clingo_when_available
```

Broader targeted gate:

```powershell
uv run pytest -q tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py tests\test_iccma_runner.py
```

Result: `1053 passed in 106.25s`.

Diagnostic benchmark gate:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --output-json data\iccma\2025\runs\aba-clingo-timeout-diagnostics.json --output-csv data\iccma\2025\runs\aba-clingo-timeout-diagnostics.csv
```

Result: all five rows returned structured `timeout` results with reason
`clingo solve exceeded 39.000s` instead of parent-kill timeouts. Each row has
`solver_metadata.clingo_interrupted = true`,
`solver_metadata.clingo_timeout_seconds = 39.0`, and sanitized
`solver_metadata.clingo_statistics`.

Observed first-row clingo search shape:

- `problem.lp.atoms = 98225`
- `problem.lp.rules = 117535`
- `solving.solvers.choices = 592699`
- `solving.solvers.conflicts = 506395`
- `solving.solvers.restarts = 1277`
- `summary.times.solve = 39.004817962646484`
- `summary.models.enumerated = 0`

Across the five rows, clingo made roughly 459k-593k choices and 378k-506k
conflicts before the diagnostic timeout, with zero enumerated models.

## Outcome

The experiment succeeded as a diagnostic instrumentation experiment. It did
not solve the remaining `SE-ST` cohort, but it converted opaque parent-worker
timeouts into solver-owned timeout results with clingo statistics.

This tells us the current flat first-model stable encoding is search-bound on
large sparse/narrow instances after grounding has already succeeded. The next
actual performance experiment should use these statistics plus `py-spy` to
change the encoding/search shape, not add another semantic-only route.

## Keep / Promote Decision

Keep and promote the diagnostic timeout surface if integration gates stay
green. Do not commit the generated benchmark JSON/CSV artifacts; they are
diagnostic output.

## Changed Paths

Implemented:

- `src/argumentation/aba_incremental.py`
- `src/argumentation/aba_asp.py`
- `src/argumentation/solver.py`
- `src/argumentation/solver_results.py`
- `tools/iccma2025_run_native.py`
- focused tests under `tests/`

Generated benchmark/profile artifacts must remain uncommitted unless a later
promotion decision explicitly asks for them.
