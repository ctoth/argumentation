# ICCMA Meta / Harness-Calibration-Coverage Gaps Scout — 2026-07-17

Scope: harness, calibration, and coverage gaps that distort the benchmark
picture independent of solver algorithms. All claims cite file:line.

## 1. Harness state (`tools/iccma2025_run_native.py`)

- **`--jobs` parallelism: LANDED.** `--jobs` arg at :158-166; `RunConfig.jobs`
  :94; concurrent execution via `ThreadPoolExecutor(max_workers=config.jobs)`
  in `run_rows_in_job_order` :278-283 (serial path preserved for jobs<=1
  :273-277). **Caveat, documented in the tool itself** (:202-206): each row is
  its own worker subprocess but they share CPU, so per-row `elapsed_seconds`
  under `--jobs>1` includes contention noise. **Consequence for the picture:
  any timing/PAR2-style number taken from a `--jobs>1` run is not
  contention-free and is not comparable to a serial run.** Solved/timeout
  counts are fine; per-row seconds are not.

- **Per-task competition time budgets: NOT applied — still one flat
  `--timeout-seconds`.** The task-matrix `task` dict carries only
  `track`/`subtrack`/`instance_kind` (see matrix load :231-236, job build
  :237-245, and `base_result` :1237-1257 which reads no budget field). The
  single `config.timeout_seconds` (:116, default 5.0) is used for both the
  outer subprocess wall-clock kill (`run_child` :559,593-602) and the derived
  in-process Z3/clingo budget. There is **no per-subtrack or per-track budget
  from metadata**; ICCMA's real 600–1200 s budgets are not modelled.

- **Z3 per-check timeout + honest `unknown`: FIXED.** The 2026-07-01 hazard
  (Z3 `unknown` silently collapsed into a negative acceptance answer) is
  closed. `AfSatKernel.check` now raises `AfSatCheckTimeout(TimeoutError)`
  whenever the result is neither `sat` nor `unsat` (`af_sat.py:398-403`, class
  at :23-44), after emitting the trace event. Budget is set via
  `_apply_check_budget` → z3 `timeout` param in ms (`af_sat.py:48-52`), applied
  in `AfSatKernel.__init__` (:161) and the CDAS/skeptical solvers (:556,:1252).
  `solver.py` catches it and maps to `SolverBackendTimeout` (`solver.py:380`,
  :437,:454,:569-570) → clean `status="timeout"` row via `solver_timeout_row`
  (`iccma2025_run_native.py:1165-1178`). Harness derives
  `check_budget_seconds = max(0.1, timeout - 1.0)` (:873), 1 s under the outer
  kill. Full write-up + no-regression gate (235=235 solved, +0.96% time) in
  `experiments/2026-07-02-af-z3-check-budget.md`. **This changes the picture:
  pre-fix "negative" answers on hard rows could have been silent wrong
  answers; they are now honest timeouts. Any DC/DS accuracy claim taken before
  this fix is suspect.** Note the fix is Z3-check-time only: rows dominated by
  many short checks or by Python-side parse/encode still rely on the outer
  kill (experiment §Interpretation), so a whole-row deadline remains unbuilt.

## 2. Budget calibration (60/120 s recal)

- **Recal runs COMPLETED** and landed under `data/iccma/2025/runs/`
  (`iccma-2025-timeout-recal-{60,120}s-20260701-*`), for subtracks DC-CO,
  DS-PR, DS-SST, DS-ST, SE-PR, SE-ST. **But they are tiny hard-instance
  subsets, not full-track reruns** — e.g. DC-CO recal is 12 rows
  (6 main + 6 heuristics), SE-PR recal is 5 rows (aba). They target the
  instances that already timed out at low budget.

