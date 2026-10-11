## Checkpoint: full sweep and timeout diagnostics
- Completed 7,394 rows at 60s/jobs8 on isolated head 052775ed01027ea8e559501368640ed079ae9e4e: 5,425 solved, 1,969 timeouts, no errors/skips; artifacts: data/iccma/2025/runs/full-20260927/.
- Timeouts cluster in abcgen (507/593 ABA timeouts), crusti_g2io (178/200 main tasks), and Medium/Large-result; counts establish patterns, not bottleneck causes.
- Runner run_child immediately process.kill()s on deadline; optional py-spy recording exists but was not enabled for this sweep. No automatic pre-kill diagnostics; 1,950 timeouts were outer deadline kills.
- Current state: user asked why diagnostics are absent; explanation given, no implementation requested or performed. Next action if implementing: executable operational contracts for diagnostic persistence and bounded termination, then real-worker py-spy verification; leave this checkpoint uncommitted.

## Checkpoint: timeout harness fix
- User authorized implementation; isolated branch fix/iccma-timeout-diagnostics at C:/Users/Q/code/argumentation-timeout-diagnostics adds automatic bounded py-spy stack dumps before outer timeout kills, result/event artifact links, actual-worker PID publication, and tree termination/reaping.
- Added operational tests first (five initial failures), then verified 49 focused tests including opt-in real py-spy attachment; Ruff and diff checks pass. In-process timeout rows retain existing solver metadata; snapshots are not historical profiles.
- Real abcgen DC-CO worker at a 3s deadline saved _minimal_supports/_add_minimal_support frames in data/iccma/2025/runs/timeout-diagnostics/timeout-69264-6b27c994c2cc4d4e86cb84b6bb98c251.json; launcher 69264 and worker 77432 both confirmed exited.
- No benchmark rerun or solver optimization performed. Fix remains isolated from the primary checkout; no push/merge requested. This checkpoint stays uncommitted.

## Checkpoint: authorized merge and first profiled solver repair
- User authorized main merge and solver fixes; harness merged locally as baabafd (two parents) after 103 interop tests. Active repair worktree/branch: C:/Users/Q/code/argumentation-profiled-bottlenecks, fix/iccma-profiled-bottlenecks.
- Real-worker 15s py-spy profiles under data/iccma/2025/runs/diagnosis-20260927 show ABA auto support enumeration/constraint building, ABA explicit ASP complete-model enumeration, crusti Z3 expression construction, and Large-result_b11 parsing 20.9M attacks.
- Added red operational contracts (7 failures) forbidding ABA support/model enumeration and bounding complete credulous queries to one solve; wired existing Clingo query helper, retained preprocessing/lifting and no-Clingo SAT fallback. Ten new route/oracle tests now pass.
- After profile of same abcgen DC-CO worker finished in ~3s command wall time; pending unprofiled frozen benchmark gate, broader tests, before/after profile summary, and review. Solver repair is uncommitted; no remote push yet.

## Checkpoint: repair validation and parser allocation fix
- ABA route repair passed 1546 tests/3 skips; pyright with main .venv interpreter and scoped Ruff clean. Same query profile fell from 14.75s sampled (9.85 support enumeration, 4.23 constraints) to 1.35s total, one solve, no enumeration.
- Full frozen 320-row ABA DC-CO gate running in exec session 81924, label dcco-query-fix-20260927, t60/jobs4; at least 221 completed (215 solved/6 timeout), no official-answer disagreements so far. Remaining abcgen dumps show time in Clingo solve, not support expansion.
- Second fix: canonical ID reuse in numeric AF parser; red operational test saw 28800 validations for 120 IDs. Fixed parser passes it and 112 interop/CLI checks (1 skipped).
- On real Medium-result_b20 (843510 attacks), parse 2.908s -> 1.309s, endpoint strings 1682557 -> 1434, identical canonical AF hash; Large-result_b11 profile still parsing at 15s but repeated-ID validation disappears. Pending final gate, profiler diagnosis of residual failures, report, and scoped commits; fixes remain uncommitted in repair worktree.

## Checkpoint: third fix and final gate underway
- Parser repair committed locally as 0ab6a3b on fix/iccma-profiled-bottlenecks. ABA query repair remains uncommitted; gate session 81924 at 306/320 rows: 267 solved/39 timeout, abcgen 70 solved/36 timeout; no regressions or answer changes in earlier comparisons.
- Third repair removes redundant per-defeat conflict clauses already implied by complete labellings, preserving separate attack conflicts. Red shape test: 460 assertions vs required <=60 on 20 vertices; now passes. Full solving suite: 338 passed/3 skipped; Ruff/Pyright pass.
- Real crusti SE-PR before/after profiles: baseline still unsolved at 59.99 sampled seconds (40.99 in add_conflict_free), repaired solves with 34.00 sampled seconds (zero add_conflict_free). Broader ABA checks previously 1546 passed/3 skipped; interop/CLI 112 passed/1 skipped.
- Remaining ABA hard case paired profiles show bottleneck moved from support/constraint construction to Clingo search (13.72/14.98s); automatic timeout dumps agree. Finish gate/official-answer comparison, update investigation, and commit ABA/AF fixes separately. No remote push; only harness is merged into local main.

## Checkpoint: completed repair gates and main integration
- Full 320-row ABA DC-CO gate complete: 269 solved/51 timeout vs 160/160 baseline; abcgen 72/120 solved vs zero, other ABA 197/200. No lost solves/changed answers; all 269 solved answers match unanimous cached official results.
- Unprofiled crusti SE-PR gate solved in 34.095s (prior 60s timeout), witness size126. Paired profiles establish deletion of 40.99s redundant conflict-clause construction. Parser and solver operational/semantic contracts pass; full solving 338 passed/3 skipped, ABA 1546 passed/3 skipped, interop/CLI112 passed/1 skipped.
- Scoped commits: 0ab6a3b parser; 20564bd AF clauses; 33e00c9 ABA direct query; 6ffe9d3 report/frozen manifest/profile tool. Repairs integrated into local main with normal merge after the earlier baabafd harness merge; no remote push.
- Final report: investigations/iccma-timeouts-20260927.md. Remaining ABA search timeouts and dense parsing/encoding costs explicitly recorded; no claim of a new full-7394-task score. This checkpoint remains uncommitted.
