# Coder report: ABA SE-ST routing gate fix

Branch: `exp/aba-sest-clingo-route-v2` (see "Branch deviation" below).
Status: COMPLETE. Recommendation: promote, with one honest caveat — the two
named target rows did not flip (root cause isolated to `simplify_aba`
preprocessing, outside the routed code; ten sibling rows DID flip).

## Branch deviation (instructed)

The planned branch `exp/aba-sest-clingo-route` already existed from a prior
run that was terminated by an API limit before doing any work:
`git log main..exp/aba-sest-clingo-route` is empty. Per launcher instructions
it was left untouched and all work happened on `exp/aba-sest-clingo-route-v2`,
created from main = 3ff70f3 (satisfies the >= 3ff70f3 requirement). The
experiment record notes this.

## Diff summary

Commit `7428faf` "Gate ABA SE-ST sat override on sparse-narrow shape"
(4 files, +143/-15):

- `src/argumentation/solving/solver.py:504-511` — in
  `_auto_aba_backend_for_framework`, the stable + single-extension auto
  override now requires `large_dense_flat_aba_shape(framework) and
  sparse_narrow_native_sat_shape(framework)` (was: `_is_large_dense_flat_aba`
  alone) before returning `"sat"`. Non-matching shapes fall through to
  `_auto_aba_backend`, which returns `"asp"` for stable+single-extension when
  clingo is available. The conjunction (rather than replacing the dense gate
  with the sparse-narrow test) is what keeps this a no-other-routing-change
  fix: abcgen_c25-shaped frameworks (sparse-narrow but density < 25) never
  matched the override and still do not, so they keep their current clingo
  route.
- `src/argumentation/solving/solver.py:512-518` (old) — hand-duplicated
  `_is_large_dense_flat_aba` DELETED.
- `src/argumentation/structured/aba/aba_route_policy.py:42-49` — new
  `large_dense_flat_aba_shape(framework)`, delegating to the pre-existing
  `native_cnf_prefsat_dense_shape` constants (>150 assumptions, >25.0
  rules/assumption, flat) via `_is_flat_aba`; behavior-neutral consolidation
  of the drift hazard named in the task.
- `tests/solving/test_solver_availability.py` — two shape builders
  (`_large_dense_non_sparse_narrow_aba_framework`: 200 assumptions, 5-atom
  bodies, contrary multiplicity 3, density 26, mirroring aba_2000's three
  sparse-narrow failures; `_sparse_narrow_large_dense_aba_framework`: 700
  assumptions, unary bodies, injective contraries, density 26), two new
  decision tests, and the pre-existing old-policy test
  `test_large_dense_aba_stable_single_extension_auto_uses_sat_not_clingo`
  inverted to `..._auto_uses_asp_when_not_sparse_narrow` (its 151-assumption
  framework is not sparse-narrow, so the new policy routes it to clingo —
  this inversion IS the intended behavior change, not a weakened test).
- `tests/structured/aba/test_aba_sparse_narrow_route_contract.py` — unit
  tests for `large_dense_flat_aba_shape` boundaries (density, assumption
  count) with a `dense_flat_framework` builder. A non-flat case is
  unconstructible (`ABAFramework.__post_init__` raises `NotFlatABAError`), so
  flatness is covered by the type invariant.

## Test output

RED (before the fix), quoted from pytest:

```
FAILED tests/solving/test_solver_availability.py::test_large_dense_aba_stable_single_extension_auto_uses_asp_when_not_sparse_narrow
FAILED tests/solving/test_solver_availability.py::test_stable_single_extension_auto_backend_is_asp_for_large_dense_non_sparse_narrow
2 failed, 1 passed, 38 deselected in 2.41s
```
(failure detail: `AssertionError: assert 'sat' == 'asp'`; the sparse-narrow
"stays sat" test already passed, as expected.)

GREEN after the gate change:

```
3 passed, 38 deselected in 0.87s
```

Full correctness gates on the final commit:

```
uv run pytest tests/solving tests/interop -q
283 passed, 3 skipped in 6.90s
```
Skips are pre-existing environment skips (quoted from `-rs`):
```
SKIPPED [1] tests\solving\test_solver_adapters.py:600: set ICCMA_AF_SOLVER to an ICCMA 2023 AF solver executable
SKIPPED [1] tests\solving\test_solver_adapters.py:965: set ASPFORABA_SOLVER or ICCMA_ABA_SOLVER to an ICCMA 2023 ABA solver
SKIPPED [1] tests\solving\test_solver_encoding.py:416: ICCMA 2017 data not available
```

