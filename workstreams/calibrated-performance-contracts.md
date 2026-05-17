# Calibrated Performance Contracts Workstream

## Goal

Build reusable local performance-contract infrastructure so solver experiments
can fail early on operational shape before reaching ICCMA benchmark gates.

This workstream does not optimize any solver. It adds calibration and budget
helpers that future solver work can use to express timed and telemetry-backed
contracts without hardcoding one developer machine's wall-clock numbers.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Clean Base and Experiment Branch.
3. Phase 2: Calibration CLI.
4. Phase 3: Test Budget Helper.
5. Phase 4: Performance Contract Tests.
6. Phase 5: Verification and Promotion.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable.

- [x] Run the order check after every edit to this workstream.
- [x] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\calibrated-performance-contracts.md
```

Expected result: every listed phase matches a phase heading in order.

## Phase 1: Clean Base and Experiment Branch

Goal: isolate the benchmark/performance infrastructure slice.

- [x] Confirm tracked files are clean.
- [x] Run on `experiment/calibrated-performance-contracts`.
- [x] Leave generated calibration output uncommitted unless explicitly
  requested.

Execution status:

- Running on `experiment/calibrated-performance-contracts` from a clean tracked
  base.

Gate:

```powershell
git branch --show-current
git status --short --untracked-files=no
```

Expected result: clean tracked files on the experiment branch.

## Phase 2: Calibration CLI

Goal: add a reusable local calibration command.

- [x] Add `tools\perf_calibrate.py`.
- [x] Report machine metadata: platform, processor string, Python version,
  CPU count, and timestamp.
- [x] Measure repeatable small tasks: Python integer loop, ABA parse,
  ABA closure, optional clingo solve, and optional Z3 check.
- [x] Emit JSON with schema version, benchmark records, elapsed seconds, and
  operations per second where meaningful.
- [x] Support `--output`, `--repeat`, and `--quiet`.
- [x] Do not commit generated calibration JSON.

Execution status:

- Added `tools\perf_calibrate.py`.
- Phase 2 gate passed with all local probes reporting `ok` on this machine.

Gate:

```powershell
uv run tools\perf_calibrate.py --repeat 1 --quiet
```

Expected result: valid JSON is printed or written; missing optional solvers are
reported as skipped, not as command failure.

## Phase 3: Test Budget Helper

Goal: expose conservative calibrated budgets to tests without requiring a
machine-local file.

- [x] Add a test helper module for performance contracts.
- [x] Load optional calibration JSON from `ARGUMENTATION_PERF_CALIBRATION`.
- [x] Provide deterministic fallback budgets when no calibration file exists.
- [x] Provide `require_perf_contracts_enabled()` controlled by
  `ARGUMENTATION_PERF_CONTRACTS`.
- [x] Make wall-clock contracts opt-in, while non-timed operational contracts
  remain normal tests.

Execution status:

- Added `tests\performance_contracts.py`.
- Phase 3 gate passed via `tests\test_performance_contracts.py`:
  `6 passed, 1 skipped in 0.62s`.

Gate:

```powershell
uv run pytest -q tests\test_performance_contracts.py
```

Expected result: helper tests pass without a calibration file.

## Phase 4: Performance Contract Tests

Goal: add first contracts for known solver classes.

- [x] Test calibration JSON shape.
- [x] Test fallback calibrated budgets.
- [x] Test no-attack preferred ABA has a bounded operational shape.
- [x] Test the large/dense stable route chooses SAT without invoking ASP.
- [x] Add an opt-in wall-clock smoke test that uses calibrated budget helpers
  only when performance contracts are enabled.

Execution status:

- Added `tests\test_performance_contracts.py`.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_solver_availability.py tests\test_aba_route_properties.py
```

Expected result: tests pass by default; opt-in timed tests are skipped unless
enabled.

## Phase 5: Verification and Promotion

Goal: complete the infrastructure slice cleanly.

- [ ] Re-run the calibration CLI.
- [ ] Re-run the performance contract tests.
- [ ] Promote the minimal source/test/workstream diff to `main` if gates pass.
- [ ] Keep generated calibration artifacts uncommitted unless explicitly
  requested.

Gate:

```powershell
git status --short --untracked-files=no
uv run tools\perf_calibrate.py --repeat 1 --quiet
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_solver_availability.py tests\test_aba_route_properties.py
```

Expected result: clean tracked files, valid calibration output, passing tests.

## Definition of Done

This workstream is complete only when the calibration CLI and performance
contract test helper are committed, verified, and promoted to `main`, or a
blocker is recorded with the exact unfinished phase.
