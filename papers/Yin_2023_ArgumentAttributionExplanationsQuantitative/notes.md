---
title: "Argument Attribution Explanations in Quantitative Bipolar Argumentation Frameworks (Technical Report)"
authors: "Xiang Yin, Nico Potyka, Francesca Toni"
year: 2023
venue: "arXiv:2307.13582 (extended technical report; conference version at ECAI 2023)"
doi_url: "https://arxiv.org/abs/2307.13582"
pages: 21
affiliations: "Imperial College London (Yin, Toni); Cardiff University (Potyka)"
---

# Argument Attribution Explanations in Quantitative Bipolar Argumentation Frameworks

## One-Sentence Summary
Defines **Argument Attribution Explanations (AAEs)** for acyclic Quantitative Bipolar Argumentation Frameworks (QBAFs) under the **DF-QuAD gradual semantics** as the partial derivative `∇|_{B↦A} = ∂σ(A)/∂τ(B)`, derives closed-form direct (Prop 2) and chain-rule indirect (Prop 4) expressions, proves six "desirable" properties (explainability, missingness, completeness, counterfactuality, agreement, monotonicity) for non-multifold connections, and demonstrates linear-time computability on case studies in fake-news detection, movie recommendation, and fraud detection.

## Problem Addressed
Quantitative reasoning outcomes of argumentation frameworks under gradual semantics had received little explanatory attention compared to qualitative dispute/debate explanations under extension semantics, despite QBAFs being the substrate for production applications (fake-news detection, movie recommendation, fraud detection). Prior argumentative XAI either gave qualitative dialogues only or used feature-attribution methods aimed at the underlying ML model rather than at the argumentation graph itself. The paper fills the gap of *quantifying the influence of one argument on a topic argument's strength under a gradual semantics*. *(p.1)*

## Key Contributions
- **Novel definition** of AAE as a partial-derivative attribution score over QBAF arguments under DF-QuAD. *(p.3, Definition 2)*
- **Closed-form** characterisations: direct attribution (Prop 2) and indirect attribution via chain rule (Prop 4). *(p.4)*
- **Property catalogue**: explainability, missingness, completeness, counterfactuality, agreement, monotonicity — including positive results when arguments are directly/indirectly connected, and **negative results** (Props 8, 10, 12, 14) when arguments are *multifold* connected. *(pp.4-5)*
- **Linear-time computability** in number of arguments. *(p.5; Prop 19 in SM, p.5 main text)*
- **Three case studies**: fake news detection (sec 6), movie recommender (sec 6), fraud detection (SM appendix C, 48-argument QBAF).
- **Visualisation scheme**: arrow colour (blue=positive, red=negative attribution), arrow thickness = magnitude; ranked bar chart on right. *(p.5, Fig 4 and p.6, Fig 6)*

## Methodology
The framework is mathematical — pure theory + small worked case studies. The authors:
1. Adopt the existing DF-QuAD gradual semantics for acyclic QBAFs as the underlying inference engine.
2. Define AAE as a **gradient** (limit of finite-difference perturbation of the base score τ(B)).
3. Prove direct/indirect closed forms by symbolically differentiating DF-QuAD.
4. Adapt feature-attribution properties from the ML XAI literature (e.g. SHAP/Integrated-Gradients literature: completeness/efficiency [42], missingness [29], counterfactuality [18], quantitative faithfulness [35]) to the QBAF setting.
5. Apply to three case-study QBAFs taken from prior work — fake news ([28] Kotonya & Toni), movie recs ([17] Cocarascu et al.), fraud detection ([16] Chen et al.).

## Background — Definitions

### Definition 1 (QBAF) *(p.2)*
A QBAF is a quadruple `Q = ⟨A, R⁻, R⁺, τ⟩` where:
- `A` is the (finite) set of arguments
- `R⁻ ⊆ A × A` is the **attack** relation
- `R⁺ ⊆ A × A` is the **support** relation, with `R⁻ ∩ R⁺ = ∅`
- `τ : A → [0,1]` is the **base score** function

### DF-QuAD Strength σ(A) *(p.2)*
Aggregated attacker/supporter strengths:

$$
v_{Aa} = 1 - \prod_{\{X | (X, A) \in \mathcal{R}^-\}} (1 - \sigma(X))
$$

