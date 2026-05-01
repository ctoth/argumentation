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
- The **proponent** selects an opinion (set of arguments) P containing x from a set of conflict-free sets that defend x *(p.4)*
- The **opponent** selects an opinion O from sets of arguments that attack x or attack arguments in P *(p.4)*
- The **payoff** to the proponent is a degree of acceptability measuring how well P defends against O *(p.4)*
- The **game value** (computed via minimax/simplex) gives the strength of x *(p.6)*

The proponent's strategy set consists of admissible (or stable) sets containing x. The opponent's strategy set consists of sets formed from attacks directed from P to O and from O to P, within the abstract argumentation framework. *(p.4)*

## Key Equations

### Degree of Acceptability

$$
d(P, O) = \frac{|P \rightarrow O|}{|P \rightarrow O| + |O \rightarrow P|}
$$

Where: $P \rightarrow O$ denotes the set of attacks from $P$ against $O$, and $O \rightarrow P$ the set of attacks from $O$ against $P$. If both are empty, $d(P, O) = 0.5$ (draw). *(p.4)*

### Payoff Function

$$
r_F(P_i, O_j) = d(P_i, O_j)
$$

Where: $P_i$ is the proponent's $i$-th strategy, $O_j$ is the opponent's $j$-th strategy. The payoff matrix $R = ((r_{i,j}))$ is used to define the game. *(p.4)*

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
P_F(x) = \{ S \subseteq Arg \mid x \in S, S \text{ is conflict-free and } \forall a \in S, \text{ if } \exists b \text{ s.t. } (b,a) \in att, \text{ then } \exists c \in S \text{ s.t. } (c,b) \in att \} \}
$$

Where: $P_F(x)$ is the set of admissible sets containing $x$. *(p.4)*

### Opponent Strategy Set

$$
O_F^x(P) = \{ O \subseteq Arg \mid \forall o \in O, \exists p \in P \text{ s.t. } (o,p) \in att \text{ or } (p,o) \in att \}
$$

Where: $O_F^x$ is derived from the union of all opponent strategies across all proponent plays. The opponent can select from sets of arguments that attack or are attacked by proponent arguments. *(p.4)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Argument strength | $s_F(x)$ | - | - | [0, 1] | p.7 | Value of the (F,x) game |
| Degree of acceptability | $d(P,O)$ | - | 0.5 (when no attacks) | [0, 1] | p.4 | Ratio of attacks P->O to total |
| Payoff matrix entry | $r_{i,j}$ | - | - | [0, 1] | p.4 | $r_F(P_i, O_j) = d(P_i, O_j)$ |
| Number of proponent strategies | $m$ | - | - | $\geq 1$ | p.7 | Size of $P_F(x)$ |
| Number of opponent strategies | $n$ | - | - | $\geq 0$ | p.7 | Size of $O_F^x$ |
| Strategy probability | $x_i$ | - | - | [0, 1] | p.7 | Probability of proponent playing $P_i$ |
| Game value | $v$ ($x_{m+1}$) | - | - | [0, 1] | p.7 | Maximized by simplex |

## Implementation Details
- The game is a two-person zero-sum game; standard LP solvers (simplex) apply directly *(p.6-7)*
- Proponent strategies: enumerate all admissible (or stable) sets containing x. Sets $P_F(x)$ and $O_F^x$ may be arbitrarily large, so exact computation may be expensive *(p.6)*
- When no opponent strategies exist (argument is unattacked), strength = 1 *(p.8)*
- When argument is attacked by an unattacked argument and has no defense, strength = 0 *(p.8)*
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
- Admissible sets (not just conflict-free sets) are used for proponent strategies to ensure self-defense — this connects to Dung's fundamental lemma *(p.4)*

## Testable Properties
- **Boundedness (Prop 2):** For all arguments x in AF, $0 \leq s_F(x) \leq 1$ *(p.8)*
- **Self-confirmation (Prop 3):** $s_F(x) = 0$ if and only if x is attacked by some argument that is not itself attacked (i.e., attacked by an unattacked argument with no counter) *(p.8)*
- **Unattacked = strongest (Prop 4):** If x has no attackers, $s_F(x) = 1$ *(p.8)*
- **Criticism reduces strength (Prop 5):** Adding a new attack on x (in a non-superfluous way) reduces $s_F(x)$ *(p.9)*
- **Strict monotonicity (Prop 6):** Adding an attack strictly reduces strength unless the attack is superfluous (Def 7) *(p.9-10)*
- **Counter-extra-aggressiveness (Prop 7):** Adding an attack on an attacker of x increases $s_F(x)$ (counter-attack helps) *(p.10)*
- **Indirect counter-support (Prop 8):** If F' adds an attack on an attacker of x's defender, then $s_F'(x) \geq s_F(x)$ *(p.10)*
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
