# Cadical195 sparse narrow engine swap

Date: 2026-05-20

Status: measured on experiment branch; source change not promoted.

Experiment branch: `exp/aba-sparse-narrow-cadical195-engine`.

Evidence commits on experiment branch:
- `8be1ccc` Test cadical195 for sparse narrow stable SAT.
- `e0d51d3` Record cadical195 sparse narrow experiment.

Changed path on experiment branch:
- `src/argumentation/aba_sat.py`

Hypothesis: changing only `_NativeSparseNarrowStableSolver` from PySAT
`glucose4` to PySAT `cadical195` would improve the sparse/narrow hard stable
row enough to justify considering CaDiCaL-specific follow-up work.

Gate:
- Targeted sparse/narrow tests:
  `uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py`
- Hard-row benchmark, 150-second solver cap:
  `uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 150 --output-json data\iccma\2025\runs\engine-cadical195-hard-row.json --output-csv data\iccma\2025\runs\engine-cadical195-hard-row.csv`

Baseline on `main`:
- Engine: PySAT `glucose4`.
- Status: solved.
- Elapsed: 144.82884259999264 seconds.
- Witness size: 148.
- Validation: valid.
- Solver checks: 5.
- Loop formulas: 344.
- Learned clauses: 33033.
- Clingo calls: 0.

Cadical195 branch result:
- Engine: PySAT `cadical195`.
- Status: solved.
- Elapsed: 134.83843040000647 seconds.
- Witness size: 148.
- Validation: valid.
- Solver checks: 10.
- Loop formulas: 649.
- Learned clauses: 33338.
- Clingo calls: 0.

Profile command on the `cadical195` branch:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 150 --profile-dir data\iccma\2025\profiles\engine-cadical195-hard-row --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\engine-cadical195-hard-row-profile.json --output-csv data\iccma\2025\runs\engine-cadical195-hard-row-profile.csv
```

Profile result:

- row status: `profiled`
- reason: `profile_duration_elapsed`
- elapsed: `25.584035900072195` seconds
- profile:
  `data\iccma\2025\profiles\engine-cadical195-hard-row\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.raw.txt`

Hot frames:

- `native_sparse_narrow_sat_extension -> _native_sparse_narrow_stable_extension -> stable_extension -> solve (pysat\solvers.py)`: `2441` samples
- loop-formula generation stacks under `_unsupported_derived_loop_formulas`
  and `_loop_formula_for`: tens of samples total
- completion clause construction and parsing: single-digit samples

Compared with
`experiments/2026-05-20-glucose4-hard-row-full-profile.md`, the bottleneck did
not move: both `glucose4` and `cadical195` are dominated by raw PySAT/CDCL solve
time, not Python loop-formula code.

Outcome: weakly positive but not a crack.

Decision: keep the branch as experiment evidence. Do not promote this as a
standalone optimization. `cadical195` was about 10 seconds faster on the hard
row, but it still missed the 30-second focused gate by a wide margin and
increased the number of CEGAR checks and loop formulas. The result is enough
to keep CaDiCaL-specific follow-up possible, including an IPASIR-UP prototype,
but not enough to justify replacing `glucose4` on `main` without broader row
coverage. The profile narrows the follow-up target: CaDiCaL-specific work must
change CDCL search behavior itself, not Python loop generation.

Generated diagnostics:
- `data\iccma\2025\runs\engine-baseline-glucose4-hard-row.json`
- `data\iccma\2025\runs\engine-baseline-glucose4-hard-row.csv`
- `data\iccma\2025\runs\engine-cadical195-hard-row.json`
- `data\iccma\2025\runs\engine-cadical195-hard-row.csv`
- `data\iccma\2025\profiles\engine-cadical195-hard-row\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.raw.txt`
- `data\iccma\2025\runs\engine-cadical195-hard-row-profile.json`
- `data\iccma\2025\runs\engine-cadical195-hard-row-profile.csv`

These generated diagnostics were not committed.

## Retroactive protocol audit

Protocol status: weak positive metric result; diagnosis complete.

The record validly shows that `cadical195` was faster than `glucose4` on the
hard row but still far from the 30-second gate. The follow-up profile shows the
bottleneck stayed in raw PySAT/CDCL solve time, not Python loop-formula code.

Required follow-up: any CaDiCaL-specific solver change should compare profiles
or solver telemetry against both the `glucose4` full profile and this
`cadical195` metric baseline.
