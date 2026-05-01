---
tags: [probabilistic-argumentation, tree-decomposition, complexity, exact-algorithms, constellation-approach]
---
Presents exact dynamic-programming algorithms for computing extension and acceptability probabilities in probabilistic argumentation frameworks (PrAFs) under the constellation approach, parameterized by treewidth. Establishes that extension probability is #P-complete while acceptability is #P^NP-complete for complete semantics, and provides FPT algorithms via nice tree-decompositions that outperform brute-force for low-treewidth instances. Directly relevant to propstore's PrAF implementation as a potential exact-mode solver alongside the existing Monte Carlo sampling approach.
