---
title: "Impact Measures for Gradual Argumentation Semantics"
authors: "Caren Al Anaissy, Jérôme Delobelle, Srdjan Vesic, Bruno Yun"
year: 2024
venue: "arXiv preprint"
doi_url: "https://doi.org/10.48550/arXiv.2407.08302"
produced_by:
  agent: "Claude Opus 4.6 (1M context)"
  skill: "paper-reader"
  timestamp: "2026-03-28T22:25:33Z"
---
# Impact Measures for Gradual Argumentation Semantics

## One-Sentence Summary
Defines and axiomatically evaluates two impact measures for attack-only AFs -- a revised removal-based measure (ImpDV) and a Shapley-based path measure (ImpSI) -- across four gradual semantics. *(Definitions 1,12,14; `pngs/page-001.png`, `pngs/page-003.png`, `pngs/page-005.png`)*

## Problem Addressed
Gradual argumentation semantics compute numeric strength scores for arguments, but interpreting these scores is difficult. An impact measure quantifies, for each argument, the effect of other arguments on its score. The existing impact measure from Delobelle and Villata (2019) has deficiencies (e.g., the self-attacking argument problem), and no Shapley-value-based measure existed for this setting. *(p.1)*

## Key Contributions
- Revised version of the Delobelle & Villata impact measure (ImpS^rev) that fixes the self-attack problem *(p.4)*
- Novel Shapley-value-based impact measure (ImpSh) for gradual argumentation *(p.5-6)*
- Nine axiomatic principles for evaluating impact measures *(p.7-9)*
- Full analysis of which principles are satisfied by each measure under four gradual semantics *(p.10)*
- Counting semantics is the only one of the four studied that violates Independence and Directionality; both impact measures inherit the corresponding impact-property violations. *(Proposition 1 and Table 3, printed pp.3,10, `pngs/page-002.png`, `pngs/page-009.png`)*

## Methodology
The paper works with attack-only AFs. It defines impact measures as functions that quantify how a set of arguments X affects the score of a target argument x. Two measures are proposed: one based on deletion operators and one based on Shapley attack contributions composed along paths. Both are evaluated across four gradual semantics. *(Definitions 1,12-14; printed pp.2,4,6, `pngs/page-001.png`, `pngs/page-003.png`, `pngs/page-005.png`)*

## Key Equations / Statistical Models

### Argumentation Framework
$$
AS = (\mathcal{A}, \mathcal{C})
$$
Where $\mathcal{A}$ is a finite argument set and $\mathcal{C}$ is the attack relation. A gradual semantics assigns an output weighting; an initial-weight function is not part of the AF. *(Definitions 1,3-4, printed p.2, `pngs/page-001.png`)*

### Attack Structure
$$
\operatorname{Str}_{AS}(x) = \{x\}\cup\{y\in\mathcal{A}\mid\text{there is a path from }y\text{ to }x\}
$$
$$
\text{Att}(x) = \{y \mid (y, x) \in \mathcal{C}\}
$$
Here $\operatorname{Str}_{AS}(x)$ is the attack structure (including indirect attackers and defenders), and $\operatorname{Att}(x)$ is the direct-attacker set. Also $\operatorname{Arg}^-(X)=\{y\in\mathcal{A}\setminus X\mid\exists x\in X:(y,x)\in\mathcal{C}\}$ and $\operatorname{Att}^-(X)=\{(y,x)\in\mathcal{C}\mid y\in\operatorname{Arg}^-(X),x\in X\}$. *(Definitions 1-2, printed p.2, `pngs/page-001.png`)*

### h-Categoriser Semantics
$$
\sigma_{h\text{-cat}}(a_i) = \frac{1}{1 + \sum_{a_j\in\operatorname{Att}(a_i)} \sigma_{h\text{-cat}}(a_j)}
$$
The numerator is 1 and the sum is over direct attackers. *(Definition 5, printed p.3, `pngs/page-002.png`)*

