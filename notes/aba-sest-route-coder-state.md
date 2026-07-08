# Coder state: ABA SE-ST routing gate fix (checkpoint 1)

## Branch situation
- Dead-run branch `exp/aba-sest-clingo-route` exists with ZERO commits beyond main
  (`git log main..exp/aba-sest-clingo-route` empty). Per launcher instructions:
  ignored it, created `exp/aba-sest-clingo-route-v2` from main (= 3ff70f3, satisfies
  >= 3ff70f3 requirement). Experiment record must note the v2 rename.
- `ward set experiment-worker` done. Working dir = worktree
  C:\Users\Q\code\argumentation\.claude\worktrees\agent-a37b2faa009d7f04f.

## Code facts (verified by reading current source)
- Gate has drifted from scout's solver.py:575-582 to
  `src/argumentation/solving/solver.py:501-508` inside
  `_auto_aba_backend_for_framework` (def at :486). Current stable+single-extension
  auto override: `_is_large_dense_flat_aba(framework)` -> "sat".
- `_is_large_dense_flat_aba` at solver.py:512-518: asms>150, flat, rules/asms>25.
- Duplicate predicate in aba_route_policy.py: `native_cnf_prefsat_dense_shape`
  (constants 150 / 25.0, is_flat) — same truth table. `_is_flat_aba` helper there too.
  Consolidation plan: delegate solver.py `_is_large_dense_flat_aba` to
  `native_cnf_prefsat_dense_shape` + `_is_flat_aba`; behavior-neutral (0-asm guard kept).
- PLANNED FIX (per prompt "No other routing change"): condition becomes
  `_is_large_dense_flat_aba(framework) AND sparse_narrow_native_sat_shape(framework)`.
  Rationale: plain replacement with sparse_narrow alone would flip abcgen_c25 SE-ST
  (sparse_narrow=True, large_dense=False, currently asp) from asp->sat = a forbidden
  extra routing change. Conjunction keeps c25=asp, c35_asms30=sat, aba_2000->asp (the fix).
- Existing test that encodes the OLD policy:
  tests/solving/test_solver_availability.py:130
  `test_large_dense_aba_stable_single_extension_auto_uses_sat_not_clingo` with
  `_large_dense_aba_framework` (151 asms, body 1, injective contraries, dens 26,
  sparse_narrow FALSE because asms<700) — will need updating to assert asp under new
  policy (this is the intended behavior change, not test weakening).
- RED tests to add (mirror monkeypatch style at :130): (a) large-dense
  non-sparse-narrow (aba_2000-like) stable single-extension auto -> asp;
  (b) large-dense sparse-narrow (>=700 asms, body<=2, injective contra,
  asms/lang<=0.45, dens>25) -> sat. Plus direct `_auto_aba_backend_for_framework`
  decision asserts with `_has_clingo` monkeypatched True.

## Runner facts (verified)
- tools/iccma2025_run_native.py: `--max-af-arguments 1` marks AF rows with >1 args
  as status=skipped (run_or_skip, tools line ~361) — SE-ST slice becomes ABA-only
  solved rows; AF rows appear as skipped. Flag semantics confirmed from source.
- Output: <root>/runs/iccma-2025-<label>.{json,csv,summary.json}.
- Task matrix: SE-ST has 2 entries (one af, one aba kind presumably). Timeout per
  prompt: 15s, --max-aba-assumptions 1000000.
- Baseline must run BEFORE code changes (branch currently == main, so running
  baseline now is equivalent to unmodified main). NOT YET STARTED.

## Next steps
1. Launch baseline benchmark in background (label aba-sest-route-baseline).
2. RED: write failing routing tests; run them, quote failure.
3. GREEN: change solver.py:506 condition; tests pass.
4. REFACTOR: consolidate _is_large_dense_flat_aba into aba_route_policy delegation.
5. Gates: uv run pytest tests/solving tests/interop; tests/structured/aba.
6. Fixed benchmark run (label aba-sest-route-fixed); compare; named rows
   aba_2000_0.1_5_5_1 / _6 must flip timeout->solved; abcgen rows unchanged TO.
7. experiments/2026-07-07-aba-sest-clingo-route.md (note v2 branch), report,
   commit, SendMessage.

