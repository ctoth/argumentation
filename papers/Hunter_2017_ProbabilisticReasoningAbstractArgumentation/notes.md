---
title: "Probabilistic Reasoning with Abstract Argumentation Frameworks"
authors: "Anthony Hunter, Matthias Thimm"
year: 2017
venue: "Journal of Artificial Intelligence Research (JAIR) 59"
doi_url: "https://doi.org/10.1613/jair.5393"
---

# Probabilistic Reasoning with Abstract Argumentation Frameworks

## One-Sentence Summary
Defines the epistemic approach to probabilistic argumentation — assigning probability functions over sets of arguments constrained by AF topology — with rationality postulates, partial assessment propagation via maximum entropy, inconsistency measures for contradictory assessments, and consolidation operators. *(p.0)*

## Problem Addressed
Classical Dung AFs use three-valued labellings (in/out/undec) which cannot represent degrees of belief. Real-world scenarios (audience modeling, dialogue, multi-agent) need graded acceptability. This paper provides a comprehensive formal framework for probabilistic reasoning over abstract argumentation that generalizes classical semantics while allowing partial and contradictory probability assessments. *(p.0-1)*

## Key Contributions
1. Laying out the building blocks for the epistemic probabilistic AF framework, introducing the notion of epistemic extensions *(p.6)*
2. Several properties for standard epistemic extensions that coincide with classical Dung semantics *(p.9)*
3. Non-standard epistemic extensions and a complete picture of relationships between probabilistic properties *(p.15)*
4. Concept of partial probability assessments and maximum entropy completion *(p.19)*
5. Inconsistency measures for evaluating contradictory probability assessments, with rationality conditions *(p.23)*
6. Distance-based consolidation operators to "repair" contradictory assessments *(p.29)*
7. Ranking-based semantics connection *(p.36)*

## Methodology

### Core Framework

A probability function P over an AF = (Arg, ->) assigns values to subsets of arguments:

$$
P : 2^{\text{Arg}} \to [0, 1]
$$
Where: P(S) is the probability assigned to the set S of arguments being the "believed" set, subject to the constraint that the sum over all subsets equals 1. *(p.7)*

The marginal probability of a single argument A being believed:

$$
P(A) = \sum_{A \in S \subseteq \text{Arg}} P(S)
$$
*(p.8)*

### Epistemic Labelling

Given a probability function P, the epistemic labelling L_P is defined: *(p.8)*

$$
L_P(A) = \text{in} \iff P(A) > 0.5
$$

$$
L_P(A) = \text{out} \iff P(A) < 0.5
$$

$$
L_P(A) = \text{undec} \iff P(A) = 0.5
$$

### Complete Probability Function (Definition 5)

P in P(AF) is a complete probability function such that for every A in Arg: *(p.8)*

1. If P(A) = 1 then P(B) = 0 for all B in Arg with B -> A
2. If P(B) = 0 for all B with B -> A then P(A) = 1
3. If P(A) = 0 then there is B with B -> A and P(B) = 1
4. If P(B) = 1 for some B with B -> A then P(A) = 0

This is a probabilistic version of Dung's definition of completeness.

## Key Equations

### Rationality Postulates (Probability Constraints)

**COH** (Coherent): *(p.9)*
$$
\text{If } A \to B \text{ then } P(A) + P(B) \leq 1
$$

**FOU** (Founded): *(p.10)*
$$
P \text{ is founded iff } \text{if } P(A) \geq 1 - P(B) \text{ for every } A \in \text{Arg with } \text{Att}_{AF}(A) = B
$$

**SFOU** (Semi-founded): *(p.9)*
$$
P \text{ is semi-founded iff } P(A) \leq 1 - \frac{\sum_{B \in \text{Att}(A)} P(B)}{|\text{Att}(A)|}
$$
Where Att(A) is the set of attackers of A. Actually stated as: if P(A) >= 0.5 for every A in Arg with Att(A) = B, then P(B) <= 0.5.

**OPT** (Optimistic): *(p.10)*
$$
\text{If } P(A) \geq 0.5 \text{ for every } A \in \text{Arg with } \text{Att}_{AF}(A) = B, \text{ then } P(B) \leq 0.5
$$

