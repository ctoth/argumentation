# Abstract

## Original Text (Verbatim)

Bondarenko et al. have recently proposed an abstract framework for default reasoning. Besides capturing most existing formalisms and proving that their standard semantics all coincide, the framework extends these formalisms by generalising the semantics of admissible and preferred arguments, originally proposed for logic programming only.

In this paper we analyse the computational complexity of credulous and sceptical reasoning under the semantics of admissible and preferred arguments for (the propositional variant of) the instances of the abstract framework capturing theorist, circumscription, logic programming, default logic, and autoepistemic logic. Although the new semantics have been tacitly assumed to mitigate the computational hardness of default reasoning under the standard semantics of stable extensions, we show that in many cases reasoning under the admissibility and preferability semantics is computationally harder than under the standard semantics. In particular, in the case of autoepistemic logic, sceptical reasoning under preferred arguments is located at the fourth level of the polynomial hierarchy, whereas the same form of reasoning under stable extensions is located at the second level.

---

## Our Interpretation

The paper tests whether ABA admissible/preferred semantics are computationally easier than stable-extension semantics for default-reasoning formalisms. Its main finding is negative in the worst case: preferred and admissible reasoning often match or exceed the stable-semantics complexity, with AEL preferred-sceptical reasoning rising to `Pi^p_4`. This matters for implementation because a local argument-construction story does not by itself imply a cheaper decision procedure.
