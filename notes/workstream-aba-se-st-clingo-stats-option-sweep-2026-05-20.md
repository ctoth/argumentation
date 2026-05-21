# Workstream: ABA SE-ST Clingo Statistics and Option Sweep

Date: 2026-05-20

## Requested Outcome

Classify why the exact five remaining large sparse/narrow `SE-ST` ABA rows are
hard for clingo, then determine whether a bounded clingo configuration change
is worth a production optimization workstream.

This workstream adds diagnostic-only clingo statistics and explicit clingo
control-argument plumbing, runs a bounded option sweep on the five-row timeout
cohort, validates every solved witness, and records a go/no-go decision.

## Current Evidence

- `experiments/2026-05-20-aba-se-st-clingo-solver-shape.md` established that
  the current five-row `SE-ST` timeout cohort is clingo-solve dominated.
- The baseline in that experiment was `5/5` timeouts under current production
  `auto` routing.
- The smaller representative profile had `2450` samples in
  `clingo.Control.solve`, with grounding/add/encoding at tiny counts.
- The larger representative profile had `2416` samples in
  `clingo.Control.solve`, with grounding/add/encoding at tiny counts.
- `src/argumentation/aba_incremental.py::AbaIncrementalSolver._new_control`
  currently hard-codes `["--models=0", "--warn=none"]`.
- `tools/aba_shape_benchmark.py` currently has no CLI surface for clingo
  control arguments or clingo statistics.
- `rg -F "statistics" tools src tests` currently finds only
  `tools/perf_calibrate.py`; there is no clingo statistics capture path.
- Local clingo reports version `pyclingo 5.8.0` and supports
  `--configuration={auto|frumpy|jumpy|tweety|handy|crafty|trendy|many|<file>}`,
  `--heuristic={Berkmin|Vmtf|Vsids|Domain|Unit|None}`, and `--stats`.

The exact cohort remains:

- `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

## Final State

Committed source and test support:

- `src/argumentation/aba_incremental.py`
  - `AbaIncrementalSolver` accepts diagnostic-only `control_args` and
    `collect_statistics` constructor options.
  - `_new_control` no longer hard-codes the full clingo argument list inline;
    it builds controls from a named default tuple plus the explicit diagnostic
    `control_args`.
  - solve methods used by `SE-ST` copy sanitized `ctl.statistics` into
    telemetry after `ctl.solve` returns when statistics collection is enabled.
- `src/argumentation/aba_asp.py`
  - `solve_aba_with_backend` and `_solve_multishot` pass the diagnostic clingo
    options through to `AbaIncrementalSolver`.
  - metadata records `clingo_control_args` for every ASP/clingo multishot row.
  - metadata records `clingo_statistics` only when statistics collection is
    explicitly enabled.
- `src/argumentation/solver.py`
  - `solve_aba_single_extension` and `_solve_asp_aba_single_extension` expose
    the diagnostic clingo options without changing default behavior.
- `tools/iccma2025_run_native.py`
  - ABA `SE` jobs read `clingo_control_args` and `collect_clingo_statistics`
    from the job payload and pass them to `solve_aba_single_extension`.
- `tools/aba_shape_benchmark.py`
  - CLI adds repeated `--clingo-control-arg <arg>` and
    `--collect-clingo-statistics`.
  - benchmark config records the exact control args and statistics flag.
  - worker job payload includes those fields.
- Focused tests prove the diagnostic path and default path.

Committed experiment record:

`experiments/2026-05-20-aba-se-st-clingo-stats-option-sweep.md`

Generated diagnostics are written under:

- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-*.json`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-*.csv`

Generated diagnostics are not committed.

## Deletion Target

Delete the inline clingo Control construction spelling:

```python
self._clingo.Control(["--models=0", "--warn=none"])
```

Replace it with one named default control-argument tuple and one explicit
diagnostic argument extension point owned by `AbaIncrementalSolver`.

## Owned Paths

Source:

- `src/argumentation/aba_incremental.py`
- `src/argumentation/aba_asp.py`
- `src/argumentation/solver.py`
- `tools/iccma2025_run_native.py`
- `tools/aba_shape_benchmark.py`

Tests:

- `tests/test_aba_multishot.py`
- `tests/test_aba_sparse_narrow_route_contract.py`
- `tests/test_iccma_runner.py`

Documentation:

- this workstream file
- `experiments/2026-05-20-aba-se-st-clingo-stats-option-sweep.md`

Generated diagnostics:

- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-*.json`
- `data/iccma/2025/runs/aba-se-st-clingo-stats-option-sweep-*.csv`

## Ordered Phases

### Phase 0: Branch

Verify branch and tracked-file cleanliness:

```powershell
git branch --show-current
git status --short
```

Create the experiment branch from a clean tracked-file base:

```powershell
git switch -c exp/aba-se-st-clingo-stats-option-sweep
```

Gate: no tracked dirty files before branch creation.

### Phase 1: Contract Tests

Add failing tests before source implementation:

- `tests/test_aba_multishot.py`
  - constructing `AbaIncrementalSolver(..., control_args=("--configuration=frumpy",))`
    passes the default args plus the explicit diagnostic arg to
    `clingo.Control`;
  - constructing with `collect_statistics=True` records sanitized clingo
    statistics in telemetry after a stable single-extension solve;
  - default construction records the default control args and no statistics.
- `tests/test_aba_sparse_narrow_route_contract.py`
  - default `auto` sparse/narrow stable routing still reports
    `solver == "clingo_multishot"` and no diagnostic clingo arg is injected.
- `tests/test_iccma_runner.py`
  - an ABA `SE` worker job containing `clingo_control_args` and
    `collect_clingo_statistics` passes those fields through to
    `solve_aba_single_extension`;
  - a default ABA `SE` worker job passes empty diagnostic args and disabled
    statistics collection.

