---
title: "AGM Meets Abstract Argumentation: Expansion and Revision for Dung Frameworks"
authors: "Ringo Baumann, Gerhard Brewka"
year: 2015
venue: "IJCAI-15"
doi_url: "https://www.ijcai.org/Abstract/15/387"
produced_by:
  agent: "claude-opus-4-6"
  skill: "paper-reader"
  timestamp: "2026-03-29T03:02:27Z"
---
# AGM Meets Abstract Argumentation: Expansion and Revision for Dung Frameworks

## One-Sentence Summary

Defines four monotonic Dung logics through kernel-based AF models, constructs expansion via intersection of model sets, and gives a concrete syntactic stable-kernel revision satisfying all eight adapted AGM axioms. *(pp.2735-2739)*

## Problem Addressed

Ordinary equality of extension sets does not ensure that AFs remain interchangeable when combined with additional information. The paper uses semantics-specific kernels to make ordinary equivalence in a new monotonic logic coincide with strong equivalence of AFs. This supplies consequence and consistency notions for AGM-style change without assuming that every selected set of AF models is realizable. *([p.2736 image](pngs/page-002.png), [p.2737 image](pngs/page-003.png))*

## Key Contributions

- Four Dung logics, indexed by stable, admissible, grounded, and complete kernels.
- A characterization of model-set realizability using closure under kernel inclusion and the existence of a least kernel.
- Expansion whose models are exactly the intersection of the original model sets.
- An explicit stable-kernel revision operator selecting the unique inclusion-maximal compatible part of the old kernel together with the new kernel.
- Selection-based operators for other kernels satisfying R1-R6; sufficient conditions for R7-R8 remain future work.
- A concrete counterexample showing that a Satoh-style semantic distance construction can select a model set that no AF realizes. *([pp.2736-2739 images](pngs/page-002.png), [expansion](pngs/page-003.png), [revision construction](pngs/page-004.png), [revision theorem](pngs/page-005.png))*

## Frameworks and Kernels

An AF is \(F=(A,R)\), with \(A\) a finite subset of a fixed infinite background universe and \(R\subseteq A\times A\). Framework inclusion, union, and symmetric difference are componentwise.

A kernel \(k\) preserves the arguments and deletes selected redundant attacks. An AF is **\(k\)-r-free** iff \(F=F^k\). Definition 2 supplies four kernels, each retaining self-loops:

| Kernel | Delete a non-self attack \((a,b)\) exactly when |
|--------|----------------------------------------------|
| \(k(stb)\) | \((a,a)\in R\) |
| \(k(ad)\) | \((a,a)\in R\) and \(\{(b,a),(b,b)\}\cap R\ne\emptyset\) |
| \(k(gr)\) | \((b,b)\in R\) and \(\{(a,a),(b,a)\}\cap R\ne\emptyset\) |
| \(k(co)\) | \((a,a),(b,b)\in R\) |

Theorem 1 relates kernel equality to strong equivalence: use the corresponding kernel for stable, admissible, complete, and grounded semantics; the admissible kernel also characterizes preferred, ideal, semi-stable, and eager strong equivalence; the stable kernel also serves stage semantics. These are different equivalence relations, not one relation unifying all semantics. The notation is **\(k\)-equivalence**, not “4-equivalence.” *([Definition 2 and Theorem 1, p.2735](pngs/page-001.png))*

## Monotonic Dung Logics

### Models and Satisfiability (Definition 3)

\[
\operatorname{Mod}^k(F)=\{G\in\mathcal A\mid F^k\subseteq G^k\},
\qquad
\operatorname{Mod}^k(\mathcal F)=
\bigcap_{F\in\mathcal F}\operatorname{Mod}^k(F).
\]

The relation is **kernel inclusion**, not equality: a model may carry more information than the formula AF. A set \(\mathcal F\) is \(k\)-satisfiable iff its model set is nonempty and \(k\)-tautological iff its model set is all AFs. Every single ordinary AF is satisfiable because it models itself. The empty AF is tautological. Infinite sets of finite AF formulas can be unsatisfiable, and finite sets can also be inconsistent. The symbol \(\bot\) denotes an unsatisfiable “framework” by convention. *([p.2736 image](pngs/page-002.png))*

### Consequence (Definition 4)

\[
\mathcal F\models^k G
\quad\Longleftrightarrow\quad
\operatorname{Mod}^k(\mathcal F)\subseteq\operatorname{Mod}^k(G),
\qquad
Cn^k(\mathcal F)=\{G\mid\mathcal F\models^k G\}.
\]

