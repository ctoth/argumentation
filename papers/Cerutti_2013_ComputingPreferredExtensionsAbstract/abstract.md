# Abstract

## Original Text (Verbatim)

This paper presents a novel SAT-based approach for the computation of extensions in abstract argumentation, with focus on preferred semantics, and an empirical evaluation of its performances. The approach is based on the idea of reducing the problem of computing complete extensions to a SAT problem and then using a depth-first search method to derive preferred extensions. The proposed approach has been tested using two distinct SAT solvers and compared with three state-of-the-art systems for preferred extension computation. It turns out that the proposed approach delivers significantly better performances in the large majority of the considered cases.

---

## Our Interpretation

The paper treats preferred-extension enumeration as a search over SAT-encoded complete labellings, using SAT solver calls to grow complete extensions until they are maximal. Its practical contribution is not only the algorithm but also the evidence that encoding choice and solver backend strongly affect performance, with the Glucose-backed `C_2` configuration dominating the evaluated systems. For this project, it supplies a concrete preferred-semantics enumeration architecture and benchmark parameters for solver validation.
