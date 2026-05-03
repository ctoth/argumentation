# Paper Retrieval & Reading Report — Delobelle & Villata (2019)

**Date:** 2026-05-02
**Pipeline:** lightweight (paper-retriever → paper-reader). Per Q's instructions, NO source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote, reconcile, or update index.md.
**Model tier:** opus throughout.

## Paper Identity

- **Title:** Interpretability of Gradual Semantics in Abstract Argumentation
- **Authors:** Jérôme Delobelle, Serena Villata
- **Year / Venue:** 2019, ECSQARU 2019 — 15th European Conference on Symbolic and Quantitative Approaches to Reasoning with Uncertainty (Belgrade, Serbia), Springer LNAI 11726, pp. 27–38
- **DOI:** 10.1007/978-3-030-29765-7_3
- **HAL Id:** hal-02277678 (open access deposit)
- **Affiliation:** Université Côte d'Azur, Inria, CNRS, I3S, Sophia-Antipolis, France
- **Funding:** DGA RAPID CONFIRMA

## Retrieval Path

1. **Search** via `paper-retriever/scripts/search_papers.py` (source `all`) confirmed the target paper in the Semantic Scholar results (DOI `10.1007/978-3-030-29765-7_3`). All other results were unrelated near-misses (later impact-measure follow-ups, unrelated Villata 2011 antigravity reply).
2. **Strong-identifier normalisation:** DOI selected over title/S2-ID per Step 1.5 ranking.
3. **`fetch_paper.py`** with the DOI returned `fallback_needed: true` (Springer paywall, no Unpaywall PDF).
4. **WebSearch** found the open-access HAL deposit (`https://hal.science/hal-02277678`) and the direct PDF URL (`https://hal.science/hal-02277678v1/file/DVecsqaru2019.pdf`).
5. **Direct curl** returned a 12KB Anubis bot-protection HTML page, not a PDF — could not bypass with simple HTTP.
6. **Browser fallback** via the claude-in-chrome MCP (Option 1 in the retriever skill): navigated to the HAL landing page (Anubis cleared in-browser), then triggered an `<a download>` click on the PDF URL, which dropped a 480803-byte PDF into `~/Downloads`.
7. **Moved** to `papers/Delobelle_2019_InterpretabilityGradualSemanticsAbstract/paper.pdf`. Verified: `PDF document, version 1.4, 13 page(s)`, 480803 bytes.
8. **Materialised metadata.json** via `fetch_paper.py --metadata-only`, then enriched with abstract text, full author names, HAL URL, and the DOI-stamped bibtex (Step 3.5 schema compliance: arxiv_id null, abstract populated).

## Reading Path

- **Pages converted** via ImageMagick at 150 DPI to `pngs/page-000.png`..`pngs/page-012.png` (13 pages; page 0 is the HAL cover sheet, paper proper begins page 1).
- **Direct read** (≤300pp branch): all 13 page images read inline with the Read tool.
- **Notes written** with full per-page coverage including: every numbered Definition (1-13), every Notation (1-2), every Property (1), every Proposition (1-3), every Equation (counting model, h-cat, complement, Imp non-attacked + general, BI, decomposition, Def. 11), Algorithm 1 (ACY) step-by-step, all four worked Examples (1-4), three Figures, parameters table, testable properties, design rationale, limitations, related-work distinctions, application notes, and full reference list.

## Output Inventory

`papers/Delobelle_2019_InterpretabilityGradualSemanticsAbstract/`:
- `paper.pdf` (480 KB, 13 pp)
- `pngs/page-000.png` … `pngs/page-012.png` (13 page images)
- `notes.md` (16.6 KB — dense paper surrogate)
- `description.md` (with tags: gradual-semantics, interpretability, abstract-argumentation, counting-semantics, h-categorizer)
- `abstract.md` (verbatim original + interpretation)
- `citations.md` (all 17 references + 6 follow-up callouts)
- `metadata.json` (Step 3.5 schema-compliant; arxiv_id null, abstract populated, HAL URL, DOI bibtex)

## Identity Verification

Resolved metadata (title, authors, year, venue, pages 27-38) matches the intended paper exactly. No mismatch.

## Key Takeaways for the Argumentation Library

1. **Counting Semantics satisfies Balanced Impact (BI)**; **h-categorizer does not**. Concrete property to test in the gradual-semantics module.
2. **Decomposition theorem (Def. 10):** under BI, `Deg(y) = 1 + Σ_x Imp({x}, y)` for acyclic AFs — gives a free per-argument-contribution explanation channel for any BI-satisfying weighted gradual semantics we ship.
3. **ACY tree-unfolding algorithm (Algorithm 1)** extends the additive decomposition to cyclic AFs by building an infinite acyclic AF rooted at the target argument; depth in practice bounded by the gradual semantics' fixed-point convergence iteration count (footnote 1, p.8).
4. **Impact ranking + PI/NI sets (Defs. 12-13):** ready-to-implement primitives for "which arguments contribute most positively/negatively to argument y" — direct fit for explanation/UX layers.
5. **Anchor for follow-ups:** This is the foundational paper Al Anaissy/Delobelle/Vesic/Yun (2024) builds on (refines + adds Shapley-value impact measure), and the explicit positioning against Amgoud/Ben-Naim/Vesic (2017) Shapley-attack work makes it useful as the reference point for the QBAF contribution-function workstream (Wave 1 tasks #2 Kampik 2024 and #3 Yun 2023).

## Usefulness Rating

- **Rating:** High
- **What it provides:** A clean, publishable additive-decomposition story for gradual semantics that satisfies BI; a discriminating axiom that separates Counting Semantics from h-categorizer; a concrete unfolding algorithm to lift acyclic results to cyclic AFs.
- **Actionable next steps:** (i) Implement Counting Semantics + verify BI as a unit-tested property; (ii) wire Defs. 7-11 as a per-argument explanation API on any BI-satisfying weighted gradual semantics; (iii) cross-link with Wave 1 papers Cayrol & Lagasquie-Schiex 2004 (bipolar AFs — listed by D&V as future work) and the Kampik/Yun QBAF contribution-function papers.
- **Skip if:** the project never exposes a gradual/weighted/quantitative semantics — i.e., stays purely Dung extension-based.

## Steps Skipped (per Q's instructions)

- Step 7 (reconcile)
- Step 8 (papers/index.md update)
- Step 9 (provenance stamp via `pks source stamp-provenance`)
- All propstore source-branch operations (source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote)
