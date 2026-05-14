# ICCMA 2025 cap-150 — pre/post graph-speedup-workstream merge

**Date:** 2026-05-13
**Pre-merge tip:** `4a1c31c` ("grounded_extension: O(V+E) labelling; bipolar grounded computes the Cayrol closure once", 2026-05-12)
**Post-merge HEAD:** `76e6366` (`--no-ff` merge of `experiment/graph-speedup-wave-a-preprocessing`, 2026-05-13)

This replaces the earlier `aa14003` placeholder report ("no numbers, here's why") with real numbers from a fresh pre/post run.

## Invocation

Both sides identical except for the working directory and label:

```
python tools/iccma2025_run_native.py \
  --backend auto \
  --max-af-arguments 150 --max-aba-assumptions 150 \
  --timeout-seconds 5 \
  --label <premerge-…|postmerge-…> --no-progress
```

- Pre-merge ran from worktree `C:/Users/Q/code/argumentation-premerge` at `4a1c31c` (`pip install -e .` in that worktree active), with `--root C:/Users/Q/code/argumentation/data/iccma/2025`. Label `premerge-4a1c31c-cap150-auto-2026-05-13`.
- Post-merge ran on `main` worktree at `76e6366` (`pip install -e .` reinstalled there). Label `postmerge-76e6366-cap150-auto-2026-05-13`.

The `--backend native` runs I initially tried error out at the brute-force 65536-subset cap on any instance larger than ~16 args — that backend is the Python reference enumerator, not the workstream's SAT/ASP path. The workstream's speedups live on `--backend auto`.

## Headline

| | pre `4a1c31c` | post `76e6366` | Δ |
|---|---:|---:|---:|
| solved | 833 | **843** | **+10** |
| timeout | 12 | **2** | **−10** |
| skipped | 6549 | 6549 | 0 |
| total rows | 7394 | 7394 | 0 |

Of 845 actually-runnable rows (i.e. excluding `--max-*` skips), the workstream takes timeouts from 12 to 2 — an **83% reduction in timeouts**, all of it on the ABA side.

## Per task family

```
TRACK       TASK     pre_S pre_T post_S post_T   ΔS   ΔT
aba         SE-PR       28    12     39      1  +11  -11   <-- WIN
aba         SE-ST       40     0     39      1   -1   +1   <-- one regression
heuristics  DC-CO       45     0     45      0    0    0
heuristics  DC-ID       45     0     45      0    0    0
heuristics  DC-SST      45     0     45      0    0    0
heuristics  DC-ST       45     0     45      0    0    0
heuristics  DS-PR       45     0     45      0    0    0
heuristics  DS-SST      45     0     45      0    0    0
heuristics  DS-ST       45     0     45      0    0    0
main        DC-CO       45     0     45      0    0    0
main        DC-SST      45     0     45      0    0    0
main        DC-ST       45     0     45      0    0    0
main        DS-PR       45     0     45      0    0    0
main        DS-SST      45     0     45      0    0    0
main        DS-ST       45     0     45      0    0    0
main        SE-ID       45     0     45      0    0    0
main        SE-PR       45     0     45      0    0    0
main        SE-SST      45     0     45      0    0    0
main        SE-ST       45     0     45      0    0    0
```

### Reading

- **ABA SE-PR is where the workstream lands.** 11 of 12 previously-timing-out SE-PR instances now solve in under 5s. This is Wave C2b's clingo multi-shot CEGAR (`AbaIncrementalSolver` running Algorithm 1 from Lehtonen–Wallner–Järvisalo TPLP 2021) doing what it was built to do: it replaces the subprocess-clingo enumerate-then-filter path that timed these out previously.
- **Every AF task family is unchanged at 45/45/0.** At cap-150 with `--timeout-seconds 5`, all AF instances passing the size filter were already solving within budget on `4a1c31c`. So Wave A (grounded reduct + structural reductions) and Wave B (SCC-recursive complete/preferred/stable) don't show up on this corpus / this cap — they would only register if (a) the cap let in instances large enough to time out, or (b) the timeout were tighter. The synthetic benches that produced 2–13×, 13–450×, and ~99× DS-PR numbers were specifically constructed to exercise those structures; the ICCMA 2025 corpus at cap-150 doesn't include AF instances where those structures cost ≥5s on the old path.
- **One regression: `aba_500_0.3_5_5_3.aba`** — was solved pre-merge on both SE-PR and SE-ST in some sub-5s time, now times out on both. This is a P2 finding; the workstream is net positive but this instance specifically got worse. Worth a follow-up to characterize whether it's a multi-shot CEGAR pathology (refinement-clause blow-up) or interaction with `simplify_aba`'s preprocessing.

