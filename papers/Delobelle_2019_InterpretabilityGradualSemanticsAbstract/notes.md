---
title: "Interpretability of Gradual Semantics in Abstract Argumentation"
authors: "Jérôme Delobelle, Serena Villata"
year: 2019
venue: "ECSQARU 2019 - 15th European Conference on Symbolic and Quantitative Approaches to Reasoning with Uncertainty (Belgrade, Serbia)"
doi_url: "https://doi.org/10.1007/978-3-030-29765-7_3"
pages: "27-38"
affiliation: "Université Côte d'Azur, Inria, CNRS, I3S, Sophia-Antipolis, France"
funding: "DGA RAPID CONFIRMA"
---

# Interpretability of Gradual Semantics in Abstract Argumentation

## One-Sentence Summary
Defines a deletion-based *impact measure* and a *Balanced Impact (BI)* property for gradual semantics in abstract argumentation: when BI holds, an argument's acceptability degree decomposes additively into per-argument impacts, yielding interpretability via per-argument rankings of most positive/negative impacting arguments.

## Problem Addressed
Gradual semantics map AFs to acceptability degrees in [0,1], but provide no method to *explain* why an argument has its score, i.e., which other arguments most contributed (positively or negatively). Existing axiomatic evaluations (Killing, Weakening) cannot distinguish how strongly a semantics weakens via attacks. Sub-question (i): how to formally define and characterise the impact of an argument on others? (ii) how does this impact play a role in interpretation of acceptability? *(p.2)*

## Key Contributions
- (C1) Definition of impact of a non-attacked set on an argument via deletion / complement operator (Def. 7) *(p.4)*.
- (C2) Generalised impact (Def. 8) for arbitrary sets, by first removing direct attackers of X to evaluate X "at its strongest" *(p.5)*.
- (C3) Bounds: Imp ∈ [-1, 1] (Prop. 1) *(p.5)*.
- (C4) Balanced Impact property (BI) (Property 1): impacts of singletons sum to impact of the union *(p.7)*.
- (C5) Counting Semantics satisfies BI (Prop. 2); h-categorizer does NOT (Prop. 3) *(p.7)*.
- (C6) Decomposition theorem under BI for acyclic AFs: Deg(y) = 1 + Σ_x Imp({x}, y) (Def. 10) *(p.7)*.
- (C7) ACY transformation algorithm — unfolds a cyclic AF into an infinite acyclic AF rooted at a target argument so the decomposition extends to cyclic AFs (Algorithm 1, Def. 11) *(p.8-9)*.
- (C8) Impact ranking (Def. 12) and most-positive / most-negative impacting arguments (Def. 13) for interpretability and debate strategy *(p.9)*.

