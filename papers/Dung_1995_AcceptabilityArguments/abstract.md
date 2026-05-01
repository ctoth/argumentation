# Abstract

## Original Text (Verbatim)

The purpose of this paper is to study the fundamental mechanism, humans use in argumentation, and to explore ways to implement this mechanism on computers. We do so by first developing a theory for argumentation whose central notion is the acceptability of arguments. Then we argue for the "correctness" or "appropriateness" of our theory with two strong arguments. The first one shows that most of the major approaches to nonmonotonic reasoning in AI and logic programming are special forms of our theory of argumentation. The second argument illustrates how our theory can be used to investigate the logical structure of many practical problems. This argument is based on a result showing that our theory captures naturally the solutions of the theory of n-person games and of the well-known stable marriage problem.

By showing that argumentation can be viewed as a special form of logic programming with negation as failure, we introduce a general logic-programming-based method for generating meta-interpreters for argumentation systems, a method very much similar to the compiler-compiler idea in conventional programming.

---

## Our Interpretation

The paper formalizes the intuitive principle that an argument is acceptable if it can survive all attacks against it. By abstracting away the internal structure of arguments and focusing only on attack relations, Dung creates a unifying framework that subsumes default logic, defeasible reasoning, and logic programming semantics. The result is directly relevant to any system that must reason about conflicting information from multiple sources, providing both the theoretical foundation and a practical implementation path via logic programming meta-interpreters.