### Newly-solved (12 instances, all ABA SE-PR)

```
ABAs/aba_100_0.1_10_10_9.aba
ABAs/aba_100_0.3_10_5_5.aba
ABAs/aba_100_0.3_10_5_7.aba
ABAs/aba_100_0.3_5_10_3.aba
ABAs/aba_500_0.1_10_5_2.aba
ABAs/aba_500_0.3_10_10_1.aba
ABAs/aba_500_0.3_10_10_7.aba
ABAs/aba_500_0.3_10_10_9.aba
ABAs/aba_500_0.3_5_10_1.aba
ABAs/aba_500_0.3_5_10_4.aba
ABAs/aba_500_0.3_5_5_2.aba
ABAs/aba_500_0.3_5_5_5.aba
```

### New timeouts / regressions (2 rows, 1 instance)

```
aba/SE-PR: ABAs/aba_500_0.3_5_5_3.aba   (pre: solved, post: timeout)
aba/SE-ST: ABAs/aba_500_0.3_5_5_3.aba   (pre: solved, post: timeout)
```

## What this means for the workstream claims

Real, modest, in the direction predicted by the design. The workstream's synthetic benches predicted big wins on layered AFs and ABA refinement-heavy DS-PR; the ICCMA cap-150 corpus mostly tests instances where the AF speedups have no headroom (already <5s) and gives us only the ABA-SE-PR axis to see speedups on. On that axis the picture is clean: a near-elimination of timeouts on the family the multi-shot CEGAR was designed for, at the cost of one regression to characterize.

## Caveats

- 5-second timeout is the standard cap-150 cell; a longer timeout would likely surface AF DS-PR wins for instances at the cap that are currently solving in the 1–5s range on both sides. Not run here.
- The recorded `iccma-2025-post-workstreams-cap150-summary.json` (833/12, 2026-05-10, commit `c4d2819`) matches this fresh pre-merge run exactly — confirming the solver's `auto`-backend behavior was stable across the 30+ commits between `c4d2819` and `4a1c31c`. So that baseline could have been used (had backend matched) and would have given identical numbers. Future runs can lean on the recorded snapshot at this cap.
- Cap-200 not run here. Q's most recent cap-200 baseline is `full-cap200-after-aba-kernel-20260512` (1361/7); a fresh cap-200 run on `76e6366` would show whether the same +N-solved / −N-timeout pattern extends to larger instances. Not in this report.
- Only one regression found, but it's reproducible (same instance on both SE-PR and SE-ST) — that's almost certainly a workstream-introduced bug or pessimization on this specific framework shape. Follow-up wave should reproduce it on the pre-merge tree, run it on the post-merge tree with `simplify=False` to isolate preprocessing-vs-multi-shot, then characterize.

## Output files

```
data/iccma/2025/runs/iccma-2025-premerge-4a1c31c-cap150-auto-2026-05-13.{csv,json,-summary.json}
data/iccma/2025/runs/iccma-2025-postmerge-76e6366-cap150-auto-2026-05-13.{csv,json,-summary.json}
data/iccma/2025/runs/premerge-4a1c31c-cap150-auto-2026-05-13.run.log
data/iccma/2025/runs/postmerge-76e6366-cap150-auto-2026-05-13.run.log
```

The earlier `--backend native` runs (`iccma-2025-premerge-4a1c31c-cap150-2026-05-13.*`, 0 solved / 554 timeout / 291 ExactEnumerationExceeded errors) are kept for context but document only the brute-force reference enumerator and are not the workstream comparison.
