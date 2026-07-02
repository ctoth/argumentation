# Coder report: Z3 per-check time budget + honest unknown (exp/af-z3-check-budget)

Branch: `exp/af-z3-check-budget` off main at `93d2897` (verified before
branching). Worktree:
`C:\Users\Q\code\argumentation\.claude\worktrees\agent-a01064970c3da35af`.
`ward set experiment-worker` succeeded ("ward: phase → experiment-worker").

## Commits

- `4d2278f` Add Z3 per-check budget and honest unknown to AF SAT layer
  (src/argumentation/solving/af_sat.py, src/argumentation/solving/solver.py,
  tests/solving/test_af_sat_check_budget.py)
- `105b518` Plumb AF worker SAT budget and map SolverTimeout to timeout rows
  (tools/iccma2025_run_native.py, tests/interop/test_iccma_af_sat_budget.py)
- `efe9e70` Record AF Z3 check-budget experiment result
  (experiments/2026-07-02-af-z3-check-budget.md,
  scripts/compare_af_z3budget_runs.py, coder state notes)

## What changed (file:line, post-change)

- `src/argumentation/solving/af_sat.py`
  - `AfSatCheckTimeout(TimeoutError)` (:23-45): structured budget-exhausted
    signal carrying `utility_name` and `check_budget_seconds`; mirrors the
    ABA `ClingoSolveTimeout` convention (`aba_incremental.py:91/419`).
  - `_apply_check_budget` (:48-52): sets z3 per-solver `timeout` in
    milliseconds (`max(1, int(seconds * 1000))`), no-op for `None`.
  - `AfSatKernel.__init__` (:138-145): new `check_budget_seconds` kwarg,
    stored and applied to the solver.
  - `AfSatKernel.check` (:383-387): a result that is neither `sat` nor
    `unsat` now raises `AfSatCheckTimeout` after emitting the trace event
    with `result="unknown"` — previously every caller collapsed it into the
    negative branch (old :443/:662/:989/:1050/:1072).
  - `_PreferredSkepticalAttackerSolver` (:1168-1193 ctor, :1234-1238 raise):
    unknown no longer means "no attacker" (which minted skeptical=True).
  - Budget threaded through every kernel construction:
    `find_stable_extension` (:465/:484), `explain_stable_unsat` standalone
    solver (:538, diagnostic `status="unknown"` behavior kept — it never
    minted an acceptance answer), `find_complete_extension` (:630/:649),
    `find_preferred_extension` (:661/:680), `is_preferred_skeptically_accepted`
    (:729/:757), `PreferredSkepticalTaskSolver` (super-core :798, extension
    kernel :807, attacker solver :823), `PreferredSuperCoreSolver` (:907),
    `find_semi_stable_extension` (:924/:943), `find_ideal_extension` incl.
    recursion (:959/:975/:982), `find_stage_extension` (:999/:1018).
  - `AfSatCheckTimeout` exported in `__all__`.
- `src/argumentation/solving/solver.py`
  - `SATConfig.check_budget_seconds: float | None = None` (:80-92), default
    `None` = unlimited = prior behavior.
  - `_sat_trace` → `_sat_options` (:533-538) returning
    (trace_sink, metadata, check_budget_seconds).
  - `_sat_check_timeout` (:541-551): `AfSatCheckTimeout` → `SolverTimeout`
    (`core/solver_results.py:58`, already a member of the result unions)
    with `backend="sat"`, `problem=f"AF-{semantics}"`, metadata
    `{utility_name, check_budget_seconds}`.
  - `solve_dung_single_extension` sat branch (:355-371): passes budget to the
    finder table, catches `AfSatCheckTimeout`.
  - `solve_dung_acceptance` sat branch (:407-427): refactored — the six
    duplicated per-semantics try/except blocks collapsed into
    `_dedicated_sat_acceptance_solver` (:961-970) + `_SAT_ACCEPTANCE_SOLVERS`
    table (:952-958); all acceptance helpers share the uniform
    `(framework, task, query, *, trace_sink, metadata, check_budget_seconds)`
    signature; the enumeration fallback stays outside the try (bit-identical
    error behavior).
- `tools/iccma2025_run_native.py`
  - `solve_af_job` builds `SATConfig(..., check_budget_seconds=max(0.1,
    float(job["solver_timeout_seconds"]) - 1.0))` (:805-819) — the same
    safety-margin convention as the ABA clingo solve budget (:969-973).
  - Both AF result ladders map `SolverBackendTimeout` →
    `solver_timeout_row` (:838, :861; helper :1110-1123); the ABA SE branch
    (:994) now uses the same helper (pure refactor, identical dict).

TDD order: both test files were written first and confirmed RED
(ImportError for `AfSatCheckTimeout`; harness `TypeError: unknown solver
result: SolverTimeout(...)` at old :833), then GREEN, then the dispatch-table
and shared-row-helper refactors.

## Test outcomes (quoted)

- New tests (15 + 3): `18 passed in 0.51s`.
- `uv run pytest tests/solving` → `219 passed, 3 skipped in 5.64s` (skips
  pre-existing env-conditional: `set ICCMA_AF_SOLVER...`,
  `set ASPFORABA_SOLVER or ICCMA_ABA_SOLVER...`, `ICCMA 2017 data not
  available`).
