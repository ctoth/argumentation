# Abstract

## Original Text (Verbatim)

We provide a systematic in-depth study of the semantics of abstract dialectical frameworks (ADFs), a recent generalisation of Dung's abstract argumentation frameworks. This is done by associating with an ADF its characteristic one-step consequence operator and defining various semantics for ADFs as different fixpoints of this operator. We first show that several existing semantical notions are faithfully captured by our definition, then proceed to define new ADF semantics and show that they are proper generalisations of existing argumentation semantics from the literature. Most remarkably, this operator-based approach allows us to compare ADFs to related nonmonotonic formalisms like Dung argumentation frameworks and propositional logic programs. We use polynomial, faithful and modular translations to relate the formalisms, and our results show that both abstract argumentation frameworks and abstract dialectical frameworks are at most as expressive as propositional normal logic programs.

© 2013 Elsevier B.V. All rights reserved.

---

## Our Interpretation

Strass embeds Brewka & Woltran's abstract dialectical frameworks (ADFs) into the Denecker-Marek-Truszczyński approximation-fixpoint-theory (AFT) framework by defining a single *characteristic operator* G_Ξ on the bilattice 2^S × 2^S whose fixpoints (and their supported/stable/3-valued/M-/L- variants) yield, in one stroke, all major semantics for ADFs — including new admissible/preferred/semi-stable/stage/naive notions for non-bipolar ADFs that previous BW machinery could not express. The paper then proves polynomial, faithful, modular translations ADFs ↔ logic programs and AFs ↔ logic programs (both via the standard "attack-as-negation-as-failure" encoding and Dung's original explicit encoding, shown equivalent), locating AFs and ADFs in the broader nonmonotonic-reasoning landscape (AFs ⊆ ADFs ⊆ LPs ⊆ default logic ⊆ autoepistemic logic). For our argumentation collection it is the canonical reference for ADF semantics infrastructure, the operator collapse SF_Θ = F_Θ that explains why AFs cannot distinguish supported from stable, and the foundation for ASP encodings of preferred/semi-stable/stable AF reasoning.
