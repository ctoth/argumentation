# ICCMA campaign history scout — working state (2026-07-11)

Role: `ward set researcher` done. Task: inventory ICCMA experiment history, reconstruct
tried/kept/rejected/diagnosis-incomplete hypotheses + causes of death. No modifications, no benchmarks.
Output target: reports/iccma-campaign-history-scout-20260711.md

## Sources located
- notes-iccma-campaign-log-2026-07-02.md (foreman dispatch log, ICCMA 2025 frontier campaign)
- notes-iccma-timeout-strategy-2026-07-01.md (rich synthesis: AF is the elephant, ranked strategy 0-8)
- experiments/2026-07-11-iccma2023-aba-600-stable-sat-route.md (NEGATIVE)
- experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md (NEGATIVE)
- experiments/ ~ many 2026-05-20/21/22 aba SE-ST records, 2026-07-02..10 frontier records
- docs/reports/iccma2023-current-papers-2026-07-11.md + iccma2023-repo-research-2026-07-11.md (from 57bebf7)
- notes/iccma-bench-cap150-2026-05-13.md, notes/iccma-bench-recon-2026-05-13-scout-checkpoint.md
- notes/ds-pr-timeouts-2026-05-02.md, notes/aba-completion-sat-bottleneck-2026-05-20.md

## Facts established so far (cited)
1. TRUTH RUN uncapped ~15s: data/iccma/2025/runs/iccma-2025-full-uncapped-auto-t5-2026-05-14.json
   4,243 solved / 1,871 TIMEOUT / 1,280 skipped. AF=1,722 TO vs ABA=149 TO => AF is elephant.
   (notes-iccma-timeout-strategy line 61-64)
2. Worst AF families: crusti_g2io >=125 args 100% TO; scc_1554 28 TO DC-CO; ER_300 34 DS-SST/30 DS-PR;
   mainkwt_250 34 DS-PR. Worst tasks DS-PR 43%. (same, 66-68)
3. cap-N = SIZE cap not time; many past "bottlenecks" phantom of 30s gates; 700-assumption SE-ST
   104s native fine, 28 experiments reverted (notes/aba-completion-sat-bottleneck-2026-05-20.md).
4. ICCMA 2023 SE-ST aba_2000_0.3_10_10_0: auto ASP/Clingo timeout>5s; 302/384 samples in clingo solve.
   - SAT ranked-closure route: timeout>5.023s, 391/399 samples in _add_ranked_closure_constraints (Z3 never solved). ABANDONED.
   - native CNF base UNSAT screen: base is UNSAT but solve=46.1s (build 0.56s). ABANDONED (46s precheck ahead of 5s worker).
   - "second consecutive slice without a kept metric improvement" — campaign may not widen.
5. Frontier campaign 2026-07: 9/30 -> 18/30 measured; DS-PR 229->235, SST 576->578, SE-ST 217->241.
   Landings: af-dspr-cdas, af-sststg-shortcuts, af-z3-check-budget, abcgen-arc-acyc, af-scc-acceptance,
   frontier-parallel, runner-parallel. (notes-iccma-campaign-log)
6. z3-scout: NO z3 per-check timeout anywhere; unknown collapsed to negative => silent wrong-answer hazard
   (af_sat.py:443; solver.py:833-853). SolverTimeout exists core/solver_results.py:58.

## Still to read
- docs/reports/iccma2023-repo-research + current-papers (research record 57bebf7)
- experiments 2026-07-02..10 frontier records (cause-of-death detail per landing)
- notes/ds-pr-timeouts-2026-05-02.md, cap150/recon notes
- git log for full experiment ledger

## Blocker: none
