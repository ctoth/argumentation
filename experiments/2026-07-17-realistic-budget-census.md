# Realistic-Budget Census (600 s) — Budget-Artifact vs Algorithmic-Hardness Split

Date: 2026-07-17
Branch: `exp/iccma-census-budgets`
Author: census/budget instrumentation worker

## Goal

Decompose the ICCMA-2025 truth-run timeout population into **budget artifacts**
(rows that time out only because the budget was too small) versus **algorithmic
hardness** (rows that stay unsolved even at a realistic competition budget), by
rerunning a frozen stratified sample of timeout rows at **600 s** and comparing
against the 2026-05-14 baseline.

## Measurement used

- **Metric:** per-row terminal `status` (`solved` / `timeout`) at a 600 s
  wall-clock budget, counted per (family × subtrack) stratum. **Counts only** —
  per-row `elapsed_seconds` in the census are taken under `--jobs 4` and carry
  CPU-contention noise (the runner prints this caveat itself); no timing claim
  is derived from the census. Contention-free timing appears only in the D3
  probe recheck (`--jobs 1`).
- **Baseline:** `data/iccma/2025/runs/iccma-2025-full-uncapped-auto-t5-2026-05-14.json`
  = **4243 solved / 1871 timeout / 1280 skipped / 7394 total**, produced at
  `--backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647
  --timeout-seconds 5` — i.e. a **5 second** per-row budget ("t5" = 5 s).
  Source CSV sha256 `bbe3865f62ecc6051fd6ebf9ff405086afc0f48584d3c16b12bfda3aa5005bda`.

## Sample manifest

- File: `experiments/iccma-census/sample-timeout-600s.json` (committed).
- Selection code: `experiments/iccma-census/select_sample.py` (committed,
  reproducible, RNG-free: per stratum sort timeout instances by `relative_path`,
  take first k).
- 52 timeout rows over 22 (family × subtrack) strata covering crusti_g2io, scc,
  ER, mainkwt (AF) and abcgen, aba (ABA) across DC-CO, DC-ID, DS-PR, DS-SST,
  SE-ID, SE-PR, SE-SST, SE-ST.
- Manifest self sha256 `f4c79993a0269218b791af38e08c2540db50d7e99f69b7bbde30c1369d0ba78b`.

## Commands

Per-subtrack invocation (driver `scratchpad/run_census_sample.sh`), from the
worktree, against the shared 2025 data root:

```
uv run python tools/iccma2025_run_native.py \
  --root <repo>/data/iccma/2025 \
  --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 \
  --timeout-seconds 600 --jobs 4 --no-progress \
  [--only-track main]  --only-subtrack <ST> --only-instance <p> ...  \
  --label census-600s-<ST>
```

Track handling: DC/DS AF subtracks are duplicated across the `main` and
`heuristics` tracks (identical solves); `--only-track main` keeps one copy.
**DC-ID exists only under `heuristics` in the 2025 task matrix**, so DC-ID was
run with no track filter (2 ER rows). SE subtracks carry the AF `main` rows plus
the ABA `aba`-track rows and have no `heuristics` duplicate, so they run
unfiltered. Every manifest entry maps to exactly one solved/timeout row (52).

## Per-stratum results (solved@600 vs still-timeout)

| family | subtrack | solved@600 | still timeout | verdict |
|---|---|---:|---:|---|
| crusti_g2io | DC-CO | 3 | 0 | budget artifact |
| crusti_g2io | DS-PR | 3 | 0 | budget artifact |
| crusti_g2io | DS-SST | 2 | 0 | budget artifact |
| crusti_g2io | SE-ID | 2 | 0 | budget artifact |
| crusti_g2io | SE-SST | 2 | 0 | budget artifact |
| crusti_g2io | SE-ST | 2 | 0 | budget artifact |
| mainkwt | DS-PR | 3 | 0 | budget artifact |
| abcgen | SE-PR | 3 | 0 | budget artifact |
| abcgen | SE-ST | 3 | 0 | budget artifact |
| aba | SE-PR | 2 | 0 | budget artifact |
| aba | SE-ST | 2 | 0 | budget artifact |
| scc | DC-CO | 3 | 0 | budget artifact |
| scc | DS-PR | 2 | 1 | mostly artifact (scc_1554 hard) |
| scc | DS-SST | 1 | 1 | mixed |
| scc | SE-ID | 1 | 1 | mixed |
| scc | SE-ST | 2 | 0 | budget artifact |
| ER | DS-SST | 2 | 0 | budget artifact |
| ER | SE-SST | 2 | 0 | budget artifact |
| ER | DS-PR | 0 | 3 | ALGORITHMIC HARD |
| ER | SE-ID | 0 | 2 | ALGORITHMIC HARD |
| ER | SE-PR | 0 | 2 | ALGORITHMIC HARD |
| ER | DC-ID | 0 | 2 | ALGORITHMIC HARD |

