---
title: "Adapting the DF-QuAD Algorithm to Bipolar Argumentation"
authors: "Antonio Rago, Kristijonas Cyras, Francesca Toni"
year: 2016
venue: "COMMA 2016 Workshop on Systems and Algorithms for Formal Argumentation (SAFA), CEUR-WS Vol-1672"
doi_url: "https://ceur-ws.org/Vol-1672/paper_3.pdf"
produced_by:
  agent: "Claude Opus 4.6 (1M context)"
  skill: "paper-reader"
  timestamp: "2026-03-28T08:08:03Z"
---
# Adapting the DF-QuAD Algorithm to Bipolar Argumentation

## One-Sentence Summary
Defines a quantitative semantics for evaluating argument strength in BAFs (Bipolar Argumentation Frameworks) by adapting the DF-QuAD algorithm from QuAD frameworks, eliminating the need for base scores and providing discontinuity-free gradual evaluation.

## Problem Addressed
The DF-QuAD algorithm [6] was originally defined for QuAD frameworks, which require a base score for every argument. BAFs (Bipolar Argumentation Frameworks) have no base scores — they only have arguments, attacks, and supports. This paper adapts DF-QuAD to work directly on BAFs without requiring base scores. *(p.1)*

## Key Contributions
- Adaptation of the DF-QuAD algorithm to BAFs (without base scores), using a default score of 0.5 for all arguments *(p.1)*
- Definition of three core functions: strength aggregation function (sigma), mediating function (mu), and score function (SF) *(p.2)*
- Proof that the adapted semantics is continuous (discontinuity-free) on [0,1] *(p.3)*
- Proof that QuAD frameworks with base score 0.5 can be seen as restricted BAFs under this semantics *(p.4)*
- Comparison with the gradual valuation of BAFs [9], which differs from the new semantics, and correspondence with social models of SAFs [8] when social support is 0.5. *(printed p.38, `pngs/page-004.png`)*

## Methodology
The paper defines three functions that compose to compute argument strength in a BAF:
1. A strength aggregation function sigma that recursively combines attacker/supporter strengths
2. A mediating function mu that balances aggregated attack and support strengths
3. A score function SF that applies sigma to get aggregated attack/support, then mu to get final strength

The semantics is then proven to satisfy key properties (continuity, saturation, bounded extremes) and shown to correspond to QuAD frameworks when base score = 0.5. *(p.1-3)*

## Key Equations / Statistical Models

### Definition 1: Strength Aggregation Function

$$
\sigma : \mathbb{I}^* \to \mathbb{I}
$$

Where for $S = (v_1, \ldots, v_n) \in \mathbb{I}^*$:
- if $n = 0$: $\sigma(S) = 0$
- if $n = 1$: $\sigma(S) = v_1$
- if $n = 2$: $\sigma(S) = f(v_1, v_2)$
- if $n > 2$: $\sigma(S) = f(\sigma(v_1, \ldots, v_{n-1}), v_n)$

with base function $f : \mathbb{I} \times \mathbb{I} \to \mathbb{I}$:

$$
f(v_1, v_2) = v_1 + (1 - v_1) \cdot v_2 = v_1 + v_2 - v_1 \cdot v_2
$$

*(p.2)*

### Definition 2: Mediating Function

$$
\mu(v_a, v_s) = 0.5 + 0.5 \cdot (v_s - v_a)
$$

Where $v_a$ = aggregated attack strength, $v_s$ = aggregated support strength, $\mu : \mathbb{I} \times \mathbb{I} \to \mathbb{I}$. *(p.2, Eq. 1)*

### Definition 3: Score Function

$$
\mathcal{SF}(a) = \mu(\sigma(SEQ_{\mathcal{SF}}(\mathcal{R}^-(a))), \sigma(SEQ_{\mathcal{SF}}(\mathcal{R}^+(a))))
$$

