---
title: "Grounding Rule-Based Argumentation Using Datalog"
authors: "Martin Diller, Sarah Alice Gaggl, Philipp Hanisch, Giuseppina Monterosso, Fritz Rauschenbach"
year: 2025
venue: "KR-25 (Proceedings of the 22nd International Conference on Principles of Knowledge Representation and Reasoning)"
doi_url: "https://doi.org/10.48550/arXiv.2508.10976"
produced_by:
  agent: "claude-opus-4-6"
  skill: "paper-reader"
  timestamp: "2026-04-10T07:41:08Z"
---
# Grounding Rule-Based Argumentation Using Datalog

## One-Sentence Summary
This paper presents an intelligent grounding procedure that translates first-order ASPIC+ argumentation theories into Datalog programs, using a Datalog engine to compute ground substitutions while applying ASPIC+-specific simplifications to avoid exponential blowup. *(p.0)*

## Problem Addressed
ASPIC+ is a main general framework for rule-based argumentation in AI, but most existing reasoning approaches only support propositional rules. First-order rules are commonly used in ASPIC+ examples, yet a preliminary grounding step is required to reason over them. Naive grounding leads to exponential increase in theory size. There is a lack of dedicated grounding solutions for ASPIC+. *(p.0)*

## Key Contributions
- An intelligent grounding procedure that translates first-order ASPIC+ instances into Datalog programs and queries a Datalog engine to obtain ground substitutions *(p.0)*
- ASPIC+-specific simplifications that avoid grounding rules with no influence on the reasoning process *(p.0)*
- Identification of "non-approximated predicates" through positive/negative dependency analysis: these are the predicates outside the approximation caused by dependency cycles containing a negative edge. *(Definition 12, p.5; [page image](pngs/page-005.png))*
- A prototypical implementation (ANGRY) with empirical evaluation showing scalability *(p.0, p.7-9)*
- Correctness proofs distinguish basic grounding (same argument graph), Transformation 2 (same complete/grounded/preferred/stable extensions), and the additional fact simplification in Algorithm 2 (same accepted conclusion sets, while arguments may change). *(Theorems 1-3; [basic](pngs/page-004.png), [Transformation 2](pngs/page-006.png), [Algorithm 2](pngs/page-007.png))*

## Methodology
The approach consists of two main transformations:

1. **Transformation 1**: Translates a first-order argumentation theory T into a Datalog program P_T. The rules and contraries of T are encoded as Datalog rules. A Datalog engine computes ground substitutions, which are then used to ground the original ASPIC+ rules and contraries. *(p.3-4)*

2. **Transformation 2**: Adds negated tests for non-approximated contraries of defeasible elements to the Datalog bodies used for grounding defeasible rules and assumptions. This excludes arguments known to be defeated, rather than simply removing every rule using a non-approximated predicate. Algorithm 2 separately materializes strict consequences of facts and removes satisfied fact premises. *(pp.5-7; [Transformation 2](pngs/page-005.png), [fact simplification](pngs/page-006.png), [algorithm](pngs/page-007.png))*

Algorithm 1 grounds an individual rule using answers for its auxiliary Datalog predicate. Algorithm 2 grounds the theory with Transformation 2 and additional fact simplification. The final procedure preserves the conclusion sets of complete, grounded, preferred, and stable extensions; it need not preserve the arguments themselves. *(pp.4,7; [Algorithm 1](pngs/page-004.png), [Algorithm 2 and Theorem 3](pngs/page-007.png))*

## Key Definitions

### Definition 1: Argumentation Theory (AT) *(p.2)*
An AT is a tuple `T = (contrary, R_s, R_d, K_n, K_p)` where:
- R_s is a finite set of strict inference rules
- R_d is a finite set of defeasible inference rules  
- K = K_n ∪ K_p is the knowledge base (K_n = necessary premises/axioms, K_p = ordinary premises)
- `contrary` is a finite collection of expressions mapping a propositional atom to a finite set of contrary atoms. *(Definition 1, pp.1-2; [start](pngs/page-001.png), [continuation](pngs/page-002.png))*

