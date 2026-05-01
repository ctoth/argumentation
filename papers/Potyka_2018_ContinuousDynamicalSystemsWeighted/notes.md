---
title: "Continuous Dynamical Systems for Weighted Bipolar Argumentation"
authors: "Nico Potyka"
year: 2018
venue: "KR 2018 (Proceedings of the Sixteenth International Conference on Principles of Knowledge Representation and Reasoning)"
doi_url: "https://doi.org/10.5555/3393515.3393530"
produced_by:
  agent: "claude-opus-4-6-1m"
  skill: "paper-reader"
  timestamp: "2026-03-28T22:39:49Z"
---
# Continuous Dynamical Systems for Weighted Bipolar Argumentation

## One-Sentence Summary
Presents a continuous dynamical systems approach (quadratic energy model) for computing gradual semantics of weighted bipolar argumentation frameworks (WBAFs) that guarantees convergence for acyclic graphs and provides strong convergence properties for cyclic graphs.

## Problem Addressed
Weighted bipolar argumentation frameworks assign initial weights to arguments and compute final strengths based on attackers and supporters, but existing approaches (DF-QuAD, Euler-based) either fail to converge for cyclic graphs or lack formal convergence guarantees. The paper proposes a continuous iterative approach based on energy models that addresses convergence issues systematically. *(p.0)*

## Key Contributions
- Introduces a **quadratic energy model** that defines strength values for acyclic BAGs (bipolar argumentation graphs) via a continuous iteration scheme *(p.7)*
- Proves convergence of the quadratic energy model for all acyclic BAGs *(p.5)*
- Demonstrates that for cyclic BAGs, the quadratic energy model converges in most cases and the Euler-based model converges relatively well *(p.7)*
- Shows that the quadratic energy model satisfies key axiomatic properties: anonymity, independence, directionality, neutrality, equivalence, resilience, strengthening, weakening, and others *(p.3-4)*
- Provides a systematic framework for studying convergence by connecting argumentation semantics to dynamical systems theory *(p.0)*
- Proposes using the graph structure of the WBAF to determine the topological ordering for iterative computation *(p.5)*

## Methodology
The paper formalizes weighted bipolar argumentation as a continuous dynamical system. It defines a BAG (Bipolar Argumentation Graph) as a tuple (A, R, S, τ) where A is a set of arguments, R is the attack relation, S is the support relation, and τ is the initial weight function. The approach uses iterative computation:

1. Define an aggregation function that combines attack and support strengths
2. Define an influence function that maps aggregated values to final strengths
3. Iterate until convergence (fixed point)

The quadratic energy model is compared against DF-QuAD and Euler-based models on both acyclic and cyclic graphs. *(p.0, p.5)*

## Key Equations / Statistical Models

### Definition 1: Bipolar Argumentation Graph (BAG)
A BAG is a tuple $(A, R, S, \tau)$ where:
- $A$ is a finite set of arguments
- $R \subseteq A \times A$ is the attack relation
- $S \subseteq A \times A$ is the support relation
- $\tau : A \to [0,1]$ is the initial weight function

Where: $R$ and $S$ are disjoint (no argument both attacks and supports the same target). *(p.1)*

### Aggregation Function
$$
\text{agg}(a) = \sum_{(b,a) \in S} \sigma(b) - \sum_{(b,a) \in R} \sigma(b)
$$
Where: $\sigma(b)$ is the current strength of argument $b$, the sum of supporter strengths minus the sum of attacker strengths. *(p.1)*

### Quadratic Energy Model - Iteration Scheme (Proposition 19)
$$
f_a(\sigma) = \begin{cases} \tau(a) + \text{agg}(a) \cdot (1 - \tau(a)) & \text{if } \text{agg}(a) \geq 0 \\ \tau(a) + \text{agg}(a) \cdot \tau(a) & \text{if } \text{agg}(a) < 0 \end{cases}
$$
Where: $f_a$ is a function that depends on the initial weight and the strength of attackers and supporters; the strength values $\sigma_a$ are computed in topological order. If $f$ is continuously differentiable with respect to all involved strength values, then for all BAG $A$, the system converges. *(p.7)*

