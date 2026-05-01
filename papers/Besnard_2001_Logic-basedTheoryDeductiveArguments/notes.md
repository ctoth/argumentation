---
title: "A logic-based theory of deductive arguments"
authors: "Philippe Besnard, Anthony Hunter"
year: 2001
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/S0004-3702(01)00071-6"
---

# A logic-based theory of deductive arguments

## One-Sentence Summary
Provides a formal framework for logic-based argumentation where arguments are minimal consistent subsets of a knowledge base paired with their deductive consequences, with formal definitions of defeaters, undercuts, rebuttals, canonical undercuts, argument trees, argument structures, and aggregation functions for determining which conclusions follow.

## Problem Addressed
Existing argumentation frameworks either used abstract attack relations (Dung 1995) without specifying internal argument structure, or used restricted languages (e.g., defeasible logic rules). This paper bridges the gap by defining arguments and their interactions entirely within classical propositional logic, providing a precise logical foundation for when one argument defeats, undercuts, or rebuts another. *(p.1/204)*

## Key Contributions
- Formal definition of deductive arguments as pairs of minimal consistent support sets and their consequences *(p.2/205)*
- Three types of counter-arguments: defeaters, undercuts, and rebuttals, with formal logical characterizations *(p.6/209)*
- Canonical undercuts as the only defeaters that need to be considered *(p.10-12/213-215)*
- Argument trees for exhaustively organizing counter-arguments with proof of finiteness *(p.12-13/215-217)*
- Argument structures pairing pro and con argument trees for aggregation *(p.17/220)*
- General aggregation framework via categoriser and accumulator functions *(p.19-20/222-223)*
- Comparison showing binary argumentation, counting arguments, Dung's system, and argumentation logic are special cases or related *(p.21-29/224-232)*
- Application to reasoning with structured news reports *(p.28-32/231-235)*

## Methodology
The framework is built on classical propositional logic. A database Delta is a finite set of formulae (possibly inconsistent). Arguments are constructed from minimal consistent subsets that entail a conclusion. Counter-arguments attack the support of arguments. The paper develops a hierarchy: arguments -> defeaters/undercuts/rebuttals -> canonical undercuts -> argument trees -> argument structures -> aggregation.

## Key Equations

### Definition 3.1: Argument
$$
\langle \Phi, \alpha \rangle \text{ is an argument iff: (1) } \Phi \nvdash \bot, \text{ (2) } \Phi \vdash \alpha, \text{ (3) } \Phi \text{ is a minimal subset of } \Delta \text{ satisfying (2)}
$$
Where: Phi is the support (a consistent subset of Delta), alpha is the consequent (a formula).
*(p.2/205)*

### Definition 3.3: More Conservative
$$
\langle \Phi, \alpha \rangle \text{ is more conservative than } \langle \Psi, \beta \rangle \text{ iff } \Phi \subseteq \Psi \text{ and } \beta \vdash \alpha
$$
*(p.3/206)*

### Definition 4.1: Defeater
$$
\langle \Phi, \alpha \rangle \text{ defeats } \langle \Psi, \beta \rangle \text{ iff } \beta \vdash \neg(\phi_1 \wedge \cdots \wedge \phi_n) \text{ for some } \{\phi_1, \ldots, \phi_n\} \subseteq \Phi
$$
Where: the consequent of one argument negates the conjunction of some support elements of another.
*(p.6/209)*

### Definition 4.3: Undercut
$$
\langle \Psi, \neg(\phi_1 \wedge \cdots \wedge \phi_n) \rangle \text{ is an undercut for } \langle \Phi, \alpha \rangle \text{ where } \{\phi_1, \ldots, \phi_n\} \subseteq \Phi
$$
Where: the consequent directly negates the conjunction of support elements (not just entails it).
*(p.6/209)*

### Definition 4.5: Rebuttal
$$
\langle \Psi, \beta \rangle \text{ is a rebuttal for } \langle \Phi, \alpha \rangle \text{ iff } \beta \leftrightarrow \neg\alpha \text{ is a tautology}
$$
*(p.6/209)*

