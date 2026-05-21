# ABA SE-ST clingo solver-shape investigation

Date: 2026-05-20

Branch: `exp/aba-se-st-clingo-solver-shape`

Workstream: `notes/workstream-aba-se-st-clingo-solver-shape-2026-05-20.md`

## Hypothesis

The remaining large sparse/narrow `SE-ST` ABA timeout cohort is no longer
explained by Python encoding, route selection, or witness validation overhead.
The dominant cost should be inside clingo's stable-model search for the current
single-extension ABA encoding.

## Cohort

The timeout manifest was generated from
`data/iccma/2025/runs/direct-asp-auto-10x10-validated.json`:

```powershell
jq '[.rows[] | select(.subtrack == "SE-ST" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-st-clingo-solver-shape-timeouts.json
```

Validation checks:

```powershell
jq 'length' data\iccma\2025\runs\aba-se-st-clingo-solver-shape-timeouts.json
jq '[.[] | .subtrack] | unique' data\iccma\2025\runs\aba-se-st-clingo-solver-shape-timeouts.json
```

Result:

- Manifest length: `5`
- Unique subtracks: `["SE-ST"]`

Rows:

- `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

## Baseline evidence

Command:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-clingo-solver-shape-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-st-clingo-solver-shape-baseline.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-solver-shape-baseline.csv
```

Summary:

```json
{
  "by_backend": {
    "auto": {
      "timeout": 5
    }
  },
  "by_solver_class": {
    "aba/single-extension/stable": 5
  },
  "total_rows": 5
}
```

Witness validation check:

```powershell
jq '[.rows[].witness_validation_results.auto] | group_by(.) | map({status: .[0], count: length})' data\iccma\2025\runs\aba-se-st-clingo-solver-shape-baseline.json
```

Result:

```json
[
  {
    "status": "not_checked",
    "count": 5
  }
]
```

No row solved in the baseline run, so there were no invalid solved witnesses.

## Profile evidence

Small representative command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-clingo-solver-shape\small --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-small.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-small.csv
```

Small representative output:

- Result status: `profiled`
- Reason: `profile_duration_elapsed`
- Profile:
  `data/iccma/2025/profiles/aba-se-st-clingo-solver-shape/small/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`

Small representative classification:

- `solve_aba_single_extension -> _solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_stable_extension -> _solve_one -> solve (clingo\control.py:1065) -> _c_call`: `2450` samples
- `find_stable_extension -> _new_control -> ground (clingo\control.py:566)`: `9` samples
- `find_stable_extension -> _new_control -> add (clingo\control.py:320)`: `17` samples
- `encode_aba_theory`: single-digit stacks

Large representative command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-clingo-solver-shape\large --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-large.json --output-csv data\iccma\2025\runs\aba-se-st-clingo-solver-shape-profile-large.csv
```

Large representative output:

- Result status: `profiled`
- Reason: `profile_duration_elapsed`
- Profile:
  `data/iccma/2025/profiles/aba-se-st-clingo-solver-shape/large/aba-SE-ST-auto-abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba-d959fab41391.raw.txt`

Large representative classification:

- `solve_aba_single_extension -> _solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_stable_extension -> _solve_one -> solve (clingo\control.py:1065) -> _c_call`: `2416` samples
- `find_stable_extension -> _new_control -> ground (clingo\control.py:566)`: `22` samples
- `find_stable_extension -> _new_control -> add (clingo\control.py:320)`: `23` samples
- `encode_aba_theory`: single-digit stacks, except one `repr` stack with `4` samples

## Changed paths

No production code was changed by this experiment.

Generated diagnostic artifacts, intentionally not promoted:

- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-timeouts.json`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-baseline.json`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-baseline.csv`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-profile-small.json`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-profile-small.csv`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-profile-large.json`
- `data/iccma/2025/runs/aba-se-st-clingo-solver-shape-profile-large.csv`
- `data/iccma/2025/profiles/aba-se-st-clingo-solver-shape/small/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`
- `data/iccma/2025/profiles/aba-se-st-clingo-solver-shape/large/aba-SE-ST-auto-abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba-d959fab41391.raw.txt`

## Outcome

The hypothesis is supported.

Both representative profiles spend almost all observed samples inside
`clingo.Control.solve`, not in Python theory encoding, clingo program addition,
grounding, route selection, or witness validation.

## Decision

Abandon this experiment branch after promoting this record to `main`.

Do not make a production solver change from this experiment alone. The evidence
does not identify a Python-side hot path to optimize and does not justify
rewriting the current stable ABA encoding blindly.

## Next workstream

Create a separate clingo statistics and option-sweep workstream for this exact
five-row `SE-ST` timeout cohort.

The next executable contract should capture deterministic clingo search
statistics and solver configuration for each row before attempting a production
change. The gate should compare solved count, invalid witness count, and clingo
search-shape metrics against the current all-timeout baseline.
