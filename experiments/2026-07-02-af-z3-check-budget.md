# AF Z3 Per-Check Time Budget + Honest Unknown Handling

Date: 2026-07-02

Status: measured on experiment branch; robustness experiment (not a speed
experiment). Correctness gates (`tests/solving`, `tests/interop`) and both
metric gates pass; two full-suite caveats (one pre-existing-on-main docs
failure, one flaky ordering test, plus pathologically slow pre-existing aspic
property tests) are documented under Fast Contracts. Promotion is a
recommendation only.

Experiment branch: `exp/af-z3-check-budget` (off main at `93d2897`)

Evidence commits:

- `4d2278f Add Z3 per-check budget and honest unknown to AF SAT layer`
- `105b518 Plumb AF worker SAT budget and map SolverTimeout to timeout rows`

Scout groundwork: `notes-af-z3-timeout-scout.md` (repo root of main checkout).

## Hypothesis

Before this change no Z3 `Solver` in the AF SAT path had a time budget, and
every acceptance caller collapsed Z3 `unknown` into the negative branch
(`af_sat.py` old lines 443/662/989/1050/1072; `find_attacker` old 1115-1141;
`solver.py` `_solve_sat_acceptance` minting `answer` from witness None-ness).
A Z3 timeout was therefore (a) impossible to trigger in-process (rows hung
until the harness's outer wall-clock kill) and (b) if it ever occurred, a
silent wrong answer (credulous→False, skeptical→True). Adding an optional
per-check budget plus structured unknown handling should produce clean
in-process `status="timeout"` rows where a single Z3 check dominates, with
zero change in solved count, answers, or (within noise) runtime.

## Single Variable

One behavior change: an optional per-check Z3 time budget with honest
`unknown` handling on the AF SAT path.

- `SATConfig.check_budget_seconds: float | None = None`
  (`src/argumentation/solving/solver.py:80-92`); `None` = unlimited =
  bit-identical default.
- `_apply_check_budget` sets the z3 per-solver `timeout` parameter in
  milliseconds (`src/argumentation/solving/af_sat.py:48-52`) on every Solver
  the AF SAT layer creates: `AfSatKernel.__init__`
  (`af_sat.py:145`), the `explain_stable_unsat` diagnostic solver
  (`af_sat.py:538`), and `_PreferredSkepticalAttackerSolver`
  (`af_sat.py:1184`). All finders and the CDAS solvers thread the budget
  (`find_stable/complete/preferred/semi_stable/stage/ideal_extension`,
  `is_preferred_skeptically_accepted`, `PreferredSkepticalTaskSolver`,
  `PreferredSuperCoreSolver`).
- Honest unknown: `AfSatKernel.check` raises `AfSatCheckTimeout(TimeoutError)`
  when the result is neither `sat` nor `unsat` (`af_sat.py:383-387`), after
  emitting the trace event with `result="unknown"`. Same in
  `_PreferredSkepticalAttackerSolver.find_attacker` (`af_sat.py:1234-1238`).
  `explain_stable_unsat` already reported `status="unknown"` honestly (it is
  a diagnostic API, never an acceptance answer) and keeps doing so.
- Mapping: `solve_dung_single_extension` / `solve_dung_acceptance` catch
  `AfSatCheckTimeout` and return `SolverTimeout` (`core/solver_results.py:58`)
  with `problem=f"AF-{semantics}"` and metadata
  `{utility_name, check_budget_seconds}` (`solver.py:541-551`, `:368-369`,
  `:418-419`). This mirrors the ABA `ClingoSolveTimeout` →
  `_failure_result(status="timeout")` convention
  (`aba_incremental.py:91/419`, `aba_asp.py:309/346`).
- Harness: `solve_af_job` derives
  `check_budget_seconds = max(0.1, solver_timeout_seconds - 1.0)`
  (`tools/iccma2025_run_native.py:813-818`), the same safety-margin
  convention as the ABA clingo solve budget
  (`iccma2025_run_native.py:969-973`:
  `max(0.1, float(job["solver_timeout_seconds"]) - 1.0)`), and both AF result
  ladders map `SolverBackendTimeout` to a clean `status="timeout"` row via the
  shared `solver_timeout_row` helper (`iccma2025_run_native.py:838`, `:861`,
  helper at `:1110-1123`; the ABA SE branch at `:994` now uses the same
  helper).

Out of scope (unchanged): ABA SAT (`aba_sat.py`), epistemic, dynamics
optimization, Python-side preprocessing/encoding time (the budget bounds Z3
check time only), clingo paths.

## Fast Contracts

All run on the experiment branch (worktree venv, z3-solver 4.16.0):

- New TDD tests: `tests/solving/test_af_sat_check_budget.py` (15) +
  `tests/interop/test_iccma_af_sat_budget.py` (3) — `18 passed in 0.51s`.
  Cover: budget seconds→ms reaches solver params; forced-`unknown` (via
  `rlimit`, deterministic: 5/5 probe trials) raises instead of returning a
  negative answer, for both the kernel and the CDAS attacker solver;
  SATConfig plumb to finders; `AfSatCheckTimeout` → `SolverTimeout` mapping
  (single-extension, credulous, skeptical); harness budget derivation (15s →
  14.0s) and `SolverTimeout` → timeout-row mapping for both AF branches.
- `uv run pytest tests/solving` → `219 passed, 3 skipped` (all 3 pre-existing
  environment-conditional skips: ICCMA_AF_SOLVER / ASPFORABA_SOLVER / ICCMA
  2017 data).
- `uv run pytest tests/interop` → `57 passed`.
- `uv run lint-imports` → `Contracts: 2 kept, 0 broken`.
- Full suite minus `tests/structured/aspic`:
  `2 failed, 2792 passed, 4 skipped, 1 xfailed in 249.18s`. Both failures are
  independent of this diff (which touches only `af_sat.py`, `solver.py`,
  `iccma2025_run_native.py`, and two new test files):
  - `tests/test_docs_surface.py::test_current_docs_do_not_cite_old_flat_source_paths`
    fails on main's own content —
    `git show main:docs/argumentation-package-boundary.md` already contains
    the offending `src/argumentation/af_revision.py` citation; no docs are
    touched here.
  - `tests/test_collapsed_profile_summary.py::test_serializable_top_reports_share_of_profile_samples`
    is flaky (equal-samples tie-break ordering): it passes on immediate rerun
    in the same tree (`9 passed` with the docs test the sole failure).
- `tests/structured/aspic` could not be brought to completion in this
  session: its hypothesis property tests (`deadline=None`) hit multi-hour
  example generation in two separate full-suite runs (two *different* tests,
  `test_defeat_is_directed` then `test_target_sub_in_sub_of_target`; py-spy
  stacks purely inside `aspic.py compute_attacks/compute_defeats`). This diff
  does not touch aspic or anything aspic imports; 2851 tests had already
  passed under `-x` before the first stall.

## Metric Gate

### 1. No-regression: DS-PR slice (t15, cap 320)

Command (from the experiment worktree):
`uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025 --only-subtrack DS-PR --backend auto --max-af-arguments 320 --timeout-seconds 15 --label af-z3budget-dspr-t15 --no-progress`

Baseline: `data/iccma/2025/runs/iccma-2025-af-dspr-cdas-variantB.json`.
Comparison: `scripts/compare_af_z3budget_runs.py`:

| metric | baseline (variantB) | candidate (af-z3budget) | gate |
| --- | --- | --- | --- |
| rows | 964 | 964 | — |
| solved | 235 | 235 | must not drop: PASS |
| timeout | 20 | 20 | — |
| skipped | 709 | 709 | — |
| solved lost / gained | — | 0 / 0 | PASS |
| answer mismatches (235 commonly solved) | — | 0 | PASS |
| commonly-solved elapsed | 605.23 s | 611.04 s (+0.96%) | within +5%: PASS |

Note: the candidate run shared the machine with one stuck single-threaded
pytest process (1 of 32 cores); +0.96% is comfortably inside the gate.

### 2. Behavior demonstration: in-process timeout rows

Within the same DS-PR slice, 4 of the 20 timeout rows now end by the
in-process budget instead of the outer kill (the other 16 are many-short-check
CDAS loops where no single check exceeds 14 s — a per-check budget cannot end
those; that is the outer kill's job). Emitted row
(`iccma-2025-af-z3budget-dspr-t15.json`, `AFs/WS_300_32_30_70.af`, track
main; the twin rows for track heuristics and `AFs/WS_300_32_90_70.af` are
identical in shape):

```json
{
  "answer": null,
  "arguments_or_atoms": 300,
  "attacks": 4800,
  "backend": "auto",
  "elapsed_seconds": "14.825150",
  "instance": "AFs/WS_300_32_30_70.af",
  "reason": "Z3 returned unknown on AF SAT check 'preferred_super_core_admissible_attacker' (check budget 14.0s)",
  "solver_metadata": {
    "check_budget_seconds": 14.0,
    "utility_name": "preferred_super_core_admissible_attacker"
  },
  "status": "timeout"
}
```

The same rows in the baseline were outer-kill rows
(`"reason": "timeout>15.0"`, elapsed 15.019 s / 15.013 s). The matching
`sat_check` trace event shows the budgeted check itself:
`"elapsed_ms": "14010.848000", "result": "unknown",
"utility_name": "preferred_super_core_admissible_attacker"`.

Hard rows from `iccma-2025-timeout-recal-60s-20260701-DS-PR.json`
(`AFs/crusti_g2io_125_0.5_31_17.af`, `AFs/crusti_g2io_225_0.2_127_42.af`,
`AFs/ER_300_20_2.af`; label `af-z3budget-hardrows-t15`, cap raised to 30000 so
the crusti instances are not cap-skipped; an earlier run of the same label
with ER_300/ER_400/ER_500 behaved identically): all six rows remain clean
`status="timeout"` rows but end by the outer kill (`timeout>15.0`), because
the ER rows split their 15 s across many sub-14 s checks and the crusti rows
spend the window in Python-side parsing/encoding before any long Z3 check.
This matches the design: the budget bounds Z3 check time, and the outer kill
remains the backstop where no single check dominates.

## Interpretation

- The correctness hazard is closed: Z3 `unknown` can no longer be minted into
  a credulous=False / skeptical=True answer anywhere on the AF SAT path; it
  becomes `SolverTimeout` → `status="timeout"`.
- With the default `budget=None` the change is behavior-neutral (identical
  statuses, answers, solved sets on the full DS-PR slice; +0.96% time noise).
- The budget demonstrably converts single-long-check hangs into clean
  in-process timeout rows ~1 s before the outer kill (WS_300 rows), with the
  responsible check named in `reason`/`solver_metadata`.
- Rows dominated by many short checks or by Python-side encoding still need
  the outer kill; a whole-row deadline (sum over checks) would be a separate
  experiment.

## Decision

Recommend promotion (recommend-only). Kill criteria evaluated: solved count
did not drop (235=235), commonly-solved time +0.96% (< +5%), no answer
changes, default path bit-identical on all exercised gates. No kill
condition triggered.
