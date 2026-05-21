# ABA SE-PR boundary ASP stability

## Branch

- `exp/aba-se-pr-boundary-asp-stability`

## Boundary Row

- Instance: `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`
- Subtrack: `SE-PR`
- Backend: `asp`

## Commands

Five 30-second ASP-only trials:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run1.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run1.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run2.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run2.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run3.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run3.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run4.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run4.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run5.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout30-run5.csv
```

Three 35-second ASP-only trials:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run1.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run1.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run2.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run2.csv
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run3.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-timeout35-run3.csv
```

Raw py-spy profile:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-pr-boundary-asp-stability --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-profile.json --output-csv data\iccma\2025\runs\aba-se-pr-boundary-asp-stability-profile.csv
```

## Trial Results

30-second trials:

| Run | Status | Elapsed seconds | Validation | Solver | Solver calls |
| --- | --- | ---: | --- | --- | ---: |
| 1 | timeout | 35.012867400073446 | not_checked | | |
| 2 | timeout | 35.01431060000323 | not_checked | | |
| 3 | solved | 33.13097529998049 | valid | clingo_multishot | 2 |
| 4 | solved | 33.2587231999496 | valid | clingo_multishot | 2 |
| 5 | solved | 33.83714479999617 | valid | clingo_multishot | 2 |

35-second trials:

| Run | Status | Elapsed seconds | Validation | Solver | Solver calls |
| --- | --- | ---: | --- | --- | ---: |
| 1 | solved | 38.5313500999473 | valid | clingo_multishot | 2 |
| 2 | solved | 35.35946359997615 | valid | clingo_multishot | 2 |
| 3 | solved | 33.96892919996753 | valid | clingo_multishot | 2 |

The benchmark worker has an outer timeout slack over `--timeout-seconds`; these
elapsed values are the benchmark-recorded end-to-end times.

## Py-Spy Profile

Profile path:

`data/iccma/2025/profiles/aba-se-pr-boundary-asp-stability/aba-SE-PR-asp-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-e20e45137f36.raw.txt`

Profile row status: `profiled`, reason `profile_duration_elapsed`.

Dominant stack:

`solve_aba_single_extension -> _solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_preferred_extension -> enumerate_preferred -> _solve_one -> solve (clingo/control.py) -> _c_call`

Dominant sample count observed: `2467`.

Secondary observed stacks:

- `enumerate_preferred -> _new_control -> ground (clingo/control.py)`: `7`
  samples.
- `enumerate_preferred -> _new_control -> add (clingo/control.py)`: `8`
  samples.
- `encode_aba_theory`: single-digit samples.

Classification: clingo solve.

## Generated Diagnostics

Generated and not committed:

- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run1.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run1.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run2.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run2.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run3.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run3.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run4.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run4.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run5.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout30-run5.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout35-run1.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout35-run1.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout35-run2.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout35-run2.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout35-run3.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-timeout35-run3.csv`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-profile.json`
- `data/iccma/2025/runs/aba-se-pr-boundary-asp-stability-profile.csv`
- `data/iccma/2025/profiles/aba-se-pr-boundary-asp-stability/aba-SE-PR-asp-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-e20e45137f36.raw.txt`

## Recommendation

No-go for an immediate production optimization.

Why:

- The row is unstable at the 30-second gate: `3/5` solved and `2/5` timed out.
- The 35-second trials solve, but still hover near the boundary with recorded
  elapsed values from `33.97` to `38.53` seconds.
- The profile is dominated by opaque clingo solve time, not Python encoding,
  grounding/add overhead, parsing, or runner overhead.
- There is no concrete local non-semantic bottleneck to target with a small
  operational contract.

Leave `SE-PR` auto routing unchanged. Move attention to the large `SE-ST`
clingo timeout cohort, or first create a deeper ASP solver-shape workstream if
we want to attack clingo solve time directly.

## Retroactive protocol audit

Protocol status: true diagnosed no-go.

This record satisfies the new failure-analysis standard: it repeats the
boundary row, records instability at the 30-second gate, and profiles the real
ASP path. The dominant cost is `clingo.Control.solve`, not Python encoding,
grounding, parsing, or runner overhead.

Required follow-up: any future `SE-PR` ASP route work must change clingo solve
shape, not just route selection.