### Definition 5.3: Canonical Undercut
$$
\langle \Psi, \neg(\phi_1 \wedge \cdots \wedge \phi_n) \rangle \text{ is a canonical undercut for } \langle \Phi, \alpha \rangle \text{ iff it is a maximally conservative undercut using the canonical enumeration of } \Phi
$$
Where: canonical enumeration is a fixed ordering of the support elements.
*(p.11/214)*

### Definition 6.1: Argument Tree
An argument tree for alpha has nodes that are arguments such that:
1. The root is an argument for alpha
2. For no node <Phi, beta> with ancestors <Phi_1, beta_1>, ..., <Phi_n, beta_n> is Phi a subset of Phi_1 union ... union Phi_n
3. Children of node N are all canonical undercuts for N that satisfy (2)
*(p.12/215)*

### Definition 8.1: Argument Structure
$$
\text{An argument structure for } \alpha \text{ is a pair } \langle \mathcal{P}, \mathcal{C} \rangle \text{ where } \mathcal{P} \text{ = set of argument trees for } \alpha, \mathcal{C} \text{ = set of argument trees for } \neg\alpha
$$
*(p.17/220)*

### Definition 8.10: Categoriser
A categoriser maps argument trees to numbers, capturing the relative strength of an argument taking into account undercuts to undercuts, and so on. The h-categoriser is defined recursively:
$$
h(N) = \begin{cases} 1 & \text{if } N \text{ is a leaf} \\ \frac{1}{1 + h(N_1) + \cdots + h(N_k)} & \text{if } N_1, \ldots, N_k \text{ are children of } N \end{cases}
$$
Where: h(N) in (0,1], higher means stronger (fewer/weaker undercuts).
*(p.19/222)*

### Definition 8.11: Accumulator
An accumulator takes pairs of numbers (from categoriser applied to pro and con trees) and returns an accumulated value. The balance of accumulated values determines whether a formula follows:
- Balance > 0: arguments for are stronger
- Balance < 0: arguments against are stronger
- Balance = 0: arguments are equal ("tied")
*(p.19-20/222-223)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| h-categoriser value | h(N) | - | - | (0, 1] | 222 | 1 for leaf nodes, decreases with more undercuts |
| Binary categoriser | s(T) | - | - | {0, 1} | 224 | 1 iff argument tree is successful (every leaf defends root) |
| Unit categoriser | c_1 | - | - | {0, 1} | 226 | Always maps to 1 |
| Free categoriser | r(T) | - | - | {0, 1} | 228 | 1 iff T is just a root node |

## Implementation Details
- Arguments are pairs <Phi, alpha> where Phi is a minimal consistent subset of Delta that entails alpha *(p.2/205)*
- Minimality is essential: it ensures every formula in the support contributes to proving the conclusion *(p.2/205)*
- The "more conservative" relation defines a pre-ordering on arguments (reflexive, transitive) *(p.3/206)*
- Equivalent arguments (Definition 3.8): <Phi, alpha> and <Phi', alpha'> are equivalent if Phi is logically equivalent to Phi' and alpha is logically equivalent to alpha' *(p.5/208)*
- For any argument, there are only finitely many arguments (up to equivalence) per consequent (Theorem 3.7) *(p.4/207)*
- Normal form: every formula in Phi is in the language of alpha when both are in normal form *(p.4/207)*
- Canonical enumeration of Delta required: each subset gets a fixed ordering of its elements *(p.2/205)*
- Argument tree construction terminates because Delta is finite and condition (2) prevents support cycles *(p.14/217)*
- If Delta is consistent, all argument trees have exactly one node (Theorem 6.6) *(p.14/217)*
- Argument structures are symmetrical: any property of P has a counterpart for C *(p.18/221)*

## Figures of Interest
- **Fig 1 (p.29/232):** XML structured news report example (country report with government stability, democracy, public spending, exports, oil price, elections, currency attributes)