Contract test command:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py tests\test_iccma_runner.py
```

Gate: new tests fail for the expected missing diagnostic plumbing before source
implementation, then pass after implementation.

### Phase 2: Diagnostic Plumbing

Implement the final source state exactly as named above.

Metadata shape:

```python
{
    "clingo_control_args": ("--models=0", "--warn=none", ...),
    "clingo_statistics": {...}
}
```

Rules:

- `clingo_statistics` is present only when `collect_statistics=True`.
- `clingo_control_args` is present for multishot clingo results and always
  includes the two default args.
- default public API calls produce the same answer, same route, and same witness
  validation behavior as before.
- invalid clingo control args surface as a runner error in the benchmark output;
  they are not swallowed.

Search gates:

```powershell
rg -F 'Control(["--models=0", "--warn=none"])' src tests
rg -F "collect_clingo_statistics" src tools tests
rg -F "clingo_control_args" src tools tests
```

Gate:

- first search has no results;
- second and third searches find the intentional diagnostic plumbing and tests.

### Phase 3: Focused Verification

Run:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py tests\test_iccma_runner.py
```

Gate:

- all focused tests pass;
- no generated diagnostic output is staged or committed.

Commit the source/test diagnostic plumbing before running the option sweep.

### Phase 4: Baseline Statistics Run

Regenerate the five-row manifest from the validated run:

```powershell
jq '[.rows[] | select(.subtrack == "SE-ST" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json
```

Validate:

```powershell
jq 'length' data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json
jq '[.[] | .subtrack] | unique' data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json
```

Gate:

- manifest length is `5`;
- unique subtracks are `["SE-ST"]`.

Run baseline with statistics and no extra clingo args. Timeout: `40` seconds
per row, using the existing runner timeout slack.

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --output-json data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-baseline.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-baseline.csv
```

Gate:

- no runner errors;
- no invalid solved witnesses;
- record solved/timeout count;
- solved rows contain `solver_metadata.clingo_statistics`;
- timeout rows record status and elapsed time.

### Phase 5: Bounded Option Sweep

Run these exact variants, one output pair per variant:

- `configuration-frumpy`: `--configuration=frumpy`
- `configuration-jumpy`: `--configuration=jumpy`
- `configuration-tweety`: `--configuration=tweety`
- `configuration-handy`: `--configuration=handy`
- `configuration-crafty`: `--configuration=crafty`
- `configuration-trendy`: `--configuration=trendy`
- `heuristic-berkmin`: `--heuristic=Berkmin`
- `heuristic-vmtf`: `--heuristic=Vmtf`
- `heuristic-vsids`: `--heuristic=Vsids`
- `heuristic-unit`: `--heuristic=Unit`
- `heuristic-none`: `--heuristic=None`

Command template:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --collect-clingo-statistics --clingo-control-arg <ARG> --output-json data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-<VARIANT>.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-stats-option-sweep-<VARIANT>.csv
```

Gate for each variant:

- no runner errors;
- no invalid solved witnesses;
- output config records the exact extra clingo arg;
- solved/timeout count is recorded;
- solved rows contain `solver_metadata.clingo_statistics`.

### Phase 6: Analyze Search Shape

For baseline and every variant, extract:

- solved count;
- timeout count;
- invalid witness count;
- per-row elapsed seconds;
- `solver_metadata.clingo_control_args`;
- clingo statistics keys available from solved rows;
- choices, conflicts, restarts, models, and solving time values;
- explicit `missing` entries for every unavailable statistics key.

Use `jq` for extraction. Generated summaries stay uncommitted diagnostics.

Gate:

- every variant appears in the comparison table;
- missing statistics keys are recorded as missing, not inferred.

### Phase 7: Experiment Record and Promotion

Write:

`experiments/2026-05-20-aba-se-st-clingo-stats-option-sweep.md`

The record must include:

- branch;
- source/test commits;
- exact cohort;
- exact commands;
- baseline result;
- every option variant result;
- invalid witness counts;
- available clingo statistics;
- kept/abandoned decision for every option family;
- direct recommendation:
  - `go`: create a production optimization workstream naming the exact clingo
    option or encoding deletion target and metric gate;
  - `no-go`: do not change production clingo options; move to an encoding
    architecture workstream.

Promote to `main`:

- the diagnostic source/test commit;
- the experiment record commit.

Do not promote generated diagnostics.

## Metric Gates

Diagnostic plumbing is complete when:

- focused tests pass;
- the hard-coded inline `Control(["--models=0", "--warn=none"])` spelling is
  gone;
- default sparse/narrow stable auto routing remains clingo multishot;
- default calls do not collect statistics.

Option sweep is complete when:

- baseline plus all eleven variants ran on the exact five-row cohort;
- every solved row passed witness validation;
- every variant has solved/timeout counts recorded;
- clingo statistics were captured for every solved row where clingo returned
  statistics;
- the experiment record states go/no-go.

Kept result threshold:

- `go` requires at least one variant to solve more than `0/5` rows with `0`
  invalid witnesses, or to expose a deterministic clingo statistic pattern that
  names a concrete next encoding deletion target.
- `no-go` is required when every variant remains `0/5` solved and statistics do
  not identify a concrete encoding target.

## Stop Conditions

- Stop when branch creation is blocked by tracked dirty files.
- Stop when the manifest is not exactly five `SE-ST` rows.
- Stop when a focused test failure is outside the owned paths.
- Stop when a benchmark returns a runner error for the baseline.
- Stop when any variant returns an invalid witness.
- Stop when clingo rejects a documented option; record the rejected option in
  the experiment record before continuing to the remaining variants.
