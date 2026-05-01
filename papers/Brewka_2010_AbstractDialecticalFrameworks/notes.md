---
title: "Abstract Dialectical Frameworks"
authors: "Gerhard Brewka, Stefan Woltran"
year: 2010
venue: "Proceedings of the Twelfth International Conference on Principles of Knowledge Representation and Reasoning (KR 2010)"
doi_url: "https://dl.acm.org/doi/10.5555/3031843.3031847"
---

# Abstract Dialectical Frameworks

## One-Sentence Summary
Introduces Abstract Dialectical Frameworks (ADFs), a generalization of Dung argumentation frameworks where each node has an arbitrary acceptance condition over its parents, enabling modeling of support, attack, and complex dependency types within a single framework.

## Problem Addressed
Dung's argumentation frameworks only support a single type of relationship between arguments: attack. Real argumentation often involves support, complex dependencies (e.g., joint attack, evidential support), and different types of nodes. Extensions like bipolar AFs (Cayrol and Lagasquie-Schiex 2005) added support but in limited ways. ADFs provide a uniform generalization where acceptance conditions on nodes can express arbitrary Boolean dependencies. *(p.0)*

## Key Contributions
- Definition of Abstract Dialectical Frameworks (ADFs) with per-node acceptance conditions *(p.0)*
- Generalization of Dung's grounded, complete, preferred, and stable semantics to ADFs *(p.1)*
- Identification of bipolar ADFs (BADFs) as the subclass where stable and preferred semantics generalize cleanly *(p.1)*
- Representation of acceptance conditions via weights and priorities on links *(p.6)*
- Modeling of legal proof standards (preponderance of evidence, clear and convincing, beyond reasonable doubt) using weighted ADFs *(p.6-7)*
- Connections to logic programming: ADFs subsume normal logic programs *(p.5)*
- Complexity analysis of ADF reasoning *(p.7)*

## Methodology
The paper defines ADFs as triples D = (S, L, C), then lifts Dung's semantics by defining a consensus operator on three-valued interpretations. It proves that Dung AFs are a special case, shows which properties carry over, identifies the bipolar subclass needed for stable/preferred semantics, and demonstrates practical expressiveness through weighted ADFs and legal proof standard examples. *(p.0-9)*

## Key Equations

### ADF Definition

An ADF is a triple $D = (S, L, C)$ where:
- $S$ is a set of statements (nodes/positions)
- $L \subseteq S \times S$ is a set of links
- $C = \{C_s\}_{s \in S}$ is a set of acceptance conditions, one per statement
Where $C_s$ is a propositional formula over $par(s) = \{b \mid (b,s) \in L\}$
*(p.1)*

### Dung AF as Special Case

For a Dung AF with attackers $a_1, \ldots, a_n$ of node $s$:

$$
C_s = \neg a_1 \wedge \neg a_2 \wedge \cdots \wedge \neg a_n
$$

If $s$ has no attackers: $C_s = \top$
*(p.1)*

### Three-Valued Interpretations

A three-valued interpretation $v: S \to \{t, f, u\}$ partitions $S$ into $(v^t, v^f, v^u)$ — the true, false, and undecided statements. Information ordering: $u <_i t$ and $u <_i f$. *(p.2)*

### Consensus Operator

$$
\Gamma_D(v)(s) = \begin{cases} t & \text{if } C_s[p/v] \text{ is irrefutable (true under all completions of } v \text{)} \\ f & \text{if } C_s[p/v] \text{ is unsatisfiable (false under all completions of } v \text{)} \\ u & \text{otherwise} \end{cases}
$$

Where $C_s[p/v]$ means: replace each parent $p$ of $s$ that has value $t$ by $\top$, value $f$ by $\bot$, and leave undecided parents as propositional variables. Then check if the resulting formula is a tautology (irrefutable), unsatisfiable, or contingent. *(p.2)*

### Grounded Interpretation

$$
\text{grd}(D) = \text{lfp}(\Gamma_D)
$$

The grounded interpretation is the least fixpoint of $\Gamma_D$, starting from the all-undecided interpretation $v_u$ where $v_u(s) = u$ for all $s$. *(p.2-3)*