### Definition 2: Arguments *(p.2)*
Arguments in ASPIC+ are built recursively:
- Every φ ∈ K is an argument with conclusion φ, premise set {φ}, and no rules or top rule. Definition 2 does not define a Sub function; its inductive argument structure is the relevant carrier. *(p.2; [page image](pngs/page-002.png))*
- If A_1,...,A_n are arguments with conclusions φ_1,...,φ_n and there exists a strict/defeasible rule r: φ_1,...,φ_n → ψ (or ⇒ ψ), then A = A_1,...,A_n → ψ (or ⇒ ψ) is an argument

### Definition 3: Attacks *(p.2)*
Argument A attacks argument B iff A undercuts, rebuts, or undermines B:
- **Undercut**: A undercuts B on B' if Conc(A) ∈ ~(n(r)) for some defeasible rule r used as top rule in B', where B' is a sub-argument of B
- **Rebut**: A rebuts B on B' if Conc(A) ∈ ~(Conc(B')) for some B' ∈ Sub(B) with defeasible top rule
- **Undermine**: A undermines B on an ordinary premise s iff `Conc(A)` is a contrary of some `s ∈ Prem(B) ∩ K_p`.
- Attacks target defeasible elements: ordinary premises or defeasible rules (through the rule name or its conclusion). *(Definition 3, p.2; [page image](pngs/page-002.png))*

### Definition 4: Argumentation Framework (AF) *(p.2)*
An AF corresponding to an AT is a tuple (A, R) where A is the set of all arguments constructible from T and R is the attack relation. 

### Definition 5: Complete Extension *(p.2)*
For an AF (A, R), a set C ⊆ A is conflict-free iff there are no a,b ∈ C with (a,b) ∈ R. C defends a iff for every b attacking a, there exists c ∈ C attacking b. C is admissible iff conflict-free and defends all its members. C is a complete extension iff admissible and contains all arguments it defends.

### Definition 7: Datalog Program *(p.3)*
A Datalog program is a finite set of Datalog rules of the form p(t_1,...,t_n) :- p_1(s_1^1,...,s_{a_1}^1),...,p_m(s_1^m,...,s_{a_m}^m), where t_i and s_j^k are terms (constants or variables). The head is p(t_1,...,t_n), the body is the conjunction of atoms. A fact is a rule with empty body. A Datalog program P is ground iff all rules in P are ground. Ground(P) denotes the grounding.

### Definition 8: Herbrand universe, base, and grounding *(p.3)*
`U_P` contains the constants occurring in P; `B_P` contains the ground atoms built from P's predicates and these constants. Grounding substitutes these constants for rule variables; `gr(P)` is the union of the groundings of its rules. *([page image](pngs/page-003.png))*

### Definition 9: Immediate consequence operator and queries *(p.3)*
`T_P(I) = {h | B → h ∈ gr(P), B ⊆ I}`. The least fixpoint is obtained from the empty set by iteration. A query `(P,q)` asks for all ground atoms with predicate q derivable from P. Grounding the argumentation theory later queries the auxiliary predicate introduced for each rule. *([page image](pngs/page-003.png))*

### Definition 10: Datalog with stratified negation *(p.3)*
Extends Datalog by allowing negated atoms (not p(...)) in rule bodies. The Datalog program P is split into strata. The stratification ensures that for every rule with not p(...) in the body, p is defined at a lower stratum. Evaluation proceeds bottom-up by stratum.

### Definition 11: First-order argumentation theory *(p.3)*
The tuple has the same five components as Definition 1, now with safe first-order strict/defeasible rules and safe contrary expressions. Head variables and defeasible-rule-name variables must occur in the rule body; contrary expressions contain no constants and introduce no variables beyond their source atom. Facts and assumptions remain finite sets of ground atoms. For Datalog rules, safety is already defined in Definition 7 as head variables being contained in body variables. *([page image](pngs/page-003.png))*