## Checkpoint 2 (RED->GREEN done, refactor in progress)
- Baseline benchmark RUNNING in background (id bixtd788q), label
  aba-sest-route-baseline, output logs-baseline-sest.out in worktree; results will
  land in data/iccma/2025/runs/iccma-2025-aba-sest-route-baseline.{json,csv}.
  Launched while src was verified identical to main (git diff main --stat -- src/ empty).
- RED verified: added to tests/solving/test_solver_availability.py:
  `_large_dense_non_sparse_narrow_aba_framework` (200 asms, body-5 rules, contra
  mult 3, dens 26 — mirrors aba_2000 failure reasons), `_sparse_narrow_large_dense_
  aba_framework` (700 asms, body-1, injective, dens 26); tests
  test_stable_single_extension_auto_backend_is_asp_for_large_dense_non_sparse_narrow
  (FAILED 'sat'=='asp' before fix), ..._stays_sat_for_sparse_narrow (passed),
  and flipped test_large_dense_aba_stable_single_extension_auto_uses_asp_when_not_
  sparse_narrow (FAILED before fix). Quoted RED output: "2 failed, 1 passed".
- GREEN verified: solver.py stable gate now requires
  `_is_large_dense_flat_aba(framework) and sparse_narrow_native_sat_shape(framework)`
  (solver.py ~:501-509). Rerun: "3 passed, 38 deselected".
- Contract test tests/structured/aba/test_aba_sparse_narrow_route_contract.py:65
  uses sparse_narrow_framework(700, rule_ratio=4) → density 4 < 25 → large_dense
  False → asp both before and after; unaffected. Verified by reading.
- REFACTOR in progress: added `large_dense_flat_aba_shape(framework)` to
  aba_route_policy.py (delegates to native_cnf_prefsat_dense_shape + _is_flat_aba;
  0-assumption guard via density 0.0). NEXT: replace solver.py
  `_is_large_dense_flat_aba` body/uses with import of large_dense_flat_aba_shape,
  rerun tests, then full gates (tests/solving tests/interop tests/structured/aba).

## Checkpoint 3 (refactor done, gates pending)
- REFACTOR complete: `large_dense_flat_aba_shape(framework)` added to
  aba_route_policy.py (delegates to native_cnf_prefsat_dense_shape + _is_flat_aba,
  0-assumption -> density 0.0). solver.py `_is_large_dense_flat_aba` DELETED; gate
  now `large_dense_flat_aba_shape(framework) and sparse_narrow_native_sat_shape(framework)`.
  grep confirms zero remaining `_is_large_dense_flat_aba` references.
- Learned: ABAFramework.__post_init__ ENFORCES flatness (NotFlatABAError), so
  non-flat ABAFramework unit test impossible; covered density + size boundaries
  instead via new `dense_flat_framework` helper in
  tests/structured/aba/test_aba_sparse_narrow_route_contract.py (2 new policy tests).
- Gotcha found: sparse_narrow_framework helper produces DUPLICATE rules that
  frozenset collapses -> density below 25 despite rule_ratio=26. First policy test
  failed for that reason; fixed by unique-head dense_flat_framework helper. My
  availability-test helpers already used unique heads (no dedup issue).
- Touched modules green: `uv run pytest tests/structured/aba/test_aba_sparse_narrow_route_contract.py tests/solving/test_solver_availability.py -q` -> "49 passed in 1.32s".
- Baseline benchmark (bixtd788q) still running: task matrix 27 tasks, SE-ST slice
  built 642 jobs (includes AF rows that will be skipped via --max-af-arguments 1).
  NOTE: --no-progress means no per-row logs; results appear only at completion in
  data/iccma/2025/runs/iccma-2025-aba-sest-route-baseline.*. Could take tens of
  minutes if many 15s timeouts.
- NEXT: full correctness gates (uv run pytest tests/solving tests/interop; then
  tests/structured/aba), then commit RED+GREEN+REFACTOR, then wait baseline,
  then fixed benchmark run, comparison, experiment record (v2 branch note), report.

## Checkpoint 4 — BASELINE CONTAMINATION INCIDENT + recovery
- Correctness gates GREEN on the fix:
  - `uv run pytest tests/solving tests/interop -q` -> "283 passed, 3 skipped in 6.90s".
    Skips pre-existing/environmental: ICCMA_AF_SOLVER unset (test_solver_adapters.py:600),
    ASPFORABA_SOLVER/ICCMA_ABA_SOLVER unset (:965), ICCMA 2017 data absent
    (test_solver_encoding.py:416).
  - `uv run pytest tests/structured -q` -> "1478 passed in 259.94s".