Proposition 2 proves inclusion, monotony, and idempotency of \(Cn^k\). Definition 5 calls \(F,G\) \(k\)-equivalent iff each entails the other. Theorem 3 identifies these equivalences with the semantics-specific strong-equivalence relations listed above. The paper explicitly says the consequence relations are **not finitary**, and that these logics possess **neither compactness nor the Craig interpolation property**; extension to infinite AFs needs separate study. *([p.2736 image](pngs/page-002.png), [p.2737 image](pngs/page-003.png))*

### Realizability (Definition 6, Theorem 4)

A set \(\mathcal M\) is \(k\)-realizable when it is the model set of a set of AF formulas. Theorem 4 gives:

1. If \(F\in\mathcal M\) and \(F^k\subseteq G^k\), then \(G\in\mathcal M\).
2. If \(\mathcal M\ne\emptyset\), there is \(F\in\mathcal M\) such that \(F^k\subseteq G^k\) for every \(G\in\mathcal M\).

Thus a nonempty realizable set must be upward closed under kernel inclusion and have a least element up to kernel equivalence. A semantic revision method cannot select an arbitrary collection of nearest models and assume it corresponds to an AF. *([Theorem 4, p.2737](pngs/page-003.png))*

## Belief Expansion

Definition 7 defines \(+\!^k\) by

\[
\operatorname{Mod}^k(F+\!^k G)=
\operatorname{Mod}^k(F)\cap\operatorname{Mod}^k(G).
\]

Theorem 5 proves this intersection has a single-AF representative. If nonempty, the representative is \(k\)-equivalent to \(F^k\cup G^k\); otherwise the result is \(\bot\). Lemma 6 supplies the syntactic satisfiability condition:

\[
\operatorname{Mod}^k(F+\!^k G)\ne\emptyset
\quad\Longleftrightarrow\quad
F^k\cup G^k\text{ is }k\text{-r-free}.
\]

One must not simply kernelize a conflicting union: deleting an old required kernel attack may lose an input formula. Nor does the definition re-add all attacks from self-attacking sources. The result depends on the selected kernel. *([Definition 7, Theorem 5, Lemma 6, p.2737](pngs/page-003.png))*

Theorem 7 establishes five expansion properties:

1. The expansion is an AF.
2. \(F+\!^kG\models^kG\).
3. If \(F\models^kG\), then \(F+\!^kG\equiv^kF\).
4. If \(F\models^kG\), then \(F+\!^kH\models^kG+\!^kH\).
5. Kernel-equivalent inputs yield kernel-equivalent expansions.

The construction generalizes to arbitrary finite intersections. *([p.2737 image](pngs/page-003.png))*

## Belief Revision

### Adapted AGM Postulates (Definition 8)

For AFs \(F,G,H,I\), a \(k\)-revision satisfies all eight axioms:

- **R1:** \(F*_kG\) is an AF.
- **R2:** \(F*_kG\models^kG\).
- **R3:** \(F+\!^kG\models^kF*_kG\).
- **R4:** If \(F+\!^kG\) is satisfiable, then \(F*_kG\models^kF+\!^kG\).
- **R5:** \(F*_kG\) is satisfiable iff \(G\) is satisfiable.
- **R6:** \(F\equiv^kG\) and \(H\equiv^kI\) imply \(F*_kH\equiv^kG*_kI\).
- **R7:** \((F*_kG)+\!^kH\models^kF*_k(G+\!^kH)\).
- **R8:** If \((F*_kG)+\!^kH\) is satisfiable, then \(F*_k(G+\!^kH)\models^k(F*_kG)+\!^kH\).

These are entailment statements between AFs, not membership statements in a classical belief set. *([p.2737 image](pngs/page-003.png))*

### Why the Satoh-Style Construction Can Fail

