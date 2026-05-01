# Abstract

## Original Text (Verbatim)

Argumentation is a formalism allowing to reason with contradictory information by modeling arguments and their interactions. There are now an increasing number of gradual semantics to compute argument strengths and impact measures that have emerged to facilitate the interpretation of their outcomes. An impact measure assesses, for each argument, the impact of other arguments on its score. In this paper, we refine an existing impact measure from Delobelle and Villata and introduce a new impact measure rooted in Shapley values. We introduce several principles to evaluate those two impact measures w.r.t. some well-known gradual semantics. Our analysis provides deeper insights into the measures' functionality and desirability.

---

## Our Interpretation

The paper addresses the explainability gap in gradual argumentation semantics: given computed argument strengths, how do we explain which arguments caused a particular score? It proposes two complementary impact measures -- one based on selective attack removal and one based on Shapley values from game theory -- and rigorously evaluates them against nine axiomatic principles across four gradual semantics. The key finding is that counting semantics uniquely satisfies both Independence and Directionality, making it the most "well-behaved" semantics for impact analysis.
