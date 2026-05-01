# Abstract

## Original Text (Verbatim)

Abstract argumentation frameworks nowadays provide the most popular formalization of argumentation on a conceptual level. Numerous semantics for this paradigm have been proposed, whereby the cf2 semantics has shown to solve particular problems concerned with odd-length cycles in such frameworks. Due to the complicated definition of this semantics it has somehow been neglected in the literature. In this article, we introduce an alternative characterization of the cf2 semantics which, roughly speaking, avoids the recursive computation of subframeworks. This facilitates further investigation steps, like a complete complexity analysis. Furthermore, we show how the notion of strong equivalence can be characterized in terms of the cf2 semantics. In contrast to other semantics, it turns out that for the cf2 semantics strong equivalence coincides with syntactical equivalence. We make this particular behaviour more explicit by defining a new property for argumentation semantics, called the succinctness property. If a semantics satisfies the succinctness property, then for every framework F, all its attacks contribute to the evaluation of at least one framework F containing F. We finally characterize strong equivalence also for the stage and the naive semantics. Together with known results these characterizations imply that none of the prominent semantics for abstract argumentation, except the cf2 semantics, satisfies the succinctness property.

## Our Interpretation

The paper’s core move is to turn cf2 from a recursively defined SCC procedure into a fixed-point computation over defeated arguments. That makes the semantics easier to analyze, gives clean complexity bounds, and exposes a strong property: under cf2, every attack can matter, so strong equivalence collapses to exact syntactic equality.

