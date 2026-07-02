# Coder state: exp/af-z3-check-budget (checkpoint 1)

## Setup done
- Worktree: C:\Users\Q\code\argumentation\.claude\worktrees\agent-a01064970c3da35af
- Branch `exp/af-z3-check-budget` created off main at 93d2897 (verified). `ward set experiment-worker` succeeded.

## What I know (verified by reading)
- `SATConfig` (src/argumentation/solving/solver.py:79-84): fields require_external, trace_sink, metadata. No budget. `_sat_trace` (solver.py:582) unpacks it; call sites solver.py:348 (single-extension sat branch), :395 (acceptance sat branch).
- AF SAT kernel: `AfSatKernel.__init__` creates `z3.Solver()` at af_sat.py:110; central `check()` at af_sat.py:309-347 returns `str(result)`; every caller collapses `!= "sat"` to negative (af_sat.py:443, :662, :989-996, :1050-1055, :1072).
- Sub-solvers with own z3.Solver(): `explain_stable_unsat` (af_sat.py:490, diagnostic, already records "unknown" honestly at :559); `_PreferredSkepticalAttackerSolver` (af_sat.py:1092, `.check()` at :1117, unknown collapses to "no attacker" => accepted=True — must raise).
- Kernel constructions to thread budget through: find_stable/complete/preferred/semi_stable/stage/ideal (af_sat.py:439, :596, :621, :868, :900, :930), PreferredSkepticalTaskSolver.decide (:738), PreferredSuperCoreSolver.compute (:834), _PreferredSkepticalAttackerSolver (:752), is_preferred_skeptically_accepted (:692).
- solver.py acceptance wrappers: _solve_sat_acceptance (:789) mints answer from witness None-ness — timeout must be raised past it, caught in solve_dung_acceptance/solve_dung_single_extension sat branches, returned as SolverTimeout (core/solver_results.py:58, dataclass NOT exception; aliased SolverBackendTimeout solver.py:67; already member of result unions :92-112).
- `sat_extensions` (solving/sat_encoding.py) does NOT use z3 — native enumeration. No budget needed there. solve_dung_extensions sat branch unaffected.
- Harness: tools/iccma2025_run_native.py — job carries `solver_timeout_seconds` (:397 = config.timeout_seconds). Clingo derivation convention: `max(0.1, float(job["solver_timeout_seconds"]) - 1.0)` at :960-963 (ABA SE branch). solve_af_job builds SATConfig(trace_sink, metadata) at :805-813 — no budget. solve_af_job SE (:822-833) and acceptance (:846-854) branches DO NOT handle SolverBackendTimeout (would hit `raise TypeError`); ABA SE branch :983-995 has the timeout->row mapping pattern to copy ({"status":"timeout", reason, ...} + with_solver_metadata).
- ABA exception pattern: ClingoSolveTimeout(TimeoutError) aba_incremental.py:91 -> caught -> status="timeout".
- run_child maps worker stdout JSON straight to row; {"status":"timeout"} = clean timeout row.

## Plan
1. af_sat.py: add `AfSatCheckTimeout(TimeoutError)` exception (carries utility_name); `_apply_check_budget(z3, solver, seconds)` helper setting solver.set("timeout", ms); `check_budget_seconds` kwarg on AfSatKernel, all finders, PreferredSkepticalTaskSolver, PreferredSuperCoreSolver, _PreferredSkepticalAttackerSolver, is_preferred_skeptically_accepted, explain_stable_unsat (budget only; keeps honest "unknown" status). AfSatKernel.check + find_attacker: result not in {sat, unsat} -> emit trace then raise.
2. solver.py: SATConfig.check_budget_seconds: float|None=None; _sat_trace returns triple; sat branches pass budget + catch AfSatCheckTimeout -> SolverTimeout(backend="sat", problem=..., message=..., metadata=...).
3. tools/iccma2025_run_native.py: solve_af_job derives `max(0.1, solver_timeout_seconds - 1.0)` into SATConfig.check_budget_seconds; add SolverBackendTimeout handling in both AF branches (copy ABA pattern).
4. Tests (TDD, new tests/solving/test_af_sat_check_budget.py + harness test near existing interop timeout tests):
   (a) budget seconds->ms reaches solver params (fake solver records .set) + SATConfig plumb via monkeypatched finder table;
   (b) forced-unknown via solver.set("rlimit", tiny) on cyclic AF -> raises AfSatCheckTimeout, not None/False; find_attacker variant too;
   (c) solve_af_job maps SolverBackendTimeout -> {"status": "timeout"} row (monkeypatch solve_dung_acceptance).