## Results Summary
- Theorem 6.5: Argument trees are finite *(p.14/217)*
- Theorem 6.6: Consistent Delta implies single-node argument trees *(p.14/217)*
- Theorem 7.5: No two maximally conservative undercuts of the same argument are duplicates *(p.16/219)*
- Theorem 7.6: No branch in an argument tree contains duplicates except possibly child of root and its sibling *(p.16/219)*
- Theorem 8.4: If an argument tree in P has exactly one node, then C is empty (assuming P non-empty) *(p.17/220)*
- Theorem 8.8: Symmetry of argument structures — support of pro root nodes is superset of support of con undercut nodes *(p.18/221)*
- Theorem 9.10: Unit categoriser yields existential inference *(p.24/227)*
- Theorem 9.11: Unit categoriser yields unrebutted inference iff accumulator returns (1,0) *(p.24/227)*
- Theorem 9.16: Free categoriser yields free inference *(p.25/228)*
- Theorem 9.24: In Dung's framework with Constraint 1, every argument is acceptable w.r.t. itself, every conflict-free set is admissible *(p.27/230)*

## Limitations
- The framework uses classical propositional logic only; first-order extensions are mentioned but not developed *(p.31/234)*
- Universal inferencing is difficult to capture in this framework because it requires cross-checking consistency across different argument trees *(p.24/227)*
- Dung's framework collapses under Constraint 1 (every conflict-free set becomes admissible) — showing fundamental incompatibility with logic-based attack *(p.27/230)*
- The paper acknowledges that the approach is not restricted to propositional logic but other modes of representation can be chosen *(p.31/234)*
- Computational complexity not analyzed *(implicit throughout)*

## Arguments Against Prior Work
- Dung's abstract argumentation framework treats the attack relation as primitive without specifying what it means for one argument to attack another. This paper shows that when you formalize attack as logical contradiction of support, Dung's framework degenerates (Theorem 9.24) *(p.27/230)*
- Binary argumentation systems use a weaker notion of argument (restricted language of literals and rules). This paper shows these are a special case of the classical logic framework *(p.21/224)*
- Prior approaches to counting arguments for/against a conclusion are ad hoc. The categoriser/accumulator framework generalizes them *(p.22-23/225-226)*
- Argumentation logic systems [21] can be directly incorporated as a special case using the unit categoriser and accumulator *(p.24-26/227-229)*

## Design Rationale
- Classical logic chosen because it is the most general foundation; restricted logics (defeasible rules, etc.) are sub-languages that can be captured as special cases *(p.21/224)*
- Minimality in argument definition ensures relevance — every formula in the support actually contributes to the proof *(p.2/205)*
- Canonical undercuts chosen as the primitive counter-argument form because they are maximally conservative (use minimal information) and every defeater has a more conservative canonical undercut (Theorem 5.8) *(p.12/215)*
- Argument trees rather than graphs because the acyclicity condition (2) prevents support reuse, ensuring termination *(p.12-14/215-217)*
- Separating categorisation from accumulation allows different aggregation strategies to be plugged in without changing the underlying argument structure *(p.19/222)*

## Testable Properties
- For any argument <Phi, alpha>: Phi is consistent, Phi entails alpha, no proper subset of Phi entails alpha *(p.2/205)*
- Every rebuttal is a defeater (Theorem 4.6) *(p.6/209)*
- Every undercut is a defeater (trivially from definitions) *(p.6/209)*
- For every defeater, there exists a canonical undercut that is more conservative (Theorem 5.8) *(p.12/215)*
- Argument trees are finite (Theorem 6.5) *(p.14/217)*
- If Delta is consistent, every argument tree is a single node (Theorem 6.6) *(p.14/217)*
- h-categoriser value is in (0,1] for all argument trees *(p.19/222)*
- h-categoriser of leaf node = 1 *(p.19/222)*
- h-categoriser decreases as more undercuts are added *(p.19/222)*
- Two canonical undercuts of the same argument from different support elements are never duplicates (Theorem 5.6) *(p.11/214)*

## Relevance to Project
This paper is foundational for the argumentation layer of propstore. It provides the formal logical definitions needed to construct arguments from a knowledge base of claims, determine when arguments defeat each other, and aggregate competing arguments. The canonical undercut concept directly relates to how propstore should identify the minimal points of conflict between claims. The categoriser/accumulator framework provides a formal basis for the render layer's aggregation functions. The comparison with Dung's framework (Section 9.4) is critical context for why propstore uses both abstract (Dung AF) and structured (ASPIC+) argumentation.

