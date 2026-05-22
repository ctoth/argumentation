# ABA clingo timeout diagnostics

Date: 2026-05-22

Status: in progress on experiment branch.

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

## Changed Paths

Planned:

- `src/argumentation/aba_incremental.py`
- `src/argumentation/aba_asp.py`
- `src/argumentation/solver.py`
- `tools/iccma2025_run_native.py`
- focused tests under `tests/`

Generated benchmark/profile artifacts must remain uncommitted unless a later
promotion decision explicitly asks for them.
