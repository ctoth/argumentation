---
title: "A Game-Theoretic Measure of Argument Strength for Abstract Argumentation"
authors: "Paul-Amaury Matt, Francesca Toni"
year: 2008
venue: "JELIA 2008, LNAI 5293"
doi_url: "https://doi.org/10.1007/978-3-540-87803-2_24"
---

# A Game-Theoretic Measure of Argument Strength for Abstract Argumentation

## One-Sentence Summary
Defines a gradual semantics for abstract argumentation by modeling argument strength as the value of a two-person zero-sum game between a proponent and opponent, computed via linear programming (simplex), yielding a strength in [0,1] that satisfies key monotonicity and sensitivity properties.

## Problem Addressed
Standard Dung-style abstract argumentation classifies arguments as either acceptable or unacceptable (binary), but many applications need a graded notion of strength. Existing gradual semantics lacked game-theoretic foundations and clear formal properties. This paper provides a principled measure based on confronting a proponent (who wants to defend argument x) against an opponent (who wants to defeat it). *(p.1)*

## Key Contributions
- Introduces a two-person zero-sum *game of argumentation strategy* that pits a proponent of an argument against an opponent *(p.1)*
- Defines argument strength as the value of this game, computable via linear programming *(p.6-7)*
- Proves nine formal properties of the strength measure including boundedness, self-confirmation, monotonicity under attack/counter-attack, and insensitivity to irrelevant information *(p.8-11)*
- Provides worked examples on eight different argumentation frameworks showing the strength values and induced orderings *(p.7)*

## Methodology
The paper builds on Dung's abstract argumentation frameworks (AF = (Arg, att)). For a given argument x, a two-person zero-sum game is constructed where:
- The **proponent** may select any subset P containing x, including a non-conflict-free subset. *(Definition 3, printed p.288, `pngs/page-003.png`)*
- The **opponent** may select any subset O of Arg; its strategy set is not restricted to attackers of x or P. *(same source)*
- The **payoff** penalizes non-conflict-free P with 0, rewards unchallenged conflict-free P with 1, and otherwise uses the degree of acceptability. *(Definition 5, printed p.289, `pngs/page-004.png`)*
- The **game value** (computed via minimax/simplex) gives the strength of x *(p.6)*

Admissibility and stability are not restrictions on the strategy sets. They appear in bounds on the resulting game value (Proposition 5). *(printed pp.288,293, `pngs/page-003.png`, `pngs/page-008.png`)*

## Key Equations

### Degree of Acceptability

$$
\phi(P,O)=\frac12\left[1+f(|P\rightarrow O|)-f(|O\rightarrow P|)\right],\qquad f(n)=\frac{n}{n+1}
$$

The paper first permits a monotonically increasing normalization f with f(0)=0 and limit 1, then adopts $n/(n+1)$ for illustrations and part of Proposition 5. The degree is not a ratio of the two raw attack counts. *(Definition 4, printed p.288, `pngs/page-003.png`)*

### Payoff Function

$$
r_F(P,O)=\begin{cases}0&P\text{ is not conflict-free},\\1&P\text{ is conflict-free and }O\text{ does not attack }P,\\\phi(P,O)&\text{otherwise}.\end{cases}
$$

The payoff matrix $R=((r_{i,j}))$ uses this three-case reward, not the degree alone. *(Definition 5, printed p.289, `pngs/page-004.png`)*

### Game Value (Argument Strength) via Linear Programming

$$
s_F(x) = v
$$

Where $v$ is the value of the game, found by maximizing $x_{m+1}$ subject to:

$$
\forall j \in \{1, \ldots, n\} : \sum_{i=1}^{m} r_{i,j} \cdot x_i - x_{m+1} \geq 0
$$

$$
\sum_{i=1}^{m} x_i = 1
$$

$$
x_1, \ldots, x_m, x_{m+1} \geq 0
$$

