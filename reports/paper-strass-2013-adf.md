# Paper Reader Report: Strass 2013 — Approximating operators and semantics for ADFs

**Date:** 2026-05-02
**Worker:** Opus 4.7 (1M context), paper-reader skill
**Paper directory:** `papers/Strass_2013_ApproximatingOperatorsSemanticsAbstract/`
**Source PDF:** `papers/Strass_2013_ApproximatingOperatorsSemanticsAbstract/paper.pdf` (32 pages, AIJ 205:39-70, DOI 10.1016/j.artint.2013.09.004)

## What was done
- Converted `paper.pdf` → 32 PNG page images at 150 DPI in `pngs/page-000.png` … `pngs/page-031.png`.
- Read every page image directly (single-agent, no chunking — paper is 32pp, well under the 300pp threshold).
- Wrote `notes.md` (~25KB) with frontmatter, one-sentence summary, problem, contributions, study design (n/a — pure theory), methodology, master operator/parameter table, all key equations in LaTeX with page citations, every numbered Definition/Lemma/Proposition/Theorem/Corollary/Example with content extracted, methods & implementation details, master Table 1 (operator-based semantics) and Table 2 (AF/Op/ADF correspondence) and Fig. 1/Fig. 2 descriptions, limitations, arguments against prior work, design rationale, testable properties (15 propositions/theorems with page numbers), relevance to project (7 specific connections), open questions, notable references with citation keys, and quote bank.
- Wrote `abstract.md` with verbatim Elsevier abstract + a 4-sentence project-aware interpretation.
- Wrote `citations.md` with all 44 references in [N] format and 6 key citations annotated for follow-up.
- Wrote `description.md` (single paragraph, 3 sentences, 5 tags: adf, semantics, approximation-fixpoint-theory, logic-programming, dung-af).
- Verified existing `metadata.json` is correct (title, authors=[Hannes Strass], year 2013, DOI, venue=Artificial Intelligence, vol 205, pages 39-70).

## Steps explicitly skipped (per task instructions)
- Step 7 (reconcile skill) — instructed not to invoke.
- Step 8 (papers/index.md update) — instructed not to invoke.
- Step 9 (provenance stamp via `pks source stamp-provenance`) — instructed not to invoke source-bootstrap-related skills.
- All downstream propstore steps (source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote) — explicitly forbidden.

## Key findings (paper-level)
- **Single-operator framework:** The characteristic operator G_Ξ : 2^S × 2^S → 2^S × 2^S is a 4-valued one-step consequence operator on the bilattice; *all* major ADF semantics (KK, supported, stable, well-founded, M-/L-supported, M-/L-stable, admissible, complete, preferred, semi-stable, stage, naive) are fixpoints/extremal fixpoints of G_Ξ or its DMT-derived stable operator SG_Ξ. This unifies what BW [3] gave only ad-hoc per-semantics for bipolar ADFs.
- **PFM translations as expressiveness probe:** Strass uses polynomial-faithful-modular translations as a *strict* expressiveness ordering on NMR formalisms (Fig. 2): AFs → ADFs → LPs → DL → AEL with PFM translations existing only in this direction. ADFs → LPs (Theorem 3.15) and AFs → LPs (Theorems 4.13, 4.16) are PFM; LPs → ADFs (BW [3]) and ADFs → AFs (Brewka et al. [4]) are dotted (non-modular, faithful only for 2-valued stable).
- **AF operator collapse:** Lemma 4.2 proves SF_Θ = F_Θ — the AF characteristic operator IS its own stable operator. Consequence: for AFs, supported = stable, well-founded = Kripke-Kleene, naive ≠ preferred but the "interesting" operator-based distinctions disappear. AFs are *strictly less* expressive than ADFs/LPs.
- **Equivalence of standard and Dung AF→LP translations (Theorem 4.14):** The "folklore" translation Π(Θ) = {a ← not Attackers(a)} and Dung's original Π_D(Θ) = {a ← not -a} ∪ {-a ← b} produce equivalent semantics under the coherent-pair lift co(S,P) = (S ∪ -P̄, P ∪ -S̄). This was open before Strass.
- **BW-stable cannot be captured by any approximating operator (Prop 3.8):** Two distinct operator-based 2-valued stable models cannot be in subset relation, but BW-stable models can be (Example 3.2: {a} and {a,b} both BW-stable for a self-supporting cycle). Strass introduces a new operator-inspired reduct (Definition 3.2) that works for *all* ADFs (not just bipolar) and coincides with operator-based 2-valued stable semantics (Prop 3.9).
- **BW-well-founded is the *ultimate* approximation:** Lemma 3.12 — BW's grounded operator Γ_Ξ equals the Denecker-Marek-Truszczyński 2004 ultimate approximation U_Ξ of G_Ξ, conjectured by Truszczyński. So BW-grounded ≠ standard well-founded lfp(SG_Ξ) in general (D example: BW = ({a},{a,b,c,d}), standard = ({a,d},{a,d})).

