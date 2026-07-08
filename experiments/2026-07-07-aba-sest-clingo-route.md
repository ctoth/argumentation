# 2026-07-07 — ABA SE-ST routing: gate the sat override on sparse-narrow shape

Branch: `exp/aba-sest-clingo-route-v2` (the planned `exp/aba-sest-clingo-route`
branch exists from a run that was terminated before doing any work; it has no
commits beyond main, so this experiment was executed on a fresh `-v2` branch
from main = 3ff70f3 and the dead branch was left untouched).

## Hypothesis

The stable single-extension (SE-ST) auto route sends every large dense flat
ABA framework to the `sat` backend. Non-sparse-narrow shapes (ICCMA 2025
`ABAs/aba_2000_0.1_5_5_1.aba` and `_6`) then land on the Z3-ranked LIA stable
path (`_sat_ranked_stable_extension`) and time out, while clingo
`find_stable_extension` solves the identical instances in ~0.25s
(`reports/aba-sepr-sest-scout.md`, executed probes). Restricting the sat
override to frameworks that also satisfy `sparse_narrow_native_sat_shape`
(the shape the native SAT stable path actually handles) flips those two rows
from timeout to solved without changing any other route.

## Single variable

The SE-ST stable single-extension auto-routing gate in
`src/argumentation/solving/solver.py` (`_auto_aba_backend_for_framework`):

- before: `large-dense-flat -> "sat"`
- after: `large-dense-flat AND sparse-narrow -> "sat"`; everything else falls
  through to `_auto_aba_backend`, which returns `"asp"` (clingo) for
  stable+single-extension when clingo is available.

Route consequences on the ICCMA shapes (from the scout's verified predicate
table): abcgen_c25 (sparse-narrow, NOT large-dense) stays `asp`;
abcgen_c35_asms30 (both true) stays `sat`/native-sparse-narrow; aba_2000
(large-dense, NOT sparse-narrow) moves `sat` -> `asp`. No other cell changes.

In-scope cleanup bundled in the same commit (behavior-neutral, tested): the
hand-duplicated `_is_large_dense_flat_aba` in solver.py was replaced by
`large_dense_flat_aba_shape` in `aba_route_policy.py`, delegating to the
existing `native_cnf_prefsat_dense_shape` constants (150 assumptions, 25.0
density) plus `_is_flat_aba`.

## Fast contracts

- RED->GREEN routing unit tests (tests/solving/test_solver_availability.py):
  auto backend decision is `asp` for a large-dense-flat non-sparse-narrow
  framework mirroring aba_2000 (200 assumptions, 5-atom bodies, contrary
  multiplicity 3, density 26) and stays `sat` for a sparse-narrow large-dense
  one (700 assumptions, unary bodies, injective contraries, density 26).
  Pre-fix run: `2 failed, 1 passed` (`AssertionError: assert 'sat' == 'asp'`);
  post-fix: all pass.
- The pre-existing end-to-end test asserting the OLD policy
  (`test_large_dense_aba_stable_single_extension_auto_uses_sat_not_clingo`,
  151-assumption non-sparse-narrow framework) encodes exactly the behavior this
  experiment removes; it was inverted to assert the clingo route.
- Policy unit tests for `large_dense_flat_aba_shape`
  (tests/structured/aba/test_aba_sparse_narrow_route_contract.py): density and
  assumption-count boundaries. (A non-flat case is unconstructible:
  `ABAFramework.__post_init__` raises `NotFlatABAError`.)
- Suites: `uv run pytest tests/solving tests/interop` -> 283 passed, 3 skipped
  (pre-existing environment skips: ICCMA_AF_SOLVER, ASPFORABA_SOLVER, ICCMA
  2017 data). `uv run pytest tests/structured` -> 1478 passed.

## Metric gate

`uv run tools/iccma2025_run_native.py --root ...\data\iccma\2025
--only-subtrack SE-ST --backend auto --max-af-arguments 1
--max-aba-assumptions 1000000 --timeout-seconds 15
--label aba-sest-route-<baseline|fixed>`

`--max-af-arguments 1` semantics verified in the runner source (run_or_skip):
AF instances above the cap are emitted as `status=skipped`, so the SE-ST slice
executes ABA rows only (SE-ST does include AF instances; the flag is needed).

Procedural note: the first baseline attempt was invalidated mid-run — the
worktree venv installs the package editable and the runner spawns a fresh
worker process per job, so workers picked up the fix the moment it landed in
src/. That run was killed and discarded. The clean baseline was rerun with the
worktree detached at main (3ff70f3); the fixed run used the committed fix.
Same machine, no concurrent heavy processes during either run.

Results (SE-ST slice, 642 rows = 322 AF skipped + 320 ABA executed, 15s cap):