### Stable Model via Reduced ADF

For a two-valued model $M$ of ADF $D$, the reduced ADF $D^M$ is obtained by:
1. Eliminating all nodes mapped to $f$ by $M$
2. For remaining nodes, dropping all links from nodes not in $M$
3. Replacing eliminated parents by their truth value in acceptance conditions

$M$ is a stable model of $D$ iff $M$ is the grounded extension of the reduced ADF $D^M$. *(p.4)*

### Weighted ADF Acceptance

For weighted ADFs with weights $w_1, \ldots, w_n$ on links and threshold $\alpha$:

$$
C_s \text{ is accepted iff } \sum_{i: a_i \text{ is true}} w_i \geq \alpha
$$

Positive weight = support, negative weight = attack. *(p.6)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Acceptance condition | $C_s$ | - | - | Any propositional formula over par(s) | 1 | One per node |
| Link weight | $w_i$ | - | - | $\mathbb{R}$ (positive=support, negative=attack) | 6 | For weighted ADFs |
| Acceptance threshold | $\alpha$ | - | - | $\mathbb{R}$ | 6 | Sum of weights of true parents must meet this |
| Preponderance threshold | - | - | 0 | - | 7 | Net weight > 0 |
| Clear and convincing threshold | - | - | - | higher than preponderance | 7 | Application-specific |
| Beyond reasonable doubt threshold | - | - | - | highest | 7 | Requires near-certainty |

## Implementation Details

### Data Structures
- ADF: triple (S, L, C) where S is set of nodes, L is set of directed edges, C maps each node to a propositional formula over its parents *(p.1)*
- Three-valued interpretation: mapping from S to {t, f, u} *(p.2)*
- Can represent acceptance conditions as: (a) explicit propositional formulas, (b) truth tables (completely defined Boolean functions), or (c) weighted sums with thresholds *(p.1, 6)*

### Grounded Model Computation
1. Start with $v_0 = v_u$ (all undecided)
2. Apply $\Gamma_D$ iteratively: $v_{i+1} = \Gamma_D(v_i)$
3. Stop when $v_{i+1} = v_i$ (fixpoint reached)
4. The fixpoint is the grounded interpretation
*(p.2-3)*

### Stable Model Check
1. Given candidate two-valued model $M$
2. Construct reduced ADF $D^M$: remove nodes where $M(s)=f$, simplify acceptance conditions
3. Compute grounded extension of $D^M$
4. $M$ is stable iff it equals the grounded extension of $D^M$
*(p.4)*

### Bipolar ADF Classification
- A link $(a,b)$ is **supporting** if: for all $V \subseteq par(b) \setminus \{a\}$, $V \cup \{a\}$ satisfies $C_b$ implies $V$ satisfies $C_b$ is false, OR equivalently flipping $a$ from false to true can only help acceptance *(p.4)*
- A link $(a,b)$ is **attacking** if: flipping $a$ from false to true can only hurt acceptance *(p.4)*
- An ADF is **bipolar** (BADF) if every link is either purely supporting or purely attacking *(p.4)*
- Dung AFs are bipolar (all links are attacking) *(p.4)*

### Reduction from ADF to Dung AF
- Not always possible to faithfully reduce
- For BADFs, can introduce auxiliary nodes for support links *(p.5)*
- For non-bipolar links, no clean reduction exists *(p.4-5)*

## Figures of Interest
- **Fig 1 (p.1):** Example ADF with 4 nodes {a,b,c,d} showing mixed support/attack. Node a: $C_a = \top$ (always accepted). Node b: $C_b = a$ (accepted if a is). Node c: $C_c = \neg a \wedge \neg b$ (attacked by both a and b). Node d: $C_d = b \vee c$ (supported by b or c).
- **Fig in Example 3 (p.3):** Example illustrating grounded model computation.
- **Fig in Example 4 (p.4):** Bipolar ADF illustrating stable models.
- **Fig (p.5):** Logic program translation example showing ADF generalizing normal logic programs.
- **Fig in Example 8 (p.5):** ADF where acceptance conditions involve non-bipolar links, demonstrating why BADF restriction matters for stable semantics.
- **Fig (p.8):** Weighted ADF for legal proof standards — a graph where weights on links determine the acceptance threshold, modeling preponderance, clear and convincing, and beyond reasonable doubt.

