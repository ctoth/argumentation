# ICCMA 2023 Campaign — Frame Partitions

This directory freezes the **development population** and the **sealed holdout**
for the ICCMA 2023 solver-throughput campaign. The ledger is
[`experiments/INDEX.md`](../INDEX.md); the baseline record is
[`experiments/2026-07-11-iccma2023-campaign-frame-baseline.md`](../2026-07-11-iccma2023-campaign-frame-baseline.md).

## Files

- `population-dev.json` — 12 ABA instances × {SE-ST, SE-PR} = **24 dev rows**.
  Triage, tuning, and the baseline live here. Candidates are measured here.
- `population-holdout.json` — 12 disjoint ABA instances × {SE-ST, SE-PR} =
  **24 sealed rows**. Never used for triage or tuning. Run once, at promotion,
  by the verifier only.

## Corpus provenance (why instance identity is anchored without committing data)

The benchmark corpus is **not** tracked: `.gitignore:7` ignores all of `data/`.
The instances and manifests are local, deterministically reconstructed, and
MD5-verified against Zenodo record `8348039` (`iccma2023_benchmarks.zip`,
MD5 `f7382a5d5b8118253a9266d5465b5bed`) — see the tracked report
`docs/reports/iccma2023-repo-research-2026-07-11.md:19-30`. The 2023 corpus is
**400 ABA `.aba` + 329 AF `.af`** parsed instances.

Because the data is gitignored by repo convention, the frozen population is
anchored by the **`relative_path` list committed in the two JSON files here**,
not by a committed manifest. Each entry is self-contained (relative_path,
assumptions, atoms, sorted_index), so the partitions survive manifest
regeneration and are reproducible from the Zenodo-pinned corpus alone.

## Deterministic derivation (RNG-free)

The harness has **no RNG seed**; selection is a pure function of the manifest.

1. From `data/iccma/2023/manifests/iccma-2023-manifest.json`, select ABA
   instances with `parse_status == "ok"` whose `assumptions` ∈
   **{10, 30, 50, 150, 200, 600}** (six of the ten equal-size ABA strata; each
   stratum holds 40 instances).
2. Within each stratum, sort by `relative_path` ascending.
3. Sorted index **{0, 1} → development**; sorted index **{2, 3} → holdout**.
   Disjoint by instance identity (verified: 0 shared `relative_path`).
4. Cross every selected instance with subtracks **{SE-ST, SE-PR}**.

Reproduce with:

```
jq '[.[] | select(.kind=="aba" and .parse_status=="ok"
      and (.assumptions|IN(10,30,50,150,200,600)))]
    | group_by(.assumptions)
    | map(sort_by(.relative_path) | to_entries
          | map({relative_path:.value.relative_path, assumptions:.value.assumptions,
                 atoms:.value.arguments_or_atoms, sorted_index:.key}))
    | add
    | {dev:[.[]|select(.sorted_index<2)],
       holdout:[.[]|select(.sorted_index>=2 and .sorted_index<4)]}' \
  data/iccma/2023/manifests/iccma-2023-manifest.json
```

## Why these strata / subtracks

- The six assumption sizes span **easy → hard** (0.3 s to hard-timeout),
  giving the solved-count metric real headroom: at the calibrated 10 s budget,
  the largest stratum (600 assumptions, `aba_2000_0.3_*`) mostly times out, so a
  candidate that cracks that shape *raises* the metric. That 600-assumption
  shape is exactly the one both 2026-07-11 negatives were measured on.
- **SE-ST** and **SE-PR** are the two profiler-named ABA offenders
  (single-extension existence, certificate emitted, no query sidecar needed).
- **Scope note (honest):** AF carries ~92 % of the 2025 timeout mass, but
  full-AF runs from this environment are recorded as fragile (background runs
  killed at `iccma_jobs_built`; see `reports/iccma-campaign-history-scout-20260711.md`).
  This first frame is deliberately the **ABA SE-ST/SE-PR slice** — tractable,
  contention-free, and aligned with the campaign's active front. An AF frame is
  a named future slice, gated on the fragile-run fix, not this commit.