- **What they show:** raising the budget helps only marginally on the hard
  tail. DC-CO: 60 s → 0/12 solved (all timeout); 120 s → 4/12 solved, 8
  timeout. SE-PR (aba): 60 s → 0/5; 120 s → 1/5. (Summaries:
  `iccma-2025-timeout-recal-{60,120}s-20260701-{DC-CO,SE-PR}-summary.json`.)
  **Interpretation: part of the 30 % timeout rate is a budget artifact —
  doubling 60→120 s converts a third of the DC-CO hard tail to solved — but
  the majority of these specific hard instances stay unsolved even at 120 s,
  which is still 5–10× below ICCMA's 600–1200 s.** We have NOT run any
  full-track sweep at a realistic (>=600 s) budget, so the true
  budget-limited-vs-algorithm-limited split is still unmeasured. This is the
  single biggest calibration gap.

## 3. Coverage

- **2015 track: wired and executed, but 100 % cap-skipped, not "never run".**
  `data/iccma/2015/runs/iccma-2015-sat-kernel-cap100.json` has 4992 rows across
  all 13 SE/DC/DS subtracks; **every row is `skipped` with reason
  `af_argument_cap>100`** (verified by counting). So the query/subtrack wiring
  works; the entire 2015 benchmark set simply exceeds the 100-argument cap.
  Nothing about 2015 has actually been *solved*.

- **2021 track: present and partially run.** `data/iccma/2021/` has
  archives/extracted/manifests/runs; runs are only cap-limited SAT-kernel
  sweeps (`iccma-2021-sat-kernel-cap{20,100}`). Same cap-skip regime applies.

- **SETAF: implemented but NOT wired into the ICCMA runner, and brute-force.**
  `frameworks/setaf.py` computes complete/preferred/stable/semi-stable/stage by
  enumerating `_all_subsets` (2^n) (:103-149,:161-163) — usable only to ~20
  arguments. It is referenced by `solving/solver.py` and
  `solving/solver_differential.py` (differential testing), **not by
  `tools/iccma2025_run_native.py`**: `AF_KINDS` (:23) has no setaf kind, the
  job builder only accepts `{"af","aba"}` (:240), and the 2025 manifest has no
  setaf instances anyway (kinds: af/aba/query_or_updates/results). So SETAF is
  a code capability with zero benchmark coverage.

- **EE-* enumeration / `ExactEnumerationExceeded`.** Exact complete-labelling
  enumeration is guarded by a candidate budget and raises
  `ExactEnumerationExceeded` (`core/labelling.py:203-208`,
  `DEFAULT_COMPLETE_LABELLING_CANDIDATE_BUDGET` :195). The ICCMA CLI catches it
  and returns exit 2 with the message (`solving/iccma_cli.py:77-79`). The 2025
  task-matrix has **no EE-* subtracks** (subtracks are DC/DS/SE only), so exact
  enumeration is not on the competition path — it is a fallback that fails
  loudly rather than a covered track. The "SCC>16" framing is about this exact
  path being viable only on tiny/heavily-decomposed inputs.

- **`dynamic` track: NOT run.** The 2025 task-matrix has a `dynamic` track (4
  tasks, `instance_kind="dynamic"`), and the manifest carries 642
  `query_or_updates` instances, but the runner's job builder only processes
  `instance_kind in {"af","aba"}` (:240). **The entire dynamic/IPAFAIR
  incremental track is silently dropped** — it does not even appear as skipped
  rows.

## 4. Routing

- **`aba_acyc_sat` / external `100ba-acyc` backend: NOT wired — source is
  gone.** `aba_acyc_sat.py` exists only as a stale
  `src/argumentation/structured/aba/__pycache__/aba_acyc_sat.cpython-313.pyc`;
  there is **no `.py` source and it is not git-tracked** (`git ls-files` shows
  nothing). Same for `iccma_setaf` (only a stale root `__pycache__/*.pyc`).
  These are orphaned build artifacts, not live routes. **Anything that claims
  to use an acyclic-ABA fast path is running dead/absent code or nothing.**

