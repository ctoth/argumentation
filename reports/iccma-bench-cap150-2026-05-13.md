# ICCMA cap-150 pre/post-merge bench — 2026-05-13

## TL;DR

Both planned cap-150 runs were killed externally before producing any row output. No
solved/timeout/skipped numbers can be reported for this commit pair. The pre-merge
reference selection logic and the operational facts (worktree, commit ancestry,
existing-baseline backend mismatch) were verified before the runs; what failed is the
execution of the bench itself, not the planning.

**No before/after comparison is available.** This document records what was
attempted, what was observed, and what would need to change to finish the job.

## What was being compared

- **Pre-merge tip**: `4a1c31cc45a2a4a67b45a72941812e1098ba7018` — "grounded_extension: O(V+E)
  labelling; bipolar grounded computes the Cayrol closure once", committed 2026-05-12 14:53 -0600.
- **Post-merge HEAD**: `76e63664fc88f5e39315655cc2dc462ddb51432e` — "Merge graph-theory
  speedup workstream", committed 2026-05-13 11:04 -0600 (see `reports/merge-graph-speedup-2026-05-13.md`).
- **Invocation under test** (cap-150, native backend, 5 s/row):
  ```
  uv run tools\iccma2025_run_native.py --backend native \
    --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5 \
    --label <unique> --no-progress
  ```

## Pre-merge reference selection

### Existing on-disk cap-150 baselines (`data/iccma/2025/runs/`)

| Label                       | File mtime          | Solved | Timeout | Skipped | Backend |
| --------------------------- | ------------------- | -----: | ------: | ------: | ------- |
| `current-cap150`            | 2026-05-09 20:36    |    808 |      37 |    6549 | auto    |
| `post-aba-stable-cap150`    | 2026-05-09 21:14    |    829 |      16 |    6549 | auto    |
| `post-workstreams-cap150`   | 2026-05-10 01:54    |    833 |      12 |    6549 | auto    |

`post-workstreams-cap150` is the strongest candidate by recency: ~2.5 days older than
`4a1c31c`, well inside the 7-day window. The commit it was most likely run on is
`c4d2819` (the latest commit before its mtime, 2026-05-10 01:39). `git merge-base
--is-ancestor c4d2819 4a1c31c` returned 0 — it **is** an ancestor of the pre-merge tip.

### Reason this baseline was rejected

All three on-disk baselines were run with `--backend auto`, verified via the `backend`
column of `iccma-2025-post-workstreams-cap150.csv` (single distinct value: `auto`).
The post-merge invocation specified in the bench prompt pins `--backend native`, and
the recon report (`reports/iccma-bench-recon-2026-05-13.md`) explicitly warns: "Pin to
`--backend native` for a deterministic pre/post comparison." Comparing an `auto`
baseline against a `native` post-merge run risks misattributing backend-selection
differences to the merge.

→ Fresh pre-merge run on `4a1c31c` in a separate worktree was required.

## Runs attempted

Both runs were launched from this session as detached background bash tasks.

### Post-merge attempt — `postmerge-76e6366-cap150-2026-05-13`

- Started: 2026-05-13 12:24:46 -0600 on the main worktree (commit `76e6366`).
- Stdout last event recorded: `{"event": "iccma_jobs_built", "jobs": 7394}` — runner
  reached the job-dispatch step.
- Outcome: harness reported `status: killed` for the background task. No row events
  were emitted (`--no-progress` suppresses them anyway) and no
  `data/iccma/2025/runs/iccma-2025-postmerge-76e6366-cap150-2026-05-13.{json,csv,summary.json}`
  artifact was written. Disk inspection after the kill confirmed absence.

### Pre-merge attempt — `premerge-4a1c31c-cap150-2026-05-13`

- Worktree created: `git worktree add ../argumentation-premerge 4a1c31c` succeeded
  (detached HEAD at `4a1c31c`). The worktree's `data/` directory was empty
  (`data/` is in `.gitignore`), so the run was launched with
  `--root C:/Users/Q/code/argumentation/data/iccma/2025` so the runner used the
  populated corpus from the main checkout.
- `uv run` in the worktree built `formal-argumentation` into a fresh `.venv` and
  installed 18 packages — startup completed cleanly.
- Started: 2026-05-13 13:25:16 -0600.
- Stdout last event recorded: `{"event": "iccma_jobs_built", "jobs": 7394}`.
- Outcome: identical to the post-merge attempt. Harness reported `status: killed`.
  No row events, no artifacts on disk.

## Wall-clock numbers

Neither run produced an `elapsed_seconds` total. Both were killed before any of the
7394 rows were dispatched to a worker subprocess. The wall-clock from runner-start to
kill is upper-bounded by the harness's background-task lifecycle, not by the bench
itself.

## What is not in this report (and why)

- **Per-task-family before/after table**: not produced — no completed runs.
- **Newly-solved instances**: cannot enumerate — no post-merge row data.
- **Newly-regressed instances**: cannot enumerate — neither side has row data
  produced under matched conditions.
- **Total solved / timeouts / skipped per side**: only known for `auto`-backend
  baselines (recorded above), not for the `native`-backend pre/post pair the prompt
  asked for.

## Caveats and observations

1. The kill cause was not verified at runtime; both background tasks ended with the
   harness `killed` status rather than a runner exception, an OS OOM message, or an
   exit code from `tools/iccma2025_run_native.py`. Without that, I will not state a
   cause.
2. The runner itself reached `iccma_jobs_built` in both attempts, so the configuration
   (root path, backend, manifest, task matrix) was acceptable to the runner. The
   failure surface is between the runner and the surrounding background-task
   plumbing.
3. Per the bench prompt's hard stop ("If a run errors out, capture stderr, STOP,
   report — don't loop retry"), I did not start a third attempt.
4. The `post-workstreams-cap150` snapshot remains the most recent on-disk cap-150
   baseline. If a backend-comparable comparison is acceptable using `--backend auto`,
   that baseline is `c4d2819`-era and still valid as a reference; this report does
   not produce that comparison because the bench prompt requested `native`.

## Worktree state

```
$ git worktree list
C:/Users/Q/code/argumentation  76e6366 [main]
```

The `../argumentation-premerge` worktree was removed via `git worktree remove` after
the second kill. Verified — only the main worktree remains.

## Commit policy

This report is committed to `main`. No corpus files (`data/iccma/2025/runs/*`) are
included in the commit because no run artifacts were produced.

## Reproduction notes for a follow-up

To complete this bench in a follow-up session:

1. On the main worktree at `76e6366`:
   ```
   uv run tools\iccma2025_run_native.py --backend native --max-af-arguments 150 \
     --max-aba-assumptions 150 --timeout-seconds 5 \
     --label postmerge-76e6366-cap150-2026-05-13 --no-progress
   ```
2. In a fresh worktree at `4a1c31c`, with the corpus accessed via `--root`:
   ```
   git worktree add ../argumentation-premerge 4a1c31c
   cd ../argumentation-premerge
   uv run --project . tools\iccma2025_run_native.py \
     --root C:\Users\Q\code\argumentation\data\iccma\2025 \
     --backend native --max-af-arguments 150 --max-aba-assumptions 150 \
     --timeout-seconds 5 --label premerge-4a1c31c-cap150-2026-05-13 --no-progress
   ```
3. Compare `iccma-2025-premerge-4a1c31c-cap150-2026-05-13.csv` against
   `iccma-2025-postmerge-76e6366-cap150-2026-05-13.csv`. Both runs need to complete
   and write `*-summary.json` for the diff to be meaningful.
4. Remove the worktree at the end.
