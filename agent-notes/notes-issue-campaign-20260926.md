# Issue campaign 2026-09-26 (supervisor notes)

Goal: fix open GitHub issues (#2-#37, 36 audit bugs) with subagents, worktrees, TDD, PRs with Closes phrases. Q cap: max 3 concurrent subagents.

## Clusters (by owning module)
- interop/IO: #4 #21 #22 #23 #24 -> PR #55 (agent interop, done), CI running
- gradual/weighted: #7 #8 #9 #20 -> agent gradual, worktree ../argumentation-wt-gradual, branch fix/gradual-weighted-validation
- dynamics: #5 #17 #18 #19 -> agent dynamics, ../argumentation-wt-dynamics, fix/dynamics-faithfulness
- epistemic: #10-#16 -> agent epistemic, ../argumentation-wt-epistemic, fix/epistemic-validation
- QUEUED probabilistic.py: #2 #3 #29 #30 #31 #32 #33 #34 (same file -> one agent, serial)
- QUEUED frameworks: #25 #26 (af_merging) #35 (vaf)
- QUEUED core/structured: #6 (preference) #37 (accrual) #28 (ABA contrariness) #36 (GroundAtom)
- LAST: #27 frozen mappings (cross-cutting; conflicts with everything)

## Observations
- Agent isolation:"worktree" fails (WorktreeCreate hook returns no path) -> create worktrees manually with git worktree add --quiet, pass path in prompt.
- Pre-existing failures on origin/main 978b10e in fresh worktrees: test_decomposed_prefsat_page_image_contract (gitignored png), 2 cadical221 routing tests (vendored binary missing). CI is what matters.
- PR #55 diff reviewed: scoped, clean. Pyright diagnostics seen mid-run were stale.

## BLOCKER found 2026-09-27: main CI red
- main CI (978b10e and earlier) fails the same 3 tests as PR #55: page-image contract (papers/**/pngs gitignored) and 2 cadical221 routing tests (vendored tools/solvers/cadical-2.2.1/cadical.exe absent). PR #55: 3 failed, 3188 passed - identical set.
- Repair as a separate base PR (branch fix/ci-optional-assets, worktree ../argumentation-wt-ci): skip page-image test when pngs absent; skip cadical tests when aba_sat._find_cadical221_binary raises OptionalDependencyUnavailable. Merge it first, then rebase/merge main into cluster PRs.

- CI repair PR #56 opened (local: 12 passed, 3 skipped). Waiting on its CI -> merge --merge -> merge main into #55 and later cluster branches.

- #56 MERGED (d220062). One 3.13 job was cancelled by a runner shutdown (infra); the sibling run passed all 3.
- Merged main into fix/interop-roundtrip, pushed; watching #55 CI.

- Epistemic done: PR #57 (#10-#16), diff reviewed OK; CI watching. Known flake: test_aba_shape_properties::test_permuting_rules_preserves_shape (Hypothesis deadline).
- Dispatched agent `probabilistic` (#2 #3 #29-#34) in ../argumentation-wt-prob, branch fix/probabilistic-dispatch from d220062.
- Live agents: gradual, dynamics, probabilistic (3).

- #55 MERGED 5e48de5 (all 6 checks green); #4 #21 #22 #23 #24 CLOSED. Removed wt-interop and wt-ci.
- Follow-up candidate: project_to_constellation_praf still raises on contradictory constraints (outside #15).

- #57 MERGED 49366bf (6/6 green); #10-#16 CLOSED. wt-epistemic removed. Main CI on 49366bf watching (run 36299463796).
- Closed so far: 12 issues (#4 #10-16 #21-24). Remaining open: #2 #3 #5-9 #17-20 #25-37 minus in-flight.

- Main CI green on 49366bf.
- FAILURE (Q caught): gradual + dynamics idle 25+ min claiming "waiting on pytest" with NO pytest process. Durable fix: memory agents-never-idle.md. Re-driven: gradual -> push its PR + frameworks cluster (#25 #26 #35) in ../argumentation-wt-frameworks (fix/frameworks-merging-vaf); dynamics -> push its PR + core cluster (#6 #37 #28 #36) in ../argumentation-wt-core (fix/core-structured-literals). probabilistic queued #27 next.
- Shut down interop and epistemic (finished).
- Supervisor rule: on every idle notification, verify pytest process exists (Win32_Process cmdline filter on worktree path).

- #70 (dynamics) MERGED 740815b, 6/6 green; #5 #17 #18 #19 CLOSED. wt-dynamics removed. 16 closed total.

- New audit issues #38-#69 filed 2026-09-27. Queued:
  - probabilistic: +#50 #51 #53 (then #27)
  - gradual: +#43 #44 #45 #46 #48 #49
  - dynamics: +#52 #58 #64 #65 #66 #67 #68 #54
  - UNASSIGNED: epistemic #39 #42 #47; optimization #40 #41; ranking/graph #38 #59 #60; clingo adapter #61 #62 #63 #69 -> give to first agent that frees up.

- PR #71 (probabilistic, #2 #3 #29-#34) open; CI watching. Accepted design: world-exponent budget 13; stable MC samples whole framework.
- probabilistic -> #50 #51 #53 (fix/praf-exact-dp-seed), then epistemic #39 #42 #47, optimization #40 #41. #27 held until other PRs merge.
- gradual -> gates for gradual + frameworks PRs running; told to start #44 #45 #46 (fix/bipolar-prudent) meanwhile.
- Still unassigned: ranking #38 #59 #60; clingo #61 #62 #63 #69.

- #71 MERGED 1c35c27 (merged by someone else first); #2 #3 #29-#34 CLOSED. 24 closed total; 30 open (audit keeps filing).
- Local main fast-forwarded to 1c35c27; committed 5 papers notes.md corrections as 0fad795 (Amgoud/Bonzon had CRLF churn vs LF index -> normalized). NOT pushed.

- PR #77 (gradual #7 #8 #9 #20 #43) open, CI watching. PR #81 (#50 #51 #53) open, CI watching.
- gradual: frameworks (#25 #26 #35 +#48 #49) gate running; core-prudent-bipolar (#44 #45 #46) in wt-core-semantics. #45/#46 replaced tests that pinned buggy Cayrol behaviour -> REVIEW CAREFULLY vs Cayrol Def 3.
- probabilistic -> epistemic #39 #42 #47 + optimization #40 #41. #27 after frameworks PRs merge.
- Unassigned: ranking #38 #59 #60; clingo #61 #62 #63 #69.

- #77 MERGED 49390ed (6/6 green); #7 #8 #9 #20 #43 CLOSED. 29 closed total.

- PR #82 (core #6 #37 #28 #36) open, CI watching. Note #36 makes p(1) != p(1.0).
- dynamics re-driven (went idle): ASPIC/Datalog #52 #58 #64-#68, then #54, then clingo #61 #62 #63 #69.
- Unassigned now: ranking #38 #59 #60 only.

- gradual: frameworks PR (#25 #26 #35 #48 #49) + core-prudent-bipolar (#44 #45 #46) gates running; told to serialize gates (MemoryError from ~6 concurrent suites). Assigned ranking #38 #59 #60. Possible new issue: complete_extensions [] on mixed relations (check after #82).
- All open issues assigned except #27 (held).

- #81 MERGED 440f2ef; #50 #51 #53 CLOSED. 32 closed total.

- PR #84 (#44 #45 #46) reviewed vs Cayrol Def 3 (p.383) + Coste-Marquis Def 7: correct; test replacements justified. CI watching.

- gradual: ranking #38 #59 #60 committed (fix/ranking-graph), frameworks gate running. Reassigned clingo #61 #62 #63 #69 from dynamics -> gradual.

- #82 MERGED ad3c01c; #6 #28 #36 #37 CLOSED. 36 closed total. Merged main into #84 myself (29e1960, tests/core 879 passed), CI rerunning.

- PR #85 (epistemic #39 #42 #47) open, CI watching. Known load flakes: test_frontier_v1_parallel, test_iccma_runner_parallel, 50k grounded timing, Hypothesis deadline.
- probabilistic: optimization #40 #41 gate running; then #27 released.

- Q merged #83 (CI matrix now 3.11 + 3.14, fewer duplicate runs). #86 dependabot - not ours.
- #87 (optimization #40 #41) merged. PR #88 (frameworks #25 #26 #35 #48 #49) open, CI watching. #84 one 3.12 job pending; #85 pending.
- probabilistic on #27 (wt-frozen, adds core/frozen.py freeze_mapping). Will conflict with #88 (vaf/caf) -> merge order: #88 first.
- gradual: ranking gate running; clingo #61 #62 done, #63 #69 next.

- MERGED: #85 1ed2a6a (#39 #42 #47), #84 f6840fc (#44 #45 #46), #88 9b20254 (#25 #26 #35 #48 #49). Watching main CI on 9b20254.
- Remaining in flight: #27 (probabilistic), ranking #38 #59 #60 + clingo #61-#63 #69 (gradual), ASPIC/Datalog #52 #58 #64-#68 + #54 (dynamics).
- Cleanup later: worktrees wt-gradual wt-core wt-core-semantics wt-frameworks wt-epistemic2 wt-optimization wt-prob (merged; have untracked logs).

- New issues #72-#80; #16 REOPENED (rounding after validation). Assigned: gradual +#78 #79 (clingo branch), #16, #74 #75 #76 #80, #73; dynamics +#72.

- Q decision: mixed AFs with attack lacking defeat either direction -> reject (ValueError). Filed #90 (prereq: ASPIC producers must not build such AFs, else stop+report). Queued to gradual after #16.

- Main CI green on 9b20254.
- PR #89 (ranking #38 #59 #60) open, CI watching.
- dynamics: 3 branches committed (aspenc #52 #64 #65; datalog #66 #67 #68; aba #54 #58), not pushed. Found local Hypothesis replay hang in test_rebutting_targets_defeasible_conclusions (compute_attacks) - told to extract example + file separate issue.

- #89 (ranking #38 #59 #60) green 3.11/3.14 -> merged.

- PR #92 (#27 frozen mappings, 12 types via core/frozen.freeze_mapping) open, CI watching.
- Rebalanced: probabilistic -> #74 #75 #76 #80, #73, + file/fix aba_shape_properties Hypothesis deadline flake. gradual -> clingo PR (+#78 #79), #16, #90.

- CORRECTED rebalance (gradual had #75 #76 committed on fix/ranking-postulates already): gradual keeps #74 #75 #76 #80 + clingo + #16 (fix/assignment-rounding); probabilistic gets #73, deadline flake, #90. Lesson: check worktree list before reassigning.

- PR #94 (clingo #61 #62 #63 #69 #78 #79) open, CI watching. gradual keeps #73 (done, fix/solver-differential-witness), #16 (fix/assignment-rounding, drops rounding), postulates #74-76 #80 (+ Bonzon notes fix commit). probabilistic: flake issue + #90.

- #92 (#27 frozen mappings) merged. probabilistic's wt-solverdiff = duplicate #73 start (told to drop); its flake fix in same worktree.

- #94 (clingo #61 #62 #63 #69 #78 #79) green -> merged.

- #90 prereq check FAILED (ASPIC+ builder M&P Def12 p<q + PrAF sampling make attack-without-defeat). Q re-decided: M&P 2018 Def 14 throughout; grounded raises ValueError if no complete ext. Issue #90 rewritten; assigned probabilistic after #73+#95. My error: issue claimed nonexistent defeats<=attacks check.
- #73 duplicate: keep probabilistic's (fix/solver-diff-witnesses, with #95); gradual told to drop fix/solver-differential-witness.
- #94 merged 190beaf. 59 closed.

- dynamics PRs: #91 (aspenc #52 #64 #65) green; #93 (datalog #66 #67 #68) green but Q decided #66 = FIRST-APPEARANCE variable order -> dynamics reworking; #96 (aba #54 #58) CI running.
- dynamics next: extract/file aspic hang issue; worktree cleanup. probabilistic: #90 must include operational contract for mixed preferred (no full subset enum; #82 perf risk).

- #91 merged 98d91b6 (#52 #64 #65). #96 (#54 #58) green -> merged.
- dynamics order: #66 rework on #93, #72 own branch, hang issue.

- #96 merged f16413e (#54 #58). 64 closed. PR #97 (#73 + #95) open, CI watching. probabilistic re-told #90 UNBLOCKED (message lag).
- Open work: #93 (#66 rework), #72 (dynamics), postulates #74-76 #80 + #16 (gradual), #90 (probabilistic).

- #97 merged 0ae0829 (#73 #95). 66 closed. probabilistic on #90 in wt-def14.

- 08:4x check: gradual idle, postulates gate exit=0 but unpushed, no pytest running -> re-driven. dynamics running (#93 rework/#72/hang probe in scratchpad), probabilistic running (#90 wt-def14).

- #98 merged acf7f9c (#74 #75 #76 #80). #99 merged 6441acd (#90: Def 14 semantics, grounded raises, pruned preferred DFS 2N+1 nodes, solver-layer fixes gated on attacks_resolved_by_defeats). 71 closed.
- Remaining: #66-#68 (#93 needs first-appearance rework - NOT started as of ~10:50), #72, #16.

- Reassigned #93 #66 rework -> probabilistic. dynamics -> #72 + file hang issue.

- #93 merged 9c6de2b (#66 first-appearance, #67, #68). 74 closed. Open: #16 (gradual green gate, unpushed -> I'm publishing it myself), #72 (no branch found; dynamics).

- PR #100 (#16) opened by me from gradual's green branch (body corrected: coarse-bound control). CI watching.
- #72 -> probabilistic (fix/aba-skeptical-underivable). dynamics -> file hang issue + cleanup. gradual -> cleanup its worktrees.

- #100 merged (#16). 75 closed. Only #72 open (probabilistic, wt-abaskep).

- #101 merged 052775e (#72). ALL original+audit issues closed (76). Only #102 open (dynamics filed: compute_attacks blow-up, 18,850 args / 8.7M rebuttals). probabilistic investigating (profile, contract, options) before any fix; semantic change -> Q decides.
- Note for Q: #93 made named defeaters with args on a bare GroundingInspection raise unless rule_variable_orders supplied (propstore callers may need update). #90 criterion "preferred = maximal complete" only holds when every attack is a defeat in some direction (540/10,664 counterexamples otherwise).
- gradual removed its 6 worktrees. Remaining cleanup: wt-rounding (mine), dynamics' worktrees, probabilistic's.

- gradual shut down. dynamics pushed duplicate #72 fix (9342f49) to already-merged #96 branch - harmless, not on main; told to clean up worktrees then shut down. dynamics' py-spy on #102: cost = attack relation size itself (8.7M pairs). probabilistic told to skip re-profiling and report ASPIC+ pruning options + generator bound.

- dynamics shut down (4 worktrees removed). Only probabilistic live.
- #102 investigation: cost = output size (8.7M rebuttals + 297M undermines) from argument multiplication (~q,~q->p = 136^2; permuted duplicate strict rules). Q chose A1+A2 (antecedent-set reading, 18,850 -> 98 args). probabilistic: item-5 PR first (generator distinct antecedents, assume guard, pinned xfail contract, "Refs #102"), then A1+A2 PR "Closes #102".

- 18:42Z: probabilistic "running" but wt-aspicgen empty for 3h, no pytest -> nudged. If no reply, stop it and redo item 5 myself or fresh agent.

- #103 (test-only, Refs #102: generator distinct antecedents, 2000-arg assume guard, pinned xfail budget contract) merged. probabilistic implementing A1+A2 in wt-rulesets.

- #104 (A1+A2 strict, Rule.__post_init__, 18,850->98 args) CI green; Q decided defeasible rules get set reading too -> probabilistic extending #104 before merge.

- probabilistic stuck 9h (no progress on defeasible extension) -> TaskStop. I implemented defeasible set reading myself in wt-rulesets (Rule.__post_init__ now canonicalises all kinds; name kept). 4 new tests red->green; rule_sets+budget 12 passed. Next: full gate, push to #104, merge.

- #104 merged db0eaad (+ defeasible set reading 17d7df7, full suite 3511 passed). #102 CLOSED. 0 open issues, 0 open PRs.
- Removed 10 remaining campaign worktrees (all clean, 0 unpushed). All agents shut down/stopped.
- CAMPAIGN COMPLETE: main CI green on 985d456 (includes db0eaad), 3.11 + 3.14.

## Next
- When #55 CI green: gh pr merge 55 --merge (never squash). Remove worktree after merge.
- On each agent finish: review diff, watch CI, merge, dispatch next queued cluster (<=3 live).
