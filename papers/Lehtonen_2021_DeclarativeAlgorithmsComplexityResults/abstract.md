# Abstract

## Original Text (Verbatim)

The study of computational models for argumentation is a vibrant area of artificial intelligence and, in particular, knowledge representation and reasoning research. Arguments most often have an intrinsic structure made explicit through derivations from more basic structures. Computational models for structured argumentation enable making the internal structure of arguments explicit. Assumption-based argumentation (ABA) is a central structured formalism for argumentation in AI. In this article, we make both algorithmic and complexity-theoretic advances in the study of ABA. In terms of algorithms, we propose a new approach to reasoning in a commonly studied fragment of ABA (namely the logic programming fragment) with and without preferences. While previous approaches to reasoning over ABA frameworks apply either specialized algorithms or translate ABA reasoning to reasoning over abstract argumentation frameworks, we develop a direct declarative approach to ABA reasoning by encoding ABA reasoning tasks in answer set programming. We show via an extensive empirical evaluation that our approach significantly improves on the empirical performance of current ABA reasoning systems. In terms of computational complexity, while the complexity of reasoning over ABA frameworks is well-understood, the complexity of reasoning in the ABA+ formalism integrating preferences into ABA is currently not fully established. Towards bridging this gap, our results suggest that the integration of preferential information into ABA via so-called reverse attacks results in increased problem complexity for several central argumentation semantics.

---

## Our Interpretation

This paper is both an implementation paper and a complexity paper for ABA reasoning. It argues for direct ASP encodings over translation-to-AF pipelines, and shows that ABA+ preferences are not a benign add-on: reverse attacks can push core reasoning tasks higher in the polynomial hierarchy.