**RAT** (Rational): *(p.9)*
$$
\text{If } A \to B \text{ then } P(A) > 0.5 \implies P(B) \leq 0.5
$$

**INV** (Involutary): *(p.15)*
$$
\text{If } A \to B \text{ then } P(A) = 1 - P(B)
$$

**NEU** (Neutral): P(A) = 0.5 for every A *(p.15)*

**MAX** (Maximal): P(A) = 1 for every A *(p.15)*

**MIN** (Minimal): P(A) = 0 for every A *(p.15)*

**JUS** (Justifiable): P(A) >= 0.5 for every A *(p.15)*

**TER** (Ternary): P(A) in {0, 0.5, 1} for every A *(p.9)*

### Correspondence Table (Table 2)

| Restriction on P | Classical semantics |
|---|---|
| No restriction (complete P) | complete extensions |
| Max A with P(A) = 0.5 | stable |
| Max A with P(A) = 1 | preferred |
| Min A with P(A) = 0.5 | preferred |
| Min A with P(A) = 0.5 (different sense) | grounded |
| Min A with P(A) = 1 | grounded |
| Min A with P(A) = 0.5 | semi-stable |
*(p.13)*

### Class Hierarchy (Proposition 1 + Figure 5)

$$
\emptyset \subset \mathcal{P}_{\text{NEU}} \subset \mathcal{P}_{\text{INV}} \subset \mathcal{P}_{\text{COH}} \subset \mathcal{P}_{\text{SOPT}} \subset \mathcal{P}_{\text{RAT}} \subset \mathcal{P}(\text{AF})
$$

$$
\mathcal{P}_{\text{MIN}} \subset \mathcal{P}_{\text{INV}}, \quad \mathcal{P}_{\text{MIN}} \subset \mathcal{P}_{\text{JUS}}
$$

$$
\mathcal{P}_{\text{JUS}} \subset \mathcal{P}_{\text{OPT}} \subset \mathcal{P}_{\text{FOU}} \subset \mathcal{P}_{\text{SFOU}} \subset \mathcal{P}(\text{AF})
$$

$$
\mathcal{P}_{\text{MAX}} \subset \mathcal{P}_{\text{JUS}}
$$

$$
\mathcal{P}_{\text{TER}} \subset \mathcal{P}_{\text{COH}}
$$
*(p.11-12, 16-17)*

### Key Propositions on Structure

- **Proposition 7**: If L is an admissible labelling, there is P in P_RAT(AF) with L ~ P *(p.17)*
- **Proposition 8**: For P in P_RAT(AF), in(L_P) is conflict-free *(p.17)*
- **Proposition 9**: If AF has odd cycle and P in P_INV(AF), then P in P_NEU(AF) *(p.17)*
- **Proposition 10**: Rational probability functions are more general than coherent — allow non-standard extensions *(p.18)*

### Partial Probability Assessments (Section 6)

A partial function beta: Arg' -> [0,1] where Arg' is a subset of Arg. *(p.19)*

**Definition 6**: beta is a partial probability assignment. The set of all partial probability assignments is denoted by II. *(p.19)*

**P^beta(AF)**: The set of all T-compliant probability functions consistent with partial assignment beta: *(p.20)*

$$
\mathcal{P}^\beta(\text{AF}) = \{P \in \mathcal{P}(\text{AF}) \mid P(A) = \beta(A) \text{ for all } A \in \text{dom}(\beta)\}
$$

**Topological properties** (Proposition 13): *(p.20)*
1. P^beta(AF) is connected, convex, and closed
2. For every T in {COH, SFOU, FOU, OPT, SOPT, JUS}, the sets P_T(AF) and P^beta_T(AF) are connected, convex, and closed
3. For every T in {COH, SFOU, FOU, OPT, SOPT, JUS} and A in Arg, the set p^beta_{T,A}(A) is connected, convex, and closed

**Complexity** (Proposition 14): *(p.22)*
- Deciding if p in p^beta_T(A) for some p in [0,1] is NP-complete
- Deciding beta_l <= p^beta_T(A) for some bounds l,u in [0,1] is coNP-complete
- Computing l,u in {0,1} such that l = p^beta_T(A), u = p^beta_T(A) is NP^NP-complete

