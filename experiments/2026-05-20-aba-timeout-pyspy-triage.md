# ABA timeout py-spy triage

## Branch

- `exp/aba-timeout-pyspy-triage`

## Representatives

- `SE-PR`: `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`
- `SE-ST`: `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`

These were the first timeout representatives for each subtrack in
`data/iccma/2025/runs/direct-asp-auto-10x10-validated.json`.

## Commands

`SE-PR` native SAT auto profile:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-timeout-pyspy-triage\se-pr-auto --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-timeout-pyspy-triage-se-pr-auto.json --output-csv data\iccma\2025\runs\aba-timeout-pyspy-triage-se-pr-auto.csv
```

`SE-ST` ASP auto profile:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-timeout-pyspy-triage\se-st-auto --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-timeout-pyspy-triage-se-st-auto.json --output-csv data\iccma\2025\runs\aba-timeout-pyspy-triage-se-st-auto.csv
```

## Outcomes

`SE-PR`:

- Row status: `profiled`
- Reason: `profile_duration_elapsed`
- Profile:
  `data/iccma/2025/profiles/aba-timeout-pyspy-triage/se-pr-auto/aba-SE-PR-auto-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-2cc0226bc564.raw.txt`
- Dominant stack:
  `native_sparse_narrow_sat_extension -> _native_sparse_narrow_stable_extension -> stable_extension -> solve (pysat/solvers.py)`
- Dominant sample count observed in raw profile: `2480`
- Classification: native SAT solve dominated.

`SE-ST`:

- Row status: `profiled`
- Reason: `profile_duration_elapsed`
- Profile:
  `data/iccma/2025/profiles/aba-timeout-pyspy-triage/se-st-auto/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`
- Dominant stack:
  `_solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_stable_extension -> _solve_one -> solve (clingo/control.py) -> _c_call`
- Dominant sample count observed in raw profile: `2463`
- Classification: clingo solve dominated.

## Generated Diagnostics

Generated and not committed:

- `data/iccma/2025/runs/aba-timeout-pyspy-triage-se-pr-auto.json`
- `data/iccma/2025/runs/aba-timeout-pyspy-triage-se-pr-auto.csv`
- `data/iccma/2025/runs/aba-timeout-pyspy-triage-se-st-auto.json`
- `data/iccma/2025/runs/aba-timeout-pyspy-triage-se-st-auto.csv`
- `data/iccma/2025/profiles/aba-timeout-pyspy-triage/se-pr-auto/aba-SE-PR-auto-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-2cc0226bc564.raw.txt`
- `data/iccma/2025/profiles/aba-timeout-pyspy-triage/se-st-auto/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`

## Recommendation

Next production experiment: measure explicit `SE-PR` ASP-vs-SAT routing on the
six remaining preferred timeout rows.

Why:

- `SE-PR` timeout is not Python setup, parsing, validation, or runner overhead;
  it is dominated by PySAT solving inside the native sparse/narrow route.
- Stable ASP timeout rows are dominated by clingo solving, not encoding or
  Python overhead, so stable improvements should target ASP solve shape later.
- The fastest near-term chance to increase the 10x10 solved count is to test
  whether preferred timeout rows also benefit from ASP routing.

The next workstream should preserve explicit `backend="sat"` and only consider
`SE-PR` `backend="auto"` promotion if an operational gate beats the current
`9/20` solved, `11/20` timeout result without invalid witnesses.

## Retroactive protocol audit

Protocol status: true diagnostic triage.

This record satisfies the profiler requirement for the initial timeout split:
`SE-PR` was native SAT solve dominated, and `SE-ST` was clingo solve dominated.
It correctly selected later workstreams from profile evidence rather than from
guessing.

Required follow-up: use this as the parent diagnostic record when auditing
later `SE-PR` and `SE-ST` route experiments.
