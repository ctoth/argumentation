# Direct ASP sparse/narrow stable routing

## Hypothesis

Large flat sparse/narrow ABA `SE-ST` single-extension rows should not use the
native sparse/narrow SAT route by default. For `backend="auto"`, routing stable
single-extension ABA instances through the existing clingo multishot ASP path
should solve the known hard row and improve the 10x10 fixture without regressing
the preferred native SAT route.

## Branch

- `exp/direct-asp-sparse-narrow-routing`

## Commits and changed paths

- `df4b2bc` `tests/test_aba_sparse_narrow_route_contract.py`
  - Added route contracts requiring sparse/narrow stable auto to call ASP when
    clingo is available.
  - Preserved explicit `backend="sat"` stable native SAT behavior.
  - Preserved preferred sparse/narrow auto native SAT behavior.
- `ea5ac7e` `src/argumentation/solver.py`
  - Removed stable from the sparse/narrow auto-to-SAT override.
- `84a1db8` `tools/run_aba_10x10_fixture.py`
  - Counted clingo multishot calls from current `solver_calls` metadata in the
    fixture summary.

Generated diagnostic outputs:

- `data/iccma/2025/runs/direct-asp-auto-hard-row.json`
- `data/iccma/2025/runs/direct-asp-auto-hard-row.csv`
- `data/iccma/2025/runs/direct-asp-auto-10x10.json`
- `data/iccma/2025/runs/direct-asp-auto-10x10.events.jsonl`
- `data/iccma/2025/runs/direct-asp-auto-10x10-shape-manifest.json`
- `data/iccma/2025/runs/direct-asp-auto-10x10-validated.json`
- `data/iccma/2025/runs/direct-asp-auto-10x10-validated.csv`

These diagnostics were not promoted as source artifacts.

## Evidence

Route contract red check before the production change:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Outcome before `ea5ac7e`: `1 failed, 5 passed`. Stable auto still reached the
native sparse/narrow SAT route.

Route contract after the production change:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Outcome: `6 passed in 0.78s`.

Regression gate:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py tests\test_solver_availability.py
```

Outcome: `48 passed in 1.52s`.

Hard row metric:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --output-json data\iccma\2025\runs\direct-asp-auto-hard-row.json --output-csv data\iccma\2025\runs\direct-asp-auto-hard-row.csv
```

Outcome: solved and valid in `22.487078599981032` seconds. Metadata reported
`solver="clingo_multishot"`, `solver_calls=1`, and `algorithm="first-model-witness"`.

10x10 fixture gate after the fixture summary fix:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-10x10.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\direct-asp-auto-10x10.json --event-log-path data\iccma\2025\runs\direct-asp-auto-10x10.events.jsonl
```

Outcome: `9` solved, `11` timed out, `3` native sparse/narrow SAT routes, and
`6` clingo solver calls. The known previous fixture baseline was `5` solved and
`15` timed out.

Validation-backed 10x10 shape gate:

```powershell
jq '[.rows[] | {year: 2025, track, subtrack, instance_kind, instance: .relative_path, arguments_or_atoms: .manifest.arguments_or_atoms}]' tests\manifests\iccma2025-abcgen-10x10.json > data\iccma\2025\runs\direct-asp-auto-10x10-shape-manifest.json
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\direct-asp-auto-10x10-shape-manifest.json --backend auto --timeout-seconds 30 --output-json data\iccma\2025\runs\direct-asp-auto-10x10-validated.json --output-csv data\iccma\2025\runs\direct-asp-auto-10x10-validated.csv
```

Outcome: `9` solved and `11` timed out. Witness validation statuses were `9`
valid and `11` not checked for timed-out rows; no invalid witnesses were
reported. Every solved `SE-ST` row used `solver="clingo_multishot"` with
`solver_calls=1`.

## Decision

Keep and promote.

Why:

- The route contract now fails before benchmark time if stable auto drifts back
  onto native sparse/narrow SAT.
- The known hard stable row solved through clingo multishot under the metric
  gate.
- The 10x10 fixture improved from `5/20` solved to `9/20` solved without
  increasing timeouts.
- Explicit SAT stable behavior and preferred auto behavior remain covered by
  tests.

## Retroactive protocol audit

Protocol status: true promotion experiment.

This record remains a completed successful experiment. It had a route contract,
a hard-row metric, a validation-backed 10x10 gate, no invalid solved witnesses,
and a concrete improvement from `5/20` solved to `9/20` solved.

Required follow-up: the remaining `SE-ST` timeout cohort still needs separate
profile-backed diagnosis, which is covered by the later clingo solver-shape
records.
