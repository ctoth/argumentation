---
title: "On the evaluation of argumentation formalisms"
authors: "Martin Caminada, Leila Amgoud"
year: 2007
venue: "Artificial Intelligence Journal, V.171 (5-6), pp. 286-310"
doi_url: "https://doi.org/10.1016/j.artint.2007.02.003"
---

# On the evaluation of argumentation formalisms

## One-Sentence Summary
Defines three rationality postulates (closure, direct consistency, indirect consistency) for evaluating rule-based argumentation systems, demonstrates that existing formalisms including ASPIC violate them, and provides two closure-operator solutions (propositional closure and transposition closure with restricted rebutting) that guarantee satisfaction of all three postulates under Dung's standard semantics.

## Problem Addressed
Rule-based argumentation systems that use strict rules and defeasible rules (such as ASPIC, Prakken & Sartor's system, and Garcia & Simari's system) can produce unintuitive results: contradictory conclusions may both be justified, conclusions derivable via strict rules from justified premises may not themselves be justified, and the closure of justified conclusions under strict rules may be inconsistent. There were no established criteria for evaluating whether an argumentation formalism produces "good" outputs.

## Key Contributions
- Three rationality postulates for evaluating argumentation systems: closure, direct consistency, indirect consistency
- Demonstration that existing rule-based argumentation formalisms violate these postulates through concrete counterexamples
- Two solutions based on closure operators for strict rules: propositional closure (Cl_pp) and transposition closure (Cl_tp)
- Proof that transposition closure combined with restricted rebutting satisfies all three postulates under ALL of Dung's standard semantics (not just grounded)
- Table 2 summary showing which combinations of rebutting type and closure operator satisfy which postulates under which semantics
- Observation that these postulates apply to ANY argumentation formalism using Dung's semantics, not just ASPIC

## Methodology
The paper works within a formal framework consisting of:
1. A defeasible theory T = (S, D) where S is a set of strict rules and D is a set of defeasible rules
2. An argumentation system (Arg, Defeat) built from T using Dung's abstract argumentation framework
3. Extensions under Dung's standard semantics (grounded, complete, preferred, stable)
4. Output = justified conclusions derived from extensions

The authors identify three problematic examples, then propose closure operators that modify the strict rule set to prevent the anomalies.

## Key Definitions

### Definition 1 (Argumentation system)
An argumentation system is a pair (A, Def) where A is a set of arguments and Def is a subset of A x A (the defeat relation). We say that argument A defeats argument B iff (A, B) is in Def.

### Definition 4 (Theory)
A defeasible theory T is a pair (S, D) where S is a set of strict rules and D is a set of defeasible rules.

### Definition 5 (Closure of a set of formulas)
Let P be a subset of L. The closure of P under the set S of strict rules, denoted Cl_S(P), is the smallest set such that:
- P is a subset of Cl_S(P)
- If phi_1, ..., phi_n -> psi is in S and phi_1, ..., phi_n are in Cl_S(P) then psi is in Cl_S(P)

### Definition 6 (Consistent set)
Let P be a subset of L, P is consistent iff there is no phi in P such that phi-bar (the negation/complement) is also in P.

### Definition 7 (Argument)
Let (S, D) be a defeasible theory. An argument A is:
- A_1, ..., A_n, n >= 0, are arguments such that there exists a strict rule Conc(A_1), ..., Conc(A_n) -> psi:
  - Conc(A) = psi
  - Sub(A) = Sub(A_1) union ... union Sub(A_n) union {A}
  - StrictRules(A) = StrictRules(A_1) union ... union StrictRules(A_n) union {Conc(A_1), ..., Conc(A_n) -> psi}
  - DefRules(A) = DefRules(A_1) union ... union DefRules(A_n)
- A_1, ..., A_n, n >= 0, are arguments such that there exists a defeasible rule Conc(A_1), ..., Conc(A_n) => psi:
  - Conc(A) = psi
  - Sub(A) = Sub(A_1) union ... union Sub(A_n) union {A}
  - StrictRules(A) = StrictRules(A_1) union ... union StrictRules(A_n)
  - DefRules(A) = DefRules(A_1) union ... union DefRules(A_n) union {Conc(A_1), ..., Conc(A_n) => psi}

### Definition 8 (Strict vs. defeasible argument)
An argument A is strict iff DefRules(A) = empty set; otherwise it is called defeasible.

