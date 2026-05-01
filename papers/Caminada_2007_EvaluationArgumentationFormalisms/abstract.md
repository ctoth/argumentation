# Abstract

## Original Text (Verbatim)

Argumentation theory has become an important topic in the field of AI. The basic idea is to construct arguments in favor and against a statement, to select the "acceptable" ones and, finally, to determine whether the original statement can be accepted or not.

Several argumentation systems have been proposed in the literature. Some of them, the so-called *rule-based systems*, use a particular logical language with *strict* and *defeasible rules*. While these systems are useful in different domains (e.g. legal reasoning), they unfortunately lead to very unintuitive results, as is discussed in this paper.

In order to avoid such anomalies, in this paper we are interested in defining principles, called *rationality postulates*, that can be used to judge the quality of a rule-based argumentation system. In particular, we define two important rationality postulates that should be satisfied: the *consistency* and the *closure* of the results returned by that system.

We then provide a relatively easy way in which these rationality postulates can be warranted for a particular rule-based argumentation system developed within a European project on argumentation.

---

## Our Interpretation

The paper addresses a fundamental quality problem in rule-based argumentation systems: they can produce contradictory or incomplete justified conclusions even when the underlying knowledge base is consistent. The key contribution is a set of three rationality postulates (closure, direct consistency, indirect consistency) that serve as formal evaluation criteria for any argumentation formalism, plus two concrete solutions (propositional closure and transposition closure with restricted rebutting) that guarantee these postulates are satisfied. This work is directly foundational for ASPIC+ and thus for any structured argumentation system used to evaluate competing claims.