Where: $m$ = number of proponent strategies, $n$ = number of opponent strategies, $x_i$ = probability of playing strategy $P_i$, $x_{m+1}$ = game value $v$. This is an $(n + m + 2)$ linear inequality system solvable by simplex. *(p.6-7)*

### Proponent Strategy Set

$$
P_F(x)=\{P\subseteq Arg\mid x\in P\}
$$

Every subset containing x is a pure proponent strategy. *(Definition 3, printed p.288, `pngs/page-003.png`)*

### Opponent Strategy Set

$$
O_F=2^{Arg}
$$

The opponent can select any subset, including the empty subset; its pure strategy set does not depend on P. *(Definition 3, printed p.288, `pngs/page-003.png`)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Argument strength | $s_F(x)$ | - | - | [0, 1] | p.7 | Value of the (F,x) game |
| Degree of acceptability | $\phi(P,O)$ | - | 0.5 (when no attacks) | [0, 1] | p.4 | Half of 1 plus normalized outgoing minus incoming attack count |
| Payoff matrix entry | $r_{i,j}$ | - | - | [0, 1] | p.5 | Three-case reward of Definition 5 |
| Number of proponent strategies | $m$ | - | - | $\geq 1$ | p.7 | Size of $P_F(x)$ |
| Number of opponent strategies | $n$ | - | - | $2^{|Arg|}$ | p.4 | Size of the full powerset $O_F$ |
| Strategy probability | $x_i$ | - | - | [0, 1] | p.7 | Probability of proponent playing $P_i$ |
| Game value | $v$ ($x_{m+1}$) | - | - | [0, 1] | p.7 | Maximized by simplex |

## Implementation Details
- The game is a two-person zero-sum game; standard LP solvers (simplex) apply directly *(p.6-7)*
- Pure strategies are all subsets containing x for the proponent and all subsets for the opponent; non-conflict-free proponent plays receive zero reward. *(Definitions 3,5, printed pp.288-289, `pngs/page-003.png`, `pngs/page-004.png`)*
- An unattacked argument has strength 1 because the proponent can play {x} and receive 1 against every opponent, not because the opponent lacks strategies. *(Proposition 4, printed pp.292-293, `pngs/page-007.png`, `pngs/page-008.png`)*
- Strength is 0 exactly for a self-attacking argument. A one-way attack a→b gives b strength 0.25, not 0. *(Proposition 3 and Table 1, printed pp.291-292, `pngs/page-006.png`, `pngs/page-007.png`)*
- Mixed strategies are essential — the proponent and opponent may randomize over multiple opinions *(p.6)*
- The value $v$ can be shown to be *a priori* positive by the game-theoretic structure; the LP always has a feasible solution *(p.6-7)*
- Computation reduces to solving one LP per argument per framework *(p.7)*

## Figures of Interest
- **Fig 1 (p.2):** Simple abstract argumentation framework with 6 arguments {a,b,c,d,e,f} showing attack structure used as running example
- **Fig 2 (p.7):** Same framework F8 annotated with computed strength values: a=0.5, b=0.5, c=0.417, d=0.5, e=0.25, f=1.0 — demonstrating the ranking f > a = b = d > c > e

## Results Summary
- Table 1 (p.7) provides strength values and orderings for 8 frameworks (F1-F8):
  - F1: single unattacked argument, strength = 1
  - F2: {a,b} with a attacks b only, strengths 1 and 0.25 (a > b)
  - F3: mutual attack {a,b}, both get 0.5 (a = b)
  - F4-F8: increasingly complex, showing nuanced orderings
- For F8 (the running example from Fig 1): f > a = b = d > c > e *(p.7)*
- The proponent's optimal mixed strategy for argument a in F8 is to play {a, f} *(p.7)*

