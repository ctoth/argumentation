---
title: "Computing ideal sceptical argumentation"
authors: "Phan Minh Dung, Paolo Mancarella, Francesca Toni"
year: 2007
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/j.artint.2007.05.003"
pages: "642-674"
produced_by:
  agent: "gpt-5-codex"
  skill: "paper-reader"
  timestamp: "2026-03-28T08:12:11Z"
---
# Computing ideal sceptical argumentation

## One-Sentence Summary

Defines proof procedures for computing the sceptical ideal semantics in both Dung-style abstract argumentation and flat assumption-based argumentation, proving soundness in general and completeness for natural p-acyclic ABA frameworks with finite languages. *(pp.642, 661--662)*

## Problem Addressed

Grounded semantics is easy to compute but can be too sceptical, while preferred semantics is more informative but credulous and harder to compute sceptically. The paper targets the middle ground: ideal semantics, which is less sceptical than grounded semantics but still sceptical relative to preferred semantics, and it asks for concrete dialectical procedures that compute it rather than merely defining it extension-theoretically. *(pp.642--643, 645)*

## Key Contributions

- Proves that every abstract argumentation framework has a unique maximal ideal set, that it is complete, and that it lies between the grounded set and the intersection of all preferred sets. *(p.645)*
- Introduces **ideal dispute trees** for abstract argumentation and proves them sound and complete for computing ideal sets. *(pp.650--651, 661)*
- Recasts assumption-based argumentation in terms of sets of assumptions so that admissible, preferred, grounded, and ideal semantics on arguments can be computed via dialectical procedures on assumptions. *(pp.646--648)*
- Defines **GB-dispute**, **AB-dispute**, **IB-dispute**, and **Fail-dispute** derivations, progressively refining older admissibility procedures into procedures for grounded and ideal beliefs. *(pp.652--660)*
- Proves AB-dispute derivations sound for admissibility in general and complete for p-acyclic, finite-language frameworks; proves IB-dispute plus Fail-dispute derivations sound in general and complete for ideal beliefs under the same restriction. *(pp.656--660)*

## Study Design

Pure theory paper; no empirical study. The method is formal definition plus soundness/completeness proof. *(throughout)*

## Methodology

The paper first revisits abstract argumentation and flat assumption-based argumentation, then defines ideal semantics for each setting and characterizes them structurally. It next develops dialectical proof objects: dispute trees for abstract argumentation and derivation tuples for ABA. The proofs then establish the correspondence between these proof objects and ideal semantics, with extra filtering machinery added when plain admissibility procedures are insufficient for sceptical reasoning. *(pp.643--660)*

## Key Equations / Formal Definitions

$$
AF = \langle Arg, attacks \rangle
$$

Where: `Arg` is a finite set of abstract arguments and `attacks` is a binary relation on `Arg`; \(x\) attacks \(y\) iff \((x,y)\in attacks\). *(p.643)*

$$
X \text{ is ideal } \iff X \text{ is admissible and } X \subseteq Y \text{ for every preferred set } Y
$$

Where: the paper studies ideal sets alongside admissible, preferred, complete, and grounded sets; the ideal set is sceptical because it must survive containment in every preferred set. *(p.644)*

$$
ABF = \langle \mathcal{L}, \mathcal{R}, \mathcal{A}, \overline{\phantom{x}} \rangle
$$

Where: \(\mathcal{L}\) is a formal language, \(\mathcal{R}\) is a set of inference rules, \(\mathcal{A}\subseteq\mathcal{L}\) is a set of candidate assumptions, and \(\bar{\alpha}\) is the contrary of assumption \(\alpha\); the paper restricts to flat ABA frameworks where assumptions do not occur as rule conclusions. *(pp.645--646)*

$$
A \text{ attacks } B \iff \exists A' \vdash \alpha \text{ such that } A' \subseteq A \text{ and } \alpha = \bar{\beta} \text{ for some } \beta \in B
$$