## Preliminaries (Section 2)
- **Def. 1 (AF)**: F = ⟨A, R⟩ with A finite non-empty arguments, R ⊆ A×A attack relation; xRy means x attacks y *(p.2)*.
- **Def. 2 (Non-attacked set)**: X ⊆ A is non-attacked iff ∀x∈X, ∄y∈A\X s.t. (y,x)∈R *(p.3)*.
- **Notation 1**: Path P(y,x) = ⟨x_0,...,x_n⟩ with x_0=x, x_n=y, (x_{i+1},x_i)∈R; length l_P=n; cycle = path from x to x; loop = cycle of length 1. R⁻_n(x) = multiset {y | ∃P(y,x) with l_P=n}. Direct attacker if n=1; direct defender if n=2; attacker if n odd; defender if n even *(p.3)*.
- **Def. 3 (Gradual semantics)**: function S that assigns Deg^S_F : A → [0,1] *(p.3)*.
- **Def. 4 (h-categorizer / Cat)** *(p.3)*: Deg^Cat_F(x) = 1 if R⁻_1(x)=∅ else 1 / (1 + Σ_{y∈R⁻_1(x)} Deg^Cat_F(y)). Range ]0,1].
- **Def. 5 (Counting model / CS)** *(p.4)*: v^k_α = Σ_{i=0..k} (-1)^i α^i M̃^i I where M̃ = M/N (M adjacency, N normalisation factor like matrix infinite norm), I the n-vector of ones, α ∈ ]0,1[ damping factor; v_α = lim_{k→∞} v^k_α; Deg^CS_F(x_i) is the i-th component.

## Methodology
Deletion-based impact: compare Deg^S_F(y) vs Deg^S_F(y) when set X is removed (via complement operator). Generalisation handles attacked X by first removing direct attackers of X (so X is "as strong as possible").

## Key Equations

Counting model:
$$
v^k_\alpha = \sum_{i=0}^{k} (-1)^i \alpha^i \tilde{M}^i \mathcal{I}
$$
M̃ = M/N normalised adjacency matrix; α∈]0,1[ damping factor; I n-vector of ones; k iteration step. Deg^CS_F(x_i) = i-th component of lim_{k→∞} v^k_α. *(p.4)*

h-categorizer:
$$
\text{Deg}^{Cat}_F(x) = \begin{cases} 1 & \text{if } \mathcal{R}^-_1(x)=\emptyset \\ \dfrac{1}{1+\sum_{y\in \mathcal{R}^-_1(x)} \text{Deg}^{Cat}_F(y)} & \text{otherwise} \end{cases}
$$
*(p.3)*

Complement operator (Def. 6): F ⊖_y X = ⟨A', R'⟩ with A' = A\(X\{y}), R' = {(x,z) ∈ R | x ∈ A\X ∧ z ∈ A\X}. *(p.4)*

Impact of a non-attacked set (Def. 7):
$$
\text{Imp}^S_F(X, y) = \text{Deg}^S_F(y) - \text{Deg}^S_{F\ominus_y X}(y)
$$
*(p.4)*

Implicit decomposition (motivation, generic): Deg^S_F(y) = 1 + Imp^S_F(A, y) — running example: Deg^CS_F(a) = 1 + (Deg^CS_F(a) − Deg^CS_{F⊖_a A}(a)) = 1 − 0.7309 = 0.2691 *(p.4)*.

General impact (Def. 8) — handles attacked X by neutralising X's attackers first:
$$
\text{Imp}^S_F(X, y) = \text{Deg}^S_{F\ominus_y(\bigcup_{x\in X}\mathcal{R}^-_1(x))}(y) - \text{Deg}^S_{F\ominus_y X}(y)
$$
*(p.5)*. Reduces to Def. 7 when X is non-attacked.

**Proposition 1**: Imp^S_F(X, y) ∈ [−1, 1] *(p.5)*.

**Def. 9 (positive/negative/neutral impact)** *(p.6)*: X has positive impact on y iff Imp>0; negative iff Imp<0; neutral iff Imp=0.

**Notation 2** *(p.6)*: I^+_S(y) = {x∈A | {x} has positive impact on y}; I^-_S(y) negative; I^=_S(y) neutral.

**Property 1 (Balanced Impact, BI)** *(p.7)*: A semantics S satisfies BI iff for any F=⟨A,R⟩ and x,y,z∈A:
$$
\text{Imp}^S_F(\{x\}, y) + \text{Imp}^S_F(\{z\}, y) = \text{Imp}^S_F(\{x,z\}, y)
$$

**Proposition 2**: Counting semantics satisfies BI *(p.7)*.
**Proposition 3**: h-categorizer does NOT satisfy BI *(p.7)*. (Fig. 2: separate impacts {b}/{c} on a are −0.5 each (sum −1) but joint impact of {b,c} is −0.667.)

**Definition 10 (Decomposition for acyclic AFs)** *(p.7)*: Under BI, for acyclic F:
$$
\text{Deg}^S_F(y) = 1 + \sum_{x\in\mathcal{A}} \text{Imp}^S_F(\{x\}, y)
$$

**Algorithm 1 (ACY)** *(p.8)*: BFS-style unfolding of a cyclic AF into an infinite acyclic AF rooted at the targeted argument x_1.
- Data: F=⟨A={x_1,...,x_n}, R⟩; target x_1∈A.
- Result: F' = ⟨A', R'⟩ infinite acyclic.
- Init: C = {x_1}; A' = {x_1^0}; R' = ∅. (x_1^0 is the universal sink vertex.)
- For every x_i in C:
  - C ← C \ {x_i}
  - m_1 ← max value of m among x_i^m ∈ A'
  - For every x_j in R⁻_1(x_i):
    - C ← C ∪ {x_j}
    - if x_j^0 ∉ A' then A' ← A' ∪ x_j^0; R' ← R' ∪ (x_j^0, x_i^{m_1})
    - else m_2 ← (max m among x_j^m ∈ A') + 1; A' ← A' ∪ x_j^{m_2}; R' ← R' ∪ (x_j^{m_2}, x_i^{m_1})

Footnote 1 *(p.8)*: scores computed via fixed-point; if the gradual-semantics function converges, the iteration count for convergence can also bound the maximal depth of the tree.

**Definition 11** *(p.8-9)*: Let F'=ACY_y(F), X = {x^0, x^1, ...} the sub-arguments of x in F'. Under BI, the impact of x on y is 0 if X=∅, otherwise:
$$
\text{Imp}^S_F(\{x\}, y) = \sum_{x^i \in \mathcal{X}} \text{Imp}^S_{F'}(\{x^i\}, y^0)
$$
This new impact then plugs into Def. 10 to compute Deg^S_F(y) in cyclic AFs.

**Definition 12 (Impact ranking)** *(p.9)*: x ⪰^S_y z iff Imp^S_F({x}, y) ≥ Imp^S_F({z}, y).

**Definition 13 (Most positive / negative impacting arguments)** *(p.9)*:
$$
PI^S_F(y) = \arg\max_{x \in I^+_S(y)} |\{z \in I^+_S(y) \mid x \succeq^S_y z\}|
$$
$$
NI^S_F(y) = \arg\max_{x \in I^-_S(y)} |\{z \in I^-_S(y) \mid z \succeq^S_y x\}|
$$
(I.e., the singletons with the highest positive / lowest negative impact rank, by counting how many other positively/negatively-impacting arguments they dominate.)

## Worked Examples
- **Example 1** *(p.6)*: AF in Fig. 1, CS (α=0.98). Imp^CS_F({e},a) = 0.4906 − 0.25530 = 0.2353. Imp^CS_F({a},a)=0; Imp^CS_F({b},a)=Imp^CS_F({d},a)=−0.49; Imp^CS_F({c},a)=0.2353; Imp^CS_F({f},a)=Imp^CS_F({g},a)=−0.1108. So I^+_CS(a)={c,e}, I^-_CS(a)={b,d,f,g}, I^=_CS(a)={a}.
- **Example 2** *(p.7)*: under BI, Deg^CS_F(a) = 1 + (0 − 0.49 + 0.2353 − 0.49 + 0.2353 − 0.1108 − 0.1108) = 0.2691.
- **Example 3** *(p.9)*: For Fig. 3 cyclic AF (b↔a, c→a), via ACY: Imp^CS_F({b},a) = Σ Imp^CS_{ACY_a(F)}({b^i}, a^0) ≃ −0.63. Also Imp^CS_F({c},a) ≃ −0.63 and Imp^CS_F({a},a) ≃ 0.3. Then Deg^CS_F(a) ≃ 0.04 = 1 + 0.3 − 0.63 − 0.63.
- **Example 4** *(p.9)*: For AF in Fig. 1 with CS, the impact ranking on a is c ≃ e ≻ a ≻ f ≃ g ≻ b ≃ d. Hence PI^CS_F(a) = {c, e}, NI^CS_F(a) = {b, d}.

## Figures of Interest
- **Fig. 1 (p.5)**: 7-argument AF (a,b,c,d,e,f,g); table compares Imp^S_F(X,a) for CS vs Cat across 5 sets (A, {e,f,g}, {b,c}, {f,g}, {c}). Demonstrates impacts can have opposite signs depending on semantics.
- **Fig. 2 (p.7)**: Three small AFs F1 (b→a), F2 (c→a), F3 (b→a, c→a) used to prove h-categorizer fails BI; counting semantics satisfies it.
- **Fig. 3 (p.8)**: Example cyclic AF (b↔a, c→a) transformed via ACY into infinite tree rooted at a^0 with children b^0, c^0; b^0 has child a^1, etc.

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Damping factor (Counting) | α | — | 0.98 (running ex.) | ]0,1[ | 4,5 | Down-weights longer attacker/defender chains |
| Acceptability degree | Deg^S_F(x) | — | — | [0,1] (h-cat ]0,1]) | 3 | Output of gradual semantics |
| Impact | Imp^S_F(X,y) | — | — | [−1,1] | 5 | Prop. 1 |
| Path length n (R⁻_n) | n | — | — | n≥1 | 3 | n=1 direct attacker; n=2 direct defender; odd attacker, even defender |
| Adjacency matrix | M | — | — | n×n binary | 3 | Adjacency of AF as digraph |
| Normalisation factor | N | — | matrix infinite norm | — | 3 | M̃ = M/N |
| Loop length | — | — | 1 | — | 3 | A loop is a cycle of length 1 |
| ACY tree depth | — | iterations | convergence-iter count | finite if S converges | 8 (footnote) | Max depth of ACY tree bounded by gradual-semantics fixed-point iterations |

## Methods & Implementation Details
- **Complement operator** (Def. 6) *(p.4)*: deletes X\{y} from A and removes attacks involving any removed node, preserving target y.
- **Impact (non-attacked X)** (Def. 7) *(p.4)*: Deg(y) − Deg(y in F⊖_y X).
- **Generalised impact** (Def. 8) *(p.5)*: pre-step that removes direct attackers of X, then takes the difference. Captures "X at its strongest".
- **ACY transformation** (Algorithm 1) *(p.8)*: BFS unfolding rooted at the target argument; each layer alternates attackers/defenders. Infinite in general; depth bounded in practice by the gradual-semantics convergence iteration count (footnote 1).
- **Decomposition** (Def. 10/11) *(p.7-9)*: under BI, Deg(y) = 1 + Σ_x Imp({x}, y) for acyclic AFs; for cyclic AFs use Def. 11 over ACY-transformed F'.
- **Impact ranking + interpretability** (Defs. 12-13) *(p.9)*: produces argument rankings; PI/NI sets identify the best targets when defending or attacking a position.
- **Application** *(p.5)*: AFs of online debates often have tree-shaped sub-debate structure; Imp on a sub-tree (e.g., environmental, health, psychological for vegan diet) measures sub-debate influence on the topic argument.

## Testable Properties
- Imp^S_F(X, y) ∈ [−1, 1] for any S, F, X, y *(p.5)*.
- For non-attacked X, Def. 8 reduces to Def. 7 *(p.5)*.
- Counting Semantics satisfies BI *(p.7)*.
- h-categorizer does NOT satisfy BI (Fig. 2 counterexample) *(p.7)*.
- For BI semantics on acyclic AFs: Deg(y) = 1 + Σ_x Imp({x}, y) *(p.7)*.
- For BI semantics on cyclic AFs (via ACY unfolding): Imp^S_F({x}, y) = Σ_{x^i∈X} Imp^S_{F'}({x^i}, y^0) *(p.9)*.
- The single-argument Imp values satisfy a pre-order (impact ranking) compatible with a numeric ordering on [−1,1] *(p.9)*.

## Design Rationale
- **Deletion-based impact** captures the natural "what changes if this argument were absent?" intuition, matching Miller's [13] notion of interpretability *(p.1-2,4)*.
- **Neutralise X's attackers (Def. 8)**: deleting an attacked X conflates its impact with side-effects from neighbouring nodes; pre-removing direct attackers measures X "at its strongest" *(p.5)*.
- **BI motivation**: existing axioms (Killing, Weakening, [1]) only label whether attacks weaken; BI captures *how much* and enables additive decomposition into per-argument contributions *(p.6)*.
- **ACY for cycles**: deletion in a cycle removes the contribution of all cycle members; unfolding to an infinite tree preserves per-argument contributions; in practice the tree is bounded by the underlying semantics' convergence depth *(p.8 footnote 1)*.
- **Two semantics chosen** specifically because they have *different features* (h-categorizer is recursive over attackers; CS is matrix-power based) — this lets the authors show that BI is a discriminating axiom *(p.2)*.

## Limitations / Open Questions
- Decomposition theorem proven only for acyclic AFs in Def. 10; cyclic AFs need ACY unfolding (Def. 11), which produces an infinite tree (depth bounded only by convergence iterations) *(p.7-8)*.
- Only two gradual semantics analysed (Cat, CS). h-categorizer does not satisfy BI, so additive decomposition does not apply to it *(p.7)*.
- Support relation [8] (bipolar AFs) not handled — listed as future work *(p.10)*.
- Extension to other gradual semantics in the literature for full coverage of the BI vs. non-BI landscape — listed as future work *(p.10)*.

## Arguments Against Prior Work
- Existing axiomatic evaluations (Amgoud & Ben-Naim's Killing/Weakening properties [1]) cannot distinguish *degree* of weakening between two semantics that both satisfy "weakening" *(p.6)*.
- Standard Dung semantics [10] only labels arguments as accepted/rejected, no per-argument explanatory granularity *(p.2)*.
- Amgoud et al. [2] introduced contribution measures via Shapley values, but only for syntax-independent + monotonic semantics (e.g., h-categorizer), and only measures contributions of *direct* attacks rather than all arguments — this paper handles all arguments and a wider class of semantics *(p.10)*.
- Fan & Toni [11,12] explanations exist for extension-based admissible semantics, but extension- vs gradual-semantics differ fundamentally (see Bonzon et al. [7]) so their interpretability work doesn't transfer *(p.10)*.

## Application: Interpretability for Online Debates and Strategy
- *(p.5)*: AFs of online debates are often tree-shaped with sub-debates (e.g., environmental/health/psychological for vegan diet). Sub-tree impact = sub-debate's influence on the topic.
- *(p.9)*: Impact ranking + PI/NI lets a debate participant who wants to *defend* a point of view find arguments with the most *negative* impact on it and target counter-arguments at them.

## Conclusion (paraphrased)
A formal interpretability framework for gradual semantics built around the impact measure; works for cyclic and acyclic AFs; the impact-of-arguments ranking explains the rationale behind a gradual-semantics result and informs strategic choices in debate. Future work: support relation (bipolar AFs); other gradual semantics. *(p.10)*

## Relevance to Project (argumentation library)
- **Direct fit for our gradual-semantics work**: if/when we implement the Counting Semantics or any BI-satisfying weighted gradual semantics, we get an additive interpretability story for free via Def. 10 / Def. 11.
- **Useful negative result**: h-categorizer fails BI, so per-argument additive decomposition is unsound for it — a concrete property to test (see "Testable Properties" above) and a constraint to surface to library users that pick h-cat.
- **ACY unfolding** is a concrete algorithm we could implement to extend any acyclic-AF technique to cyclic AFs, with a principled depth bound from the underlying semantics' convergence iteration count.
- **Related anchors**: this paper is the foundation for Al Anaissy/Delobelle/Vesic/Yun (2024) *Impact Measures for Gradual Argumentation Semantics* which generalises the impact measure and adds Shapley-value-based variants — relevant for the QBAF/contribution-function workstream (Wave 1 task #2/#3).

## Related Work Worth Reading
- [2] Amgoud, Ben-Naim, Vesic — Shapley contribution measure for attack intensity (IJCAI 2017).
- [4] Baroni, Rago, Toni — fine-grained / broad principles spectrum for gradual argumentation (Int. J. Approx. Reasoning 2019).
- [6] Bonzon, Delobelle, Konieczny, Maudet — comparative study of ranking-based semantics (AAAI 2016).
- [7] Bonzon et al. — combining extension-based and ranking-based semantics (KR 2018).
- [8] Cayrol, Lagasquie-Schiex — bipolarity in argumentation graphs (already on Wave 1 list).
- [13] Miller — Explanation in AI: insights from social sciences (AIJ 2019).
- [16] Pu et al. — counting semantics (CogSci 2015), the underlying CS used here.
