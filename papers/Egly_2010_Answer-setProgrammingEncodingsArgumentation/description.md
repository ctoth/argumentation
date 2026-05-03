---
tags: [argumentation, asp, dung, semantics, implementation]
---
Presents fixed-query disjunctive-datalog (ASP) encodings for the principal abstract argumentation semantics over Dung AFs (conflict-free, stable, admissible, complete, grounded, preferred, semi-stable) plus value-based and bipolar generalisations, packaged as the ASPARTIX system over DLV.
The encodings are *fixed* per semantics (the AF varies only through the input database), each module's data complexity matches the natural complexity class of the encoded reasoning problem, and Σ₂ᴾ/Π₂ᴾ-hard semantics use disjunction + saturation rather than per-instance recompilation.
Canonical reference for any project that wants to compute or compare AF extensions via off-the-shelf ASP solvers, and a template for encoding new semantics or extension-comparison metaproblems (coherence, semi=preferred) in the same paradigm.
