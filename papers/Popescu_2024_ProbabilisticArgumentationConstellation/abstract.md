# Abstract

## Original Text (Verbatim)

Reasoning with defeasible and conflicting knowledge is an argumentation form a key research field in computational argumentation. Recently many works have focused on incorporating both a key feature and a challenging barrier for automated argumentation reasoning: It was shown that real argumentation settings often come with varying degrees of probability and structural complexity. In particular for the so-called constellation approach. In this paper, we develop an algorithmic approach to these combined challenges. On the theoretical side, we present new complexity results and show that two main reasoning tasks, that of computing the probability of a set of arguments being an extension and that of computing acceptability of an argument, while the former is #P-complete and the latter is #·NP-complete when counted. On the algorithmic side, we devise dynamic programming algorithms using tree-decompositions, an algorithm for the complex task of computing the probability of a set of arguments being an extension. To bridge theory and algorithms, we develop a dynamic programming. Our experimental evaluation shows promise of our approach.

---

## Our Interpretation

The paper addresses the challenge of exact probability computation in Probabilistic Argumentation Frameworks (PAFs) under the constellation approach, where arguments and attacks exist with independent probabilities. The key finding is a complexity separation: counting subframeworks for set-extension is #·P-complete while argument acceptability counting is #·NP-complete, and tree-decomposition DP makes exact computation tractable for bounded-treewidth instances. This is directly relevant to propstore's PrAF layer, providing the implementation blueprint for exact probabilistic reasoning when argumentation graphs have exploitable structure.
