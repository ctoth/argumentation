# Workstream: ABA SE-PR ASP Auto Routing

Date: 2026-05-20

## Requested Outcome

Route large flat sparse/narrow ABA `SE-PR` single-extension auto requests
through the existing ASP/clingo backend when clingo is available, while keeping
explicit `backend="sat"` on the native sparse/narrow SAT path.

## Current Evidence

- `experiments/2026-05-20-aba-timeout-pyspy-triage.md`: representative
  preferred timeout is PySAT solve dominated.
- `experiments/2026-05-20-aba-se-pr-asp-vs-sat.md`: on the six preferred
  timeout rows:
  - `auto`: `0` solved, `6` timeout;
  - `sat`: `0` solved, `6` timeout;
  - `asp`: `1` solved, `5` timeout;
  - invalid solved witnesses: `0`.
- The ASP-only preferred win is
  `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba`.

## Scope

Owned production path:

- `src/argumentation/solver.py`

Owned tests:

- `tests/test_aba_sparse_narrow_route_contract.py`
- `tests/test_aba_sparse_narrow_native_sat.py` only as verification

Owned documentation:

- this workstream file
- `experiments/YYYY-MM-DD-aba-se-pr-asp-routing.md`

Generated diagnostics are not committed.

## Final State

- `backend="auto"` plus sparse/narrow flat ABA plus `semantics="preferred"`
  plus `task="single-extension"` plus clingo available routes to ASP.
- The result metadata for the route contract includes:
  - `backend == "asp"`;
  - `semantics == "preferred"`;
  - `solver == "clingo_multishot"`;
  - `algorithm == "first-model-witness"`.
- Explicit `backend="sat"` plus `semantics="preferred"` still calls
  `native_sparse_narrow_aba_extension`.
- No production test says preferred sparse/narrow auto is native-SAT-only.

## Deletion Target

Delete the early auto-route override in `_auto_aba_backend_for_framework` that
returns `"sat"` for sparse/narrow `preferred` single-extension frameworks before
`_auto_aba_backend` can select ASP.

Do not delete:

- `sparse_narrow_native_sat_shape`;
- `_NativeSparseNarrowStableSolver`;
- explicit native sparse/narrow SAT tests.

## Ordered Phases

### Phase 0: Branch

1. Verify current branch and tracked-file cleanliness.
2. Create experiment branch:
   `exp/aba-se-pr-asp-routing`

### Phase 1: Route Contract Red Tests

Replace the preferred auto native-SAT test with:

- preferred sparse/narrow auto with clingo calls `_solve_asp_aba_single_extension`;
- preferred sparse/narrow explicit `backend="sat"` calls
  `native_sparse_narrow_aba_extension`.

Gate:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Expected before production edit: preferred auto ASP route test fails.

### Phase 2: Delete Wrong Preferred Auto Route

Edit `_auto_aba_backend_for_framework` in `src/argumentation/solver.py` and
remove the sparse/narrow preferred auto `"sat"` override.

Gate:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Expected after production edit: route contract passes.

### Phase 3: Focused Regression Gate

Run:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py tests\test_solver_availability.py
```

### Phase 4: Full 10x10 Gate

Run:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-10x10.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\aba-se-pr-asp-routing-10x10.json --event-log-path data\iccma\2025\runs\aba-se-pr-asp-routing-10x10.events.jsonl
```

Pass requires:

- solved count is at least `10`;
- timeout count is at most `10`;
- no runner errors;
- preferred rows that solve through ASP report `solver == "clingo_multishot"`.

### Phase 5: Validation-Backed Gate

Run the shape benchmark over the 10x10 manifest with `backend=auto` and
`timeout-seconds=30`, using generated manifest conversion if needed.

Pass requires:

- no invalid solved witnesses;
- solved count is at least `10`;
- preferred solved rows through ASP are valid.

### Phase 6: Experiment Record and Promotion

Write:

`experiments/YYYY-MM-DD-aba-se-pr-asp-routing.md`

Promote production changes only if Phases 3, 4, and 5 pass.

## Stop Conditions

- Stop if branch creation is blocked by tracked dirty files.
- Stop after Phase 4 if solved count remains below `10`.
- Stop after Phase 5 if any solved witness is invalid.