$$
v_{As} = 1 - \prod_{\{X | (X, A) \in \mathcal{R}^+\}} (1 - \sigma(X))
$$

Strength:

$$
\sigma(A) = \begin{cases} \tau(A) - \tau(A) \cdot (v_{Aa} - v_{As}) & \text{if } v_{Aa} \ge v_{As} \\ \tau(A) + (1 - \tau(A)) \cdot (v_{As} - v_{Aa}) & \text{if } v_{Aa} < v_{As} \end{cases}
$$

where `v_{Aa}, v_{As} ∈ [0,1]` are the aggregated attacker/supporter strengths. DF-QuAD is well-defined for **acyclic** QBAFs (the paper restricts to acyclic throughout). *(p.2)*

### Connectivity (Defs 4-5) *(p.3)*
- **Path** between X and Y: sequence of distinct arguments `X = X_1, X_2, ..., X_n = Y` with each adjacent pair in `R = R⁻ ∪ R⁺`.
- **Directly connected**: `(B, A) ∈ R`.
- **Indirectly connected**: a path of length ≥3 exists from B to A and B is not directly connected.
- **Multifold connected**: B is directly or indirectly connected to A via at least two distinct paths.

## §4 The AAE Definition

### Definition 2 (AAE) *(p.3)*
Let A, B ∈ A with A the *topic argument*. For a perturbation ε ∈ [−τ(B), 0) ∪ (0, 1−τ(B)], let σ_ε(A) denote the strength of A under the QBAF Q' obtained from Q by replacing τ(B) with τ(B)+ε. The AAE from B to A is:

$$
\nabla\Big|_{B \mapsto A} = \lim_{\varepsilon \to 0} \frac{\sigma_\varepsilon(A) - \sigma(A)}{\varepsilon}
$$

This is the partial derivative of A's strength with respect to B's base score at the current state. *(p.3)*

### Definition 3 (Attribution Influence) *(p.3)*
- B has **positive** attribution influence on A iff ∇|_{B↦A} > 0.
- B has **negative** attribution influence on A iff ∇|_{B↦A} < 0.
- Either case = "non-zero" attribution influence.

## §4-5 Propositions / Closed Forms

### Proposition 1 (Direct Qualitative Attribution Influence) *(p.3)*
If (B, A) directly connected:
- If `(B, A) ∈ R⁻`, then `∇|_{B↦A} ≤ 0`.
- If `(B, A) ∈ R⁺`, then `∇|_{B↦A} ≥ 0`.

(Sign matches relation polarity.) *(Proof p.9)*

### Proposition 2 (Direct Quantitative Attribution Influence) *(p.4)*

$$
\nabla\Big|_{B \mapsto A} = \xi_B \cdot \big(1 - |v_{Ba} - v_{Bs}|\big) \prod_{\{Z \in \mathcal{A} \setminus B\,|\,(Z, A) \in \mathcal{R}^*\}} \big[1 - \sigma(Z)\big]
$$

where `R* ∈ {R⁻, R⁺}` is the relation linking B to A, and:

$$
\xi_B = \begin{cases}
-\tau(A) & \text{if } \mathcal{R}^* = \mathcal{R}^- \wedge v_{Aa} \ge v_{As} \\
\tau(A) - 1 & \text{if } \mathcal{R}^* = \mathcal{R}^- \wedge v_{Aa} < v_{As} \\
\tau(A) & \text{if } \mathcal{R}^* = \mathcal{R}^+ \wedge v_{Aa} > v_{As} \\
1 - \tau(A) & \text{if } \mathcal{R}^* = \mathcal{R}^+ \wedge v_{Aa} \le v_{As}
\end{cases}
$$

i.e. four cases on (relation polarity × attacker-vs-supporter dominance).

### Proposition 3 (Indirect Qualitative Attribution Influence) *(p.4)*
For X_1, ..., X_n ∈ A with n ≥ 3 indirectly connected through path φ = X_1, ..., X_n, let Θ = |S ∩ R⁻| be the number of attack edges on the path:
1. If Θ is odd, then `∇|_{X_1 ↦ X_n} ≤ 0`.
2. If Θ is even, then `∇|_{X_1 ↦ X_n} ≥ 0`.