## Relevance to argumentation/ codebase
1. **ASP-backend workstream (notes/workstream-asp-backend-2026-05-01.md):** Theorem 4.13/4.16 is the textbook foundation; Strass extends Wu et al. [43] from complete to preferred (M-supported), semi-stable (L-supported), and stable (2-valued). Together with Egly-Gaggl-Woltran [15] (task #9 in queue) this gives the canonical ASP encoding stack for AF reasoning.
2. **ADF reasoning paths:** Any ADF implementation should follow Strass's operator scheme over BW's ad hoc reducts. The asymmetry "supported = stable for AFs, supported ≠ stable for ADFs" must be preserved — relevant to anyone implementing ADF semantics in our codebase.
3. **Conflict-free pair definition (asymmetric, Definition 5.3):** Justifies a particular labelling-based conflict-freeness check for QBAFs and gradual semantics that may differ from intuitive symmetric formulations.

## Usefulness Assessment

**Rating:** High

**What it provides:**
- Canonical operator-based formulation of ADF semantics that should anchor any ADF infrastructure in argumentation/.
- PFM AF↔LP correspondence (Theorems 4.13, 4.16) for ASP encodings of preferred/semi-stable/stable.
- Master Table 1 (operator-based semantics on a bilattice) and Fig. 1 (inclusion lattice) — directly useful as a semantic-design reference card.
- Unifying picture (Fig. 2) of where AFs and ADFs sit in the broader NMR landscape.
- 44-reference bibliography giving a near-complete entry point into ADF/AFT/argumentation-LP literature circa 2013.

**Actionable next steps:**
- When implementing ADF reasoning: implement G_Ξ first, derive everything else as fixpoints (avoid BW's per-semantics ad hoc machinery).
- For ASP backend: encode AFs via standard translation Π(Θ) (Theorem 4.13); for modularity over attacks consider Dung's Π_D (Theorem 4.16); both yield same semantics.
- For ADF→LP routing: standard translation Π(Ξ) is linear, modular per disjoint statements, faithful for all approximation-operator semantics. Use it.
- Cross-reference with Egly-Gaggl-Woltran 2010 [15] (in our collection, task #9) for concrete ASP encodings of preferred/semi-stable that operationalise Strass's correspondence.
- Cross-reference with Brewka et al. 2013 [5] (ADFs revisited) for *ultimate* ADF semantics not covered by Strass.

**Skip if:**
- Working purely on numerical/gradual semantics (h-categoriser, weighted h, QBAFs) where extension semantics are not used — Strass is purely extension-based.
- Working on structured argumentation (ASPIC+, DeLP, defeasible logic) without need for ADF or operator-based abstraction — Strass is at the abstract end of the spectrum.
- Need only Dung AF basics — Dung 1995 [14] suffices; Strass adds value only when ADF semantics or operator-based reformulations of AF semantics are needed.

## Status
- All paper-reader artifacts created.
- Downstream propstore ingestion (claims, predicates, rules, context, source promotion, reconcile, index update) explicitly NOT performed per task instructions.
- Task #8 in the active task list remains in_progress pending caller's downstream-pipeline decision.
