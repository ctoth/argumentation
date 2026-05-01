---
tags:
  - structured-argumentation
  - aspic-plus
  - incomplete-information
  - answer-set-programming
  - defeasible-reasoning
---

Extends ASPIC+ structured argumentation to handle incomplete information by defining four justification statuses (unsatisfiable, defended, out, blocked) for literals whose truth values may be unknown, and introduces stability and relevance as decision problems for determining whether a literal's status is robust to new information and which unresolved queries could change it. Provides complexity results (coNP-complete for stability, Sigma_2^P-complete for relevance under grounded semantics) and practical ASP-based algorithms implemented in Clingo, evaluated on both synthetic benchmarks and real-world criminal investigation data from the Netherlands Police. Directly relevant to propstore as a computational framework for reasoning about claim acceptance under incrementally arriving evidence, building on the ASPIC+ formalization (Modgil & Prakken 2014, 2018) already in the collection.
