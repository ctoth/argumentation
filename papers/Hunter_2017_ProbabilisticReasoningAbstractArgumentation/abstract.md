# Abstract

## Original Text (Verbatim)

Abstract argumentation offers an appealing way of representing and evaluating arguments and counterarguments. This approach can be enhanced by considering probability assignments on arguments, allowing for a quantitative treatment of formal argumentation. In this paper, we regard the assignment as denoting the degree of belief that an agent has in an argument being acceptable. While there are various interpretations of this, an important one that we pursue here involves the probability that a particular audience will find an agent has in an argument being acceptable is a combination of the degree to which it believes the premises, the claim, and the derivation of the claim from the premises. We consider constraints on these probability assignments, inspired by crisp notions from classical abstract argumentation frameworks and discuss the issue of probabilistic reasoning with abstract argumentation frameworks. Moreover, we consider the scenario when assessments on the probability of a subset of the arguments are given and the probabilities of the remaining arguments have to be derived, taking both the topology of the argumentation framework and principles of probabilistic reasoning into account. We provide inconsistency measures that allow quantifying the amount of conflict of these assessments and provide a method for inconsistency-tolerant reasoning.

---

## Our Interpretation

This paper defines the epistemic approach to probabilistic argumentation, where P(A) represents degree of belief that argument A is acceptable, constrained by the attack graph topology via rationality postulates (COH, FOU, RAT, etc.). The key practical contribution is a framework for propagating partial probability assessments to unassigned arguments via maximum entropy, plus consolidation operators for handling contradictory assessments — directly relevant to replacing bare floats with principled probabilistic reasoning in propstore's argumentation layer.