### Definition 12: Dependencies and approximated predicates *(p.5)*
For a rule with head predicate p, p depends positively on predicates in the rule body and negatively on predicates occurring in contraries of the rule's defeasible elements. A predicate occurring in an assumption also depends negatively on predicates in that assumption's contrary expression.

The **approximated** predicates form the minimal set containing a predicate p whenever:
1. p depends on an approximated predicate; or
2. p lies on a dependency cycle containing at least one negative dependency.

Every predicate outside this set is **non-approximated**. The definition does not require all rules producing a non-approximated predicate to be strict: it analyzes whether the grounding can determine derivability in an extension, including the relevant contrary dependencies. *([Definition 12 and Example 6 page image](pngs/page-005.png))*

## Key Equations / Statistical Models

$$
T_P(I) = \{h(r)\theta \mid r \in P, \theta \text{ ground substitution}, body(r)\theta \subseteq I\}
$$
Where: T_P is the immediate consequence operator, I is an interpretation (set of ground atoms), h(r) is the head of rule r, θ is a ground substitution, body(r) is the body of rule r.
*(p.3)*

$$
lfp(T_P) = T_P^0(\emptyset) \cup T_P^1(\emptyset) \cup \cdots = \bigcup_{i \geq 0} T_P^i(\emptyset)
$$
Where: lfp is the least fixpoint, computed by iterating T_P starting from the empty set until convergence.
*(p.3)*

$$
\text{Ground substitutions for rule } r: \{(r, \theta) \mid body(r)\theta \subseteq lfp(T_{P_T})\}
$$
Where: P_T is the Datalog program derived from argumentation theory T, and θ ranges over ground substitutions with constants from the Herbrand universe.
*(p.3)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Grounding time limit | - | min | 20 | - | 7 | Per instance |
| Reasoning time limit (S1/S2) | - | min | 20 additional | - | 7 | Separate from grounding |
| Memory limit | - | GB | 32 | - | 7 | Per instance |
| S1 instances per domain | - | - | 20 | - | 7 | Legal-bench-derived theories |
| S2 maximum variables per rule | - | - | - | 3, 4, 5, 7, 9, 11, 13 | 9 | Columns of Table 1 |
| S3 instances | - | - | - | translated ASP instances | 7, 9 | Grounding comparison with Gringo |

*Configuration provenance: [evaluation setup](pngs/page-007.png), [Table 1](pngs/page-009.png). The existing page-008 image obscures most of the detailed configuration text; the former numeric rule/constant ranges are not retained as verified transcriptions.*

## Methods & Implementation Details

### Transformation 1: AT to Datalog Program (Algorithm 1) *(p.3-4)*
For a strict rule `B(X) → h(Y)` or a defeasible rule `n(Z): B(X) ⇒ h(Y)`, introduce a fresh auxiliary predicate `n_r(X)` and Datalog rules `B(X) → n_r(X)` and `n_r(X) → h(Y)`. For a defeasible rule also add `n_r(X) → n(Z)`. Facts and assumptions become Datalog facts. Query `n_r` to recover rule substitutions; query the source predicate of each contrary expression to ground that expression. Contrary expressions are not themselves translated into inference rules connecting their source and target atoms. *(Transformation 1 and Algorithm 1; [page image](pngs/page-004.png))*

### Transformation 2: With Simplifications (Algorithm 2) *(p.4-6)*
Transformation 2 and the additional algorithmic simplification have distinct roles:
1. **Identify approximated/non-approximated predicates** using Definition 12's dependency graph.
2. **Filter derivations by settled contraries**: for each rule, add negated body tests for exactly the non-approximated predicates occurring in contraries of its defeasible elements. Transform assumptions similarly; keep facts as Datalog facts.
3. **Query assumptions as well as rules and contraries**: this can remove assumptions whose settled contrary is derivable. It does not discard all non-approximated predicates from the resulting argumentation theory.
4. **Materialize strict facts in Algorithm 2**: process rule SCCs in topological order, remove known fact atoms from rule bodies, and turn a remaining empty-body strict rule into a fact when its head is not an ordinary premise.
5. **Iterate fact production within the current SCC**, then ground assumptions and contrary expressions and assemble the theory.

