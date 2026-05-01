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
- Identification of "non-approximated predicates" — predicates whose ground instances can be determined from strict rules and facts alone *(p.5)*
- A prototypical implementation (ANGRY) with empirical evaluation showing scalability *(p.0, p.7-9)*
- Correctness proofs: the grounded and propositional argumentation theory has the same complete extensions as the original first-order theory *(p.6-7, appendix p.11-16)*

## Methodology
The approach consists of two main transformations:

1. **Transformation 1**: Translates a first-order argumentation theory T into a Datalog program P_T. The rules and contraries of T are encoded as Datalog rules. A Datalog engine computes ground substitutions, which are then used to ground the original ASPIC+ rules and contraries. *(p.3-4)*

2. **Transformation 2**: Extends Transformation 1 with ASPIC+-specific simplifications. Identifies "non-approximated predicates" that only depend on strict rules and facts, allowing them to be resolved entirely within Datalog without generating corresponding ground ASPIC+ rules. Additional simplifications include removing fact-only rules and eliminating contraries that can never be triggered. *(p.4-6)*

The final grounding procedure (Algorithm 1 for Transformation 1, Algorithm 2 for Transformation 2) produces a propositional ASPIC+ theory that preserves the complete extensions of the original first-order theory.

## Key Definitions

### Definition 1: Argumentation Theory (AT) *(p.2)*
An AT is a tuple T = (R_s, R_d, K, ~) where:
- R_s is a finite set of strict inference rules
- R_d is a finite set of defeasible inference rules  
- K = K_n ∪ K_p is the knowledge base (K_n = necessary premises/axioms, K_p = ordinary premises)
- ~ is a contrariness function mapping literals to sets of literals

### Definition 2: Arguments *(p.2)*
Arguments in ASPIC+ are built recursively:
- Every φ ∈ K is an argument with conclusion φ (Prem = {φ}, no sub-arguments, no rules, no top rule)
- If A_1,...,A_n are arguments with conclusions φ_1,...,φ_n and there exists a strict/defeasible rule r: φ_1,...,φ_n → ψ (or ⇒ ψ), then A = A_1,...,A_n → ψ (or ⇒ ψ) is an argument

### Definition 3: Attacks *(p.2)*
Argument A attacks argument B iff A undercuts or rebuts B:
- **Undercut**: A undercuts B on B' if Conc(A) ∈ ~(n(r)) for some defeasible rule r used as top rule in B', where B' is a sub-argument of B
- **Rebut**: A rebuts B on B' if Conc(A) ∈ ~(Conc(B')) for some B' ∈ Sub(B) with defeasible top rule
- Attacks always target defeasible elements (rules or conclusions of defeasible sub-arguments)

### Definition 4: Argumentation Framework (AF) *(p.2)*
An AF corresponding to an AT is a tuple (A, R) where A is the set of all arguments constructible from T and R is the attack relation. 

### Definition 5: Complete Extension *(p.2)*
For an AF (A, R), a set C ⊆ A is conflict-free iff there are no a,b ∈ C with (a,b) ∈ R. C defends a iff for every b attacking a, there exists c ∈ C attacking b. C is admissible iff conflict-free and defends all its members. C is a complete extension iff admissible and contains all arguments it defends.

### Definition 7: Datalog Program *(p.3)*
A Datalog program is a finite set of Datalog rules of the form p(t_1,...,t_n) :- p_1(s_1^1,...,s_{a_1}^1),...,p_m(s_1^m,...,s_{a_m}^m), where t_i and s_j^k are terms (constants or variables). The head is p(t_1,...,t_n), the body is the conjunction of atoms. A fact is a rule with empty body. A Datalog program P is ground iff all rules in P are ground. Ground(P) denotes the grounding.

### Definition 8: Immediate Consequence Operator T_P *(p.3)*
T_P(I) = {h(r)θ | r ∈ P, θ ground substitution, body(r)θ ⊆ I}. The least fixpoint lfp(T_P) computes the minimal Herbrand model.

### Definition 9: Ground substitutions from Datalog *(p.3)*
For a rule r from ASPIC+ AT, the set of ground substitutions is obtained by querying the Datalog program: find all θ such that body(r)θ ⊆ lfp(T_P).