5. Gates: uv run pytest tests/solving; tests/interop iccma selector; then metric gate DS-PR benchmark (background) + 3 hard rows.

## Checkpoint 2 (RED done, GREEN in progress)
- Probe (scripts/probe_z3_rlimit_unknown.py, uncommitted): z3 4.16.0 installed; `solver.set("rlimit", 10)` on 60-node cyclic AF returns `unknown` deterministically (5/5 trials); `timeout` param accepted in ms; the probe instance solves in <1ms unlimited => wall-clock forcing would be flaky, rlimit is right.
- RED confirmed: tests/solving/test_af_sat_check_budget.py fails on ImportError (AfSatCheckTimeout missing); tests/interop/test_iccma_af_sat_budget.py 3 failures (budget kwarg missing; solve_af_job raises TypeError on SolverTimeout at tools/iccma2025_run_native.py:833).
- Harness test pattern copied from tests/interop/test_iccma_runner.py:476 (monkeypatch parse_* + solver fns, call solve_af_job directly).
- worker_solve (iccma2025_run_native.py:696-708) catches BaseException => timeout mapping MUST live inside solve_af_job, not rely on the exception escaping.
- GREEN edits so far in af_sat.py: AfSatCheckTimeout(TimeoutError) + _apply_check_budget added above SATCheck; AfSatKernel.__init__ takes check_budget_seconds, applies to solver; AfSatKernel.check raises AfSatCheckTimeout on non-sat/unsat AFTER emitting trace.
- Remaining GREEN: finders + is_preferred_skeptically_accepted + PreferredSkepticalTaskSolver + PreferredSuperCoreSolver + _PreferredSkepticalAttackerSolver (raise in find_attacker) + explain_stable_unsat budget; __all__ export; solver.py SATConfig.check_budget_seconds + _sat_options triple + try/except AfSatCheckTimeout -> SolverTimeout(backend="sat", problem=f"AF-{semantics}", metadata w/ utility_name+budget) in single-extension and all acceptance sat branches; harness solve_af_job budget=max(0.1, t-1.0) + SolverBackendTimeout row mapping in SE and acceptance ladders (copy ABA :983-995).
- Then: full gates (uv run pytest tests/solving; tests/interop -k iccma), commit, metric gate runs.

## Checkpoint 3 (GREEN, af_sat.py nearly done)
af_sat.py edits completed so far:
- AfSatCheckTimeout + _apply_check_budget added; AfSatKernel stores/applies budget; check() raises on non-sat/unsat after trace.
- check_budget_seconds threaded through: find_stable_extension, explain_stable_unsat (budget applied to standalone solver; unknown stays status="unknown" — diagnostic, honest), find_complete_extension, find_preferred_extension, is_preferred_skeptically_accepted -> PreferredSkepticalTaskSolver (stores + passes to super-core/kernel/attacker solver), PreferredSuperCoreSolver, find_semi_stable_extension, find_ideal_extension (incl. recursive call), find_stage_extension, _PreferredSkepticalAttackerSolver (stores + applies to its solver).
Remaining in af_sat.py:
- find_attacker: raise AfSatCheckTimeout when result not in {sat, unsat} (after trace emit).
- Export AfSatCheckTimeout in __all__.
Then solver.py + harness edits per checkpoint 2 plan; run tests.

## Checkpoint 4 (GREEN edits nearly complete)
- af_sat.py DONE: exception + budget helper + kernel/finders/sub-solvers threaded; find_attacker raises on unknown; AfSatCheckTimeout exported in __all__.
- solver.py DONE: SATConfig.check_budget_seconds (documented); _sat_trace renamed _sat_options (returns triple); _sat_check_timeout helper -> SolverBackendTimeout(problem=f"AF-{semantics}", metadata utility_name+budget); single-extension sat branch passes budget + catches AfSatCheckTimeout; acceptance sat branch REFACTORED: six duplicate try/except blocks collapsed into _dedicated_sat_acceptance_solver(semantics, task) + _SAT_ACCEPTANCE_SOLVERS table; all acceptance helpers now share uniform (framework, task, query, *, trace_sink, metadata, check_budget_seconds) signature (preferred helpers `del task`). Fallback _solve_dung_acceptance_from_extensions kept OUTSIDE try (bit-identical error behavior for non-dedicated semantics).
- tools/iccma2025_run_native.py: solve_af_job imports SolverBackendTimeout; SATConfig now gets check_budget_seconds=max(0.1, solver_timeout_seconds - 1.0) (cited ABA clingo convention in comment); added solver_timeout_row(result) helper next to unavailable_result.
- REMAINING: wire solver_timeout_row into solve_af_job SE + acceptance ladders (isinstance SolverBackendTimeout branches); optionally refactor ABA SE inline timeout dict to use the helper; then run new tests, tests/solving, tests/interop iccma, full suite; commit; metric gates.