### Definition 9 (Rebutting)
Let A, B be arguments. A rebuts B iff there exists B' in Sub(B) with Conc(A) = -c and Conc(B') = c, where B' is a non-strict argument and Conc(B') != -c.

### Definition 10 (Undercutting)
Let A and B be arguments. A undercuts B iff there exists B' in Sub(B) such that Conc(A) = -c and B' is a defeasible argument of the form B1', ..., Bn' => c, where Conc(A) = -Conc(B') -> -c.

(Note: The paper uses a notation where undercutting targets the applicability of a defeasible rule, using the objectification operator [.] that converts a meta-level expression into an object-level expression.)

### Definition 11 (Defeat)
Let A and B be elements of Arg. We say that A defeats B iff:
(1) A rebuts B, or
(2) A undercuts B.

### Definition 12 (Justified conclusions)
Let (Arg, Defeat) be an argumentation system, and {E_1, ..., E_n} (n >= 1) be the set of extensions under one of Dung's standard semantics.

- Conc(E_i) = {Conc(A) | A in E_i} (1 <= i <= n)
- Output = intersection of Conc(E_i) over all i

### Definition 13 (Consistent set of strict rules)
Let S be a set of strict rules. S is said to be consistent iff S, A, D is consistent (i.e., any such that A and D are strict arguments and if C in Sub(D)) then Conc(A) != -Conc(D).

### Definition 14 (Propositional operator)
Let S be a set of strict rules and P a subset of L. We define:

$$
Prop(S) = \{\phi_1 \wedge \ldots \wedge \phi_n \supset \psi \mid \phi_1, \ldots, \phi_n \longrightarrow \psi \in S\}
$$

$$
Cn_{prop}(P) = \{\psi \mid P \vdash \psi\}
$$

$$
Rules(P) = \{\phi_1, \ldots, \phi_n \longrightarrow \psi \mid \phi_1 \wedge \ldots \wedge \phi_n \supset \psi \in P\}
$$

The propositional closure of S is:

$$
Cl_{pp}(S) = Rules(Cn_{prop}(Prop(S)))
$$

### Definition 15 (Restricted rebutting)
Let A and B be arguments. A restrictively rebuts B on (A', B') iff A' in Sub(A) such that Conc(A') = -c and B' in Sub(B) such that the top rule of B' is a defeasible rule with conclusion c.

### Definition 17 (Transposition)
A strict rule a_1, ..., a_n -> psi is a transposition of a_1, ..., a_n -> psi for some 1 <= i <= n.

### Definition 18 (Transposition operator)
Let S be a set of strict rules. Cl_tp(S) is a minimal set such that:
- S is a subset of Cl_tp(S), and
- if s is in Cl_tp(S) and t is a transposition of s then t is in Cl_tp(S).

## Key Equations

The propositional closure:

$$
Cl_{pp}(\mathcal{S}) = Rules(Cn_{prop}(Prop(\mathcal{S})))
$$

Where: Prop converts strict rules to material implications, Cn_prop computes classical propositional consequences, Rules converts back to strict rules.

The transposition closure:

$$
Cl_{tp}(\mathcal{S}) = \mathcal{S} \cup \{t \mid t \text{ is a transposition of some } s \in Cl_{tp}(\mathcal{S})\}
$$

## Rationality Postulates

### Postulate 1 (Closure)
Let T be a defeasible theory, (A, Def) be an argumentation system built from T. Output is its set of justified conclusions, and E_1, ..., E_n its extensions under a given semantics. (A, Def) satisfies closure iff:
1. Conc(E_i) = Cl_S(Conc(E_i)) for each 1 <= i <= n
2. Output = Cl_S(Output)

### Postulate 2 (Direct Consistency)
Let T be a defeasible theory, (A, Def) be an argumentation system built from T. Output is its set of justified conclusions, and E_1, ..., E_n the extensions under a given semantics. (A, Def) satisfies direct consistency iff:
1. Conc(E_i) is consistent for each 1 <= i <= n
2. Output is consistent.

### Postulate 3 (Indirect Consistency)
Let T be a defeasible theory, (A, Def) be an argumentation system built from T and E_1, ..., E_n its extensions under a given semantics. (A, Def) satisfies indirect consistency iff:
1. Cl_S(Conc(E_i)) is consistent for each 1 <= i <= n
2. Cl_S(Output) is consistent.

## Parameters

