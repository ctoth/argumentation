---
tags: [qbaf, gradual-semantics, explanation, attribution, df-quad]
---
Defines Argument Attribution Explanations (AAEs) as gradient-based attribution scores `∇|_{B↦A} = ∂σ(A)/∂τ(B)` over arguments in acyclic Quantitative Bipolar Argumentation Frameworks (QBAFs) under DF-QuAD gradual semantics, with closed-form direct (Prop 2) and indirect chain-rule (Prop 4) expressions computable in O(n) time.
The paper proves six properties (explainability, missingness, completeness, counterfactuality, agreement, monotonicity) for arguments connected via a single path and gives explicit counterexamples (Props 8, 10, 12, 14) showing those guarantees can fail under multifold connectivity, then validates with case studies in fake-news detection, movie recommendation, and a 48-argument fraud-detection QBAF.
This is the anchor paper for any quantitative explanation workstream over the project's QBAF substrate; closed forms enable a non-SAT, linear-time attribution implementation, and the property gaps under multifold paths flag a concrete open problem to address in the project.
