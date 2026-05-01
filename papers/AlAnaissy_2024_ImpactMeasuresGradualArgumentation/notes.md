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
Defines and axiomatically evaluates two impact measures for QBAFs -- a revised removal-based measure (ImpS^rev) and a new Shapley-value-based measure (ImpSh) -- across four gradual semantics, providing principled tools for explaining how arguments affect each other's scores.

## Problem Addressed
Gradual argumentation semantics compute numeric strength scores for arguments, but interpreting these scores is difficult. An impact measure quantifies, for each argument, the effect of other arguments on its score. The existing impact measure from Delobelle and Villata (2019) has deficiencies (e.g., the self-attacking argument problem), and no Shapley-value-based measure existed for this setting. *(p.1)*

## Key Contributions
- Revised version of the Delobelle & Villata impact measure (ImpS^rev) that fixes the self-attack problem *(p.4)*
- Novel Shapley-value-based impact measure (ImpSh) for gradual argumentation *(p.5-6)*
- Nine axiomatic principles for evaluating impact measures *(p.7-9)*
- Full analysis of which principles are satisfied by each measure under four gradual semantics *(p.10)*
- Proof that the counting semantics is the only one (of the four studied) satisfying both Independence and Directionality *(p.10)*

## Methodology
The paper works within the framework of Quantitative Bipolar Argumentation Frameworks (QBAFs). It defines impact measures as functions that quantify how a set of arguments X affects the score of a target argument x. Two measures are proposed: one based on argument removal (revised from prior work) and one based on Shapley values from cooperative game theory. Both are evaluated against a set of desirable axiomatic principles across four well-known gradual semantics. *(p.1-2)*

## Key Equations / Statistical Models

### Argumentation Framework
$$
AS = (\mathcal{A}, \mathcal{C}, w)
$$
Where: $\mathcal{A}$ is a set of arguments, $\mathcal{C} \subseteq \mathcal{A} \times \mathcal{A}$ is the attack relation, $w: \mathcal{A} \to [0,1]$ is the initial weighting.
*(p.2)*

### Attack Structure
$$
\text{Dir}(x) = \{(y, x) \mid (y, x) \in \mathcal{C}\}
$$
$$
\text{Att}(x) = \{y \mid (y, x) \in \mathcal{C}\}
$$
Where: $\text{Dir}(x)$ is the set of direct attacks on $x$, $\text{Att}(x)$ is the set of direct attackers of $x$.
*(p.2)*

### h-Categoriser Semantics
$$
\sigma_{h\text{-cat}}(a_i) = \frac{w(a_i)}{1 + \sum_{(a_j, a_i) \in \mathcal{C}} \sigma_{h\text{-cat}}(a_j)}
$$
Where: $w(a_i)$ is the initial weight of $a_i$, the sum is over all direct attackers.
*(p.2)*

### Card-Based Semantics
$$
\sigma_{\text{Card}}(a_i) = \frac{1}{2} \left(1 + \frac{v_i^+ - v_i^-}{1 + v_i^+ + v_i^-}\right)
$$
Where: $v_i^+$ counts the proponents, $v_i^-$ counts the opponents of argument $a_i$, computed recursively considering the number of direct attackers and their degrees.
*(p.2)*

### Max-Based Semantics
$$
\sigma_{\text{Max}}(a_i) = \frac{1}{2} \left(1 + \frac{g(v^+) - g(v^-)}{1 + g(v^+) + g(v^-)}\right)
$$
Where: $g$ is a function mapping multisets to values, $v^+$ and $v^-$ are multisets of proponent and opponent scores.
*(p.3)*

### Counting Semantics (Pu et al.)
The counting semantics converts an AF into a matrix $M$, where $M$ is an $N \times N$ normalization factor and $\mathcal{A}$ is the $n$-dimensional column vector of initial weights. The score is: *(p.3)*
$$
\sigma_{\text{count}}(a_i) = \lim_{n \to \infty} \left(\sum_{k=0}^{n} \frac{(-1)^k M^k}{k!}\right) \cdot \mathcal{A}
$$
Where: $M$ is the adjacency matrix, the model of $e^{-M}$ is the counting model, $(-1)^k$ alternates attack polarity.

### Acceptability Degree (for counting semantics)
$$
\text{Deg}_{AS}(a_i) = w(a_i) \cdot e^{-\sum_{(a_j, a_i) \in \mathcal{C}} \text{Deg}_{AS}(a_j)}
$$
Where: the exponential decay captures the cumulative effect of attackers.
*(p.3)*

