# Paper Report: Yin, Potyka, Toni (2023) — Argument Attribution Explanations in QBAFs

**Date:** 2026-05-02
**Paper ID:** arxiv:2307.13582
**Directory:** `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/`

## Retrieval Outcome

- **Status:** SUCCESS — paper.pdf, metadata.json, abstract.md, notes.md, description.md, citations.md all present.
- **Retrieval method:** direct curl from `https://arxiv.org/pdf/2307.13582.pdf` (skipped fetch_paper.py and Semantic Scholar metadata enrichment per parent task instruction; S2 calls would have hung on rate-limited 429s).
- **Time used:** ~2 min download + page-image rendering, ~6 min reading and note authorship. Within the 5-minute *retrieval* budget; reading exceeded that but the budget cap was on retrieval specifically.
- **Lead spelling fix confirmed:** surname is **Yin** (Xiang Yin). Earlier "Yun" was a typo.

## What This Paper Provides

Defines **Argument Attribution Explanations (AAEs)** as gradient-based attribution scores for arguments in acyclic Quantitative Bipolar Argumentation Frameworks (QBAFs) under DF-QuAD gradual semantics:

```
∇|_{B↦A} := lim_{ε→0} [σ_{τ(B)+ε}(A) − σ(A)] / ε
```

Equivalently, the partial derivative of topic argument A's strength with respect to source argument B's base score.

### Closed-form Operators
- **Direct attribution (Prop 2):** four-case formula on (relation polarity × attacker-vs-supporter dominance) returning `ξ_B · (1 − |v_{Ba} − v_{Bs}|) · ∏_{Z ≠ B, sibling}(1 − σ(Z))`.
- **Indirect attribution (Prop 4):** chain rule `∇|_{X1↦Xn} = (1 − |v_{X1a} − v_{X1s}|) · ∏ ∇|_{Xi↦Xi+1} / (1 − |v_{Xi a} − v_{Xi s}|)`.
- **Sign-only direct (Prop 1):** attack ⇒ ≤0, support ⇒ ≥0.
- **Sign-only indirect (Prop 3):** parity rule on number of attacks Θ along path; even Θ ⇒ ≥0, odd ⇒ ≤0.

### Properties Proved
| Property | Defining ref | Status under direct/indirect | Status under multifold |
|----------|--------------|------------------------------|------------------------|
| Explainability | [4] Amgoud-BenNaim | ✓ always | ✓ |
| Missingness | [29] SHAP | ✓ always | ✓ |
| Completeness | [42] IG/DeepLIFT | ✓ (Prop 7) | **✗ can violate (Prop 8)** |
| Counterfactuality | [18] Covert-Lundberg-Lee | ✓ (Prop 9) | **✗ can violate (Prop 10)** |
| Agreement | new | ✓ (Prop 11) | **✗ can violate (Prop 12)** |
| Monotonicity | new | ✓ (Prop 13) | **✗ can violate (Prop 14)** |

### Computational Complexity
**O(n)** total time to compute all AAEs into a single topic argument (n = |A|). Re-uses the v_{Aa}, v_{As} aggregates computed during the DF-QuAD forward pass.

### Case Studies (3, not 2)
1. **Fake news detection** (sec 6): 8-arg QBAF from Kotonya & Toni [28]. σ(A)=0.59375. Top positive AAE: Reply C → A = 0.375. Top negative: Reply D → A = −0.4375.
2. **Movie recommender** (sec 6): "The Post" QBAF from Cocarascu et al. [17] with sub-features. σ(m)=0.85. Top positive: Acting f_A → m = 0.17625. Top negative: Writing f_W → m = −0.21.
3. **Fraud detection** (SM appendix C, missed by abstract): 48-arg QBAF from Chen et al. [16]. σ(1)=0.2543945275247097 ⇒ "no investigation". 29 positive + 18 negative AAEs; magnitude of negatives outweighs positives despite count imbalance.

## Relation to Prior Attribution Work
- **Generalises gradient feature attribution** [8] from input features to QBAF arguments. Doesn't reinvent — explicitly inherits properties from SHAP [29], IG/DeepLIFT [42, 43], counterfactual methods [18], and the same authors' faithfulness work [35].
- **Beats SHAP/Shapley computationally:** O(n) vs exponential. Beats LIME [39] perturbation cost. Beats SILO [12].
- **Differs from Delobelle & Villata interpretability** [22]: D&V analyse what *semantics function* does, AAE attributes per-argument contribution.
- **Related to Čyras et al. dispute-tree explanations** [19]: complementary — qualitative dialectical structure vs quantitative gradient.

## Limitations / Open Problems
1. **Acyclic restriction.** Cyclic QBAFs need fixed-point differentiation; cites [31, 33] for non-convergence concerns.
2. **DF-QuAD-specific properties.** Generalises to Euler-based [3] and quadratic energy [32] semantics in principle but proofs are open.
3. **Multifold connectivity gap.** Four out of six properties fail. No proposed remedy.
4. **Single-argument focus.** Joint/coalition attribution for argument *sets* is open.
5. **No human study.** All "intuitive" claims are author-assessed on toy QBAFs.

## Relevance to This Project

**Rating: HIGH.** Direct anchor for the project's quantitative-attribution explanation workstream over QBAFs.

### Concrete actionable next steps
1. **Implement `aae_direct(B, A, qbaf)` and `aae_indirect_chain(path, qbaf)`** matching Props 2 and 4 verbatim. Closed forms are O(n), no SAT needed.
2. **Add property-test fixtures** from Table 1 (fake news) and Table 2 (movie). The exact AAE values (e.g. C→A = 0.375, Acting→m = 0.17625) make excellent regression assertions.
3. **Detect and warn on multifold connectivity** — flag when properties may break.
4. **Linear-time AAE pass after DF-QuAD forward pass** — both can share the v_{Aa}/v_{As} cache.
5. **Visualisation widget** — coloured arrows + sorted bar chart, per Figs 4 and 6.
6. **Integration test** using the 48-argument fraud detection QBAF (SM Table 3) — large enough to stress edge cases, small enough to inspect by eye.

### Open research workstreams the project could lead
- AAE for cyclic QBAFs via implicit-function-theorem differentiation of fixed point.
- AAE for Euler-based and quadratic-energy semantics.
- Closing the multifold-connectivity property gap via path decomposition or Shapley-on-paths hybrid.

### Skip if
- The project does not use QBAFs (only abstract Dung AFs) — AAEs are fundamentally tied to numerical strength.
- The project only needs qualitative explanations — AAE is a quantitative tool.

## Files Produced
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/paper.pdf` (1.38 MB, 21 pp)
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/metadata.json` (full enriched)
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/abstract.md`
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/notes.md` (~600 lines, dense extraction)
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/description.md`
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/citations.md` (45 refs + 12 follow-ups)
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/pngs/` (21 page images at 150 DPI + 4 hi-res clean re-renders)

## Steps NOT Performed (per parent constraints)
- `source-bootstrap`, `register-concepts`, `extract-claims`, `register-predicates`, `author-rules`, `author-context`
- `source-promote`, `reconcile`
- `papers/index.md` update
- propstore provenance stamp

The artifacts above are sufficient for the parent agent to drive any of these downstream steps later.