| Name | Symbol | Units | Default | Range | Notes |
|------|--------|-------|---------|-------|-------|
| Language | L | - | - | any set of literals | Assumed to contain a function-free symbol set with negation |
| Strict rules | S | - | - | - | Rules of form a_1,...,a_n -> psi |
| Defeasible rules | D | - | - | - | Rules of form a_1,...,a_n => psi |
| Extensions | E_1,...,E_n | - | - | n >= 1 | Under Dung's standard semantics |
| Closure operator | Cl_S | - | - | {Cl_pp, Cl_tp} | Applied to strict rules to ensure postulates |

## Implementation Details

### Solution 1: Propositional Closure (Cl_pp)
1. Convert strict rules S to material implications: Prop(S)
2. Compute classical propositional closure: Cn_prop(Prop(S))
3. Convert back to strict rules: Rules(Cn_prop(Prop(S)))
4. Use the resulting Cl_pp(S) as the strict rule set in the defeasible theory
5. Under grounded semantics, all three postulates are satisfied (Theorem 1)
6. Limitation: Only guaranteed for grounded semantics, not preferred/stable

### Solution 2: Transposition Closure (Cl_tp) + Restricted Rebutting
1. Close strict rules under transposition: for each rule a_1,...,a_n -> psi, add all rules obtained by swapping one antecedent with the negated consequent
2. Replace standard rebutting with restricted rebutting (Definition 15): an argument can only rebut at the conclusion of a defeasible rule, not a strict rule
3. Under ALL of Dung's standard semantics, all three postulates are satisfied (Theorems 3 and 4)
4. This is the preferred solution

### Computational Complexity of Transposition
- A strict rule with n elements (n-1 antecedents + 1 consequent) can generate at most n transpositions
- A set S of strict rules with average size n generates at most |S| * n transpositions in the worst case
- More precisely, if S has k rules each of size at most n, transposition generates at most k * 4^n rules (accounting for all combinations)
- In practice, far fewer rules are generated because many transpositions duplicate existing rules
- For query-based approaches (answering specific questions), the full closure need not be materialized

### Key Properties of Cl_pp (Property 3)
1. S is a subset of Cl_pp(S)
2. If S_1 is a subset of S_2 then Cl_pp(S_1) is a subset of Cl_pp(S_2)
3. Cl_pp(Cl_pp(S)) = Cl_pp(S) (idempotent)

### Key Properties of Cl_tp
- S is closed under transposition iff Cl_tp(S) = S
- Properties analogous to Cl_pp (subset, monotone, idempotent)

## Problematic Examples

### Example 4 ("Married John")
S = {-> wr; -> go; -> -d} and D = {a -> m; b -> hw; b -> -hw}
Where: wr = "John wears a wedding ring", m = "John is married", hw = "John has a wife", go = "John often goes out and has fun with his friends", b = "John is a bachelor"

Arguments A_1 through A_6 can be built. Under grounded semantics, both "John is married" and "John is a bachelor" are considered justified, violating common sense.

The problem: The set of inferences under the set of strict rules may be inconsistent. The closure of Output = {wr, go, m, b} under strict rules is inconsistent.

### Example 5
S = {-> a; -> b; a,b -> c; c,b -> -a} and D = {a -> b; b -> c; c -> -a}
Shows justified conclusions are not closed under strict rules: can derive inconsistency.

### Example 6 (Garcia & Simari)
S = {-> a; -> b; a,b -> c; d -> g; b, c, f -> -g} and D = {a -> b; b -> c; d -> c; c -> f}
Shows that even Garcia & Simari's formalism, which handles some cases correctly, still has issues.

## Figures of Interest
- **Table 1 (page 15):** Effects of violated postulates - direct consistency violation leads to absurdities; indirect consistency violation leads to users not being allowed to apply modus ponens using strict rules; closure violation leads to conclusions that should come but appear to be missing
- **Table 2 (page 22):** Summary of which postulate combinations are satisfied under which rebutting type and closure operator
- **Fig. 1 (page 40):** Graphical representation of the proof of Theorem 4

## Results Summary

| Rebutting Type | Direct Consistency | Indirect Consistency | Closure |
|---|---|---|---|
| Standard Rebut + Cl_pp | Under any semantics | Under grounded extension only | Under grounded extension only |
| Restricted Rebut + Cl_tp | Under any semantics | Under any semantics | Under any semantics |