### Original Impact Measure (Delobelle & Villata 2019)
$$
\text{Imp}_{AS}^{\sigma}(X, x) = \sigma_{AS \setminus X}(x) - \sigma_{AS}(x)
$$
Where: $AS \setminus X$ removes all arguments in $X$ and their associated attacks, $\sigma$ is a gradual semantics.
*(p.4)*

### Revised Impact Measure (ImpS^rev) - Definition 12
$$
\text{Imp}_{AS}^{\sigma, \text{rev}}(X, x) = \sigma_{AS'}(x) - \sigma_{AS}(x)
$$
Where: $AS' = (\mathcal{A}, \mathcal{C}')$ with $\mathcal{C}' = \mathcal{C} \setminus \{(y, x) \mid y \in X, (y, x) \in \mathcal{C}\}$. Instead of removing arguments entirely, it removes only the direct attacks from $X$ to $x$, preserving the rest of the framework structure. This fixes the self-attack problem.
*(p.4)*

### Shapley Measure (Definition 13)
$$
\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N|-|S|-1)!}{|N|!} [v(S \cup \{i\}) - v(S)]
$$
Where: $\phi_i(v)$ is the Shapley value of player $i$ in game $v$, $N$ is the set of players, $S$ ranges over subsets not containing $i$.
*(p.5)*

### Shapley-Based Impact Measure (ImpSh) - Definition 14
$$
\text{Imp}_{AS}^{\sigma, \text{Sh}}(x, \cdot) = \sum_{z \in P(x, z, \text{even})} \phi_z - \sum_{z \in P(x, z, \text{odd})} \phi_z
$$
More precisely: *(p.6)*
$$
\text{Imp}_{AS}^{\sigma, \text{Sh}}(x) = \sum_{z \in \text{Att}(x)} \phi_z(v_x)
$$
Where: $P(x, z, \text{even/odd})$ are the set of all odd/even paths from $z$ to $x$, $\phi_z$ is the Shapley value of $z$ in the coalition game $v_x$ defined for target $x$.

The coalition game $v_x$ for target argument $x$ is defined as:
$$
v_x(S) = \sigma_{AS}(x) - \sigma_{AS \setminus S}(x)
$$
Where: $S \subseteq \mathcal{A} \setminus \{x\}$, this measures how much coalition $S$ contributes to changing $x$'s score.
*(p.6)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Initial weight | $w(a_i)$ | — | — | [0, 1] | 2 | Weight assigned to each argument |
| Acceptability degree | $\text{Deg}_{AS}(a_i)$ | — | — | [0, 1] | 3 | Output of gradual semantics |
| Impact value | $\text{Imp}(X, x)$ | — | — | [-1, 1] | 4 | Impact of set X on argument x |
| Shapley value | $\phi_i(v)$ | — | — | (-∞, ∞) | 5 | Shapley contribution of player i |

## Methods & Implementation Details
- Impact measures operate on QBAFs with attack-only relations (no support) *(p.2)*
- The revised measure (ImpS^rev) removes only direct attacks from X to x, not the arguments themselves. This preserves the graph structure and avoids the self-attack problem where removing a self-attacking argument changes its own score *(p.4)*
- For the Shapley measure, a cooperative game $v_x$ is defined for each target argument $x$. The game assigns to each coalition $S$ the value $\sigma_{AS}(x) - \sigma_{AS \setminus S}(x)$ *(p.6)*
- Computing Shapley values requires evaluating all $2^n$ subsets where $n = |\mathcal{A}| - 1$, making it exponentially expensive *(p.6)*
- The paper only considers attack relations, not support. Extension to bipolar frameworks is mentioned as future work *(p.11)*

## Figures of Interest
- **Fig 1 (p.2):** Example AF with 7 arguments showing attack structure. Used throughout for examples.
- **Fig 2 (p.6):** Counter-example for Bounded Loss with counting semantics. 3-argument chain.
- **Fig 3 (p.7):** AF with 8 arguments used for Shapley measure observations. Edge labels show red intensity values.
- **Fig 4 (p.7):** Intensity of attacks with Shapley measure for the h-categoriser semantics. Blue = argument degrees, red = impact intensity on edges.
- **Fig 5 (p.9):** Illustration of Impact Symmetry concept.

## Results Summary

