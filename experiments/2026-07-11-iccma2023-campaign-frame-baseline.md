# ICCMA 2023 Campaign Frame — Baseline

Date: 2026-07-11

Status: campaign-frame baseline measured on `main`. This is the committed noise
floor every future candidate is judged against. No solver change was made.

This is the **Frame** deliverable of the campaign protocol
(`/protocols:campaign`, phase 1). It is not a hypothesis test: it defines the
goal metric, freezes the population and holdout, and records the baseline.
Candidate hypotheses run the experiment protocol against this frame.

## Primary metric (frozen)

- **Metric:** count of `solved` rows over the frozen **development population**
  (`experiments/iccma2023-frame/population-dev.json`, 24 rows), fail-closed:
  only `status == "solved"` counts; `timeout` / `skipped` / `solver_error` /
  `protocol_error` / crash / unparseable = not solved. Direction: **maximize**.
  This is an ICCMA performance outcome (instances solved within a fixed budget),
  not semantic correctness — witnesses are recorded but validated out-of-band
  per experiment; the metric alone never rewards a wrong-but-fast answer.
- **Exact command** (per-row budget calibrated to **10 s**, see Calibration):

  ```
  uv run tools/iccma2025_run_native.py \
    --root data/iccma/2023 --backend auto \
    --max-af-arguments -1 --max-aba-assumptions 1000000 \
    --timeout-seconds 10 \
    <--only-instance ...×12 from population-dev.json...> \
    --only-subtrack SE-ST --only-subtrack SE-PR \
    --jobs 1 --label <branch-commit>-frame-dev-<n> --no-progress
  ```

  (`--jobs 1` is mandatory: the runner injects CPU-contention noise into elapsed
  times at `--jobs > 1`. `--max-aba-assumptions -1` would skip every ABA row —
  use `1000000`. `--max-af-arguments -1` disables the AF cap, harmless here.)

- **Evaluator paths + hashes** (pinned at commit `5f75a7c`; a non-empty diff of
  any of these at promotion time is an automatic no-go):
  - runner `tools/iccma2025_run_native.py` — blob `4c1c7d35cd2028fa6ce93c8091ab0fbc1054d9b5`
  - route contract `tests/structured/aba/test_aba_sparse_narrow_route_contract.py` — blob `fa52706224ee546416704c9c966a8fd91893dda0`
  - perf contracts `tests/performance_contracts.py` — blob `0ed6a8e4cdb77c538c1f6890e95e876b3bb177dc`
  - population: `experiments/iccma2023-frame/population-dev.json` (committed here)
  - corpus: gitignored, Zenodo `8348039`, MD5-verified
    (`docs/reports/iccma2023-repo-research-2026-07-11.md:19-30`)

## Operational contract (AGENTS.md gate) — verified

AGENTS.md requires an executable operational contract that can fail *before* the
full benchmark. The **shape-based route contract** already exists and is
verified for this frame:

```
uv run pytest -q \
  tests/structured/aba/test_aba_sparse_narrow_route_contract.py \
  tests/test_performance_contracts.py \
  tests/solving/test_solver_availability.py
→ 56 passed, 1 skipped in 1.70s
```

- The route contract (8 tests) runs **normally**, is a pure function of
  framework *shape*, and **rejects locator metadata** (path/label/year/instance
  keys forbidden). This is the deterministic route contract AGENTS.md requires.