Where $\mathcal{R}^-(a)$ = set of attackers of $a$, $\mathcal{R}^+(a)$ = set of supporters of $a$, $SEQ_{\mathcal{SF}}$ lists their strengths in an arbitrary permutation; it does not sort by strength. *(printed pp.35,38, `pngs/page-001.png`, `pngs/page-004.png`)*

### Combination Function (from original DF-QuAD [6])

$$
c(v_0, v_a, v_s) = v_0 - v_0 \cdot |v_s - v_a| \quad \text{if } v_a \geq v_s
$$

$$
c(v_0, v_a, v_s) = v_0 + (1 - v_0) \cdot |v_s - v_a| \quad \text{if } v_a < v_s
$$

Where $v_0$ = base score. *(p.4, Eqs. 2-3)*

### Proposition 3: Equivalence at base score 0.5

$$
c(0.5, v_a, v_s) = \mu(v_a, v_s)
$$

The mediating function equals the combination function when base score is 0.5. *(p.4)*

### Explicit closed form of SF

$$
\mathcal{SF}(a) = 0.5 + 0.5 \cdot \left(\prod_{j=1}^{m} (1 - a_j) - \prod_{i=1}^{n} (1 - s_i)\right)
$$

Where $(s_1, \ldots, s_n)$ are the supporter strengths and $(a_1, \ldots, a_m)$ are the attacker strengths. This follows algebraically from the noisy-OR aggregation and $\mu(v_a,v_s)=0.5+0.5(v_s-v_a)$; the attacker product comes first. *(Definitions 1-3, printed p.35, `pngs/page-001.png`)*

### Comparison with Gradual Valuation of BAFs

For the gradual valuation semantics of BAFs [9], the paper gives an equivalent presentation with aggregation $\sigma':[-1,1]^*\to[0,\infty)$:

$$
\sigma'(S) = \sum_{i=1}^{n} \frac{s_i+1}{2}
$$

The mediating function becomes:

$$
\mu' : [0, \infty) \times [0, \infty) \to [-1, 1]
$$

$$
\mu'(v_a, v_s) = \frac{1}{1 + v_a} - \frac{1}{1 + v_s}
$$

The equivalent score function:

$$
\mathcal{SF}'(a) = \mu'\!\left(\sigma'(SEQ_{\mathcal{SF}'}(\mathcal{R}^-(a))),\sigma'(SEQ_{\mathcal{SF}'}(\mathcal{R}^+(a)))\right)
$$

This is a reformulation of the older gradual valuation, not an equivalence between that semantics and the new DF-QuAD adaptation. The separate social-model correspondence is with SAF social support equal to 0.5. *(printed p.38, `pngs/page-004.png`)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Base score (implicit) | v_0 | — | 0.5 | [0,1] | p.4 | Fixed at 0.5 for BAF adaptation; explicit in QuAD |
| Strength aggregation output | sigma | — | — | [0,1] | p.2 | Aggregates attacker or supporter sequence |
| Mediating function output | mu | — | — | [0,1] | p.2 | Balances attack vs support |
| Score function output | SF | — | — | [0,1] | p.2 | Final argument strength |

## Methods & Implementation Details
- BAF is defined as triple (X, R^-, R^+) where X = set of arguments, R^- = attack relation, R^+ = support relation *(p.2)*
- The semantics does NOT require a base score — all arguments implicitly start at 0.5 *(p.2)*
- The strength aggregation function sigma uses a recursive base function f(v1,v2) = v1 + v2 - v1*v2, which is the probabilistic OR *(p.2)*
- sigma is order-independent: its noisy-OR base function is commutative and associative, so the arbitrary permutation does not change the aggregate. *(Definition 1, printed p.35, `pngs/page-001.png`)*
- The adaptation includes possibly cyclic BAFs; acyclicity is a restriction of the original QuAD frameworks. Existence is sketched and uniqueness conjectured. *(Conclusion, printed p.39, `pngs/page-005.png`)*
- Continuity: SF is continuous on [0,1] because it is a composition of continuous functions (the base function f is a polynomial, mu is linear) *(p.3)*
- The product form gives SF(a) = 0.5 + 0.5 * (product(1-a_j) - product(1-s_i)), where a_j are attacker scores and s_i are supporter scores. *(derived from Definitions 1-3, printed p.35, `pngs/page-001.png`)*
- Brouwer's fixed-point theorem guarantees existence of a solution for the score function on BAFs *(p.3)*
- The paper conjectures uniqueness (unique fixed point) but does not prove it — left for future work *(p.3)*