### Definition 10: Datalog with stratified negation *(p.3)*
Extends Datalog by allowing negated atoms (not p(...)) in rule bodies. The Datalog program P is split into strata. The stratification ensures that for every rule with not p(...) in the body, p is defined at a lower stratum. Evaluation proceeds bottom-up by stratum.

### Definition 11: Safety of rules *(p.4)*
A rule r in a Datalog program is safe iff every variable in r appears in at least one positive body atom.

### Definition 12: Non-approximated predicates *(p.5)*
Let T = (R_s, R_d, K, ~) be an ASPIC+ AT. A predicate p is non-approximated iff:
- The rule whose head is an atom containing p is strict
- p depends negatively on a predicate q, then q is also non-approximated
- A producer q produces positively for p: q is non-approximated AND the rule consuming q is strict

The set of all non-approximated predicates is the minimal set satisfying:
1. p is a fact predicate, OR
2. p depends on an approximated predicate, OR  
3. It depends positively on predicates that are all non-approximated AND the rules are strict, OR
4. It depends negatively on q, and q is non-approximated

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
| Number of strict rules | n_s | - | - | 10-100 | 8 | Varied in S1 |
| Number of defeasible rules | n_d | - | - | 0 | 8 | Fixed at 0 in S1 |
| Number of contrary relations | n_c | - | - | 5-90 | 8 | Varied in S1 |
| Number of variables per rule | - | - | - | 1-3 | 8 | Varied in S1 |
| Number of constants | - | - | - | 3-30 | 8 | Varied in S1 |
| Grounding time limit | - | s | 300 | - | 8 | 5 min timeout |
| Time limit for full pipeline | - | s | 300 | - | 8 | 5 min total |
| S2 instances count | - | - | 20 | - | 8 | Per configuration |
| S3 instances count | - | - | - | - | 8 | From ICCMA 2023 |

## Methods & Implementation Details

### Transformation 1: AT to Datalog Program (Algorithm 1) *(p.3-4)*
Given AT T = (R_s, R_d, K, ~):
1. For each rule r ∈ R_s ∪ R_d with body atoms φ_1,...,φ_n and head ψ:
   - Create Datalog rule: ψ' :- φ_1',...,φ_n' (where primed versions map to Datalog atoms)
   - τ_1 is a fresh predicate unique to rule r
2. For each contrary relation φ ∈ ~(ψ):
   - Create Datalog rule encoding the contrary: connecting the conclusion atoms
3. For each knowledge base element φ ∈ K_n ∪ K_p:
   - Add as Datalog fact
4. Query the Datalog engine for ground substitutions

### Transformation 2: With Simplifications (Algorithm 2) *(p.4-6)*
Extends Transformation 1 by:
1. **Identify non-approximated predicates**: predicates whose ground instances are fully determined by strict rules and facts (Definition 12) *(p.5)*
2. **Resolve non-approximated predicates in Datalog**: Instead of generating ASPIC+ ground rules, evaluate these predicates entirely within the Datalog engine *(p.5-6)*
3. **Delete fact-only rules**: If a ground rule r has body atoms that are all facts and the conclusion is already a fact, remove r (it adds no new information) *(p.4, Algorithm 2 step 7)*
4. **Eliminate unused contraries**: Remove contrary relations where the attacking predicate has no ground instances *(p.4, Algorithm 2 step 8)*
5. **Repeat until fixpoint**: Iterate fact/contrary elimination and new fact production *(p.4)*

### Algorithm 1: Grounding via Transformation 1 *(p.4)*
```
Input: AT T = (R_s, R_d, K, ~), Datalog engine E
Output: ground AT T' = (R_s', R_d', K', ~')
1. P_T = translate(T) via Transformation 1
2. For each rule r ∈ R_s ∪ R_d:
   query = body(r) as conjunction
   results = E.query(P_T, query)
   for each ground substitution θ in results:
     add ground rule rθ to R_s' or R_d'
3. Ground contraries similarly
4. K' = ground knowledge base
5. Return T'
```