### Table 1 (p.5): ImpS^rev values for example AF
Values of $\text{Imp}_{AS}^{\sigma,\text{rev}}(X, x)$ for various semantics with $AS = AS'$, $\mathcal{A}' = \{a_1\}$, and $AS - AS' \setminus X$:
- h-cat: ranges from -0.158 to 0.397
- Card-based: ranges from -0.175 to 0.514
- Max-based: similar ranges
- Counting: 0 to 0.5

### Table 3 (p.10): Properties satisfied by impact measures

| Principle | ImpS^rev h-cat | ImpS^rev Card | ImpS^rev Max | ImpS^rev Count | ImpSh h-cat | ImpSh Card | ImpSh Max | ImpSh Count |
|-----------|-------|------|------|-------|------|------|------|-------|
| Impact Anonymity | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Void Impact | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Impact Independence | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| Balanced Impact | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| Impact Monotonisation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Zero Impact | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Impact Symmetry | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Impact Directionality | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| Bounded Loss | ✓(≥2 args) | ✓ | ✓ | ✗ | ✓(≥2 args) | ✓ | ✓ | ✗ |

*(p.10)*

### Key Theorems
- **Theorem 1 (p.5):** ImpS^rev is a well-defined impact measure for any gradual semantics $\sigma$.
- **Theorem 2 (p.5):** Let $\sigma$ be a gradual semantics and $AS = (\mathcal{A}, \mathcal{C}, w)$ be an AF. ImpS^rev is an impact measure.
- **Theorem 3 (p.6):** The Shapley-based impact measure is well-defined.
- **Proposition 1 (p.3):** The counting semantics does not satisfy Impact Independence and Directionality (for the original measure).
- **Propositions 7-10 (p.10):** Satisfaction results for specific principles.
- **Theorem 4 (p.9):** ImpS^rev satisfies Impact Anonymity, Void Impact, Impact Minimisation, Zero Impact, Impact Symmetry.
- **Theorem 5 (p.9):** ImpSh satisfies Impact Anonymity, Void Impact, Impact Minimisation, Zero Impact, Impact Symmetry.
- **Theorem 6 (p.9):** For ImpS^rev: Impact Independence and Impact Directionality only for counting semantics.

## Limitations
- Both measures only handle attack relations, not support *(p.11)*
- Computing Shapley values is exponential in the number of arguments *(p.6)*
- Only four gradual semantics studied; other semantics (e.g., DF-QuAD, Euler-based) not analyzed *(p.10)*
- Current properties cannot distinguish two semantics that allow the attack to weaken its target but with different degrees of weakening *(p.12)*
- Neither measure captures the difference between complete removal and partial weakening of attack influence *(p.12)*

## Arguments Against Prior Work
- The original Delobelle & Villata (2019) impact measure has the "self-attack problem": when measuring impact of a self-attacking argument, removing it changes its own score, leading to counterintuitive results *(p.4)*
- The original measure removes arguments entirely, which also removes indirect effects through the graph structure *(p.4)*
- Previous work on Attack Removal Monotonicity (Property 3) used a different formulation; this paper shows the counting semantics does not satisfy it *(p.5)*

## Design Rationale
- The revised measure removes only direct attacks (not arguments) to preserve graph structure and avoid the self-attack problem *(p.4)*
- Shapley values chosen because they provide a unique allocation satisfying efficiency, symmetry, dummy player, and additivity axioms from cooperative game theory *(p.5)*
- Principles derived from existing gradual semantics properties (Independence, Directionality from Amgoud & Ben-Naim) adapted to the impact measure setting *(p.8)*
- The choice to study only attack-only frameworks is deliberate to establish foundations before extending to bipolar settings *(p.2)*

## Testable Properties
- For any gradual semantics $\sigma$ and any AF, ImpS^rev(∅, x) = 0 (Void Impact) *(p.8)*
- If argument y does not attack x directly or indirectly, ImpS^rev({y}, x) = 0 (Zero Impact) *(p.8)*
- If two AFs have isomorphic attack structures on x, impact values must be equal (Impact Anonymity) *(p.8)*
- For counting semantics: ImpS^rev is additive over independent subgraphs (Impact Independence) *(p.8)*
- ImpSh always returns a value in [0, σ(x)] when removing only attackers (Bounded Loss, for h-cat with ≥2 args) *(p.6)*
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
- Pu et al. (2021) — Counting semantics — the only semantics satisfying both Independence and Directionality

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