(Sign equals product of edge signs along the path.)

### Proposition 4 (Indirect Quantitative Attribution Influence — chain rule) *(p.4)*
For X_1, ..., X_n indirectly connected through path φ = X_1, ..., X_n:

$$
\nabla\Big|_{X_1 \mapsto X_n} = \big(1 - |v_{X_1 a} - v_{X_1 s}|\big) \cdot \prod_{i=1}^{n-1} \frac{\nabla|_{X_i \mapsto X_{i+1}}}{1 - |v_{X_i a} - v_{X_i s}|}
$$

This is the gradient chain rule applied through the QBAF as a feed-forward computation graph.

### Properties (§5, restricted to DF-QuAD setting) *(pp.4-5)*

| # | Name | Statement | When satisfied |
|---|------|-----------|----------------|
| Prop 5 | **Explainability** | ∀A,B: ∇\|_{B↦A} ∈ ℝ is well-defined. | Always (by construction). |
| Prop 6 | **Missingness** | If B is disconnected from A, then ∇\|_{B↦A} = 0. | Always. *(Adapted from [29] SHAP.)* |
| Property 1 | **Completeness** | `−τ(B) · ∇\|_{B↦A} = σ′_B(A) − σ(A)`, where σ′_B(A) is the strength of A when τ(B) is reset to 0. | Prop 7: holds if B directly/indirectly connected. *Adapted from [42] (efficiency).* |
| Prop 8 | (negative) | Completeness can be **violated** if B is multifold connected to A. | — |
| Property 2 | **Counterfactuality** | If ∇\|_{B↦A} ≤ 0, then σ′_B(A) ≥ σ(A); if ∇\|_{B↦A} ≥ 0, then σ′_B(A) ≤ σ(A). | Prop 9: holds if directly/indirectly connected. *Adapted from [18].* |
| Prop 10 | (negative) | Counterfactuality can be **violated** if B is multifold connected to A. | — |
| Property 3 | **Agreement** | If τ(B)·∇\|_{B↦A} = τ(C)·∇\|_{C↦A}, then \|σ′_B(A) − σ(A)\| = \|σ′_C(A) − σ(A)\|. | Prop 11: directly connected. Prop 12: violated if multifold. *(p.4)* |
| Property 4 | **Monotonicity** | If τ(B)·∇\|_{B↦A} ≤ τ(C)·∇\|_{C↦A}, then \|σ′_B(A) − σ(A)\| ≤ \|σ′_C(A) − σ(A)\|. | Prop 13: directly connected. Prop 14: violated if multifold. *(p.4)* |

### Tractability (Prop 19, main paper p.5) *(p.5)*
All AAEs in a QBAF can be computed in **O(n)** time in the number of arguments (because DF-QuAD propagation itself is linear over a DAG and the closed forms above re-use the same v_{Aa}/v_{As} quantities). *(p.5)*

### Generalisability (Prop 20) *(p.5)*
AAEs are *generalisable* — definable for any gradual semantics, not just DF-QuAD; only the property guarantees are DF-QuAD-specific.

## §6 Case Studies

### Case Study 1: Fake News Detection *(pp.4-5)*
Adapted from a fake news QBAF in [28] (Kotonya & Toni, Sydney Lindt Cafe siege tweets). 8 arguments: source tweet A; replies B, C (positive/supports), D (attacks); replies E (replies to B), F (replies to D), G & H (reply to F).

Initial settings:
- τ(X) = 0.5 for all X.
- DF-QuAD strength σ(A) = **0.59375** > 0.5 ⇒ classified "True News".

**Table 1 — AAEs in descending order** *(p.5)*

| Argument | τ | σ′_X(A) | σ′_X(A) − σ(A) | ∇\|_{X↦A} |
|----------|---|---------|----------------|-----------|
| Reply2: C | 0.5 | 0.40625 | −0.18750 | **0.3750** |
| Reply1: B | 0.5 | 0.53125 | −0.06250 | 0.1250 |
| Reply5: F | 0.5 | 0.56250 | −0.03125 | 0.0625 |
| Reply6: G | 0.5 | 0.62500 | +0.03125 | −0.0625 |
| Reply7: H | 0.5 | 0.62500 | +0.03125 | −0.0625 |
| Reply4: E | 0.5 | 0.65625 | +0.06250 | −0.1250 |
| Reply3: D | 0.5 | 0.81250 | +0.21875 | **−0.4375** |

