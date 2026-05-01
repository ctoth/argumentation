---
tags: [aspic-plus, grounding, datalog, rule-based-argumentation, first-order]
---
Proposes an intelligent grounding procedure that translates first-order ASPIC+ argumentation theories into Datalog programs, using a Datalog engine to compute ground substitutions for rules and contraries. Introduces ASPIC+-specific simplifications including non-approximated predicate detection that avoids grounding rules with no influence on reasoning, and demonstrates scalability through the ANGRY prototype evaluated on random and benchmark instances. Directly relevant to propstore's ASPIC+ bridge and planned Defeasible Datalog rule language, providing formal correctness guarantees (complete extension preservation) for the grounding step.