The constraints can be represented as linear constraints on P, making the problem solvable via linear programming. *(p.22)*

### Maximum Entropy (Definition 7)

$$
P^{\text{ME}}_{\Gamma, \text{AF}} = \arg\max_{P \in \mathcal{P}^\beta_\Gamma(\text{AF})} H(P)
$$

Where H(P) is Shannon entropy: *(p.22)*

$$
H(P) = -\sum_{S \subseteq \text{Arg}} P(S) \log P(S)
$$

**Proposition 15**: P^ME contains exactly one uniquely defined probability function. *(p.22)*

Maximum entropy corresponds to grounded semantics: for a complete assignment with no partial info, the ME solution gives the grounded extension. *(p.23)*

### Inconsistency Measures (Section 7)

**Definition 8**: An inconsistency measure I_T is a function from II x A -> [0, infinity). *(p.23)*

Properties: *(p.24)*
- **Consistency**: I_T(beta, AF) = 0 iff P^beta(AF) intersect P_T(AF) is not empty
- **Monotonicity**: If beta is an extension of beta', then I_T(beta, AF) >= I_T(beta', AF)
- **Super-additivity**: I_T(beta union beta', AF) >= I_T(beta, AF) + I_T(beta', AF) when disjoint
- **Separability**: I_T(beta, AF) = sum over connected components AF_i of I_T(beta, AF_i)

### Distance-Based Inconsistency (Definition 10)

$$
\mathcal{I}^{d_p}_T(\beta, \text{AF}) = d_p(\mathcal{P}^\beta(\text{AF}), \mathcal{P}_T(\text{AF}))
$$

Where d_p is a pre-metrical distance measure (e.g., Euclidean for p=2, Manhattan for p=1, KL divergence for d_KL). *(p.24-25)*

**Proposition 18**: For p >= 1, I^{d_p}_T satisfies consistency and monotonicity. For p = 1 it also satisfies separability and super-additivity. *(p.27)*

### Consolidation Operators (Section 7.2)

**Definition 11**: H_{T,beta}(delta) is the set of probability functions in P^beta(AF) that minimize inconsistency to within delta. *(p.29)*

**Two consolidation approaches**: *(p.30-31)*
1. **H_{T,beta}(0)**: "Soft repair" — preserve prior info, get as close as possible to satisfying rationality constraints T. Used when you want to preserve the prior information but want to get as close as possible to satisfying constraints.
2. **H'_{T,beta}(0)**: "Hard repair" — impose rationality constraints T while staying as close as possible to the prior. Used when you want to impose constraints at cost of losing some original info.

**Topological properties** (Proposition 13 extended): *(p.20-21)*
- P^beta(AF) is connected, convex, closed
- H_{T,beta}(delta) is connected, convex, closed for delta in an interval
- These sets are compact subsets of [0,1]^{2^n}

**Maximum entropy consolidation** (Definition 12-13): *(p.30)*

$$
P^{\text{ME},T}_{\beta} = \arg\max_{P \in H_{T,\beta}(0)} H(P)
$$

$$
P^{\text{ME}',T}_{\beta} = \arg\max_{P \in H'_{T,\beta}(0)} H(P)
$$

Both yield unique probability functions. *(p.30)*

**Example 17 (revision vs update analogy)**: *(p.31-32)*
- H_{T,beta}(0) is analogous to AGM revision — preserve prior, accommodate new constraints
- H'_{T,beta}(0) is analogous to AGM update — impose new topology, adjust beliefs

### Ranking-Based Semantics Connection (Section 8.3)

The paper connects to ranking-based argumentation approaches that exploit AF topology to derive a preference relation >= among arguments. *(p.36)*

