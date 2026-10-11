# ICCMA 2023 campaign frame — CLI continuation worker state

Role: `ward set experiment` (applied). Task: complete OR verify the single
framing commit per `prompts/iccma-campaign-frame-continuation-cli-20260711.md`.

## Situation found
- HEAD `5f75a7c`, branch `main`. NO commit after `5f75a7c` yet.
- Partial state: `experiments/INDEX.md` + `experiments/2026-07-11-iccma2023-campaign-frame-baseline.md`
  are STAGED (git add-ed) but not committed. `experiments/iccma2023-frame/`
  (README.md, population-dev.json, population-holdout.json) is UNTRACKED.
- Prior worker (`notes-iccma-campaign-frame-worker-state.md`) authored all 5
  artifacts and measured baseline, then stalled before committing.
- This is a partial completion, NOT a collision — I finish the commit after verifying.

## Verified so far
- 3 summary JSONs (run1/2/3): each `solved:21, timeout:3, total:24`. MATCHES record.
- Frame dir artifacts read: dev=12 inst x{SE-ST,SE-PR}=24, holdout=12 disjoint x2=24.
  Strata {10,30,50,150,200,600}, sorted-index {0,1}=dev {2,3}=holdout.
- Raw run JSON = array of 24 rows. jq present.

## Still to verify
- Per-row status+elapsed in baseline record vs run1/2/3 JSON (timeout rows:
  aba_2000_0.3_10_10_0 SE-ST+SE-PR, aba_2000_0.3_10_10_1 SE-PR; _1 SE-ST solved).
- dev/holdout disjointness (0 shared relative_path) — via repo script or small script file.
- Re-run operational-contract pytest triple (record claims 56 passed/1 skipped).

## OUTCOME — SUCCESS (verified, not edited)
A concurrent completion committed the slice DURING this session: `main` moved
`5f75a7c` -> `4782b76` "Frame ICCMA 2023 ABA throughput campaign with committed
baseline". Per collision-guard step 3 I did NOT edit; I verified against the prompt:

- Commit `4782b76` = exactly the 5 intended slice files (516 insertions), nothing
  extra: experiments/{INDEX.md, 2026-07-11-iccma2023-campaign-frame-baseline.md,
  iccma2023-frame/{README.md, population-dev.json, population-holdout.json}}.
- Tracked working tree CLEAN (git status --untracked-files=no empty).
- NOT pushed: origin/main...HEAD = 0 1 (HEAD 1 ahead).
- Worker report + state notes remain UNTRACKED (correct convention).
- Baseline 21/24 solved verified vs raw run1/2/3 JSON: identical status pairing
  (same md5 across 3 runs), timeout rows aba_2000_0.3_10_10_0 SE-ST+SE-PR &
  aba_2000_0.3_10_10_1 SE-PR; per-row elapsed matches record table.
- Populations identity-verified against manifest (jq re-derivation diff clean);
  dev/holdout disjoint (0 shared; 12+12 unique); assumptions/atoms match manifest.
- Contract triple re-run: 56 passed, 1 skipped. Pinned evaluator blobs match.
- Did NOT rerun baseline (raw evidence internally consistent). Preserved all
  unrelated untracked files.
