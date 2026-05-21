# Workstream: ABA Timeout Py-Spy Triage

Date: 2026-05-20

## Requested Outcome

Identify the next production experiment for the remaining ABA 10x10 timeout
cohort by profiling representative `SE-PR` and `SE-ST` timeout rows through the
real ICCMA worker path with py-spy.

## Current Evidence

- `experiments/2026-05-20-direct-asp-sparse-narrow-routing.md` promoted stable
  sparse/narrow `backend="auto"` routing to ASP.
- `data/iccma/2025/runs/direct-asp-auto-10x10-validated.json` reports `9`
  solved and `11` timed out at the 30 second gate.
- Timeout cohort:
  - `SE-PR`: `6` timeout rows, still routed through native sparse/narrow SAT.
  - `SE-ST`: `5` timeout rows, routed through ASP when clingo is available.

## Scope

Owned documentation:

- this workstream file
- `experiments/YYYY-MM-DD-aba-timeout-pyspy-triage.md`

Owned generated diagnostics:

- `data/iccma/2025/runs/aba-timeout-pyspy-triage-*.json`
- `data/iccma/2025/runs/aba-timeout-pyspy-triage-*.csv`
- `data/iccma/2025/profiles/aba-timeout-pyspy-triage/**`

Generated diagnostics are not source edits and are not committed unless a later
user request explicitly asks to promote them.

No production code is owned by this triage workstream.

## Representatives

Profile exactly these first:

- `SE-PR` timeout representative:
  `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`
- `SE-ST` timeout representative:
  `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`

These are the first timeout rows in each subtrack from
`direct-asp-auto-10x10-validated.json`.

## Ordered Phases

### Phase 0: Branch

1. Verify current branch and tracked-file cleanliness.
2. Create experiment branch:
   `exp/aba-timeout-pyspy-triage`

Gate: no tracked dirty files before branch creation.

### Phase 1: `SE-PR` Native SAT Timeout Profile

Run:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-timeout-pyspy-triage\se-pr-auto --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-timeout-pyspy-triage-se-pr-auto.json --output-csv data\iccma\2025\runs\aba-timeout-pyspy-triage-se-pr-auto.csv
```

Gate: profile file exists and the benchmark row records either `profiled`,
`timeout`, or `solved`, with no runner error.

### Phase 2: `SE-ST` ASP Timeout Profile

Run:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-timeout-pyspy-triage\se-st-auto --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-timeout-pyspy-triage-se-st-auto.json --output-csv data\iccma\2025\runs\aba-timeout-pyspy-triage-se-st-auto.csv
```

Gate: profile file exists and the benchmark row records either `profiled`,
`timeout`, or `solved`, with no runner error.

### Phase 3: Classify Hot Path

For each profile, read the raw py-spy file and classify the dominant stack:

- PySAT/Z3/native SAT solve loop;
- clingo solve/grounding;
- Python encoding/conversion overhead;
- parsing/validation/runner overhead;
- inconclusive.

The classification must cite the profile path and the dominant stack names.

### Phase 4: Experiment Record

Write:

`experiments/YYYY-MM-DD-aba-timeout-pyspy-triage.md`

The record must include:

- branch;
- representative rows;
- exact commands;
- profile paths;
- row outcomes;
- dominant stack classification;
- next production experiment recommendation;
- generated diagnostics not committed.

## Decision Rules

- If `SE-PR` is native SAT solve dominated, next experiment is explicit
  `SE-PR` ASP-vs-SAT measurement on the timeout cohort.
- If `SE-ST` is clingo dominated, next experiment targets ASP grounding/solver
  shape, not native SAT.
- If either profile is dominated by Python setup or validation, next experiment
  targets that overhead before solver changes.
- If a profile is inconclusive, rerun the same representative with a longer
  profile duration before choosing a production experiment.

## Stop Conditions

- Stop if branch creation is blocked by tracked dirty files.
- Stop if py-spy is unavailable through `uv tool run py-spy`.
- Stop if a benchmark command returns a runner error instead of a profile,
  timeout, or solved row.

