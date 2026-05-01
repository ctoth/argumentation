# Katie Atkinson and Trevor J. M. Bench-Capon (2007), "Practical reasoning as presumptive argumentation using action based alternating transition systems"

## Bibliographic Details

- Title: "Practical reasoning as presumptive argumentation using action based alternating transition systems"
- Authors: Katie Atkinson and Trevor J. M. Bench-Capon
- Venue: Artificial Intelligence 171, 855-874
- Year: 2007
- DOI: 10.1016/j.artint.2007.04.009
- Page images read directly: printed pages 855-874.

## Core Contribution

The paper formalizes practical reasoning as presumptive argumentation. A candidate action is justified by instantiating an argument scheme, and then challenged through critical questions. The formal grounding is an Action-Based Alternating Transition System (AATS), extended with value promotion and demotion, so that argument schemes and critical questions have precise interpretations (pp. 855-856).

The contribution is not just another action-choice heuristic. The paper insists that practical reasoning differs from belief reasoning because action choice is defeasible, subjective, and preference-forming: values and preferences are products of practical reasoning rather than fixed utility inputs (pp. 856-857, 872-873).

## Practical Reasoning Background

The paper begins with the practical syllogism: if the agent wants `E`, and doing `M` is the best way to achieve `E`, then the agent will do `M` (p. 856). It identifies three bases for criticism:

- C1: the argument is abductive; there may be alternative ways to achieve the goal.
- C2: performing an action excludes other actions that may have more desirable results.
- C3: actions have consequences; undesirable consequences may be enough to abandon the goal.

The paper treats practical reasoning as presumptive: an argument gives a prima facie reason for action, but the presumption can be challenged and withdrawn by critical questions (p. 857).

Values are qualitative reasons for choosing or avoiding states, not utility numbers. Values denote social attitudes or interests an agent may or may not subscribe to. Quantitative measures may represent degree of promotion, but those are not rankings of values (p. 857).

## AS1 Argument Scheme

The argument scheme AS1 is stated on p. 858:

```text
AS1
In the current circumstances R
We should perform action A
Which will result in new circumstances S
Which will realise goal G
Which will promote some value V.
```

The scheme separates the state of affairs brought about by the action, the goal as desired features in that state, and the value explaining why those features are desirable (p. 858).

## Critical Questions

The paper lists sixteen critical questions on p. 858:

- CQ1: Are the believed circumstances true?
- CQ2: Assuming the circumstances, does the action have the stated consequences?
- CQ3: Assuming the circumstances and that the action has the stated consequences, will the action bring about the desired goal?
- CQ4: Does the goal realise the value stated?
- CQ5: Are there alternative ways of realising the same consequences?
- CQ6: Are there alternative ways of realising the same goal?
- CQ7: Are there alternative ways of promoting the same value?
- CQ8: Does doing the action have a side effect which demotes the value?
- CQ9: Does doing the action have a side effect which demotes some other value?
- CQ10: Does doing the action promote some other value?
- CQ11: Does doing the action preclude some other action which would promote some other value?
- CQ12: Are the circumstances as described possible?
- CQ13: Is the action possible?
- CQ14: Are the consequences as described possible?
- CQ15: Can the desired goal be realised?
- CQ16: Is the value indeed a legitimate value?

Because AATS joint actions may depend on other agents' action choices, the paper adds CQ17: is the other agent guaranteed to execute its part of the desired joint action? (p. 859). CQ17 is distinct from CQ2 because the transition may be correct if the joint action occurs, while the objector challenges whether the other agent will actually choose its component action (p. 859).

Negative answers to CQ5-CQ11 themselves form AS1-style arguments, because they propose alternatives, side effects, or action conflicts in the choice-of-action stage (p. 859).

## AATS Definition

Section 4 introduces Action-Based Alternating Transition Systems (AATSs) as the formal structure for actions and effects (p. 860). The base AATS contains:

