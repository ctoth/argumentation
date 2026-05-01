---
title: "Probabilistic Argumentation Frameworks"
authors: "Hengfei Li, Nir Oren, Timothy J. Norman"
year: 2011
venue: "COMMA 2012 (Computational Models of Argument)"
---

# Probabilistic Argumentation Frameworks

## One-Sentence Summary
Defines PrAF (Probabilistic Argumentation Frameworks) that extend Dung AFs with independent probabilities on arguments and defeats, computes acceptance likelihood by marginalizing over all inducible sub-DAFs, and provides a Monte Carlo approximation algorithm with convergence guarantees. *(p.0)*

## Problem Addressed
Standard Dung AFs treat argument existence and attack relations as certain. In real dialogues, uncertainty exists about whether arguments/defeats are present (e.g., participants may or may not raise certain points). This paper provides a principled way to associate probabilities with arguments and defeats, then compute the likelihood that a set of arguments is justified under any Dung semantics. *(p.0-1)*

## Key Contributions
- **PrAF definition**: A 4-tuple extending Dung AF with probability functions over arguments and defeats *(p.2)*
- **Exact computation**: Enumerates all inducible DAFs, checks semantic evaluation for each, marginalizes — exponential complexity *(p.3-4)*
- **Monte Carlo approximation**: Algorithm 1 samples DAFs proportional to their probability, counts semantic satisfaction — polynomial per iteration *(p.5)*
- **Convergence bound**: Uses Agresti-Coull confidence intervals to determine stopping condition for desired error tolerance *(p.6-7)*
- **Coalition formation application**: Extends PrAFs to compute likelihood of coalition success *(p.11)*
- **Applicability to ANY Dung semantics**: grounded, preferred, stable, complete — the framework is parametric in semantic evaluation function *(p.1-2)*

## Methodology

### The Constellations Approach
A PrAF assigns independent probabilities to each argument and each defeat. The set of all possible sub-frameworks (DAFs) forms the "constellation" — each DAF is a possible world. The probability of a set of arguments being justified equals the sum of probabilities of all DAFs in which that set is justified under the chosen semantics. *(p.2-4)*

### Core Definitions

**Definition 1 (Dung AF):** $DAF$ is a pair $(Arg, Def)$ where $Arg$ is a set of arguments, and $Def \subseteq Arg \times Arg$ is defeats. *(p.1)*

**Definition 2 (PrAF):** A Probabilistic Argumentation Framework $PrAF$ is a tuple $(A, P_A, D, P_D)$ where $(A, D)$ is a DAF, $P_A : A \to [0,1]$ and $P_D : D \to [0,1]$. *(p.2)*

- $P_A(a)$ = probability that argument $a$ exists
- $P_D((f,t))$ = probability that defeat from $f$ to $t$ exists
- These represent likelihoods of existence, implicitly conditional probabilities *(p.2)*

**Definition 3 (Inducing a DAF from PrAF):** A DAF $(Arg, Def)$ can be induced from PrAF if: *(p.2)*
1. $Arg \subseteq A$ (arguments are a subset)
2. $Def \subseteq \{(f,t) \in D : f,t \in Arg\}$ (defeats only between present arguments)
3. For each $a \in A$: $a \notin Arg \Rightarrow \forall (a,b) \in D, (b,a) \in D$, those defeats also absent
4. A defeat can only appear if BOTH its source and target arguments are present

This is the "subcontext" concept — each inducible DAF is a possible world/context. *(p.2-3)*

## Key Equations

### Probability of a specific induced DAF

$$
P_{PrAF}(AF) = \prod_{a \in Arg} P_A(a) \cdot \prod_{a \notin Arg} (1 - P_A(a)) \cdot \prod_{d \in Def} P_D(d) \cdot \prod_{d \notin Def, both\_endpoints\_in\_Arg} (1 - P_D(d))
$$
Where: $Arg$ = arguments in the induced DAF, $Def$ = defeats in the induced DAF, products over present/absent arguments and defeats respectively.
*(p.3-4)*

### Probability of all inducible DAFs (Proposition 1)

