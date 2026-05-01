# Abstract

## Original Text (Verbatim)

An assumption-based truth maintenance system provides a very general facility for all types of default reasoning. However, the ATMS is only one component of an overall reasoning system. This paper presents a set of concerns for interfacing with the ATMS, an interface protocol, and an example of a constraint language based on the protocol. The paper concludes with a comparison of the ATMS and the view of problem solving it entails with other approaches.

---

## Our Interpretation

The ATMS tracks which assumptions support which conclusions, but building a correct problem solver on top of it requires careful protocol design. This paper defines that protocol: a "consumer" architecture where inference rules are modular units attached to nodes, firing exactly once when their prerequisites hold; a scheduling strategy that finds simpler solutions first; and a constraint language that compiles arithmetic and logical constraints into ATMS primitives. This is the implementation companion to the ATMS theory paper, providing the concrete machinery needed to build systems like propstore's world model.