- COMMIT: 7428faf "Gate ABA SE-ST sat override on sparse-narrow shape"
  (solver.py gate + policy consolidation + 5 tests across 2 test files).
- INCIDENT: first baseline run was CONTAMINATED. Discovered .venv install is
  EDITABLE (direct_url.json dir_info.editable=true; __editable__ pth) and the
  runner spawns a fresh python subprocess PER JOB (run_child, tools line 504),
  so workers launched after my GREEN edit imported FIXED code while labeled
  baseline. Killed the whole process tree via taskkill (PIDs incl. 423660
  runner python). Contaminated partial outputs (if any) under
  data/iccma/2025/runs/iccma-2025-aba-sest-route-baseline.* will be OVERWRITTEN
  by the clean rerun (same label). Background task bixtd788q reported failed
  (exit 1) = the kill, expected.
- RECOVERY PLAN (in progress): (1) FIXED run now on committed fix, background id
  bb5yn7a1z, label aba-sest-route-fixed, log logs-fixed-sest.out. NO src edits
  during runs. (2) After it completes: `git checkout --detach main` in this
  worktree, rerun baseline label aba-sest-route-baseline, then
  `git checkout exp/aba-sest-clingo-route-v2`. Branch checkout is allowed
  (forbidden list = stash/restore/reset/clean/path-checkout); tree is clean.
- No heavy pytest during benchmark runs (timing comparability).

## Checkpoint 5 — fixed run in flight, tooling staged
- FIXED benchmark running (bg id bb5yn7a1z, label aba-sest-route-fixed, jobs=642,
  log logs-fixed-sest.out; no per-row progress because --no-progress). SE-ST slice
  = 322 AF rows (skipped via cap) + 320 ABA rows (executed, 15s timeout).
  Named rows present in manifest: ABAs/aba_2000_0.1_5_5_1.aba and _6.aba (200
  assumptions each). 120 abcgen ABA instances total.
- experiments/2026-07-07-aba-sest-clingo-route.md drafted with v2-branch note and
  contamination note; RESULTS/INTERPRETATION/DECISION placeholders pending runs.
- Wrote scripts/compare_aba_sest_routes.py (modeled on compare_af_sststg_runs.py):
  status tables, lost (kill), gained, answer mismatches (kill), commonly-solved
  total + per-row >10% regression list (kill), named rows, all abcgen rows, and
  native closure-based stable-witness verification for gained/witness-changed
  solved ABA rows (flat ABA: W stable iff no contrary of W in Cl(W) and contrary
  of every outside assumption in Cl(W); closedness free by flatness).
  Witness text tokens = repr(Literal) = bare atom name for non-negated atoms.
- Baseline rerun plan after fixed completes: `git checkout --detach main` (3ff70f3)
  in worktree -> rerun with label aba-sest-route-baseline -> checkout branch back.
  Editable venv means detached src is what workers import. Do NOT edit src during.
- Commit so far: 7428faf on exp/aba-sest-clingo-route-v2.

## Checkpoint 6 — coordinator pyright heads-up; runtime import PROVEN fine
- Coordinator mid-task message: pyright reports `large_dense_flat_aba_shape`
  UNKNOWN import symbol (solver.py:45, contract test :11) plus `.metadata`
  attr errors on Solver*Error at contract test ~107-109; asked to verify the
  running fixed benchmark isn't emitting import-error rows.
- VERIFIED runtime import fine in the EXACT worker interpreter
  (scratchpad import_check.py via `uv run`): python =
  worktree .venv\Scripts\python.exe, solver.__file__ = worktree src solver.py,
  symbol imports, solver.large_dense_flat_aba_shape is same object. Plus all
  post-refactor pytest runs (49/283/1478 passed) imported these modules.
  => fixed benchmark NOT import-contaminated; did NOT kill it.
