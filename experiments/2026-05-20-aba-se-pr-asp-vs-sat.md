# ABA SE-PR ASP-vs-SAT timeout measurement

## Branch

- `exp/aba-se-pr-asp-vs-sat`

## Manifest Source

Generated from `data/iccma/2025/runs/direct-asp-auto-10x10-validated.json`:

```powershell
jq '[.rows[] | select(.subtrack == "SE-PR" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-pr-timeouts-manifest.json
```

Manifest row count: `6`.

## Backend Matrix

Command:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-pr-timeouts-manifest.json --subtrack SE-PR --backend auto --backend asp --backend sat --timeout-seconds 35 --output-json data\iccma\2025\runs\aba-se-pr-asp-vs-sat.json --output-csv data\iccma\2025\runs\aba-se-pr-asp-vs-sat.csv
```

Backend outcomes:

- `auto`: `0` solved, `6` timeout
- `sat`: `0` solved, `6` timeout
- `asp`: `1` solved, `5` timeout

Validation outcomes:

- `asp`: `1` solved valid witness, `5` timeout not checked
- `auto`: `6` timeout not checked
- `sat`: `6` timeout not checked
- invalid solved witnesses: `0`

The ASP-only win was:

- `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`
- `auto`: timeout
- `sat`: timeout
- `asp`: solved, valid
- ASP elapsed in matrix: `34.79867479996756`

## 30 Second Recheck

Command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba --subtrack SE-PR --backend asp --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-se-pr-asp-winning-row-timeout30.json --output-csv data\iccma\2025\runs\aba-se-pr-asp-winning-row-timeout30.csv
```

Outcome:

- status: `solved`
- validation: `valid`
- elapsed recorded by benchmark: `33.00011160003487`
- solver: `clingo_multishot`
- solver calls: `2`
- algorithm: `first-model-witness`

The benchmark worker allows a small outer timeout slack over the solver timeout,
so the row is accepted as solved by the current benchmark path but is close to
the gate boundary.

## Generated Diagnostics

Generated and not committed:

- `data/iccma/2025/runs/aba-se-pr-timeouts-manifest.json`
- `data/iccma/2025/runs/aba-se-pr-asp-vs-sat.json`
- `data/iccma/2025/runs/aba-se-pr-asp-vs-sat.csv`
- `data/iccma/2025/runs/aba-se-pr-asp-winning-row-timeout30.json`
- `data/iccma/2025/runs/aba-se-pr-asp-winning-row-timeout30.csv`

## Decision

ASP beats native SAT on the `SE-PR` timeout cohort, but narrowly:

- It adds one solved preferred row over both `auto` and explicit `sat`.
- It has no invalid solved witnesses.
- The win is near the timeout boundary, so route promotion needs a contract that
  captures the specific cohort improvement and solver metadata.

Next production workstream: route `SE-PR` sparse/narrow auto through ASP when
clingo is available, preserving explicit `backend="sat"`, and gate it against
the full 10x10 fixture. The expected production improvement is from `9/20`
solved to `10/20` solved if the boundary row remains stable under the full
fixture run.

