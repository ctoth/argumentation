# ICCMA 2023 repository research — 2026-07-11

## Scope and verification status

This is a read-only repository investigation apart from this report. I did not run a benchmark. The checkout was `main`; `git show -s 84cbb04` resolved to merge commit `84cbb04d8f9130467f8828abe14118fab7d31392` with subject `Merge native ICCMA runner parallelization`. The worktree already had many unrelated untracked files, which I did not modify.

Commands used for corpus verification included:

```powershell
uv run tools\iccma_data.py --year 2023 list --json
Get-FileHash -Algorithm MD5 data\iccma\2023\archives\iccma2023_benchmarks.zip,data\iccma\2023\archives\iccma2023_results.zip
jq -r 'group_by([.kind,.parse_status])[] | [.[0].kind, .[0].parse_status, length] | @tsv' data/iccma/2023/manifests/iccma-2023-manifest.json
jq -r 'map(select(.archive=="instances") | . + {family:(.relative_path|split("/")|.[0:2]|join("/"))}) | group_by([.family,.kind,.parse_status])[] | [.[0].family,.[0].kind,.[0].parse_status,length] | @tsv' data/iccma/2023/manifests/iccma-2023-manifest.json
uv run tools\iccma2025_run_native.py --help
```

## Verified local ICCMA 2023 assets

The repository's multi-year data tool defines the 2023 source as Zenodo record `8348039`: benchmark archive `iccma2023_benchmarks.zip`, size `851,774,875`, MD5 `f7382a5d5b8118253a9266d5465b5bed`, and results archive `iccma2023_results.zip`, size `448,400,865`, MD5 `bdb5e5008e7393f4b52cdb19f33012ec` (`tools/iccma_data.py:139-161`). The documentation identifies those two archive classes and the deterministic `archives/`, `extracted/`, and `manifests/` layout (`docs/iccma-data.md:17-18`, `docs/iccma-data.md:26-37`).

Both archives exist at `data/iccma/2023/archives/` with exactly those sizes. A current `Get-FileHash -Algorithm MD5` produced the two expected hashes, so these are verified local copies rather than merely declared download specs.

The local extracted/derived inventory is:

- `data/iccma/2023/extracted/instances/benchmarks/main/`: 329 parsed AF `.af` instances plus 329 `.arg` query sidecars. Manifest rows for these are `af/ok` and `query_or_updates/skipped`, respectively.
- `data/iccma/2023/extracted/instances/benchmarks/aba/`: 400 parsed ABA `.aba` instances plus 400 `.asm` sidecars. Manifest rows are `aba/ok` and `query_or_updates/skipped`.
- `data/iccma/2023/extracted/instances/benchmarks/dynamic/`: one `dynamic_track.py`, classified `dynamic_app/skipped`.
- `data/iccma/2023/extracted/results/results/`: 23 support/result artifacts, all classified `results/skipped`. They include five CSV result files, four plot scripts, four extraction scripts, four log zip files, four barplot PDFs, and two shell scripts; the exact names are recorded by the 23 `archive == "results"` manifest rows.
- `data/iccma/2023/manifests/iccma-2023-manifest.{json,csv}`: 1,482 rows total: 400 `aba/ok`, 329 `af/ok`, 1 `dynamic_app/skipped`, 729 `query_or_updates/skipped`, and 23 `results/skipped` (current `jq` aggregation shown above). The manifest writer's row schema and deterministic JSON/CSV output are in `tools/iccma_data.py:31-43` and `tools/iccma_data.py:318-335`.
- `data/iccma/2023/manifests/iccma-2023-task-matrix.{json,csv}`: local 27-row matrix: 10 main AF tasks, 7 heuristics AF tasks, 4 dynamic tasks, and 6 ABA tasks. For the first bottleneck slice, AF `DS-PR` is present in both main and heuristics (`data/iccma/2023/manifests/iccma-2023-task-matrix.json:23-28`, `:100-105`), while ABA `SE-PR` and `SE-ST` are present at `:177-189`.
- `data/iccma/2023/runs/`: 16 prior artifacts from five named historical runs (JSON, CSV, summary files, plus a progress JSONL for one run). These are evidence of prior runs, not a current baseline.

The data tool's manifest pass deliberately classifies query/update sidecars as skipped and never runs solvers (`docs/iccma-data.md:78-93`). The native runner independently filters jobs to normalized `af` and `aba` kinds, so the dynamic application is not exercised by this path (`tools/iccma2025_run_native.py:233-240`).

I did not verify the provenance or generator of the local 2023 task-matrix files. I verified their current contents. I also found no `tests/manifests/*2023*` frozen timeout/frontier manifest; all checked frontier/timeout manifests presently found under `tests/manifests/` are 2025-specific.