## Figures of Interest
- **Fig 1 (p.3):** Example BAFs with strengths of arguments as indicated. Shows 9 small BAF examples with computed SF values demonstrating the semantics. Notable: SF(a)=SF(b)=0.5 for isolated arguments; attack reduces to 0.25; support increases to 0.75; multiple attackers compound.

## Results Summary
- The adapted DF-QuAD semantics for BAFs is continuous (discontinuity-free) on [0,1] *(p.3)*
- QuAD frameworks with base score 0.5 map to corresponding BAFs with the same strengths; this does not assert that every acyclic BAF is a QuAD framework. *(Proposition 4, printed p.38, `pngs/page-004.png`)*
- The older gradual valuation of BAFs [9] differs: its aggregation $\sigma'$ is unbounded as more maximum-strength arguments are added, unlike the saturating noisy-OR aggregation. Its final strengths remain in [-1,1]. *(printed pp.38-39, `pngs/page-004.png`, `pngs/page-005.png`)*

## Limitations
- Uniqueness of the fixed point (score function solution) is conjectured but NOT proven — left as future work *(p.3)*
- Cyclic BAFs are included, but uniqueness is conjectured and a computational system is left for future work. *(printed p.39, `pngs/page-005.png`)*
- Details of the social-model correspondence and equivalence of the reformulated older gradual valuation to its original presentation are omitted for space. *(printed p.38, `pngs/page-004.png`)*

## Arguments Against Prior Work
- The original DF-QuAD [6] requires base scores for all arguments, which BAFs don't have — this paper removes that requirement *(p.1-2)*
- The older gradual valuation of BAFs [9] uses shifted summation for aggregation, which does not saturate; the adapted DF-QuAD uses noisy-OR. *(printed p.38, `pngs/page-004.png`)*
- The adapted semantics differs from social models in that extreme values 0 and 1 can only be achieved if they are "somehow already present" (Proposition 2) *(p.4)*

## Design Rationale
- Base score fixed at 0.5 to represent "neutral" — no prior evidence for or against the argument *(p.2, p.4)*
- The mediating function mu centers at 0.5 and adjusts based on the difference between support and attack aggregated strengths *(p.2)*
- Probabilistic OR for aggregation (f(v1,v2) = v1+v2-v1*v2) chosen because it proportionally increases attacking/supporting strength towards 1 *(p.2)*
- Continuity is a key design goal — the paper inherits this from the original DF-QuAD's discontinuity-free property *(p.1, p.3)*

## Testable Properties
- For any argument a with no attackers and no supporters: SF(a) = 0.5 *(p.2-3)*
- Saturation: sigma(S ∪ (1)) = 1 for any sequence S (Proposition 1) *(p.4)*
- Extreme values: SF(a) = 0 iff v_a = 1 and v_s = 0; SF(a) = 1 iff v_a = 0 and v_s = 1 (Proposition 2) *(p.4)*
- Equivalence: c(0.5, v_a, v_s) = mu(v_a, v_s) for all v_a, v_s in [0,1] (Proposition 3) *(p.4)*
- Continuity: SF is continuous on [0,1] *(p.3)*
- Range: SF(a) is always in [0,1] for any argument a in an acyclic BAF *(p.2-3)*
- Base function: f(v1,v2) = v1 + v2 - v1*v2 (probabilistic OR) *(p.2)*
- Closed form: SF(a) = 0.5 + 0.5*(prod(1-a_j) - prod(1-s_i)), with a_j attacker strengths and s_i supporter strengths. *(derived from printed p.35, `pngs/page-001.png`)*

