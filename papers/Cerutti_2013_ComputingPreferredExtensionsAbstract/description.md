---
tags: [abstract-argumentation, sat-solving, preferred-semantics, solver-architecture]
---
Presents PrefSat, a SAT-based algorithm for enumerating preferred extensions of finite abstract argumentation frameworks by searching over complete labellings. The paper classifies complete-labelling SAT encodings, proves the enumeration algorithm correct, and reports that a Glucose-backed implementation substantially outperforms ASPARTIX/dlv, ASPARTIX-META, and NOF on 2,816 random AFs. It is directly useful for designing and testing SAT-backed preferred-extension enumeration in this project's argumentation solver work.
