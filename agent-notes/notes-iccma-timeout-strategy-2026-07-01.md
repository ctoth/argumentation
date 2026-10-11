# ICCMA timeout strategy session — 2026-07-01

## Goal
Figure out current ICCMA timeouts across prior runs, then strategize fixes using
./papers and existing notes. Go wide and deep. Now under FOREMAN protocol:
drive pass rate upward on master, pushing as we go.

## Observed so far (first-hand)
- Branch: `exp/iccma-aba-dcco-100ba-acyc`. Latest commit 58b13df records the
  routing-shape discovery result in
  `experiments/2026-07-01-aba-dcco-routing-shape-result.md`.
- Freshest run: `data/iccma/2025/runs/iccma-2025-100ba-acyc-dcco-routing-shape-summary.json`
  — ABA DC-CO, 20 rows, 30s cap: 16 solved / 4 timeout. Timeouts all in
  `aba_2000_{0.1,0.3}_10_{5,10}_*` family.
- Discovered predicate `assumption_dependency_max_scc_size >= 56` has
  unsafe_recall 1.0 but 5 false-unsafe rows → NOT promoted. Recorded decision:
  do not resume blind 964-row pass; need better features (query-SCC membership,
  query→assumption reachability in big SCC, capped backend preflight).
- Repo has 383 ICCMA data files under data/iccma/<year>/{runs,manifests,extracted}.
  papers/ has 66 paper dirs with notes.md.

## notes-scout key findings (condensed)
- Benchmark trajectory: cap150 16->12 TO; cap200 49->7 after ABA kernel.
  cap-N = SIZE cap, not time. Real ICCMA budget is 1200s; several past
  "bottlenecks" were phantoms of mis-calibrated 30s gates (esp. the
  700-assumption SE-ST row: 104s native, fine — 28 experiments reverted;
  see notes/aba-completion-sat-bottleneck-2026-05-20.md).
- OPEN bottleneck 1: AF DS-PR (also DS-SST/SE-SST at cap200, "Phase 4"
  unstarted). Diagnosed: weak blocking lemma in af_sat.py
  PreferredSkepticalTaskSolver.learn_witness_region; SCC decomposition +
  grounded-reduct preprocessing EXIST but NOT wired. Fixes never executed
  (notes/ds-pr-timeouts-2026-05-02.md).
- OPEN bottleneck 2: ABA DC-CO large/uncapped (current branch campaign).
  Root causes: support materialization (92.7% in _add_minimal_support,
  aba_support_model.py) then clingo search blow-up on aba_2000_0.3 rows.
  External KR2025 100ba-acyc solver SOLVES the hard class (hard row 10.45s)
  and is wired as bench backend (--backend 100ba-acyc, WSL). Native acyc
  ports: lazy-CNF NO-GO; IPASIR-UP propagator correct but ~4x too slow
  (Python callback overhead). Routing predicate not promoted (5 false-unsafe).
- Unexecuted queue: workstreams/aba-next-optimization-possibilities.md
  (16 items w/ paper anchors); cap200 Phases 2-5; aba-shape-portfolio;
  ds-pr fix hypotheses.
- aba_2000_0.3_10_10_4 DC-CO answer is YES (earlier "false query" label wrong).
- Full-corpus runs from this env are fragile (2026-05-13 runs externally
  killed; never root-caused).

## papers-scout key findings (condensed)
- 66 paper dirs, ~20 performance-relevant; 6 technique families. Full
  inventory: scratchpad/speedup-inventory-checkpoint.md.
- Top-5 actionable: (1) incremental-SAT substrate (Fudge/CEGARTIX pattern);
  (2) CEGAR loops for 2nd-level tasks (Dvorak 2014 CEGARTIX); (3) CDAS/CDIS
  admissibility-only DS-PR + SE-ID (Thimm 2021 — direct hit on open AF DS-PR
  bottleneck); (4) Cerutti C_2 complete-labelling CNF + Pu range-vector for
  SST/STG; (5) Lehtonen direct ASP over defeasible elements for ABA.
- Cheap safe preprocessing: connected-component decomposition; Oikarinen
  kernels only help when self-loops exist.
- GAPS to fetch: mu-toksia system paper (top priority), ICCMA 23/25 system
  descriptions, SETAF solving, portfolio/algorithm-selection literature.

## runs-analyst key findings (condensed)
- TRUTH RUN: data/iccma/2025/runs/iccma-2025-full-uncapped-auto-t5-2026-05-14
  .json — uncapped, ~15s budget: 4,243 solved / 1,871 TIMEOUT (~30% of 6,114
  executed) / 1,280 skipped. AF = 1,722 TO vs ABA = 149 TO.
  => ABA DC-CO branch attacks ~8% of timeout mass; AF is the elephant.
- Worst AF families: crusti_g2io >=125 args 100% TO (40/40 all tasks);
  scc_1554 (28 TO DC-CO); ER_300 (34 TO DS-SST, 30 DS-PR); mainkwt_250
  (34 TO DS-PR). Worst tasks: DS-PR 43%, SE-ID/DC-ID 35%, DS-SST/SE-SST 34%,
  SE-PR 29%, DC-CO 28%.
- ABA offenders: abcgen ~54% TO on SE-PR/SE-ST; aba_2000 SE-PR 24/SE-ST 13.
- 2017/2019 essentially solved at cap100-150. Large-AF families untouched.
- Budget caveat: our 12-30s vs ICCMA ~600s; reference solvers fail ~12% AF
  main at 600s. Part of our 30% is budget artifact.
- Anomalies: 2015 & 2021 NEVER executed (queries not wired).
- Scripts: scratchpad agg.py, drill.py, official.py, runs_index.txt.