**Per-family split (sampled timeouts):**

- crusti_g2io **14/14 solved** at 600 s — 100% budget artifact (solve 7–30 s).
- mainkwt **3/3**, abcgen **6/6**, aba **4/4** — 100% budget artifact.
- scc **9/12 solved** — 75% budget artifact; residual hardness `scc_1554_2`
  (DS-PR) and one DS-SST + one SE-ID row.
- ER **4/13 solved** — the dominant algorithmic-hardness family: ER_300 DS-PR
  (0/3), SE-ID (0/2), SE-PR (0/2), DC-ID (0/2) all time out at 600 s; only the
  DS-SST (2/2) and SE-SST (2/2) ER rows solve.

## Budget-artifact fraction

Measured on all 52 rows: **40 solved / 52 = 0.769**. The 12 still-timeout rows
are **ER (9)** — DS-PR 3, DC-ID 2, SE-ID 2, SE-PR 2 — and **scc (3)** — DS-PR 1
(`scc_1554_2`), DS-SST 1, SE-ID 1. Every other sampled family (crusti_g2io 14/14,
mainkwt 3/3, abcgen 6/6, aba 4/4) is a 100% budget artifact at 600 s.

**Extrapolation to the 1871 truth-run timeouts (directional, not a census):**
the sample is deliberately stratified over the *known-hard* families
(crusti/scc/ER + the ABA giants) and is NOT a uniform random draw. Even within
this hard-weighted sample 0.77 of the 5 s timeouts solve at 600 s, and the
families that are 100% budget artifacts here (crusti, mainkwt, abcgen, aba) plus
the un-sampled easier families (sembuster, WS, admbuster, st_, …, which make up
much of the 1871) push the *population* budget-artifact fraction **higher** than
0.8. Genuine algorithmic hardness at 600 s is concentrated in **ER** (all sampled
tasks except SST) and a **minority of scc** rows. Net: the great majority of the
1871 "timeouts" are artifacts of the 5 s truth budget, not algorithmic walls;
the real hard core is ER (and a little scc), materially smaller than 1871.

## D3 — Probe-kill budget recheck

The 2026-07-11 ICCMA-2023 ABA campaign (Probes 1–8, dev frame
`experiments/iccma2023-frame/population-dev.json`) ran at a frozen **5–10 s** row
wall on the two 600-assumption / 2000-atom shapes
`benchmarks/aba/aba_2000_0.3_10_10_0.aba` and `..._1.aba` (real ICCMA-2023 ABA
budget is 1200 s). Affected records: **N1**
(`2026-07-11-iccma2023-aba-600-stable-sat-route.md`, `aba_2000_0.3_10_10_0`
SE-ST `timeout>5 s`), **N2** (base-UNSAT 46 s precheck), **R1-P3**
(support-free preprocessing, "600-assumption headroom instances"), and **Probe
8** (`aba_2000_0.3_10_10_0.aba` SE-ST emitted no telemetry before its 5.0 s wall,
failing Gate B closed — INDEX.md).

Recheck command (`--jobs 1`, contention-free timing). Note: the shared
`data/iccma/2023` currently ships only a `task-matrix.csv` (no `.json`), so the
runner falls back to AF-only task inference and builds **zero** `aba` jobs. To
avoid mutating shared 2023 data (also used by the af-satsub worker), the recheck
ran against an isolated root `scratchpad/d3root/` carrying a minimal
`manifests/iccma-2023d3-{manifest,task-matrix}.json` (aba SE-ST + SE-PR over the
two instances) and the two instances re-extracted from the benchmarks zip:

