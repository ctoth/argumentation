# Working state: exp 4B — simplify_aba(stable) pre-solve hang

## Status
Investigation phase (pre-implementation). Branch `exp/aba-simplify-stable-budget`
created off main@cc50c4a (contains bc140ba SE-ST routing gate — preflight PASS).
`ward set experiment-worker` done.

## Evidence chain (all three reports read)
- scout: aba_2000_0.1_5_5_{1,6} SE-ST — clingo find_stable solves 0.25s; shape
  fails sparse_narrow (200 asms, body<=5, contra mult 3).
- exp-4 coder: routing gate landed (now main bc140ba); named rows still TO because
  `solve_aba_with_backend(..., simplify=True)` runs simplify_aba BEFORE clingo.
- verifier: simplify_aba(stable) on aba_2000_0.1_5_5_1 EXCEEDS 200s cap; clingo
  core with simplify=False = 0.376s. stable IS in GROUNDED_REDUCT_ABA_SEMANTICS.

## Root cause located (code read)
Call chain: solve_aba_with_backend (aba_asp.py:99, simplify=True default)
-> simplify_aba (aba_preprocessing.py:241)
-> grounded_assumption_set_via_supports (aba_preprocessing.py:143)
-> _SupportState.from_framework (aba_support_model.py:31)
-> _minimal_supports (aba_support_model.py:108) — EXPONENTIAL minimal-support
enumeration: `_combine_supports` takes Cartesian products over rule bodies
(up to 5 antecedents on this shape, contra mult 3, 5560 rules, 2000 atoms).
Same `_add_minimal_support` hotspot the DC-CO profile measured at 92.7%.
Everything else in simplify_aba is polynomial (`_forward_closure` = horn_closure,
`_residual_framework` is O(rules)). The cheap bail-out at aba_preprocessing.py:265
already computes 2 forward closures and evidently does NOT fire on these rows.

## Chosen design (option a — algorithmic fix), to be justified in record
Grounded assumption set does NOT need minimal supports. Closure-based def
operator, all-polynomial:
- attacked_by(S) = {b : contrary(b) in horn_closure(S)}
- defended(a) iff contrary(a) NOT in horn_closure(assumptions - attacked_by(S))
Proof of equivalence with current mask code: contrary(a) in Th(X) iff exists
minimal support s subseteq X. X = assumptions\attacked; s=empty subseteq X always,
so "not defended iff exists s with s∩attacked=∅ (incl. s=∅)" == current per-mask
check (support==0 -> not defended; support&attacked==0 -> not defended). Iterate
def from ∅ (monotone, keep selected ∪ defended) — identical fixpoint. <=n+1
iterations × 2 closures each.
Prior verification of current impl: reports/graph-speedup-wave-c3-analyst.md —
matches ∩complete on 800 random (aba.grounded_extension itself has a known bug).

## Other callers of grounded_assumption_set_via_supports
- aba_incremental.py:469 (AbaIncrementalSolver.grounded_extension) — also benefits.
- tests/structured/aba/test_aba_preprocessing.py:21,188,247 (differential oracle
  tests exist — these are my equivalence safety net).
Plan: rename to implementation-neutral `grounded_assumption_set` OR keep name?
Leaning: rename in refactor step, update 2 callers + tests + __all__.

## Next steps
1. Profiling script (scripts/, uv run) proving blow-up on aba_2000_0.1_5_5_1:
   time bail-out closures (fast) + subprocess-timeout _SupportState.from_framework
   (hangs) + prototype closure-based grounded (ms). Instance at
   data/iccma/2025/ABAs/aba_2000_0.1_5_5_1.aba (verify path).
2. RED test: simplify_aba completes within budget on a construct that blows up
   minimal supports (small chained multi-antecedent rules with combinatorial
   supports) — plus equality-of-reduct differential tests stay green.
3. Implement, GREEN, refactor.
4. Correctness gates: uv run pytest tests/solving tests/interop tests/structured.
5. Metric gate: iccma runner SE-ST baseline (detached main) vs fixed, labels
   aba-simplify-{baseline,fixed}; poll output mtimes. Also frontier driver
   scripts/run_frontier_v1.py --subtrack SE-ST 120s if present on main.
6. Deliverables: experiments/2026-07-08-aba-simplify-stable-budget.md,
   reports/aba-simplify-budget-coder.md, commits.

## Profiling DONE (scripts/profile_aba_simplify_stable.py, logs-profile-simplify.txt)
Quoted results:
- aba_2000_0.1_5_5_1: bail-out closures 0.026s (does NOT bail out);
  closure-based prototype 0.131s |grounded|=152; _SupportState.from_framework
  TIMEOUT >60s (subprocess killed).
