# Wave-2 Promotion-Gate Verifier Report (2026-07-18)

Verifier actor. Default stance: NO-MERGE. Verdicts only; no merges. Holdout files are OFF-LIMITS.

Ward phase: `verifier` (set + verified). Main tip: `f4b8eac`.

## VERDICT SUMMARY
1. **exp/iccma-census-budgets** — **MERGE**. Instrumentation-only, byte-identical default dispatch (proven by full-job-dict equivalence test), 14/14 tests + pyright clean, manifest reproduces 52 rows byte-identically, record 40/52 headline + every per-family split match raw JSONs exactly. No blocking items.
2. **exp/af-flat-satcore** — **MERGE**. Diff scope matches claim (flat complete/preferred/cdas sat-core routing only; cone file unchanged; explicit-engine paths intact); 45 contracts pass; semi-stable/stage PbGe/PbEq exclusion real in code; my independent adversary pass = 6096 checks, 0 answer mismatches sat-core vs smt; disclosed full-suite non-passes confirmed pre-existing on baseline. One NON-BLOCKING caveat: t15 81->81 solve-count not independently reran (machine-contended); relying on committed record, correctness half independently corroborated.
3. **exp/abcgen-arc-acyc** — **MOOT / ALREADY LANDED**. Tip b90ebe0 is already an ancestor of main f4b8eac; fully merged; tests green on current main. No merge action exists or is needed. (Not NO-MERGE, not DEFER — already promoted.)

Integrator flags: (a) add `.gitattributes` eol normalization — CRLF churn confirmed real; (b) close exp/af-satcore-flat (3973193) as superseded when af-flat-satcore lands — confirmed by that branch's own record.

## Worktrees (reusing session scratchpad, e531f1d6)
- census-wt @ 5fd52fd = exp/iccma-census-budgets tip
- main-census-wt @ f4b8eac = main baseline
- af-flat-satcore-wt @ 9c52859 = exp/af-flat-satcore tip
- af-flat-satcore-baseline-wt @ f4b8eac = main baseline
- abcgen: branch tip b90ebe0 (need detached worktree; branch already checked out at .claude/worktrees/agent-a2a16e2a...)

Branch tips confirmed match prereg: census 5fd52fd ✓, af-flat-satcore 9c52859 ✓.

---

## 1. exp/iccma-census-budgets — VERDICT: **MERGE**

Commits: 3d7fc24, 7b36cbf, a816a75, 32290b5, 764a170, 5fd52fd. Instrumentation only. NO blocking items.
EVIDENCE:
- Production diff (tools/iccma2025_run_native.py) is instrumentation-only. Empty task_budgets => budget_for_task returns config.timeout_seconds for every row => dispatch byte-identical. Adds --budgets-json (default None), --only-track filter, load_task_budgets/budget_for_task helpers, profile_duration_seconds refactored to take budget_seconds (==timeout_seconds when no budgets). Read the whole diff — no solver-behavior change.
- test_empty_budgets_dispatch_is_byte_identical_to_flat_timeout asserts full job dict equality (flat_job == budget_job). Real equivalence test. PASS (14/14 in census-wt).
- pyright: 0 errors, 0 warnings on all 4 changed py files.
- Manifest reproduces EXACTLY: re-ran select_sample.py against source CSV (sha bbe3865... matches manifest source_csv_sha256), output entries/strata/selection all == committed sample-timeout-600s.json (52 entries, 22 strata). RNG-free deterministic confirmed.
- Record headline 40/52 solved (0.769) matches raw JSON aggregate EXACTLY: independently aggregated data/iccma/2025/runs/iccma-2025-census-600s-*.json => 40 solved / 12 timeout / 0 other / 52 total. Per-family all match: ER 4/13, scc 9/12, crusti 14/14, mainkwt 3/3, abcgen 6/6, aba 4/4.
- INDEX.md addition appended cleanly, correctly cross-references the record, labeled "not part of this campaign or its budget". Consistent.
- No holdout opened.

## 2. exp/af-flat-satcore — VERDICT: **MERGE** (one non-correctness caveat, non-blocking)

Commits: 473ef4d, 6265fca, dd778ff, 9c52859. Solver routing.
FINDINGS SO FAR:
- CRLF confirmed: base f4b8eac solver.py has MIXED CRLF+LF terminators; tip 9c52859 is pure CRLF. Branch normalized file to CRLF -> full diff 110/77 inflated; --ignore-all-space=51/18, --ignore-cr-at-eol=55/22. Meaningful (token) diff is complete under --ignore-all-space (any token change survives it). => INTEGRATOR FLAG: add .gitattributes eol normalization.
- Production changes (solver.py, af_sat.py) route FLAT AF SAT ops to sat-core engine:
  * _flat_sat_engine(kind, fw): complete/preferred_witness -> "sat-core" unconditional; cdas_skeptical -> "sat-core" iff len(fw.defeats) >= PREFERRED_CONE_MIN_DEFEATS else "smt"; ALL ELSE (stable, ideal, semi-stable, stage) -> "smt".
  * Applied at: solve_dung_single_extension (complete/preferred only), _solve_sat_complete_acceptance, _solve_sat_preferred_credulous_acceptance, _solve_sat_preferred_skeptical_acceptance(cdas).
  * _solve_sat_acceptance refactored to collect kwargs into `shared` dict, forwards engine ONLY if not None -> semi-stable/stage finders (no engine param) unaffected. Semantically identical.
  * af_sat.py: adds engine field to SATCheck telemetry + engine param to find_preferred_extension (default "smt") + kernel .engine attr. Additive.
