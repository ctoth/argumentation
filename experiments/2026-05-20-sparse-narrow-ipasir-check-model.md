# Sparse/Narrow IPASIR Check-Model Solver

Date: 2026-05-20

Status: measured on experiment branch; source change not promoted.

Experiment branch: `exp/aba-sparse-narrow-ipasir-check-model`

Evidence commits:
- `f38493d` routed sparse/narrow loop refinement through an IPASIR check-model propagator.
- `71f3aa3` narrowed observed variables to assumption and derived-literal variables.
- `0426a72` added route telemetry contracts.

Hypothesis: moving loop-formula rejection into a CaDiCaL IPASIR check-model
callback will avoid the late repeated outer SAT solves that dominated the
glucose4 profile and solve-timing vector.

Single variable: replace the outer Python loop that calls `solver.solve()` once
per rejected candidate with one `cadical195` solve using a check-model
propagator; observe only assumption and derived-literal variables.

Baseline:
- Command: `uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --output-json data\iccma\2025\runs\profile-glucose4-hard-row-full.json --output-csv data\iccma\2025\runs\profile-glucose4-hard-row-full.csv`
- Result: main/glucose4 solved the hard row in `151.83979749993887s`.
- Supporting baseline: `cadical195` engine-only solved the same row in
  `134.83843040000647s`.

Experiment result:
- Command: `uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --output-json data\iccma\2025\runs\ipasir-check-model-hard-row.json --output-csv data\iccma\2025\runs\ipasir-check-model-hard-row.csv`
- Result: timeout, backend reason `timeout>245.0`; no solved backend.

Fast contracts:
- `uv run pytest -q tests\test_aba_sparse_narrow_native_sat.py`
- `uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py`
- Result: `8 passed`.

Metric gate:
- Pass if the hard row solves under the `240s` row timeout and improves over
  the current `glucose4` baseline.
- Result: failed by timeout.

Outcome: negative.

Decision: abandon this source delta. The narrow-observed check-model callback
is semantically valid but slower than both the current `glucose4` main route and
the `cadical195` engine-only route on the hard row.

Generated diagnostics:
- `data\iccma\2025\runs\ipasir-check-model-hard-row.json`
- `data\iccma\2025\runs\ipasir-check-model-hard-row.csv`

These generated diagnostics were not committed.

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

The record proves that the check-model callback route timed out and should not
be promoted. It does not profile that failed branch, so it does not prove why
the callback shape was slower than `glucose4` and `cadical195` engine-only.

Required follow-up: before rejecting all check-model-style propagators, profile
the real failed worker path or add callback/solver telemetry that shows where
the timeout is spent.