## Checkpoint 5 (GREEN complete, gates in progress)
- All GREEN edits done: af_sat.py, solver.py, tools/iccma2025_run_native.py (solve_af_job SE + acceptance ladders now map SolverBackendTimeout -> solver_timeout_row; ABA SE inline dict refactored to same helper).
- New tests: 18/18 pass (tests/solving/test_af_sat_check_budget.py 15, tests/interop/test_iccma_af_sat_budget.py 3).
- Gate: uv run pytest tests/solving -> 219 passed, 3 skipped (all 3 pre-existing env-conditional: ICCMA_AF_SOLVER / ASPFORABA_SOLVER / ICCMA-2017-data; none mine).
- Gate: uv run pytest tests/interop -> 57 passed.
- Full suite running in background (task bmeiyx998, log logs-af-z3budget-fullsuite.log in worktree).
- Metric gate recon: runner writes to <root>/runs/<contest>-<label>.{json,csv,-summary.json}; root will be main repo data/iccma/2025 which is GITIGNORED (.gitignore:7 "data/") — writing new-label artifacts there is sanctioned by the prompt and not a tracked-tree touch. Baseline artifacts present: iccma-2025-af-dspr-cdas-variantB.{json,csv,summary}; hard rows source: iccma-2025-timeout-recal-60s-20260701-DS-PR.json.
- Bench must run FROM the worktree so workers import modified code (worker command = sys.executable tools/iccma2025_run_native.py from worktree).
- Next: wait full suite; commit (2 logical commits: solving layer; harness+interop); then DS-PR t15 bench label af-z3budget-dspr-t15 (background, chunked); pick 3 timeout rows from 60s recal DS-PR json; run --only-instance with t15 label af-z3budget-hardrows-t15; write experiment record + report.

## Checkpoint 6 (waiting on full suite)
- Hard rows chosen from iccma-2025-timeout-recal-60s-20260701-DS-PR.json (6 distinct timeout instances): AFs/ER_300_20_2.af (301 args), AFs/ER_400_60_3.af (401), AFs/ER_500_10_10.af (501). Note: 401/501 exceed --max-af-arguments 320 cap (run_or_skip skips at :360-372), so hard-rows run will use --max-af-arguments 600, cited in record.
- Full suite (background task bmeiyx998, `uv run pytest -q -x`) at 95% for ~15 min, python processes alive — a known-slow tail test (repo has prior full-suite logs; sensitivity proptests are slow). No failures so far (-x would have stopped). Log: worktree logs-af-z3budget-fullsuite.log.
- run_or_skip cap logic confirmed: af cap by argument_count > max_af_arguments -> status=skipped.
- Everything else GREEN per checkpoint 5.

## Checkpoint 7 (full-suite stall diagnosed and handled)
- First full-suite run (bmeiyx998) stalled 30+ min at ~test 2851: py-spy dump (PID 202920) showed hypothesis property test tests/structured/aspic/test_aspic.py::test_defeat_is_directed (deadline=None) actively computing in aspic compute_defeats/build_arguments — PRE-EXISTING pathology (exponential argument build on unlucky draws + cold .hypothesis cache in fresh worktree), zero relation to my change (no aspic code touched). Prior main full-suite logs finish in ~4:36 with warm cache.
- Action: killed my own pytest PIDs 202920/208620; copied main repo .hypothesis cache into worktree (read from main only); rerunning full suite in background task be6wms2xq -> logs-af-z3budget-fullsuite2.log.
- 2851 tests had already passed under -x before the stall (no failures).
- Next after suite passes: commits, then metric-gate benches (DS-PR t15 label af-z3budget-dspr-t15 with --max-af-arguments 320; hard rows ER_300_20_2/ER_400_60_3/ER_500_10_10 with --max-af-arguments 600, label af-z3budget-hardrows-t15), experiment record + report.