## Open Questions
- [ ] How does this framework scale computationally? The paper does not address complexity of argument enumeration.
- [ ] Can the h-categoriser be extended to handle weighted or probabilistic arguments?
- [ ] How do argument structures interact with the ATMS label-based approach used in propstore?
- [ ] The paper mentions first-order extensions — are these developed in later Besnard & Hunter work?

## Related Work Worth Reading
- [5] Dung 1995 — Abstract argumentation, the framework this paper extends with internal structure
- [21] Pollock 1987 — Defeasible reasoning, rebutting vs undercutting defeat
- [9] Elvang-Goransson et al. — Dialectical argumentation framework (referenced for binary argumentation)
- [7] Chesnevar, Maguitman, Loui — Logical models of argumentation (ACM Computing Surveys)
- [17] Loui 1987 — Defeat among arguments
- [3] Benferhat, Dubois, Prade — Argumentative framework for dealing with inconsistency
- [13] Hunter — Merging inconsistent items of structured text
- [14] Hunter — Reasoning with inconsistency in structured text

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [5], the abstract argumentation framework this paper extends with internal argument structure; Section 9.4 shows Dung's framework collapses under logic-based attack (Theorem 9.24)
- [[Simari_1992_MathematicalTreatmentDefeasibleReasoning]] — cited as [22], mathematical treatment of defeasible reasoning with specificity-based preferences
- [[Pollock_1987_DefeasibleReasoning]] — cited as [18], defeasible reasoning with rebutting/undercutting defeat distinction that this paper formalizes in classical logic
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — cites this paper; ASPIC+ framework builds on classical-logic argumentation foundations
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — ASPIC+ tutorial references logic-based argumentation approach
- [[Amgoud_2008_BipolarityArgumentationFrameworks]] — cites this paper in context of logic-based argument construction
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — cites this paper; the h-categoriser from this paper is a ranking-based semantics
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — cites this paper in survey of argumentation approaches
- [[Caminada_2007_EvaluationArgumentationFormalisms]] — cites this paper in evaluation of argumentation formalisms

### New Leads (Not Yet in Collection)
- Vreeswijk (1997) — "Abstract argumentation systems" — AI 90:225-279 — alternative abstract argumentation that B&H compare against
- Chesnevar, Maguitman, Loui — "Logical models of argumentation" — ACM Computing Surveys — comprehensive survey
- Prakken & Vreeswijk — "Logical systems for defeasible argumentation" — handbook chapter surveying defeasible argumentation landscape

### Cited By (in Collection)
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — cites for classical logic instantiation of ASPIC+
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — cites for h-categoriser as ranking semantics
- [[Amgoud_2008_BipolarityArgumentationFrameworks]] — cites for logic-based argument definition
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — cites in context of structured argumentation approaches
- [[Caminada_2007_EvaluationArgumentationFormalisms]] — cites for argumentation formalisms comparison
- [[Doutre_2018_ConstraintsChangesSurveyAbstract]] — cites in survey of abstract argumentation
- [[Coste-Marquis_2005_SymmetricArgumentationFrameworks]] — cites for argument definition

### Conceptual Links (not citation-based)
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — Gabbay's equational semantics with numerical values in [0,1] are a generalization of B&H's h-categoriser; both assign graded strength to arguments based on attacker structure, but Gabbay works at the abstract level while B&H ground in classical logic
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — Baroni's principle-based evaluation criteria (directionality, reinstatement, skepticism adequacy) could be applied to evaluate the semantics induced by B&H's different categoriser/accumulator combinations
- [[Fang_2025_LLM-ASPICNeuro-SymbolicFrameworkDefeasible]] — LLM-ASPIC+ extracts knowledge for ASPIC+ reasoning; B&H's classical logic framework provides the formal semantics for what "argument" and "attack" mean in the classical-logic instantiation that ASPIC+ uses