The transposition closure + restricted rebutting solution is strictly superior because it works under all of Dung's standard semantics, not just grounded.

## Key Theorems

### Theorem 1
Let (Arg, Defeat) be an argumentation system built from the defeasible theory (Cl_pp(S), D) such that Cl_pp(S) is consistent. Output is its set of justified conclusions and E its grounded extension. Then, (Arg, Defeat) satisfies closure and indirect consistency.

### Theorem 2
Let (Arg, Defeat_r) be an argumentation system built from the theory (Cl_tp(S), D) such that Cl_tp(S) is consistent. Output is its set of justified conclusions and E_1,...,E_n its extensions under one of Dung's standard semantics. Then, (Arg, Defeat_r) satisfies direct consistency and indirect consistency.

### Theorem 3
Let (Arg, Defeat_r) be an argumentation system built from the theory (Cl_tp(S), D) with S consistent. Output its set of justified conclusions and E_1,...,E_n its complete extensions. (Arg, Defeat_r) satisfies closure and consistency.

### Theorem 4
Let (Arg, Defeat_r) be an argumentation system built from the theory (Cl_tp(S), D) with Cl_tp(S) consistent. Output is its set of justified conclusions and E_1,...,E_n its extensions under one of Dung's standard semantics. (Arg, Defeat_r) satisfies direct consistency and indirect consistency.