*(pp.5-7; [Transformation 2](pngs/page-005.png), [fact motivation](pngs/page-006.png), [Algorithm 2](pngs/page-007.png))*

### Algorithm 1: Grounding an individual ASPIC+ rule *(p.4)*
```
Input: theory T, rule r, translated Datalog program P_T with n_r(X)
Output: gr_DL(r, P_T)
1. result = empty set
2. For each answer n_r(a) to query (P_T, n_r):
   form substitution X_i -> a_i
   add the corresponding ground instance of r to result
3. Return result
```
*The auxiliary predicate records bindings for all rule-body variables. [Algorithm 1 page image](pngs/page-004.png).*

### Algorithm 2: Grounding via Transformation 2 *(p.7)*
```
Input: theory T, topologically ordered rule SCCs L_T,
       Datalog program P_T from Transformation 2
Output: gr_DL(T)
1. Ground facts = K_n; ground rules = empty set
2. For each rule SCC C in L_T:
   ground its rules using Algorithm 1
   repeat:
     remember the current fact set
     for each grounded rule r in this SCC:
       remove known facts from its body
       if r is strict, its body is empty, and its head is not in K_p:
         add its head to facts and remove r
   until no new facts were added
   collect the remaining rules of this SCC
3. Query P_T for the surviving ordinary premises
4. Ground the contrary expressions via their source-predicate queries
5. Return the theory with these rules, facts, premises, and contraries
```
*Paraphrase of the displayed Algorithm 2, including its `head(r) not in K_p` condition; [page image](pngs/page-007.png).*

### ANGRY Prototype *(p.7-8)*
- Implementation of the grounding approach
- Written in Rust
- Uses the Datalog engine Nemo as back-end
- Can interface with existing ASP/AF solvers after grounding
- Evaluated against naive grounding and existing tools

*Implementation and comparison systems: [evaluation page image](pngs/page-007.png).*

## Figures of Interest
- **Fig 1 (p.2):** Argumentation theory and induced AF from Example 1. Shows arguments A1-A6, attacks between them, and the complete extension structure.
- **Fig 2 (p.6):** Theory and argument graph from Example 7, after Transformation 2 removes defeated arguments. *([page image](pngs/page-006.png))*
- **Fig 3 (p.7):** Theory and argument graph from Example 10 after fact simplification; arguments change while accepted conclusion sets agree. *([page image](pngs/page-007.png))*
- **Table 1 (p.9):** Scenario S2 configurations c1-c5, with columns for up to 3, 4, 5, 7, 9, 11, and 13 variables per rule; reports grounded/solved counts, grounding timeouts/memory outs, and grounding mean/median seconds. It is not a Transformation 1 versus 2 table. *([page image](pngs/page-009.png))*

## Results Summary

### Scenario S1: First-order ground+solve comparison *(p.7)*
- Instances are based on ASPIC+ encodings from Legal bench, inspired by Robaldo et al. (2024), with 20 instances per domain and increasing numbers of knowledge-base atoms.
- Compares ANGRY plus ASPforASPIC against Arg2P for enumeration of claim sets under complete semantics.
- Grounding and reasoning each receive a separate 20-minute limit; memory is limited to 32 GB.
- The conclusion reports that the combined ground+solve approach outperforms the existing first-order argumentation comparison system.

*([setup](pngs/page-007.png), [conclusion](pngs/page-009.png))*

