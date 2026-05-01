# Abstract

## Original Text (Verbatim)

We introduce and investigate a natural extension of Dung's well-known model of argument systems in which attacks are associated with a weight, indicating the relative strength of the attack. A key concept in our framework is the notion of an inconsistency budget, which characterises how much inconsistency we are prepared to tolerate: given an inconsistency budget β, we would be prepared to disregard attacks up to a total weight of β. The key advantage of this approach is that it permits a much finer grained level of analysis of argument systems than unweighted systems, and gives useful solutions when conventional (unweighted) argument systems have none. We begin by reviewing Dung's abstract argument systems, and motivating weights on attacks (as opposed to the alternative possibility, which is to attach weights to arguments). We then present the framework of weighted argument systems. We investigate solutions for weighted argument systems and the complexity of computing such solutions, focussing in particular on weighted variations of grounded extensions. Finally, we relate our work to the most relevant examples of argumentation frameworks that incorporate strengths.

---

## Our Interpretation

The paper turns abstract argumentation into a budgeted optimization problem: instead of treating all attacks equally, it lets a system ignore a bounded amount of attack weight and then computes ordinary semantics on the reduced graph. For propstore, the main value is that this gives a principled formal semantics for externally assigned attack strengths together with concrete complexity and optimization results for grounded-style reasoning.