- A finite, nonempty set `Q` of states.
- Initial state `q0 in Q`.
- A finite, nonempty set of agents `Ag = {1, ..., n}`.
- For each agent `i`, a finite nonempty action set `Ac_i`; different agents' action sets are pairwise disjoint.
- An action precondition function `rho: Ac_Ag -> 2^Q`, where `rho(alpha)` is the set of states from which action `alpha` may be executed.
- A partial transition function `tau: Q x J_Ag -> Q`, where `tau(q, j)` is the state that results when joint action `j` is performed from state `q`.
- A finite, nonempty set `Phi` of atomic propositions.
- Interpretation function `pi: Q -> 2^Phi`, giving propositions true in each state.

Joint action `j` for a coalition is a tuple of component actions, one per participating agent. `J_C` is the set of joint actions for coalition `C`; `j_i` is agent `i`'s component action in joint action `j` (p. 860).

The paper extends AATSs with values (pp. 860-861):

- For each agent `i`, `Av_i` is a finite nonempty set of values.
- `delta: Q x Q x Av_Ag -> {+, -, =}` is a valuation function. `delta(q_x, q_y, v_u)` labels the transition between states `q_x` and `q_y` as promoting `v_u` (`+`), demoting `v_u` (`-`), or neutral with respect to `v_u` (`=`).

The extended AATS is written (p. 861):

```text
S = (Q, q0, Ag, Ac1, ..., Acn, Av1, ..., Avn, rho, tau, Phi, pi, delta)
```

## AS2: AS1 Restated In AATS Terms

Section 5 restates AS1 over the extended AATS as AS2 (p. 861):

```text
AS2
The initial state q0 = qx in Q,
Agent i in Ag should participate in joint action jn in JAg where ji_n = alpha_i,
Such that tau(qx, jn) is qy,
Such that p_a in pi(qy) and p_a notin pi(qx), or p_a notin pi(qy) and p_a in pi(qx),
Such that for some vu in Av_i, delta(qx, qy, vu) is +.
```

The scheme maps current state, chosen joint action, resulting state, goal-relevant proposition change, and value promotion to the AATS (p. 861).

## Formal Critical Question Conditions

The paper groups CQs by practical-reasoning stage. CQ2-CQ4 and CQ12-CQ16 relate to problem formulation; CQ1 and CQ17 relate to epistemic reasoning; CQ5-CQ11 relate to the final choice-of-action stage (pp. 861-862).

For the workstream slice, the relevant choice-stage questions are on p. 862:

```text
CQ5:
Agent i in Ag can participate in joint action jm in JAg, where jn != jm,
such that tau(qx, jm) is qy.
```

CQ5 asks whether a different joint action reaches the same state/consequences as the proposed action (p. 862).

```text
CQ6:
Agent i in Ag can participate in joint action jm in JAg, where jn != jm,
such that tau(qx, jm) is qy,
such that p_a in pi(qy) and p_a notin pi(qx), or
p_a notin pi(qy) and p_a in pi(qx).
```

CQ6 asks whether a different joint action realizes the same goal-relevant proposition change (p. 862).

```text
CQ11:
In the initial state qx in Q, if agent i in Ag participates in joint action jn in JAg,
then tau(qx, jn) is qy and delta(qx, qy, vu) is +.
But there is some other joint action jm in JAg, where jn != jm,
such that tau(qx, jm) is qz,
such that delta(qx, qz, vw) is +, where vu != vw.
```

CQ11 identifies a clash between the proposed action and another desirable action: the proposed action precludes a different action that would promote a different value (p. 862). The worked example explicitly says CQ11 accounts for future as well as current actions that are precluded (p. 870).

The paper gives variants, e.g. CQ2b and CQ4b, where a challenger not only denies a claimed transition/value promotion but asserts an alternative transition or demotion. These variants can make stronger attacks, but the paper does not fully formalize all variants (p. 863).

## Worked Example