- `.metadata` union-attr access pattern at contract test lines ~107-109 is
  PRE-EXISTING in that file (same access at lines ~149-155 predates my change;
  my added policy tests don't touch .metadata).
- ward gotcha: both `.venv/Scripts/python.exe script.py` and `uv run python
  script.py` are blocked; sanctioned form is `uv run script.py`.
- Report skeleton written (reports/aba-sest-route-coder.md): branch deviation,
  diff summary, test output sections DONE; metrics/kill/recommendation pending.
- pyproject.toml has [tool.pyright] (line 92), pyright>=1.1.390 in dev deps.
- NEXT: run pyright on touched files, record actual diagnostics; then wait on
  fixed benchmark (bg bb5yn7a1z; monitor bfuxytd0v watches for
  runs/iccma-2025-aba-sest-route-fixed-summary.json), then baseline rerun on
  detached main, comparison, docs, commits.

## Checkpoint 7 — pyright adjudicated
- Ran repo-config pyright (typeCheckingMode=basic, pyright 1.1.408 via uv) on all
  4 touched files -> logs-pyright-touched.txt: 54 errors, ALL in
  tests/structured/aba/test_aba_sparse_narrow_route_contract.py, ALL
  reportAttributeAccessIssue `.metadata` on the SingleExtensionSolverResult
  union's error members (lines 142-146, ~149-155, 191-196, 228-231 = the
  PRE-EXISTING end-to-end tests, shifted ~+40 by my insertion at lines 11+65-96).
  ZERO diagnostics for solver.py, aba_route_policy.py,
  test_solver_availability.py, and ZERO import-symbol errors. Coordinator's
  "unknown import symbol at solver.py:45" does NOT reproduce under the repo's
  own pyright config — likely stale index on their side. Benchmark NOT killed
  (runtime import already proven fine in checkpoint 6).
- TODO during baseline phase: run same pyright at detached main to prove the 54
  are pre-existing (expect same errors at unshifted lines).
- Fixed benchmark still running ~35 min in (no runs/ output yet; jobs=642).

## Checkpoint 8 — fixed run done; baseline in flight on detached main; pyright pre-existence PROVEN
- FIXED run completed exit 0. Summary: {skipped: 322 (all AF), solved: 227,
  timeout: 93} of 642 rows; ABA rows = 320. Outputs at
  data/iccma/2025/runs/iccma-2025-aba-sest-route-fixed.{json,csv,summary}.
- Worktree DETACHED at main 3ff70f3 (clean; verified solver.py has old
  `_is_large_dense_flat_aba(framework)` at :506, zero large_dense_flat_aba_shape).
  Branch exp/aba-sest-clingo-route-v2 still holds 7428faf; untracked files
  (report, notes, logs, comparison script, experiment md) persist across checkout.
- BASELINE run launched on main code: bg id bd1wt5aa3, label
  aba-sest-route-baseline, log logs-baseline-sest.out.
- PYRIGHT AT MAIN on the same 4 files: "54 errors, 0 warnings" — IDENTICAL
  count/kind (all reportAttributeAccessIssue .metadata in the contract test).
  => my commit introduces ZERO new pyright diagnostics; coordinator's
  import-symbol report does not reproduce at either revision with repo config.
- AFTER baseline completes: `git checkout exp/aba-sest-clingo-route-v2`, run
  scripts/compare_aba_sest_routes.py BASELINE_JSON FIXED_JSON DATA_ROOT,
  fill experiment md + report, commit script+docs, SendMessage.

## Checkpoint 9 — BOTH RUNS DONE; comparison done; named rows STILL TIMEOUT; root cause isolated to simplify_aba
- Baseline (main 3ff70f3): 217 solved / 103 timeout / 322 AF-skipped.
  Fixed (7428faf): 227 solved / 93 timeout / 322 skipped. Back on branch
  exp/aba-sest-clingo-route-v2. Comparison log: logs-compare-sest.txt.
