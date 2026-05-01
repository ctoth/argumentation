# Abstract

## Original Text (Verbatim)

We explore a framework for argumentation (based on classical logic) in which an argument is a pair where the first item in the pair is a minimal consistent set of formulae that proves the second item (which is a formula). We provide some basic definitions for arguments, and various kinds of counter-arguments (defeaters). This leads us to the definition of canonical undercuts which we argue are the only defeaters that we need to take into account. We then motivate and formalise the notion of argument trees and argument structures which provide a way of exhaustively collating arguments and counter-arguments. We use argument structures as the basis of our general proposal for argument aggregation.

There are a number of frameworks for modelling argumentation in logic. They incorporate formal representation of individual arguments and techniques for comparing conflicting arguments. In these frameworks, if there are a number of arguments for and against a particular conclusion, an aggregation function determines whether the conclusion is taken to hold. We propose a generalisation of these frameworks. In particular, our new framework makes it possible to define aggregation functions that are sensitive to the number of arguments for or against. We compare our framework with a number of other types of argument systems, and finally discuss an application in reasoning with structured news reports.

---

## Our Interpretation

This paper establishes the formal logical foundations for structured argumentation based on classical propositional logic. The key innovation is defining arguments as minimal consistent support sets paired with their deductive consequences, then building a complete hierarchy of counter-argument types (defeaters, undercuts, rebuttals), argument trees, argument structures, and aggregation functions. This is directly relevant to propstore's argumentation layer because it provides the precise definitions needed to construct and evaluate arguments from a knowledge base of potentially conflicting claims, and its categoriser/accumulator framework provides a formal basis for aggregating competing arguments at render time.