### Scenario S2: Feasibility as instance size and variables increase *(pp.7,9)*
- Uses first-order ASPIC+ instances with increasing numbers of atoms, rules, and variables.
- Table 1 reports five configurations c1-c5 and variable limits up to 3, 4, 5, 7, 9, 11, and 13 per rule, rather than a Transformation 1 versus 2 comparison.
- Grounding mean/median times, grounded/solved counts, and grounding timeouts/memory outs are reported separately.
- The paper identifies the number of variables per rule as the dominant influence; more rules and contraries are less problematic when variable counts remain low.
- For challenging instances, memory outs occur more frequently than timeouts. The authors suggest that many real-world rules would use no more than four or five variables.

*([scenario definition](pngs/page-007.png), [Table 1 and interpretation](pngs/page-009.png))*

### Scenario S3: ASP grounding comparison *(pp.7,9)*
- Translates well-known ASP instances to ASPIC+ and compares ANGRY as a grounder against Gringo.
- Figure 5 compares resulting grounding sizes and records grounding time by color.
- The conclusion describes ANGRY's grounding sizes as comparable and slightly larger, while ANGRY is less efficient in runtime than Gringo on this comparison.
- The comparison assesses grounding quality, distinct from S1's argumentation ground+solve evaluation.

*([scenario and systems](pngs/page-007.png), [results and conclusion](pngs/page-009.png))*

## Limitations
- The prototype performs grounding; the evaluated argumentation pipeline combines it with ASPforASPIC, an ASP-based propositional reasoner. *(p.7; [page image](pngs/page-007.png))*
- In the translated-ASP comparison, ANGRY is less efficient than Gringo; the paper identifies translations and Gringo's ASP-specific optimizations as relevant factors. *(p.9; [page image](pngs/page-009.png))*
- Correctness is not limited to complete semantics: Transformation 1 preserves admissible/complete/grounded/preferred/stable extensions, Transformation 2 preserves complete/grounded/preferred/stable extensions, and Algorithm 2 preserves accepted conclusion sets for those four complete-based semantics. *(Theorems 1-3; [basic](pngs/page-004.png), [Transformation 2](pngs/page-006.png), [Algorithm 2](pngs/page-007.png))*
- The approach assumes function-free first-order ASPIC+ (no function symbols beyond constants) *(p.2-3)*
- The dependency-based non-approximation criterion determines which contrary tests can safely be evaluated during grounding; predicates affected by cycles containing a negative edge remain approximated for the solver. *(Definition 12, p.5; [page image](pngs/page-005.png))*
- The contrary function is limited to contraries between atoms (not arbitrary formulas) *(p.2)*
- Stratified negation in Datalog limits the forms of rules that can be handled *(p.3)*

## Arguments Against Prior Work
- ASPforASPIC (Lehtonen et al. 2021) only supports propositional ASPIC+, cannot handle first-order rules directly *(p.0, p.8)*
- Arg2P is the first-order ASPIC+-like comparison system discussed in the introduction; the paper motivates a dedicated grounding procedure instead of relying on that system's reasoning pipeline. *(p.1; [page image](pngs/page-001.png))*
- Naive grounding causes exponential blow-up by generating all possible instantiations, making it impractical for realistic-sized theories *(p.0, p.3)*
- Existing ASP-based approaches like those of Modgil and Prakken 2018 and Lehtonen et al. 2021 do not address the grounding problem for first-order rules *(p.0)*
- General grounding approaches from ASP (Gebser et al. 2015) and Datalog do not exploit ASPIC+-specific structure *(p.5)*