| run | solved | timeout | AF skipped |
|---|---|---|---|
| baseline (main 3ff70f3) | 217 | 103 | 322 |
| fixed (7428faf) | **227** | **93** | 322 |

- Lost rows: **0**. Answer mismatches on 217 commonly-solved rows: **0**.
- Gained 10 rows (all previously 15s timeouts):
  aba_2000_0.1_10_10_0 (2.78s), aba_2000_0.1_10_10_7 (2.90s),
  aba_2000_0.1_10_5_0 (1.23s), aba_2000_0.1_10_5_1 (1.31s, no-stable-extension
  answer), aba_2000_0.1_10_5_2 (1.31s), aba_2000_0.1_10_5_4 (1.23s),
  aba_2000_0.1_10_5_8 (1.40s), aba_2000_0.1_5_5_7 (0.64s),
  aba_5000_0.1_10_5_7 (3.48s), aba_5000_0.1_5_5_6 (8.09s, no-stable-extension
  answer). All 8 gained positive witnesses were natively verified stable via
  an independent closure check (scripts/compare_aba_sest_routes.py); the two
  negative answers are clingo UNSAT results and are not cheaply verifiable
  natively (flagged, not verified).
- Route flips among commonly-solved rows (from solver_metadata): 6 rows moved
  Z3-ranked sat -> clingo_multishot, **all 6 faster** (largest:
  aba_5000_0.1_5_10_9 12.77s -> 2.16s; aba_5000_0.1_5_10_5 12.73s -> 2.34s).
  The other 211 rows kept identical routes (mostly already clingo).
- Commonly-solved aggregate elapsed: 362.86s -> 355.25s (**-2.10%**).
- Per-row >10% slowdowns: 82 rows — but every one is on an UNCHANGED code
  path (same clingo_multishot route in both runs), and same-route rows show a
  systematic +8.11% aggregate skew (82 slower / 7 faster / 122 within ±10%),
  i.e., the fixed run ran under more CPU contention (the operator ran pyright
  during it). Solo re-runs of the three worst "regressions" on fixed code:
  aba_5_3750literals 1.27s (baseline 1.19s, in-run reading 2.18s),
  aba_5_5000literals 1.71s (baseline 1.63s, was 3.12s), aba_6_5000literals
  1.78s (baseline 1.58s, was 2.40s) — baseline-level, confirming environment
  noise, not a change-caused regression.
- abcgen SE-ST rows: statuses unchanged row-for-row (solved rows stay solved
  at comparable times; timeout rows stay timeouts), as required.
- **Named rows aba_2000_0.1_5_5_1 / _6: STILL TIMEOUT at 15s** — the metric
  gate's headline requirement is NOT met. Diagnosis (probe on fixed code):
  the auto decision IS `asp` (0.003s), and a direct
  `AbaIncrementalSolver.find_stable_extension` solves in **0.378s with a
  152-assumption witness** (replicating the scout's 0.25s), but the
  production asp path (`solve_aba_with_backend`, aba_asp.py, default
  `simplify=True`) first runs `simplify_aba(framework, semantics="stable")`,
  which did not finish within 240s on this instance. The scout's probe called
  clingo directly and bypassed that preprocessing; the ten gained siblings
  evidently pass through it quickly. The named rows' residual blocker is the
  simplifier, not routing.

## Interpretation

The routing hypothesis is confirmed in mechanism and mostly in effect: taking
the aba_2000-family shapes off the Z3-ranked LIA stable path and onto clingo
converts 10 SE-ST timeouts into sub-9s solves and speeds up all 6
route-flipped already-solved rows, with zero lost rows, zero answer changes,
and no regression attributable to the change. The specific two instances the
scout benchmarked, however, expose a second, previously-masked bottleneck:
`simplify_aba` stable-semantics preprocessing inside the asp backend runs for
minutes on exactly those instances, so they time out before clingo is ever
reached — the scout's 0.25s measurement was of the clingo solve alone. Fixing
that is a preprocessing-budget/skip question (out of scope for this
routing-only change; candidate follow-up: budget or bypass `simplify_aba` for
stable single-extension when the incremental clingo path is available, or
profile `simplify_aba` on aba_2000_0.1_5_5_1).

## Decision

Metric gate as written: PARTIAL — "no lost/changed rows" and "no >10%
change-attributable regression" both hold (aggregate -2.10%; all per-row
slowdowns are same-route environment noise, spot-rerun-verified), but the
named rows did not flip. Net effect on the SE-ST slice is strongly positive
(+10 solved, -10 timeouts, 227/320 ABA rows solved).

Recommendation: PROMOTE the routing gate change (it is correct, tested,
behavior-narrow, and strictly improves the slice), and file the simplify_aba
stable-preprocessing bottleneck as an immediate follow-up experiment to
finish the named rows. Not promoting would forfeit 10 solved rows to keep 2
rows timing out either way.