- aba_2000_0.1_5_5_6: bail-out 0.040s no-bail; prototype 0.124s |grounded|=152;
  from_framework TIMEOUT >60s.
- Equivalence (current impl vs prototype, small instances): aba_100_0.1_10_10_6
  equal=True (0.011s vs 0.019s); _10_10_7 equal=True; _10_5_7 equal=True and
  current=13.962s vs prototype=0.004s (blow-up already visible at 100 atoms).
DIAGNOSIS CONFIRMED: exponential _minimal_supports enumeration inside
grounded_assumption_set_via_supports; everything else polynomial. |grounded|=152
matches the clingo witness size 152 from scout/coder reports (consistent).

DESIGN CHOSEN: option (a) only — replace support-mask fixpoint with closure-based
def-operator fixpoint (exact, polynomial: <=n+1 rounds x 2 horn_closures).
No budget (b) needed since result is worst-case polynomial; no skip (c) needed
since simplify becomes cheap and is genuinely useful here (fixes 152/200 asms).

## TDD plan
pytest-timeout>=2.3 IS in pyproject (line 145) — RED test uses
@pytest.mark.timeout on a Cartesian blow-up framework (layered rules, ~3^k
minimal supports) where old code hangs, new code instant. Plus differential
equality tests (existing oracle tests at tests/structured/aba/
test_aba_preprocessing.py:188,247 stay green).
Refactor step: function renamed? Leaning keep public name
`grounded_assumption_set_via_supports`? NO — name would lie. Decide during
refactor; callers: aba_incremental.py:469, simplify_aba, tests.

## Next
1. RED test in tests/structured/aba/test_aba_preprocessing.py.
2. GREEN: rewrite grounded_assumption_set_via_supports body.
3. REFACTOR: naming/docstring (module docstring at top of aba_preprocessing.py
   also references support-mask machinery — update).
4. Gates: uv run pytest tests/solving tests/interop tests/structured.
5. Metric gate SE-ST baseline (detached at main cc50c4a — remember editable
   venv hazard from exp-4: baseline MUST run with worktree src at main) then
   fixed. Labels aba-simplify-{baseline,fixed}. Poll file mtimes.
6. scripts/run_frontier_v1.py exists in worktree — check flags before use.

## TDD progress
- RED: two tests added to tests/structured/aba/test_aba_preprocessing.py
  (test_grounded_via_supports_polynomial_on_minimal_support_blowup — later
  renamed grounded_via_supports->closures in the identifier sweep — and
  test_simplify_aba_stable_polynomial_on_minimal_support_blowup) using
  _layered_choice_blowup_framework (3**12 minimal supports, q_0 fact, per-level
  x/y/z choices, contrary(t)=q_12; grounded = all-but-t, fixed_out={t}).
  RED confirmed: pytest-timeout(60) fired, stack pinned at
  aba_support_model.py:153 _add_minimal_support inside _SupportState.from_framework.
  NOTE: pytest-timeout thread method aborts whole session on RED — no summary
  line; the Timeout dump IS the failure evidence.
- GREEN: rewrote grounded_assumption_set_via_supports body in
  aba_preprocessing.py to closure-based def fixpoint (2 horn closures/round,
  monotone, <=n+1 rounds). Result: 132 passed in 114s (whole preprocessing file,
  incl. differential oracles).
- REFACTOR (in progress): renamed grounded_assumption_set_via_supports ->
  grounded_assumption_set_via_closures. DONE in aba_preprocessing.py, test file,
  scripts/profile_aba_simplify_stable.py. PENDING: aba_incremental.py (Edit
  failed — file not read yet; must Read then Edit lines 39, 469). Also updated
  module docstring (support-mask -> forward-closure). __all__ updated via sweep.
  Test names still say "via_supports"? — check test file after sweep (function
  name test_grounded_via_supports_... contains the substring so it WAS renamed
  by replace_all to test_grounded_via_closures_...? NO — substring was
  'grounded_assumption_set_via_supports', test fn name is
  'test_grounded_via_supports_polynomial...' which does NOT contain it; rename
  test fn manually for honesty).

## Refactor DONE + gates GREEN + commit 1
- Rename complete everywhere (aba_incremental.py:39,469 done via Read+Edit;
  test fn names test_grounded_via_closures_*; zero grep hits for via_supports
  in src/tests/scripts).
- Gates: tests/solving+tests/interop = 291 passed, 3 skipped (same 3
  pre-existing env skips as exp-4). tests/structured = 1480 passed in 282.58s
  (exp-4 had 1478; +2 = my two new blowup tests). Log:
  logs-pytest-structured-fixed.txt (worktree root, untracked).
