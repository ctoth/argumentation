# ABA Preferred Salvage With Performance Contracts Workstream

## Goal

Salvage useful assets from failed ABA preferred experiments without reviving
failed production solver paths.

The required learning is now explicit: semantic correctness is not enough for
preferred-row performance work. Before importing old research, this workstream
adds executable operational contracts for the preferred failure class, then
uses those contracts to decide what can be pulled forward.

## Failed Branches To Inspect

- `experiment/aba-greedy-preferred-growth`
- `experiment/aba-complete-labelling-prefsat-backend`
- `experiment/aba-native-rule-closure-prefsat`
- `experiment/aba-asp-saturation-preferred`
- `experiment/aba-preferred-maximality-backend`

## Salvage Policy

Allowed salvage:

- tests that enforce operational shape;
- telemetry contracts;
- route/shape predicates;
- benchmark runner fixes;
- page-image citations;
- explicit failure records and benchmark evidence;
- notes that prevent repeated failed hypotheses.

Forbidden salvage:

- failed production preferred solver paths;
- semantic-only tests that greenlight timeout-prone implementations unless
  paired with operational contracts;
- filename, path, generator, year, or manifest-id heuristics;
- generated diagnostics unless explicitly requested.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Clean Base and Experiment Branch.
3. Phase 2: Preferred Operational Contracts.
4. Phase 3: Failed Branch Inventory.
5. Phase 4: Salvage Only Contract-Enforcing Assets.
6. Phase 5: Verification and Promotion.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable.

- [x] Run the order check after every edit to this workstream.
- [x] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-preferred-salvage-with-perf-contracts.md
```

Expected result: every listed phase matches a phase heading in order.

## Phase 1: Clean Base and Experiment Branch

Goal: isolate the salvage slice.

- [x] Confirm tracked files are clean.
- [x] Run on `experiment/aba-preferred-salvage-perf-contracts`.
- [x] Do not create worktrees, temporary clones, or alternate checkouts.
- [x] Leave unrelated untracked diagnostics alone.

Execution status:

- Running on `experiment/aba-preferred-salvage-perf-contracts` from a clean
  tracked base.

Gate:

```powershell
git branch --show-current
git status --short --untracked-files=no
```

Expected result: clean tracked files on the experiment branch.

## Phase 2: Preferred Operational Contracts

Goal: encode the performance learning before reading old branch diffs.

- [ ] Add a preferred no-attack operational contract with bounded solver calls.
- [ ] Add a preferred dense-monolithic known-failure contract that marks the
  current large/dense preferred shape as lacking a production route.
- [ ] Add a contract proving failed preferred SAT/ASP route candidates are not
  marked production merely because they are semantically valid candidates.
- [ ] Keep timed wall-clock checks opt-in/calibrated only.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_aba_route_properties.py
```

Expected result: contracts pass before any old research is imported.

## Phase 3: Failed Branch Inventory

Goal: inventory failed experiments for reusable assets only.

- [ ] Inspect each failed branch's commits and touched paths.
- [ ] Record which tests, tools, citations, and failure records are useful.
- [ ] Record which production solver paths are rejected.
- [ ] Write the inventory in `reports\aba-preferred-salvage-inventory.md`.

Gate:

```powershell
git status --short -- reports\aba-preferred-salvage-inventory.md
```

Expected result: a tracked report exists with branch-by-branch salvage and
reject decisions.

## Phase 4: Salvage Only Contract-Enforcing Assets

Goal: import only assets that improve future guardrails.

- [ ] Import or recreate any missing failure record needed on `main`.
- [ ] Import or recreate any missing test/tooling asset that enforces the new
  contracts.
- [ ] Do not import failed preferred production solver code.
- [ ] Run the contract gate after each salvage edit.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_aba_route_properties.py tests\test_aba_shape_benchmark.py
```

Expected result: contract and route tests pass; no failed production preferred
path is introduced.

## Phase 5: Verification and Promotion

Goal: finish cleanly.

- [ ] Re-run all gates.
- [ ] Promote the minimal report/test/workstream diff to `main` if gates pass.
- [ ] Keep generated diagnostics uncommitted unless explicitly requested.

Gate:

```powershell
git status --short --untracked-files=no
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_aba_route_properties.py tests\test_aba_shape_benchmark.py
```

Expected result: clean tracked files and passing contract gates.

## Definition of Done

This workstream is complete only when preferred-row salvage is captured as
contract-enforcing tests/reports and promoted to `main`, or a blocker is
recorded with the exact unfinished phase.