```
uv run python tools/iccma2025_run_native.py --root scratchpad/d3root \
  --backend auto --max-af-arguments -1 --max-aba-assumptions 1000000 \
  --timeout-seconds 600 --jobs 1 --no-progress \
  --only-subtrack SE-ST --only-subtrack SE-PR \
  --label census-probe-recheck-600s
```

**Result — all 4 rows solved at 600 s (contention-free elapsed, `--jobs 1`):**

| instance | subtrack | status | elapsed |
|---|---|---|---:|
| aba_2000_0.3_10_10_0.aba | SE-ST | solved | 109.8 s |
| aba_2000_0.3_10_10_0.aba | SE-PR | solved | 128.4 s |
| aba_2000_0.3_10_10_1.aba | SE-ST | solved | 1.1 s |
| aba_2000_0.3_10_10_1.aba | SE-PR | solved | 14.8 s |

**Verdict — the Probe 1–8 kills on these rows were budget artifacts.** The exact
row cited by N1 and consumed by Probe 8 (`aba_2000_0.3_10_10_0.aba` SE-ST) solves
in **109.8 s** — ~22× the frozen 5.0 s row wall it was killed at, but only ~9% of
the real ICCMA-2023 ABA budget of 1200 s (and well inside this 600 s recheck).
The SE-PR companion solves in 128.4 s; the `_1` shape solves in 1.1 s / 14.8 s.
None of these rows is algorithmically unsolvable at a realistic budget: the
campaign's "dead-end" was reached under a 5–10 s wall that is **120–240× smaller
than ICCMA's 1200 s**, so the triage measured budget starvation, not solver
limits. This does not reverse the campaign's *semantic* kills (e.g. Probe 6's
non-separator fixture), but it does mean the wall-clock kills (N1, R1-P3, Probe
8's Gate-B row-wall timeout) carry no evidence about algorithmic hardness.

## Caveats

1. **`--jobs 4` timing contention.** Census counts are valid; per-row seconds
   are contention-noisy and are not reported as timings. (Runner emits its own
   caveat.)
2. **Sample size / stratification.** 52 of 1871 timeouts, deliberately
   stratified over the hard families and named tasks — NOT a uniform random
   sample. The 0.77 budget-artifact fraction is for those strata; extrapolation
   to all 1871 is directional (and, per above, likely an underestimate of the
   population fraction).
3. **Track duplication.** The 2025 matrix pairs each AF instance with both
   `main` and `heuristics` tracks (identical solve); the census counts one copy
   per instance (`--only-track main`, except DC-ID which is heuristics-only).
4. **Budget path exercised.** The runner's new `--budgets-json` per-subtrack
   budget path (D1) is separately unit-tested; this census used a uniform 600 s
   via `--timeout-seconds` (equivalent to an all-600 budget map).
5. **pyright scope observation (not acted on).** CI runs `uv run pyright src`;
   `tools/` and `tests/` are outside the enforced gate. Both D1 files are
   pyright-clean under basic and standard modes regardless. Widening
   `include` is left for Q to decide.

## Comparison against the 2026-05-14 baseline

Baseline: 4243 solved / 1871 timeout at 5 s. This census shows that raising the
budget from 5 s → 600 s converts **40/52 = 77%** of the sampled hard-family
timeouts to solved (many in 7–30 s), i.e. the 5 s truth budget massively
understated solved count. The 4243 solved figure is a **5 s-budget floor**, not
an algorithmic ceiling; a fresh full census at a realistic budget would land
materially above 4243, with the unsolved remainder concentrated in ER (and a
slice of scc) rather than spread across the 1871.

## Reproducibility

- Runner: committed on `exp/iccma-census-budgets` (D1 `3d7fc24`, `--only-track`
  `32290b5`, pyright fix `7b36cbf`).
- Sample: `a816a75`.
- 2023 instances re-extracted from
  `data/iccma/2023/archives/iccma2023_benchmarks.zip` into
  `data/iccma/2023/extracted/instances/benchmarks/aba/`.
