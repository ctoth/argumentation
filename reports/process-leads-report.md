# Process Leads Report

**Date:** 2026-05-02
**Mode:** Mode A (notes-based) only; M=5 parallel; default count 10
**Pipeline:** retriever + reader only (lightweight; full paper-process skipped per Q)

## Counts
- **Total leads found:** 144
- **Already-in-collection skip (extract-leads):** 22
- **Triaged candidate set:** 10
- **Attempted:** 10
- **Succeeded (new artifacts):** 6
- **Moved from propstore (Q's call A):** 2
- **Duplicates caught (no work):** 1
- **Mismatches / hallucinated:** 1

## Succeeded — fresh retrievals
| # | Lead | Paper Directory |
|---|------|-----------------|
| 1 | Delobelle & Villata (2019) — Interpretability of gradual semantics | `papers/Delobelle_2019_InterpretabilityGradualSemanticsAbstract/` |
| 2 | Kampik et al. (2024) — Contribution functions for QBAFs (51pp) | `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/` |
| 3 | Yin (Yun) et al. (2023) — Argument attribution explanations | `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/` |
| 4 | Amgoud, Cayrol, Lagasquie-Schiex (2004) — On the bipolarity in AFs (NMR 2004) | `papers/Amgoud_2004_BipolarityArgumentationFrameworks/` |
| 8 | Strass (2013) — Approximating operators and semantics for ADFs | `papers/Strass_2013_ApproximatingOperatorsSemanticsAbstract/` |
| 9 | Egly, Gaggl, Woltran (2010) — ASP encodings for AFs (ASPARTIX) | `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/` |

## Moved from propstore (Q's option A — each project owns its own papers)
| # | Lead | Source → Destination | Note |
|---|------|----------------------|------|
| 5 | Oikarinen & Woltran (2011→2010) — Strong Equivalence | `propstore/papers/Oikarinen_2010_*` → `papers/` | Full artifacts moved |
| 6 | Baumann & Brewka (2019) — AGM Contraction for Dung Frameworks | `propstore/papers/Baumann_2019_*` → `papers/` | **Source had no PDF / pages / pngs — only metadata.** PDF retrieval is a separate todo if Q wants. |

Both moves staged in argumentation (additions) and propstore (deletions). 17+ propstore knowledge files (index.md, plans, reports, reviews, claims.yaml refs) still reference these dirs — propstore agent's cleanup, out of scope for this run.

## Duplicates / mismatches
| # | Lead | Reason |
|---|------|--------|
| 7 | Hanisch & Rauschenbach (2025) — ANGRY: A grounder for rule-based argumentation | **Already in collection** as `Diller_2025_GroundingRule-BasedArgumentationDatalog`. ANGRY is the system name; Hanisch & Rauschenbach are 2 of 5 co-authors. Lead-extraction surface-text dedupe miss. No new dir created. |
| — | Cayrol & Lagasquie-Schiex (2004) — Bipolar abstract argumentation systems | **Bad cite** — that title is a 2009 book chapter, not 2004. Genuine 2004 paper is the 3-author Amgoud/Cayrol/Lagasquie NMR paper, retrieved as #4 above. |
| 10 | Noor, Rago, Toni (2024) — Argumentative LLMs for explainable medical decision-making | **Paper does not exist.** Verified across arxiv, Crossref, OpenAlex, and Antonio Rago's 30 most recent works. Closest match is Freedman et al. 2024 "Argumentative LLMs for Explainable and Contestable Claim Verification" (arxiv 2405.02079) — different topic, different authors. Likely hallucinated lead in the Freedman 2025 notes. |

## Remaining (not attempted)
**134 leads** not attempted. Run again with a higher N or `--all` to continue. Many remaining leads are pre-1990 papers, books, or vague bundled cites — triage by extract-leads is recommended before bulk dispatch.

## Per-paper reports
- `reports/paper-delobelle-villata-2019.md`
- `reports/paper-kampik-2024-contribution.md`
- `reports/paper-yin-2023-attribution.md`
- `reports/paper-amgoud-cayrol-lagasquie-2004.md`
- `reports/paper-strass-2013-adf.md`
- `reports/paper-egly-gaggl-woltran-2010.md`
- `reports/paper-cayrol-lagasquie-2004.md` (mismatch report)
- `reports/paper-hanisch-rauschenbach-2025.md` (duplicate report)
- (no Noor report — agent stopped on mismatch per instruction)

## Index updated
`papers/index.md` extended with 8 new entries (6 fresh + 2 moved) following the existing curated format.

## Operational lessons
- The `process-leads` skill template invokes the heavyweight `paper-process` (full propstore ingestion). Q wants the lightweight `paper-retriever + paper-reader` only for this skill. Worth fixing the template.
- `fetch_paper.py` calls Semantic Scholar for supplemental metadata — S2 is rate-limited (HTTP 429) and can hang for many minutes. Bypass: download PDF directly via arxiv/HAL/sci-hub and synthesize metadata locally.
- Lead extraction surface-matching is loose. Hanisch&Rauschenbach 2025 = Diller 2025 wasn't caught by `extract-leads --skip-collected` because the surface text didn't share an author-year with the existing dir name.
- Citations in `notes.md` can be hallucinated. Always verify the paper exists (arxiv/Crossref/OpenAlex) before deep retrieval — the Noor/Rago/Toni 2024 lead burned <5 min of agent time but cost zero new papers.
