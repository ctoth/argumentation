---
title: "Contribution Functions for Quantitative Bipolar Argumentation Graphs: A Principle-based Analysis"
authors: "Timotheus Kampik, Nico Potyka, Xiang Yin, Kristijonas Čyras, Francesca Toni"
year: 2024
venue: "arXiv preprint (cs.AI), 2401.08879v2"
doi_url: "https://arxiv.org/abs/2401.08879"
pages: 51
---

# Contribution Functions for Quantitative Bipolar Argumentation Graphs: A Principle-based Analysis

## One-Sentence Summary
Defines four contribution functions (Removal, Removal-without-indirection, Shapley, Gradient) that quantify how one argument influences another's final strength in an acyclic Quantitative Bipolar Argumentation Graph (QBAG), introduces five principles (Contribution Existence, Quantitative Contribution Existence, Directionality, (Quantitative) Local Faithfulness, (Quantitative) Counterfactuality) and shows under five well-known QBAG semantics (QE, DFQuAD, SD-DFQuAD, EB, EBT) which functions satisfy which principles — none satisfies them all, motivating use-case-driven choice.

## Problem Addressed
Explainable AI applications of QBAGs (recommenders, review aggregation, neural-network surrogates, random forests) need a rigorous notion of "how much does argument x influence argument a's final strength?" Prior work (workshop paper [13], gradual-arg-attribution paper [19]) sketched contribution functions but lacked a comprehensive principle-based analysis. This paper closes that gap for the acyclic case. *(p.2)*

