# Process Leads Run — 2026-05-02

## Status: closing out
- Wave 1 + Wave 2 + Strass finisher complete.
- 8 paper-related operations done (6 fresh retrievals, 2 propstore→argumentation moves, 1 dedupe catch, 1 hallucinated-cite mismatch).
- argumentation/papers: 56 → 63 dirs.
- All 8 retrievals have full notes.md / abstract.md / citations.md / description.md / paper.pdf / pngs/ / metadata.json.
- 8 per-paper reports under reports/ (including 2 mismatch reports).
- papers/index.md extended with 8 new entries (matching curated format).
- reports/process-leads-report.md written (final summary).

## Wave outcomes
| # | Lead | Outcome | Path |
|---|------|---------|------|
| 1 | Delobelle & Villata 2019 | ✅ | papers/Delobelle_2019_InterpretabilityGradualSemanticsAbstract/ |
| 2 | Kampik 2024 contribution | ✅ (51pp) | papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/ |
| 3 | Yin 2023 attribution (corrected from Yun) | ✅ arxiv 2307.13582 direct | papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/ |
| 4 | Amgoud, Cayrol, Lagasquie 2004 NMR (corrected from bad Cayrol cite) | ✅ HAL hal-03198386 | papers/Amgoud_2004_BipolarityArgumentationFrameworks/ |
| 5 | Oikarinen 2010 strong equivalence | ⊕ MOVED from propstore | papers/Oikarinen_2010_CharacterizingStrongEquivalenceArgumentation/ |
| 6 | Baumann 2019 AGM contraction | ⊕ MOVED from propstore (no PDF in source) | papers/Baumann_2019_AGMContractionDung/ |
| 7 | Hanisch & Rauschenbach 2025 ANGRY | ⊘ DUPLICATE = Diller_2025 already in collection |
| 8 | Strass 2013 ADF AIJ | ✅ sci-hub (after re-dispatch for paper-reader) | papers/Strass_2013_ApproximatingOperatorsSemanticsAbstract/ |
| 9 | Egly, Gaggl, Woltran 2010 ASPARTIX | ✅ sci-hub (32pp) | papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/ |
| 10 | Noor, Rago, Toni 2024 medical | ❌ MISMATCH — paper does not exist anywhere |

## Git state (pre-commit)
- argumentation: 8 staged adds for moves (Baumann_2019 + Oikarinen_2010 text artifacts), 6 untracked new paper dirs, papers/index.md modified, 1 surprising untracked: papers/Diller_2025_*/metadata.json modified (likely by paper-reader during the Hanisch&Rauschenbach 2025 dispatch which discovered Diller — agent updated metadata while reading).
- propstore: 14+ staged deletions for the 2 moved dirs.
- Many other untracked files (notes/, reports/, scratch/) — pre-existing, not touching them.

## Next step
1. Commit argumentation: index.md update + 8 new paper dirs (text only — pdfs/pngs gitignored) + Diller metadata update + the moved-in Baumann/Oikarinen text artifacts.
2. Commit propstore: deletion of moved-out dirs.
3. Done.

## Decisions made
- Q approved: index.md update (all 8), commits in both repos, final report write.
- Will commit selected paths only, NOT `git add -A` (avoid sweeping in unrelated untracked notes/reports/scratch from other workstreams).

## Blocker
None — proceeding to commit.
