# Abstract

## Original Text (Verbatim)

In this paper, we extend Dung's seminal argument framework to form a probabilistic argument framework for associating probabilities with arguments and defeats. We then compute the likelihood of some set of arguments appearing within an extension of such a framework according to a given Dung semantics from this work. We show that the complexity of computing this likelihood precisely is exponential in the number of arguments and defeats, and then describe an approximate approach to computing these likelihoods based on Monte Carlo simulation. Evaluating the latter approach against the exact approach shows significant computational gains in favour of the approximate approach. Based on a number of real world problems, we show its utility by applying it to the problem of coalition formation.

---

## Our Interpretation

The paper formalizes how to attach existence probabilities to arguments and attack relations in Dung-style argumentation, then compute the probability that a query set of arguments is accepted under any Dung semantics by marginalizing over all possible sub-frameworks. Since exact computation is exponential, they provide a Monte Carlo sampling algorithm with Agresti-Coull convergence bounds that scales linearly per iteration. This is directly relevant to propstore's need for probabilistic uncertainty in its argumentation layer — each sampled sub-framework corresponds to an ATMS context/environment.
