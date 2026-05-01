---
tags: [abstract-argumentation, sat-solving, solver-architecture]
---
Describes Fudge, a lightweight C++ SAT-based abstract-argumentation solver. Its central engineering choices are standard SAT reductions for easy tasks, novel encodings for preferred skeptical and ideal reasoning, and incremental CaDiCaL calls. It supports our plan to refactor the package SAT helpers into an incremental task-directed backend.
