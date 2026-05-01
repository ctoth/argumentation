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
- Comparison with the gradual valuation of social models of AFs [1] and equivalence to Euler-based semantics *(p.5)*
- Extension to social models (SAFs) by defining equivalent aggregation and mediating functions *(p.5)*

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

Where $\mathcal{R}^-(a)$ = set of attackers of $a$, $\mathcal{R}^+(a)$ = set of supporters of $a$, $SEQ_{\mathcal{SF}}$ is an arbitrary permutation of the attacker/supporter sets ordered by their SF scores. *(p.2-3)*

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
\mathcal{SF}(a) = 0.5 + 0.5 \cdot \left(\prod_{i=1}^{n} (1 - s_i) - \prod_{j=1}^{m} (1 - a_j)\right)
$$

Where $(s_1, \ldots, s_n)$ are the (n >= 0) supporter strengths and $(a_1, \ldots, a_m)$ are the (m >= 0) attacker strengths, after recursive evaluation. This is the closed form derived from iterating the base function. *(p.3)*

### Gradual Valuation Equivalence (Social Models)

For equivalence with social models of AFs [1], the aggregation function is redefined on $\mathbb{Z}^* \to \mathbb{R}$:

$$
\sigma'(S) = \sum_{i=1}^{n} s_i
$$

The mediating function becomes:

$$
\mu' : [0, n] \times [0, m] \to [-1, 1]
$$

$$
\mu'(v_a, v_s) = \frac{1}{1 + v_a} - \frac{1}{1 + v_s}
$$

The equivalent score function:

$$
\mathcal{SF}'(a) = 1 + \sigma'(SEQ_{\mathcal{SF}'}(\mathcal{R}^-(a))) \cdot \sigma'(SEQ_{\mathcal{SF}'}(\mathcal{R}^+(a))) - \mathcal{SF}'(a)(\text{something})
$$

Actually the full formulation is:

$$
\mathcal{SF}'(a) = 1 + \sigma'(SEQ_{\mathcal{SF}'}(\mathcal{R}^-(a)))^{-1} \cdot (1 + \sigma'(SEQ_{\mathcal{SF}'}(\mathcal{R}^+(a))))^{-1}
$$

*(p.5)*

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
- sigma is order-dependent in general, but the paper uses SEQ_SF which is an arbitrary permutation; the SF values are used to sort but the paper notes this is an arbitrary choice *(p.2-3)*
- The score function SF is well-defined because BAFs are acyclic (no cycles in attack/support) *(p.3)*
- Continuity: SF is continuous on [0,1] because it is a composition of continuous functions (the base function f is a polynomial, mu is linear) *(p.3)*
- The product form gives the closed expression: SF(a) = 0.5 + 0.5 * (product(1-s_i) - product(1-a_j)) where s_i are supporter scores and a_j are attacker scores *(p.3)*
- Brouwer's fixed-point theorem guarantees existence of a solution for the score function on BAFs *(p.3)*
- The paper conjectures uniqueness (unique fixed point) but does not prove it — left for future work *(p.3)*

## Figures of Interest
- **Fig 1 (p.3):** Example BAFs with strengths of arguments as indicated. Shows 9 small BAF examples with computed SF values demonstrating the semantics. Notable: SF(a)=SF(b)=0.5 for isolated arguments; attack reduces to 0.25; support increases to 0.75; multiple attackers compound.

## Results Summary
- The adapted DF-QuAD semantics for BAFs is continuous (discontinuity-free) on [0,1] *(p.3)*
- QuAD frameworks with base score 0.5 correspond exactly to acyclic BAFs under this semantics (Proposition 3, Definition 4) *(p.4)*
- The semantics differs from the gradual valuation of social models [1] because it saturates: adding an attacker/supporter with maximum strength saturates sigma at 1 (Proposition 1) *(p.4)*
- For social models [1], the equivalent semantics increases argument strength monotonically with supporter count — no saturation *(p.5)*
- The paper's Proposition 1 on saturation does NOT hold for social model equivalence — the social model version increases unboundedly with more supporters *(p.5)*

## Limitations
- Uniqueness of the fixed point (score function solution) is conjectured but NOT proven — left as future work *(p.3)*
- The semantics only works for acyclic BAFs — cyclic frameworks are not addressed *(p.3-4)*
- Comparison with Euler-based semantics and social models is informal; full formal comparison deferred *(p.5)*
- The order of the permutation SEQ_SF may affect results — the paper acknowledges this is arbitrary *(p.2-3)*

## Arguments Against Prior Work
- The original DF-QuAD [6] requires base scores for all arguments, which BAFs don't have — this paper removes that requirement *(p.1-2)*
- Social models of AFs [1] use simple summation for aggregation, which doesn't saturate — the adapted DF-QuAD uses probabilistic OR which saturates at 1 *(p.4-5)*
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
- Closed form: SF(a) = 0.5 + 0.5*(prod(1-s_i) - prod(1-a_j)) *(p.3)*

## Relevance to Project
This paper is directly relevant to propstore's DF-QuAD implementation. The current implementation (noted in CLAUDE.md as "DF-QuAD gradual semantics for quantitative bipolar argumentation frameworks — but P_A conflated with base score") uses the original QuAD formulation. This paper provides the BAF adaptation which eliminates the need for base scores entirely, using a fixed 0.5 default. The key equations (sigma, mu, SF) and their closed forms are directly implementable. The saturation property and extreme value propositions provide testable invariants.

## Open Questions
- [ ] Is the fixed point unique? (conjectured but unproven)
- [ ] How does order-dependence of SEQ_SF affect results in practice?
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
