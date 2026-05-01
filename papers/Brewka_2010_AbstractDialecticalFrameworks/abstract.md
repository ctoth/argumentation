# Abstract

## Original Text (Verbatim)

In this paper we introduce dialectical frameworks, a powerful generalization of Dung-style argumentation frameworks where each node comes with an associated acceptance condition. This allows us to model different types of dependencies, e.g. support and attack, as well as different types of nodes within a single framework. We show that Dung's standard semantics can be generalized to dialectical frameworks, in case of stable and preferred semantics to a slightly restricted class which we call bipolar frameworks. We show how acceptance conditions can be conveniently represented using weights respectively priorities on the links and demonstrate how some of the legal proof standards can be modeled based on this idea.

---

## Our Interpretation

The paper addresses the limitation that Dung argumentation frameworks can only represent attack relationships between arguments. By attaching an arbitrary propositional acceptance condition to each node, ADFs can express support, joint attack, evidential dependencies, and any other Boolean combination of parent influences. This is directly relevant to propstore's argumentation layer, which needs to model not just defeats but also support relationships and complex acceptance criteria — particularly weighted acceptance conditions that map to legal proof standards like preponderance of evidence.