## Design Rationale
- **Why Datalog over ASP for grounding**: Datalog's bottom-up evaluation naturally computes exactly the ground atoms needed, avoiding the overhead of ASP's answer-set computation. The goal is grounding only, not full reasoning. *(p.3)*
- **Why non-approximated predicates**: Their contrary atoms can be tested during grounding, which excludes known-defeated assumptions and rule instances. This is distinct from Algorithm 2's additional strict-fact materialization. *(pp.5-7; [Transformation 2](pngs/page-005.png), [Algorithm 2](pngs/page-007.png))*
- **Why stratified negation**: Needed to handle contrariness (which involves negation-like contrary relations) within the Datalog framework while maintaining well-defined semantics. *(p.3)*
- **Why two transformations**: Transformation 1 provides the basic correct grounding; Transformation 2 adds optimizations. Separating them allows proving correctness incrementally. *(p.3-6)*
- **Why fact materialization**: Algorithm 2 deletes known facts from rule bodies and promotes an empty-body strict rule's head to a fact if that head is not an ordinary premise. Removing that strict rule changes the argument graph, so correctness is stated for accepted conclusions rather than identical extensions. *(Examples 9-10 and Theorem 3, pp.6-7; [motivation](pngs/page-006.png), [algorithm and theorem](pngs/page-007.png))*

## Testable Properties
- Transformation 1 yields the same arguments and attacks as naive grounding (Lemma 1), hence the same admissible, complete, grounded, preferred, and stable extensions (Theorem 1). *(p.4; [page image](pngs/page-004.png))*
- Transformation 2 preserves complete, grounded, preferred, and stable extensions (Theorem 2); it need not preserve admissible extensions (Example 8). *(p.6; [page image](pngs/page-006.png))*
- Algorithm 2's additional fact simplification preserves sets of extension conclusions under complete, grounded, preferred, and stable semantics (Theorem 3), even though the argument sets can differ. *(p.7; [page image](pngs/page-007.png))*
- The grounding via Transformation 1 is finite (since the Herbrand universe is finite for function-free first-order languages) *(p.3)*
- Fact materialization must respect Algorithm 2's condition that a promoted head is not an ordinary premise; extension identity is not its preservation contract. *(p.7; [page image](pngs/page-007.png))*
- Ground substitutions are recovered from answers to a rule's auxiliary predicate, which records its body-variable bindings (Algorithm 1). *(p.4; [page image](pngs/page-004.png))*
- Non-approximated predicates are the complement of Definition 12's dependency-closed set of approximated predicates; strict-rule-only derivability is not the criterion. *(p.5; [page image](pngs/page-005.png))*
- Transformation 2 may exclude rule instances through non-approximated contrary tests; non-approximated predicates alone do not imply a strict reduction in grounding size. *(Transformation 2 and Example 7, p.5; [page image](pngs/page-005.png))*

## Relevance to Project
This paper is directly relevant to propstore's ASPIC+ bridge and planned Defeasible Datalog rule language:
1. **Grounding procedure**: propstore's aspic_bridge.py currently operates over propositional claims. This paper provides the theoretical foundation for extending to first-order rules with variables.
2. **Datalog integration**: The translation from ASPIC+ to Datalog could inform propstore's planned Defeasible Datalog rule language, providing a grounding back-end.
3. **Non-approximated predicate optimization**: The concept of identifying predicates that can be fully resolved without argumentative overhead maps directly to propstore's need to distinguish between "settled facts" and "contested claims."
4. **Correctness guarantees**: The paper separates identical argument graphs, preserved extensions, and preserved accepted conclusions. A grounding implementation must use the guarantee corresponding to its actual simplifications. *(Theorems 1-3; [basic](pngs/page-004.png), [Transformation 2](pngs/page-006.png), [Algorithm 2](pngs/page-007.png))*
5. **ANGRY prototype**: Could serve as a reference implementation or integration target for propstore's argumentation engine.

## Open Questions
- [ ] How does the ANGRY prototype handle updates/incremental grounding when new rules or facts are added?
- [ ] Can the non-approximated predicate analysis be extended to identify predicates that are non-approximated under specific assumption sets (relevant to ATMS-style reasoning)?
- [ ] What is the complexity of the non-approximated predicate identification algorithm?
- [ ] How does this interact with preference orderings on defeasible rules (not addressed in the paper)?
- [ ] Can Transformation 2's simplifications be applied incrementally as new rules are added?

## Collection Cross-References

