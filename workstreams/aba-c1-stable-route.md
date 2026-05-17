# ABA C1 Stable Route Workstream

## Goal

Resolve the C1 stable-control issue with a structural route, not a filename or
ICCMA-specific heuristic.

The repeated hard-bucket gates showed a concrete class: large flat ABA
single-extension stable rows can be better served by the existing SAT stable
backend than by the default clingo multishot route. The target is narrow:
route only structurally large/dense stable single-extension ABA inputs to SAT,
preserve the existing small clingo route, and benchmark C1.

## Evidence

- `workstreams/aba-complete-labelling-prefsat-backend.md`: C1
  `ABAs/aba_2000_0.1_5_5_3.aba` / `SE-ST` solved on `sat` while preferred SAT
  experiments failed.
- `workstreams/aba-hard-bucket-backend-execution.md`: C1 is a named stable
  control that must be repaired, rerouted, or explicitly rebaselined.
- The route must use framework shape only: flatness, semantics, task,
  assumption count, and rule density. It must not inspect filenames, paths,
  generator names, years, or manifest ids.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Clean Base and Experiment Branch.
3. Phase 2: Hypothesis-First Route Tests.
4. Phase 3: Implement Structural Stable Route.
5. Phase 4: Targeted C1 Benchmark Gate.
6. Phase 5: Promote or Record Failure.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable.

- [x] Run the order check after every edit to this workstream.
- [x] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-c1-stable-route.md
```

Expected result: every listed phase matches a phase heading in the same order.

## Phase 1: Clean Base and Experiment Branch

Goal: isolate the route experiment.

- [x] Confirm tracked files are clean.
- [x] Run on `experiment/aba-c1-stable-route`.
- [x] Leave unrelated untracked files alone.

Execution status:

- Running on `experiment/aba-c1-stable-route` with clean tracked files.

Gate:

```powershell
git branch --show-current
git status --short --untracked-files=no
```

Expected result: clean tracked files on `experiment/aba-c1-stable-route`.

## Phase 2: Hypothesis-First Route Tests

Goal: prove the intended routing behavior before source changes.

- [ ] Add a test that small stable ABA auto routing still uses clingo when
  clingo is available.
- [ ] Add a test that large/dense flat ABA stable single-extension auto routing
  uses SAT and does not call clingo.
- [ ] Add a route-shape invariance test proving the predicate ignores path,
  filename, year, generator, and row order.
- [ ] Add C1-shaped benchmark-route metadata expectations if the benchmark
  route surface supports them.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba.py tests\test_solver_availability.py tests\test_aba_route_properties.py tests\test_aba_shape_benchmark.py
```

Expected result: new tests fail only because the large/dense stable route still
chooses clingo.

## Phase 3: Implement Structural Stable Route

Goal: route the proven class without broadening the solver contract.

- [ ] Change ABA auto backend selection so it can inspect flat ABA framework
  shape for stable single-extension tasks.
- [ ] Route large/dense stable single-extension ABA to SAT.
- [ ] Preserve preferred auto routing through ASP when clingo is available.
- [ ] Preserve small stable clingo routing.
- [ ] Do not inspect filenames, paths, years, generator names, or manifest ids.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba.py tests\test_solver_availability.py tests\test_aba_route_properties.py tests\test_aba_shape_benchmark.py
```

Expected result: route tests pass before benchmarking.

## Phase 4: Targeted C1 Benchmark Gate

Goal: prove the route fixes the named stable control.

- [ ] Run C1 under the 30-second budget.
- [ ] Keep generated diagnostics uncommitted unless explicitly requested.
- [ ] If C1 does not solve under auto, record the failed hypothesis; do not
  widen to preferred targets as a substitute.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id C1 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-c1-stable-route.json --output-csv data\iccma\2025\runs\aba-c1-stable-route.csv
```

Expected result: C1 `auto` solves under 30 seconds, with `sat` as the selected
structural route or best solved backend.

## Phase 5: Promote or Record Failure

If the gate passes:

- [ ] Re-run the route tests and C1 benchmark gate.
- [ ] Promote the minimal route/test/workstream diff to `main`.
- [ ] Leave diagnostic artifacts uncommitted unless explicitly requested.

If the gate fails:

- [ ] Do not promote the experiment branch.
- [ ] Record the failed route hypothesis and the next concrete backend
  hypothesis.

## Definition of Done

This workstream is complete only when C1 auto stable is structurally rerouted
and benchmarked successfully, or the route hypothesis is recorded as failed with
the next concrete backend hypothesis.