- COMMIT 1 = 8a934dc "Compute ABA grounded fixpoint via Horn closures, not
  minimal supports" (4 files: aba_preprocessing.py, aba_incremental.py,
  test_aba_preprocessing.py, scripts/profile_aba_simplify_stable.py).

## Metric gate plan (next)
1. BASELINE on unmodified main: worktree venv is EDITABLE (exp-4 lesson) —
   must detach worktree src at main cc50c4a while baseline runs. Method used
   by exp-4 coder: git checkout --detach? FORBIDDEN ops list includes
   git checkout <path> (pathspec) — branch/detach checkout of the whole tree
   is allowed and reversible (git checkout exp/... to come back). Plan:
   `git checkout --detach cc50c4a` -> run baseline -> `git checkout
   exp/aba-simplify-stable-budget` -> run fixed. No src edits during runs.
2. Command: uv run tools/iccma2025_run_native.py --root
   C:\Users\Q\code\argumentation\data\iccma\2025 --only-subtrack SE-ST
   --backend auto --max-aba-assumptions 1000000 --timeout-seconds 15
   --label aba-simplify-baseline|aba-simplify-fixed
   (exp-4 also used --max-af-arguments 1 to skip AF rows — prompt's command
   omits it; CHECK runner flags: without it AF SE-ST rows will run and burn
   hours. exp-4 verified AF rows emit status=skipped with the cap. Add it?
   Prompt command lacks it but prompt says "Same SE-ST slice command as exp 4"
   — exp 4 DID use --max-af-arguments 1. Use exp-4's exact command with both
   caps; labels from this prompt.)
3. Background run, poll output file mtimes in a loop (one-shot monitors
   unreliable). Find where runner writes output (data/iccma/2025/runs?).
4. After both: compare named rows aba_2000_0.1_5_5_{1,6} (expect solved ~2s),
   abcgen rows unchanged, no lost/changed rows, >10% common-solved regression
   = kill. Reuse/adapt scripts/compare_aba_sest_routes.py.
5. Frontier: scripts/run_frontier_v1.py --subtrack SE-ST at 120s if flags
   support it (check source first).

## Metric gate in flight
- Worktree DETACHED at main cc50c4a (tracked files show main content — my fix
  lives only on branch commit 8a934dc; DO NOT edit src while detached).
- BASELINE run launched in background (task br1izjaho):
  uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025
  --only-subtrack SE-ST --backend auto --max-af-arguments 1
  --max-aba-assumptions 1000000 --timeout-seconds 15
  --label aba-simplify-baseline --no-progress > logs-run-baseline.txt
  (--max-af-arguments 1 added vs prompt's literal command: prompt says "Same
  SE-ST slice command as exp 4" and exp-4 used it — AF rows skip, ABA-only
  slice, identical row set to exp-4 tables. DISCLOSE in report.)
- Output written only at END: data/iccma/2025/runs/iccma-2025-aba-simplify-baseline.{json,csv}
  + -summary.json. Polling until file exists; ~20 min elapsed, python workers
  alive (tasklist confirms). Expect ~30-40 min (exp-4: 103 baseline TOs x 15s).
- data/ is gitignored — writing runs there does not touch tracked main tree.
- experiments/2026-07-08-aba-simplify-stable-budget.md DRAFTED (untracked;
  RESULTS-PENDING markers for metric gate). Design justification for (a) over
  (b)/(c) written in.
- Comparison: scripts/compare_aba_sest_routes.py (on main) is generic:
  uv run scripts/compare_aba_sest_routes.py BASELINE_JSON FIXED_JSON [DATA_ROOT]
  — includes named rows, abcgen table, >10% regression kill check, witness
  verification. Reuse as-is.
- Frontier driver scripts/run_frontier_v1.py EXISTS on main: flags --subtrack
  SE-ST --timeout-seconds 120 --label ... --manifest (DEFAULT_MANIFEST) — run
  SE-ST chunk after fixed run, on branch code.

## Remaining sequence
1. Baseline JSON appears -> checkout branch exp/aba-simplify-stable-budget.
2. Launch fixed run (label aba-simplify-fixed). Poll.
3. compare script baseline vs fixed (+ DATA_ROOT witness check).
4. run_frontier_v1.py --subtrack SE-ST (branch code, 120s) — check its
   DEFAULT_MANIFEST/OUTPUT_DIR first.
5. Finalize experiment record + reports/aba-simplify-budget-coder.md, commit
   docs (+ notes), report hashes, SendMessage 5-line summary to main.

