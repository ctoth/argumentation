---
tags: [probabilistic-argumentation, dung-af, monte-carlo, uncertainty]
---
Extends Dung's abstract argumentation frameworks with independent probabilities on argument and defeat existence, defining Probabilistic Argumentation Frameworks (PrAFs). Acceptance probability is computed by marginalizing over all possible sub-frameworks (the constellations approach), with an exact exponential method and a practical Monte Carlo approximation using Agresti-Coull convergence bounds. Directly applicable to propstore's need for probabilistic uncertainty over ATMS environments — each inducible sub-framework maps to a weighted context.