## Exact bounded baseline command

Run this first from the repository root:

```powershell
uv run tools\iccma2025_run_native.py --root data\iccma\2023 --backend native --max-af-arguments 100 --max-aba-assumptions 10 --timeout-seconds 5 --only-instance benchmarks/aba/aba_100_0.1_10_5_7.aba --only-subtrack SE-PR --only-subtrack SE-ST --jobs 1 --event-log-path data\iccma\2023\runs\iccma-2023-main-84cbb04-aba-se-first-slice-events.jsonl --label main-84cbb04-aba-se-first-slice
```

This exact command is accepted by the current CLI surface (`tools/iccma2025_run_native.py:100-160`; confirmed with `--help`). The runner discovers the single `iccma-*-manifest.json` and optional matching task matrix beneath the supplied root (`tools/iccma2025_run_native.py:292-304`), filters exact instance and subtrack names before constructing jobs (`tools/iccma2025_run_native.py:233-243`), and writes JSON, CSV, and summary artifacts under `<root>/runs/` (`tools/iccma2025_run_native.py:184-197`).

The target file currently exists, and its manifest record is `ok`: 100 atoms, 10 assumptions, 531 rules, and 10 contraries (`data/iccma/2023/manifests/iccma-2023-manifest.json:445-456`). This produces exactly two solver rows, ABA `SE-PR` and `SE-ST`. With `--jobs 1`, rows are serial and per-row elapsed values avoid parallel CPU-contention noise; the runner explicitly warns that `jobs > 1` adds that noise (`tools/iccma2025_run_native.py:198-202`). Each solver worker has a five-second outer wall-clock kill (`tools/iccma2025_run_native.py:555-600`), so the intended solver-row budget is at most 10 seconds, plus fixed process/startup/output overhead.

I did not execute this command. Therefore I did not verify current-main status, elapsed time, answers, or a total end-to-end wall clock.

## Why these tasks/families come first

The selection is based on the newest local 2023 result artifact, not on a fresh run. `data/iccma/2023/runs/iccma-2023-range-max-inclusion-cap100-summary.json:1-12` records 7,993 rows: 487 solved, 83 timeout, and 7,423 skipped. That artifact used `backend: auto`, predates the current merge, and is not a current baseline.

Within that historical artifact:

- ABA `SE-PR` and `SE-ST` are the only timeout groups: 42 and 41 timeouts, respectively (verified by current `jq` grouping). On the chosen in-cap instance, `SE-PR` took `4.531199s` and `SE-ST` took `4.468040s` (`data/iccma/2023/runs/iccma-2023-range-max-inclusion-cap100.json:2125-2161`). These two rows are near the proposed five-second cap and directly exercise preferred/stable single-extension paths.
- AF `DS-PR` was the slowest solved AF task on the chosen 100-argument instance: `2.862235s` in main and `2.947226s` in heuristics (current `jq` sort; the main row is at `data/iccma/2023/runs/iccma-2023-range-max-inclusion-cap100.json:118445-118461`). This exercises preferred skeptical acceptance and its SAT trace surface.

Accordingly, use this order:

1. ABA `SE-PR` and `SE-ST` on `aba_100_0.1_10_5_7.aba`.
2. AF `DS-PR` on `n100p3q34ve.af` in main and heuristics. The exact follow-up command is:

   ```powershell
   uv run tools\iccma2025_run_native.py --root data\iccma\2023 --backend native --max-af-arguments 100 --max-aba-assumptions 10 --timeout-seconds 5 --only-instance benchmarks/main/n100p3q34ve.af --only-subtrack DS-PR --jobs 1 --event-log-path data\iccma\2023\runs\iccma-2023-main-84cbb04-af-dspr-first-slice-events.jsonl --label main-84cbb04-af-dspr-first-slice
   ```

   The AF manifest row is `ok` with 100 arguments and 2,025 attacks (`data/iccma/2023/manifests/iccma-2023-manifest.json:15798-15809`). The task matrix contains main and heuristics `DS-PR`, so this produces two five-second-budget rows.
3. Only after obtaining current results and operational evidence, expand within the same task family to adjacent 100-atom/argument instances. Do not start with the full 7,993-row cross-product.

I did not verify that these remain the slowest rows on current `main`; the bounded command is the required refresh.

## Existing operational evidence surfaces

### Runner telemetry and bounds

`--event-log-path` is a direct JSONL sink. The runner logs run start, manifest/task loading, job count, row start, and row completion (`tools/iccma2025_run_native.py:207-244`, `:339-386`). Concurrent in-process writers are serialized by a lock (`:389-403`). For AF SAT work, each solver check emits `sat_check` with task identity, utility name, result, elapsed milliseconds, assumptions count, model size/fingerprint, loop index, learned count, and range-bound fields (`:918-969`). `SATCheck` itself is a frozen telemetry record (`src/argumentation/solving/af_sat.py:64-80`), and the runner sets an in-process Z3 check budget one second inside the outer worker timeout (`tools/iccma2025_run_native.py:857-870`).