### Card-Based Semantics
$$
\sigma_{\text{Card}}(a_i) = \frac{1}{1+|\operatorname{Att}(a_i)|+\dfrac{\sum_{a_j\in\operatorname{Att}(a_i)}\sigma_{\text{Card}}(a_j)}{|\operatorname{Att}(a_i)|}}
$$
This combines attacker cardinality with the mean attacker degree, rather than a proponent/opponent difference. *(Definition 6, printed p.3, `pngs/page-002.png`)*

### Max-Based Semantics
$$
\sigma_{\text{Max}}(a_i) = \frac{1}{1+\max_{a_j\in\operatorname{Att}(a_i)}\sigma_{\text{Max}}(a_j)}
$$
The strongest direct attacker determines the denominator. *(Definition 7, printed p.3, `pngs/page-002.png`)*

### Counting Semantics (Pu et al.)
The counting semantics uses the adjacency matrix $M$, normalization factor $N$, normalized matrix $\widetilde M=M/N$, damping $\alpha\in(0,1)$, and all-ones vector $\mathcal I$. *(Definition 8, printed p.3, `pngs/page-002.png`)*
$$
v_\alpha=\lim_{k\to\infty}\sum_{i=0}^{k}(-1)^i\alpha^i\widetilde M^i\mathcal I,\qquad \sigma_{\text{count}}(a_i)=(v_\alpha)_i
$$
This is an alternating damped matrix series, without factorials; it is not a matrix exponential or an exponential-decay recurrence. *(printed p.3, `pngs/page-002.png`)*

### Original Impact Measure (Delobelle & Villata 2019)
$$
\operatorname{ImpDV}_{AS}^{\sigma}(X,y)=\sigma_{AS\ominus_y^{\mathcal A}\operatorname{Arg}^-(X)}(y)-\sigma_{AS\ominus_y^{\mathcal A}X}(y)
$$
The first term deletes external attacker arguments of X; the second deletes X. The target-preserving operator $AS\ominus_y^{\mathcal A}X$ keeps y as a node if y belongs to X, but removes every attack with an endpoint in X. *(Definitions 10-11, printed p.4, `pngs/page-003.png`)*

### Revised Impact Measure (ImpS^rev) - Definition 12
$$
\operatorname{ImpDV}_{AS}^{\sigma}(X,y)=\sigma_{AS\ominus^{\mathcal C}\operatorname{Att}^-(X)}(y)-\sigma_{AS\ominus_y^{\mathcal A}X}(y)
$$
The first term removes external attacks **into X**, not attacks from X to y. The second term still removes X using the target-preserving argument-deletion operator. *(Definitions 10,12, printed p.4, `pngs/page-003.png`)*

### Extended Shapley Attack Measure (Definition 13)
$$
s((b,a))=\sum_{X\subseteq Y}\frac{|X|!(n-|X|-1)!}{n!}\left(\sigma_{AS\ominus^{\mathcal C}(X\cup\{(b,a)\})}(a)-\sigma_{AS\ominus^{\mathcal C}X}(a)\right)
$$
Here $Y=\{(z,a)\mid z\in\operatorname{Att}(a)\}\setminus\{(b,a)\}$ and $n=|\operatorname{Att}(a)|$. Players are incoming attacks, and each marginal is the gain from deleting one more attack. The extended range is [-1,1]. *(printed p.6, `pngs/page-005.png`)*