Key properties tested: *(p.37-38)*
- **Abstraction**: If AF = (Arg, ->) and AF' = (Arg', ->') are isomorphic and gamma: Arg -> Arg' is the isomorphism, then P' = P composed with gamma^{-1}
- **Independence**: For AF'' = (Arg, ->) = CC(AF), for all A,B in Arg', A >= B implies A >= B (ranking restricted to connected components)
- **Void Precedence**: If Att(A) = emptyset and Att(B) != emptyset then A > B *(p.38)*
- **Non-attacked Equivalence**: If Att(A) = emptyset and Att(B) = emptyset then A ~ B
- **Attack vs Full Defense**: If A has no attack branch, Att(C) = emptyset, and Att(B) = {C}, then A -> B (different from standard)
- **Proposition 27**: COH satisfies Void Precedence, Non-attacked Equivalence, Abstraction, Independence *(p.38)*
- **Proposition 29**: FOU and COH satisfy Attack vs Full Defense in non-strict form *(p.39)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Probability of argument | P(A) | - | - | [0, 1] | 8 | Marginal probability of belief in A |
| Probability of argument set | P(S) | - | - | [0, 1] | 7 | Full joint probability over subsets |
| Epistemic labelling threshold | - | - | 0.5 | fixed | 8 | in/out/undec boundary |
| Distance measure exponent | p | - | 1 | [1, infinity) | 24 | p=1 Manhattan, p=2 Euclidean |
| Consolidation tolerance | delta | - | 0 | [0, infinity) | 29 | How far from optimal repair to accept |
| Entropy | H(P) | bits | - | [0, n] | 22 | Shannon entropy over 2^n subsets |

## Implementation Details

### Data Structures Needed
- **Probability function**: Map from 2^Arg -> [0,1], subject to sum = 1. For n arguments, this is 2^n values. *(p.7)*
- **Partial probability assignment**: Map from subset of Arg -> [0,1]. *(p.19)*
- **AF graph**: Standard (Arg, ->) directed graph. *(p.7)*
- **Epistemic labelling**: Derived from P via threshold at 0.5. *(p.8)*

### Computational Approach
- The rationality constraints (COH, FOU, RAT, etc.) are **linear constraints** on P. *(p.22)*
- Therefore the feasibility set P^beta_T(AF) is a **convex polytope** in [0,1]^{2^n}. *(p.20)*
- Maximum entropy over a convex polytope = **convex optimization** (unique solution). *(p.22)*
- For practical computation: express constraints as LP/QP, use maximum entropy solver. *(p.22)*
- NP-complete in general, but tractable for small AFs or decomposable AFs (separability by connected components). *(p.22)*

### Key Algorithm: Maximum Entropy Propagation
1. Start with partial assignment beta on some arguments
2. Choose rationality constraint set T (e.g., COH, FOU)
3. Form the convex set P^beta_T(AF) of all compliant probability functions
4. Solve: P^ME = argmax H(P) subject to P in P^beta_T(AF)
5. Read off P^ME(A) for all unassigned arguments
*(p.22)*

