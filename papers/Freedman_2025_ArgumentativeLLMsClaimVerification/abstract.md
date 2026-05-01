# Abstract

## Original Text (Verbatim)

The profusion of knowledge encoded in large language models (LLMs) and their ability to apply this knowledge onto a range of settings makes them promising candidates for use in decision-making. However, they are currently limited by their inability to explain their reasoning in a way that can be fully explained and effectively contested to correct mistakes. In this paper, we attempt to reconcile these strengths and weaknesses by introducing argumentative LLMs (ArgLLMs), a method for argumentation-based claim verification. More concretely, ArgLLMs construct argumentation frameworks, which then serve as the basis for forming reasoning in support of decision-making. The interpretable nature of these argumentation frameworks guarantees that claims or other decisions made by ArgLLMs may be explained and contested. We conduct a comprehensive experimental evaluation in comparison with state-of-the-art techniques, in the context of the decision-making task of claim verification. We also define novel properties to characterize contestability and assess ArgLLMs formally against these properties.

---

## Our Interpretation

The paper addresses the gap between LLMs' knowledge and their inability to produce explainable, contestable reasoning. ArgLLMs solve this by having LLMs generate structured pro/con arguments with confidence scores, assembling them into QBAFs, and computing verdicts via DF-QuAD gradual semantics. This is directly relevant to propstore because it provides a concrete, proven mechanism for converting LLM confidence outputs into formal argumentation structures with guaranteed monotonicity and contestability properties.