### Shapley-Based Impact Measure (ImpSh) - Definition 14
$$
\operatorname{ImpSI}_{AS}^{\sigma}(X,a)=\sum_{x\in X}\operatorname{ImpSI}_{AS}^{\sigma}(\{x\},a)
$$
The singleton impact composes edge contributions along paths: *(printed p.6, `pngs/page-005.png`)*
$$
\operatorname{ImpSI}_{AS}^{\sigma}(\{x\},a)=\sum_{(a_1,\ldots,a_n)\in P_E(x,a)}\prod_{i=1}^{n-1}s((a_{i+1},a_i))-\sum_{(a_1,\ldots,a_n)\in P_O(x,a)}\prod_{i=1}^{n-1}s((a_{i+1},a_i))
$$
Here $P_E$ and $P_O$ are even and odd paths from x to a. The displayed indexing follows Definition 14; this measure uses products of attack Shapley values, not a Shapley game whose players are arbitrary argument subsets. *(printed p.6, `pngs/page-005.png`)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Output weighting | $\sigma_{AS}(a_i)$ | — | — | [0, 1] | 2 | Degree assigned by the semantics, not an initial AF weight |
| Acceptability degree | $\text{Deg}_{AS}(a_i)$ | — | — | [0, 1] | 3 | Output of gradual semantics |
| Impact value | $\text{Imp}(X, x)$ | — | — | [-1, 1] | 4 | Impact of set X on argument x |
| Shapley value | $\phi_i(v)$ | — | — | (-∞, ∞) | 5 | Shapley contribution of player i |

## Methods & Implementation Details
- Impact measures operate on attack-only AFs. *(Definition 1, printed p.2, `pngs/page-001.png`)*
- Revised ImpDV compares deletion of external incoming attacks to X against target-preserving deletion of X. *(Definition 12, printed p.4, `pngs/page-003.png`)*
- The Shapley measure enumerates coalitions of the other incoming attacks to each target; ImpSI then combines edge values along even and odd paths. For one edge the coalition count is $2^{|\operatorname{Att}(a)|-1}$. *(Definitions 13-14, printed p.6, `pngs/page-005.png`)*
- The paper only considers attack relations, not support. Extension to bipolar frameworks is mentioned as future work *(p.11)*

## Figures of Interest
- **Fig 1 (p.2):** Example AF with 7 arguments showing attack structure. Used throughout for examples.
- **Fig 2 (p.6):** Counterexample to Attack Removal Monotonicity for counting semantics; adding $(a_2,a_3)$ raises $a_3$ from 0.02 to 0.26. *(`pngs/page-005.png`)*
- **Fig 3 (p.7):** AF with 8 arguments used for Shapley measure observations. Edge labels show red intensity values.
- **Fig 4 (p.7):** Intensity of attacks with Shapley measure for the h-categoriser semantics. Blue = argument degrees, red = impact intensity on edges.
- **Fig 5 (p.9):** Illustration of Impact Symmetry concept.

## Results Summary

### Table 1 (p.5): ImpS^rev values for example AF
Table 1 reports **only h-categoriser**, with revised impacts 0.015, -0.158, -0.175, 0.07, and 0 for the five displayed (X,y) pairs. Values such as 0.397 and 0.514 are component framework scores, not impacts or results for other semantics. *(printed p.5, `pngs/page-004.png`)*

### Table 3 (p.10): Properties satisfied by impact measures

| Principle | ImpS^rev h-cat | ImpS^rev Card | ImpS^rev Max | ImpS^rev Count | ImpSh h-cat | ImpSh Card | ImpSh Max | ImpSh Count |
|-----------|-------|------|------|-------|------|------|------|-------|
| Impact Anonymity | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Void Impact | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Impact Independence | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Balanced Impact | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Impact Minimisation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Zero Impact | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Impact Symmetry | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Impact Directionality | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Impact Existence | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓(≥2 max-indegree args) |

The table uses ImpDV for the revised measure and ImpSI for the Shapley-based path measure. The qualification concerns at least two arguments attaining maximum in-degree, not merely two arguments. Bounded Loss is a separate semantics property and is conjectured in Section 3.2; it is not a Table 3 row. *(printed pp.6,10, `pngs/page-005.png`, `pngs/page-009.png`)*