- The 1 skip is the **opt-in** wall-clock contract (`ARGUMENTATION_PERF_CONTRACTS=1`),
  correctly gated per AGENTS.md ("wall-clock contracts must be opt-in or
  calibrated").
- **Verdict:** the operational contract satisfies AGENTS.md. No gap; no solver
  change needed. Any candidate that changes ABA routing must extend this
  contract with a shape predicate that fails on baseline and passes only on its
  measured shape (per the sat-route record's standing requirement).

## Calibration (per-row budget)

Short observation before fixing the budget (backend auto, `--jobs 1`):

| Instance (SE-ST unless noted) | assumptions | status | elapsed |
|---|---|---|---|
| aba_100_0.1_10_10_0 | 10 | solved | 0.32 s |
| aba_2000_0.1_10_10_0 | 200 | solved | 1.60 s |
| aba_2000_0.3_10_10_0 | 600 | timeout | 20.01 s (cap) |
| aba_100_0.1_10_10_0 (SE-PR) | 10 | solved | 0.29 s |
| aba_500_0.3_10_10_0 (SE-PR) | 150 | solved | 0.50 s |
| aba_2000_0.1_10_10_0 (SE-PR) | 200 | solved | 1.57 s |

Slowest observed *solved* row ≈ 1.6 s. **Calibrated budget T = 10 s** — ~6×
slack over the slowest solved row, so no solvable instance is falsely killed,
while the hard 600-assumption shape (needs ≫ 20 s) caps at 10 s. Modest slack,
bounded run.

## Baseline result

- Command: as above, `--timeout-seconds 10`, labels
  `frame-dev-baseline-run{1,2,3}-2026-07-11`.
- **Primary metric = 21 solved / 24, IDENTICAL across all 3 repeats.**
- Status is perfectly **paired**: the same 24 (instance, subtrack) rows carry
  the same status in every run (24 distinct row→status pairs). The three
  non-solved rows every run:
  - `aba_2000_0.3_10_10_0.aba` SE-ST — timeout
  - `aba_2000_0.3_10_10_0.aba` SE-PR — timeout
  - `aba_2000_0.3_10_10_1.aba` SE-PR — timeout
  - (`aba_2000_0.3_10_10_1.aba` SE-ST *solved* in ~1.2 s — the sole 600-stratum
    row that fits the budget; the campaign's headroom is the other three.)

Per-row elapsed (seconds), all 24 rows, three runs:

| instance | subtrack | status | run1 | run2 | run3 |
|---|---|---|---|---|---|
| aba_100_0.1_10_10_0.aba | SE-PR | solved | 0.299 | 0.306 | 0.298 |
| aba_100_0.1_10_10_1.aba | SE-PR | solved | 0.289 | 0.324 | 0.284 |
| aba_100_0.3_10_10_0.aba | SE-PR | solved | 0.293 | 0.356 | 0.280 |
| aba_100_0.3_10_10_1.aba | SE-PR | solved | 0.281 | 0.308 | 0.277 |
| aba_2000_0.1_10_10_0.aba | SE-PR | solved | 1.528 | 1.601 | 1.562 |
| aba_2000_0.1_10_10_1.aba | SE-PR | solved | 1.648 | 1.541 | 1.594 |
| aba_2000_0.3_10_10_0.aba | SE-PR | timeout | 10.011 | 10.026 | 10.020 |
| aba_2000_0.3_10_10_1.aba | SE-PR | timeout | 10.009 | 10.013 | 10.023 |
| aba_500_0.1_10_10_0.aba | SE-PR | solved | 0.542 | 0.553 | 0.546 |
| aba_500_0.1_10_10_1.aba | SE-PR | solved | 0.545 | 0.536 | 0.528 |
| aba_500_0.3_10_10_0.aba | SE-PR | solved | 0.513 | 0.593 | 0.494 |
| aba_500_0.3_10_10_1.aba | SE-PR | solved | 0.608 | 0.597 | 0.561 |
| aba_100_0.1_10_10_0.aba | SE-ST | solved | 0.298 | 0.334 | 0.299 |
| aba_100_0.1_10_10_1.aba | SE-ST | solved | 0.289 | 0.343 | 0.284 |
| aba_100_0.3_10_10_0.aba | SE-ST | solved | 0.277 | 0.310 | 0.275 |
| aba_100_0.3_10_10_1.aba | SE-ST | solved | 0.278 | 0.314 | 0.283 |
| aba_2000_0.1_10_10_0.aba | SE-ST | solved | 1.676 | 1.535 | 1.538 |
| aba_2000_0.1_10_10_1.aba | SE-ST | solved | 1.674 | 1.615 | 1.594 |
| aba_2000_0.3_10_10_0.aba | SE-ST | timeout | 10.011 | 10.025 | 10.019 |
| aba_2000_0.3_10_10_1.aba | SE-ST | solved | 1.224 | 1.210 | 1.197 |
| aba_500_0.1_10_10_0.aba | SE-ST | solved | 0.561 | 0.543 | 0.548 |
| aba_500_0.1_10_10_1.aba | SE-ST | solved | 0.521 | 0.531 | 0.508 |
| aba_500_0.3_10_10_0.aba | SE-ST | solved | 0.520 | 0.569 | 0.464 |
| aba_500_0.3_10_10_1.aba | SE-ST | solved | 0.582 | 0.528 | 0.537 |

Wall-clock on the 21 solved rows (per run): median ≈ 0.51 / 0.54 / 0.51 s;
max ≈ 1.68 / 1.62 / 1.59 s; sum ≈ 14.45 / 14.55 / 13.95 s. Total wall per full
24-row run ≈ 44.5 / 44.6 / 44.0 s.

## Determinism / noise rule (honest, no invented seed statistics)

- **The harness has no RNG seed.** The solving path is deterministic given a
  fixed instance + backend; witnesses use `natural_key` canonical ordering, so
  the metric is **`PYTHONHASHSEED`-independent by construction** — I did not
  fabricate per-seed metric variation that does not exist. (The repo's
  `scripts/run_hashseed_matrix.py` hash-seed sweep targets ordering-sensitive
  *tests*, not this throughput metric, so it does not change the metric
  decision and was not run here.)
- **Solved-count is deterministic:** 21/21/21 across three repeats, identical
  paired statuses. The only noisy quantity is wall-clock elapsed.
- **Boundary-stability:** every solved row finishes ≥ 8 s below the 10 s budget
  and every timeout row needs ≫ 10 s, so wall-clock noise (observed ≤ ~0.08 s
  run-to-run) cannot flip a row between `solved` and `timeout`. The metric is
  therefore boundary-stable at T = 10 s.
- **Noise rule for candidates:** a candidate improvement is real only if it
  **increases the paired solved-count** on the dev population (Δ ≥ +1 solved
  row that was a baseline timeout), measured with the same command, same rows,
  `--jobs 1`. Wall-clock speedups on already-solved rows are exploratory, never
  the promotion metric (they do not change ICCMA score and sit inside the wall
  noise). Minimum meaningful effect: **+1 solved row on dev, confirmed on the
  sealed holdout at promotion.**

## Holdout — sealed

`experiments/iccma2023-frame/population-holdout.json` (24 disjoint rows) was
**not run**. The campaign protocol does not require a pre-candidate holdout
baseline, so none was measured; the holdout is untouched until a verifier runs
it once at promotion.

## Provenance

- Code commit: `5f75a7cdd96f7f08b4665fb3772d60cf650d835c` (`main`, clean).
- Harness blob: `4c1c7d35cd2028fa6ce93c8091ab0fbc1054d9b5`.
- Corpus: Zenodo `8348039`, MD5-verified local, gitignored (`.gitignore:7`).
- Environment: Windows 11 (MINGW64_NT-10.0-26200), `uv run`, single process,
  `--jobs 1`.
- Raw run artifacts (gitignored, per repo convention — the committed record is
  this markdown, which quotes command, commit, statuses, and elapsed):
  `data/iccma/2023/runs/iccma-2023-frame-dev-baseline-run{1,2,3}-2026-07-11.{json,csv,summary.json}`
  and the calibration runs `iccma-2023-calib-{sest,sepr}-2026-07-11.*`.

Outcome: baseline established. Metric = **21/24 solved**, deterministic, at
`5f75a7c`. Frame ready for candidate triage.