## Results Summary
- Dung AFs are a special case of ADFs where all acceptance conditions are conjunctions of negated attackers *(p.1)*
- Grounded semantics generalizes cleanly to all ADFs; complete semantics also generalizes *(p.2-3)*
- Preferred and stable semantics require restriction to bipolar ADFs (BADFs) for clean generalization *(p.3-5)*
- For BADFs, stable models exist and well-founded model coincides with grounded interpretation *(p.3-4)*
- Normal logic programs can be faithfully represented as ADFs; stable models of ADF correspond to answer sets *(p.5)*
- Weighted ADFs provide a practical representation of acceptance conditions using numerical weights *(p.6-7)*
- Deciding whether a statement is accepted in some (resp. all) stable/preferred models is in the complexity class $\Sigma_2^P$ (resp. $\Pi_2^P$) for general ADFs *(p.7)*

## Limitations
- Stable and preferred semantics do not generalize cleanly beyond bipolar ADFs — the paper acknowledges this restriction is needed but limits expressiveness *(p.3-4)*
- Complexity is higher than Dung AFs (second level of polynomial hierarchy vs first level) *(p.7)*
- The paper is an initial proposal; many details (algorithms, implementations) are left to future work *(p.8)*
- The weighted ADF approach uses simple linear threshold functions; more complex acceptance conditions require full propositional formulas *(p.6)*
- Translation to Dung frameworks is possible for BADFs but introduces auxiliary nodes that may be exponential *(p.5)*

## Arguments Against Prior Work
- Dung AFs are too restrictive: only one link type (attack), so support, joint attack, and other dependencies cannot be directly modeled *(p.0)*
- Bipolar AFs (Cayrol & Lagasquie-Schiex 2005) add support but in a limited, ad-hoc way — they don't allow arbitrary acceptance conditions *(p.0, 8)*
- AFRA (Baroni, Cerutti, Giacomin 2009) models recursive attacks but not general dependencies *(p.8)*
- Prakken (2005) showed translating bipolar AFs to Dung AFs requires auxiliary constructs, losing abstraction *(p.5)*
- Prior approaches to support (Cayrol 2005, Odekerken) require separate treatment of support links rather than unifying attack and support in acceptance conditions *(p.0)*

## Design Rationale
- Acceptance conditions are placed on nodes rather than links because the same link may be supporting in some contexts and attacking in others — the node's condition determines the aggregate effect *(p.1)*
- Three-valued semantics (t/f/u) chosen because undecided status is essential for grounded semantics and cautious reasoning *(p.2)*
- Bipolar restriction for stable/preferred semantics is motivated by the observation that without it, the reduced ADF construction doesn't preserve the intended relationship between models *(p.3-4)*
- Weighted ADFs bridge theory and practice: weights are intuitive for users (especially in legal domains) while acceptance conditions provide formal precision *(p.6-7)*

## Testable Properties
- For any Dung AF translated to ADF, the grounded extension of the Dung AF must equal the grounded interpretation of the ADF *(p.2)*
- For a BADF, every stable model must also be a preferred model *(p.4)*
- For a BADF, every preferred model must be a complete model *(p.3)*
- The grounded interpretation must be a subset (information-wise) of every complete interpretation *(p.3)*
- For weighted ADFs: if all supporting parents are true and sum of positive weights >= threshold, node must be accepted *(p.6)*
- For Dung AFs viewed as ADFs: stable extensions of the Dung AF = stable models of the corresponding ADF *(p.2)*
- If an ADF has no links (all conditions are $\top$ or $\bot$), grounded model assigns t to nodes with $C_s = \top$ and f to nodes with $C_s = \bot$ *(p.2)*
- A node with $C_s = \top$ (no parents, self-accepting) must be in every complete/preferred/stable extension *(p.2)*
- Translation of normal logic program to ADF: answer sets of the program = stable models of the ADF *(p.5)*

