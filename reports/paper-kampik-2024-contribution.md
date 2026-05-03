# Paper Report: Kampik et al. (2024) — Contribution Functions for QBAGs

## Retrieval Summary

- **Intended paper:** Kampik et al. (2024) "Contribution functions for quantitative bipolar argumentation graphs"
- **Resolved match:** ✓ exact — Timotheus Kampik, Nico Potyka, Xiang Yin, Kristijonas Čyras, Francesca Toni, *"Contribution Functions for Quantitative Bipolar Argumentation Graphs: A Principle-based Analysis"*, arXiv:2401.08879v2 [cs.AI], 13 Jun 2024 (preprint dated 17 Jun 2024)
- **Source:** arXiv direct PDF
- **Identifier used:** arxiv:2401.08879
- **PDF path:** `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/paper.pdf`
- **PDF size:** 642,967 bytes (≈ 642 KB)
- **PDF pages:** 51
- **Mismatch check:** none — title, author list, and abstract on page 0 match request verbatim.

## Pipeline Used

Per user instructions: lightweight pipeline only.

1. `/research-papers:paper-retriever` → arXiv search → fetch_paper.py → `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/{paper.pdf, metadata.json}` created.
2. `/research-papers:paper-reader` → `magick` page conversion (51 PNGs at 150 DPI) → all 51 pages read directly (Step 2A: ≤300 pages) → wrote `notes.md`, `description.md`, `abstract.md`, `citations.md`.

**Skipped per user override:** `paper-process`, `source-bootstrap`, `register-concepts`, `extract-claims`, `register-predicates`, `author-rules`, `author-context`, `source-promote`, `reconcile`, `papers/index.md` update, `pks source stamp-provenance`.

## Artifacts Produced

| File | Purpose | Status |
|---|---|---|
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/paper.pdf` | Source PDF | ✓ |
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/metadata.json` | Bibliographic metadata | ✓ (from retriever) |
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/pngs/page-000.png` … `page-050.png` | Per-page images | ✓ (51 files) |
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/notes.md` | Dense extraction notes | ✓ |
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/description.md` | Index-style description with tags | ✓ |
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/abstract.md` | Verbatim abstract + interpretation | ✓ |
| `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/citations.md` | Full 38-entry reference list + key follow-ups | ✓ |

## Content Highlights

### Headline contribution
Four contribution functions (Removal R, Removal-without-indirection R', Shapley S, Gradient ∂) for *acyclic* QBAGs, evaluated against five gradual semantics (QE, DFQuAD, SD-DFQuAD, EB, EBT) on five principles (Contribution Existence, Quantitative Contribution Existence, Directionality, (Quantitative) Local Faithfulness, (Quantitative) Counterfactuality). **No function satisfies all five principles**; each "main" function uniquely characterises one:
- **Ctrb^R** ↔ (Quantitative) Counterfactuality — by definition.
- **Ctrb^S** ↔ (Quantitative) Contribution Existence — by Shapley efficiency.
- **Ctrb^∂** ↔ (Quantitative) Local Faithfulness — by definition of partial derivative.
- **Directionality** is universal across all four functions (Prop 5.9).

### Master satisfaction matrix (Table 1, p.6)

| Principle | Ctrb^R | Ctrb^R' | Ctrb^S | Ctrb^∂ |
|---|---|---|---|---|
| Contribution Existence | QE,EB only | QE,EB only | **all 5** | QE,EB only |
| Quantitative Contribution Existence | none | none | **all 5** | none |
| Directionality | **all 5** | **all 5** | **all 5** | **all 5** |
| (Quantitative) Local Faithfulness | none | none | none | **all 5** (differentiable case) |
| (Quantitative) Counterfactuality | **all 5** | none | none | none |

### Notable side results (§6)
- **Proximity** principle (closer arguments contribute more in absolute value) is too strong: violated by all functions across all five semantics for Ctrb^R/R'/S, and by Ctrb^∂ for QE/DFQuAD/SD-DFQuAD/EB. Ctrb^∂ + EBT case is open. Conjecture 1: Ctrb^S satisfies proximity over *pure support paths*.
- **Strong faithfulness** is violated everywhere (Prop 6.2). Conjecture 2: Ctrb^∂ satisfies strong faithfulness on the restricted class of *monotonic-effect QBAGs* (Definitions 6.3-6.4).
- **Application example (§7):** Rotten-Tomatoes-style movie-rating QBAG; Table 5 shows numeric contributions and how each function tells a different practical story.

### Implementation cues
- Final-strength computation in acyclic QBAGs is **linear-time forward propagation** along topological order (Potyka [22]).
- Shapley-based contribution requires summing over $2^{|Args|-2}$ coalitions — exponential; needs sampling/approximation in practice.
- Gradient contribution computable via autodiff over the recursively-built composition $f_a$; memoization caps placeholder count at $|Args|$.
- All counterexamples in §5 were validated in **two independent implementations**: QBAF-Py (https://github.com/TimKam/Quantitative-Bipolar-Argumentation) and Uncertainpy (https://github.com/nicopotyka/Uncertainpy).

## Usefulness to This Project

**Rating:** Medium-High (relevant to explainability workstream, methodologically valuable for any reduction/encoding work).

**What it provides:**
- A rigorous principle-based comparison framework that translates cleanly to other argumentation contexts; could anchor a parallel analysis for our reductions/encodings.
- Algorithmic recipes for four attribution-style explanation functions with explicit complexity tradeoffs.
- A counterexample corpus (Figures 1-26 main + 25-41 appendix) usable as test cases for any QBA implementation.
- Reference [13] (Čyras et al. 2022 dispute trees) and [14] (Yin et al. 2023 argument attribution) are direct neighbours — already on the project's wave-1 list (Yun et al. 2023; Delobelle & Villata for the gradual-semantics ancestor [19]).

**Actionable next steps:**
- If we extend the project's reasoners with weighted/probabilistic argumentation: adopt the modular-semantics framing (Table 2/3) directly.
- For an explainability layer: implement Ctrb^R first (cheap, satisfies counterfactuality everywhere) plus optionally Ctrb^∂ (Prop 5.10's quantitative local faithfulness gives clean sensitivity readings).
- Consider the principle-based analysis style as a template for assessing our reduction targets (e.g., does a given encoding preserve a "directionality"-analogue?).

**Skip if:** the project remains strictly on classical (extension-based, non-quantitative) Dung-style argumentation with no explanation-attribution requirement.

## Notes File Cross-Reference

- Page-by-page extraction lives in `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/notes.md`.
- Full 38-entry reference list (with arxiv/DOI/URL where available) and 10 key-citations-for-followup at `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/citations.md`.
- Description (with tags `quantitative-argumentation, bipolar, explainability, contribution-functions, principle-based-analysis`) at `papers/Kampik_2024_ContributionFunctionsQuantitativeBipolar/description.md`.
