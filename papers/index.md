# Paper Index

## [Skeptical Reasoning with Preferred Semantics in Abstract Argumentation without Computing Preferred Extensions](Thimm_2021_SkepticalReasoningPreferredSemantics/notes.md)  (abstract-argumentation, sat-solving, preferred-semantics, ideal-semantics)
Presents CDAS, a SAT-call algorithm for skeptical preferred acceptance that avoids computing preferred extensions. Also derives CDIS, a related ideal-extension algorithm based on preferred-super-core pruning. This is the main implementation source for replacing native `DS-PR` and `SE-ID` enumeration paths in the solver.

## [Fudge: A light-weight solver for abstract argumentation based on SAT reductions](Thimm_2021_FudgeLight-weightSolverAbstract/notes.md)  (abstract-argumentation, sat-solving, solver-architecture)
Describes Fudge, a lightweight C++ SAT-based abstract-argumentation solver. Its central engineering choices are standard SAT reductions for easy tasks, novel encodings for preferred skeptical and ideal reasoning, and incremental CaDiCaL calls. It supports our plan to refactor the package SAT helpers into an incremental task-directed backend.

## [ArgSemSAT-1.0: Exploiting SAT Solvers in Abstract Argumentation](Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/notes.md)  (abstract-argumentation, sat-solving, preferred-semantics)
Describes ArgSemSAT, a C++/Glucose solver built around SAT encodings of complete labellings. It gives a compact implementation model for complete, grounded, preferred, stable, and acceptance tasks. It supports the package direction of making complete labellings the shared SAT surface.