## Limitations
- Strategy sets $P_F(x)$ and $O_F^x$ may be exponentially large; enumeration is the bottleneck *(p.6)*
- The degree of acceptability function $d(P,O)$ treats all attacks as equally weighted — no support for weighted or preference-based attacks *(p.4)*
- Authors acknowledge that some properties of dialectical viability and stability are not yet established for this measure *(p.11)*
- The paper produces only a ranking, not absolute calibrated probabilities — two arguments with the same strength may have very different dialectical structure *(p.7)*
- Counter-intuitive results possible: in some cases one might expect stronger differentiation between arguments that the measure treats as equal *(p.8)*

## Arguments Against Prior Work
- Binary (extension-based) semantics force a harsh acceptable/not-acceptable dichotomy that discards gradation information *(p.1)*
- Prior gradual semantics (Cayrol & Lagasquie-Schiex 2005, Besnard & Hunter 2001) do not have game-theoretic foundations, making it harder to justify the particular strength function chosen *(p.11)*
- The "interaction-based" measures (Cayrol & Lagasquie-Schiex 2005) and "categoriser" function treat attacks and supports differently from game-theoretic equilibrium reasoning *(p.11)*
- Extension-based approaches do not naturally quantify "how strong" an argument is within an extension — they only determine membership *(p.1)*

## Design Rationale
- Game theory provides a principled foundation because argument strength is fundamentally about adversarial confrontation — how well can the argument survive the best possible attack? *(p.1-2)*
- Two-person zero-sum games are chosen because the proponent's gain is exactly the opponent's loss — there is no cooperation in argumentation disputes *(p.6)*
- Mixed strategies are necessary because in many frameworks neither proponent nor opponent has a single dominant pure strategy *(p.6)*
- The simplex algorithm is chosen for computation because the game value is always positive (a priori), enabling direct LP formulation *(p.7)*
- All subsets containing the topic are available to the proponent; conflict-freeness is encouraged by the reward, while admissibility yields strength bounds rather than a strategy restriction. *(Definitions 3,5 and Proposition 5, printed pp.288-289,293, `pngs/page-003.png`, `pngs/page-004.png`, `pngs/page-008.png`)*

## Testable Properties
- **Boundedness (Prop 2):** For all arguments x in AF, $0 \leq s_F(x) \leq 1$ *(p.8)*
- **Self-contradiction (Prop 3):** $s_F(x)=0$ iff x attacks itself. *(printed p.292, `pngs/page-007.png`)*
- **Unattacked = strongest (Prop 4):** If x has no attackers, $s_F(x) = 1$ *(p.8)*
- **Acceptable-argument bound (Prop 5):** If x belongs to an admissible (or stable) set, $s_F(x)\ge\frac12[1+\frac12-\frac{k}{k+1}]$, where k is the maximum out-degree and $f(n)=n/(n+1)$. If n attacks target x, $s_F(x)\le1-\frac12f(n)$. *(printed p.293, `pngs/page-008.png`)*
- **Criticism reduces strength (Prop 6):** Adding an attack (a,b) gives $s_{F+(a,b)}(b)\le s_F(b)$; strict decrease is not asserted. *(printed p.293, `pngs/page-008.png`)*
- **Cautious extra-aggressiveness (Prop 7):** Adding (a,b) weakly increases a's strength if b is superfluous with respect to a, and weakly decreases it otherwise. Superfluous means forbidding proponent strategies containing b does not decrease the game value. *(Definition 7, printed p.294, `pngs/page-009.png`)*
- **Indirect counter-attack (Prop 8):** If b attacks x, adding (a,b) weakly increases x's strength. *(printed p.294, `pngs/page-009.png`)*
- **Insensitivity to irrelevant info (Prop 9):** Adding arguments and attacks disconnected from x does not change $s_F(x)$ *(p.10-11)*
- **Symmetry in mutual attack:** Two arguments that mutually attack each other with no other connections both get strength 0.5 (Table 1, F3) *(p.7)*

## Relevance to Project
This paper provides a principled gradual semantics for abstract argumentation frameworks. For propstore's argumentation layer (Layer 4), this game-theoretic strength measure offers a way to quantify how strong each argument is in a Dung AF — going beyond binary extension membership. It could be used to rank competing claims by their dialectical strength, supporting the render layer's need for graded resolution strategies. The LP-based computation is straightforward to implement and the formal properties (monotonicity, sensitivity to attacks/counter-attacks) align with intuitive requirements for argument ranking.