## METRIC GATE RESULTS (first pass) — NAMED ROWS STILL TIMEOUT
- baseline (main cc50c4a): 225 solved / 95 timeout (320 ABA rows).
- fixed (branch 8a934dc): 226 solved / 94 timeout.
- LOST=0, answer mismatches=0, aggregate elapsed -5.19% on 225 common-solved.
- gained (1): aba_2000_0.3_10_10_9 (timeout -> solved 13.99s, answer None =
  no-stable-extension row?).
- 12 per-row >10% regressions, mostly abcgen (unchanged routes) — looks
  environmental again, must quantify/spotcheck later.
- **PROBLEM: aba_2000_0.1_5_5_1 and _6 BOTH STILL TIMEOUT at 15s in fixed.**
  So simplify was NOT the only >15s stage, OR the fixed run didn't exercise my
  code (venv check needed), OR another stage dominates.

## Second bottleneck hunt (in progress)
- Runner path: solve_aba_job -> solve_aba_single_extension (solver.py:173).
  For stable+auto on this shape -> backend asp -> _solve_asp_aba_single_extension
  (solver.py, need to read) with clingo_control_args=() etc.
- exp-4 coder probe had found: backend decision asp 0.003s, DIRECT
  AbaIncrementalSolver.find_stable_extension 0.378s, then production path hung
  in simplify_aba. My fix makes simplify_aba fast (0.13s grounded). So either
  _solve_asp_aba_single_extension has ANOTHER slow stage (residual solve? task
  dispatch? enumeration instead of single?) or the lift/verify path is slow.
- NEXT: read _solve_asp_aba_single_extension + _solve_simplified (aba_asp.py),
  then write scripts/probe_aba_sest_named_row.py timing each stage on
  aba_2000_0.1_5_5_1 with branch code: simplify_aba, residual solve, full
  solve_aba_single_extension. Verify code version imported (print module file +
  function name grounded_assumption_set_via_closures exists).
- Comparison output: logs-compare-simplify.txt (worktree root). Runs at
  data/iccma/2025/runs/iccma-2025-aba-simplify-{baseline,fixed}.*.

## SECOND BOTTLENECK ROOT-CAUSED + RED CONFIRMED
- Path: solve_aba_single_extension -> _solve_asp_aba_single_extension ->
  solve_aba_with_backend -> simplify (now fast) -> _solve_simplified ->
  residual solve OK (core facts, include_supports=False, multishot
  find_stable_extension) -> **aba_asp.py:436 `encode_aba_theory(original)`**
  with default include_supports=True -> `_minimal_supports(original)` — the
  SAME exponential primitive, on the FULL original framework, building
  support_* facts that asp/clingo backends never consume (they are only
  result payload; residual solve builds its own core-facts encoding).
  Second instance at aba_asp.py:486 `_solve_simplified_ds_pr` (backend
  guaranteed asp/clingo there — caller gates on it at :408-413).
- _task_result single-extension branch is cheap (no derives calls). No test
  depends on flat_aba_assumption_support_facts in simplified results (grepped).
  aba_incremental.py:300 builds its own include_supports=False encoding.
- RED test added: test_asp_stable_single_extension_polynomial_on_minimal_support_blowup
  in test_aba_preprocessing.py (full asp path on 3**12 blow-up framework,
  expects witness = assumptions - {t}, preprocessing metadata present).
  RED CONFIRMED: timeout(60) fired, stack pinned at aba_asp.py encode ->
  _minimal_supports -> _add_minimal_support:153.
- FIX (next): aba_asp.py:436 -> encode_aba_theory(original,
  include_supports=backend not in {"asp", "clingo"}) mirroring line 146;
  aba_asp.py:486 -> include_supports=False. Answer-preserving: only the
  encoding facts payload/metadata label changes (core facts vs support facts)
  for simplified asp results.
- Metric consequence: first "fixed" run (226/94, named rows still TO) is
  PARTIAL — rename its files to *-fixed-simplifyonly, rerun fixed after
  commit 2, then compare + frontier.

## Encode fix DONE, GREEN, probe PASSED
- Fix applied (uncommitted yet): aba_asp.py `_solve_simplified` encode ->
  include_supports=backend not in {"asp","clingo"} (with comment);
  `_solve_simplified_ds_pr` encode -> include_supports=False (caller gates
  backend). RED->GREEN: 3 blowup tests pass in 0.36s.
- END-TO-END PROBE (scripts/probe_aba_sest_named_row.py, branch code, exact
  production entry solve_aba_single_extension backend=auto):
  aba_2000_0.1_5_5_1: solved 0.539s witness_size=152 solver=clingo_multishot
  preprocessing=grounded_reduct_aba
  aba_2000_0.1_5_5_6: solved 0.483s witness_size=152 same route.
