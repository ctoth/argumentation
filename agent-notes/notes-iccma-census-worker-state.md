# ICCMA Census + Budget Worker — State

Branch: `exp/iccma-census-budgets` (off main). Ward: experiment mode. NEVER touch main.
HARD PROHIBITION: never open/read/run any `*holdout*` file (esp. experiments/iccma2023-frame/population-holdout.json).

## Deliverables (in order)
1. PER-TASK BUDGETS in tools/iccma2025_run_native.py: add `--budgets-json FILE` (task→seconds), fallback to --timeout-seconds. Default byte-identical when absent. Add test proving dispatch equivalence. Commit.
2. STRATIFIED TIMEOUT SAMPLE (~48-60 timeout rows) from truth run, freeze manifest experiments/iccma-census/sample-timeout-600s.json + selection code. Run at 600s --jobs 4. Per-stratum: solved@600 vs still-timeout.
3. PROBE-KILL RECHECK: rerun 2-3 killed ABA Probe 1-8 rows (aba_2000_0.3 600-assumption, known solve 84-104s) at 600s.
4. RECORD experiments/2026-07-17-realistic-budget-census.md + INDEX.md.
5. IF TIME: estimate wall-clock for full fresh census at t15 --jobs 8 (do NOT launch).

## Facts established so far
- Truth run: data/iccma/2025/runs/iccma-2025-full-uncapped-auto-t5-2026-05-14.{json,csv,summary.json}
  - 4243 solved / 1871 timeout / 1280 skipped / 7394 total. Tracks: aba 1920, heuristics 2254, main 3220.
  - CSV 7394 data rows. Cols: track,subtrack,instance_kind,instance,backend,status,reason,elapsed_seconds,answer,extension_count,witness_size,witness,arguments_or_atoms,attacks,assumptions,rules,contraries,error
  - JSON is 48MB. Use CSV for sampling.
- Runner tools/iccma2025_run_native.py:
  - Timeout used in TWO places: run_child(timeout_seconds=config.timeout_seconds) at :465 (outer subprocess wall kill) AND job["solver_timeout_seconds"]=config.timeout_seconds at :452 (in-process Z3/clingo budget). Per-task budget must flow to BOTH.
  - `task` dict has track/subtrack/instance_kind. Budget key = subtrack (e.g. "DS-PR"). run_or_skip has config+instance+task in scope at :409.
  - RunConfig frozen dataclass :79. --jobs landed. jobs>1 timings contention-noisy (counts OK).
  - NO existing test file matching tests/**/*iccma2025_run* — need to find how runner is tested.

## D1 PROGRESS (per-task budgets)
- RunConfig.task_budgets: dict[str,float]=field(default_factory=dict) added (import field).
- budget_for_task(config, task) helper: returns task_budgets.get(subtrack, timeout_seconds). Placed before run_or_skip.
- run_or_skip: budget_seconds=budget_for_task(...); used in job["solver_timeout_seconds"], profile_duration_seconds(budget_seconds), run_child(timeout_seconds=budget_seconds).
- profile_duration_seconds now takes float (was config). Only in-module caller is line 474. aba_shape_benchmark has its own separate one.
- Existing tests use RunConfig without task_budgets -> default empty -> byte-identical. test at line 444 expects 29.0 w/ timeout 30 -> budget_for_task=30 -> 29.0 OK.
- Test files: tests/interop/test_iccma_runner.py, test_iccma_runner_timeout_contract.py (monkeypatch build_worker_command pattern), test_iccma_runner_parallel.py.
- STILL TODO D1: add --budgets-json CLI flag + parse + RunConfig wiring + main() info print; add dispatch-equivalence test; run pytest; commit.

## !! COLLISION (shared working dir) — 2026-07-17
- Created exp/iccma-census-budgets off main (f4b8eac). Implemented D1. But my commit
  `3d7fc24` (feat per-subtrack budgets, D1 DONE + 38 tests pass) landed on branch
  `exp/af-satsub-incremental`, NOT my branch.
- reflog: HEAD@{2} main->exp/iccma-census-budgets (me); HEAD@{1} exp/iccma-census-budgets->exp/af-satsub-incremental
  (ANOTHER AGENT switched HEAD in the SHARED working dir — I did not); HEAD@{0} my commit.