- `uv run pytest tests/interop` → `57 passed in 2.07s`.
- `uv run lint-imports` → `Contracts: 2 kept, 0 broken.`
- Full suite minus `tests/structured/aspic` →
  `2 failed, 2792 passed, 4 skipped, 1 xfailed in 249.18s (0:04:09)`.
  Both failures independent of this diff (`git diff main --stat` touches only
  the five files above):
  - `test_docs_surface.py::test_current_docs_do_not_cite_old_flat_source_paths`
    fails on main's own content: `git show
    main:docs/argumentation-package-boundary.md` contains
    `src/argumentation/af_revision.py` (offender count 1). Pre-existing on
    main.
  - `test_collapsed_profile_summary.py::test_serializable_top_reports_share_of_profile_samples`
    is order-flaky (equal samples/share tie): immediate rerun in the same
    tree → passes (`1 failed, 9 passed` with only the docs test failing).
- `tests/structured/aspic` did not complete in-session: two separate
  full-suite runs each spent 40-80+ minutes inside a single hypothesis
  example (first `test_defeat_is_directed`, then
  `test_target_sub_in_sub_of_target`; `@settings(deadline=None)`); py-spy
  dumps show active computation purely inside
  `argumentation\structured\aspic\aspic.py` `compute_attacks`/
  `compute_defeats`/`__hash__`. This diff does not touch aspic or anything it
  imports; 2851 tests had already passed under `-x` before the first stall.
  I killed my own stalled pytest processes (202920/208620) and composed the
  gate from the minus-aspic run; the aspic-inclusive run was still grinding
  when this report was written.
- Forced-unknown determinism probe (scripts/probe_z3_rlimit_unknown.py,
  uncommitted scratch): z3 4.16.0; `rlimit=10` on a 60-node cyclic AF →
  `unknown` 5/5 trials; the same instance solves in <1 ms unlimited, which is
  why the tests force unknown via `rlimit` rather than wall-clock.

## Metric gate 1 — DS-PR no-regression (t15, cap 320)

Command (from the worktree):
`uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025 --only-subtrack DS-PR --backend auto --max-af-arguments 320 --timeout-seconds 15 --label af-z3budget-dspr-t15 --no-progress`

vs baseline `iccma-2025-af-dspr-cdas-variantB.json`
(`scripts/compare_af_z3budget_runs.py` output):

| metric | baseline | candidate | gate |
| --- | --- | --- | --- |
| rows / common keys | 964 | 964 (964 common) | — |
| solved | 235 | 235 | no drop: PASS |
| timeout / skipped | 20 / 709 | 20 / 709 | — |
| solved lost / gained | — | 0 / 0 | PASS |
| answer mismatches (235 common solved) | — | 0 | PASS |
| commonly-solved elapsed | 605.23 s | 611.04 s | +0.96% (< +5%): PASS |

(The candidate run shared the box with one stuck single-threaded pytest —
1 of 32 cores; noted for honesty, margin unaffected.)

## Metric gate 2 — behavior demonstration

In the slice itself, 4/20 timeout rows now end by the in-process budget:

```json
"reason": "Z3 returned unknown on AF SAT check 'preferred_super_core_admissible_attacker' (check budget 14.0s)",
"solver_metadata": {"check_budget_seconds": 14.0, "utility_name": "preferred_super_core_admissible_attacker"},
"status": "timeout", "elapsed_seconds": "14.825150", "instance": "AFs/WS_300_32_30_70.af"
```

(the twin `WS_300_32_90_70.af` rows are identical in shape; matching
`sat_check` events show `"elapsed_ms": "14010.848000", "result": "unknown"`).
The same rows in the baseline were outer-kill rows
(`"reason": "timeout>15.0"`, 15.019 s / 15.013 s) — the row now ends by the
in-process signal ~1 s before the outer kill.

Hard rows from `iccma-2025-timeout-recal-60s-20260701-DS-PR.json` (label
`af-z3budget-hardrows-t15`; final artifact: crusti_g2io_125_0.5_31_17,
crusti_g2io_225_0.2_127_42, ER_300_20_2 at cap 30000; an earlier same-label
run with ER_300/ER_400/ER_500 at cap 600 behaved identically): all six rows
are clean `status="timeout"` rows but end by the outer kill
(`"reason": "timeout>15.0"`), because the ER instances split their 15 s
across many sub-14 s checks and the crusti instances spend the window in
Python-side parsing/encoding before any single long Z3 check. That is the
honest boundary of a per-check budget: it fires exactly where a single Z3
check dominates (demonstrated by the WS_300 rows), and the outer kill remains
the backstop elsewhere.

## Kill-criteria evaluation

- Solved count drop? No (235 = 235).
- Commonly-solved time > +5%? No (+0.96%).
- Any answer change? No (0 mismatches).
- Default (budget=None) behavior change? None observed anywhere
  (`TestDefaultBehaviorUnchanged` plus all existing suites green except the
  two exonerated non-aspic failures above).

## Promotion recommendation (recommend-only)

RECOMMEND PROMOTION. The change closes a real correctness hazard (Z3
`unknown` silently minted as credulous=False / skeptical=True), is
behavior-neutral by default, costs ~1% on the DS-PR slice (within noise/gate),
and produces structured, attributable in-process timeout rows where a single
check dominates. Known limitation for a follow-up experiment: rows dominated
by many short checks or Python-side encoding still rely on the outer kill; a
whole-row deadline (cumulative budget across checks) would be the next single
variable.

Caveat for the promoter: before merging, decide how to handle the two
pre-existing main failures surfaced here (docs-surface offenders in
`docs/argumentation-package-boundary.md`; flaky
`test_collapsed_profile_summary` ordering) and the pathologically slow aspic
hypothesis tests — none are caused by this branch.
