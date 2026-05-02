# Abstract

## Original Text (Verbatim)

Abstract argumentation frameworks (AFs) provide the basis for various reasoning problems in the areas of Knowledge Representation and Artificial Intelligence. Efficient evaluation of AFs has thus been identified as an important research challenge. So far, implemented systems for evaluating AFs have either followed a straight-forward reduction-based approach or been limited to certain tractable classes of AFs. In this work, we present a generic approach for reasoning over AFs, based on the novel concept of complexity-sensitivity. Establishing the theoretical foundations of this approach, we derive several new complexity results for preferred, semi-stable and stage semantics which complement the current complexity landscape for abstract argumentation, providing further understanding on the sources of intractability of AF reasoning problems. The introduced generic framework exploits decision procedures for problems of lower complexity whenever possible. This allows, in particular, instantiations of the generic framework via harnessing in an iterative way current sophisticated Boolean satisfiability (SAT) solver technology for solving the considered AF reasoning problems. First experimental results show that the SAT-based instantiation of our novel approach outperforms existing systems.

---

## Our Interpretation

The paper targets hard second-level reasoning problems in abstract argumentation and asks how to exploit lower-complexity fragments rather than always using large monolithic encodings. Its main result is both theoretical and practical: many graph-distance fragments remain hard, but bounded extension/range structure can support SAT-oracle CEGAR procedures. The work is relevant because it gives implementation-level SAT encodings and loop structure for incremental preferred, semi-stable, and stage reasoning.