## Checkpoint 8 (commits made; aspic proptest still grinding)
- Commits: 4d2278f (af_sat.py + solver.py + tests/solving/test_af_sat_check_budget.py), 105b518 (tools/iccma2025_run_native.py + tests/interop/test_iccma_af_sat_budget.py).
- lint-imports: Contracts 2 kept, 0 broken.
- Full-suite rerun (be6wms2xq, warm .hypothesis cache) progressed past prior stall region but is now stuck 15+ min INSIDE tests/structured/aspic/test_aspic.py::test_target_sub_in_sub_of_target — active+gil in aspic compute_attacks/__hash__ (exponential example; deadline=None). DIFFERENT aspic test than run 1 (test_defeat_is_directed) => not deterministic-stuck, just pathological slow generation; entirely outside my diff (aspic untouched).
- Plan if it doesn't finish soon: let it keep running in background; separately run full suite with --ignore=tests/structured/aspic PLUS a dedicated tests/structured/aspic run to compose full coverage; benchmarks must NOT run concurrently with CPU-hungry suite (timing gate +5%), so sequence carefully: bench first (suite done or killed), or wait.
- Decision now: give it one more wait cycle; if unfinished, kill it, run suite-minus-aspic (fast) + aspic-dir-only run in background overnight-style while doing benches ONLY after the fast part completes and aspic run is the sole background load? NO — benches also compete with aspic run. Will kill aspic-containing run, run suite-minus-aspic to completion, then run benches with machine idle, then run tests/structured/aspic alone at the very end and quote result.

## Checkpoint 9 (metric gates measured)
- METRIC GATE 1 PASS: DS-PR t15 cap320 (label af-z3budget-dspr-t15, artifacts in main data/iccma/2025/runs): baseline variantB vs candidate — 964/964 rows, statuses identical (709 skipped/235 solved/20 timeout), solved 235=235 (0 lost, 0 gained), 0 answer mismatches, commonly-solved elapsed 605.23s -> 611.04s = +0.96% (within +5%). Comparison via scripts/compare_af_z3budget_runs.py. NOTE: run was concurrent with the single-threaded stuck aspic pytest (1 of 32 cores) — noted in record.
- In-process budget demonstrated IN THE SLICE: 4 of 20 timeout rows have reason "Z3 returned unknown on AF SAT check 'preferred_super_core_admissible_attacker' (check budget 14.0s)" — instances AFs/WS_300_32_30_70.af and AFs/WS_300_32_90_70.af (both tracks each). Other 16 rows end by outer kill (multi-check CDAS loops where no single check exceeds 14s — inherent to a per-check budget).
- Hard-rows run 1 (ER_300_20_2/ER_400_60_3/ER_500_10_10, label af-z3budget-hardrows-t15, cap 600): all 6 rows outer-kill (timeout>15.0) — these rows are many-short-check loops; plumbing "applies" per check. Will REDO the hardrows label with 3 rows incl. WS_300 instances? WS_300 not in recal-60s timeout set? Prompt requires rows from recal-60s DS-PR timeouts. WS_300 rows: check whether they appear as timeouts in recal-60s json — they were not in the 6 distinct (ER_300_20_2, ER_400_60_3, ER_500_10_10, crusti 125/175/225). crusti_g2io_125 (3875 args) may single-check-timeout. Plan: run crusti_g2io_125_0.5_31_17.af (+ keep ER rows) with cap high under a new label to show in-process rows sourced from the recal set; keep both artifacts and quote honestly.
- Full suite (be6wms2xq) STILL inside aspic proptest test_target_sub_in_sub_of_target (40+ min, active). Pre-existing; not my diff.

## Checkpoint 10 (record written; gates nearly all in)
- Hard-rows rerun (crusti_125, crusti_225, ER_300_20_2; cap 30000; label af-z3budget-hardrows-t15): all 6 rows clean status=timeout but by OUTER kill — ER = many sub-14s checks; crusti = 15s consumed by Python-side parse/encode before a long check. Honest finding; the per-check budget by design bounds only Z3 check time.
- In-process demonstration evidence (slice): WS_300_32_30_70/WS_300_32_90_70 rows end at ~14.83s with reason "Z3 returned unknown on AF SAT check 'preferred_super_core_admissible_attacker' (check budget 14.0s)" + solver_metadata{check_budget_seconds:14.0, utility_name}; sat_check events elapsed_ms≈14010-14016, result=unknown. Baseline same rows: reason timeout>15.0 at 15.01s.
- experiments/2026-07-02-af-z3-check-budget.md written with verified file:line citations (grep-checked; sed+Edit fixed).
- Suite-minus-aspic running (task bltd9p2xh -> logs-af-z3budget-suite-minus-aspic.log); aspic-included run (be6wms2xq) still grinding same proptest (~80+ min, pre-existing).
- Remaining: suite-minus-aspic result; commit record+notes+compare script; write reports/af-z3-check-budget-coder.md; SendMessage summary to main.

## Current blocker
Waiting on suite-minus-aspic run.