- Another live agent (notes-af-satsub-worker-state.md freshly untracked) shares this exact
  checkout and switches branches. This BREAKS long budgeted benchmark runs: a mid-run checkout
  reverts tools/iccma2025_run_native.py to the non-budget version.
- FIX PLAN (reversible, branch-pointer only, no working-tree clobber since both branches == 3d7fc24):
  1. git branch -f exp/iccma-census-budgets 3d7fc24
  2. git checkout exp/iccma-census-budgets  (no-op tree change; carries other worker's uncommitted work)
  3. git branch -f exp/af-satsub-incremental f4b8eac  (restore their branch to its base)
- Then REPORT to team-lead: need isolated worktree before running D2/D3 long benchmarks.

## RESOLUTION: isolated worktree (all further work here)
- WORKTREE: C:/Users/Q/AppData/Local/Temp/claude/C--Users-Q-code-argumentation/e531f1d6-db52-4333-8cee-1726098fa014/scratchpad/census-wt
  on branch exp/iccma-census-budgets (head 3d7fc24, budget code verified present). Use `git -C <WT>` + absolute paths. NEVER work in the shared dir again.
- Shared dir HEAD restored to exp/af-satsub-incremental for the other worker.
- ENTANGLEMENT flagged to team-lead: my commit 3d7fc24 is now an ancestor of their c844e1a
  (their commit's parent = my commit). No work lost; their branch just carries my budget commit.
  Left as-is (rewriting their committed hash unilaterally is worse). Lead/other worker to decide.
- D1 COMPLETE: commit 3d7fc24 on exp/iccma-census-budgets, 38 tests pass.

## D2 PROGRESS (stratified sample)
- Truth run command (from experiments/2026-06-29-...): `--backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 5`. So t5 = 5 SECONDS. All 1871 timeouts at 5s budget -> huge headroom to 600s.
- Timeout distribution by subtrack: DS-PR 275, DS-SST 216, SE-PR 183, DC-SST 180, DS-ST 179, DC-CO 178, SE-ST 164, DC-ST 160, SE-ID 114, DC-ID 114, SE-SST 108 (=1871).
- Family x subtrack crosstab computed (crusti_g2io/scc/ER/mainkwt/abcgen/aba). abcgen+aba are ABA-only (SE-PR/SE-ST). mainkwt real only in DS-PR (34).
- Selection code: experiments/iccma-census/select_sample.py (in worktree). STRATA plan = 22 cells, 52 rows total. Deterministic: sort by relative_path, take first k.
- CSV instance column == manifest relative_path (matches --only-instance filter). Confirmed via base_result.
- RUN PLAN: per-subtrack runner invocations (runner filters instance & subtrack independently, NOT per-pair; so run one invocation per subtrack with only that subtrack's sampled instances -> exactly the cell pairs). Flags: --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 600 --jobs 4 --root C:/Users/Q/code/argumentation/data/iccma/2025.
- ESTIMATE: 52 rows, worst case all-timeout at jobs4 = ceil(52/4)*600 = 7800s ~130min. Expect 60-110min. Background + poll log.
- NEXT: run select_sample.py -> manifest; commit manifest+code; launch background run; poll; tabulate per-stratum solved@600 vs timeout.

## D2 continued — commits + run design
- Manifest committed a816a75. --only-track filter committed 32290b5 (each AF instance runs
  under BOTH main+heuristics = identical redundant solves; --only-track main halves wall time).
- Preflight PASSED: worktree tool runs vs shared --root data, resolves instances, produces rows.
  crusti_g2io_125_0.5_31_17.af DS-PR still timeout at 15s (hard family).
- Manifest hashes: source_csv sha256 bbe3865f62ecc6051fd6ebf9ff405086afc0f48584d3c16b12bfda3aa5005bda ;
  manifest self sha256 f4c79993a0269218b791af38e08c2540db50d7e99f69b7bbde30c1369d0ba78b (WILL CHANGE if regenerated).
- RUN DRIVER: per-subtrack invocation, --only-track main, from worktree, --root shared data.
  8 subtracks: DC-CO DC-ID DS-PR DS-SST SE-ID SE-PR SE-SST SE-ST.
- Commits on my branch so far: 3d7fc24 (D1 budgets) -> a816a75 (D2 sample) -> 32290b5 (only-track).

## D2 RUN — track scheme + CRLF bug fixed
- Track scheme: DC/DS subtracks -> --only-track main (drops heuristics AF dup). SE subtracks -> NO track filter (main af + aba both wanted; ABA strata under track "aba"; SE has no heuristics). Yields exactly 52 rows (1 per manifest entry).
- BUG: first driver run built 0 jobs — uv/python prints CRLF, mapfile -t leaves \r, --only-instance "val\r" matched nothing. FIX: pipe python output through `tr -d '\r'`. Preflight2 DC-CO now jobs=6 rows=6 (all timeout@6s).
- Driver: scratchpad/run_census_sample.sh. Log: logs/census-sample-600s-2026-07-17.log. Outputs: data/iccma/2025/runs/iccma-2025-census-600s-<ST>.{json,csv,summary.json}.
- Expected rows per subtrack: DC-CO 6, DC-ID 2, DS-PR 12, DS-SST 6, SE-ID 6, SE-PR 7, SE-SST 4, SE-ST 9 = 52.
- D3 deferred until census done (CPU contention would cause false timeouts).

## LIVE RESULTS (census be0wo1izb running)
- DC-CO: 6/6 SOLVED at 600s (elapsed 7-30s under jobs4 contention). Truth run: all timed out at 5s.
  => PURE BUDGET ARTIFACTS. The 5s truth budget was far too tight.
- BUG in track scheme: DC-ID built 0 jobs. DC-ID exists ONLY under heuristics track in 2025 matrix
  (main lacks DC-ID). My --only-track main dropped the 2 ER DC-ID rows. FIX: run DC-ID with NO track
  filter (or --only-track heuristics) as a separate fixup after census. Only DC-ID affected; all other
  subtracks correct (DC-CO 6, DS-PR 12 jobs confirmed).
- D3 READY: extracted benchmarks/aba/aba_2000_0.3_10_10_{0,1}.aba into data/iccma/2023/extracted/instances/
  (from archives/iccma2023_benchmarks.zip). 600-assumption, 2000 atoms. SE tasks need no query.
  D3 command (run AFTER census, jobs 1 for clean timing):
    uv run tools/iccma2025_run_native.py --root data/iccma/2023 --backend auto --max-af-arguments -1
    --max-aba-assumptions 1000000 --timeout-seconds 600 --jobs 1 --only-subtrack SE-ST --only-subtrack SE-PR
    --only-instance benchmarks/aba/aba_2000_0.3_10_10_0.aba --only-instance benchmarks/aba/aba_2000_0.3_10_10_1.aba
    --label census-probe-recheck-600s
  (aba instances are kind aba -> only aba-track SE tasks match; no track filter needed. 4 rows.)
  Probe records affected: N1 (aba_2000_0.3_10_10_0 SE-ST timeout>5s), R1-P3 (600-assumption headroom),
  and the whole Probe 1-8 campaign ran at 5-10s wall on these rows.

## WAVE 2 — full t15 jobs8 census RUNNING (2026-07-18)
- Measuring MAIN f4b8eac (clean detached worktree scratchpad/main-census-wt; runner has NO --budgets/--only-track = clean main). Task bbh9w0vg2 (harness-managed, NOT nohup).
- Cmd: --root data/iccma/2025 --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 15 --jobs 8 --event-log-path logs/census-full-t15-jobs8-2026-07-18.events.jsonl --label full-uncapped-auto-t15-jobs8-2026-07-18.
- Output will be: data/iccma/2025/runs/iccma-2025-full-uncapped-auto-t15-jobs8-2026-07-18.{json,csv,summary.json}.
- Polling in-turn via `timeout 480 tail -f EVLOG | grep -m1 iccma_run_rows_complete` (8-min blocking slices, no sleep, no nohup). Progress: 1846/7394 @ 11:22 (25min in). ~87-100min est total. mtime fresh = healthy.
- Launched ~10:57. Jobs built 7394 (1280 will be cap-skips instant). 
- WHEN COMPLETE: load summary -> delta vs 2026-05-14 truth (4243/1871/1280) by track+family -> update record (measured commit=f4b8eac, all July landings) -> commit summary+record on exp/iccma-census-budgets -> report to lead.

## ALL DELIVERABLES DONE (15:43)
- D3 DONE: all 4 aba rows SOLVED@600 jobs1: _0 SE-ST 109.8s, _0 SE-PR 128.4s, _1 SE-ST 1.1s, _1 SE-PR 14.8s.
  VERDICT: Probe 1-8 wall-clock kills were BUDGET ARTIFACTS (5s wall vs 109.8s solve vs 1200s real ICCMA budget). Semantic kills (Probe 6) stand.
- FINAL CENSUS: 52 rows, 40 solved/12 timeout = 0.769. Hard = ER(9)+scc(3). crusti/mainkwt/abcgen/aba=100% artifact.
- D5 estimate: t15 jobs8 full census ~87min (~1.4h). CPU~41,600s /8. Command in record. NOT launched.
- Record COMMITTED: 764a170 (record+INDEX+driver+aggregator). Branch: 3d7fc24 -> a816a75 -> 32290b5 -> 7b36cbf -> 764a170. D5 edit pending commit.
- BRANCH SHAs (exp/iccma-census-budgets): D1=3d7fc24, D2sample=a816a75, only-track=32290b5, pyright=7b36cbf, record=764a170.
- NEXT: commit D5 edit, send final report to lead.

## DC-ID DONE + D3 FIX (15:36)
- DC-ID fixup DONE: 2 ER rows BOTH timeout@600 (ER_300_20_2, ER_300_30_4). ER = algorithmic hard confirmed.
- FULL CENSUS 52 rows: 40 solved / 12 timeout = 0.769 budget-artifact fraction.
- D3 first attempt FAILED (0 jobs): data/iccma/2023 has only task-matrix.CSV (no .json) -> runner infer_task_matrix produces AF-only legacy tasks, no aba tasks. (frame baseline Jul11 must have had a .json since replaced Jul12.)
- D3 FIX: built ISOLATED root (no shared-data change, no af-satsub interference): scratchpad/d3root/ with manifests/iccma-2023d3-{manifest,task-matrix}.json (aba SE-ST+SE-PR) + extracted/instances/benchmarks/aba/*.aba (2 copied files). Discovery verified.
- NEXT: run D3 --root d3root at 600s jobs1 (SYNC, in-turn poll — foreground, 4 rows: 2 inst x SE-ST/SE-PR). Then patch record (DC-ID row DONE=0/2, final fraction 40/52=0.769, D3 verdict), commit record+INDEX+driver scripts, final report to lead.
- All my launched procs are DONE now (finish script FINISH DONE 15:36:04; DC-ID done; waiters fired). No live procs.

## FINALIZING (15:32) — record drafted, DC-ID+D3 running
- Record DRAFTED: scratchpad/census-wt/experiments/2026-07-17-realistic-budget-census.md (full 50-row table + narrative; 2 patch points: DC-ID row + D3 results + final 52-row fraction).
- INDEX.md: appended "Related standalone measurement" cross-ref in worktree (uncommitted).
- DC-ID fixup still running (2 ER rows toward 600s, started 15:25:54, no rows yet at 15:32).
- finish_census.sh launched background (bukeu5zax launcher returned; script running): waits DC-ID done -> runs D3 recheck jobs1 (4 aba rows) -> writes logs/census-finish-2026-07-17.log. Poll for "FINISH DONE".
- D3 output will be data/iccma/2023/runs/iccma-2023-census-probe-recheck-600s.json (4 rows: 2 instances x SE-ST+SE-PR).
- WHEN FINISH DONE: patch record (DC-ID row, final fraction 40+?/52, D3 verdict), commit record+INDEX+scripts (select_sample already committed; add driver scripts optionally), send final report to lead with SHAs+table+fraction+probe verdicts.
- NEVER open population-holdout.json (only dev used for D3).

## CENSUS COMPLETE (be0wo1izb done 03:36) — RESUMED SYNC after 12h wakeup failure
- Background WAKEUP mechanism failed session-wide (~12h lost). Now: run in background but ACTIVELY POLL disk (log mtime/COMPLETE marker) in-turn; never await wakeup. Q CLAUDE.md updated (SUPERVISION IS VERIFICATION).
- 50 rows aggregated (all strata except DC-ID which my track bug dropped): 40 solved / 10 timeout = 0.80 budget-artifact fraction.
- 10 hard rows: ER (DS-PR 3, SE-ID 2, SE-PR 2 = 7) + scc (DS-PR 1, DS-SST 1, SE-ID 1 = 3). crusti/mainkwt/abcgen/aba = 100% budget artifacts at 600s.
- DC-ID fixup running in background (launcher task bggam74dg returned; runner still going). Log: logs/census-dcid-fixup-2026-07-17.log. 2 ER rows, likely timeout (~10min). POLL until 2 rows in data/iccma/2025/runs/iccma-2025-census-600s-DC-ID.json.
- Aggregation script: scratchpad/aggregate_census.py. Record draft: scratchpad/census-wt/experiments/2026-07-17-realistic-budget-census.md.
- REMAINING: poll DC-ID done -> re-aggregate (52 rows) -> D3 recheck (jobs1, 4 aba rows, background+poll) -> fill+commit record + INDEX.md -> final report to lead with SHAs.

## PARTIAL RESULTS (be0wo1izb, DC-CO+DS-PR done)
- DC-CO: 6/6 solved @600 (crusti+scc, 7-30s). Budget artifacts.
- DS-PR (12): crusti 3/3 solved (27-29s), mainkwt 3/3 solved (11-12s), scc 2/3 solved (23-25s; scc_1554 TIMEOUT@600), ER 0/3 solved (ALL timeout@600 = ALGORITHMIC HARD).
- KEY: split is family/instance-specific. crusti_g2io_125/150 solve (budget artifact) though scoreboard flagged crusti DS-PR hard — the hard ones were crusti_175/225 (not in sample). ER DS-PR + scc_1554 are genuinely hard at 600s.
- DS-PR took 11 min. Remaining: DS-SST, SE-ID, SE-PR, SE-SST, SE-ST running.
- PYRIGHT verified clean at 7b36cbf (project basic config 0 errors; broad standard-mode run: my file 0 mentions). Lead's 132/138 = stale LSP cache of pre-fix dict[str,object]. Reported.

## WAITING on census be0wo1izb (background)
- Draft record: scratchpad/census-wt/experiments/2026-07-17-realistic-budget-census.md (placeholders for table+fractions).
- Aggregation script: scratchpad/aggregate_census.py (reads census-600s-<ST>.json, family-classifies, per-stratum solved/timeout + budget-artifact fraction).
- SE-* summary files currently STALE (from first empty run bjaz9ewgi). Only trust after log shows COMPLETE.
- ON CENSUS COMPLETE, do in order:
  1. Run DC-ID fixup: same cmd but --only-subtrack DC-ID with NO --only-track (heuristics-only), --label census-600s-DC-ID. (2 ER rows) — overwrites the empty DC-ID output.
  2. Run aggregate_census.py -> per-stratum table + budget-artifact fraction.
  3. Run D3 probe recheck (jobs 1) -> 4 aba rows.
  4. Fill record, add to experiments/INDEX.md, commit record (+ driver/agg scripts optionally).
  5. Final message to team-lead: SHAs, table, fraction, probe verdicts, entanglement blocker.
- Commits on branch: 3d7fc24 (D1) -> a816a75 (D2 sample) -> 32290b5 (only-track) -> 7b36cbf (pyright fix). Record+D3 still uncommitted.
- PYRIGHT: D1 files now 0 errors. Fixed test _config to use dataclasses.replace (not dict splat) + captured dict[str,Any]. 14 budget tests pass. Runner file was already clean.

## Blocker/next
- Find existing runner tests (glob found none; search broader).
- Design: add budgets_json path → RunConfig.task_budgets: Mapping[str,float] = {}. Helper budget_for_task(config, task) -> float. Apply in run_or_skip for both run_child timeout and job solver_timeout_seconds.