## Limitations
- Propositional closure (Cl_pp) only works under grounded semantics; does not generalize to preferred/stable
- Transposition closure can generate exponentially many rules in the worst case (up to k * 4^n)
- The paper only considers propositional-level argumentation; first-order extensions are left for future work
- Argument strength/preferences are not treated (referred to footnote 2 citing Modgil's work)
- The paper does not address stable semantics separately (stable extensions are not guaranteed to exist)
- Only considers the case where there are no axioms (the language L has only function-free symbols)

## Testable Properties
- If an argumentation system satisfies indirect consistency, it also satisfies direct consistency (Proposition 6/7)
- If the strict rules are closed under transposition, then Cl_tp(S) = S
- Cl_pp is idempotent: Cl_pp(Cl_pp(S)) = Cl_pp(S)
- Under restricted rebutting + Cl_tp: if A restrictively rebuts B, then A rebuts B (but not vice versa)
- Every complete extension is also admissible and conflict-free (Proposition 1)
- The grounded extension is unique and is the intersection of all complete extensions

## Relevance to Project
This paper is foundational for the propstore's argumentation architecture. It provides the formal criteria (rationality postulates) that any rule-based argumentation system must satisfy to produce meaningful results. The ASPIC+ framework (Modgil & Prakken 2014, 2018) already in the collection was designed specifically to satisfy these postulates. Understanding what can go wrong (the counterexamples) and how to fix it (transposition closure + restricted rebutting) is essential for implementing correct argumentation-based claim evaluation.

Key connections:
- The closure operator solutions directly inform how strict rules should be managed in any ASPIC+-based implementation
- The restricted rebutting definition is adopted in ASPIC+ (Modgil & Prakken 2014, 2018)
- The rationality postulates are the acceptance criteria against which the propstore's argumentation subsystem should be validated

## Open Questions
- [ ] How does transposition closure interact with first-order rules?
- [ ] What is the practical computational cost of transposition closure for typical knowledge bases?
- [ ] How do these postulates extend to bipolar argumentation frameworks (Cayrol 2005)?
- [ ] Connection between Cl_tp and Clark completion for logic programs (mentioned in discussion)

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [42]; the foundational abstract argumentation framework (AF = (Args, Defeats), grounded/preferred/stable/complete extensions) that all of this paper's constructions build upon. The three rationality postulates are defined relative to Dung's semantics, and the key result (Cl_tp + restricted rebutting satisfies all postulates under ALL Dung semantics) requires Dung's framework as its semantic base.
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — cited as [25]; Cayrol's gradual semantics paper is cited in the context of related valuation approaches. Cayrol's bipolar framework adds support relations that interact with the closure and consistency requirements this paper defines.
- [[Caminada_2006_IssueReinstatementArgumentation]] — cited as [23] (same first author's companion paper); establishes the labelling-based semantics (in/out/undec) and semi-stable semantics that provide an alternative formal foundation for evaluating argumentation formalisms. The reinstatement labellings defined there are the formal substrate on which the postulates here are evaluated.
- [[Pollock_1987_DefeasibleReasoning]] — cited as [36]; Pollock's rebutting vs. undercutting defeat distinction is adopted directly in this paper's Definitions 9-11. Restricted rebutting (Definition 15), the key ingredient of the preferred solution, directly refines Pollock's rebutting to apply only at defeasible rule conclusions.

### New Leads (Not Yet in Collection)
- Prakken & Sartor (1997) [39] — "Argument-based extended logic programming with defeasible priorities" — one of the two structured argumentation systems demonstrated to violate the rationality postulates; precursor to ASPIC+
- Garcia & Simari (2004) [30] — "Defeasible logic programming: an argumentative approach" — DeLP; the second formalism shown to only partially satisfy the postulates (Example 6)
- Amgoud et al. (2004) [4] — ASPIC Deliverable D2.2; the original ASPIC framework that this paper evaluates and finds deficient; precursor to ASPIC+

### Supersedes or Recontextualizes
- (none — this paper defines evaluation criteria that motivated the redesign of ASPIC into ASPIC+, but does not directly supersede a collection paper)

### Cited By (in Collection)
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — cites this paper extensively; Example 4.1 (Married John) and Def 4.3 (closed under transposition) are drawn directly from this paper. ASPIC+ was designed specifically to satisfy the three rationality postulates defined here.
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — cites this paper for the rationality postulates and transposition closure; the revised conflict-free definition (attack-based rather than defeat-based) is motivated by the need to ensure all four postulates hold without auxiliary assumptions.
- [[Prakken_2010_AbstractFrameworkArgumentationStructured]] — cites this paper for the rationality postulates (closure, direct/indirect consistency) and the transposition/contraposition closure conditions (Defs 5.1-5.5).
- [[Prakken_2012_AppreciationJohnPollock'sWork]] — cites this paper in the context of ASPIC's handling of Pollock-style defeat and the formal criteria for evaluating argumentation systems.
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — cites the rationality postulates as the correctness criteria that the incomplete-information extension of ASPIC+ is designed to preserve.
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — cited in Baroni's Conceptual Links; both papers evaluate argumentation formalisms against formal criteria, covering complementary sides (structured vs. abstract, rule-based vs. extension-based).
- [[Caminada_2006_IssueReinstatementArgumentation]] — the companion labelling paper already lists this paper in its Cited By section.

### Conceptual Links (not citation-based)
**Principle-based evaluation:**
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — **Strong.** Both papers evaluate argumentation formalisms against formal criteria, but at different levels: Baroni evaluates abstract-level semantics (grounded, preferred, stable, semi-stable, CF2) against structural principles (reinstatement, directionality, SCC-recursiveness); this paper evaluates structured rule-based formalisms against semantic-output principles (closure, consistency). Together they provide a two-level evaluation framework: structural correctness (Baroni) and semantic-output correctness (Caminada & Amgoud).

**Structured argumentation and ASPIC+:**
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — **Strong.** ASPIC+ was redesigned specifically to satisfy the three rationality postulates defined in this paper. The transposition closure requirement (Def 4.3 in Modgil 2014) is taken directly from Definition 18 here, and restricted rebutting (Def 4.3 in Modgil 2014) from Definition 15 here.
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — **Strong.** The revised attack-based conflict-free definition in Modgil 2018 (replacing defeat-based) is motivated directly by the need to guarantee all rationality postulates from this paper under a broader class of instantiations and preference orderings.

## Related Work Worth Reading
- [4] Amgoud, M. Caminada, C. Cayrol, M. Lagasquie, and H. Prakken. Towards a consensual formal model: inference part. Technical report, In Deliverable D2.2 Draft Formal Semantics for Inference and Decision-Making. ASPIC project, 2004. (The ASPIC framework this paper evaluates)
- [14] P. Baroni and M. Giacomin. Two-resolutions: a general schema for argumentation semantics. (Semi-stable semantics)
- [27] P. Besnard and A. Hunter. A logic-based theory of deductive arguments. (Alternative approach to argument-based reasoning)
- [30] G. T. F. and K. Karaoglanidis. The zero argumentation framework. (Alternative formalism evaluated against postulates)
- [42] H. Prakken and G. Sartor. Argument-based extended logic programming with defeasible priorities. (Predecessor system shown to have issues)
- [44] H. Prakken and G. A. W. Vreeswijk. Logics for defeasible argumentation. (Survey of defeasible argumentation logics)