This is enough to encode deterministic AF contracts such as bounded SAT-check count, required shortcut/utility selection, bounded loop index, or absence of an expensive utility before using wall clock.

### ABA deterministic telemetry and route contracts

`IncrementalTelemetry` exposes refinement clauses, outer/inner iterations, solver calls, clingo control arguments/statistics/grounding, assignment probes, timeout, and interruption state (`src/argumentation/structured/aba/aba_incremental.py:75-88`, `:346-364`, `:401-423`). Existing executable contracts already assert at most two solver calls and one outer iteration for a no-attack preferred case (`tests/test_performance_contracts.py:126-135`).

Structural ABA telemetry is deterministic and identity-free: atom/assumption/rule counts, rule-body width, fan-in/fan-out, ratios, rule and assumption dependency SCC counts/max sizes, and closure-growth probes (`src/argumentation/structured/aba/aba_telemetry.py:18-35`, `:39-70`). Its tests require identical output across repeated calls and reordered inputs (`tests/structured/aba/test_aba_structural_telemetry.py:101-131`).

More specific preferred-path contracts already exist:

- real PrefSat bounds solver checks, candidate models/blocks, clause growth, and forbids attacker-solver builds/checks (`tests/structured/aba/test_aba_real_prefsat_contract.py:198-213`, `:237-253`);
- decomposed PrefSat records original/residual sizes, component sizes/calls, full-instance calls, solver checks, and the no-reduction reason, with assertions that a reduced route avoids the full-instance call and shrinks component size (`tests/structured/aba/test_aba_decomposed_prefsat_contract.py:34-46`, `:263-279`);
- route tests require decisions to be invariant to file path, manifest order, atom renaming, and rule order (`tests/structured/aba/test_aba_route_properties.py:28-107`).

These satisfy the repository rule's deterministic route, solver-call, residual-size, and skipped-bad-path contract categories before a larger benchmark.

### Calibrated wall-clock contracts

`tools/perf_calibrate.py` measures Python loop, ABA parse/closure, and optional clingo/Z3 probes, recording repeat counts, elapsed and median seconds, machine data, and skip reasons (`tools/perf_calibrate.py:26-33`, `:61-88`, `:161-190`). Its CLI accepts `--output` and `--repeat` (`:193-213`). `tests/performance_contracts.py` reads `ARGUMENTATION_PERF_CALIBRATION`, derives a slowdown factor from reference medians, and scales fallback budgets (`tests/performance_contracts.py:11-26`, `:38-78`). Wall-clock enforcement is opt-in through `ARGUMENTATION_PERF_CONTRACTS` (`:29-35`), while deterministic contracts run normally (`tests/test_performance_contracts.py:119-179`).

### Profiler hook and actual worker boundary

Each row is executed in its own subprocess. The parent writes a temporary job JSON, launches `sys.executable tools/iccma2025_run_native.py _worker <job>`, waits for the configured row timeout, and kills that process on expiry (`tools/iccma2025_run_native.py:555-614`, `:676-697`, `:738-744`). Parallelism is only a parent-side `ThreadPoolExecutor` scheduling multiple independent worker subprocesses; job-order results are retained (`:248-279`).

`--profile-workers-dir` wraps selected workers with `uv tool run py-spy record --subprocesses`; optional `--profile-worker-subtrack` limits profiling, profile duration is kept one second inside the row timeout, and stable profile filenames include track/subtrack/instance identity plus a hash (`tools/iccma2025_run_native.py:126-140`, `:676-735`). Tests pin the `py-spy --subprocesses` command and the inside-timeout duration (`tests/interop/test_iccma_runner.py:361-376`, `:408-445`). This profiles the real worker/solver process rather than only the orchestration wrapper, satisfying `AGENTS.md:22-25`.

After the bounded baseline identifies a miss, rerun only that exact row with the same caps and timeout plus `--profile-workers-dir <dir> --profile-worker-subtrack <subtrack>`. I did not verify a current profile for either selected 2023 instance.

## Unknowns that remain after this research

- I did not run the proposed baseline, so current-main timing and route behavior are unknown.
- I did not verify that the local 2023 task matrix was produced from an official machine-readable source.
- I did not verify correctness against official 2023 result answers; this report only traces local assets and operational surfaces.
- I did not verify a frozen, checked 2023 frontier manifest because none was found.
- The historical `auto`-backend results are not comparable to the proposed pinned-`native` baseline. They justify target selection only.
