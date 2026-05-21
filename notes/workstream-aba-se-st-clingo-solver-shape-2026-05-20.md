# Workstream: ABA SE-ST Clingo Solver-Shape Investigation

Date: 2026-05-20

## Requested Outcome

Find the next principled production experiment for the remaining large
`SE-ST` sparse/narrow ABA timeout cohort now that stable auto routing already
uses ASP/clingo.

This workstream is evidence-first. It does not promote a route flip. It either
identifies a concrete ASP/clingo solver-shape optimization with an executable
metric gate, or records that the current rows are opaque clingo-solve hard
cases and should not receive a speculative production change.

## Current Evidence

- `experiments/2026-05-20-direct-asp-sparse-narrow-routing.md`
  promoted sparse/narrow `SE-ST` auto routing through ASP/clingo and improved
  the 10x10 fixture from `5/20` solved to `9/20` solved.
- `experiments/2026-05-20-aba-timeout-pyspy-triage.md`
  classified the representative large `SE-ST` timeout as clingo-solve
  dominated, not Python setup or encoding overhead.
- `experiments/2026-05-20-aba-se-pr-boundary-asp-stability.md`
  ruled out immediate `SE-PR` production work: the boundary preferred row is
  unstable and also dominated by clingo solve time.
- Current remaining `SE-ST` timeout cohort from
  `data/iccma/2025/runs/direct-asp-auto-10x10-validated.json`:
  - `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

All five rows are flat large stable ABA rows with `1400` assumptions, low rule
arity, medium rule density, and no preprocessing collapse.

## Relevant Code Surface

- Stable single-extension ASP route:
  `src/argumentation/solver.py::_solve_asp_aba_single_extension`
- ASP dispatch:
  `src/argumentation/aba_asp.py::_solve_multishot`
- Stable solve implementation:
  `src/argumentation/aba_incremental.py::AbaIncrementalSolver.find_stable_extension`
- Clingo control construction:
  `src/argumentation/aba_incremental.py::AbaIncrementalSolver._new_control`

Current stable path shape:

- `find_stable_extension` builds one clingo `Control`;
- it adds the stable constraint `:- out(X), not defeated(X).`;
- it calls `_solve_one` exactly once;
- `_new_control` currently uses clingo arguments `["--models=0", "--warn=none"]`;
- existing metadata already records `solver_calls`, `algorithm`, and
  `solver="clingo_multishot"` for solved rows.

## Final State

The final committed artifact is:

`experiments/YYYY-MM-DD-aba-se-st-clingo-solver-shape.md`

It must include:

- branch;
- exact timeout cohort manifest;
- exact commands;
- row outcomes;
- profile paths;
- dominant stack classifications;
- any clingo configuration or encoding variants tested;
- per-variant solved/timeout counts;
- valid/invalid witness counts;
- direct recommendation:
  - `go`: create a separate production optimization workstream with a named
    deletion target and metric gate;
  - `no-go`: do not change the stable ASP production path yet.

## Scope

Owned documentation:

- this workstream file
- `experiments/YYYY-MM-DD-aba-se-st-clingo-solver-shape.md`

Owned generated diagnostics:

- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-*.json`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-*.csv`
- `data/iccma/2025/profiles/aba-se-st-clingo-solver-shape/**`

Generated diagnostics are not committed.

No production solver change is owned in this workstream. If a source edit is
needed to expose diagnostics or a configurable clingo option, it must be
committed as a diagnostic-only experiment slice and must not change default
production behavior.

## Ordered Phases

### Phase 0: Branch

1. Verify current branch and tracked-file cleanliness:

```powershell
git branch --show-current
git status --short
```

2. Create experiment branch:

```powershell
git switch -c exp/aba-se-st-clingo-solver-shape
```

Gate: no tracked dirty files before branch creation.

### Phase 1: Build Timeout Cohort Manifest

Generate the exact five-row `SE-ST` timeout manifest:

```powershell
jq '[.rows[] | select(.subtrack == "SE-ST" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-st-clingo-solver-shape-timeouts.json
```

Gate:

- manifest contains exactly `5` rows;
- every row has `subtrack == "SE-ST"`.

### Phase 2: Baseline Cohort Recheck

Run the five-row cohort through current production auto routing:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-solver-shape-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-st-clingo-solver-shape-baseline.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-solver-shape-baseline.csv
```

Gate:

- no runner errors;
- no invalid solved witnesses;
- record solved/timeout count.

### Phase 3: Representative Py-Spy Profiles

Profile exactly two representatives:

- smaller representative:
  `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
- larger representative:
  `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

Commands:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-clingo-solver-shape\small --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-small.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-small.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-clingo-solver-shape\large --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-large.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-large.csv
```

Gate:

- both profile files exist;
- row status is `profiled`, `solved`, or `timeout`;
- no runner error.

### Phase 4: Classify Bottleneck

For each profile, classify the dominant stack as exactly one of:

- clingo solve;
- clingo grounding/add;
- Python fact encoding;
- preprocessing/simplification;
- parsing/runner overhead;
- inconclusive.

The experiment record must cite the profile paths and dominant stack names.

### Phase 5: Solver-Shape Variant Plan

Only if Phase 4 shows clingo solve dominance, write a bounded follow-up variant
plan inside the experiment record. The plan must name one concrete variant
family and its metric gate before any production implementation starts.

Allowed variant families for the next workstream:

- clingo option sweep by explicit `Control` arguments;
- stable encoding split or added deterministic constraints;
- clingo statistics capture to compare choices/conflicts/restarts across the
  five-row cohort.

Do not implement a variant in this workstream unless the variant can be exposed
without changing default production behavior and has a testable operational
contract.

### Phase 6: Experiment Record and Promotion

Write and commit:

`experiments/YYYY-MM-DD-aba-se-st-clingo-solver-shape.md`

Promote only the experiment record to `main`. Do not promote generated
diagnostics.

## Metric Gates

The workstream is complete when all of these are true:

- five-row timeout manifest recorded;
- baseline five-row cohort result recorded;
- two py-spy profiles recorded;
- bottleneck classification recorded;
- next go/no-go recommendation recorded;
- experiment record committed on `main`.

## Stop Conditions

- Stop if branch creation is blocked by tracked dirty files.
- Stop if the timeout manifest does not contain exactly five `SE-ST` rows.
- Stop if a benchmark returns a runner error.
- Stop if py-spy is unavailable through `uv tool run py-spy`.
- Stop if generated diagnostics cannot be written.

