# Abstract

## Original Text (Verbatim)

An argumentation system consists of a set of interacting arguments. The most popular semantics are those from Dung. They consist of computing extensions, i.e. sets of arguments which are acceptable together. The purpose of this paper is to propose a new family of semantics which rank-orders arguments from the most acceptable to the weakest one(s). The new semantics carry two other main features: i) an attack weakens its target but does not kill it; ii) the number of attackers has a great impact on the acceptability of an argument. We start by proposing a set of rational postulates that such semantics could satisfy, then construct various semantics that enjoy them.

---

## Our Interpretation

The paper addresses the coarseness of Dung's extension-based semantics, which partition arguments into at most three classes (accepted/rejected/undecided), by introducing ranking-based semantics that produce a total preorder over all arguments. It proposes eight formal postulates as correctness criteria for such rankings and constructs two concrete semantics (Discussion-based and Burden-based) with proven postulate-satisfaction properties. This is directly relevant for implementing graded argument acceptability in systems that need finer distinctions than binary accept/reject, such as propstore's render-layer resolution strategies.