Section 6 applies the approach to a classic crossing problem with farmer, boat, chicken, seeds, and dog. States are represented by item lists on the river banks. The initial state is `[BCDS, _]` (p. 863). Joint actions include rowing alone, rowing seeds, rowing dog, rowing chicken, doing nothing, and animal actions such as chicken eating seeds or dog eating chicken (pp. 863-864).

The values used in the example are listed on p. 864:

- `P`: progress, promoted by moving a possession to the right bank and demoted by revisiting states.
- `S`: having seeds, demoted by losing seeds.
- `C`: having chicken, demoted by losing chicken.
- `F`: friendship, promoted by traveling with the dog.
- `DH`: dog happiness, promoted when the dog eats the chicken.
- `CH`: chicken happiness, promoted when the chicken eats the seeds.

The example instantiates arguments and objections for all seventeen CQs (pp. 864-870). Examples relevant to the workstream slice:

- Objection `Obj2f`: rowing alone precludes rowing the seeds, which would put the seeds on the right bank and promote `P`; this is CQ11 (p. 865).
- Objection `Obj4b`: rowing the chicken would also promote `P`; this is CQ6 (p. 865).
- Objection `Obj4c`: if the farmer rows the seeds, he cannot row the dog to promote `F`; this is CQ11 (p. 865).
- At state `q11`, rowing seeds promotes `P`, but rowing dog is an alternative way of moving something to the right bank and is precluded by rowing seeds; rowing dog also promotes `F`, so CQ6 and CQ11 can both apply (p. 868).
- At state `q16`, all alternatives have arguments against them; going home is selected (p. 869).

The authors stress that the example is not meant as a planning algorithm. It demonstrates how action choices can be justified locally with presumptive arguments and critical questions, while values explain which objections defeat which arguments for a particular agent (pp. 869-870).

## Social Laws Comparison

Section 7 compares the AATS/practical-reasoning approach with social laws. Social laws constrain agents to guarantee objectives such as avoiding collisions (pp. 870-871). The paper argues that practical reasoning can evaluate whether a law is acceptable, not only whether it is effective. A good social law should align with what rational agents already have reason to do, or agents may be tempted to violate it (pp. 871-872).

Social laws make other agents' behavior more predictable. In this framework, they can provide arguments against CQ17-style objections by showing the other agent is not allowed to act in a way that produces an undesired state (p. 872).

## Conclusions

The concluding section identifies three characteristics a satisfactory account of practical reasoning must support (p. 872):

- Practical reasoning is inescapably defeasible and must always be evaluated in the context of arguments already made.
- It is inherently subjective because agents have different values, interests, and aspirations.
- Preferences should be capable of being a product of practical reasoning, not only an input to it.

The paper's main contribution is the well-defined AATS structure that lets practical argument schemes and critical questions be precisely instantiated, using value promotion/demotion as the bridge from actions to argumentation (pp. 873-874).

## Implementation Consequences

- Model AS1/AS2 as a typed practical argument over current state, acting agent, joint action, resulting state, goal proposition change, and promoted value (pp. 858, 861).
- Model AATS transition and value valuation explicitly; CQ predicates should inspect `tau`, `pi`, and `delta`, not parse prose strings (pp. 860-862).
- CQ5 succeeds when an alternative joint action reaches the same resulting state (p. 862).
- CQ6 succeeds when an alternative joint action realizes the same goal proposition change (p. 862).
- CQ11 succeeds when the proposed value-promoting action precludes a different joint action that promotes a different value (p. 862), including future/current action conflicts in the worked example (p. 870).
- CQ5-CQ11 objections can themselves be treated as AS1-style alternative arguments and are appropriate inputs to value-based defeat/ranking rather than mere validation errors (p. 859).

## New Leads

- Walton (1996), Argumentation Schemes for Presumptive Reasoning.
- van der Hoek, Roberts, and Wooldridge (2007), "Social laws in alternating time: Effectiveness, feasibility and synthesis."
- Atkinson (2005), "What should we do? Computational representation of persuasive argument in practical reasoning."
