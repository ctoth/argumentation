# Workstream: ABA SE-PR Boundary ASP Stability

Date: 2026-05-20

## Requested Outcome

Determine whether the boundary preferred ASP row can be made into a reliable
production improvement, or whether `SE-PR` auto routing should stay on the
current native sparse/narrow SAT path.

This workstream is evidence-only. It does not change production routing or
solver code. A production optimization requires a follow-up workstream with a
specific deletion target and metric gate.

## Boundary Row

Profile and measure exactly this row first:

`ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`

Task:

- subtrack: `SE-PR`
- backend: `asp`
- expected solver metadata:
  - `solver == "clingo_multishot"`
  - `algorithm == "first-model-witness"`
  - `solver_calls <= 2`

## Current Evidence

- `experiments/2026-05-20-aba-se-pr-asp-vs-sat.md`
  - isolated six-row backend matrix:
    - `asp`: `1` solved, `5` timeout;
    - `auto`: `0` solved, `6` timeout;
    - `sat`: `0` solved, `6` timeout;
  - boundary row ASP matrix elapsed: `34.79867479996756`;
  - boundary row ASP 30-second recheck elapsed: `33.00011160003487`.
- `experiments/2026-05-20-aba-se-pr-asp-routing.md`
  - blanket `SE-PR` auto-to-ASP production experiment failed;
  - full 10x10 result stayed `9` solved and `11` timeout;
  - the boundary row timed out in the full fixture at `30.009533`.

## Final State

The final committed artifact is:

`experiments/YYYY-MM-DD-aba-se-pr-boundary-asp-stability.md`

It must include:

- branch;
- exact commands;
- repeated-trial timing table;
- py-spy profile path;
- dominant stack classification;
- solver metadata for every solved trial;
- a direct go/no-go recommendation:
  - `go`: write a separate production optimization workstream for the identified
    bottleneck;
  - `no-go`: leave `SE-PR` auto routing unchanged and move attention to the
    large `SE-ST` clingo timeout cohort.

## Scope

Owned documentation:

- this workstream file
- `experiments/YYYY-MM-DD-aba-se-pr-boundary-asp-stability.md`

Owned generated diagnostics:

- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-*.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-*.csv`
- `data/iccma/2025/profiles/aba-se-pr-boundary-asp-stability/**`

Generated diagnostics are not committed.

No production files are owned in this workstream.

## Ordered Phases

### Phase 0: Branch

1. Verify current branch and tracked-file cleanliness:

```powershell
git branch --show-current
git status --short
```

2. Create experiment branch:

```powershell
git switch -c exp/aba-se-pr-boundary-asp-stability
```

Gate: no tracked dirty files before branch creation.

### Phase 1: Repeated 30-Second Trials

Run five ASP-only trials at the production timeout:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run1.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run1.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run2.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run2.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run3.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run3.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run4.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run4.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run5.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run5.csv
```

Gate:

- record solved/timeout for all five runs;
- record elapsed time for solved runs;
- record validation status for solved runs;
- record `solver_calls` for solved runs.

### Phase 2: Repeated 35-Second Trials

Run three ASP-only trials with a 35-second solver timeout:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run1.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run1.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run2.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run2.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run3.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run3.csv
```

Gate:

- at least one 35-second run must solve validly before profiling; otherwise the
  row is not a near-boundary optimization target for this cycle.

### Phase 3: Py-Spy Profile

Run one raw py-spy profile through the real worker path:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-pr-boundary-asp-stability --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-profile.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-profile.csv
```

Gate:

- profile file exists;
- row status is `profiled`, `solved`, or `timeout`;
- no runner error.

### Phase 4: Classify Bottleneck

Classify the dominant stack from the raw profile as exactly one of:

- clingo solve;
- clingo grounding/add;
- preferred refinement second call;
- Python fact encoding;
- parsing/runner overhead;
- inconclusive.

The experiment record must cite the profile path and the dominant stack names.

### Phase 5: Recommendation

Write the experiment record and commit it.

Recommendation rule:

- `go` only if repeated trials show the row is within a small, stable margin of
  the 30-second gate and py-spy identifies a concrete non-semantic bottleneck.
- `no-go` if the row is unstable at 30 seconds, fails most 35-second runs, or
  is dominated by opaque clingo solve time with no local operational contract.

## Metric Gates

The workstream is complete when all of these are true:

- five 30-second trials are recorded;
- three 35-second trials are recorded;
- one py-spy profile is recorded;
- the bottleneck classification is written;
- the experiment record is committed on `main`.

## Stop Conditions

- Stop if branch creation is blocked by tracked dirty files.
- Stop if py-spy is unavailable through `uv tool run py-spy`.
- Stop if any benchmark returns a runner error.
- Stop if a generated diagnostic path cannot be written.