## Open Questions
- [ ] How does this scale for large AFs with many admissible sets? Strategy enumeration is exponential.
- [ ] Can the degree of acceptability d(P,O) be extended to handle weighted attacks or preference orderings (as in ASPIC+)?
- [ ] How does this measure compare empirically to the categoriser function of Besnard & Hunter or the h-categoriser of Pu et al.?
- [ ] Is there a polynomial approximation for the game value when strategy sets are too large to enumerate?

## Related Work Worth Reading
- Cayrol, C., Lagasquie-Schiex, M.-C.: Graduality in Argumentation (JAIR 2005) — alternative gradual semantics based on interaction
- Besnard, P., Hunter, A.: A logic-based theory of deductive arguments (AIJ 2001) — structured argumentation with strength
- Dunne, M.: The Mathematics of Games of Strategy (Dover 1960) — game theory foundations used here
- Amgoud, L., Ben-Naim, J.: Argumentation-based ranking semantics — later work building on gradual approaches
- Baroni, P., Giacomin, M.: Semantics of abstract argument systems (Ch. 2, 2009) — broader survey of semantics
- Rahwan, I., Larson, K.: Mechanism Design for Abstract Argumentation (AAMAS 2008) — game-theoretic mechanisms in argumentation
- Pollock, J.L.: How to reason defeasibly (AIJ 1992) — defeasible reasoning foundations

## Collection Cross-References

### Already in Collection
- [[Dung_1995_AcceptabilityArguments]] — foundational AF = (Arg, att) definition on which this entire paper builds
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — cited as extending Dung with support relations; Matt & Toni's gradual approach provides an alternative to Cayrol's bipolar extensions
- [[Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation]] — SCC-recursiveness and evaluation of argumentation semantics; provides the decomposition structure this paper's game operates over
- [[Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation]] — principle-based evaluation of extension semantics; Matt & Toni's properties (Prop 2-9) serve an analogous role for gradual semantics
- [[Pollock_1987_DefeasibleReasoning]] — defeasible reasoning foundations; Pollock 1992 (cited) builds on this
- [[Besnard_2001_Logic-basedTheoryDeductiveArguments]] — logic-based deductive arguments; origin of the Categoriser function that is an alternative strength measure

### New Leads (Not Yet in Collection)
- Rahwan & Larson (2008) — "Mechanism Design for Abstract Argumentation" — another game-theoretic approach to argumentation but focused on incentive compatibility rather than strength measurement
- Coste-Marquis et al. (2006) — "Weighted attacks in argumentation frameworks" — weighted attacks provide an alternative parameterization of argument strength

### Cited By (in Collection)
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — directly compares Matt & Toni semantics against 16 axiomatic properties alongside four other ranking semantics; finds M&T satisfies Abs, VP+, DP, SCT, TAB, TDB, +AB, Ext, Ind, Null but not CT, CP, DDP, QP

### Conceptual Links (not citation-based)
- [[Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks]] — proposes the axiomatic postulate framework that Bonzon 2016 later uses to evaluate Matt & Toni's semantics; Amgoud's Burden-based and Discussion-based semantics are direct competitors to the game-theoretic approach, solving the same problem (gradual argument ranking) from an axiomatic rather than game-theoretic foundation
- [[Hunter_2017_ProbabilisticReasoningAbstractArgumentation]] — addresses argument strength from a probabilistic rather than game-theoretic perspective; both provide continuous [0,1] strength values for arguments in Dung AFs but with different interpretations (probability of acceptability vs. game value)
- [[Li_2011_ProbabilisticArgumentationFrameworks]] — another approach to graded argument assessment using probability distributions over sub-frameworks; complements the game-theoretic approach with a Bayesian perspective
