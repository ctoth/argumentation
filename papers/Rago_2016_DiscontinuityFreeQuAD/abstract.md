# Abstract

## Original Text (Verbatim)

BBS (Issue Based Information System) provides a widely adopted approach for knowledge representation especially suitable for the challenging task of representing a real decision-making process, which may involve several issues. Since creative development of BBS graphs are automated, automated decision support for decision or still undecided topics, even though it might still benefit current applications, QuAD (Quantitative Argumentation Debate) frameworks are a recently proposed BBS-based formalism encouraging automated decision support by means of an algorithm for computing the strength of answers in decision questions, given an BBS graph of a restricted kind (Baroni et al. 2015) for details. The algorithm aggregates the strengths of attacking and supporting arguments for the answers and for the other arguments from their base scores, given by a function BS, upward within the design/IBIS/BBS tree (Baroni et al. 2015), and the data analysis system (Aurisicchio et al. 2015) has shown practical in several applications in engineering design. The initially proposed aggregation method, however, may give rise to discontinuities. In this paper we propose a novel, discontinuity-free alternative, called DF-QuAD, for computing the strength of arguments in QuAD frameworks. We prove several desirable properties of the new algorithm and compare its behaviour to the original one with the two aggregation methods, showing that both may be appropriate in the context of different application scenarios.

---

## Our Interpretation

The paper addresses a fundamental flaw in the original QuAD strength aggregation algorithm: discontinuity at the boundary where aggregated attacking strength equals aggregated supporting strength. The DF-QuAD algorithm eliminates this by replacing the absolute-value case split with a smooth interpolation scaled by the base score. This is directly relevant to propstore's bipolar argumentation layer, which implements DF-QuAD for gradual semantics.
