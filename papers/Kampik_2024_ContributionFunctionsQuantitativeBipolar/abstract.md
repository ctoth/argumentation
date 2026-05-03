# Abstract

## Original Text (Verbatim)

We present a principle-based analysis of *contribution functions* for quantitative bipolar argumentation graphs that quantify the contribution of one argument to another. The introduced principles formalise the intuitions underlying different contribution functions as well as expectations one would have regarding the behaviour of contribution functions in general. As none of the covered contribution functions satisfies all principles, our analysis can serve as a tool that enables the selection of the most suitable function based on the requirements of a given use case.

*Key words:* Quantitative Argumentation, Explainable AI, Automated Reasoning

---

## Our Interpretation

The paper closes a gap in QBA explainability by giving the first comprehensive principle-based analysis of contribution functions: it formalises four candidate functions (Removal, Removal-without-indirection, Shapley, Gradient) and five principles (Contribution Existence, Quantitative Contribution Existence, Directionality, (Quantitative) Local Faithfulness, (Quantitative) Counterfactuality), and proves a 5×4 satisfaction matrix across five named gradual semantics (QE, DFQuAD, SD-DFQuAD, EB, EBT). The key practical takeaway is that Counterfactuality and Local Faithfulness are mutually unsatisfiable in general, so users must pick the contribution function aligned with their explanation goal — Removal for "what happens if I delete this argument," Gradient for "how sensitive is the topic to small changes," Shapley for "how do contributions decompose additively." Relevant to argumentation-based explanation frameworks that need a defensible attribution semantics atop QBAGs, and as a methodological template for principle-based comparison of any inference-attribution scheme.