$$
\sum_{AF \in D(PrAF)} P_{PrAF}(AF) = 1
$$
Where: $D(PrAF)$ = set of all DAFs inducible from $PrAF$. The probabilities form a proper distribution. *(p.4)*

### Semantic evaluation function

$$
\xi^S(AF, X) \in \{true, false\}
$$
Where: $S$ = Dung semantics (grounded/preferred/stable/complete), $AF$ = a DAF, $X$ = set of arguments to check. Returns true iff $X$ is justified under $S$ in $AF$. *(p.4)*

### Acceptance probability (Equation 2)

$$
P_{PrAF}(X) = \sum_{AF \in D(PrAF)} P_{PrAF}^I(AF) \cdot \xi^S(AF, X)
$$
Where: $P_{PrAF}^I(AF)$ = probability of induced DAF $AF$, $X$ = query set of arguments. This marginalizes over all possible worlds. *(p.4)*

### Likelihood of X being consistent with semantics S

$$
P_{PrAF}(X) = \sum_{PrAF' \in D(PrAF)} P_{PrAF}(PrAF') \text{ where } \xi^S(AF', X) = true
$$
*(p.4)*

### Normal approximation confidence interval (Equation 3)

$$
p' \pm z_{1-\alpha/2} \sqrt{\frac{p'(1-p')}{n}}
$$
Where: $p'$ = observed proportion, $n$ = number of trials, $z$ = normal quantile. *(p.6)*

### Required trials for error bound (Equation 4 — Normal)

$$
N > \frac{z^2 \cdot p'(1-p')}{\epsilon^2}
$$
Where: $\epsilon$ = desired error level, $z = z_{1-\alpha/2}$, $p'$ = observed probability. *(p.6)*

### Required trials — Agresti-Coull corrected (Equation 5)

$$
N > \frac{4p'(1-p')}{\epsilon^2} - 4
$$
Where: $p'$ = observed success ratio, $\epsilon$ = desired error. At 95% confidence with $z \approx 1.96$, this provides the stopping condition for Algorithm 1. *(p.7)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Argument probability | $P_A(a)$ | - | - | [0,1] | 2 | Independent per argument |
| Defeat probability | $P_D((f,t))$ | - | - | [0,1] | 2 | Independent per defeat relation |
| Number of MC trials | $N$ | - | - | $\mathbb{N}$ | 5 | Determined by convergence criterion |
| Error tolerance | $\epsilon$ | - | 0.01 | (0,1) | 8 | Desired approximation error |
| Confidence level | $1-\alpha$ | - | 0.95 | (0,1) | 6 | For convergence bound |
| Confidence interval half | $z_{1-\alpha/2}$ | - | 1.96 | - | 6 | Normal quantile for 95% CI |

## Implementation Details

### Algorithm 1: Monte Carlo Approximation of $P_{PrAF}(X)$ *(p.5)*

**Input:** PrAF = $(A, P_A, D, P_D)$, query set $X \subseteq A$, number of trials $N$, semantic evaluation function $\xi^S$

**Procedure:**
1. $Count = 0$
2. For $I = 0$ to $N$:
   a. $Arg = \{\}$, $Def = \{\}$
   b. For all $a \in A$: generate random $r \in [0,1]$; if $P_A(a) \geq r$ then $Arg = Arg \cup \{a\}$
   c. For all $(f,t) \in D$ such that $f,t \in Arg$: generate random $r \in [0,1]$; if $P_D((f,t)) \geq r$ then $Def = Def \cup \{(f,t)\}$
   d. If $\xi^S((Arg, Def), X) = true$ then $Count = Count + 1$
3. Return $Count / N$

**Key implementation notes:**
- Step 2c: defeats are only sampled if BOTH endpoints are present — this enforces Definition 3 *(p.5)*
- $\xi^S$ is a black box — any Dung semantics checker can be plugged in *(p.5)*
- The `for` loop can be replaced with a `while` loop using the Agresti-Coull stopping condition (Equation 5) *(p.7)*
- **Independence assumption**: the probability of one argument appearing is independent of others. Paper notes this will be relaxed in future work *(p.3)*