### Key Theorems
- **Theorem 2 (p.5):** Revised ImpDV is an impact measure for any gradual semantics. *(`pngs/page-004.png`)*
- **Theorem 3 (p.6):** If $\sigma$ satisfies Attack Removal Monotonicity, then $\operatorname{ImpSI}_{AS}^{\sigma}(\mathcal A,x)\in[-1,0]$. *(`pngs/page-005.png`)*
- **Proposition 1 (p.3):** Counting semantics violates the semantics-level Independence and Directionality properties. *(`pngs/page-002.png`)*
- **Propositions 7-10 (p.10):** Satisfaction results for specific principles.
- **Theorem 4 (p.9):** Impact Anonymity, Impact Directionality, Impact Minimisation and Impact Independence jointly imply Impact Symmetry. *(`pngs/page-008.png`)*
- **Theorem 5 (p.9):** Zero Impact and Balanced Impact jointly imply Impact Minimisation. **Theorem 6:** Void Impact and Impact Minimisation jointly imply Zero Impact. *(`pngs/page-008.png`)*
- **Propositions 7-8 (p.10):** Both measures satisfy Impact Independence/Directionality when the underlying semantics satisfies Independence/Directionality. Counting is the studied exception. *(`pngs/page-009.png`)*

## Limitations
- Both measures only handle attack relations, not support *(p.11)*
- Computing Shapley values is exponential in the number of arguments *(p.6)*
- Only four gradual semantics studied; other semantics (e.g., DF-QuAD, Euler-based) not analyzed *(p.10)*
- Current properties cannot distinguish two semantics that allow the attack to weaken its target but with different degrees of weakening *(p.12)*
- Neither measure captures the difference between complete removal and partial weakening of attack influence *(p.12)*

## Arguments Against Prior Work
- The original measure gives a self-attacking argument zero self-impact; the revised measure separates the retained self-attacking graph from the isolated retained target, producing a negative self-impact (about -0.382 for h-categoriser). *(printed pp.4-5, `pngs/page-003.png`, `pngs/page-004.png`)*
- The original measure removes arguments entirely, which also removes indirect effects through the graph structure *(p.4)*
- Previous work on Attack Removal Monotonicity (Property 3) used a different formulation; this paper shows the counting semantics does not satisfy it *(p.5)*

## Design Rationale
- The revised measure changes the first term from deleting external attackers of X to deleting their attacks into X, preserving their other effects; the second term still deletes X with the target-preserving operator. *(printed p.4, `pngs/page-003.png`)*
- Shapley values chosen because they provide a unique allocation satisfying efficiency, symmetry, dummy player, and additivity axioms from cooperative game theory *(p.5)*
- Principles derived from existing gradual semantics properties (Independence, Directionality from Amgoud & Ben-Naim) adapted to the impact measure setting *(p.8)*
- The choice to study only attack-only frameworks is deliberate to establish foundations before extending to bipolar settings *(p.2)*

## Testable Properties
- For any gradual semantics $\sigma$ and any AF, ImpS^rev(∅, x) = 0 (Void Impact) *(p.8)*
- If argument y does not attack x directly or indirectly, ImpS^rev({y}, x) = 0 (Zero Impact) *(p.8)*
- If two AFs have isomorphic attack structures on x, impact values must be equal (Impact Anonymity) *(p.8)*
- For Hbs, Car and Max, both impact measures satisfy Impact Independence and Directionality; counting violates them. *(Table 3, printed p.10, `pngs/page-009.png`)*
- Bounded Loss means $|s((a,b))|\le\sigma_{AS}(a)$; the paper conjectures it for all four studied semantics. It is not a proven [0,σ(x)] impact bound. *(Property 4 and Conjecture 1, printed p.6, `pngs/page-005.png`)*
- For h-cat semantics: ImpS^rev({y}, x) = ImpS^rev({z}, x) when y and z are structurally symmetric attackers of x (Impact Symmetry) *(p.9)*