### Algorithm 2: Grounding via Transformation 2 *(p.7)*
```
Input: AT T = (R_s, R_d, K, ~), Datalog engine E
Output: ground AT T' with simplifications
1. Compute non-approximated predicates N
2. P_T = translate(T) via Transformation 2
   - For non-approximated predicates: resolve in Datalog
   - For approximated predicates: generate ground ASPIC+ rules
3. Query Datalog engine for ground substitutions
4. Generate ground rules (only for approximated predicates)
5. Generate ground contraries
6. Delete fact-only rules (rules where all body atoms are facts)
7. Eliminate contraries with no ground attacking instances
8. Repeat steps 6-7 until fixpoint
9. Return simplified ground AT T'
```

### ANGRY Prototype *(p.7-8)*
- Implementation of the grounding approach
- Written as a prototype system
- Uses an external Datalog engine as back-end
- Can interface with existing ASP/AF solvers after grounding
- Evaluated against naive grounding and existing tools

## Figures of Interest
- **Fig 1 (p.2):** Argumentation theory and induced AF from Example 1. Shows arguments A1-A6, attacks between them, and the complete extension structure.
- **Fig 2 (p.6):** Argumentation theory and induced AF from Example 5. Shows simplified grounding result with non-approximated predicates resolved in Datalog.
- **Fig 3a (p.7):** Argumentation theory from Example 6, demonstrating further simplification.
- **Fig 3b (p.7):** Argumentation theory and induced AF from Example 6 after grounding.
- **Fig 4 (p.8):** Results of Scenario S2 experiments. Scatter plots showing time vs. number of atoms for grounding and solving, comparing ANGRY approaches.
- **Table 1 (p.9):** Results of Scenarios S2, showing configurations S_1 through S_6 with metrics for grounded/solved instances, mean/median times for grounding and solving, comparing Transformation 1 vs Transformation 2 across different configurations.

## Results Summary

### Scenario S1: Random FO-ASPIC+ instances *(p.8)*
- Evaluated feasibility of grounding on random instances (Ontomerson et al. 2025)
- Tested with increasing number of strict rules, variables, and constants
- A 5-minute time limit for grounding and in S1 used 5-minute timeout for full pipeline
- S2 used 20 instances per configuration
- ANGRY successfully grounds instances that naive grounding cannot handle

### Scenario S2: Evaluating grounding quality *(p.8-9)*
- Compares Transformation 1 vs Transformation 2 (with simplifications)
- Tested on FO-ASPIC+ instances with varying:
  - n_s: 10, 30, 50 strict rules
  - n_d: 0, 5, 10 defeasible rules  
  - n_c: 5, 20, 50 contrary relations
  - Variables: 1-3 per rule
  - Constants: 3-30
- Transformation 2 produces significantly smaller ground theories
- Mean and median grounding times compared across configurations
- Transformation 2 consistently outperforms Transformation 1 in producing smaller groundings

### Scenario S3: Comparison with existing tools *(p.8-9)*
- Compared ANGRY against ICCMA 2023 benchmark instances
- Compared against ASPforASPIC (Lehtonen et al. 2021) for propositional ASPIC+
- Compared against TOAST (for grounding)
- Used instances from ICCMA 2023 competition
- Results show ANGRY can handle instances that other tools timeout on
- Some loss of performance on small instances due to overhead of Datalog translation
- Overall demonstrates scalability advantages for larger instances

## Limitations
- The prototype is currently limited to the grounding step — full argumentation reasoning requires piping output to an external AF solver *(p.9)*
- Overhead of Datalog translation can cause slower performance on small/trivial instances compared to direct propositional solvers *(p.9)*
- Only supports complete extensions semantics in the correctness proofs *(p.6-7)*
- The approach assumes function-free first-order ASPIC+ (no function symbols beyond constants) *(p.2-3)*
- Non-approximated predicate detection is conservative — some predicates that could be simplified may not be identified *(p.5)*
- The contrary function is limited to contraries between atoms (not arbitrary formulas) *(p.2)*
- Stratified negation in Datalog limits the forms of rules that can be handled *(p.3)*