### Quadratic Energy Model - Unique Solution for Acyclic BAGs
$$
\sigma^* = f(\sigma^*)
$$
with initial conditions $\sigma_a(0) = \tau(a)$ for all $a \in A$.

A unique solution of $\frac{d\sigma}{dt} = f(\sigma) - \sigma$ exists on $[0, \infty)$ for acyclic BAGs. *(p.7)*

### DF-QuAD Aggregation (from Rago et al. 2016)
$$
\sigma_{t+1}(a) = \begin{cases} \tau(a) + \tau(a) \cdot (1 - \tau(a)) \cdot v_S - \tau(a) \cdot v_A & \text{combined} \end{cases}
$$
Where: $v_S$ is the result of combining supporters, $v_A$ is the result of combining attackers. The combination uses a specific recursive formula. *(p.0)*

### Euler-Based Model (from Amgoud et al.)
Uses Euler number based semantics where the influence function involves the Euler constant $e$:
$$
\sigma_{t+1}(a) = \frac{1}{1 + (1/\tau(a) - 1) \cdot e^{-\alpha \cdot \text{agg}(a)}}
$$
Where: $\alpha$ controls the steepness of the sigmoid. Note: the exact Euler formulation from Amgoud and Ben-Naim 2017 is referenced throughout. *(p.1)*

### Proposition 2 (Equilibria/Fixed Points)
For a BAG, equilibrium states of the Euler-based restricted semantics cause an oscillation because mean attack and support can cycle. An argument's initial weight $\tau$ and its supporters/attackers determine whether equilibrium exists. *(p.2)*

### Lemma 1 (Bounded Strengths)
$$
\sigma(a) \in [0,1] \text{ for all } a \in A \text{ and all } t \geq 0
$$
Where: For all arguments, strengths always remain in $[0,1]$ provided the initial conditions $\sigma(0) = \tau(a) \in [0,1]$. *(p.2)*

### Proposition 16 (Convergence for Acyclic BAGs)
For an acyclic BAG, the quadratic energy model converges. Since there has no predecessors, the energy at argument 1 is 0 for all time. The derivative is 0 for all time. Since $\sigma_1(0) = \tau(1)$, the derivative is 0 for all time. For arguments $a > 1$, the variable $a$ can only be influenced by arguments $1, \ldots, a-1$. Since the derivative at all predecessors is eventually 0, the energy at $a$ will converge to a limit $L$. By continuity, the derivative at $a$ will also converge to $w(L) - \sigma(L) = 0$. *(p.5)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Initial weight | τ(a) | — | — | [0,1] | p.1 | Per-argument initial strength |
| Strength value | σ(a) | — | — | [0,1] | p.1 | Computed iteratively |
| Aggregation value | agg(a) | — | — | [-n, n] | p.1 | Sum of supporter minus attacker strengths |
| Number of arguments | \|A\| | — | — | 1-1000+ | p.7 | Tested up to thousands |
| Number of random graphs | — | — | 100 | — | p.7 | Per cycle length in experiments |
| Cycle lengths tested | — | — | — | 3-100 | p.7 | In convergence experiments |
| Maximum iterations | — | — | 100 | — | p.7 | For convergence testing |
| Convergence threshold | ε | — | 0.0001 | — | p.7 | Maximum change between iterations |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| Quadratic energy convergence (acyclic) | convergence rate | 100% | — | — | All acyclic BAGs | p.5 |
| Quadratic energy convergence (cyclic) | convergence rate | ~99%+ | — | — | Random cyclic BAGs with thousands of nodes | p.7 |
| Euler-based convergence (cyclic) | convergence rate | slightly lower | — | — | Random cyclic BAGs | p.7 |
| DF-QuAD convergence (cyclic) | convergence rate | fails for some cycles | — | — | Cyclic BAGs | p.5 |
| Runtime (1000 args, acyclic) | time | ~0.1s | — | — | Single core, Land Cray 17.470 with 4 GB RAM, Windows 10 | p.7 |

