# Abstract

## Original Text (Verbatim)

Argumentation, in the field of Artificial Intelligence, is a formalism allowing to reason with contradictory information as well as to model an exchange of arguments between one or several agents. For this purpose, many semantics have been defined with, amongst them, gradual semantics aiming to assign an acceptability degree to each argument. Although the number of these semantics continues to increase, there is currently no method allowing to explain the results returned by these semantics. In this paper, we study the interpretability of these semantics by measuring, for each argument, the impact of the other arguments on its acceptability degree. We define a new property and show that the score of an argument returned by a gradual semantics which satisfies this property can also be computed by aggregating the impact of the other arguments on it. This result allows to provide, for each argument in an argumentation framework, a ranking between arguments from the most to the least impacting ones w.r.t. a given gradual semantics.

Keywords: Abstract Argumentation; Gradual Semantics; Interpretability

---

## Our Interpretation

Gradual semantics produce a numeric acceptability score per argument but no native explanation of *why*. The paper formalises a deletion-based "impact" measure of one argument (or set) on another, identifies a Balanced Impact (BI) axiom under which scores decompose additively into per-argument contributions (Counting Semantics satisfies it; h-categorizer does not), and gives an ACY unfolding to extend the decomposition to cyclic AFs. The result is a principled interpretability story for gradual semantics: per-argument impact rankings that identify the most positive/negative contributors and inform debate strategy.
