# Abstract

## Original Text (Verbatim)

In argumentation theory, Dung's abstract framework provides a unifying view of several alternative semantics based on the notion of extension. In this context, we propose a general recursive schema for argumentation semantics, based on decomposition along the strongly connected components of the argumentation framework. We introduce the fundamental notion of SCC-recursiveness and we show that all Dung's admissibility-based semantics are SCC-recursive, and therefore a special case of our schema. On these grounds, we argue that the concept of SCC-recursiveness plays a fundamental role in the study and definition of argumentation semantics. In particular, the space of SCC-recursive semantics provides an ideal basis for the investigation of new proposals: starting from the analysis of several examples where Dung's preferred semantics gives rise to questionable results, we introduce four novel SCC-recursive semantics, able to overcome the limitations of preferred semantics, while differing in other respects.

---

## Our Interpretation

The paper factors any admissibility-based argumentation semantics into two pieces: a graph decomposition (strongly connected components of the defeat graph, processed in topological order of the acyclic condensation) and a semantics-specific base function `BF_S` that is only ever evaluated on single-SCC sub-frameworks. Parent SCCs' choices are injected into each child SCC via the `D`/`U`/`P` partition (Def 18) and a restriction operator (Def 19), so a semantics is fully specified by its base function alone. For this project it is the canonical source for `core/scc_recursive.py`: the directionality principle is exactly what makes query-directed pruning sound, and the paper's closing call for "incremental algorithms based on local computation at the level of SCCs" is the precedent for wiring SCC decomposition into the SAT acceptance solver.
