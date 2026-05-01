# Abstract

## Original Text (Verbatim)

We present ABA+, a new approach to handling preferences in a well known structured argumentation formalism, Assumption-Based Argumentation (ABA). In ABA+, preference information given over assumptions is incorporated directly into the attack relation, thus resulting in attack reversal. ABA+ conservatively extends ABA and exhibits various desirable features regarding relationship among argumentation semantics as well as preference handling. We also introduce Weak Contraposition, a principle concerning reasoning with rules and preferences that relaxes the standard principle of contraposition, while guaranteeing additional desirable features for ABA+.

---

## Our Interpretation

The paper's implementation-relevant core is the preference-aware attack relation. For flat ABA+, the project needs the attack-reversal rule and the referendum example where `alpha < beta` makes `{beta}` the unique acceptable extension.