### Adaptive stopping variant *(p.7)*
Replace the fixed `for I = 0 to N` with a `while` loop:
- After each iteration, compute current $p' = Count / I$
- Compute required $N$ from Equation 5
- If current iteration count exceeds required $N$, terminate

### Exact computation *(p.3-4)*
- Enumerate all $2^{|A|+|D|}$ possible DAFs (each argument/defeat present or absent)
- Filter to valid inducible DAFs (Definition 3 constraints)
- For each, compute $P_{PrAF}(AF)$ and check $\xi^S$
- Sum probabilities where $\xi^S = true$
- **Complexity**: exponential in $|A| + |D|$ — each element is binary present/absent

### Data structures needed *(p.2-3)*
- PrAF: set of arguments with probability map, set of defeats with probability map
- DAF: subset of arguments, subset of defeats (both as sets)
- Semantic evaluation function: takes (DAF, X) returns bool
- The set $D(PrAF)$: all inducible DAFs — enumerate lazily or sample

### Worked Example *(p.3)*
PrAF with 4 arguments $\{a, b, c, d\}$:
- $P_A$: $a=0.8$, $b=0.5$, $c=0.8$, $d=0.5$
- Defeats: $(a,b)$, $(b,a)$, $(c,d)$, $(d,c)$ — all with $P_D = 1$
- Defeat relations have no uncertainty associated (prob = 1 for each)
- Grounded extension of 3 out of 4 induced DAFs contains $\{a\}$
- $P_{PrAF}(\{a\}) = 0.8$ (by summing over all DAFs where $\{a\}$ is in grounded extension)

## Figures of Interest
- **Fig 1 (p.3):** Graphical depiction of PrAF with 4 arguments, nodes labeled with probabilities, showing attack relations
- **Fig 2 (p.7):** 3D surface showing relationship between variable likelihood (0-1), number of trials (0-200), and error — error is highest at probability 0.5 and decreases toward extremes
- **Fig 3 (p.8):** Runtime comparison: exact method (exponential curve) vs Monte Carlo at $\epsilon=0.01$ and $\epsilon=0.005$ — MC overtakes exact at ~13-15 arguments
- **Fig 4 (p.9):** Iterations and CPU time for MC approach across PrAF sizes — iterations depend on joint probability, not PrAF size; CPU time scales linearly
- **Fig 5 (p.11):** PrAF for coalition formation example with roles (pilot $p$, mechanics $b$, $j$)

## Results Summary
- Exact approach: exponential in number of arguments — impractical beyond ~13 arguments *(p.8)*
- Monte Carlo: iterations depend only on the joint probability being estimated (worst case at $p=0.5$), not on PrAF size; CPU time per iteration is linear in $|A|+|D|$ *(p.9)*
- MC overtakes exact at ~13 arguments ($\epsilon=0.01$) or ~15 arguments ($\epsilon=0.005$) *(p.8)*
- Convergence: error at extreme probabilities (near 0 or 1) is resolved much faster than at 0.5 *(p.7)*
- Implementation in SWI-Prolog; defeats all set to probability 1 in experiments *(p.8)*

## Limitations
- **Independence assumption**: argument and defeat probabilities are treated as independent — correlated uncertainties not modeled *(p.3)*
- **Exponential exact method**: only feasible for small frameworks (~13 args) *(p.4, 8)*
- **Scalability of coalition application**: identifying all possible coalitions doesn't scale *(p.11)*
- **Only Dung semantics**: no structured argumentation (ASPIC+), no support relations *(p.12)*
- **No conditional probabilities**: $P_A$ and $P_D$ are marginal, not conditioned on other arguments/defeats *(p.3)*

## Arguments Against Prior Work
- Prior work on likelihoods in argumentation focused on "strength" measures as proxies (e.g., number of attackers, numerical values assigned to arguments) — these don't capture probabilistic uncertainty about argument/defeat existence *(p.12)*
- Weighted argument systems [21] use a value between 0 and 1 to model strength but this describes "to what degree an argument holds or attacks another argument" — different from existence probability *(p.12)*
- Fuzzy argumentation frameworks [24] model vagueness, not probabilistic uncertainty *(p.12)*
- Trust/reputation frameworks [29,30] associate probabilities with agents rather than arguments *(p.12)*