## Arguments Against Prior Work
- ASPforASPIC (Lehtonen et al. 2021) only supports propositional ASPIC+, cannot handle first-order rules directly *(p.0, p.8)*
- TOAST and other existing grounding tools for argumentation do not provide ASPIC+-specific optimizations *(p.0)*
- Naive grounding causes exponential blow-up by generating all possible instantiations, making it impractical for realistic-sized theories *(p.0, p.3)*
- Existing ASP-based approaches like those of Modgil and Prakken 2018 and Lehtonen et al. 2021 do not address the grounding problem for first-order rules *(p.0)*
- General grounding approaches from ASP (Gebser et al. 2015) and Datalog do not exploit ASPIC+-specific structure *(p.5)*

## Design Rationale
- **Why Datalog over ASP for grounding**: Datalog's bottom-up evaluation naturally computes exactly the ground atoms needed, avoiding the overhead of ASP's answer-set computation. The goal is grounding only, not full reasoning. *(p.3)*
- **Why non-approximated predicates**: Strict rules with facts produce deterministic conclusions — these can be fully resolved in Datalog without generating ASPIC+ rules, dramatically reducing ground theory size. *(p.5)*
- **Why stratified negation**: Needed to handle contrariness (which involves negation-like contrary relations) within the Datalog framework while maintaining well-defined semantics. *(p.3)*
- **Why two transformations**: Transformation 1 provides the basic correct grounding; Transformation 2 adds optimizations. Separating them allows proving correctness incrementally. *(p.3-6)*
- **Why fact-only rule deletion**: A ground rule whose body consists entirely of facts and whose conclusion is already derivable adds no argumentative value — it cannot be attacked and produces no new information. *(p.4)*

## Testable Properties
- Transformation 1 preserves complete extensions: for AT T and its grounding T', the complete extensions of the induced AFs coincide (Theorem 3) *(p.6)*
- Transformation 2 preserves complete extensions: for AT T and its simplified grounding T'', the complete extensions coincide (Theorem 5) *(p.7)*
- Non-approximated predicates produce the same ground atoms via Datalog as via full ASPIC+ argument construction *(p.5, Lemma 1)*
- The grounding via Transformation 1 is finite (since the Herbrand universe is finite for function-free first-order languages) *(p.3)*
- Fact-only rule deletion does not affect complete extensions *(p.4, p.15)*
- Contrary elimination (removing contraries with no ground instances) does not affect complete extensions *(p.4, p.15-16)*
- Ground substitutions obtained from the Datalog engine are exactly those that make rule bodies true in the minimal model *(p.3, Definition 9)*
- For non-approximated predicate p: the set of ground atoms derivable from strict rules and facts alone equals the Datalog-computed ground atoms for p *(p.5, Definition 12)*
- Transformation 2 produces a subset of the ground rules produced by Transformation 1 (strictly fewer rules when non-approximated predicates exist) *(p.5-6)*

## Relevance to Project
This paper is directly relevant to propstore's ASPIC+ bridge and planned Defeasible Datalog rule language:
1. **Grounding procedure**: propstore's aspic_bridge.py currently operates over propositional claims. This paper provides the theoretical foundation for extending to first-order rules with variables.
2. **Datalog integration**: The translation from ASPIC+ to Datalog could inform propstore's planned Defeasible Datalog rule language, providing a grounding back-end.
3. **Non-approximated predicate optimization**: The concept of identifying predicates that can be fully resolved without argumentative overhead maps directly to propstore's need to distinguish between "settled facts" and "contested claims."
4. **Correctness guarantees**: The preservation of complete extensions through grounding provides formal justification for any grounding step propstore implements.
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
- Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2021. Declarative algorithms and complexity results for assumption-based argumentation. *J. Artif. Intell. Res.* 71:265-318. (ASPforASPIC — main comparison target)
- Modgil, S. and Prakken, H. 2018. Abstract rule-based argumentation. In Baroni et al., *Handbook of Formal Argumentation*, 287-364.
- Hanisch, P. and Rauschenbach, F. 2025. ANGRY: A grounder for rule-based argumentation. (System paper for the ANGRY prototype)
- Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2022. ASP-based algorithms for the alternative-based and abstraction-based semantics for ASPIC+.
- Fichte, J. K., Gaggl, S. A., and Rusovac, D. 2022. Rushing and strolling among answer sets — navigation made easy.
- Gebser, M., Kaminski, R., Kaufmann, B., Lühne, P., and Schaub, T. 2015. *Abstract grunge: Theory and practice of logic programming.*