## Methods & Implementation Details
- BAG defined as tuple (A, R, S, τ) with disjoint attack and support relations *(p.1)*
- Three models compared: DF-QuAD (Rago et al. 2016), Euler-based (Amgoud and Ben-Naim 2017), quadratic energy model (this paper) *(p.0)*
- Topological ordering used for acyclic graphs to determine computation order — process arguments with no predecessors first *(p.5)*
- For acyclic BAGs: compute strength in topological order; each argument's strength depends only on predecessors already computed *(p.5)*
- For cyclic BAGs: iterate the system and check for convergence within max iterations *(p.7)*
- Implementation in R; code and all BAGs downloadable from linked repository *(p.7)*
- Experiments: random cyclic BAGs generated with 100 random graphs per cycle length (3-100), with random edge types (attack/support) and random initial weights *(p.7)*
- Convergence checked: maximum change between iterations < ε = 0.0001 *(p.7)*
- The quadratic energy model is guaranteed to converge for acyclic BAGs; for cyclic BAGs convergence is an empirical observation *(p.5, p.7)*

## Figures of Interest
- **Fig 1 (p.2):** BAG from Amgoud and Ben-Naim 2017 showing initial weight, strength under quadratic energy model, strength under Euler-based restricted semantics
- **Fig 2 (p.2):** Long-term behaviour of σ* for BAG in Figure 1, showing convergence from different starting values between 0 and 1
- **Fig 3 (p.4):** Duality Example showing initial weight, strength under quadratic energy model, strength under Euler-based restricted semantics
- **Fig 4 (p.5):** Weakening and Strengthening counterexample — nodes show initial weight under quadratic energy model, strength under Euler-based restricted semantics
- **Fig 5 (p.6):** Cyclic BAG showing initial weight, strength under quadratic energy, and Euler-based model, with convergence behaviour
- **Fig 6 (p.6):** Long-term behaviour of continuous Euler-based model for BAG in Figure 5 — note it does not converge to the strength values defined by the Euler-based semantics
- **Fig 7 (p.7):** Runtime results for computing equilibria — min, mean, and maximum runtimes on random BAGs with 100-1000 nodes; cyclic BAGs with 5 arguments and 96%+ convergence rate
- **Fig 8 (p.8):** Long-term behaviour of continuous Euler-based model for BAG in Figure 5 — comparison

## Results Summary
The quadratic energy model converges for all acyclic BAGs (proven) and for virtually all tested cyclic BAGs (empirically demonstrated). It satisfies most desirable axiomatic properties. The Euler-based model has convergence issues even for some simple cyclic cases. DF-QuAD fails to converge for certain cyclic structures. The quadratic energy model provides a principled continuous dynamical systems framework that can be extended to other argumentation models. Runtime is efficient — under 0.1 seconds for 1000-argument acyclic BAGs. *(p.5, p.7)*

## Limitations
- Convergence for cyclic BAGs is only demonstrated empirically, not proven *(p.7)*
- The quadratic energy model does not satisfy the Strengthening axiom in all cases (counterexample in Figure 4) — specifically, there exist BAGs where adding a supporter does not strictly increase the strength *(p.4)*
- The Weakening axiom is also violated in certain configurations *(p.4)*
- Does not handle weighted edges (only binary attack/support relations with argument weights) *(p.1)*
- The continuous dynamical systems approach may be more computationally expensive than direct iteration for simple cases *(p.8)*
- Only binary relations (attack or support) — no graded attack/support strengths on edges *(p.1)*
- Authors acknowledge that convergence guarantees for cyclic graphs remain an open problem; only provide convergent guarantees for some simple special cases (e.g., the BAG contains only support relations) *(p.6)*