## Relevance to Project
ADFs are directly relevant to propstore's argumentation layer. Where Dung AFs only model attack between arguments, ADFs allow modeling support relationships, evidential dependencies, and complex acceptance conditions. This is critical for:
- Modeling claims that support other claims (not just attack)
- Representing complex defeat conditions (e.g., a claim is defeated only if BOTH of two counterarguments hold)
- Weighted acceptance conditions map to confidence/strength-based reasoning
- Legal proof standards (preponderance, clear and convincing, beyond reasonable doubt) can be directly modeled as threshold parameters in the render layer
- The bipolar subclass (BADFs) may be sufficient for most propstore use cases while keeping computational properties manageable

## Open Questions
- [ ] Can the BADF restriction be relaxed for propstore's use cases, or are all relevant links bipolar?
- [ ] How do ADFs interact with ASPIC+ structured argumentation?
- [ ] What is the practical algorithm for computing preferred extensions of BADFs?
- [ ] How do weighted ADFs relate to probabilistic argumentation frameworks (Hunter 2017, Li 2011)?
- [ ] Later work (Brewka et al. 2013) extended ADFs significantly — should that be read next?

## Cross-References (in this repo)

### Cites
- [[Dung_1995_AcceptabilityArguments]] — The foundational AF paper that ADFs generalize
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — Bipolar AFs, the most direct predecessor; ADFs subsume BAFs
- [[Bench-Capon_2003_PersuasionPracticalArgumentValue-based]] — Value-based AFs; cited for preference-based extensions
- [[Caminada_2006_IssueReinstatementArgumentation]] — Semi-stable semantics; cited for alternative semantics
- [[Simari_1992_MathematicalTreatmentDefeasibleReasoning]] — Defeasible reasoning; cited for specificity-based preferences
- [[Vreeswijk_1997_AbstractArgumentationSystems]] — Abstract argumentation systems; cited as prior generalization attempt
- [[Prakken_2010_AbstractFrameworkArgumentationStructured]] — ASPIC+; cited for structured argumentation

### Cited by
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — Discusses how ADFs with Boolean conditions relate to equational approach (Section 2.2)
- [[Thimm_2012_ProbabilisticSemanticsAbstractArgumentation]] — Cites the 2013 revisited version in context of probabilistic semantics
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — References probabilistic ADFs (Polberg & Doder 2014)
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — Mentions ADFs as a generalization
- [[Čyras_2021_ArgumentativeXAISurvey]] — Directly cites Brewka & Woltran 2010
- [[Charwat_2015_MethodsSolvingReasoningProblems]] — Cites the 2013 revisited version for solving methods
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — Cites ADF semantics work
- [[Tang_2025_EncodingArgumentationFrameworksPropositional]] — Cites ADF encoding work
- [[Doutre_2018_ConstraintsChangesSurveyAbstract]] — References ADF revision work

## Related Work Worth Reading
- Brewka, Ellmauthaler, Strass, Wallner, Woltran (2013) — "Abstract Dialectical Frameworks Revisited" — the journal-length follow-up with full technical details → NOW IN COLLECTION: [[Brewka_2013_AbstractDialecticalFrameworksRevisited]]
- Strass (2013) — Approximating operators and semantics for ADFs
- Cayrol and Lagasquie-Schiex (2005) — On the acceptability of arguments in bipolar argumentation frameworks (the bipolar AF paper ADFs generalize)
- Pollock (2005) — Followed ADF-like approach with multiple link types before ADFs formalized it
- Dung (1995) — The foundational AF paper that ADFs generalize
- Prakken (2005) — On relating Dung frameworks to rule-based argumentation
- Fazzinga, Flesca, and Furfaro (2016) — Probabilistic extension of ADFs
- Dunne, Dvorak, and Woltran (2011) — Complexity of ADFs (cited in paper)

## Collection Cross-References

### Now in Collection (previously listed as leads)
- [[Brewka_2013_AbstractDialecticalFrameworksRevisited]] — Repairs the original paper's restricted preferred/stable semantics by defining three-valued semantics for arbitrary ADFs, adds static and dynamic preference handling, and sketches the DIAMOND ASP implementation.
