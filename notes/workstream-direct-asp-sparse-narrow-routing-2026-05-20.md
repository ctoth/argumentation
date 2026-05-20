# Workstream: Direct ASP Routing for Sparse/Narrow ABA SE-ST

Date: 2026-05-20

## Requested Outcome

Make the paper-backed direct ASP ABA solver the production route for large
flat sparse/narrow `SE-ST` single-extension instances when clingo is available.
The final state is that the measured hard row routes to
`AbaIncrementalSolver.find_stable_extension`, returns a valid stable witness,
and no longer enters `_NativeSparseNarrowStableSolver` through `backend="auto"`.

## Current Evidence

- `experiments/2026-05-20-glucose4-hard-row-full-profile.md`: native
  sparse/narrow SAT solved
  `ABAs/abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba` in
  `151.83979749993887s`; `150.96s` exclusive was inside PySAT `solve`.
- `experiments/2026-05-20-sparse-narrow-solve-timing.md`: the native SAT
  route used five solve calls with timings
  `[3298, 4056, 5318, 53180, 102730]` ms.
- `experiments/2026-05-20-sparse-narrow-ipasir-check-model.md`: moving loop
  rejection into IPASIR check-model callbacks timed out with `timeout>245.0`.
- `data/iccma/2025/runs/asp-hard-row-architecture-probe.json`: direct ASP
  solved the same hard row in `18.74283690005541s`, one solver call,
  `solver="clingo_multishot"`, `algorithm="first-model-witness"`,
  validation `stable_large_closure=valid`.
- Page images inspected directly for this decision:
  - `papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-013.png`
  - `papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-014.png`
  - `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png`
  - `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png`

## Architecture Decision

For flat ABA stable single-extension, stable semantics is an assumption-level
coverage problem:

- choose `in/out` assumptions;
- derive `supported` literals from chosen assumptions and rules;
- reject selected assumptions whose contraries are supported;
- require every `out` assumption to be `defeated`.

The production architecture is therefore:

- facts from `argumentation.aba_asp.encode_aba_theory(..., include_supports=False)`;
- `argumentation.encodings.aba_com_incremental.lp` for `supported`,
  `defeated`, admissibility/complete machinery, and stable coverage;
- `argumentation.aba_incremental.AbaIncrementalSolver.find_stable_extension`
  for `SE-ST`;
- `argumentation.solver.solve_aba_single_extension(..., backend="auto")`
  routing large sparse/narrow `stable` single-extension to the ASP backend when
  `_has_clingo()` is true.

The native sparse/narrow SAT route remains available for explicit
`backend="sat"` and as an auto fallback when clingo is unavailable. It is not
the auto route for `stable` sparse/narrow frameworks when clingo is available.

## Scope

Owned production paths:

- `src/argumentation/solver.py`

Owned tests:

- `tests/test_aba_sparse_narrow_route_contract.py`
- `tests/test_aba_sparse_narrow_native_sat.py` only for assertions that must
  remain true for explicit `backend="sat"`
- `tests/test_solver_availability.py` is verification-only in this workstream;
  do not edit it unless its current assertions fail after the route change.

Owned documentation/records:

- this workstream file
- `experiments/YYYY-MM-DD-direct-asp-sparse-narrow-routing.md`

Not owned:

- `src/argumentation/aba_incremental.py`
- `src/argumentation/aba_asp.py`
- `src/argumentation/aba_sat.py`
- `src/argumentation/aba_route_policy.py`
- generated benchmark JSON/CSV/profile outputs
- unrelated untracked notes, logs, prompts, and reports

## Final State

- `backend="auto"` plus `semantics="stable"` plus sparse/narrow flat ABA plus
  clingo available returns metadata with:
  - `solver == "clingo_multishot"`;
  - `algorithm == "first-model-witness"`;
  - `solver_calls == 1` on the hard row;
  - paper metadata from `Lehtonen_2021_IncrementalASP_ABA`.
- The same framework with explicit `backend="sat"` still calls
  `native_sparse_narrow_aba_extension` and returns metadata with
  `algorithm == "native_sparse_narrow_sat"`.
- `test_auto_single_extension_sparse_narrow_never_calls_clingo` is deleted or
  replaced. No production test asserts that sparse/narrow `SE-ST` auto must
  avoid clingo.
- The hard row
  `ABAs/abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba` solves with
  `backend=auto` through ASP in under `30s` on the local machine.
- The focused 10x10 ABA fixture gate does not regress solved row count.
  Baseline file: `data/iccma/2025/runs/sparse-narrow-fix-10x10.json`;
  baseline at `30s`: `5` solved, `15` timeout, `5` routed native SAT.

## Deletion Targets

- Delete the production auto-routing branch in
  `_auto_aba_backend_for_framework` that sends sparse/narrow `stable`
  single-extension to `"sat"` before `_auto_aba_backend` can select `"asp"`.
- Delete or replace the test assertion that sparse/narrow auto routing must not
  call clingo.
- Delete stale route wording in tests that names sparse/narrow `stable` auto as
  native-SAT-only.

Do not delete:

- `sparse_narrow_native_sat_shape`; explicit SAT and route diagnostics still use
  it.
- `_NativeSparseNarrowStableSolver`; explicit `backend="sat"` remains a real
  solver path.
- `SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES`; it remains provenance for the explicit
  native SAT route until a later documentation cleanup owns that rename.