```
uv run pytest tests/structured -q
1478 passed in 259.94s (0:04:19)
```
(tests/structured includes all ABA test modules; run whole rather than a
`-k "aba"` selector since the layout puts them under tests/structured/aba.)

Pyright (coordinator raised a mid-task heads-up claiming
`large_dense_flat_aba_shape` was an unresolved import in solver.py and that
the benchmark might be emitting import-error rows):

- Runtime import PROVEN fine in the exact worker interpreter (script run via
  `uv run` in the worktree venv): solver module resolves to worktree src, the
  symbol imports, and `solver.large_dense_flat_aba_shape` is the identical
  object. All post-refactor pytest runs (49/283/1478 passed) also import it.
  The benchmark was NOT import-contaminated and was not killed.
- Repo-config pyright (`typeCheckingMode = "basic"`, pyright 1.1.408 via uv)
  on all four touched files at commit 7428faf: `54 errors, 0 warnings` — every
  error is a pre-existing `reportAttributeAccessIssue` on `.metadata` access
  against the solver-result union's error members in the OLD sections of
  test_aba_sparse_narrow_route_contract.py. Zero diagnostics on solver.py,
  aba_route_policy.py, or test_solver_availability.py; zero import-symbol
  errors.
- Same pyright invocation with the worktree detached at main (3ff70f3): also
  exactly `54 errors, 0 warnings`, same kind, same file. The commit introduces
  no new pyright diagnostics; the reported unknown-import does not reproduce
  at either revision.

One test-authoring gotcha found on the way: the contract file's
`sparse_narrow_framework` helper emits duplicate rules that the `frozenset`
collapses, so its nominal `rule_ratio=26` densities land below 25; the policy
unit tests use a dedicated unique-heads `dense_flat_framework` builder
instead.

## Metric gate

Command (both runs; flag semantics of `--max-af-arguments 1` verified in the
runner source — AF rows above the cap emit `status=skipped`, so the SE-ST
slice executes ABA rows only; the flag IS needed since SE-ST includes AF
instances):

```
uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025
  --only-subtrack SE-ST --backend auto --max-af-arguments 1
  --max-aba-assumptions 1000000 --timeout-seconds 15
  --label aba-sest-route-<baseline|fixed> --no-progress
```

Procedural incidents, disclosed:

1. The FIRST baseline attempt was invalidated mid-run: the worktree venv is an
   editable install and the runner spawns a fresh worker process per job, so
   workers began importing the fix as soon as it landed in src/. That run was
   killed and discarded. The clean baseline ran with the worktree detached at
   main (3ff70f3); the fixed run used the committed fix; no src edits during
   either run.