## Arguments Against Prior Work
- **DF-QuAD (Rago et al. 2016):** The paper demonstrates that DF-QuAD can fail to converge for cyclic graphs. Specifically, the discrete iteration can oscillate. The quadratic energy model avoids this by using a continuous dynamical system approach. *(p.0, p.5)*
- **Euler-based semantics (Amgoud and Ben-Naim 2017):** The continuous Euler-based model does not converge to the same values as the discrete Euler-based semantics in cyclic cases (Figure 6). The Euler-based approach also has issues with the Strengthening property. *(p.6)*
- **General critique of discrete approaches:** Discrete iteration schemes can miss fixed points or oscillate. The continuous dynamical systems approach provides a more principled mathematical framework for convergence analysis. *(p.0)*
- **Existing axiomatic approaches:** Previous work defines axioms but does not always check satisfiability or provide models that satisfy all axioms simultaneously. This paper systematically checks which axioms each model satisfies. *(p.3-4)*

## Design Rationale
- **Why continuous dynamical systems?** Discrete iteration can oscillate or diverge for cyclic graphs. Continuous systems provide tools from dynamical systems theory (Lyapunov stability, convergence theorems) that can prove convergence properties. *(p.0, p.7)*
- **Why quadratic energy model?** It satisfies more axioms than alternatives, converges provably for acyclic graphs, and empirically converges for cyclic graphs. The energy function provides a natural interpretation — arguments settle to minimal-energy states. *(p.7, p.8)*
- **Why topological ordering for acyclic graphs?** It allows computing strengths in a single pass through the graph, with each argument's strength depending only on already-computed predecessors. This guarantees convergence and is computationally efficient. *(p.5)*
- **Why not just DF-QuAD?** DF-QuAD conflates initial weight with base score and can fail to converge on cycles. The quadratic energy model separates these concerns more cleanly. *(p.0, p.5)*

## Testable Properties
- Strengths always remain in [0,1] for all arguments under the quadratic energy model *(p.2)*
- For acyclic BAGs, the quadratic energy model always converges to a unique fixed point *(p.5)*
- An argument with no attackers and no supporters retains its initial weight: σ(a) = τ(a) *(p.3)*
- Anonymity: renaming arguments does not change strengths *(p.3)*
- Independence: strength of a depends only on its direct attackers and supporters (and their strengths) *(p.3)*
- Directionality: arguments not connected to a do not influence σ(a) *(p.3)*
- Neutrality: if agg(a) = 0, then σ(a) = τ(a) *(p.3)*
- Equivalence: isomorphic sub-BAGs produce same strengths *(p.3)*
- Monotonicity: increasing a supporter's initial weight does not decrease the argument's strength; increasing an attacker's initial weight does not increase it *(p.3)*
- For cyclic BAGs, the quadratic energy model empirically converges in >99% of random instances *(p.7)*
- If all relations are support only, convergence is guaranteed even for cyclic BAGs *(p.6)*

## Relevance to Project
This paper is directly relevant to propstore's argumentation layer. The quadratic energy model provides an alternative gradual semantics for weighted bipolar argumentation frameworks that could complement or replace DF-QuAD. Key relevance:

1. **Convergence guarantees:** The quadratic energy model has proven convergence for acyclic BAGs and strong empirical convergence for cyclic BAGs — this is better than DF-QuAD's convergence properties.
2. **Axiomatic properties:** Systematic comparison of which axioms are satisfied helps in choosing the right semantics for propstore's use cases.
3. **Continuous dynamics:** The dynamical systems perspective could enable analysis of argument strength stability and sensitivity.
4. **Cyclic graph handling:** Propstore's argumentation graphs may contain cycles (mutual attacks, support loops); the quadratic energy model handles these more robustly than DF-QuAD.

