# AF incremental-SAT substrate worker — state

Branch: exp/af-satsub-incremental (off main)
Hypothesis: persistent incremental SAT substrate for CDAS DS-PR eliminates the
~62s Python clause-construction bottleneck on crusti_175/225 DS-PR rows.

## Progress log
- [x] ward set experiment (confirmed: phase → experiment)
- [x] Read AGENTS.md top 166 lines
- [x] Read the two meta-scout notes (opportunity + scoreboard)
- [x] PRIOR-ART GATE committed: c844e1a. Clean prior. Probe 7 death does NOT
      apply (Z3 not IPASIR; AF not ABA; deaths were frozen-contract artifacts).
      Read mu-toksia pp.1-2 + Crustabri p.20 from page images.
- [x] PREREGISTER committed: 45d6cdc (experiment doc + probe driver).
- [x] TRIAGE PROBE DONE — **KILLS THE HYPOTHESIS**. See below.
- [ ] IMPLEMENT if probe survives
- [ ] dev slice + regression guard + full pytest
- [ ] RECORD + verdict

## Commits (all on exp/af-satsub-incremental; main untouched)
- c844e1a prior-art record
- 45d6cdc preregistration + probe driver
- c935627 NO-GO failure record + probe scripts  <-- FINAL. Experiment complete.

## FINAL VERDICT: NO-GO (clean triage kill). Cost model falsified by py-spy.
Skip-supercore confirmatory: 123.9s answer=NO (correct), still >t120 (no flip).
INDEX.md NOT touched (it is ABA-2023-campaign-scoped; no AF experiments indexed).
Recommend-only, no promotion, no self-merge.

## POST-EXPERIMENT: worktree isolation + de-entanglement (team-lead correction)
- My isolated worktree: C:/Users/Q/AppData/Local/Temp/claude/
  C--Users-Q-code-argumentation/e531f1d6-db52-4333-8cee-1726098fa014/scratchpad/af-satsub-wt
- Freed my branch by detaching shared-dir HEAD (no-op on files, same commit c935627).
- Rebased: git rebase --onto main 3d7fc24 exp/af-satsub-incremental. CLEAN
  (my files disjoint from census runner files). Dropped census commit 3d7fc24.
- NEW SHAs (post-rebase, only my 3 commits above main=f4b8eac):
  fe5c8bd prior-art / b5f719c preregistration+probe / 14f3e9a NO-GO record.
- Verified: diff main..HEAD = ONLY my 4 files; census files (iccma2025_run_native.py,
  test_iccma_runner_budgets.py) ABSENT. pyright my scripts = 0 errors.
- Experiment already complete; nothing further to resume.

## Current blocker / gotcha
- DRIVER BUG (fixing): cone routing in solver.py:421 only fires when
  requested_backend == "auto". My probe passed backend="sat" -> skipped cone,
  ran flat path on full 89k-arg/6.2M-attack graph -> >120s. FIX: backend="auto".
- py-spy 0.4.2 installed via `uv tool install py-spy`.
- crusti_175: query 38006, ref NO, 6.2M attacks (cone ~92k). crusti_125:
  query 1478, ref NO, 334k attacks (known-green flip).

## TRIAGE PROBE RESULT — CLEAN KILL (py-spy, real process, crusti_175 DS-PR)
Profile: scratchpad/crusti175-dspr.speedscope.json, 12851 samples @100Hz = 128.5s.
- **66.2% (85.0s) in Z3_solver_check_assumptions (SAT SEARCH)** — NOT construction.
- decide 76.7% -> compute (super-core) 67.1% -> _admissible_attacker_of_set 66.4%
  -> check -> Z3_solver_check_assumptions 66.2%.
- add_admissible_labelling (Python clause CONSTRUCTION): ~12-15s total, ONE build.
- parse 14.3s, cone extraction ~12s.
- Process KILLED still inside super-core; extension_problem + attacker_problem
  NEVER RAN. So "3 kernel builds ~62s" cost model on record is FALSE: the run
  dies in super-core SAT SEARCH before building kernels 2 & 3.
- The super-core ALREADY builds one encoding + reuses via push/pop -> already
  "incremental". Its cost is SEARCH, which a build-once substrate cannot touch.
- VERDICT: incremental-construction substrate hypothesis FALSIFIED. Clean kill.
- Next target NAMED BY EVIDENCE: the answer-preserving super-core precheck's
  SAT search (85s) on big cones — either SKIP it on big cones (2026-07-10
  follow-up), or cut its per-iteration search / iteration count. Separate
  hypothesis, needs own preregistration. Recommend-only.

## Architecture facts (af_sat.py)
- DS-PR CDAS (PreferredSkepticalTaskSolver.decide) builds 3-4 O(attacks)
  encodings: super-core admissible(~16s), extension complete(~14s), attacker
  DUAL admissible copies(~32s). ~62s total on crusti_175 cone.
- super-core precheck is answer-preserving (droppable on big cones).
- Paper-backed target: single complete-labelling encoding + Dvorak CEGAR
  (mu-toksia Sec 3.2) => ONE base build, blocking clauses + assumptions.

## Key facts on record
- crusti_g2io_175/225 DS-PR still TO after SCC-cone win; profile = Python-API
  clause construction (rebuilds 3 Z3 kernels ~62s), NOT SAT search.
- Probe 7 (CaDiCaL 2.2.1) death = IPASIR val()/statistic API capability on
  ABA eager-arc CNF — NOT the incremental-SAT idea for AF (per opportunity scout).