**Quantitative Analysis:** C has largest positive influence; D has largest negative (D directly attacks A AND has indirect supporters G, H attacking D's attacker F). E negative because it attacks supporter B. G, H smaller negative than B because farther from A.

**Property analysis on this example:** changing τ(B) anywhere in [0,1] does not change ∇|_{B↦A} = 0.125 (invariability). Disconnected pair (e.g. C, E) gives ∇=0 (missingness). Setting τ(C)=0 yields σ′_C(A) − σ(A) = −τ(C)·∇|_{C↦A} = −0.1875 (completeness + counterfactuality). G & H have identical |τ·∇| = 0.03125 ⇒ identical strength change (agreement). B's |τ·∇|=0.0625 < C's 0.1875 ⇒ |σ′_B(A) − σ(A)| < |σ′_C(A) − σ(A)| (monotonicity holds). All AAEs computed in linear time. *(p.5)*

### Case Study 2: Movie Recommender Systems *(p.6)*
QBAF from [17] (Cocarascu et al. ADAs over online review aggregation) for the movie *The Post*. Topic argument m. Features: f_A (acting), f_D (directing), f_W (writing). Sub-features: f'_A1, f'_A2 (sub-features of acting).

Base scores (regular font in Fig 5) → DF-QuAD strengths (bold):
- f_A: 0.16 → **0.26**
- f_D: 0.05 → **0.05**
- f_W: 0.02 → **0.02**
- f'_A1: 0.05 → **0.05**
- f'_A2: 0.07 → **0.07**
- m: 0.79 → **0.85**

**Table 2 — AAEs descending** *(p.6)*

| Argument | τ | σ′_X(m) | σ′_X(m) − σ(m) | ∇\|_{X↦m} |
|----------|---|---------|----------------|-----------|
| Acting (f_A) | 0.16 | 0.81954 | −0.02820 | **0.17625** |
| Actor2 (f'_A2) | 0.07 | 0.83660 | −0.01114 | 0.15920 |
| Actor1 (f'_A1) | 0.05 | 0.83995 | −0.00779 | 0.15585 |
| Directing (f_D) | 0.05 | 0.83995 | −0.00779 | 0.15584 |
| Writing (f_W) | 0.02 | 0.85194 | +0.00420 | **−0.21000** |

Despite Writing having largest *gradient magnitude* (−0.21), its low τ=0.02 means small actual strength change. Acting f_A has largest absolute change in σ(m) because high τ × positive gradient.

**Faithfulness check:** disconnected pair (f'_A2 attacking m through nothing direct) would give 0. Removing f_A: |τ(f_A)·∇| = 0.02820 > |τ(f_D)·∇| = 0.00779 ⇒ greater change in σ(m), so monotonicity holds across f_A vs f_D.

### Case Study 3: Fraud Detection *(SM Appendix C, pp.18-20)*
QBAF from [16] (Chen et al.). 48 arguments. Topic argument 1 = "We should start an investigation on this case as it is a fraud case". Argument 2 supports topic ("It is a fraud case"); argument 3 attacks ("It is not a fraud case"). All τ = 0.5.

Result: σ(1) = **0.2543945275247097** < 0.5 ⇒ "no investigation needed".

Of 48 arguments, **29 have positive AAE, 18 have negative AAE**, one is the topic itself. Argument 2 has largest positive AAE (4.99E-1); argument 3 has largest negative AAE (−7.81E-3). The average **magnitude of negative AAEs exceeds that of positive AAEs**, explaining the < 0.5 outcome despite there being more positive arguments. AAE values span roughly 5e-1 down to 4e-16 (deeply nested arguments have effectively zero gradient). *(p.20, Table 3)*

This case study demonstrates AAEs' utility for **debugging**: counting positive vs negative arguments alone misleads; the gradient-weighted contribution gives the true picture.

## Parameters / Quantities

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Base score | τ(A) | — | 0.5 (case studies) | [0, 1] | 2 | Per-argument prior strength |
| Strength | σ(A) | — | computed | [0, 1] | 2 | DF-QuAD output |
| Aggregate attacker strength | v_{Aa} | — | computed | [0, 1] | 2 | `1 − ∏(1 − σ(X))` over R⁻ predecessors |
| Aggregate supporter strength | v_{As} | — | computed | [0, 1] | 2 | `1 − ∏(1 − σ(X))` over R⁺ predecessors |
| AAE (gradient) | ∇\|_{B↦A} | — | computed | ℝ (typically bounded by τ(A)) | 3 | Partial derivative ∂σ(A)/∂τ(B) |
| Perturbation | ε | — | →0 | (−τ(B), 1−τ(B)) | 3 | Limit variable in def of ∇ |
| Path attack count | Θ | — | — | {0, 1, ...} | 4 | Parity determines sign in Prop 3 |
| Topic threshold | — | — | 0.5 | — | 5 | "True News" iff σ > 0.5; "investigate" iff σ > 0.5 |
| Computational complexity | — | time | O(n) | — | 5 | n = \|A\| |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | Population/Context | Page |
|---------|---------|-------|--------------------|------|
| Fake-news σ(A) | Strength | 0.59375 | Sydney siege QBAF, all τ=0.5 | 5 |
| Largest positive AAE (fake news) | ∇ | +0.3750 | Reply C → A | 5 |
| Largest negative AAE (fake news) | ∇ | −0.4375 | Reply D → A | 5 |
| Movie recommender σ(m) "The Post" | Strength | 0.85 | ADA QBAF | 6 |
| Largest positive AAE (movies) | ∇ | +0.17625 | Acting f_A → m | 6 |
| Largest negative AAE (movies) | ∇ | −0.21000 | Writing f_W → m | 6 |
| Fraud detection σ(1) | Strength | 0.2543945275247097 | 48-arg QBAF, τ=0.5 | 20 |
| Fraud detection positive/negative split | Count | 29 vs 18 | Of 47 non-topic args | 20 |

## Methods & Implementation Details
- Restricted to **acyclic** QBAFs throughout (cyclic QBAFs flagged as future work — DF-QuAD strength values defined by iterative procedure that may not converge; cites [31, 33]). *(p.6)*
- AAE computation uses the closed forms in Props 2 and 4 directly; no automatic differentiation required. Each AAE re-uses the v_{Aa}, v_{As} values from the DF-QuAD forward pass. *(p.5)*
- The chain-rule formula in Prop 4 lets you avoid repeated forward passes: compute direct AAEs along edges in DAG order, then multiply along paths.
- Visualisation: blue arrows for positive AAE, red for negative; thickness ∝ |∇|; a sorted bar chart on the right side of the figure mirrors the magnitudes. *(pp.5-6, Figs 4 & 6)*
- For property checks, completeness verification reduces to a single counterfactual evaluation (set τ(B)=0, recompute σ(A), check `−τ(B)·∇|_{B↦A} == σ′_B(A) − σ(A)`).

## Figures of Interest
- **Fig 1 (p.1):** Fraud detection in e-commerce QBAF (motivating example, ref [16]).
- **Fig 2 (p.2):** Generic example acyclic QBAF illustrating Definition 1.
- **Fig 3 (p.4):** Fake news QBAF (8 arguments, A topic, B/C/D direct, E/F/G/H indirect).
- **Fig 4 (p.5):** Visualisation of AAEs for fake news — coloured arrows + ranked bar chart.
- **Fig 5 (p.6):** Movie recommender QBAF for *The Post* (6 arguments incl. sub-features).
- **Fig 6 (p.6):** Visualisation of AAEs for movie recs.
- **Fig 11-12 (p.18):** Acyclic QBAF examples used in SM Examples 6 and 7.
- **Fig 13 (p.19):** Full 48-argument fraud-detection QBAF.

## Results Summary
AAEs successfully:
1. Differentiate the *quantitative* contribution of each argument to a topic, beyond what binary "supports/attacks" qualitative explanations convey. *(p.5)*
2. Are computable in linear time. *(p.5)*
3. Satisfy all six proposed faithfulness properties on directly/indirectly connected arguments. *(pp.4-5)*
4. Match human intuition on case studies — arguments that are direct attackers/supporters dominate; deeply nested arguments have small magnitudes. *(pp.5-6, 20)*
5. Reveal *non-obvious* dynamics — e.g. in fake-news case, indirect supporter F has positive influence on A despite being two attack-hops away (even parity); in fraud case, magnitude of negative AAEs outweighs sheer count of positive arguments. *(pp.5, 20)*

## Limitations
- **Acyclic QBAFs only.** Cyclic case is non-trivial because DF-QuAD strength may not converge (cites [31, 33]). *(p.6)*
- **DF-QuAD-specific properties.** While AAE definition generalises to any gradual semantics, the property guarantees (Props 5-14) are derived for DF-QuAD only. Authors flag Euler-based [3] and quadratic energy [32] semantics as targets for future analysis. *(p.6)*
- **Multifold connectivity violates completeness, counterfactuality, agreement, monotonicity.** Authors explicitly prove these can fail (Props 8, 10, 12, 14) when arguments reach the topic via multiple paths. No proposed remedy. *(pp.4-5)*
- **Single-argument focus.** AAEs measure influence of one argument at a time; collective influence of argument *sets* is left as future work. *(p.6)*
- **No human study.** All "intuitive plausibility" claims rest on author analysis of toy QBAFs. Formal user evaluation flagged as future work. *(p.6)*

## Arguments Against Prior Work
- **Qualitative XAI for AFs (e.g. [20] explanations-via-attacks, [17] template dialogues) is insufficient** for QBAFs because it ignores numerical strength information. *(p.1)* The AAE paper argues that quantitative reasoning (gradual semantics) deserves quantitative explanations.
- **ML feature attribution methods (LIME [39], SHAP [29], SILO [12], gradient methods [8])** explain input→output mappings of an opaque model but cannot explain *internal* dialectical interactions among arguments encoded in a QBAF. AAEs explicitly target intra-graph influences, not input-output. *(p.1)*
- **LIME's perturbation surrogate is computationally inefficient** when conditional independencies hold. *(p.1)* SHAP's exact Shapley computation is exponential. SILO requires post-hoc differentiation of approximations to differentiate non-differentiable classifiers and is computationally inefficient. AAE inherits gradient's efficiency without those overheads since QBAF DF-QuAD is exactly differentiable in closed form.
- **Existing argumentation explanation property catalogues** (e.g. [4] explainability, [29] missingness, [42] efficiency, [35] quantitative faithfulness, [18] counterfactuality) are scattered across literatures. The paper consolidates and adapts them to AAEs. *(pp.4-5)*

## Design Rationale
- **Why gradient instead of Shapley?** SHAP-style Shapley computation is exponential in number of features/arguments. Gradient is constant-time per edge plus a chain-rule traversal, hence O(n) overall. Authors explicitly compare AAE favourably against SHAP for runtime. *(pp.1, 5)*
- **Why DF-QuAD specifically?** DF-QuAD is "discontinuity-free" — the strength function is differentiable everywhere except at the v_{Aa}=v_{As} boundary, making `lim_{ε→0}` clean. Other gradual semantics (Euler, quadratic energy) would need separate analysis. *(p.4 footnote 4 implicit; p.6 future work)*
- **Why restrict to acyclic?** Cycles introduce iterative DF-QuAD that may not converge ⇒ ε-perturbation may diverge or oscillate. *(p.6)*
- **Why also have a *qualitative* sign rule (Prop 1, Prop 3) instead of only the closed form?** Sign-only properties are robust to numerical noise and useful for sanity checking; parity-of-attacks (Prop 3) gives a structural-only result independent of base scores. *(pp.3-4)*
- **Why visualise both arrows and bar chart?** Arrows show topology + direction; bar chart shows magnitude ordering — humans need both for fast comprehension. *(p.5)*

## Testable Properties (for any AAE implementation)
- **Sign correctness (Prop 1):** for direct attack edge, AAE ≤ 0; for direct support, ≥ 0. *(p.3)*
- **Parity correctness (Prop 3):** along an indirect path, sign of AAE = (−1)^Θ where Θ = # attack edges on the path. *(p.4)*
- **Chain rule (Prop 4):** indirect AAE = product of incident direct AAEs / `(1 − |v_{X_i a} − v_{X_i s}|)` factors along path. *(p.4)*
- **Explainability:** ∇|_{B↦A} ∈ ℝ for all A, B (no NaN, no undefined). *(p.4)*
- **Missingness:** if no path B → A in the DAG, then ∇|_{B↦A} = 0. *(p.4)*
- **Completeness on connected:** `−τ(B) · ∇|_{B↦A} = σ′_B(A) − σ(A)` to numerical precision when B is directly/indirectly (not multifold) connected. *(p.4)*
- **Counterfactuality on connected:** removing B (set τ(B)=0) moves σ(A) in the direction predicted by sign of ∇. *(p.4)*
- **Linear runtime:** total cost O(|A| + |R|) for all AAEs into a single topic. *(p.5)*
- **DF-QuAD recovers σ(A)** exactly via forward pass (not strictly testable for AAE itself but a precondition). *(p.2)*

## Relevance to This Project
This is the *anchor paper* for the project's quantitative-attribution-style explanation workstream. Direct relevance:
1. **Implement the gradient-based AAE in the project's argumentation backend.** Closed-form Props 2 + 4 give an O(n) algorithm — no SAT solver, no enumeration.
2. **Add property tests** for explainability/missingness/completeness/counterfactuality directly mirroring §5; the paper's Table 1 numbers (fake news QBAF) make a perfect regression fixture.
3. **Visualisation pattern** (blue/red coloured edges + sorted bar chart) is reusable for any graph-structured argumentation explanation.
4. **Caveat to surface to users:** completeness/counterfactuality break under *multifold connectivity*. The implementation should detect multifold paths and warn or fall back to a SHAP-style aggregation.
5. **Future-work direction relevant to project:** AAE for cyclic QBAFs (project's iterative QBAF reasoner could be the first to provide one), and AAE for Euler-based semantics (project supports both DF-QuAD and Euler).
6. The fraud-detection case study (SM C, 48 arguments, exact σ(1)=0.254...) is large enough to serve as a non-trivial integration test.

## Open Questions
- [ ] Can the property gap (completeness/counterfactuality under multifold connectivity) be closed by a path-decomposition or by aggregating per-path contributions (Shapley-on-paths)?
- [ ] Does the chain rule (Prop 4) extend to cyclic QBAFs via fixed-point differentiation (implicit function theorem)?
- [ ] How does AAE compare numerically to SHAP-on-arguments on these same QBAFs? Authors don't run that head-to-head.
- [ ] What's the analogue of Prop 2 for Euler-based gradual semantics? For quadratic energy?
- [ ] Sub-feature handling: in the movie case study f'_A1, f'_A2 are sub-features of f_A. Does the AAE correctly attribute combined sub-feature contribution? Authors don't formalise sub-features as a class.
- [ ] User evaluation — do AAE rankings match human intuition under controlled study?

## Related Work Worth Reading
- **[10] Baroni, Rago, Toni 2018** — origin of QBAFs and DF-QuAD semantics. Mandatory reading for implementing.
- **[28] Kotonya & Toni** — fake-news argumentation pipeline (case study 1 source).
- **[17] Cocarascu et al.** — Argumentative Dialogical Agents (ADAs) for movie reviews (case study 2 source).
- **[16] Chen et al.** — fraud detection AF (case study 3 source, 48-argument QBAF).
- **[29] Lundberg & Lee 2017** — SHAP. Source of *missingness* property.
- **[42] Sundararajan et al.** — Integrated Gradients. Source of *completeness* (efficiency) property.
- **[35] Potyka 2021** — quantitative faithfulness in QBAFs. Property catalogue overlap.
- **[18] Datta, Sen, Zick 2016 (QII)** — counterfactual influence. Source of *counterfactuality* property.
- **[3] Amgoud et al.** — Euler-based gradual semantics (future-work target).
- **[32] Mossakowski & Neuhaus** — quadratic energy semantics (future-work target).
- **[4] Amgoud, Ben-Naim** — explainability property origin.
- **[8] Baehrens et al.** — gradient-scoring feature attribution (the most directly related ML-XAI ancestor).
- **[39] Ribeiro et al.** — LIME.
- **[12] Chen et al.** — SILO.
- **[43] Shrikumar et al.** — DeepLIFT.
- **[44] Vassiliades et al. KER 2021** — argumentation + XAI survey.
- **[31, 33]** — non-convergence of iterative DF-QuAD on cyclic QBAFs.
