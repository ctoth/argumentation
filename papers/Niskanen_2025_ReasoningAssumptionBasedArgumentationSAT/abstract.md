# Abstract

## Original Text (Verbatim)

The dominant approaches for solving NP-hard reasoning problems in computational argumentation are declarative—namely, Boolean satisfiability (SAT) in the case of abstract argumentation and answer set programming (ASP) in the case of structured formalisms such as assumption-based argumentation (ABA). ASP is particularly suited for the commonly-studied logic programming variant of ABA as acyclic derivations in ABA can be naturally modelled in ASP. In this work, we develop and evaluate various alternative approaches to realizing SAT-based reasoning for ABA, motivated by the success of SAT solvers in the realm of abstract argumentation. In contrast to ASP, non-trivial encodings or extensions to SAT solvers are needed to efficiently handle the acyclicity constraint underlying ABA reasoning. We develop and evaluate both advanced encodings and user-defined propagation mechanisms for realizing efficient SAT-based reasoning in ABA. As a result, we provide a first SAT-based ABA reasoner that can outperform the current state-of-the-art ASP approach to ABA.

---

## Our Interpretation

The core problem is that SAT, unlike ASP's stable-model semantics, does not natively forbid an atom from cyclically supporting its own derivation, so a naive SAT encoding of ABA is unsound; enforcing acyclic derivation over potentially long chains is the technical obstacle. The paper solves it four ways — a level-indexed encoding, a compact vertex-elimination encoding, and two IPASIR-UP user propagators (graph-DFS acyclicity and CLASP-style unfounded-set source pointers) — and shows the vertex-elimination and unfounded-set variants are the first SAT-based ABA reasoners competitive with, and sometimes clearly better than, the dominant ASPforABA. It is directly relevant because this project implements its own ABA SAT acyclicity encodings, for which this is the authoritative reference.
