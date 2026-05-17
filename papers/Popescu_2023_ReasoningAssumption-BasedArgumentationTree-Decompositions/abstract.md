# Abstract

## Original Text (Verbatim)

We address complex reasoning tasks in assumption-based argumentation (ABA) by developing dynamic programming algorithms based on tree-decompositions. As one of the prominent approaches in computational argumentation, our focus is on NP-hard reasoning in ABA. We utilize tree-width, a structural measure describing closeness to trees, for an approach to handle computationally complex tasks in ABA. We contribute to the state of the art by first showing that many reasoning tasks in ABA are fixed-parameter tractable w.r.t. tree-width using Courcelle's theorem, informally signaling wide applicability of dynamic programming algorithms for ABA. Secondly, we develop such algorithms operating on tree-decompositions of given ABA frameworks. We instantiate the algorithms in the recent D-FLAT framework allowing for declarative and extensible specification of dynamic programming algorithms. In an experimental evaluation on a resulting prototype, we show promise of the approach in particular for complex counting tasks.

---

## Our Interpretation

The paper moves ABA reasoning beyond generic ASP encodings by exploiting bounded tree-width directly. Its main value is the combination of an MSO tractability result with concrete D-FLAT dynamic-programming table states for stable, admissible, and complete assumption-set reasoning.