### Already in Collection
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — the definitive ASPIC+ reference; this paper's grounding procedure operates over the framework defined here
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — tutorial companion to Modgil & Prakken 2018; provides the definitions (arguments, attacks, extensions) that this paper's correctness proofs rely on
- [[Lehtonen_2020_AnswerSetProgrammingApproach]] — ASPforASPIC, the main comparison system; handles propositional ASPIC+ via ASP but cannot handle first-order rules directly
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md) - direct ABA ASP and complexity reference cited as part of the ASP-based structured-argumentation implementation lineage.
- [[Dung_1995_AcceptabilityArguments]] — foundational AF semantics that ASPIC+ instantiates; the complete extensions preserved by Diller's grounding are Dung's complete extensions
- [[Caminada_2006_IssueReinstatementArgumentation]] — labellings-based semantics for Dung AFs; the semantics that ANGRY's grounded output feeds into
- [[Diller_2015_ExtensionBasedBeliefRevision]] — earlier work by the same first author on extension-based belief revision in AFs

### New Leads (Not Yet in Collection)
- Hanisch and Rauschenbach (2025) — "ANGRY: A grounder for rule-based argumentation" — system paper for the prototype evaluated in this work
- Jordan, Scholz, and Subotic (2016) — "Souffle: On synthesis of program analyzers" — high-performance Datalog engine relevant as grounding back-end
- Gebser et al. (2015) — "Abstract Grounding" / Clingo grounding infrastructure — ASP grounding technology compared against

### Supersedes or Recontextualizes
- (none — this is a new contribution area not previously covered in the collection)

### Conceptual Links (not citation-based)
- [[Fang_2025_LLM-ASPICNeuro-SymbolicFrameworkDefeasible]] — both papers extend ASPIC+ beyond propositional rules; Fang uses LLMs for rule construction while Diller uses Datalog for grounding. Complementary: Fang produces the first-order rules, Diller grounds them for reasoning.
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — both address computational tractability of ASPIC+; Odekerken handles incomplete information via ASP while Diller handles first-order grounding via Datalog. Different bottlenecks, same goal of making ASPIC+ computationally practical.
- [[Odekerken_2025_ArgumentativeReasoningASPICIncompleteInformation]] — extended version of Odekerken 2023; same conceptual relationship as above.
- [[Li_2017_TwoFormsMinimalityASPIC]] — Li's minimality analysis constrains which arguments are constructed; Diller's grounding constrains which ground rules are generated. Both reduce the size of the argumentation framework through different mechanisms.
- [[Morris_2020_DefeasibleDisjunctiveDatalog]] — Morris extends KLM-style defeasible reasoning (Rational, Lexicographic, Relevant Closure) into Disjunctive Datalog. Diller uses Datalog as a grounding back-end for ASPIC+. Complementary: Morris defines defeasible entailment semantics in Datalog, Diller provides the grounding mechanism that could make first-order defeasible Datalog rules computationally tractable.

### Cited By (in Collection)
- (none found)

## Related Work Worth Reading
- Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2021. Declarative algorithms and complexity results for assumption-based argumentation. *J. Artif. Intell. Res.* 71:265-318. (direct ABA ASP/computational baseline) → NOW IN COLLECTION: [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md)
- Modgil, S. and Prakken, H. 2018. Abstract rule-based argumentation. In Baroni et al., *Handbook of Formal Argumentation*, 287-364.
- Hanisch, P. and Rauschenbach, F. 2025. ANGRY: A grounder for rule-based argumentation. (System paper for the ANGRY prototype)
- Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2022. ASP-based algorithms for the alternative-based and abstraction-based semantics for ASPIC+.
- Fichte, J. K., Gaggl, S. A., and Rusovac, D. 2022. Rushing and strolling among answer sets — navigation made easy.
- Gebser, M., Kaminski, R., Kaufmann, B., Lühne, P., and Schaub, T. 2015. *Abstract grunge: Theory and practice of logic programming.*
