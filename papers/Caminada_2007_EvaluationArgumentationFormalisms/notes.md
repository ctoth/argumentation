---
title: "On the evaluation of argumentation formalisms"
authors: "Martin Caminada, Leila Amgoud"
year: 2007
venue: "Artificial Intelligence Journal, V.171 (5-6), pp. 286-310"
doi_url: "https://doi.org/10.1016/j.artint.2007.02.003"
---

# On the evaluation of argumentation formalisms

## One-Sentence Summary
Defines three rationality postulates (closure, direct consistency, indirect consistency) for evaluating rule-based argumentation systems, demonstrates violations in existing formalisms, and shows that consistent propositional or transposition closure combined with restricted rebutting satisfies all three under complete, grounded and preferred semantics.

Source pagination below refers to the local 40-page preprint, not the journal pagination. Its definition of “Dung's standard semantics” explicitly means complete, grounded and preferred ([p. 5](pngs/page-004.png)); stable semantics is excluded because the family of extensions may be empty ([p. 9](pngs/page-008.png)).

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
3. Extensions under Dung's standard semantics as defined here: grounded, complete and preferred
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
Let A, B be arguments. A rebuts B iff there exist A' in Sub(A) with Conc(A') = phi and B' in Sub(B) such that B' is non-strict and Conc(B') = -phi. The attacking conclusion may belong to a subargument of A; it need not be Conc(A). “Non-strict” means some defeasible rule occurs in B', not necessarily its top rule. Source: [p. 7, Definition 9](pngs/page-006.png).

### Definition 10 (Undercutting)
Let A and B be arguments. A undercuts B iff there exists B' in Sub(B) of the form B''_1, ..., B''_n => psi, and A' in Sub(A) such that Conc(A') = negation of the objectified rule Conc(B''_1), ..., Conc(B''_n) => psi. In symbols, Conc(A') = ¬⌈Conc(B''_1), ..., Conc(B''_n) => psi⌉. This attacks applicability of the specific defeasible rule, rather than asserting the contrary of its conclusion. Source: [p. 8, Definition 10](pngs/page-007.png).

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
Let S be a set of strict rules. S is consistent iff there do not exist strict arguments A and B with Conc(A) = -Conc(B). Thus the strict rules alone must not construct arguments for complementary literals. Source: [p. 10, Definition 13](pngs/page-009.png).

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

Unlike Definition 9, this requires the targeted subargument's top rule itself to be defeasible. A' can still be any subargument of A. Definition 16 sets Defeat_r to restricted rebutting or undercutting. Proposition 8 proves closure for complete extensions with Defeat_r even without closing S under either rule operator. Sources: [p. 18](pngs/page-017.png), [p. 19](pngs/page-018.png).

### Definition 17 (Transposition)
A strict rule s is a transposition of phi_1, ..., phi_n -> psi iff, for some 1 <= i <= n,

$$
s = \phi_1,\ldots,\phi_{i-1},\neg\psi,\phi_{i+1},\ldots,\phi_n \longrightarrow \neg\phi_i.
$$

Replace the selected premise by the negated old conclusion, and make the selected premise's negation the new conclusion. Source: [p. 20, Definition 17](pngs/page-019.png).

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
| Language | L | - | - | set of literals | Literals are atoms or their negations, with a complement operation |
| Strict rules | S | - | - | n >= 0 | Rules of form a_1,...,a_n -> psi; empty antecedents are allowed |
| Defeasible rules | D | - | - | n >= 0 | Rules of form a_1,...,a_n => psi; empty antecedents are allowed |
| Extensions | E_1,...,E_n | - | - | n >= 1 | Under Dung's standard semantics |
| Formula closure | Cl_S | - | - | subsets of L | Closes a formula set under the fixed strict rules S |
| Rule closure operators | Cl_pp, Cl_tp | - | - | strict rule sets | Two alternative ways of enriching S |

## Implementation Details

### Solution 1: Propositional Closure (Cl_pp)
1. Convert strict rules S to material implications: Prop(S)
2. Compute classical propositional closure: Cn_prop(Prop(S))
3. Convert back to strict rules: Rules(Cn_prop(Prop(S)))
4. Use the resulting Cl_pp(S) as the strict rule set in the defeasible theory
5. With unrestricted rebutting and consistent Cl_pp(S), grounded semantics satisfies all three postulates (Theorem 1 plus direct consistency)
6. With restricted rebutting and consistent Cl_pp(S), all three hold under complete, grounded and preferred semantics (Proposition 8 and Theorem 2)
7. Unrestricted rebutting still permits a preferred extension containing both m and b in Married John; closing its conclusions derives hw and ¬hw, even though skeptical Output avoids this inconsistency ([p. 18](pngs/page-017.png))

### Solution 2: Transposition Closure (Cl_tp) + Restricted Rebutting
1. Close strict rules under transposition: replace each selected antecedent a_i by ¬psi and make ¬a_i the consequent; include transpositions of generated rules until closure
2. Replace standard rebutting with restricted rebutting (Definition 15): an argument can only rebut at the conclusion of a defeasible rule, not a strict rule
3. If Cl_tp(S) is consistent, complete, grounded and preferred semantics satisfy all three postulates (Proposition 8 and Theorem 4)
4. With unrestricted rebutting, Theorem 3 only supplies the grounded guarantee; Example 7 shows the remaining preferred-extension problem ([p. 21](pngs/page-020.png))
5. Transposition avoids the full classical closure's additional consequences, including explosion rules such as p, ¬p -> ¬q that can let conflicting arguments defeat unrelated conclusions ([p. 20](pngs/page-019.png))

### Computational Complexity of Transposition
- The paper states that a strict rule has at most k transpositions, where k is its body size.
- For n strict rules with average body size k, it gives at most n*k transpositions, and describes generation as linear in the size of S. There is no 4^n bound in this discussion.
- The paper contrasts this with the usual computational complexity of classical propositional closure; the bound is about generating transposed rules, not the cost of computing argumentation extensions.
- Query-based argumentation can answer whether a formula follows from some or every extension without computing every extension or generating every argument. Source for these observations: [p. 24](pngs/page-023.png).

### Key Properties of Cl_pp (Property 3)
1. S is a subset of Cl_pp(S)
2. If S_1 is a subset of S_2 then Cl_pp(S_1) is a subset of Cl_pp(S_2)
3. Cl_pp(Cl_pp(S)) = Cl_pp(S) (idempotent)

### Key Properties of Cl_tp
- S is closed under transposition iff Cl_tp(S) = S
- Properties analogous to Cl_pp (subset, monotone, idempotent)

## Problematic Examples

### Example 4 ("Married John")
S = {-> wr; -> go; b -> ¬hw; m -> hw} and D = {wr => m; go => b}.
Here wr means John wears something that looks like a wedding ring, m means John is married, hw means John has a wife, go means John often goes out until late with his friends, and b means John is a bachelor.

The arguments are A_1 = [-> wr], A_2 = [-> go], A_3 = [A_1 => m], A_4 = [A_2 => b], A_5 = [A_3 -> hw], A_6 = [A_4 -> ¬hw]. A_5 and A_6 defeat each other; A_1 through A_4 are undefeated. The grounded extension is {A_1,A_2,A_3,A_4}, so both m and b are justified.

The strict closure of Output = {wr, go, m, b} adds hw and ¬hw. This violates closure and indirect consistency while Output itself remains directly consistent. Source: [p. 11](pngs/page-010.png). After closing strict rules, A_7 = [A_5 -> ¬b] and A_8 = [A_6 -> ¬m] attack A_4 and A_3 respectively; grounded Output then contains only wr and go ([pp. 17–18](pngs/page-016.png)).

### Example 5
S = {-> a; -> d; -> c; b,e -> ¬c} and D = {a => b; d => e}.
Under the Prakken–Sartor formalism discussed here, A = [[-> a] => b], B = [[-> d] => e] and C = [-> c] have no defeaters, so b, e and c are justified. Although b,e -> ¬c is strict, ¬c is not justified; closing the justified conclusions therefore produces inconsistency. This shows that their treatment of Example 4 does not settle the general problem. Source: [p. 12](pngs/page-011.png).

### Example 6 (Garcia & Simari)
S = {-> a; -> d; -> g; b,c,e,f -> ¬g} and D = {a => b; b => c; d => e; e => f}.
Garcia–Simari's disagreement notion can handle Examples 4 and 5 but misses this collective conflict. A = [[-> a] => b], B = [[-> d] => e], C = [A => c] and D = [B => f] have no defeaters. Hence b,c,e,f, together with the facts a,d,g, are justified; their strict closure also derives ¬g and is inconsistent. Source: [p. 12](pngs/page-011.png).

### Example 7 (Why transposition still needs restricted rebutting)
S = {-> a; -> b; -> c; -> g; d,e,f -> ¬g} and D = {a => d; b => e; c => f}. With Cl_tp(S), the three arguments concluding d,e,f acquire counterarguments, so those conclusions leave grounded Output. Under unrestricted rebutting, however, the three arguments defend themselves collectively and occur together in a preferred extension whose strict closure is inconsistent. Restricted rebutting removes their reverse attacks on the strictly topped counterarguments, so that set is no longer admissible. Sources: [p. 21](pngs/page-020.png), [p. 22](pngs/page-021.png).

## Figures of Interest
- **Table 1 (page 15):** Effects of violated postulates - direct consistency violation leads to absurdities; indirect consistency violation leads to users not being allowed to apply modus ponens using strict rules; closure violation leads to conclusions that should come but appear to be missing
- **Table 2 (page 22):** Summary of which postulate combinations are satisfied under which rebutting type and closure operator
- **Fig. 1 (page 40):** Graphical representation of the proof of Theorem 4

## Results Summary

| Rebutting Type | Direct Consistency | Indirect Consistency | Closure |
|---|---|---|---|
| Standard Rebut + either closure operator | Complete, grounded, preferred | Grounded only | Grounded only |
| Restricted Rebut + either closure operator | Complete, grounded, preferred | Complete, grounded, preferred | Complete, grounded, preferred |

This is Table 2's distinction between rebutting types with the two closure operators, assuming the chosen closed strict-rule set is consistent. Both operators work with restricted rebutting; transposition is the weaker rule closure and avoids unwanted classical explosion rules. Source: [p. 22, Table 2](pngs/page-021.png). The discussion extends the transposition/restricted-rebut result to semantics selecting a nonempty family of complete extensions, including ideal and semi-stable semantics ([p. 23](pngs/page-022.png)).

## Key Theorems

### Theorem 1
Let (Arg, Defeat) be an argumentation system built from the defeasible theory (Cl_pp(S), D) such that Cl_pp(S) is consistent. Output is its set of justified conclusions and E its grounded extension. Then, (Arg, Defeat) satisfies closure and indirect consistency.

### Theorem 2
Let (Arg, Defeat_r) be built from (Cl_pp(S), D), with Cl_pp(S) consistent, and E_1,...,E_n its extensions under one of Dung's standard semantics. It satisfies direct and indirect consistency. Closure follows separately from Proposition 8. Source: [p. 19](pngs/page-018.png).

### Theorem 3
Let (Arg, Defeat), using unrestricted rebutting, be built from (Cl_tp(S), D), with Cl_tp(S) consistent, and E its grounded extension. It satisfies closure and indirect consistency. Direct consistency follows from Property 2. Source: [p. 21](pngs/page-020.png).

### Theorem 4
Let (Arg, Defeat_r) be an argumentation system built from the theory (Cl_tp(S), D) with Cl_tp(S) consistent. Output is its set of justified conclusions and E_1,...,E_n its extensions under one of Dung's standard semantics. (Arg, Defeat_r) satisfies direct consistency and indirect consistency.

Closure follows from Proposition 8. Source: [p. 22](pngs/page-021.png).

## Limitations
- Either closure operator with unrestricted rebutting guarantees closure and indirect consistency only for grounded semantics; restricted rebutting supplies the stronger complete/preferred results.
- Full propositional closure may introduce unnecessary rules and explosion-based attacks on unrelated conclusions; transposition is proposed as a weaker alternative ([p. 20](pngs/page-019.png)).
- Arguments are built over literals with strict and defeasible rules; this paper does not supply a first-order implementation or complexity theorem for full extension computation.
- Argument strength is explicitly omitted for simplicity ([p. 4](pngs/page-003.png)); footnote 1 points to [6] for a preferences-based extension ([p. 8](pngs/page-007.png)).
- The formal treatment requires at least one extension and explicitly excludes stable semantics ([p. 9](pngs/page-008.png)).
- Consistency of the chosen closed strict-rule set is a hypothesis, not something either repair can guarantee for arbitrary input. Empty-antecedent strict rules are permitted and serve as facts in the examples.

## Testable Properties
- Indirect consistency implies direct consistency (Proposition 6); closure plus direct consistency implies indirect consistency (Proposition 7), [p. 15](pngs/page-014.png).
- If the strict rules are closed under transposition, then Cl_tp(S) = S
- Cl_pp is idempotent: Cl_pp(Cl_pp(S)) = Cl_pp(S)
- Under restricted rebutting + Cl_tp: if A restrictively rebuts B, then A rebuts B (but not vice versa)
- Every extension is closed under subarguments: A in E implies Sub(A) is a subset of E (Proposition 1), [p. 8](pngs/page-007.png).
- Every complete extension is admissible and conflict-free (Definition 3).
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
- [[Dung_1995_AcceptabilityArguments]] — reference [28], the abstract argumentation framework used for the instantiated systems. The formal results here use complete, grounded and preferred extensions; the postulates themselves are more broadly applicable. Source: [p. 27, bibliography](pngs/page-026.png).
- [[Caminada_2006_IssueReinstatementArgumentation]] — reference [23]. The discussion contrasts postulates about conclusions with postulates characterizing argument-based semantics; the postulates here are stated directly on extension conclusions and Output, rather than defined via reinstatement labellings. Sources: [p. 25](pngs/page-024.png), [p. 27](pngs/page-026.png).
- Pollock is cited through *How to reason defeasibly* (1992), [39], and *Cognitive Carpentry* (1995), [40], rather than the collection's [[Pollock_1987_DefeasibleReasoning]]. The 1987 paper is a conceptual connection, not an identified citation here. Source: [p. 28](pngs/page-027.png).
- Reference [25] is Cayrol and Lagasquie-Schiex's *Graduality in argumentation* (2005), not [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]]. The bipolar paper is therefore only a conceptual cross-reference. Source: [p. 27](pngs/page-026.png).

### New Leads (Not Yet in Collection)
- Prakken & Sartor (1997) [42] — "Argument-based extended logic programming with defeasible priorities" — the system considered in Example 5
- Garcia & Simari (2004) [33] — "Defeasible logic programming: an argumentative approach" — DeLP; the formalism considered in Example 6
- Amgoud et al. (2004) [4] — ASPIC Deliverable D2.2; the original ASPIC framework that this paper evaluates and finds deficient; precursor to ASPIC+

Bibliographic identities are visible on [p. 25](pngs/page-024.png) and [p. 28](pngs/page-027.png).

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
- [13] P. Baroni and M. Giacomin. SCC-recursiveness: a general schema for argumentation semantics. Artificial Intelligence 168(1–2):165–210, 2005.
- [14] T. J. M. Bench-Capon. Persuasion in practical argument using value-based argumentation frameworks. Journal of Logic and Computation 13(3):429–448, 2003.
- [16] P. Besnard and A. Hunter. A logic-based theory of deductive arguments. Artificial Intelligence 128(1–2):203–235, 2001.
- [24] M. Caminada. Semi-stable semantics. COMMA 2006, pp. 121–130.
- [27] K. Clark. Negation as failure. Logic and data bases, pp. 293–322, 1978.
- [30] G. T. F. and N. Karacapilidis. The zeno argumentation framework. ICAIL 1997, pp. 10–18. (The author initials here follow the local paper's bibliography.)
- [42] H. Prakken and G. Sartor. Argument-based extended logic programming with defeasible priorities. (Predecessor system shown to have issues)
- [43] H. Prakken and G. A. W. Vreeswijk. Logics for defeasible argumentation. Handbook of Philosophical Logic, vol. 4, pp. 219–318, 2002.

Sources: bibliography [p. 26](pngs/page-025.png), [p. 27](pngs/page-026.png), [p. 28](pngs/page-027.png).