- Gates: tests/solving+interop 291 passed 3 skipped (rerun after encode fix).
  tests/structured RUNNING in background -> logs-pytest-structured-fixed2.txt
  (a monitor task bu80ab2yp waits for the summary line).
- Partial fixed benchmark files RENAMED to
  iccma-2025-aba-simplify-fixed-simplifyonly.* (evidence of the two-stage
  discovery: simplify-only fix => named rows still TO 15s, 226/94).

## Remaining sequence (updated)
1. structured suite finishes -> commit 2 (aba_asp.py + new test + probe
   script; separate message citing second call site).
2. Rerun fixed benchmark (label aba-simplify-fixed) on branch. Poll.
3. compare baseline vs fixed (+ witness verification via compare script).
4. run_frontier_v1.py --subtrack SE-ST --root main-data --label ... on branch
   code, 120s (also needs --output-dir since worktree data/ absent; check).
5. Finalize experiment record (rewrite Single Variable section: ONE mechanism,
   two call sites of the same exponential primitive), write report, commit
   docs, SendMessage.

## FULL METRIC GATE PASSED (second fixed run, commit 23c6856)
- structured suite post-encode-fix: 1481 passed (1990s — much slower wall time
  than the 282s run earlier; likely environment; all green).
- Commit 2 = 23c6856 "Encode ABA support facts only for backends that consume
  them" (aba_asp.py 2 call sites + regression test + probe script).
- Fixed benchmark rerun (label aba-simplify-fixed, logs-run-fixed2.txt):
  241 solved / 79 timeout vs baseline 225/95. LOST=0, answer mismatches=0.
  Commonly-solved elapsed 348.71s -> 312.82s = -10.29% (FASTER).
  NAMED ROWS FLIPPED: aba_2000_0.1_5_5_1 timeout->solved 0.743s w=152;
  _6 timeout->solved 0.681s w=152.
  16 gained total (aba_2000_0.1_5_5_{1,3,6,9}, aba_5000_0.1_5_5_1,
  aba_500_0.3_5_5_3, aba_2000_0.3_10_10_9, + 9 abcgen_c5/... rows).
  Witness verification: 9/16 natively verified stable; 7 unverifiable =
  negative "no stable extension" (witness None), flagged like exp-4.
  abcgen c25/c35/c7 rows unchanged row-for-row (solved stay solved, TO stay TO).
  10 per-row >10% regressions, all sub-second rows with 0.05-0.25s absolute
  deltas (noise); aggregate strongly negative. Optional: spot-rerun top 3.
- Comparison log: logs-compare-simplify2.txt.

## Frontier run in flight
scripts/run_frontier_v1.py --subtrack SE-ST --timeout-seconds 120
--label frontier-v1-aba-simplify-23c6856 --root main data --output-dir main
runs dir (worktree lacks data/). 4 cells: 2 named (expect solved) + 2 abcgen
hard (expect 120s TO each). Output:
data/iccma/2025/runs/iccma-2025-frontier-v1-aba-simplify-23c6856-SE-ST.json,
log logs-frontier-sest.txt. Task b6nr51qyo.

## FINAL RESULTS — everything passed
- Frontier-v1 SE-ST (120s, label frontier-v1-aba-simplify-23c6856): 4 cells ->
  2 solved (BOTH named rows, w=152, reported as deviations from frozen hard
  expectation) + 2 timeout (abcgen hard cells, expected/out of scope).
- Spot reruns (label aba-simplify-spotcheck, quiet machine, fixed code):
  aba_100_0.3_5_10_0 0.226s (baseline 0.226 / contended 0.301);
  aba_500_0.1_5_5_3 0.315s (0.323/0.443); aba_500_0.3_5_5_2 0.297s
  (0.287/0.367) — regressions refuted as environmental.
- Experiment record FINALIZED (no placeholders): two call sites, one
  mechanism, promote decision, follow-ups (abcgen SCC map, remaining
  _minimal_supports consumers).
- reports/aba-simplify-budget-coder.md WRITTEN (preflight, design decision,
  TDD quotes, gates, metric tables, kill eval, honest notes incl. the
  "budget-not-implemented (a) instead" justification and the
  --max-af-arguments 1 disclosure, PROMOTE).

## Remaining
1. git add + commit docs: experiments/2026-07-08-aba-simplify-stable-budget.md,
   reports/aba-simplify-budget-coder.md, notes/aba-simplify-budget-coder-state.md.
2. Report commit hashes (8a934dc, 23c6856, docs) + SendMessage 5-line summary
   to "main".

## Blockers
None.
