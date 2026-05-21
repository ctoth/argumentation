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

Profiler diagnosis:
- Command: `uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --profile-dir data\iccma\2025\profiles\ipasir-check-model-hard-row --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\ipasir-check-model-hard-row-profile.json --output-csv data\iccma\2025\runs\ipasir-check-model-hard-row-profile.csv`
- Result: profiled row, reason `profile_duration_elapsed`, elapsed
  `25.152009299956262s`.
- Profile:
  `data\iccma\2025\profiles\ipasir-check-model-hard-row\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.raw.txt`
- Dominant observed stacks run through
  `stable_extension -> solve (pysat\solvers.py) -> check_model
  (argumentation\aba_sat.py:924) ->
  _unsupported_derived_loop_formulas_from_model ->
  _loop_formula_for`, with large sampled stacks at `667`, `446`, `175`,
  `85`, and `60`.
- The narrowed assignment-observation hook was not the hot path:
  `on_assignment (pysat\engines.py:589)` appeared with only `2` samples.

Failure diagnosis:
- This was a true experiment failure, not just an unchecked timeout.
- The branch did avoid the old repeated outer `solver.solve()` loop shape, but
  it paid for that by doing expensive Python unsupported-loop discovery and
  loop-formula construction from inside the IPASIR check-model callback.
- The failed part is therefore not "observing too many assignment literals";
  it is the callback architecture: every candidate model rejection invokes the
  same Python loop-formula machinery while the CDCL solve is paused.
- The salvageable asset is the telemetry/contract surface, not the production
  callback route.

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
the `cadical195` engine-only route on the hard row. Do not pursue this IPASIR
check-model design unless the callback can reject candidates with a cached,
incremental, non-Python-heavy support check instead of constructing full loop
formulas during callback execution.

Generated diagnostics:
- `data\iccma\2025\runs\ipasir-check-model-hard-row.json`
- `data\iccma\2025\runs\ipasir-check-model-hard-row.csv`
- `data\iccma\2025\runs\ipasir-check-model-hard-row-profile.json`
- `data\iccma\2025\runs\ipasir-check-model-hard-row-profile.csv`
- `data\iccma\2025\profiles\ipasir-check-model-hard-row\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.raw.txt`

These generated diagnostics were not committed.

## Retroactive protocol audit

Protocol status: `promotion no-go; profiled failure diagnosis complete`.

The record proves that the check-model callback route timed out and should not
be promoted. The py-spy follow-up shows why: the route moved rejection work into
Python `check_model` / loop-formula generation under the solver callback,
rather than making the solve loop cheap.

Required follow-up: do not revive this branch as-is. A future callback design
must first provide an operational contract showing cheap cached rejection work,
because semantic validity and narrowed assignment observation were not enough.
