# ICCMA 2023 Campaign Frame Worker — working state

Role: `ward set experiment` (accepted, `phase → experiment`). Direct Claude CLI.
Slice: campaign framing + baseline + one atomic commit. NO solver changes.

## Established facts
- Branch `main` clean @ `5f75a7c`; == origin/main. No tracked changes.
- `experiments/INDEX.md` does NOT exist yet — I must create the ledger.
- 2023 population: 400 `.aba` + 329 `.af` instances under
  `data/iccma/2023/extracted/instances/benchmarks/{aba,main}/`.
- Manifest: `data/iccma/2023/manifests/iccma-2023-manifest.json` — objects with
  `relative_path` like `benchmarks/aba/aba_100_0.1_10_10_0.aba`, `kind` in
  {aba, af, query_or_updates, ...}, `parse_status` ok/skipped.
- Harness: `tools/iccma2025_run_native.py`, `uv run`, `--jobs 1`, per-row wall
  timeout. Only injected noise = `--jobs>1` CPU contention. No RNG seed;
  deterministic witness ordering. `--max-aba-assumptions -1` skips ALL aba rows
  (no >=0 guard) — use 1000000. `--max-af-arguments -1` disables AF cap.
- Existing 2023 experiment records (committed baselines, both NEGATIVE):
  - `experiments/2026-07-11-iccma2023-aba-600-stable-sat-route.md`
  - `experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md`
  - + diagnostic `experiments/2026-06-29-iccma-uncapped-aba-dcco-profile.md`
- 47-commit DC-CO branch `exp/iccma-aba-dcco-100ba-acyc` (tip f21c22f) is
  UNMERGED unpromoted evidence — ledger must name it as such.
- Operational-contract test surface already exists (benchmark scout §8):
  - `tests/structured/aba/test_aba_sparse_narrow_route_contract.py`
  - `tests/test_performance_contracts.py`
  - `tests/solving/test_solver_availability.py`
- `python -c` is ward-blocked (no bare Python — good, matches AGENTS.md).

## Plan
1. Author committed repo-local partition artifacts: deterministic dev population
   + disjoint sealed holdout (instance identities recorded).
2. Define ONE primary metric + exact command (solved-count / wall outcome, not
   semantics alone).
3. Verify existing operational contract via targeted pytest. If it fails
   AGENTS.md, STOP + report gap (no solver change).
4. Measure baseline via authoritative harness `--jobs 1`, `uv run`, calibrated
   timeout from short observation. Record per-run, median, spread, noise rule.
5. Write `experiments/INDEX.md` ledger reconciling prior records + DC-CO branch.
6. Write worker report `reports/iccma-campaign-frame-worker-20260711.md`.
7. ONE atomic commit of frame + manifests + baseline record (+ report if ledger
   convention). Do not push. Preserve unrelated untracked files.

## BASELINE MEASURED (done)
- Calibrated per-row budget T = 10s (slowest observed solved row ~1.6s; ~6x slack).
- Contract triple PASSES: 56 passed, 1 skipped (opt-in wall-clock contract).
  Route contract = 8 tests run normally, shape-based, rejects locator metadata
  → satisfies AGENTS.md. NO gap, NO solver change.
- Dev population = 24 rows: 12 ABA instances x {SE-ST, SE-PR}.
  Derivation: sizes {10,30,50,150,200,600}; per size take sorted-index 0,1 = dev,
  index 2,3 = holdout (disjoint). Subtracks SE-ST + SE-PR.
- PRIMARY METRIC = solved-count on dev pop @ T=10s, backend auto, --jobs 1.
- RESULT: **21 solved / 24 (3 timeout), IDENTICAL across 3 repeats** (paired,
  deterministic). Timeout rows: aba_2000_0.3_10_10_0 SE-ST+SE-PR,
  aba_2000_0.3_10_10_1 SE-PR. (aba_2000_0.3_10_10_1 SE-ST solved ~1.2s.)
- Wall on solved rows: median ~0.51-0.54s, max ~1.6s. Total run wall ~44s.
- Noise rule: solved-count deterministic (3x identical); wall-clock only noisy
  quantity; all solved rows >=8s below T, timeouts need >>10s -> no boundary
  flips -> metric boundary-stable. Hash-seed irrelevant (natural_key ordering).
- Run artifacts (uncommitted): data/iccma/2023/runs/iccma-2023-frame-dev-baseline-run{1,2,3}-2026-07-11.*

## Remaining: write artifacts + ONE atomic commit
- experiments/INDEX.md (ledger; reconcile 2 negatives + name 47-commit DC-CO branch)
- experiments/iccma2023-frame/{population-dev.json,population-holdout.json,README.md}
- experiments/2026-07-11-iccma2023-campaign-frame-baseline.md (baseline record)
- reports/iccma-campaign-frame-worker-20260711.md (worker report)
- Commit atomically; do NOT commit unrelated untracked files or run/ outputs.

## ARTIFACTS WRITTEN (all done)
- experiments/INDEX.md — ledger (reconciles N1,N2 negatives + D1 47-commit DC-CO branch)
- experiments/2026-07-11-iccma2023-campaign-frame-baseline.md — baseline record
- experiments/iccma2023-frame/{population-dev.json,population-holdout.json,README.md}
- reports/iccma-campaign-frame-worker-20260711.md — worker report (UNTRACKED, matches
  sibling scout reports convention; stated in report + will not stage it)

## CONVENTIONS CONFIRMED
- data/ fully gitignored (.gitignore:7) — benchmark instances + manifests + runs NOT committed.
  Partition JSON is self-contained (embeds relative_paths) -> anchors population without data.
- The 3 sibling 2026-07-11 campaign scout reports are UNTRACKED -> worker report stays untracked.
- Provenance report docs/reports/iccma2023-repo-research-2026-07-11.md is TRACKED (citable).

## COMMIT PLAN (next, only these 5 files staged explicitly)
  experiments/INDEX.md
  experiments/2026-07-11-iccma2023-campaign-frame-baseline.md
  experiments/iccma2023-frame/population-dev.json
  experiments/iccma2023-frame/population-holdout.json
  experiments/iccma2023-frame/README.md
- Exclude: worker report, this note, data/ outputs, all pre-existing untracked. Do NOT push.
- End state: KEPT.

## STAGING (done) — ward quirks learned
- `git add` guard: only Write/Edit-"touched" OR adopted paths stage; compound
  bash (loops/pipes) confuses the parser -> blocks; use PLAIN single-path adds.
- Bash-jq-generated JSON files were NOT "touched" -> re-materialized both via
  Write tool, then plain single git add each. All 5 now staged, nothing else.
- Staged set verified = exactly the 5 frame artifacts. Next: commit (no push).