## arch-scout key findings (condensed)
- Harness: tools/iccma2025_run_native.py, fork-per-instance, wall-clock kill;
  Z3 in-process checks have NO timeout. Competition budgets in task-matrix
  metadata NEVER applied; one flat --timeout-seconds.
- Dispatch: solving/solver.py. Z3-only SAT backend. DS-PR = CEGAR
  PreferredSkepticalTaskSolver af_sat.py:669/699. EE-CO/PR/ST = brute 2^n per
  SCC, budget 65,536 => SCC>16 args raises ExactEnumerationExceeded.
- ABA routing: _auto_aba_backend_for_framework solver.py:551; predicates in
  aba_route_policy.py; _is_large_dense_flat_aba duplicated solver.py:586.
  Mid-size ABA falls onto exponential Z3 support path
  (aba_support_model.py:234 Cartesian blow-up).
- aba_acyc_sat.py NOT wired into auto routing (external --backend 100ba-acyc
  only). SETAF: uncapped 2^n brute force (setaf.py). Symmetric-AF poly case +
  kernels detected but unused (preprocessing.py:29-37,92); SCC-recursive
  DC/DS query pruning deferred (scc_recursive.py:41).
- Resumable sub-scouts: harness a1e2a6e827e56a469, ABA a4104db20675861ea,
  AF/SETAF ae1d43927a7c68405.

## z3-scout report (full text at notes-af-z3-timeout-scout.md)
- NO Z3 Solver/Optimize sets timeout or rlimit anywhere; only outer
  subprocess wall-clock + clingo async budget (aba_incremental.py).
- SATConfig (solver.py:82-88) has no time-budget field; af_sat.py:425 API
  takes no timeout; worker builds bare SATConfig() (iccma2025_run_native.py:837).
- CORRECTNESS HAZARD: every SAT acceptance caller collapses `unknown` into
  the negative answer (af_sat.py:443; solver.py:833-853 => credulous=False /
  skeptical=True SILENTLY). A Z3 timeout would be a silent wrong answer.
- Failover patterns to imitate: dynamics/optimization.py:134-138
  (unknown vs unsat distinguished); aba_incremental.py:91/419 + aba_asp.py:
  309/346 raise TimeoutError subclass -> status="timeout"; SolverTimeout
  exists at core/solver_results.py:58.
- Could not verify installed z3 version (Bash blocked); pyproject pins
  z3-solver>=4.12 (pyproject.toml:54,147).

## SYNTHESIS — ranked strategy (2026-07-01)
Reframe: AF is the elephant (1,722 of 1,871 uncapped TOs). Our 15s budget vs
ICCMA 600-1200s means part of the 30% is budget artifact (phantom trap).
0. RECALIBRATE FIRST: 60/120s sample of timeout rows (in flight).
1. AF DS-PR + SE-ID/DC-ID via CDAS/CDIS (Thimm 2021): replaces
   diagnosed-weak blocking lemma; attacks 43%+35%-rate tasks; wire existing
   grounded-reduct+SCC preprocessing into DS-PR path.
2. Z3 per-check timeout + failover (cheap; also fixes silent-wrong-answer
   hazard found by z3-scout).
3. AF SST/STG: Pu 2017 range-vector + CEGARTIX loops.
4. ABA mid-size: lower/lazy support-completion gate (aba_support_model.py:234).
5. ABA DC-CO acyc: promote external 100ba-acyc via capped-preflight routing,
   or C++ propagator port.
6. EE: query-driven SCC pruning (scc_recursive.py:41).
7. SETAF: candidate cap now; SAT encoding later.
8. Fetch mu-toksia + ICCMA system-description papers.
Also: 2015/2021 tracks never executed — coverage gap.

## FOREMAN CAMPAIGN (activated 2026-07-01, ward set foreman)
Metric plan:
- Frontier metric: pass rate on frozen stratified timeout-row manifest at
  t60 (freeze AFTER recal report).
- Regression guard: cap200-class selection at t15 must not regress.
- Baselines on master.

Queue: 1 CDAS/CDIS DS-PR -> 2 Z3 timeout -> 3 SST/STG -> 4 ABA support gate
-> 5 acyc promotion -> 6 EE SCC pruning -> 7 SETAF cap -> 8 papers fetch.

Dispatch log:
- [in flight] recal-runner: 60s/120s recalibration sample (30 rows, 6
  subtrack batches, labels timeout-recal-{60,120}s-20260701). Spawned
  PRE-ward, so unaffected by hook.
- [done] z3-scout -> notes-af-z3-timeout-scout.md (see above). Now probing
  ward phases for me.
- [in flight] dspr-scout -> reports/af-dspr-cdas-scout.md (fallback
  notes-af-dspr-cdas-scout.md if ward blocks reports/).

## WARD ISSUE (open, may need Q)
`ward set foreman` state appears SHARED with subagents: z3-scout (spawned
post-ward) was denied Write to reports/ and denied Bash, with the foreman
denial message. Subagent protocol says experiment workers run
`ward set experiment-worker` themselves => phases are worker-switchable.
Probing via z3-scout (ward help/list/status, ward set scout). If workers
cannot self-set phases, scout/coder dispatch is crippled and Q must adjust
the hook. Foreman itself: Bash fully blocked except (previously) `ward set`.

## Next step
1. Read z3-scout's ward probe results; establish worker unblock mechanism.
2. When recal-runner reports: freeze frontier manifest + dispatch master
   baseline worker.
3. When dspr-scout reports: verify vs plan, dispatch CDAS coder on
   exp/af-dspr-cdas (branch off master; ward set experiment-worker; commits
   own work; NO self-promotion; recommend-only).
4. Promotion to master + push via integrator after verifier MERGE verdict.
