# Abstract

## Original Text (Verbatim)

Reasoning with defaulting and conflicting knowledge in argumentation is a key research field in computational argumentation. Reasoning under forms of uncertainty in argumentation is computationally hard. In this paper we consider a form of probabilistic argumentation framework, where arguments and attacks are associated with probabilities, and investigate algorithmic approaches under the so-called constellation approach. In this approach, each subset of arguments and attacks gives rise to a possible argumentation framework. It is known that computing the probability of a given set being an extension and that of computing the probability of acceptability of an argument are #P-complete and #P^NP-complete tasks (the latter for the so-called complete semantics). We first show existing complexity results stating that computing extension probability and computing acceptability share the same complexity. We show new counting complexity classes, that their underlying counting problems differ in their complexity; the former problem is #P-complete for complete semantics, and the latter is #P^NP-complete, indicating a jump in the counting complexity hierarchy. Next we look into algorithms to solve these tasks. We give algorithms for computing probability using tree-decompositions. We experimentally evaluate promise of our approach.

---

## Our Interpretation

This paper addresses exact computation of extension and acceptability probabilities in probabilistic argumentation frameworks (PrAFs) under the constellation approach, where each subset of arguments/attacks is a possible AF. The key contribution is a dynamic programming algorithm over nice tree-decompositions that is fixed-parameter tractable w.r.t. treewidth, enabling exact computation for structurally sparse PAFs. This is directly relevant to propstore's probabilistic argumentation layer as a potential exact-mode alternative to the existing Monte Carlo sampling approach.