- Comparison (scripts/compare_aba_sest_routes.py, with native witness checks):
  - LOST: 0. Answer mismatches: 0.
  - GAINED 10: aba_2000_0.1_10_10_0 (2.78s), _10_10_7 (2.90s), _10_5_0 (1.23s),
    _10_5_1 (1.31s, witness None = reports NO stable ext), _10_5_2 (1.31s),
    _10_5_4 (1.23s), _10_5_8 (1.40s), aba_2000_0.1_5_5_7 (0.64s),
    aba_5000_0.1_10_5_7 (3.48s), aba_5000_0.1_5_5_6 (8.09s, witness None).
  - Witness verification: 8/8 positive witnesses natively verified stable
    (closure check). The 2 witness=None rows are negative answers ("no stable
    extension"), not cheaply verifiable natively — flag in report.
  - Commonly-solved (217 rows) total: baseline 362.86s -> fixed 355.25s =
    -2.10% (aggregate under the +10% kill line).
  - Per-row >10% regressions: 82 rows, worst aba_5_3750literals 1.19->2.18s,
    aba_5_5000literals 1.63->3.12s (~+91%); mostly aba_N_XXXXliterals family
    and 0.2-0.5s rows with +0.03-0.1s deltas. Pattern suggests some flipped
    route sat->asp too (large-dense, not sparse-narrow) and clingo is
    slower-but-still-solving; sub-second deltas may be noise. TODO: quantify
    which regressed rows changed route (solver_metadata in run JSONs).
  - abcgen SE-ST rows: statuses UNCHANGED per-row (solved stay solved ~equal
    times, timeouts stay timeouts) — as required.
- CRITICAL FINDING: named rows aba_2000_0.1_5_5_1/_6 STILL TIMEOUT in fixed
  run (metric gate REQUIRED them to flip). Probe on fixed code
  (scratchpad probe_named_row.py -> probe-named-row.out):
  - auto backend decision = asp (gate works, 0.003s);
  - DIRECT AbaIncrementalSolver.find_stable_extension = 0.378s witness 152
    (scout's 0.25s replicated);
  - simplify_aba(framework, semantics="stable") RAN >240s WITHOUT FINISHING
    (probe killed during that stage). solve_aba_with_backend (aba_asp.py:99,
    simplify=True default) calls simplify_aba BEFORE clingo — the
    preprocessing, not clingo, is why named rows still timeout at 15s.
  - Scout's projection missed that the production asp route includes
    simplify_aba; flipped siblings evidently simplify fast. Fixing named rows
    needs a simplify budget/skip — OUT OF SCOPE for this routing-only task;
    report honestly: metric gate PARTIAL (named rows unchanged) + collateral
    win (+10 solved, 0 lost, 0 mismatches, aggregate -2.1%).
- Exit-code note: `timeout 240 uv run ...` returned 127 while producing
  output; gitbash timeout exit codes unreliable — rely on output files.
- NEXT: (1) quantify route-flip among regressed rows via solver_metadata;
  (2) kill evaluation per criteria; (3) fill experiment md + report;
  (4) commit script+docs+notes; (5) 5-line summary to main.

## Checkpoint 10 — analysis complete, docs written, pre-commit checks green
- Route-flip analysis (scratchpad route_flip_analysis.py): of 217
  commonly-solved rows, 211 same-route (clingo_multishot both runs — most
  solved ABA SE-ST rows were ALREADY asp at baseline), 6 flipped Z3-sat->asp
  and ALL 6 got faster (12.77->2.16s, 12.73->2.34s, 7.80->2.68s, 4.35->1.03s,
  4.28->1.09s, 5.07->4.46s). ZERO regressed rows changed route. Baseline
  (None,None) metadata = Z3 sat path (returns success without metadata).
- Noise symmetry (scratchpad noise_symmetry.py): same-route rows skew +8.11%
  aggregate (82 slower / 7 faster / 122 within +-10%) => fixed run had CPU
  contention (my pyright runs during it — disclosed in report). Spot solo
  reruns of 3 worst on fixed code: 1.27s/1.71s/1.78s vs baselines
  1.19s/1.63s/1.58s (contended readings 2.18/3.12/2.40) => environmental.
  Spot-check label: aba-sest-route-spotcheck in runs/.
- experiments/2026-07-07-aba-sest-clingo-route.md COMPLETE (results,
  interpretation, decision: metric gate PARTIAL, recommend PROMOTE +
  simplify_aba follow-up).
- reports/aba-sest-route-coder.md COMPLETE except FINAL_COMMIT_PLACEHOLDER
  (needs final commit hash).
- Pre-commit checks: pyright scripts/compare_aba_sest_routes.py = "0 errors,
  0 warnings"; routing tests re-run green "49 passed in 1.34s".
- NEXT (only steps left): (1) git add experiments/2026-07-07-aba-sest-clingo-
  route.md scripts/compare_aba_sest_routes.py reports/aba-sest-route-coder.md
  notes/aba-sest-route-coder-state.md; commit; (2) replace
  FINAL_COMMIT_PLACEHOLDER with hash via amend-free second commit? NO —
  simpler: commit docs first WITHOUT placeholder text fixed, then amend is
  forbidden? (amend not forbidden but keep simple): plan = fix placeholder to
  say "docs commit (this commit)" BEFORE committing, then commit once, then
  report hash in final message; (3) 5-line summary to main as final message.

## Blockers
None. Finishing commits + summary.
