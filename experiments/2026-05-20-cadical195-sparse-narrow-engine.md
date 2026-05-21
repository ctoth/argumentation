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

Outcome: weakly positive but not a crack.

Decision: keep the branch as experiment evidence. Do not promote this as a
standalone optimization. `cadical195` was about 10 seconds faster on the hard
row, but it still missed the 30-second focused gate by a wide margin and
increased the number of CEGAR checks and loop formulas. The result is enough
to keep CaDiCaL-specific follow-up possible, including an IPASIR-UP prototype,
but not enough to justify replacing `glucose4` on `main` without broader row
coverage.

Generated diagnostics:
- `data\iccma\2025\runs\engine-baseline-glucose4-hard-row.json`
- `data\iccma\2025\runs\engine-baseline-glucose4-hard-row.csv`
- `data\iccma\2025\runs\engine-cadical195-hard-row.json`
- `data\iccma\2025\runs\engine-cadical195-hard-row.csv`

These generated diagnostics were not committed.

## Retroactive protocol audit

Protocol status: weak positive metric result; failure diagnosis incomplete.

The record validly shows that `cadical195` was faster than `glucose4` on the
hard row but still far from the 30-second gate. It does not profile the
`cadical195` branch, so it does not fully explain why the engine swap still
missed the gate or why it increased CEGAR checks and loop formulas.

Required follow-up: any CaDiCaL-specific solver change should compare profiles
or solver telemetry against both the `glucose4` full profile and this
`cadical195` metric baseline.