## Open Questions
- [ ] Can the convergence proof be extended to all cyclic BAGs, not just support-only cycles?
- [ ] How does the quadratic energy model compare to DF-QuAD in propstore's specific use cases?
- [ ] What is the relationship between the continuous dynamical system's fixed points and Dung-style extensions?
- [ ] Can weighted edges (graded attack/support strengths) be incorporated?
- [ ] How does the model perform with very deep argumentation graphs (long chains)?

## Related Work Worth Reading
- Amgoud, L. and Ben-Naim, J. 2017. Evaluation of arguments from support relations: Axioms and semantics. IJCAI 2017 — defines the Euler-based semantics this paper improves upon
- Rago, A., Toni, F., Aurisicchio, M., and Baroni, P. 2016. Discontinuity-free QuAD — the DF-QuAD model compared against
- Baroni, P., Rago, A., and Toni, F. 2019. From fine-grained properties to broad principles for gradual argumentation — broader axiomatic framework
- Mossakowski, T. and Neuhaus, F. 2018. Modular semantics for bipolar weighted argumentation — related modular approach
- Cayrol, C. and Lagasquie-Schiex, M.C. 2005. Gradual valuation in bipolar argumentation frameworks — foundational bipolar AF work

## Collection Cross-References

### Already in Collection
- [[Rago_2016_DiscontinuityFreeQuAD]] — DF-QuAD model, one of the main comparison targets in this paper; Potyka demonstrates convergence failures for cyclic graphs
- [[Rago_2016_AdaptingDFQuADBipolarArgumentation]] — adaptation of DF-QuAD for bipolar argumentation
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — foundational bipolar AF work that defines the support+attack framework this paper builds on
- [[Bonzon_2016_ComparativeStudyRanking-basedSemantics]] — comparative study of ranking-based semantics; overlapping axiomatic analysis
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — alternative equational approach to numerical argument strength computation

### New Leads (Not Yet in Collection)
- Amgoud and Ben-Naim (2017) — "Evaluation of arguments from support relations: Axioms and semantics" — defines the Euler-based semantics that this paper directly improves upon
- Baroni, Rago, and Toni (2019) — "From fine-grained properties to broad principles for gradual argumentation" — broader axiomatic framework for gradual semantics
- Mossakowski and Neuhaus (2018) — "Modular semantics for bipolar weighted argumentation" — complementary modular approach presented at the same venue

### Cited By (in Collection)
- [[Freedman_2025_ArgumentativeLLMsClaimVerification]] — references Potyka 2018 for continuous dynamical systems approach to gradual semantics; QEM (Quantitative Energy Model) in that paper likely refers to the quadratic energy model defined here
- [[Hunter_2021_ProbabilisticArgumentationSurvey]] — Potyka is a co-author; references his work on epistemic probabilistic argumentation
- [[AlAnaissy_2024_ImpactMeasuresGradualArgumentation]] — cites Potyka's later work on contribution functions for QBAFs

### Conceptual Links (not citation-based)
- [[Freedman_2025_ArgumentativeLLMsClaimVerification]] — uses DF-QuAD for gradual semantics; Potyka's quadratic energy model is a direct alternative with better convergence properties for cyclic graphs
- [[Gabbay_2012_EquationalApproachArgumentationNetworks]] — both papers define numerical strength computation via equations over [0,1]; Gabbay uses equation families (Eq_inverse, Eq_max), Potyka uses continuous dynamical systems — different formalisms converging on the same goal of principled numerical semantics
- [[Amgoud_2008_BipolarityArgumentationFrameworks]] — foundational bipolarity work; Potyka's model operates over the same bipolar argumentation structure
- [[Matt_2008_Game-TheoreticMeasureArgumentStrength]] — alternative approach to argument strength via game theory; both aim to compute graded acceptance values
- [[Dunne_2011_WeightedArgumentSystemsBasic]] — weighted argumentation systems; related but focuses on extension-based semantics rather than gradual semantics
- [[Leite_2011_SocialAbstractArgumentation]] — social abstract argumentation with votes as weights; different weight interpretation but same convergence concerns for iterative computation