Where: attack between sets of assumptions is induced by an argument based on assumptions \(A'\) deriving the contrary of an assumption in \(B\). This lets the paper compute semantics on assumption sets rather than explicit argument objects. *(p.647)*

$$
S \text{ is ideal } \iff \forall a \text{ attacking } S,\ \nexists X \text{ admissible with } a \in X
$$

Where: Theorem 3.3 gives the key characterization behind ideal dispute trees: an admissible set is ideal exactly when every attacker fails to belong to any admissible set. *(p.650)*

## Parameters

The paper has no empirical or statistical parameters. Its operational control parameters are structural proof-state components:

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| GB-dispute tuple arity | - | - | 4 | - | 653 | GB derivations use \((P_i, O_i, A_i, C_i)\): proponent frontier, opponent frontier, defence assumptions, culprits. |
| AB-dispute tuple arity | - | - | 4 | - | 655 | AB derivations keep the same four components but strengthen filtering conditions. |
| IB-dispute tuple arity | - | - | 5 | - | 658 | IB derivations add \(F_i\), a set of potential attacks that must later be checked via `Fail`. |
| Completeness condition | p-acyclic | - | required | acyclic dependency graph | 656--657, 659--660 | AB and IB completeness require a p-acyclic ABA framework with finite underlying language. |
| Admissible-tree finiteness condition | - | - | sufficient | no infinitely long branches | 650 | Theorem 3.1 gives a sufficient condition for admissibility of a dispute tree. |

## Effect Sizes / Key Quantitative Results

Not applicable. This is a formal semantics and proof-procedure paper, not an empirical evaluation. *(throughout)*

## Methods & Implementation Details

- **Dispute trees for abstract AFs.** A dispute tree for initial argument \(a\) alternates proponent and opponent nodes, with the root as a proponent node labelled \(a\); every opponent attack must be countered by a unique proponent child, while every proponent node must branch to all attackers. The defence of the tree is the set of all proponent-labelled arguments. *(pp.648--649)*
- **Admissible dispute trees.** A dispute tree is admissible iff no argument labels both a proponent and an opponent node. Trees with no infinitely long branches are automatically admissible, and the defence of an admissible dispute tree is an admissible set. *(p.650)*
- **Ideal dispute trees.** An admissible dispute tree is ideal iff no opponent node in the tree has any admissible dispute tree rooted at that node. The defence of an ideal dispute tree is ideal, and conversely every argument in an ideal set has such a tree. *(pp.650--651)*
- **Backward deductions in ABA.** A backward deduction of conclusion \(\alpha\) from premises \(P\) is a sequence of frontier multisets \(S_1,\ldots,S_m\) controlled by a selection function \(f\), expanding either by replacing a selected non-assumption with rule premises or by deleting a selected premise assumption. The paper requires that once a sentence occurrence is selected from a multiset, it cannot be selected again later in the same sequence. *(p.646)*
- **Assumption-level semantics.** Because ABA attacks depend only on assumptions, the paper defines admissible, preferred, complete, grounded, and ideal sets directly on sets of assumptions, then links them back to the corresponding argument semantics by Theorem 2.2. *(pp.647--648)*
- **GB-dispute derivations for grounded beliefs.** GB derivations use culprit sets \(C_i\) to filter potential defence arguments and defence-assumption sets \(A_i\) to filter potential culprits, ensuring the constructed support does not attack itself. They compute grounded beliefs soundly but remain incomplete for admissibility. *(pp.652--654)*
- **AB-dispute derivations for admissible beliefs.** AB derivations strengthen GB derivations with extra filtering: defences filter defences, culprits filter culprits, and some opponent assumptions are marked or ignored to avoid redundant counter-attack. Theorem 4.3 gives soundness; Theorem 4.4 gives completeness for p-acyclic, finite-language frameworks. *(pp.654--657)*
- **p-acyclic restriction.** The paper defines \(ABF^+\) by dropping all assumptions from rule premises and then defines a dependency graph over the remaining atoms. A framework is p-acyclic when this graph is acyclic; the property rules out infinite partial deductions and underwrites completeness. *(pp.656--657)*
- **IB-dispute derivations for ideal beliefs.** IB derivations extend AB derivations by adding a fifth component \(F_i\) of potential attacks that still need sceptical checking. Opponent sentences may be marked so they are not reselected until needed for `Fail`, which separates defence construction from sceptical attack elimination. *(pp.657--659)*
- **Fail-dispute derivations.** `Fail` for a multiset \(S\) means that no admissible set of assumptions supports \(S\). Fail-dispute derivations operationalize this check; they are sound in general and complete under p-acyclicity with finite language, giving the missing negative test required for ideal semantics. *(pp.659--660)*

## Figures of Interest

- **Fig. 1 (p.649):** A dispute tree labelled by \(e\); the defence set is \(\{e,c,d\}\), showing the tree shape for admissibility reasoning.
- **Fig. 2 (p.649):** A dispute tree labelled by \(f\); the defence set is \(\{f,d\}\), contrasting with the non-admissible tree of Fig. 1.
- **Fig. 3 (p.651):** An ideal dispute tree for \(b\) consisting of proponent \(b\) and opponent \(a\); the example witnesses an ideal set directly.

## Results Summary

For abstract argumentation, the paper proves that the ideal set is unique, complete, contains the grounded set, and is contained in the intersection of all preferred sets; if the intersection of all preferred sets is itself admissible, then it already is the maximal ideal set. *(p.645)* Theorem 3.3 gives the crucial admissibility-plus-no-admissible-attacker characterization of ideality, and Theorem 3.4 turns that characterization into a sound and complete ideal-dispute-tree proof procedure. *(pp.650--651)* For ABA, GB derivations compute grounded beliefs soundly but may miss admissible supports, AB derivations repair this for admissibility, and IB + Fail derivations compute ideal beliefs soundly in general and completely in p-acyclic finite frameworks. *(pp.653--660)*

## Limitations

- The ABA procedures are defined only for **flat** assumption-based argumentation frameworks. *(p.646)*
- AB- and IB-based completeness results require **p-acyclicity** and a **finite underlying language**; outside that class the procedures are only proved sound. *(pp.656--660)*
- Admissible and ideal dispute trees can be **infinite**, so the tree notions themselves are not directly constructive until the derivation machinery is introduced. *(pp.650--651)*
- The paper explicitly leaves a **full computational complexity analysis** of ideal semantics for future work. *(p.662)*

## Arguments Against Prior Work

- **Grounded semantics is too sceptical for many applications.** The paper argues that grounded semantics often computes only the stable arguments in coherent abstract and normal-logic settings, so it can be overly conservative when a stronger sceptical semantics is available. *(pp.642--643)*
- **Sceptically preferred procedures are too narrow.** The TPI-style sceptically preferred procedure computes under coherent abstract frameworks and p-acyclic ABA frameworks only; the paper positions ideal semantics as a better target because it remains sceptical but avoids the same restriction to preferred semantics. *(p.643, p.660)*
- **Older grounded procedures are not dialectically clean enough.** The Kakas-Toni procedure for grounded semantics is described as less clear in its dialogic nature than the new dispute-derivation procedures. *(p.661)*
- **Vreeswijk's admissibility tool does not answer sceptical support.** Vreeswijk's algorithm can compute relevant parts of grounded/admissible defence sets, but it does not determine whether a belief is sceptically supported unless that belief is in the grounded extension. *(p.661)*

## Design Rationale

- **Target the middle semantics.** The ideal semantics is chosen because it is less sceptical than grounded semantics and less credulous than preferred semantics, giving a conservative but not vacuous sceptical reading. *(pp.642--645)*
- **Exploit existing admissibility machinery rather than discard it.** The paper deliberately adapts earlier admissible proof procedures instead of replacing them wholesale, adding exactly the extra machinery needed for sceptical ideal reasoning. *(pp.642, 652, 654, 657)*
- **Operate on assumptions, not explicit arguments, in ABA.** Since attacks depend only on assumptions, the procedures manipulate potential arguments and assumption sets instead of constructing every full argument before any attack checking. This is the key efficiency and tractability move. *(pp.646--647, 651)*
- **Use culprit and defence-assumption filters to preserve admissibility.** The procedural state explicitly tracks assumptions already used for defence and currently culpable assumptions, preventing redundant counter-attacks and self-defeating supports. *(pp.652--656)*
- **Separate positive support from negative admissibility checks.** IB derivations store unresolved potential attacks in \(F_i\), and Fail-dispute derivations check them only when needed; this isolates the sceptical "no admissible attacker exists" condition required by ideal semantics. *(pp.657--660)*

## Testable Properties

- Every abstract argumentation framework admits a **unique maximal ideal set**. *(p.645)*
- The maximal ideal set is **complete**. *(p.645)*
- The maximal ideal set is a **superset of the grounded set** and a **subset of the intersection of all preferred sets**. *(p.645)*
- If the intersection of all preferred sets is admissible, it **coincides with the maximal ideal set**. *(p.645)*
- A dispute tree with **no infinitely long branches** is admissible. *(p.650)*
- The defence set of an admissible dispute tree is **admissible**, and every argument in an admissible set has an admissible dispute tree. *(p.650)*
- An admissible set \(S\) is ideal iff every attacker of \(S\) belongs to **no admissible set**. *(p.650)*
- The defence set of an ideal dispute tree is **ideal**, and every argument in an ideal set has an ideal dispute tree. *(p.650)*
- For ABA, if \(A\) is the defence set of any AB-dispute derivation for \(\alpha\), then \(A\) is admissible and some subset of \(A\) supports an argument for \(\alpha\). *(p.656)*
- In p-acyclic ABA frameworks with finite language, \(\alpha\) is an admissible belief iff there exists an AB-dispute derivation for \(\alpha\). *(p.657)*
- If there exists an IB-dispute derivation for \(\alpha\), then \(\alpha\) is an ideal belief. *(p.659)*
- In p-acyclic ABA frameworks with finite language, \(\alpha\) is an ideal belief iff there exists an IB-dispute derivation for \(\alpha\). *(p.659)*
- If there exists a Fail-dispute derivation for a multiset \(S\), then `Fail(S)` holds; under p-acyclicity and finite language, the converse holds too. *(pp.659--660)*

## Relevance to Project

This paper is directly relevant to propstore's sceptical conflict-resolution layer. It gives a proof-theoretic way to compute a conservative acceptance status that is stronger than grounded semantics but still protected against one-off credulous choices, which is exactly the kind of render-time stance discipline a claim store needs when contradictory arguments remain live. The ABA procedures are especially useful because they work over assumptions and contraries rather than demanding full eager materialization of every argument object, aligning with the repo's interest in assumption-tracking, dispute-state filtering, and proof-carrying justification. *(pp.646--660)*

## Open Questions

- [ ] Can the p-acyclicity restriction be weakened without losing completeness? *(pp.656--660)*
- [ ] What is the precise computational complexity of ideal semantics and its proof procedures? *(p.662)*
- [ ] How should these ideal-semantics procedures relate to later structured systems such as ASPIC+ and modern SAT/ASP solvers for ideal extensions? *(pp.660--662)*

## Related Work Worth Reading

- Dung, Kowalski, Toni (2006), *Dialectic proof procedures for assumption-based, admissible argumentation* — the direct procedural predecessor this paper adapts and strengthens. *(pp.642, 652, 654, 657)*
- Dung (1995), *On the acceptability of arguments and its fundamental role in non-monotonic reasoning, logic programming, and n-person games* — foundational abstract argumentation semantics underlying the whole paper. *(pp.643--645)*
- Vreeswijk (2000), *Preferred, grounded and ideal semantics in argument systems* — earlier algorithmic treatment of ideal semantics used for comparison. *(p.661)*
- Kakas and Toni (1999), *Computing argumentation in logic programming* — earlier grounded-semantics proof procedure that this paper critiques and extends. *(p.661)*

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — cited as [7]; the abstract foundation whose preferred, complete, grounded, and ideal semantics are refined into explicit proof procedures here.
- [[Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault]] — cited as [3]; one of the assumption-based argumentation foundations that this paper builds on for its ABA results.
- [[Pollock_1987_DefeasibleReasoning]] — cited as [18]; part of the defeasible-reasoning background that frames the dialogue/proof-procedure perspective.

### New Leads (Not Yet in Collection)
- Dung, Kowalski, and Toni (2006) — "Dialectic proof procedures for assumption-based, admissible argumentation" — direct procedural predecessor adapted here.
- Vreeswijk (2000) — "Preferred, grounded and ideal semantics in argument systems" — earlier algorithmic treatment of ideal semantics compared in the conclusion.
- Kakas and Toni (1999) — "Computing argumentation in logic programming" — earlier grounded-semantics proof procedure this paper critiques and extends.

### Cited By (in Collection)
- [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]] — cites it as the ideal-semantics comparison point for ranking semantics.
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — cites it as the paper defining ideal semantics for conservative rendering modes.
- [[Caminada_2006_IssueReinstatementArgumentation]] — cites it in the context of extension-semantics relationships around grounded and ideal reasoning.

### Conceptual Links (not citation-based)
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — Moderate. Baroni's principles explain what skeptical semantics should satisfy; this paper gives concrete procedures for one of those skeptical semantics, namely ideal semantics.
- [[Caminada_2006_IssueReinstatementArgumentation]] — Moderate. Caminada recasts classical semantics via labellings, while this paper supplies proof procedures for the ideal semantics that sits between grounded and preferred.
- [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]] — Moderate. Ranking semantics addresses the same dissatisfaction with grounded semantics' coarseness, but by gradual ordering rather than ideal-set proof procedures.
- [[Modgil_2011_RevisitingPreferencesArgumentation]] — Moderate. Both papers seek conservative justification procedures beyond plain grounded semantics, but Modgil does so through structured preference-sensitive defeat rather than ideal dispute trees.
