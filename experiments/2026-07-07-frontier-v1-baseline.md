# frontier-v1: frozen pass-rate manifest + main baseline

Date: 2026-07-07
Branch: exp/frontier-manifest-v1 (from main@57da538)
Manifest: tests/manifests/iccma2025-frontier-v1.json (30 rows)

## What this freezes

The recalibration campaign (2026-07-01) took the 2025 uncapped run's timeout
rows and drew a stratified 30-cell sample over (family x subtrack) cells,
keyed by (relative_path, subtrack) — instances recur across subtracks. Each
cell was rerun at 60s and at 120s. The outcome becomes the campaign's frozen
frontier metric: a small, fixed replay set whose per-class pass rate tracks
whether solver changes move the timeout frontier.

**Caveat: this samples 30 of the 1,871 timeout rows** in the 2025 uncapped
run. It is a stratified probe of the frontier, not a census; family-level
conclusions beyond the sampled cells need the full timeout corpus.

## Sample provenance

- Source rows: 2025 uncapped run timeout rows (timeout@15s), stratified by
  (family x subtrack); sample file `recal-sample.json` (campaign scratchpad).
- Recal runs: `data/iccma/2025/runs/iccma-2025-timeout-recal-60s-20260701-*.json`
  and `...-timeout-recal-120s-20260701-*.json` (per-subtrack chunks,
  `--backend auto`, uncapped sizes). Cells that solved at 60s were not rerun
  at 120s.
- Manifest built by `scripts/build_frontier_v1_manifest.py` from the sample
  plus both recal run sets; each row records the 60s/120s statuses and
  elapsed times it was classified from, and the instance file's sha256.

## Class definitions

| class | rows | definition |
|---|---|---|
| hard | 21 | still timeout at 120s |
| boundary_melt | 4 | timeout at 60s, solved at 120s budget (includes the flaky boundary row aba_2000_0.3_10_10_4 SE-PR, solved in 47.9s under the 120s run but timeout under the 60s run) |
| melt | 5 | solved within the 60s budget |

boundary_melt rows: crusti_g2io_125_0.5_31_17 DC-CO (63.0s),
scc_1554_2_0.4_0.2_3 DC-CO (78.0s), ER_200_20_3 DS-SST (79.6s),
aba_2000_0.3_10_10_4 SE-PR (47.9s, flaky).

melt rows: mainkwt_250_100_50_100_100_..._5 DS-PR (19.7s),
mainkwt_250_150_75_100_200_..._5 DS-PR (6.7s),
mainkwt_250_150_75_150_200_..._4 DS-PR (17.1s), ER_500_100_5 DS-SST (28.5s),
crusti_g2io_125_0.5_31_17 DS-ST (59.7s).

## Rerun command

One command runs exactly the 30 manifest rows at 120s, uncapped, auto
backend, and emits solved/timeout per class plus deviations:

```
uv run scripts/run_frontier_v1.py \
    --label frontier-v1-<tag> \
    --root C:/Users/Q/code/argumentation/data/iccma/2025 \
    --timeout-seconds 120 --backend auto
```

Chunk with repeated `--subtrack <SUB>` (each chunk writes its own output
file), then combine: `uv run scripts/run_frontier_v1.py --aggregate
<chunk-outputs...>`. Outputs land in `data/iccma/2025/runs/` under the repo
the script lives in (gitignored).

## Baseline on main@57da538

Label: `frontier-v1-main-57da538`. Run as sequential background chunks
(DS-PR | DC-CO+DS-ST | DS-SST | SE-PR | SE-ST), 120s timeout, backend auto,
uncapped, against `C:/Users/Q/code/argumentation/data/iccma/2025`. (A
combined DS-SST+SE-PR+SE-ST chunk died with exit 127 after 6 rows during an
infrastructure outage — its 6 completed rows all matched expectations — and
was rerun as three per-subtrack chunks, all exit 0.)

| class | rows | solved | timeout | pass rate |
|---|---|---|---|---|
| hard | 21 | 0 | 21 | 0/21 |
| boundary_melt | 4 | 4 | 0 | 4/4 |
| melt | 5 | 5 | 0 | 5/5 |
| **total** | **30** | **9** | **21** | **9/30** |

Deviations vs recal expectations: **none** (aggregate `deviations: []`).
Every hard cell timed out at 120s; every boundary_melt and melt cell solved,
including the flagged flaky boundary row aba_2000_0.3_10_10_4 SE-PR, which
solved on both baseline attempts. The AF Z3 check-budget change (105b518,
landed between recal and baseline) did not move any sampled cell across the
solved/timeout boundary.

Per-row outputs: `data/iccma/2025/runs/iccma-2025-frontier-v1-main-57da538-
{DS-PR,DC-CO-DS-ST,DS-SST,SE-PR,SE-ST}.json` under the experiment worktree
(gitignored; the replay driver records status/answer per row, not elapsed —
the frozen recal elapsed times live in the manifest rows).

## Notes

- Main moved between the recal runs (2026-07-01) and this baseline: the AF
  Z3 check-budget change (105b518) landed in between, so small deviations vs
  the recal expectations are informative signal about that change, not
  harness noise.