## Design Rationale
- **Why probabilities on existence, not strength**: Existence probability captures dialogue uncertainty (will an argument be raised?) rather than argument quality. These are orthogonal concerns. *(p.0-1)*
- **Why independent probabilities**: Simplifying assumption enabling product-form computation. Correlation is acknowledged as future work. *(p.3)*
- **Why Monte Carlo over exact**: Exact is $O(2^{|A|+|D|})$; MC is $O(N \cdot (|A|+|D|))$ where $N$ depends only on desired accuracy, not framework size. *(p.5, 8-9)*
- **Why Agresti-Coull over normal approximation**: Normal CI breaks down when observed proportion is 0 or 1 (which happens when $P_{PrAF}(X) \approx 0$ or $\approx 1$). Agresti-Coull adds pseudo-observations to handle this edge case. *(p.6-7)*
- **Parametric in semantics**: The $\xi^S$ function is a black box — any Dung semantics can be used without changing the framework. This is a deliberate design choice. *(p.4-5)*

## Testable Properties
- Sum of all induced DAF probabilities = 1 (Proposition 1) *(p.4)*
- For PrAF where all $P_A = 1$ and all $P_D = 1$: $P_{PrAF}(X) \in \{0, 1\}$ and equals standard Dung evaluation *(p.2)*
- MC approximation error decreases as $1/\sqrt{N}$ *(p.6)*
- Extreme probabilities (near 0 or 1) converge faster than probabilities near 0.5 *(p.7)*
- MC iteration count is independent of PrAF size — depends only on the estimated probability *(p.9)*
- MC CPU time per iteration scales linearly with $|A| + |D|$ *(p.9)*
- If argument $a$ has $P_A(a) = 0$, it never appears in any sampled DAF and all defeats involving it are excluded *(p.2-3)*
- Defeats are only sampled when both endpoints are present — enforces Definition 3 constraint *(p.5)*

## Relevance to Project
This paper is directly relevant to propstore's argumentation layer. The key insight for implementation:

1. **PrAF maps to ATMS contexts**: Each inducible DAF is a possible world — this is exactly an ATMS environment/context. The set of all inducible DAFs = the ATMS label space. Argument existence probabilities weight environments.
2. **Current bare floats can become $P_A$ and $P_D$**: The existing confidence/weight floats in propstore can be formalized as PrAF probabilities on argument and defeat existence.
3. **Monte Carlo is practical**: For frameworks with >13 arguments, the MC approach is necessary. The adaptive stopping criterion (Equation 5) is straightforward to implement.
4. **Semantics-agnostic**: Since propstore already computes Dung extensions (grounded), plugging in the MC sampling loop around the existing extension computation gives probabilistic acceptance for free.
5. **Independence assumption aligns with ATMS**: ATMS environments are assumption sets — each assumption is independently present or absent. PrAF's independence assumption on argument/defeat existence maps directly to weighted ATMS assumptions.

## Open Questions
- [ ] How to handle correlated argument probabilities (paper defers this)
- [ ] Integration with ASPIC+ structured argumentation (paper only handles abstract AFs)
- [ ] How to derive $P_A$ and $P_D$ values from propstore's existing data (stance confidence, source reliability)
- [ ] Whether the coalition formation extension is useful for propstore's multi-source reconciliation
- [ ] Relationship to Cayrol's bipolar frameworks (support + attack) with probabilities

## Related Work Worth Reading
- **Dung 1995** [2]: Foundation — abstract argumentation frameworks (already in propstore literature)
- **Li et al. 2012** [3]: Complexity of abstract argumentation — relevant for understanding computational limits
- **Dunne et al. 2011** [21]: Weighted argument systems — alternative to probabilistic approach, uses strength values
- **Rotstein et al. 2011** [25]: Resource bounded argumentation — relevant for practical computation limits
- **Hunter 2012** [14]: Uses likelihoods as proxies for argument strength — different semantics than PrAF
- **Baroni et al. 2010** [23]: Extension counting problems — relevant complexity results for exact computation
- **Janssen et al. 2008** [24]: Fuzzy argumentation frameworks — alternative uncertainty model