## Relevance to Project
This paper is directly relevant to propstore's argumentation layer. The project already implements DF-QuAD gradual semantics (Freedman et al. 2025) and Dung AFs. Impact measures would provide an explainability layer for the gradual semantics -- explaining *why* an argument received its score by quantifying the contribution of each attacker. The Shapley-based measure is particularly interesting for the render layer, where users need to understand how different arguments affected outcomes. However, the exponential complexity of Shapley computation is a concern for practical deployment.

## Open Questions
- [ ] How do these impact measures extend to bipolar frameworks (with support)?
- [ ] Can the Shapley measure be efficiently approximated for large frameworks?
- [ ] How do ImpS^rev and ImpSh behave under DF-QuAD semantics (not studied in this paper)?
- [ ] Can impact measures be composed with the ATMS layer for explaining assumption-based results?

## Collection Cross-References

### Already in Collection
- [[Rago_2016_DiscontinuityFreeQuAD]] — cited as ref [23]; DF-QuAD is a gradual semantics not studied in this paper but relevant as propstore's primary gradual semantics
- [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]] — cited implicitly via Amgoud & Ben-Naim's axiomatic approach to ranking-based semantics, which this paper adapts for impact measures
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — cited as ref [12]; comparative study of ranking-based semantics properties, directly relevant as this paper extends that axiomatic analysis to impact measures
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — cited as ref [37]; equational approach to argumentation
- [[Freedman_2025_ArgumentativeLLMsClaimVerification]] — not directly cited but uses DF-QuAD, which this paper's impact measures could be applied to

### New Leads (Not Yet in Collection)
- Delobelle and Villata (2019/2020) — "Interpretability of gradual semantics in abstract argumentation" — original impact measure that this paper revises; essential predecessor
- Kampik et al. (2024) — "Contribution functions for quantitative bipolar argumentation graphs" — parallel approach to QBAF explainability using contribution functions
- Yun et al. (2023) — "Argument attribution explanations in quantitative bipolar argumentation frameworks" — Shapley-based attribution in bipolar setting
- Pu et al. (2015), ref. [32] — Counting semantics, the studied semantics violating Independence and Directionality. *(Proposition 1, printed p.3, `pngs/page-002.png`)*

### Conceptual Links (not citation-based)
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — Both papers perform systematic axiomatic evaluation of gradual semantics properties. Bonzon evaluates the semantics themselves; Al Anaissy evaluates impact measures derived from those semantics. The axiomatic methodology is shared (Independence, Directionality principles originate from the same Amgoud & Ben-Naim lineage).
- [[Matt_2008_Game-TheoreticMeasureArgumentStrength]] — Matt & Toni's game-theoretic argument strength uses cooperative game theory (like Shapley values); Al Anaissy's ImpSh uses Shapley values to measure impact. Different applications of game theory to argumentation: one for computing strength, the other for explaining it.
- [[Čyras_2021_ArgumentativeXAISurvey]] — Survey of argumentative XAI approaches. Impact measures are a specific instance of the explainability methods this survey categorizes.
- [[Rago_2016_DiscontinuityFreeQuAD]] — DF-QuAD is a gradual semantics not studied by Al Anaissy but implemented in propstore. Applying ImpS^rev and ImpSh to DF-QuAD would be a natural extension.

### Cited By (in Collection)
- (none found)

## Related Work Worth Reading
- Delobelle and Villata (2019) - Original impact measure paper [ref 2]
- Amgoud and Ben-Naim (2016/2018) - Acceptability semantics foundations, evaluation of gradual semantics [ref 4, 5]
- Pu et al. (2021) - Counting semantics (the one that satisfies most properties) [ref 22]
- Kampik et al. (2024) - Contribution functions for quantitative bipolar argumentation [ref 16]
- Yun et al. (2021) - Argument attribution explanations in quantitative bipolar argumentation [ref 38]
- Xu and Cayrol (2018/2020) - Contrastive explanations for argumentation [ref 35, 36]