- Cone path: solver.py only ADDS import of PREFERRED_CONE_MIN_DEFEATS; solve_cone_acceptance body unchanged. TBD confirm byte-identical.
VERIFIED:
- PREFERRED_CONE_MIN_DEFEATS = 15_000 (af_scc_cone.py:57). Matches "defeats>=15000 gate". Reused, not redefined.
- af_scc_cone.py body UNCHANGED (only new import in solver.py). Cone path byte-identical.
- Semi-stable/stage exclusion REAL IN CODE: _solve_sat_semi_stable_acceptance / _solve_sat_stage_acceptance call _solve_sat_acceptance WITHOUT engine -> stays None -> not forwarded; and find_semi_stable_extension/find_stage_extension signatures have NO engine param (would TypeError if forwarded). Belt+suspenders.
- Contracts: 45 passed (tests/solving/test_af_satcore_flat_routing.py) — matches claimed 45. Includes answer-equivalence-vs-native + telemetry-observable-engine contracts.
- ADVERSARY PASS (my own, independent): 400 random small AFs (n=1..7), complete+preferred x credulous+skeptical, engine=sat-core vs engine=smt directly. 6096 acceptance checks, 0 mismatches. Engine swap answer-equivalent. Threshold routing is perf-only (both engines answer-identical) so 15000 gate carries no answer risk.
- Full-suite gate spot-check: record claims 3136 passed / 1 failed / 4 skipped / 1 xfailed. The 1 fail (test_decomposed_prefsat_page_image_contract, paper page image) + Probe 7 collection error (test_aba_cadical2_eager_arc_contract.py -> absent scripts.probe_iccma2023_cadical221_eager_arc) are BOTH outside the diff and DISCLOSED. CONFIRMED pre-existing: reproduced the Probe 7 collection error on BASELINE f4b8eac (not branch-introduced). Both unrelated to flat AF sat routing.
- tests/solving/ reran clean in worktree: 304 passed, 3 skipped. No regression in the routed area.
CAVEAT (non-blocking, non-correctness): t15 DS-PR 81->81 zero-loss is a benchmark solve-count measurement; NOT independently rerun (machine owned by census-worker; wall-clock-sensitive => blocked per etiquette). Relying on committed record (baseline 81 / after 81 / 0 lost / 0 answer changes / -4% time; only 2/81 rows cross the 15000 threshold). Correctness half (0 answer changes) is independently corroborated by my 6096-check adversary equivalence. Recommend integrator or a post-census rerun re-confirm the solve-count before final landing if desired, but this is coverage not correctness.

BLOCKING ITEMS: none. MERGE.

## 3. exp/abcgen-arc-acyc — VERDICT: **MOOT / ALREADY LANDED** (no merge action; NOT a NO-MERGE, NOT a DEFER)

Tip b90ebe0. KEY FINDING: **b90ebe0 IS ALREADY AN ANCESTOR OF main f4b8eac** (position 84 in main history; `git rev-list b90ebe0 ^f4b8eac --count` = 0). The whole experiment (commits b446dfb derive, 08e19cd eager SCC-local arc acyclicity, 9ca0b56 block static intra-SCC cycles, b90ebe0 record) is fully merged. The "stalled recommend-promotion" was already promoted. There is nothing to merge.
EVIDENCE IT'S LIVE + GREEN:
- Production change src/argumentation/structured/aba/aba_sat.py (+369/-95) present on main; tests/structured/aba/test_aba_stable_arc_acyclic.py present on main.
- Ran that test on current main f4b8eac (main-census-wt): 3 passed. Evidence holds.
- rebase-ability: N/A (already in main, no conflicts possible).
c35 KNOWN OPEN ISSUE — status: the abcgen record's residual c35 giant-SCC wall (~591.6s glucose4; task said 522s) is being addressed by a SEPARATE in-flight lane exp/aba-c35-lane (record experiments/2026-07-17-aba-c35-cadical-engine.md, NOT on main). That experiment's triage = **GO**: CaDiCaL 2.2.1 solves the byte-identical eager-arc c35 SE-ST DIMACS in 25.28s (asms30) / 9.19s (asms35), models independently verified, vs glucose4 >590-650s. So the wall is directionally resolved but via a distinct, not-yet-promoted experiment. NOT a gate on branch 3 (already landed).

---

## Integrator flags

1. **CRLF / .gitattributes (CONFIRMED real).** Base f4b8eac `src/argumentation/solving/solver.py` blob has MIXED CRLF+LF line terminators; branch tip 9c52859 normalized it to pure CRLF. This inflated the af-flat-satcore solver.py diff from 51/18 (meaningful) to 110/77. `git diff --ignore-all-space` still surfaces every token change, so review was unaffected, but future diffs will keep churning. RECOMMEND: add a `.gitattributes` with `*.py text eol=lf` (or `* text=auto`) and a one-time `git add --renormalize .` commit on main so line endings stop polluting diffs. (Verifier used --ignore-all-space per instructions; whitespace-only lines confirmed whitespace-only because --ignore-all-space collapses only lines with no token difference.)

2. **exp/af-satcore-flat (3973193) → close as SUPERSEDED (CONFIRMED).** 3973193 is NOT in main; it is a stalled "Decision: TO BE FILLED" probe-only experiment ("Probe smt vs sat-core on flat AF paths; derive routing before code"). The af-flat-satcore record (experiments/2026-07-17-af-flat-satcore.md) explicitly states it "**Supersedes exp/af-satcore-flat (3973193)** ... That branch's record should be marked superseded by this one." At promotion time of af-flat-satcore, close 3973193 as superseded. Confirmed correct.

## Integrator flags
- CRLF issue (.gitattributes) — TBD
- exp/af-satcore-flat (3973193) superseded? — TBD