2. I ran pyright (per the coordinator's mid-task request) while the FIXED
   benchmark was running, which produced a measurable CPU-contention skew on
   that run (see kill evaluation) — quantified and spot-check-corrected below.

### Before/after table (SE-ST, 320 ABA rows executed, 322 AF rows skipped, 15s cap)

| run | solved | timeout |
|---|---|---|
| baseline (main 3ff70f3) | 217 | 103 |
| fixed (7428faf) | 227 | 93 |

Lost: 0. Answer mismatches: 0. Gained 10 (all timeout -> solved):

| instance | baseline | fixed |
|---|---|---|
| ABAs/aba_2000_0.1_10_10_0.aba | timeout 15s | solved 2.78s (w=162) |
| ABAs/aba_2000_0.1_10_10_7.aba | timeout 15s | solved 2.90s (w=157) |
| ABAs/aba_2000_0.1_10_5_0.aba | timeout 15s | solved 1.23s (w=23) |
| ABAs/aba_2000_0.1_10_5_1.aba | timeout 15s | solved 1.31s (no stable ext) |
| ABAs/aba_2000_0.1_10_5_2.aba | timeout 15s | solved 1.31s (w=28) |
| ABAs/aba_2000_0.1_10_5_4.aba | timeout 15s | solved 1.23s (w=34) |
| ABAs/aba_2000_0.1_10_5_8.aba | timeout 15s | solved 1.40s (w=28) |
| ABAs/aba_2000_0.1_5_5_7.aba | timeout 15s | solved 0.64s (w=158) |
| ABAs/aba_5000_0.1_10_5_7.aba | timeout 15s | solved 3.48s (w=65) |
| ABAs/aba_5000_0.1_5_5_6.aba | timeout 15s | solved 8.09s (no stable ext) |

All 8 positive gained witnesses were natively verified as stable extensions
by an independent closure check in scripts/compare_aba_sest_routes.py
(`natively verified stable: 8/10`; the other 2 are negative "no stable
extension" answers from clingo UNSAT, which have no cheap native check —
flagged, not verified).

### The NAMED rows (required by the gate to flip): NOT flipped

| instance | baseline | fixed |
|---|---|---|
| ABAs/aba_2000_0.1_5_5_1.aba | timeout 15.020s | timeout 15.009s |
| ABAs/aba_2000_0.1_5_5_6.aba | timeout 15.011s | timeout 15.013s |

Diagnosis (probe on fixed code, quoted from probe output):

```
parsed: atoms=2000 asms=200 rules=5560
auto backend decision: asp (0.003s)
direct AbaIncrementalSolver.find_stable_extension: 0.378s witness_size=152
```

then `simplify_aba(framework, semantics="stable")` ran for the remaining
>240s of the probe budget without finishing. The routing gate DID move these
rows to the asp backend, and the clingo solve itself takes 0.378s
(replicating the scout's 0.25s), but the production asp path
(`solve_aba_with_backend`, src/argumentation/structured/aba/aba_asp.py:99,
default `simplify=True`) runs `simplify_aba` before clingo, and that
preprocessing is the >15s bottleneck on exactly these two instances. The
scout's probe called clingo directly and bypassed it. The ten gained siblings
pass through preprocessing quickly. Fixing this is a simplifier budget/skip
change — outside this task's routing-only scope; left as the follow-up named
in the experiment record.

### abcgen SE-ST rows (expected: unchanged)

Statuses unchanged row-for-row across all abcgen SE-ST instances: every
baseline-solved abcgen row stays solved at comparable time (e.g.
abcgen_c7_atoms100_asms100_cp0.9_ins1 5.19s -> 5.09s), every baseline
timeout stays a timeout. Full listing in logs-compare-sest.txt (worktree).

### Timing on baseline-solved rows

- Commonly-solved (217 rows) aggregate: 362.86s -> 355.25s (**-2.10%**).
- Route flips among commonly-solved rows (via solver_metadata): exactly 6,
  all Z3-ranked-sat -> clingo_multishot, ALL faster (aba_5000_0.1_5_10_9
  12.77s->2.16s, _5_10_5 12.73s->2.34s, _5_10_4 7.80s->2.68s,
  aba_2000_0.1_5_10_7 4.35s->1.03s, _5_10_3 4.28s->1.09s,
  aba_5000_0.1_5_5_9 5.07s->4.46s).
- 82 rows show per-row >10% slowdowns, but all 82 are on UNCHANGED routes
  (identical code both runs), and same-route rows collectively skew +8.11%
  (82 slower / 7 faster / 122 within ±10%) — CPU contention during the fixed
  run (incident 2 above). Spot re-runs of the three worst offenders on fixed
  code, quiet machine: aba_5_3750literals 1.27s (baseline 1.19s, contended
  reading 2.18s), aba_5_5000literals 1.71s (1.63s / 3.12s),
  aba_6_5000literals 1.78s (1.58s / 2.40s) — baseline-level, confirming the
  slowdowns are environmental, not change-caused.

## Kill evaluation

- Baseline-solved SE-ST row lost: **0** — pass.
- Answer changed on baseline-solved rows: **0** — pass.
- >10% time regression on baseline-solved rows: aggregate **-2.10%**; every
  per-row >10% slowdown is on an unchanged code path with a demonstrated
  environment skew and spot-rerun refutation — no change-attributable
  regression — pass.
- "aba_2000_0.1_5_5_1 and _6 go timeout -> solved fast": **FAIL** — both
  still timeout. Root cause isolated (simplify_aba preprocessing, not
  routing); the ten sibling gains show the routing mechanism itself works.

No kill criterion is triggered; the headline named-row requirement is unmet
for a reason outside the changed code.

## Promotion recommendation

PROMOTE the routing change, with the named-row caveat stated. It is exactly
the scout's fix #1, tested (RED->GREEN, 5 new/updated tests, full suites
green, zero new pyright diagnostics), and on the frozen SE-ST slice it gains
10 solved rows, loses none, changes no answers, and speeds up every row whose
route it actually changed. The named rows need a follow-up experiment on
`simplify_aba` (budget it, or skip it for stable single-extension when the
incremental clingo path is available); that bottleneck exists on main today
and was merely unmeasurable before this fix because the Z3 path timed out
first. Not promoting keeps 10 rows timing out and still leaves the named rows
timing out.

## Commits (exp/aba-sest-clingo-route-v2)

- 7428faf — Gate ABA SE-ST sat override on sparse-narrow shape (fix + policy
  consolidation + tests).
- (follow-on docs commit, hash reported in the final summary) — experiment
  record, comparison script, this report, working notes.
