# Workstream: ABA SE-PR ASP-vs-SAT Timeout Measurement

Date: 2026-05-20

## Requested Outcome

Measure whether explicit ASP is better than the current native sparse/narrow
SAT route on the six remaining `SE-PR` timeout rows from the direct ASP routing
10x10 fixture.

## Current Evidence

- `experiments/2026-05-20-aba-timeout-pyspy-triage.md` classified the
  representative `SE-PR` timeout as native SAT solve dominated.
- Current promoted 10x10 gate:
  `data/iccma/2025/runs/direct-asp-auto-10x10-validated.json`
  reports `9` solved and `11` timed out.
- The six `SE-PR` timeout rows are:
  - `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`
  - `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba`
  - `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

## Scope

Owned documentation:

- this workstream file
- `experiments/YYYY-MM-DD-aba-se-pr-asp-vs-sat.md`

Owned generated diagnostics:

- `data/iccma/2025/runs/aba-se-pr-timeouts-manifest.json`
- `data/iccma/2025/runs/aba-se-pr-asp-vs-sat.json`
- `data/iccma/2025/runs/aba-se-pr-asp-vs-sat.csv`

Generated diagnostics are not committed.

No production code is owned unless the measurement gate passes and a separate
route-contract slice is written.

## Ordered Phases

### Phase 0: Branch

1. Verify current branch and tracked-file cleanliness.
2. Create experiment branch:
   `exp/aba-se-pr-asp-vs-sat`

### Phase 1: Build Timeout Manifest

Generate:

```powershell
jq '[.rows[] | select(.subtrack == "SE-PR" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-pr-timeouts-manifest.json
```

Gate: manifest contains exactly six rows.

### Phase 2: Backend Matrix Measurement

Run:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-pr-timeouts-manifest.json --subtrack SE-PR --backend auto --backend asp --backend sat --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-asp-vs-sat.json --output-csv data\iccma\2025\runs\aba-se-pr-asp-vs-sat.csv
```

Gate: no runner errors and no invalid solved witnesses.

### Phase 3: Decide

Write:

`experiments/YYYY-MM-DD-aba-se-pr-asp-vs-sat.md`

The record must include:

- branch;
- manifest source;
- exact command;
- per-backend solved/timeout counts;
- validation result counts;
- whether ASP beats native SAT on the six-row cohort;
- keep/abandon recommendation.

## Promotion Rule

Do not change production routing in this measurement workstream.

If explicit ASP solves at least one row that auto/SAT time out on, and has no
invalid solved witnesses, the next workstream may propose a route-contract
change for `SE-PR` auto routing. If ASP does not beat SAT, record the failed
gate and abandon route promotion.

## Stop Conditions

- Stop if tracked dirty files block branch creation.
- Stop if the manifest does not contain exactly six rows.
- Stop if the backend matrix returns a runner error.