## Ordered Phases

### Phase 0: Baseline and Branch

1. Verify branch and tracked-file cleanliness:
   `git branch --show-current`
   `git status --short`
2. Create experiment branch:
   `git switch -c exp/direct-asp-sparse-narrow-routing`
3. Record current explicit baselines:
   - `backend=auto` hard row currently routes to SAT and is slow;
   - `backend=asp` hard row solves in `18.74283690005541s`;
   - explicit `backend=sat` remains valid.

Phase 0 gate: no tracked dirty files before branch creation.

### Phase 1: Route Contract Red Tests

1. Replace `test_auto_single_extension_sparse_narrow_never_calls_clingo` with
   stable/preferred split tests:
   - stable sparse/narrow auto with `_has_clingo() == True` calls
     `_solve_asp_aba_single_extension` and does not call
     `native_sparse_narrow_aba_extension`;
   - stable sparse/narrow explicit `backend="sat"` calls
     `native_sparse_narrow_aba_extension`;
   - preferred sparse/narrow auto with `_has_clingo() == True` still calls
     `native_sparse_narrow_aba_extension` in this workstream.
2. Add a metadata assertion for stable auto:
   `backend == "asp"` is not enough; the result metadata must include
   `solver == "clingo_multishot"` and `algorithm == "first-model-witness"`.

Phase 1 gate:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Expected before implementation: the new stable auto route test fails.

### Phase 2: Delete the Wrong Auto Route

1. Edit `_auto_aba_backend_for_framework` in `src/argumentation/solver.py`.
2. Remove sparse/narrow `stable` single-extension from the early `"sat"`
   override when `_has_clingo()` is true.
3. Keep explicit `backend="sat"` unchanged.
4. Keep auto sparse/narrow preferred unchanged until a separate preferred-row
   measurement proves ASP is better for `SE-PR`.

Phase 2 gate:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Expected after implementation: route contract passes.

### Phase 3: Focused Semantic and Routing Verification

Run:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py tests\test_solver_availability.py
```

Passing this gate proves:

- auto stable sparse/narrow chooses ASP when clingo is available;
- explicit native sparse/narrow SAT still satisfies its semantic oracle tests;
- public solver availability behavior did not regress.

### Phase 4: Hard-Row Metric Gate

Run the hard row through auto routing:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --output-json data\iccma\2025\runs\direct-asp-auto-hard-row.json --output-csv data\iccma\2025\runs\direct-asp-auto-hard-row.csv
```

Metric pass requires all of:

- status `solved`;
- validation `valid`;
- `elapsed_seconds < 30`;
- metadata `solver == "clingo_multishot"`;
- metadata `solver_calls == 1`.

Metric fail requires abandoning the source delta and recording the failed
experiment.

### Phase 5: 10x10 Fixture Gate

Run the focused ICCMA fixture used for sparse/narrow ABA work:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-10x10.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\direct-asp-auto-10x10.json --event-log-path data\iccma\2025\runs\direct-asp-auto-10x10.events.jsonl
```

Metric pass requires:

- `summary.status_counts.solved >= 5`;
- `summary.status_counts.timeout <= 15`;
- no invalid witnesses;
- every `SE-ST` sparse/narrow row that routes through ASP has metadata
  `solver == "clingo_multishot"`.

Metric fail requires abandoning the source delta and recording the failed
experiment.

### Phase 6: Experiment Record and Promotion

Write:

`experiments/YYYY-MM-DD-direct-asp-sparse-narrow-routing.md`

The record must include:

- hypothesis;
- single variable;
- branch;
- commits;
- exact test commands;
- hard-row result;
- 10x10 result;
- generated diagnostics not committed;
- promote/abandon decision.

Promotion rule:

- Promote the route change only if Phases 3, 4, and 5 pass.
- Promote with clean commits on `main`.
- Do not commit generated JSON/CSV diagnostics.

## Old-Path Search Gates

After implementation, run:

```powershell
rg -n -F "sparse/narrow auto route must not call clingo" tests src notes experiments
rg -n -F "sparse/narrow auto route" tests src notes experiments
rg -n -F "native_sparse_narrow_sat" tests src
```

Required result:

- no test text says sparse/narrow stable auto must avoid clingo;
- explicit native SAT tests remain;
- `native_sparse_narrow_sat` remains reachable only through explicit SAT routing
  or preferred behavior pinned by Phase 1.

## Commit Plan

Each slice is committed before moving on:

1. Workstream artifact:
   `notes/workstream-direct-asp-sparse-narrow-routing-2026-05-20.md`
2. Route contract test changes.
3. Production routing change.
4. Experiment record.
5. Promotion commit on `main` if gates pass.

## Stop Conditions

- Stop before implementation if branch creation is blocked by tracked dirty
  files.
- Stop after Phase 1 if preferred sparse/narrow auto no longer routes through
  native sparse/narrow SAT before the production route edit.
- Stop after Phase 4 if the hard row does not route through ASP or does not
  solve under `30s`.
- Stop after Phase 5 if the 10x10 fixture regresses solved row count or
  produces an invalid witness.

## Non-Goals

- No bounded Horn/level encoding.
- No IPASIR work.
- No clingo encoding rewrite.
- No preferred-route promotion without separate `SE-PR` measurements.
- No changes to paper page-image artifacts.