- **Symmetric-AF poly case / kernel preprocessing: WIRED.**
  `core/preprocessing.simplify_af` is imported and applied in the AF SAT
  finder prep (`af_sat.py:19`, `_prepare` :446-478, `simplify=True` default on
  the finders, e.g. :465). Preprocessing shortcuts also emit trace markers
  (`af_sat.py:764-770`). So kernel/grounded-reduct preprocessing is on the live
  path. (Did not separately confirm a dedicated symmetric-AF detector; the
  general simplify layer is active.)

- **SCC-recursive decomposition: WIRED (not deferred).**
  `core/scc_recursive.scc_extensions` is imported and used by
  `solving/sat_encoding.py:39-41` (Baroni-Giacomin-Guida SCC decomposition
  composed with preprocessing) and `solving/solver.py:51` (Wave B2 grounded-
  reduct + SCC composition, comment at :1125). SCC-recursive DC/DS *pruning*
  specifically may still be partial, but the decomposition machinery is live,
  contradicting the "still deferred" premise.

## 5. What a real ICCMA submission still needs

- **Solver-adapter workstream is Phase-1-ish, self-described as a "minimal
  subprocess wrapper" being replaced** (`workstreams/iccma-solver-adapter.md`
  §Goal, §Current State :19-25). Adapters exist:
  `solver_adapters/iccma_af.py`, `iccma_aba.py`, `clingo.py`, `_commands.py`.
  `iccma_af` targets the ICCMA 2023 `solver -p <task> -f <file> [-a <query>]`
  protocol and parses YES/NO/witness output (workstream :21-25). It is a
  *client* adapter (we call an external solver), not a conformant *server* CLI
  that a competition would invoke against us.
- **Our own competition-facing CLI is `solving/iccma_cli.py`** and is close on
  I/O: `-p/-f/-a` flags (:87-95), YES/NO + `w ...` witness lines
  (:180-186,:273-276), `NO` for empty SE (:153,:241), p af / p aba autodetect
  (:118-129). Gaps vs a real submission:
  - Supports only DC/DS/SE (`TASKS` :35) and CO/GR/PR/ST/SST/STG/ID/CF2
    semantics (:24-33). No dynamic/IPAFAIR incremental interface, no
    approximate track, no SETAF I/O.
  - **No IPAFAIR / incremental-solver C API** anywhere in the package
    (`dynamics/dynamic.py` exists but is not connected to any ICCMA adapter;
    grep for IPAFAIR/ipafair finds nothing). The dynamic track is
    unreachable both in the batch runner (§3) and the CLI.
  - No `--formats`/`--problems` capability-advertisement handshake (ICCMA
    solvers must answer `--problems`); `iccma_cli._parser` (:82-102) has no
    such flag.
- **Bottom line for submission-readiness:** we have a batch benchmark harness
  and a single-shot AF/ABA CLI, but not (a) IPAFAIR incremental support,
  (b) the `--problems` capability handshake, (c) dynamic/approximate/SETAF
  track I/O, or (d) a validated real-solver conformance round-trip
  (workstream Phase 4 still "select one installable solver", :99-113).

## Priority gaps distorting the picture (ranked)

1. **No realistic-budget full-track run.** All headline runs are 12–30 s (or
   the tiny 60/120 s hard-subset recals); ICCMA is 600–1200 s. The 30 %
   timeout rate conflates budget starvation with algorithmic limits and cannot
   be decomposed from current data. (§2)
2. **Dynamic track silently dropped** (4 tasks, 642 instances) — invisible,
   not even counted as skipped. (§3, runner :240)
3. **Flat timeout, no per-task metadata budget** — every subtrack judged on
   the same wall clock regardless of competition allowance. (§1)
4. **2015/2021 are 100 % cap-skipped**, so "coverage" of those years is
   nominal wiring, zero solved instances. (§3)
5. **Orphaned dead routes** (`aba_acyc_sat`, `iccma_setaf` pyc-only) risk being
   cited as live capability. (§4)
6. **`--jobs>1` timings are contention-noisy** — fine for counts, unsafe for
   per-row speed claims. (§1)