## Key Contributions
- Four formally-defined contribution functions: $\mathsf{Ctrb}^\mathcal{R}$ (removal), $\mathsf{Ctrb}^{\mathcal{R}'}$ (removal without indirection / intrinsic removal), $\mathsf{Ctrb}^\mathcal{S}$ (Shapley value), $\mathsf{Ctrb}^\partial$ (gradient). *(p.2-3, p.9-11)*
- Five contribution-function principles: Contribution Existence (4.1), Quantitative Contribution Existence (4.2), Directionality (4.3), (Quantitative) Local Faithfulness (4.5/4.6), (Quantitative) Counterfactuality (4.7/4.8). *(p.13-19)*
- Principle-satisfaction analysis across 5×4 (semantics × function) grid summarized in Table 1; complete proofs in Section 5 with explicit counterexample QBAGs. *(p.6, p.20-32)*
- Side results / conjectures (Section 6): Shapley sum identity equals σ(a)-τ(a); independence of irrelevant alternatives; conjectures on stability classes. *(p.32-?)*
- Application example: explanation in clinical-decision-style recommender. *(later sections)*
- Comprehensive related work + roadmap for cyclic-graph extension.

## Methodology
Formal/theoretical: defines QBAGs, gradual semantics in modular form (aggregation × influence), contribution functions, principles. Establishes principle satisfaction via direct proofs and refutes via constructed counterexample QBAGs. Restricts attention to acyclic QBAGs because (a) common application graphs are hierarchical/temporal and acyclic, (b) cycles cause non-convergence issues that obscure the principal points.

## Section Map
- §1 Introduction — motivation, Example 1.1 (4-arg QBAG with conflicting counterfactuality vs faithfulness)
- §2 Preliminaries — Defs 2.1 (QBAG), 2.2 (gradual semantics, modular semantics), Table 2 (aggregation: Sum/Product/Top), Table 3 (semantics: QE, DFQuAD, SD-DFQuAD, EB, EBT), Principles 2.1 (Directionality), 2.2 (Stability)
- §3 Argument Contributions — definitions of the four contribution functions (Eqs 1-5), Observation 3.1, Example 3.1, Table 4
- §4 Principles — Principles 4.1-4.8; Propositions 4.1-4.x relating principles
- §5 Analysis — proofs of which (function, semantics) pairs satisfy each principle; Table 1 summary
- §6 Side results / conjectures
- §7 Application example
- §8 Related work and conclusion

## Key Equations

### Aggregated parent score (DFQuAD-style example, intro Eq.)
$$
f(A,S) := \prod_{b \in A}(1 - \sigma(b)) - \prod_{c \in S}(1 - \sigma(c))
$$
Where: $A$ direct attackers, $S$ direct supporters, $\sigma(\cdot)$ is final strength. *(p.2)*

### Update step (DFQuAD)
$$
g(\tau(a), f(A,S)) := \tau(a) - \tau(a)\cdot \max\{0, -f(A,S)\} + (1-\tau(a))\cdot \max\{0, f(A,S)\}
$$
*(p.3)*

### QBAG and restriction
QBAG $\mathsf{G} = (Args, \tau, Att, Supp)$ with $\tau:Args\to\mathbb{I}$, $\mathbb{I}=[0,1]$, $Att\cap Supp=\emptyset$. Restriction $\mathsf{G}{\downarrow}_A = (A, \tau\cap(A\times\mathbb{I}), Att\cap(A\times A), Supp\cap(A\times A))$. *(p.5,7)*

### Aggregation functions (Table 2, p.8)
$$
\alpha^{\Sigma}_v(s) = \sum_{i=1}^n v_i \times s_i
$$
$$
\alpha^{\Pi}_v(s) = \prod_{i: v_i = -1}(1 - s_i) - \prod_{i: v_i = 1}(1 - s_i)
$$
$$
\alpha^{max}_v(s) = M_v(s) - M_{-v}(s),\quad M_v(s) = \max\{0, v_1 s_1, \ldots, v_n s_n\}
$$
Where $s\in[0,1]^n$ is strength vector, $v\in\{-1,0,1\}^n$ encodes attacker(-1)/supporter(+1)/none(0). *(p.8)*

### Influence functions (Table 2, p.8)
$$
\iota^l_w(s) = w - \tfrac{w}{k}\max\{0,-s\} + \tfrac{1-w}{k}\max\{0,s\}\quad \text{Linear(k)}
$$
$$
\iota^e_w(s) = 1 - \tfrac{1-w^2}{1+w\cdot e^s}\quad \text{Euler-based}
$$
$$
\iota^p_w(s) = w - w\cdot h(-\tfrac{s}{k}) + (1-w)\cdot h(\tfrac{s}{k}),\quad h(x) = \tfrac{\max\{0,x\}^p}{1+\max\{0,x\}^p}\quad \text{p-Max(k)}
$$
*(p.8; with fixed typo for p-Max(k) per authors' note)*

### Removal-based contribution
$$
\mathsf{Ctrb}^{\mathcal{R}}_a(x) = \sigma_{\mathsf{G}}(a) - \sigma_{\mathsf{G}{\downarrow}_{Args\setminus\{x\}}}(a) \quad (1)
$$
*(p.9)*

### Removal-based contribution without indirection (intrinsic removal)
$$
\mathsf{Ctrb}^{\mathcal{R}'}_a(x) = \sigma_{(Args, \tau, Att\setminus\{(y,x)|(y,x)\in Att\}, Supp\setminus\{(y,x)|(y,x)\in Supp\})}(a) - \sigma_{\mathsf{G}{\downarrow}_{Args\setminus\{x\}}}(a) \quad (2)
$$
First term computes σ(a) in QBAG with all relations *targeting x* removed (so x's strength is its initial τ(x)); second term removes x entirely. *(p.9)*

### Shapley-based contribution
$$
\mathsf{Ctrb}^{\mathcal{S}}_a(x) = \sum_{X \subseteq Args\setminus\{x,a\}} \frac{|X|!\cdot(|Args\setminus\{a\}|-|X|-1)!}{|Args\setminus\{a\}|!}\Big(\sigma_{\mathsf{G}{\downarrow}_{Args\setminus X}}(a) - \sigma_{\mathsf{G}{\downarrow}_{Args\setminus(X\cup\{x\})}}(a)\Big) \quad (3)
$$
Weighted average over coalitions $X$ that contain $a$ but not $x$, of the marginal effect of adding $x$. *(p.10)*

### Gradient-based contribution
$$
\mathsf{Ctrb}^{\partial}_a(x) = \frac{\partial f_a}{\partial\tau(x)}\big(\tau(x_1),\ldots,\tau(x_n)\big) \quad (5)
$$
Where $f_a:\mathbb{R}^n\to\mathbb{R}$ is the explicit recursive composition of influence and aggregation functions mapping initial strengths to a's final strength. Partial derivative also written $\frac{\partial \sigma(a)}{\partial \tau(x)}$. *(p.11)*

### Recursive expansion of $f_a$
$$
f_a = \iota_{w_a}\big(\alpha_{v_a}(T_{i_1}, \ldots, T_{i_{k_a}})\big) \quad (4)
$$
Placeholders $T_{i_j}$ for parent strength functions; $w_a = \tau(a)$, $v_a$ has -1/0/+1 at index $i$ if $x_i$ attacks/none/supports $a$. Recursion stops because acyclic. May share templates (≤ |Args|) via memoization. *(p.10)*

## Observations and Propositions

- **Observation 3.1** *(p.11)*: $f_a(s^{(0)})$ depends on $s_i^{(0)}$ iff there is a directed path from $x_i$ to $a$ — i.e., gradient inherits directionality structurally.
- **Proposition 4.1** *(p.13)*: Quantitative Contribution Existence implies Contribution Existence.
- Symbolic Note (p.12): For the simple chain $\sigma(a)=\tau(a)-\tau(a)\sigma(b)$ with $\sigma(b)=\tau(b)+(1-\tau(b))\sigma(c)$, the gradient yields $\partial\sigma(a)/\partial\tau(b) = -\tau(a)+\tau(a)\tau(c)$ which evaluates to $-0.25$ at $(0.5,0.5,0.5)$, demonstrating the gradient quantifies marginal effect of a single arg's *initial* strength.

## Worked Example 1.1 (Figure 1, p.2-4)
QBAG G with 5 args {a,b,c,d,e}. Initial strengths all 0.5 (a) and 0.5 for e; others 0.0/0.5 mixed (per fig). Edges: e supports b,c,d; b supports a; c attacks a; d attacks a. Under DFQuAD: σ(a)≈0.375 with e present. Removing e leaves b,c,d with strength 0 ⇒ a's final strength = its initial 0.5. So removing e *increases* a's strength from 0.375 to 0.5 ⇒ counterfactuality says e's contribution to a should be **negative**. But plotting σ(a) vs τ(e) (Figure 1.2) shows curve is U-shaped with min near τ(e)≈0.5 and σ(a) *increases* as τ(e) increases past 0.5 ⇒ marginally increasing τ(e) increases σ(a). So local faithfulness (negative contribution ⇒ marginal increase decreases σ(a)) is violated. Counterfactuality and faithfulness are **simultaneously unsatisfiable** here.

## Worked Example 3.1 (Figure 2, p.11-12)
Three-arg chain c→supports→b→attacks→a, all initial strengths 0.5. DFQuAD final strengths: a=0.125, b=0.75, c=0.5.
- $\mathsf{Ctrb}^{\mathcal{R}}_a(b) = -0.375$
- $\mathsf{Ctrb}^{\mathcal{R}'}_a(b) = -0.25$ (G″: incoming relations to b removed ⇒ b stays at 0.5 ⇒ σ(a)=0.25; minus σ_{G↓\{b}}(a)=0.5 ⇒ −0.25)
- $\mathsf{Ctrb}^{\mathcal{S}}_a(b) = -0.3125$
- $\mathsf{Ctrb}^{\partial}_a(b) = -0.25$
- Shapley sum identity: $\mathsf{Ctrb}^{\mathcal{S}}_a(b) + \mathsf{Ctrb}^{\mathcal{S}}_a(c) = \tau(a)-\sigma(a) = 0.5-0.125 = 0.375$. Also $-0.3125 + (-0.0625) = -0.375$ (sign convention; sum of contributions accounts for delta). *(p.11)*
- Self-gradient: $\mathsf{Ctrb}^{\partial}_a(a) = 1 - \tau(b) + \tau(b)\tau(c) - \tau(c) = 0.25$ at (0.5,0.5,0.5). *(p.12)*

Table 4 (p.13) presents all pairwise contributions for all four functions in this example.

## Parameters / Quantities

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Strength interval | $\mathbb{I}$ | — | [0,1] | [0,1] | 5 | Real interval; here unit interval |
| Initial strength | $\tau(x)$ | — | — | [0,1] | 5 | Per-argument |
| Final strength | $\sigma(x)$ | — | — | [0,1]∪{⊥} | 7 | Computed by gradual semantics |
| Aggregation kind | $\alpha$ | — | — | Sum/Product/Top | 8 | Table 2 |
| Influence kind | $\iota$ | — | — | Linear(k)/Euler-based/p-Max(k) | 8 | Table 2 |
| Linear-influence k | k | — | 1 | ℕ | 8 | Slope/range param for Linear(k) |
| p-Max exponent | p | — | — | ℕ | 8 | Used in p-Max(k) |

## Semantics Used (Table 3, p.8)

| Semantics | Aggregation | Influence |
|---|---|---|
| QuadraticEnergy (QE) | Sum | 2-Max(1) |
| DFQuAD | Product | Linear(1) |
| SquaredDFQuAD (SD-DFQuAD) | Product | 1-Max(1) |
| EulerBased (EB) | Sum | EulerBased |
| EulerBasedTop (EBT) | Top | EulerBased |

All five satisfy directionality and stability ([21,27,28]). *(p.9)*

## Principles (Section 4)

### Principle 4.1 — Contribution Existence *(p.13)*
$\sigma(a)\neq \tau(a) \Rightarrow \exists x\in Args\setminus\{a\},\ \mathsf{Ctrb}_a(x)\neq 0$. (Adjusted from [13]: non-zero contribution must come from an argument other than the topic itself — footnote 4 p.13.)

### Principle 4.2 — Quantitative Contribution Existence *(p.13)*
$\sum_{x\in Args\setminus\{a\}} \mathsf{Ctrb}_a(x) = \sigma(a) - \tau(a)$.

**Proposition 4.1** *(p.13)*: Quantitative Contribution Existence ⇒ Contribution Existence (proof: if RHS≠0, sum≠0, hence some addend≠0).

### Principle 4.3 — Directionality (Contribution Function) *(p.14)*
If there is no directed path from x to a in G, then $\mathsf{Ctrb}_a(x)=0$.
Caveat *(p.14)*: directionality is intuitive only against modular semantics that traverse from leaves; for *range-based*-style semantics like $\sigma(x)=\tau(x)-\sum_{y|x\in Att(y)}\tau(y)$ (where x's strength depends on what it attacks), directionality fails. Counterexample QBAG ({a,b}, {(a,1),(b,1)}, {(b,a)}, {}): no path a→b yet removing a flips σ(b) from 0 to 1 ⇒ Ctrb^R = -1 ≠ 0 (Figure 3, p.14).

### QBAG Initial Strength Modification — Definition 4.1 *(p.15)*
$\mathsf{G}{\downarrow}_{\tau(x)\leftarrow\varepsilon} := (Args, \tau', Att, Supp)$ with $\tau'(x)=\varepsilon$, $\tau'(y)=\tau(y)$ for y≠x.

### Principle 4.4 — Strong Faithfulness *(p.15)*
For every QBAG, every $a,x\in Args$, every $\varepsilon\in\mathbb{I}$, with $G_\varepsilon=\mathsf{G}{\downarrow}_{\tau(x)\leftarrow\varepsilon}$:
- If $\mathsf{Ctrb}_a(x)<0$: $\sigma_G(a)<\sigma_{G_\varepsilon}(a)$ when $\varepsilon<\tau(x)$ and $\sigma_G(a)>\sigma_{G_\varepsilon}(a)$ when $\varepsilon>\tau(x)$.
- If $\mathsf{Ctrb}_a(x)=0$: $\sigma_G(a)=\sigma_{G_\varepsilon}(a)$ for all ε.
- If $\mathsf{Ctrb}_a(x)>0$: symmetric (positive direction).

Authors argue strong faithfulness is **too strong** for general acyclic QBAGs (Figure 1 has non-monotonic e→a effect under DFQuAD; counterexamples for QE in Fig 6, EB in Fig 9; counterexamples to Ctrb=0 case for SD-DFQuAD/EBT in Figs 8, 10). It may be desirable for "monotonic" QBAGs (Section 6).

### Principle 4.5 — Local Faithfulness *(p.16)*
There exists $\delta>0$ such that for all $\varepsilon\in[\tau(x)-\delta,\tau(x)+\delta]\cap\mathbb{I}$ and $G_\varepsilon=\mathsf{G}{\downarrow}_{\tau(x)\leftarrow\varepsilon}$:
- If $\mathsf{Ctrb}_a(x)<0$: σ ordering flips with sign of (ε−τ(x)) (negative implies decrease then increase as before).
- If $\mathsf{Ctrb}_a(x)>0$: symmetric.

Note: 0 case is **dropped** (because at switching points the local effect can be sign-changing).

### Principle 4.6 — Quantitative Local Faithfulness *(p.16)*
$\sigma_{\mathsf{G}{\downarrow}_{\tau(x)\leftarrow\varepsilon}}(a) = \sigma_G(a) + \varepsilon\cdot\mathsf{Ctrb}_a(x) - e(\varepsilon)$, where $\lim_{\varepsilon\to 0} e(\varepsilon)/\varepsilon = 0$.

I.e. error term goes to 0 strictly faster than ε.

**Proposition 4.2** *(p.16)*: Strong Faithfulness ⇒ Local Faithfulness; Quantitative Local Faithfulness ⇒ Local Faithfulness. Proof on p.16-17. Strong and Quantitative Local Faithfulness are **incomparable** (one is global+qualitative, other is local+quantitative). *(p.17)*

### Principle 4.7 — Counterfactuality *(p.17)*
For any $x\in Args$:
- $\mathsf{Ctrb}_a(x)<0 \Rightarrow \sigma_G(a)<\sigma_{\mathsf{G}{\downarrow}_{Args\setminus\{x\}}}(a)$.
- $\mathsf{Ctrb}_a(x)=0 \Rightarrow \sigma_G(a)=\sigma_{\mathsf{G}{\downarrow}_{Args\setminus\{x\}}}(a)$.
- $\mathsf{Ctrb}_a(x)>0 \Rightarrow \sigma_G(a)>\sigma_{\mathsf{G}{\downarrow}_{Args\setminus\{x\}}}(a)$.

### Principle 4.8 — Quantitative Counterfactuality *(p.17)*
$\mathsf{Ctrb}_a(x) = \sigma_G(a) - \sigma_{\mathsf{G}{\downarrow}_{Args\setminus\{x\}}}(a)$.

**Proposition 4.3** *(p.17)*: Quantitative Counterfactuality ⇒ Counterfactuality (proof p.18, three-case sign analysis).

## Principle Satisfaction Matrix (Table 1, p.6)

Row = contribution function, Column = semantics; ✓ = satisfied for all acyclic QBAGs, ✗ = there exists a counterexample QBAG.

**Contribution Existence**

| | QE | DFQuAD | SD-DFQuAD | EB | EBT |
|---|---|---|---|---|---|
| Ctrb^R | ✓ | ✗ | ✗ | ✓ | ✗ |
| Ctrb^R' | ✓ | ✗ | ✗ | ✓ | ✗ |
| Ctrb^S | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ctrb^∂ | ✓ | ✗ | ✗ | ✓ | ✗ |

**Quantitative Contribution Existence**

| | QE | DFQuAD | SD-DFQuAD | EB | EBT |
|---|---|---|---|---|---|
| Ctrb^R | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^R' | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^S | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ctrb^∂ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Directionality** — all ✓ for every (function, semantics) pair.

**(Quantitative) Local Faithfulness**

| | QE | DFQuAD | SD-DFQuAD | EB | EBT |
|---|---|---|---|---|---|
| Ctrb^R | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^R' | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^S | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^∂ | ✓ | ✓ | ✓ | ✓ | ✓ |

**(Quantitative) Counterfactuality**

| | QE | DFQuAD | SD-DFQuAD | EB | EBT |
|---|---|---|---|---|---|
| Ctrb^R | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ctrb^R' | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^S | ✗ | ✗ | ✗ | ✗ | ✗ |
| Ctrb^∂ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Big picture:**
- Only **Shapley** satisfies (Quantitative) Contribution Existence universally — by efficiency.
- Only **Removal-based** satisfies (Quantitative) Counterfactuality universally — by definition.
- Only **Gradient-based** satisfies (Quantitative) Local Faithfulness universally — gradient *is* the marginal-effect notion.
- **Directionality** is universal across all four (with the qualification that R/R' rely on the underlying semantics' directionality; gradient inherits it via Observation 3.1).
- **No function** satisfies all five principles — Counterfactuality and Faithfulness are inherently in tension (Example 1.1).

## Section 5 — Principle-based Analysis (Proofs)

**Computational verification:** All counterexamples were computed in **two independent implementations** to guard against floating-point error: (a) **QBAF-Py**, an extended C/Python library [32] at <https://github.com/TimKam/Quantitative-Bipolar-Argumentation>; (b) **Uncertainpy** [33] at <https://github.com/nicopotyka/Uncertainpy>. *(p.18)*

### §5.1 Contribution Existence proofs

- **Prop 5.1 (p.18):** $\mathsf{Ctrb}^\mathcal{R}$ satisfies CE w.r.t. **QE** and **EB** (Sum aggregation + Linear or Euler-based or p-Max influence). Proof: Sum aggregation forces a non-zero direct attacker/supporter to exist when σ(a)≠τ(a) in acyclic G; influence functions preserve this through the modular update.
- **Prop 5.2 (p.19):** $\mathsf{Ctrb}^{\mathcal{R}'}$ satisfies CE w.r.t. QE and EB (analogous proof).
- **Prop 5.3 (p.19):** $\mathsf{Ctrb}^\mathcal{R}$ and $\mathsf{Ctrb}^{\mathcal{R}'}$ **violate CE** w.r.t. **DFQuAD, SD-DFQuAD, EBT** — counterexample QBAG (Figure 4, p.20): two attackers b,c at strength 1 attacking a at strength 0.5; under Product or Top aggregation, removing one still leaves the other at strength 1, so σ doesn't change ⇒ Ctrb_a(b)=Ctrb_a(c)=0 yet σ(a)<0.5=τ(a). Same QBAG works for max-aggregation (EBT). *(p.19-20)*
- **Prop 5.4 (p.20):** $\mathsf{Ctrb}^\mathcal{S}$ satisfies **Quantitative** Contribution Existence (and hence CE) for **all five** semantics. Proof: characterise $\mathsf{Ctrb}^\mathcal{S}_a(x)$ as the Shapley value $\phi_x(v)$ of the coalition game with players $Args\setminus\{a\}$ and utility $v(S):=\sigma(a)-\sigma_{\mathsf{G}{\downarrow}_{Args\setminus S}}(a)$; the **efficiency principle** of Shapley values gives $\sum_x \phi_x(v)=v(Args\setminus\{a\})=\sigma(a)-\tau(a)$.
- **Corollary 5.5 (p.20):** $\mathsf{Ctrb}^\mathcal{S}$ satisfies CE for all five semantics (immediate from Prop 5.4 + Prop 4.1).
- **Prop 5.6 (p.21):** $\mathsf{Ctrb}^\partial$ violates CE (and qCE) w.r.t. DFQuAD, SD-DFQuAD, EBT — same Figure 4 QBAG counterexample.
- **Prop 5.7 (p.21):** $\mathsf{Ctrb}^\partial$ satisfies CE w.r.t. **QE and EB**. Proof: pick the predecessor x of a with highest topological index; then x is a parent of a with no other path; sign of partial derivative ∂σ(a)/∂τ(x) is strictly negative (if x attacks) or positive (if x supports) under QE/EB.
- **Prop 5.8 (p.21):** $\mathsf{Ctrb}^\mathcal{R},\mathsf{Ctrb}^{\mathcal{R}'},\mathsf{Ctrb}^\partial$ **violate qCE** w.r.t. QE and EB. Counterexample (Figure 4 again):
  - QE: σ(a)−τ(a) = −0.4; sums Ctrb^R(b)+Ctrb^R(c) = Ctrb^{R'}(b)+Ctrb^{R'}(c) = −0.3; Ctrb^∂(b)+Ctrb^∂(c) ≈ −0.16 — none equals −0.4.
  - EB: σ(a)−τ(a) ≈ −0.2025; corresponding sums ≈ −0.138 (R, R'); ≈ −0.089 (∂).

**Example 5.1 (p.22):** Star graph with topic a (τ=0.5) supported by b₁,…,bₙ (each τ=1), QE semantics. Plot (Figure 5): Shapley contribution of a single supporter ~0.05 at n=10; removal/gradient contributions already visually 0 at n=6. **Insight:** removal/gradient functions have a *vanishing-individual-contribution* effect when many redundant contributors exist; Shapley does not. CE alone may be too weak — for n=10..20, $\mathsf{Ctrb}^\mathcal{R}_{b_i}(a)$ and $\mathsf{Ctrb}^\partial_{b_i}(a)$ are negligible despite the proportional effect of a single supporter still being substantial (potentially misleading).

### §5.2 Directionality proofs

**Proposition 5.9 (p.23):** All four contribution functions satisfy directionality w.r.t. **all modular semantics**. Proofs by case for each function:
- **Ctrb^R:** if no path x→a, σ_G(a)=σ_{G\{x}}(a) by modular semantics ⇒ Ctrb^R = 0.
- **Ctrb^R':** similar — removing edges into x doesn't change a's strength because a is unreachable from x.
- **Ctrb^S:** for every coalition X, σ_{G↓Args\(X∪{x})}(a)=σ_{G↓Args\X}(a) when no path x→a ⇒ each marginal is 0.
- **Ctrb^∂:** by Observation 3.1, if no path x→a then $f_a$ is independent of τ(x), so partial derivative is 0.

### §5.3 (Quantitative) Local Faithfulness proofs

**Prop 5.10 (p.23):** $\mathsf{Ctrb}^\partial$ satisfies **quantitative** local faithfulness for every **differentiable** modular semantics. Proof (Eq.6, p.23-24): the error term $e(\varepsilon)=\sigma_{G{\downarrow}_{\tau(x)\leftarrow\varepsilon}}(a)-(\sigma_G(a)+\varepsilon\cdot\mathsf{Ctrb}^\partial_a(x))$ has $\lim_{\varepsilon\to 0} e(\varepsilon)/\varepsilon = \mathsf{Ctrb}^\partial_a(x)-\mathsf{Ctrb}^\partial_a(x) = 0$, by definition of the partial derivative.

**Differentiability note (p.23):** All semantics in Table 3 use differentiable α and ι, except p-Max(k) at certain p values (differentiable for p=2 [25 Prop 1] but not always elsewhere).

**Prop 5.11 (p.24):** $\mathsf{Ctrb}^\partial$ satisfies local faithfulness (immediate from Prop 5.10 + Prop 4.2).

**Counterexamples for the other three functions:**

- **Prop 5.12 (p.24):** $\mathsf{Ctrb}^\mathcal{R},\mathsf{Ctrb}^{\mathcal{R}'}$ violate local faithfulness w.r.t. **QE**. Figure 6.1 QBAG; topic a, contributor d. Ctrb^R(d) = Ctrb^{R'}(d) ≈ −0.01122; Ctrb^∂(d) ≈ +0.02987. Sign mismatch ⇒ removal/intrinsic-removal sign disagrees with marginal-effect direction.
- **Prop 5.13 (p.24):** Same functions violate LF w.r.t. **DFQuAD** (Figure 7); Ctrb^R = Ctrb^{R'} ≈ +0.32 but increasing τ(d) does not increase σ(a).
- **Prop 5.14 (p.25):** Same for **SD-DFQuAD** (Figure 8); ≈ +0.1398 but no marginal increase.
- **Prop 5.15 (p.25):** Same for **EB** (Figure 9); Ctrb^R = Ctrb^{R'} ≈ +0.0016 but Ctrb^∂(d) ≈ −0.002 (sign flip).
- **Prop 5.16 (p.25):** Same for **EBT** (Figure 10); ≈ +0.013 but no marginal increase.
- **Prop 5.17 (p.25):** $\mathsf{Ctrb}^\mathcal{S}$ violates LF w.r.t. **QE** (Figure 11); Ctrb^S(d) ≈ −0.0016 but Ctrb^∂(d) ≈ +0.0302 (sign mismatch).
- (Continued on pages 26-27 — Props 5.18–5.21 — Shapley violations of LF for DFQuAD, SD-DFQuAD, EB, EBT.)

These propositions plus Prop 4.2 give the column "(Quantitative) Local Faithfulness" of Table 1: only Ctrb^∂ is universally compliant.

**Continued Local Faithfulness violations (Shapley):**
- **Prop 5.18 (p.26):** Ctrb^S violates LF w.r.t. **DFQuAD** (Figure 1.1 reused; topic a contributor e). Ctrb^S(e) ≈ −0.0833 < 0, but increasing τ(e) actually increases σ(a) (Figure 1.2 plot rises after the minimum).
- **Prop 5.19 (p.26):** Ctrb^S violates LF w.r.t. **SD-DFQuAD** (Figure 8.1; topic a contributor d). Ctrb^S(d) ≈ +0.0636 > 0, but increasing τ(d) does not increase σ(a).
- **Prop 5.20 (p.26):** Ctrb^S violates LF w.r.t. **EB** (Figure 12.1). Ctrb^S(d) ≈ +0.0007 vs Ctrb^∂(d) ≈ −0.0037 (sign disagreement).
- **Prop 5.21 (p.26):** Ctrb^S violates LF w.r.t. **EBT** (Figure 13.1). Ctrb^S(b) ≈ −0.0377 < 0, but changing τ(b) does not affect σ(a) at all (flat plot in Fig 13.2 = constant 0.3665).

### §5.4 (Quantitative) Counterfactuality proofs

**Prop 5.22 (p.27):** $\mathsf{Ctrb}^\mathcal{R}$ satisfies **quantitative** counterfactuality for **all** semantics — by definition, $\mathsf{Ctrb}^\mathcal{R}_a(x) = \sigma_G(a) - \sigma_{G\setminus\{x\}}(a)$ matches Principle 4.8 verbatim.

**Corollary 5.23 (p.27):** $\mathsf{Ctrb}^\mathcal{R}$ satisfies counterfactuality (from Prop 5.22 + Prop 4.3).

**Counterexamples for the other three functions (no semantics escapes):**

- **Prop 5.24 (p.27):** $\mathsf{Ctrb}^{\mathcal{R}'}$ violates counterfactuality and quantitative counterfactuality w.r.t. **QE, DFQuAD, SD-DFQuAD**. Counterexample (Figure 14, p.32): three-arg chain c→+b→−a (c at strength 1, b at 0, a at 0.5). Under QE/DFQuAD/SD-DFQuAD, σ(b)>0 and σ(a)<τ(a)=0.8; with b removed σ(a)=0.8. Yet Ctrb^{R'}(b)=0 (because removing incoming-to-b first leaves b at 0 ⇒ no effect on a) while removal *would* show a positive contribution.
- **Prop 5.25 (p.28):** Ctrb^{R'} violates (q)CF w.r.t. **EB**. Figure 15 QBAG; topic a contributor e. σ(a)−σ_{G\{e}}(a) ≈ −2.5×10⁻⁶ but Ctrb^{R'}(e) ≈ +3.5431×10⁻⁶ — sign mismatch.
- **Prop 5.26 (p.28):** Ctrb^{R'} violates (q)CF w.r.t. **EBT**. Figure 16; topic a contributor b. σ(a)−σ_{G\{b}}(a) ≈ −0.0145 but Ctrb^{R'}(b) = 0.
- **Prop 5.27 (p.28):** $\mathsf{Ctrb}^\mathcal{S}$ violates (q)CF w.r.t. **QE** (Figure 17); σ(a)−σ_{G\{e}}(a) ≈ −0.0149 but Ctrb^S(e) ≈ +4.93×10⁻⁵.
- **Prop 5.28 (p.29):** Ctrb^S violates (q)CF w.r.t. **DFQuAD** (Figure 18); ≈ −0.0109 vs Ctrb^S(e) ≈ +0.0021.
- **Prop 5.29 (p.29):** Ctrb^S violates (q)CF w.r.t. **SD-DFQuAD** (Figure 19); ≈ −0.0049 vs Ctrb^S(e) ≈ +0.0027.
- **Prop 5.30 (p.29):** Ctrb^S violates (q)CF w.r.t. **EB** (Figure 20); ≈ −7.84×10⁻⁵ vs Ctrb^S(f) ≈ +3.44×10⁻⁶.
- **Prop 5.31 (p.30):** Ctrb^S violates (q)CF w.r.t. **EBT** (Figure 21); ≈ +7.33×10⁻⁵ vs Ctrb^S(f) ≈ −2.70×10⁻⁵.
- **Prop 5.32 (p.30):** $\mathsf{Ctrb}^\partial$ violates (q)CF w.r.t. **QE** (Figure 22 — large 11-node fan-in/fan-out structure with d as topic-influencer); σ(a)−σ_{G\{d}}(a) ≈ −0.0038 but Ctrb^∂(f)=0.
- **Prop 5.33 (p.31):** Ctrb^∂ violates (q)CF w.r.t. **DFQuAD** (Figure 1, the original counterfactual-vs-faithfulness example with τ(e)=0.5 plateau); σ(a)−σ_{G\{e}}(a)=−0.125 but Ctrb^∂(e)=0 because the plateau gives zero gradient.
- **Prop 5.34 (p.31):** Ctrb^∂ violates (q)CF w.r.t. **SD-DFQuAD** (Figure 23 — chain c→−b→−a, all 0.5); σ(a)=σ_{G\{b}}(a)=0.5 but Ctrb^∂(b)=−0.25.
- **Prop 5.35 (p.31):** Ctrb^∂ violates (q)CF w.r.t. **EB and EBT** (Figure 24 — chain c→+b→−a). Same structural reason.

These 14 propositions plus Prop 5.22/5.23 give the "Counterfactuality" rows of Table 1.

## Section 6 — Minor Results and Conjectures

### §6.1 Proximity (rejected as a principle)

**Definition 6.1 (Strictly Closer)** *(p.32)*: y is strictly closer to a than x is, iff y lies on **every** directed path from x to a.

**Principle 6.1 (Proximity)** *(p.33)*: If y is strictly closer to a than x is, then $|\mathsf{Ctrb}_a(y)| \geq |\mathsf{Ctrb}_a(x)|$.

**Status:** Proximity is **violated even for very simple cases** (e.g., Ctrb^R + QE, Figure 25: |Ctrb^R(b)| ≈ 0.0012 < |Ctrb^R(c)| ≈ 0.0037 even though b is closer to a than c). The intuition fails when c substantially weakens b: removing b only marginally affects a, but removing c strengthens b and thus substantially weakens a.

**Proposition 6.1 (p.33):** Ctrb^R, Ctrb^{R'}, Ctrb^S violate proximity w.r.t. all five semantics; Ctrb^∂ violates proximity w.r.t. QE, DFQuAD, SD-DFQuAD, EB. (Status for Ctrb^∂ + EBT left open.) Authors **excluded proximity from the main principle list**.

**Definition 6.2 (Pure Support Path)** *(p.33)*: a path from a to b is a *pure support path* iff it lies entirely in the directed graph (Args, Supp).

**Conjecture 1** *(p.35)*: $\mathsf{Ctrb}^\mathcal{S}$ satisfies proximity w.r.t. all five semantics for contributors x and topic a such that **all paths from x to a are pure support paths** (no attacks intervene).

### §6.2 Violation of Strong Faithfulness

**Proposition 6.2 (p.35):** All four contribution functions violate strong faithfulness w.r.t. all five semantics. Proof structure (p.36-37): for strong faithfulness to hold, one of three monotone trichotomy statements must hold for all (a,x,ε,ε') with ε>τ(x)>ε'. Each semantics admits a counterexample QBAG that breaks the trichotomy:
- **QE:** Figure 6.1 with d/a as contributor/topic — non-monotone σ(a) vs τ(d).
- **DFQuAD:** Figure 1.1 with e/a — U-shape (negative below 0.5, positive above 0.5).
- **SD-DFQuAD:** Figure 8.1 with d/a — non-monotone.
- **EB:** Figure 9.1 with d/a — peaked plot.
- **EBT:** Figure 10.1 with d/a — piecewise increasing then plateau.

The walk-through for DFQuAD/Figure 1.1 (p.37) shows: at τ(e)=0.2, the local effect of incremental ε is *negative* for ε∈[0,0.8), *neutral* at ε=0.8, *positive* on (0.8, 1] — no single sign assignment can be correct globally.

### §6.3 Strong Faithfulness given Monotonic Effects *(p.37-39)*

Authors observe: in strong-faithfulness counterexamples, the contributor exerts **non-monotone** influence on the topic; restricting to monotone-effect cases may recover strong faithfulness for Ctrb^∂.

**Definition 6.3 (Monotonic Effect)** *(p.38)*: x has a monotonic effect on a w.r.t. σ iff for every QBAG-strength-modification of x, **either** ε<ε' implies $\sigma_{G{\downarrow}_{\tau(x)\leftarrow\varepsilon}}(a) \leq \sigma_{G{\downarrow}_{\tau(x)\leftarrow\varepsilon'}}(a)$ **or** ε<ε' implies the reverse. (Globally monotone increasing or decreasing.)

**Definition 6.4 (Monotonic Effect QBAGs)** *(p.38)*: G is a *monotonic effect QBAG* w.r.t. σ iff for all x,a∈Args, x has monotonic effect on a w.r.t. σ. Class denoted $\mathcal{Q}^\sigma_{ME}$.

**Conjecture 2** *(p.38)*: For σ ∈ {QE, DFQuAD, SD-DFQuAD, EB, EBT}, restricting to G ∈ $\mathcal{Q}^\sigma_{ME}$, $\mathsf{Ctrb}^\partial$ satisfies strong faithfulness w.r.t. σ.

**Topological speculation** *(p.38-39)*: A contributor's role w.r.t. topic argument can be classified as:
- direct attacker / direct supporter,
- indirect attacker (attacks supporters / supports attackers),
- indirect supporter (supports supporters / attacks attackers),
- "clear attacker" — direct or indirect attacker but **not** also a direct/indirect supporter,
- "clear supporter" — direct or indirect supporter but **not** also a direct/indirect attacker.

Speculation: clear supporters always have effect ≥ 0 on topic regardless of their initial strength; clear attackers always have effect ≤ 0. This sets up the formal monotonicity classes for which strong faithfulness should be recoverable.

## Section 7 — Case Study (Movie-rating QBAG) *(p.39-40)*

Application: explaining aggregated movie ratings on Rotten Tomatoes (drawing from [5]). QBAGs are hierarchical with topic = movie evaluation; attackers/supporters are evaluation criteria (acting/directing/writing) and sub-criteria (individual actors). Initial strengths from NLP pipeline: phrase extraction → sentiment analysis → topic classification → aggregation that aligns final strength with actual Rotten Tomatoes score.

**Example QBAG (Figure 26, p.40):** topic m (movie, τ=0.79, σ=0.85). Attacker f_W (writing, τ=0.02). Supporters f_D (directing, τ=0.05) and f_A (acting, τ=0.16, σ=0.26). f_A further supported by two specific actors f'_A1 (τ=0.05) and f'_A2 (τ=0.07). DFQuAD semantics.

**Table 5 (p.40) — contributions to m:**

| Argument | Ctrb^R | Ctrb^{R'} | Ctrb^S | Ctrb^∂ |
|---|---|---|---|---|
| f_A | 0.051443 | 0.03192 | 0.044726 | 0.176258 |
| f'_A1 | 0.007792 | 0.007792 | 0.004065 | 0.15585 |
| f'_A2 | 0.011144 | 0.011144 | 0.00577 | 0.1592 |
| f_D | 0.007792 | 0.007792 | 0.011248 | 0.15584 |
| f_W | -0.0042 | -0.0042 | -0.00807 | -0.21 |

**Qualitative agreement (p.39-40):** All four functions agree on signs (f_W negative, others positive) and that f_A has the largest positive contribution. Quantitative ranking diverges:
- Removal-based (R, R'): f_A > f'_A2 > f'_A1 ≈ f_D
- Shapley (S): f_A > f_D > f'_A2 > f'_A1; sum ≈ 0.85 − 0.79 = 0.06 (efficiency).
- Gradient (∂): f_A > f'_A2 > f'_A1 ≈ f_D; large magnitudes (~0.15-0.17) reflecting per-unit sensitivity.

**Practical readings derived from principles (p.40):**
- Ctrb^∂ ≈ 0.15 for f'_A1, f'_A2, f_D ⇒ "small change δ in initial strength of any of these changes m by ≈ 0.15·δ"; for f_A ≈ 0.17·δ; for f_W ≈ −0.21·δ. (From Quantitative Local Faithfulness, Prop 5.10.)
- Ctrb^R(f_A) ≈ 0.05 ⇒ "removing f_A entirely would decrease m's final strength by ≈ 0.05" (Quantitative Counterfactuality, Prop 5.22).
- Directionality (Prop 5.9): if asking f_A as topic, contribution from f_D to f_A must be 0 under all four functions because no path f_D → f_A.

## Section 8 — Discussion and Related Work *(p.41)*

Positioning: contribution to **argumentative explainability**, focused on QBA. Related explanation-trend work cited [2, 3, 14, 34, 35]. Applied uses of QBA cited [4, 36, 18, 15, 5, 16, 17].

**Key novelties vs prior work:**
- **[32]** introduces explanation notions for *sets* of arguments explaining inference *changes* after updates — different focus (set explanations, dynamic).
- **[13]** is the original workshop paper; this paper extends and corrects it.
- **[34, 19]** introduced contribution functions for **gradual semantics over non-bipolar** abstract argumentation; this paper extends to bipolar.
- **[37]** is referenced as the survey of semantics in this area.
- **[14]** specifically studies gradient-based contribution under DFQuAD in more depth.
- **[38]** introduces a function corresponding to counterfactual contribution but at *agent* level (aggregated across an agent's utterances), not single-argument.

**Author summary of distinguishing principles** (p.41): For each of the three "main" contribution functions, exactly one principle is satisfied universally and only by it:
- **Ctrb^R** ⇄ (quantitative) **counterfactuality**.
- **Ctrb^S** ⇄ **quantitative contribution existence**.
- **Ctrb^∂** ⇄ (quantitative) **local faithfulness**.

**Ctrb^{R'}** does *not* get its own characterising principle — authors note it would be "trivially possible but arguably pointless" to construct one tailored to R'.

**Open work named:** the conjectures in §6 (proximity for Ctrb^S over pure-support paths; strong faithfulness for Ctrb^∂ over monotonic-effect QBAGs); cyclic QBAGs.

**Funding:** ERC Horizon 2020 grant 101020934; J.P. Morgan; Royal Academy of Engineering Research Chairs.

## Appendix A — Counterexamples Proving Violation of Proximity *(p.42-50)*

Detailed appendix providing explicit QBAG counterexamples + numeric contributions for the proximity-violation claims of §6.1 (Proposition 6.1).

- **Prop A.1 (p.42)** — **Ctrb^R** violates proximity w.r.t. all five semantics. Examples in Figures 25, 27, 27 (re-used for SD-DFQuAD), 29:
  - QE (Fig 25): |Ctrb^R(b)|≈0.0012 < |Ctrb^R(c)|≈0.0037.
  - DFQuAD (Fig 27): |Ctrb^R(b)|=0 < |Ctrb^R(c)|≈0.05.
  - SD-DFQuAD (Fig 27): |Ctrb^R(b)|≈0.0238 < |Ctrb^R(c)|≈0.1483.
  - EB & EBT (Fig 29): |Ctrb^R(b)|≈0.0075 < |Ctrb^R(c)|≈0.0089.
- **Prop A.2 (p.43)** — **Ctrb^{R'}** violates proximity for all five. Figures 30 (QE), 31 (DFQuAD), 32 (SD-DFQuAD), 33 (EB & EBT). Values noted in proof; e.g., DFQuAD chain c→+b→+a with τ=(0.9, 0.1, 0.5) gives |Ctrb^{R'}(b)|≈0.05 < |Ctrb^{R'}(c)|=0.405.
- **Prop A.3 (p.43-44)** — **Ctrb^S** violates proximity for all five. Figures 34-38 used; multiple small magnitudes confirmed (e.g., QE Fig 34: |Ctrb^S(e)|≈5×10⁻⁵ < |Ctrb^S(f)|≈5.6×10⁻⁴).
- **Prop A.4 (p.44-45)** — **Ctrb^∂** violates proximity for QE, DFQuAD, SD-DFQuAD, EB. Figures 39, 31 (re-used), 40, 41. **Status for Ctrb^∂ + EBT left open** (no proof of satisfaction or violation provided).

The appendix contains many small QBAG diagrams (Figures 25-41) — chains, fan-in, fan-out — each documented with initial strengths, final strengths, and the proximity violation magnitudes. Useful as a corpus of test cases for any contribution-function implementation.

## Knowledge State Summary

- **All 51 page images read** (page-000 through page-050 inclusive). Confirmed paper identity (arXiv:2401.08879v2, 13 Jun 2024) on first page; paper PDF is 642 KB and was downloaded by paper-retriever via arXiv direct.
- **Notes captured** in this file: abstract, full §1-§8 detail, all numbered Definitions (2.1-2.2, 4.1, 6.1-6.4), all numbered Principles (2.1-2.2, 4.1-4.8, 6.1), all numbered Propositions/Corollaries (4.1-4.3, 5.1-5.35, 6.1-6.2, A.1-A.4) with counterexample-figure pointers, master Table 1 satisfaction matrix, Tables 2-5 verbatim (parameters, semantics, contributions, case study), all 26 worked-example diagrams referenced (Figures 1-26 main text; 27-41 appendix).
- **Reference list** (38 entries) captured in citations.md verbatim with key-citations-for-followup notes; appendix A proximity-violation counterexamples (Props A.1-A.4, Figures 25-41) summarised.
- **Artifacts written:** notes.md, metadata.json (already present from retrieval), description.md (with tags), abstract.md (verbatim + interpretation), citations.md.
- **Skipped per user override:** Step 7 reconcile, Step 8 papers/index.md update, Step 9 `pks source stamp-provenance` provenance stamp. User explicitly said "DO NOT" for source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote, reconcile, update index.md.
- **Blocker:** none. Pipeline complete. Final step is writing the per-paper report at `./reports/paper-kampik-2024-contribution.md`.

- **Final strength computation (acyclic):** linear-time forward propagation along topological order [22]. Parents' final strengths fixed before child is updated. *(p.8)*
- **Modular update:** for arg x_i, vector v∈{-1,0,1}^n encodes parent relationship type; aggregate α_v(s); apply influence ι_w(aggregate) where w=τ(x_i) ⇒ new strength. *(p.7-8)*
- **Removal contribution computation:** compute σ_G(a), then construct G↓_{Args\{x}} by deleting x and its incident edges, recompute σ. O(|Args|·T_σ) for one query.
- **Intrinsic removal:** also delete only edges *incoming to x* to obtain G^- (so x stays at τ(x)); compute σ_{G^-}(a) and σ_{G\{x}}(a). *(p.9)*
- **Shapley:** sum over $2^{|Args|-2}$ coalitions. Worst case exponential. Practical: use Monte-Carlo sampling or restrict to small graphs.
- **Gradient:** symbolic differentiation of recursively-built f_a. With memoization, ≤ |Args| placeholder templates. Modern autodiff makes this efficient. *(p.10)*
- **Counterexample QBAGs** in proofs are small (3-5 nodes); useful test cases for any implementation.

## Figures of Interest
- **Fig 1 (p.4):** Example 1.1 graph + plot of σ(a) vs τ(e); shows U-shape.
- **Fig 2 (p.12):** Example 3.1 — base graph G, G' (b removed), G'' (incoming-to-b removed). Used for intrinsic-removal intuition.
- **Table 1 (p.6):** Master principle-satisfaction matrix.
- **Table 2 (p.8):** Aggregation/influence formulas.
- **Table 3 (p.8):** Five named gradual semantics.
- **Table 4 (p.13):** Per-pair contributions in Example 3.1 across all four functions.

## Limitations
- Restricted to **acyclic** QBAGs. Cycles cause non-convergence in some semantics (e.g., DFQuAD); extension is future work. *(p.5)*
- Does not formally study computational tractability beyond mentioning Shapley exponentiality.
- Self-contribution: removal-based functions are *partial* (undefined when x=a); only gradient is total. *(p.12)*
- No empirical user study of which principles users actually want — purely formal analysis.

## Arguments Against Prior Work
- **[13] Workshop paper** (their own): re-presented here with **technical fix to Shapley**: original definition needed correction (footnote p.3, p.10 fn 2) to handle topic-not-in-coalition correctly. Also **adjusted Contribution Existence principle**: requires non-zero contribution from a *different* argument than topic itself (footnote 4, p.13).
- **Gradual-attribution work [19]:** introduced removal/intrinsic-removal-style contributions for abstract gradual argumentation (no support, single-relation); this paper generalises to bipolar.
- **Existing QBA semantics [21,27,28]** focus on strength assignment; do *not* address inter-argument contribution analysis. Authors fill the gap.
- **Cooperative-game-theoretic feature attribution (SHAP etc.)**: analogy drawn but not directly applied; Shapley value adapted via QBAG-specific marginal contributions.

## Design Rationale
- **Acyclic restriction** justified by application reality: hierarchical recommenders, temporal arguments, machine-learning-derived graphs typically acyclic. *(p.2,5)*
- **Four functions chosen** because they capture distinct intuitions: (R) global counterfactual, (R') intrinsic counterfactual stripped of indirect effects, (S) cooperative-game fairness, (∂) marginal sensitivity.
- **Strength interval [0,1]** for concreteness; framework parametrised by $\mathbb{I}$. *(p.5)*
- **Modular semantics framing** lets new (aggregation, influence) pairs slot in without re-deriving theory.
- **Directionality** treated as a *prerequisite* property of the semantics (Principle 2.1) so contribution functions inherit it cleanly.
- **Stability principle (2.2)** ensures parentless arguments preserve initial strength — needed for clean recursive base case in $f_a$.

## Testable Properties (for an implementation)
- For any acyclic QBAG and Shapley contribution: $\sum_{x\in Args\setminus\{a\}}\mathsf{Ctrb}^{\mathcal{S}}_a(x) = \sigma(a)-\tau(a)$. *(p.13)*
- For any (function, semantics): if there is no directed path from x to a, $\mathsf{Ctrb}_a(x) = 0$. *(p.14, Principle 4.3)*
- For Removal contribution under any of the 5 listed semantics: counterfactuality holds — sign and magnitude match σ(a)-σ_{G\{x}}(a). *(p.6 Table 1)*
- For Gradient contribution under any of the 5 listed semantics: marginal increase in τ(x) by ε changes σ(a) by ≈ ε·$\mathsf{Ctrb}^{\partial}_a(x)$. *(p.6 Table 1)*
- Removal, Intrinsic-Removal, and Gradient contributions can violate Quantitative Contribution Existence — implementations must not assume sums equal σ(a)−τ(a) unless using Shapley. *(p.6 Table 1)*
- For Example 3.1 chain (c→+b→−a, all τ=0.5, DFQuAD): expected outputs $\mathsf{Ctrb}^{\mathcal{R}}_a(b)=-0.375$, $\mathsf{Ctrb}^{\mathcal{R}'}_a(b)=-0.25$, $\mathsf{Ctrb}^{\mathcal{S}}_a(b)=-0.3125$, $\mathsf{Ctrb}^{\partial}_a(b)=-0.25$. *(p.11-13)*
- Self-contribution: $\mathsf{Ctrb}^{\mathcal{R}/\mathcal{R}'/\mathcal{S}}_a(a)=\bot$; $\mathsf{Ctrb}^{\partial}_a(a)$ defined and computable via $\partial\sigma(a)/\partial\tau(a)$. *(p.12)*

## Relevance to Project (argumentation reductions / encoding)
- This project deals with reductions and encodings for abstract argumentation. The QBA setting is *quantitative* (no extension semantics) but cousin to the discrete acceptance setting we mostly work with.
- Shapley-value contribution lifts cleanly to *any* monotone aggregation; could be a model for explanation in our skeptical/credulous reasoners (e.g., "which arguments most influence acceptance of topic a").
- The principle-based methodology is directly portable: one can ask whether our reductions preserve quantitative properties analogously.
- Gradient-based contributions are computable via autodiff over our encodings — relevant if we ever extend ASP/Datalog backends to weighted/probabilistic argumentation.
- The acyclic-only caveat aligns with our common case (well-founded preferred fragments).

## Open Questions / Future Work
- [ ] Extend contribution functions to **cyclic** QBAGs; handle non-convergence formally.
- [ ] Tractable approximation of Shapley contribution (Monte-Carlo; structured graphs).
- [ ] User studies: which principles actually align with stakeholder expectations in real XAI deployments?
- [ ] Combine functions to get hybrid contributions satisfying broader principle subsets (only possible if some inherently-conflicting principles are dropped).
- [ ] Are there contribution functions tailored to specific semantics (e.g., EulerBased) that satisfy more principles?

## Notable References Cited
- [13] Authors' workshop paper introducing the four contribution functions (this paper extends and corrects).
- [18] DFQuAD semantics.
- [19] Amgoud et al.-style gradual-argumentation contribution work (introduced first two functions for non-bipolar).
- [21] Directionality / stability principles for gradual semantics.
- [22] QBAG / gradual semantics core theory (Potyka).
- [23] Bipolar gradual semantics framework.
- [24,25,26] Other named semantics (likely Baroni et al., Mossakowski et al., etc.).
- [27] Modular semantics framing.
- [28] Stability discussion / Potyka.
- [29] Shapley 1953 (original).
- [30] Real analysis / gradient text reference.

(Full citation list: see citations.md.)

## Quotes Worth Preserving
> "As none of the covered contribution functions satisfies all principles, our analysis can serve as a tool that enables the selection of the most suitable function based on the requirements of a given use case." (Abstract)

> "Hence, it is impossible to satisfy both *counterfactuality* and *faithfulness* simultaneously in this example." (p.3)

> "We claim that this limitation is well-motivated: in many applications of QBAGs there is a clear hierarchical or temporal structure to the arguments." (p.2)