## Relevance to Project
This paper is directly relevant to propstore's DF-QuAD implementation. The current implementation (noted in CLAUDE.md as "DF-QuAD gradual semantics for quantitative bipolar argumentation frameworks — but P_A conflated with base score") uses the original QuAD formulation. This paper provides the BAF adaptation which eliminates the need for base scores entirely, using a fixed 0.5 default. The key equations (sigma, mu, SF) and their closed forms are directly implementable. The saturation property and extreme value propositions provide testable invariants.

## Open Questions
- [ ] Is the fixed point unique? (conjectured but unproven)
- [ ] Which numerical solution methods perform best on the possibly cyclic BAFs allowed by the adaptation?
- [ ] How does this relate to our current DF-QuAD implementation's P_A/base-score conflation?

## Collection Cross-References

### Already in Collection
- [[Rago_2016_DiscontinuityFreeQuAD]] — cited as [6], the parent paper. This COMMA workshop paper adapts DF-QuAD from that KR paper to work on BAFs without base scores.
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — cited as [2]. Foundational BAF paper defining attack and support relations that this paper builds upon.

### New Leads (Not Yet in Collection)
- Amgoud, Ben-Naim, Doder & Vesic (2016) — "Ranking Arguments With Compensation-Based Semantics," KR 2016 — social models with gradual valuation, compared against in Section 3
- Baroni, Romano, Toni, Aurisicchio & Bertanza (2015) — "Automatic Evaluation of Design Alternatives with Quantitative Argumentation," Argument & Computation — original QuAD framework definition
- Matt & Toni (2008) — "A Game-Theoretic Measure of Argument Strength for Abstract Argumentation," JELIA 2008 — alternative strength measure

### Cited By (in Collection)
- (none found — Freedman 2025 cites the KR paper [6] but not this specific COMMA workshop paper)

### Conceptual Links (not citation-based)
- [[Freedman_2025_ArgumentativeLLMsClaimVerification]] — **Strong.** Freedman uses DF-QuAD gradual semantics for QBAF evaluation and proves base score monotonicity and argument relation contestability properties. This COMMA paper's BAF adaptation (removing base scores, fixing at 0.5) is exactly the formulation Freedman's ArgLLMs pipeline implicitly uses when it starts arguments at a neutral baseline.
- [[Amgoud_2008_BipolarityArgumentationFrameworks]] — **Strong.** Amgoud 2008 surveys BAF formalisms and defines a local gradual valuation for bipolar frameworks. This paper provides a specific, concrete gradual semantics (DF-QuAD adapted) for the same BAF structures, offering an alternative to Amgoud's approach with provably different properties (saturation vs unbounded).
- [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]] — **Moderate.** Amgoud 2013 provides axiomatic foundations for ranking-based semantics. This paper's DF-QuAD adaptation produces a ranking (via score function values) but does not explicitly check against Amgoud's axioms.

## Related Work Worth Reading
- [1] L. Amgoud, J. Ben-Naim, D. Doder, S. Vesic, "Ranking Arguments With Compensation-Based Semantics," KR 2016 (social models, gradual valuation)
- [6] A. Rago, F. Toni, M. Aurisicchio & P. Baroni, "Discontinuity-Free Decision Support with Quantitative Argumentation Debates," KR 2016 (the original DF-QuAD paper)
- [7] P. Baroni, M. Romano, F. Toni, M. Aurisicchio & G. Bertanza, "Automatic Evaluation of Design Alternatives with Quantitative Argumentation," Argument & Computation, 2015 (QuAD frameworks)
- [3] P. Matt & F. Toni, "A Game-Theoretic Measure of Argument Strength for Abstract Argumentation," JELIA 2008 (game-theoretic strength measures for AFs)
- [5] A. Hunter & M. Thimm, "On Partial Information and Contradictions in Probabilistic Abstract Argumentation," KR 2016 (probabilistic approaches)