Definition 9 selects models of the new AF having inclusion-minimal symmetric difference from some model of the old AF. Example 3 shows the selected set need not be realizable: it contains \(F'\), but omits a framework with the same kernel that upward closedness would require. Thus R1 fails. More generally, distance selection can omit required upward extensions or select multiple incomparable minimal kernels. The obstacle is realizability, not merely different argument sets or an unspecified metric. *([p.2738 image](pngs/page-004.png))*

### Concrete Syntactic Revision (Definitions 10-11)

\[
\mathcal M^k_{FG}=
\max_{\subseteq}
\{G^k\cup H\mid H\subseteq F^k,\ 
G^k\cup H\text{ is }k\text{-r-free}\}.
\]

The new kernel is retained; as much of the old kernel as possible is added while preserving kernel redundancy-freedom. Example 4 gives multiple maximal candidates for the admissible, grounded, and complete kernels. Lemma 8 proves the surprising stable-kernel exception:

\[
|\mathcal M^{k(stb)}_{FG}|=1.
\]

Definition 11 defines \(F\circ^{k(stb)}G=I\) where \(\mathcal M^{k(stb)}_{FG}=\{I\}\). **Theorem 9 proves this concrete operator satisfies R1-R8.** This is not a faithful-total-preorder representation theorem. *([p.2738 construction](pngs/page-004.png), [p.2739 operator and theorem](pngs/page-005.png))*

### Other Kernels (Definition 12, Proposition 10)

A \(k\)-selection operator chooses a suitable member of \(\mathcal M^k_{FG}\). Proposition 10 proves R1-R6. R7-R8 require additional properties of the selection function; a subset-compatibility idea is sketched, but sufficient conditions are left for future work. *([p.2739 image](pngs/page-005.png))*

## Figures and Examples

- **Example 1 (p.2736):** Six two-argument AFs illustrate satisfiable and unsatisfiable combinations of AF formulas, and dependence on the selected kernel.
- **Example 2 (p.2737):** Grounded-kernel expansion is satisfiable, while stable/admissible/complete-kernel expansion of the same inputs is unsatisfiable.
- **Example 3 (p.2738):** Satoh-style closest-model selection violates realizability.
- **Example 4 (p.2738):** Multiple admissible/complete/grounded maximal candidates contrast with a unique stable candidate.
- **Example 5 (p.2739):** Concrete revisions in opposite orders illustrate revision's directionality.

The corresponding images are [p.2736](pngs/page-002.png), [p.2737](pngs/page-003.png), [p.2738](pngs/page-004.png), and [p.2739](pngs/page-005.png).

## Limitations and Implementation Consequences

- The concrete fully axiomatized revision result is for the stable kernel; do not claim a single operator works for every semantics.
- Expansion may be inconsistent even though each input AF is individually satisfiable.
- A kernel function must preserve argument sets and self-loops and implement the selected redundancy condition.
- Model testing uses kernel inclusion; kernel equality is reserved for equivalence.
- A distance-based revision implementation needs a realizability argument.
- The paper's consequence operations are not finitary or compact.
- AFs here are finite; infinite-AF behavior is not established by these results.
- Contraction is outside this paper's construction.

## Relationship to Other Work

The related-work section distinguishes AF revision from answer-set-program revision: strong equivalence of AFs need not coincide with strong equivalence under a logic-program translation, and a logic-program result need not be realizable as an AF.

Cayrol et al. study extension change after adding an argument, and Baumann and Brewka (2010) study enforcement; neither supplies the AGM consistency and inference notions introduced here. Coste-Marquis et al. (2014) select formula-compatible extensions close to old extensions and return a set of AFs because of realizability. Their construction changes attacks and does not add arguments. A subsequent propositional-translation approach changes the revising formula's reading from credulous to skeptical acceptance. *([p.2739 image](pngs/page-005.png))*

## Testable Properties

- Kernel equality matches the corresponding semantics' strong equivalence, with the exact family split in Theorem 1.
- \(G\models^kF\) iff \(F^k\subseteq G^k\).
- \(Cn^k\) satisfies inclusion, monotony, and idempotency.
- Expansion models are the intersection of input model sets.
- Expansion is satisfiable iff \(F^k\cup G^k\) is \(k\)-r-free.
- The stable-kernel maximal-candidate set has one element.
- The concrete stable-kernel operator satisfies R1-R8.
- Arbitrary suitable selection operators for the other kernels satisfy R1-R6; R7-R8 are not established without further conditions.

## Relevance to Project and Open Questions

The four kernels provide separate canonical AF representations, while kernel inclusion supplies a monotonic consequence relation for comparing AF information. The stable syntactic revision construction is a concrete reference for AF belief change; a union-and-kernelize helper alone does not implement the paper's expansion when the kernel union is inconsistent.

- [ ] Which kernel and associated equivalence is intended for a consuming application?
- [ ] Does a proposed revision result preserve realizability and the AF entailment form of the axioms?
- [ ] Which selection conditions suffice for R7-R8 under the other kernels?
- [ ] How should structured-argumentation generation interact with change at the abstract AF level?

## Collection Cross-References

- [[Dung_1995_AcceptabilityArguments]] — foundational AF semantics.
- [[Oikarinen_2010_CharacterizingStrongEquivalenceArgumentation]] — semantics-specific strong-equivalence kernels.
- [[Cayrol_2014_ChangeAbstractArgumentationFrameworks]] — adding-argument dynamics discussed in related work.
- [[Coste-Marquis_2007_MergingDung'sArgumentationSystems]] — distance-based merging is a related change problem, not this paper's revision construction.
- [[Diller_2015_ExtensionBasedBeliefRevision]] — extension-based revision is a separate approach.
- [[Baumann_2019_AGMContractionDung]] — later contraction work; its contents require separate verification.
