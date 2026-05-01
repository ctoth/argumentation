# Abstract

## Original Text (Verbatim)

ASPIC+ is one of the main general frameworks for rule-based argumentation for AI. Although first-order rules are commonly used in ASPIC+ examples, most existing approaches to reason over rule-based argumentation only support propositional rules. To enable reasoning over first-order instances, a preliminary grounding step is required. As groundings can lead to an exponential increase in the size of the input theories, intelligent procedures are needed. However, there is a lack of dedicated solutions for ASPIC+. Therefore, we propose an intelligent grounding procedure that keeps the size of the grounding manageable while preserving the correctness of the reasoning process. To this end, we translate the first-order ASPIC+ instance into a Datalog program and query a Datalog engine to obtain ground substitutions to perform the grounding of rules and contraries. Additionally, we propose simplifications specific to the ASPIC+ formalism to avoid grounding of rules that have no influence on the reasoning process. Finally, we performed an empirical evaluation of a prototypical implementation to show scalability.

---

## Our Interpretation

The paper addresses the gap between first-order ASPIC+ theory (where rules naturally use variables) and existing propositional solvers by providing a principled grounding step via Datalog translation. The key innovation is exploiting ASPIC+-specific structure — particularly "non-approximated predicates" that can be fully resolved within Datalog without generating ground argumentation rules — to keep groundings tractable. This is directly relevant to propstore's planned extension from propositional claims to first-order defeasible rules, providing both the algorithm and correctness proofs needed for a Datalog-backed grounding engine.