### Key Algorithm: Consolidation of Contradictory Assessments
1. Given contradictory beta (P^beta_T(AF) = empty set)
2. Compute inconsistency I_T(beta, AF) using chosen distance d_p
3. Choose consolidation mode:
   - **Soft (H)**: Find P closest to P^beta(AF) that satisfies T — preserves prior, accommodates topology
   - **Hard (H')**: Find P in P_T(AF) closest to P^beta(AF) — imposes topology, adjusts prior
4. Apply maximum entropy over the consolidation set for unique result
*(p.29-31)*

### Edge Cases
- **Odd cycles**: Force involutary functions to be neutral (P(A) = 0.5 for all). *(p.17)*
- **Self-attacking arguments**: If A -> A, then under COH: P(A) + P(A) <= 1, so P(A) <= 0.5. *(p.9)*
- **Isolated arguments** (no attackers): Under FOU, must have P(A) = 1. Under COH, no constraint. *(p.10)*
- **Exponential blowup**: 2^n subsets for n arguments. Practical only for small n unless decomposed. *(p.7)*

## Figures of Interest
- **Fig 1 (p.4-5)**: Foreign takeover argumentation framework — 10-argument example with probability values showing audience belief modeling
- **Fig 2 (p.7)**: Small AF from Example 4 used throughout
- **Fig 3 (p.9)**: Three arguments in a simple cycle — demonstrates involutary forcing
- **Fig 4 (p.10)**: Simple AF for illustrating probability classes (Table 1)
- **Fig 5 (p.17)**: Complete class hierarchy diagram — strict subset relations between all probability function classes
- **Fig 6 (p.19)**: Court case AF — John guilty/innocent with surveillance evidence
- **Fig 7 (p.32)**: Two-object example for revision vs update distinction

## Results Summary
- The epistemic approach strictly generalizes classical Dung semantics — every classical extension corresponds to specific probability function constraints *(p.12-13)*
- The class hierarchy (Fig 5) provides a complete lattice of constraint strengths *(p.16-17)*
- Maximum entropy gives unique, well-defined propagation from partial assessments *(p.22)*
- Inconsistency measures with d_1 (Manhattan) satisfy all four desirable properties (consistency, monotonicity, super-additivity, separability) *(p.27)*
- Consolidation operators provide principled ways to handle contradictory assessments with connections to AGM revision/update *(p.31-32)*
- The framework decomposes by connected components (separability), enabling tractable computation on decomposable AFs *(p.27-28)*

## Limitations
- Exponential representation: 2^n probability values for n arguments — practical only for small AFs or with decomposition *(p.7)*
- NP-complete to decide membership in constrained probability sets *(p.22)*
- The paper focuses on abstract argumentation — no direct treatment of structured argumentation (ASPIC+) *(p.33)*
- No concrete implemented algorithms — the computational approach is described theoretically via linear programming and convex optimization *(p.22)*
- Ranking-based semantics properties are not all satisfied — e.g., FOU and COH do not distinguish attack branch structures the same way some ranking semantics do *(p.38-39)*

## Arguments Against Prior Work
- **Constellations approach** (probability over possible argument graphs) is criticized as less natural for the epistemic setting — it models uncertainty about graph structure rather than belief in arguments *(p.1-2)*
- **Bare three-valued labellings** are too coarse for real applications like audience modeling, dialogue, multi-agent systems *(p.0-1)*
- **Dung & Thang (2010)** approach to extracting abstract argumentation with probability distribution over possible argument graphs — different concern (graph uncertainty vs belief uncertainty) *(p.33)*
- **Pollock (1987)** probabilistic reasoning with logical statements — doesn't consider acceptability, just assigns probabilities to formulas *(p.34)*

## Design Rationale
- **Why epistemic over constellations**: The epistemic approach models degree of belief in argument acceptability, which is the natural question for audience modeling, dialogue, and multi-agent scenarios. Constellations model uncertainty about which arguments exist. *(p.1-2)*
- **Why multiple constraint classes**: Different applications need different strength of topology enforcement. COH is weak (just pairwise), FOU is strong (all attackers), RAT is intermediate. The hierarchy allows choosing the right level. *(p.9-11)*
- **Why maximum entropy**: Unique solution, well-motivated by information theory (least commitment), corresponds to grounded extension in the limit. *(p.22-23)*
- **Why two consolidation modes**: Soft repair preserves prior beliefs (like revision), hard repair preserves topology constraints (like update). Both are needed depending on whether the topology or the prior is more trusted. *(p.31-32)*

## Testable Properties
- For any P in P_COH(AF): if A -> B then P(A) + P(B) <= 1 *(p.9)*
- For any P in P_RAT(AF): if A -> B and P(A) > 0.5 then P(B) <= 0.5 *(p.9)*
- For any P in P_FOU(AF): if A -> B then P(A) <= 1 - P(B) *(p.10)*
- For complete P: L_P is a complete labelling in the Dung sense *(p.8)*
- P^ME is unique for any non-empty convex constraint set *(p.22)*
- Inconsistency I^{d_1}_T satisfies separability: decomposes over connected components *(p.27)*
- For P in P_RAT(AF): in(L_P) is conflict-free *(p.17)*
- If AF has odd cycle and P in P_INV(AF) then P in P_NEU(AF) (all arguments get 0.5) *(p.17)*
- Consolidation sets H_{T,beta}(delta) are convex and closed for all valid delta *(p.29)*
- P^beta_T(AF) is connected, convex, and closed for T in {COH, SFOU, FOU, OPT, SOPT, JUS} *(p.20)*

## Relevance to Project
This paper provides the formal foundation for replacing bare floats with principled probabilistic argumentation in propstore. Key implications:

1. **Constraint-based probability**: Instead of storing arbitrary P(A) floats, enforce rationality constraints (at minimum COH, ideally FOU or RAT) that respect the attack graph topology.
2. **Partial assessment propagation**: When only some arguments have assigned probabilities, use maximum entropy to derive the rest — this is the principled way to "fill in" missing beliefs.
3. **Inconsistency detection**: When new evidence contradicts existing probabilities, the inconsistency measure quantifies how bad the contradiction is before any repair.
4. **Consolidation = belief revision**: The two consolidation operators map directly to the existing concern about not collapsing disagreement — soft repair preserves prior beliefs, hard repair preserves topology.
5. **Decomposition**: Separability by connected components means the exponential blowup can be managed if the AF decomposes into small components.
6. **ATMS connection**: The probability function over subsets of arguments is conceptually similar to ATMS labels — each subset is like an assumption context, and the probability weights them.

## Open Questions
- [ ] How to efficiently represent P for AFs with more than ~20 arguments (2^20 = 1M subsets)?
- [ ] Can the linear programming formulation be connected to Z3 (which propstore already uses)?
- [ ] How do the consolidation operators compose with ATMS context switching (Dixon 1993)?
- [ ] What is the right constraint class for propstore — COH (minimal), RAT (moderate), or FOU (strong)?
- [ ] Can the ranking-based semantics properties be leveraged for the existing tie-breaking mechanisms?
- [ ] How does this interact with ASPIC+ structured argumentation (Modgil & Prakken 2018)?

## Related Work Worth Reading
- **Hunter & Thimm (2014b)**: Probabilistic argument graphs for argumentation lotteries — extends to structured case
- **Thimm (2013)**: Inconsistency measures for probabilistic logics — the d_KL and d_p measures used here
- **Baroni et al. (2018)**: Ranking-based semantics — the properties tested in Section 8.3 come from here
- **Rienstra, Thimm, & Oren (2013)**: Opponent models with uncertainty for strategic argumentation
- **Fazzinga, Flesca, & Parisi (2015)**: Complexity of probabilistic abstract argumentation
- **Dung & Thang (2010)**: Towards (probabilistic) argumentation for jury-based dispute resolution — the constellations approach
- **Polberg, Doder (2014)**: Probabilistic abstract dialectical frameworks — alternative probabilistic framework
- **Besnard & Hunter (2008)**: Elements of Argumentation — textbook foundation

## Collection Cross-References

### Already in Collection
- [[Coste-Marquis_2007_MergingDung'sArgumentationSystems]] — Cited for distance-based merging of Dung AFs; the merging framework's PAF formalism complements Hunter's probabilistic approach by handling structural uncertainty (which attacks exist) via three-valued relations rather than probabilities.

### Conceptual Links (not citation-based)
- [[Fang_2025_LLM-ASPICNeuro-SymbolicFrameworkDefeasible]] — **Strong.** Fang's LLM-ASPIC+ framework uses binary beliefs (in the belief set or not) with grounded extensions for conflict resolution. Hunter provides the formal machinery for graded/probabilistic acceptability over AFs. For propstore, the combination is needed: LLM-ASPIC+ style extraction feeding into Hunter-style probabilistic reasoning rather than binary extension membership, bridging the gap between LLM-based extraction uncertainty and formal argumentation semantics.
- [[Popescu_2024_ProbabilisticArgumentationConstellation]] — **Strong.** Popescu & Wallner provide exact DP algorithms for computing constellation-approach probabilities, complementing Hunter & Thimm's epistemic approach. Hunter assigns belief probabilities to arguments within a fixed AF; Popescu computes probabilities over the AF structure itself (which arguments/attacks exist). For propstore, both probability types are needed: epistemic (how much do we believe this argument?) and structural (what is the probability this argument exists in the framework?).

---

**See also:** [[Thimm_2012_ProbabilisticSemanticsAbstractArgumentation]] - The original 6-page ECAI 2012 paper by Thimm that this 2017 journal paper substantially extends. Introduces the core probabilistic semantics, rationality postulates, and maximum entropy model in compact form.
