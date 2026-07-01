# Probabilistic Argumentation

Standard Dung AFs treat arguments and defeats as either present or absent. In practice, both may be uncertain: a claim's existence depends on evidence quality, and a defeat relationship may hold only with some probability. The PrAF subsystem extends Dung's framework with probabilistic argument and defeat existence, enabling reasoning under genuine uncertainty rather than forcing binary commitment.

The implementation follows Li et al. (2012), with opinions from Josang (2001)
as propstore's uncertainty carrier, component decomposition from Hunter &
Thimm (2017), and gradual semantics from Freedman et al. (2025).

The reusable probabilistic AF kernel lives in `argumentation.probabilistic`.
It accepts plain float probabilities in `[0, 1]` and owns deterministic,
exact-enumeration, Monte Carlo, tree-decomposition DP, and DF-QuAD / QBAF
algorithms. Propstore owns the adapter layer around that kernel: opinions,
source calibration, provenance-bearing relation rows, repository projection,
and CLI/worldline policy.

## The PrAF model

A probabilistic argumentation framework PrAF = (A, P_A, D, P_D) extends a Dung AF with existence probabilities (Li et al. 2012, Def 2):

- **P_A** maps each argument to an existence probability. In propstore these
  start as subjective logic opinions (Josang 2001), then convert to floats at
  the `argumentation.probabilistic` boundary. Default:
  `Opinion.dogmatic_true()` (the argument definitely exists).
- **P_D** maps each defeat relation to an existence probability. Propstore
  derives those opinions from stance confidence, opinion columns, or
  dogmatic-true defaults before converting them to floats for the external
  kernel.
- **Sampling probability** uses the opinion expectation E(w) = b + a*u
  (Josang 2001, Def 6). This bridges the four-valued opinion algebra to the
  plain probability accepted by the formal kernel.

`argumentation.probabilistic.ProbabilisticAF` carries the formal Dung
framework, argument probabilities, defeat probabilities, optional primitive
attack probabilities, support probabilities, support edges, and base defeats.
`propstore.praf.engine.PropstorePrAF` wraps that kernel with propstore-owned
opinion and provenance metadata.

A PrAF induces a distribution over deterministic sub-frameworks (DAFs). Each DAF is a standard Dung AF obtained by sampling which arguments and defeats exist. Acceptance probability for an argument is the weighted sum of its acceptance across all induced DAFs.

## Computation strategies

### Auto dispatch

The default strategy `"auto"` selects the best computation method based on
framework characteristics (`argumentation.probabilistic`):

```
All probabilities ~= 1.0?  -->  deterministic fallback
<= 13 arguments?           -->  exact enumeration
Has supports or separate   -->  Monte Carlo
  attack/defeat relations?
Low treewidth + DP on?     -->  tree decomposition DP (currently gated off)
Otherwise                  -->  Monte Carlo
```

Auto dispatch avoids MC overhead when the framework is small enough for exact computation, and falls back to deterministic Dung evaluation when all opinions are dogmatic.

### Deterministic fallback

When every P_A and P_D is dogmatic true (expectation = 1.0), the PrAF reduces to a standard Dung AF (Li et al. 2012, p.2). The system detects this and delegates directly to the Dung solver, avoiding sampling entirely. The result reports `strategy_used: "deterministic"`.

### Exact enumeration

For small frameworks (<= 13 arguments), brute-force enumeration over all inducible DAFs is tractable (Li et al. 2012, p.3-4, p.8). The procedure:

1. Enumerate all argument subsets (2^|A| possibilities)
2. For each argument subset, enumerate all attack/support configurations
3. Compute extensions for each induced DAF
4. Accumulate weighted acceptance probabilities

Complexity is O(2^(|A|+|D|)). The 13-argument threshold follows Li et al. (2012, p.8), where exact computation beats MC for small frameworks.

### Monte Carlo sampling

For larger frameworks, MC sampling estimates acceptance probabilities (Li et al. 2012, Algorithm 1, p.5):

1. **Sample a subgraph** (`argumentation.probabilistic`): for each argument,
   include with probability P_A. For each edge where both endpoints survived,
   include with probability P_D. Apply Cayrol derived defeats from sampled
   supports and direct defeats.
2. **Compute extensions** on the sampled Dung AF.
3. **Record acceptance** for each argument in the extension.
4. **Repeat** until convergence.

**Agresti-Coull stopping** (Li et al. 2012, Eq. 5, p.7; Agresti & Coull 1998): rather than running a fixed number of samples, the sampler monitors confidence interval width and stops when all arguments have converged. The adjusted Wald interval:

- adjusted_n = n + z^2
- adjusted_p = (count + z^2/2) / adjusted_n
- ci_half = z * sqrt(adjusted_p * (1 - adjusted_p) / adjusted_n)

Convergence requires ci_half <= epsilon for every argument in the component. Minimum 30 samples before checking. Safety cap at 100,000 samples. Z-scores: 0.90 -> 1.645, 0.95 -> 1.960, 0.99 -> 2.576.

**Connected component decomposition** (Hunter & Thimm 2017, Prop 18):
acceptance probability separates over connected components of the
attack/support graph. Each component gets independent MC sampling
(`argumentation.probabilistic_components` and `argumentation.probabilistic`).
Components where all probabilities are deterministic are short-circuited to
exact Dung evaluation, avoiding unnecessary sampling.

### DF-QuAD gradual semantics

DF-QuAD (Freedman et al. 2025, p.3) computes continuous argument strengths in
[0,1] rather than binary acceptance. Implemented in
`argumentation.dfquad` over `argumentation.gradual.WeightedBipolarGraph`.

The evaluation formula: sigma(a) = f_agg(tau(a), f_comb(v_a+, v_a-))

**Combination function** (`argumentation.dfquad`): aggregates
influence from supporters and attackers using noisy-OR:

- support = 1 - product(1 - s for s in supporter_strengths)
- attack = 1 - product(1 - a for a in attacker_strengths)
- combined = support - attack

**Aggregation function** (`argumentation.dfquad`): combines base
score with combined influence:

- If combined >= 0: base + combined * (1 - base) (push toward 1)
- If combined < 0: base + combined * base (push toward 0)

**Evaluation order**: topological sort via Kahn's algorithm for acyclic graphs. Cyclic arguments are handled by iterative fixpoint (max 100 iterations, convergence at 1e-9). Support edge weights act as multipliers on supporter strength.

**Two modes:**

- `dfquad_quad`: requires an explicit `tau` dict mapping each argument to an intrinsic strength. Only works with grounded semantics.
- `dfquad_baf`: uses neutral base score 0.5 for all arguments, treating the BAF structure alone as the source of differentiation.

### Tree decomposition DP

Per Popescu & Wallner (2024). Exact computation via tree decomposition dynamic
programming. Implemented in `argumentation.probabilistic_treedecomp`.

Currently **gated off** in auto dispatch (`_public_exact_dp_enabled` returns False). The current implementation tracks full edge sets, giving O(2^|defeats| * 2^|args|) complexity -- no asymptotic improvement over brute force. Effective only for treewidth <= ~15. Only supports credulous argument acceptance over defeat-only frameworks.

The auto dispatch checks treewidth but will not select this strategy unless explicitly requested. The lower-level Python API still accepts `strategy="exact_dp"` for experimental use, but the public CLI does not expose it.

## COH constraint

The COH rationality constraint (Hunter & Thimm 2017, p.9) requires that for every attack (A, B), the existence probabilities satisfy P(A) + P(B) <= 1. Self-attacks imply P(A) <= 0.5. This prevents paradoxical situations where two mutually attacking arguments both exist with high probability.

`enforce_coh()` (`propstore/praf/engine.py`) is propstore-owned because it
rewrites subjective opinions before kernel construction. It applies iterative
proportional scaling (up to 100 iterations): when a pair violates the
constraint, both expectations are scaled proportionally so their sum equals
1.0. Opinions are rebuilt from adjusted expectations preserving evidence
counts.

COH is opt-in. Apply it when your domain requires that mutual attackers cannot coexist with high probability. Skip it when argument existence is independently justified and you want the MC sampler to see the full probability space.

## Opinion integration

Opinions flow into PrAF from the stance and calibration layer:

1. **P_A (argument existence):** `p_arg_from_claim()` (`propstore/praf/engine.py`) returns `Opinion.dogmatic_true()` for all active claims. Per Li et al. (2012, p.2), arguments in the knowledge base exist with certainty.

2. **P_D (edge existence):** `p_relation_from_stance()` (`propstore/praf/engine.py`) extracts opinions from stance data through a fallback chain:
   - Full opinion columns (b, d, u, a) -> direct Opinion construction
   - Confidence float -> `from_probability(confidence, 1)` (moderate uncertainty)
   - No data -> `Opinion.dogmatic_true()` (backward compatibility)

3. **Construction from store:** `build_praf()` in
   `propstore/praf/projection.py` is the store-facing entrypoint. It is
   re-exported from `propstore.praf` and delegates to the shared argumentation
   projection in `propstore.argumentation` to assemble a `PropstorePrAF` from
   relation maps and claim data. The embedded `.kernel` is an
   `argumentation.probabilistic.ProbabilisticAF`.

The calibration layer (temperature scaling per Guo et al. 2017,
evidence-to-opinion mapping per Sensoy et al. 2018) feeds into opinion
construction upstream of PrAF. The external `argumentation` package does not
own a subjective-logic opinion calculus; propstore converts opinions to float
expectations before invoking `argumentation.probabilistic`. See
`docs/argumentation.md` for details on the opinion algebra and calibration.

## CLI usage

### Extensions with PrAF backend

```bash
# PrAF extensions with auto strategy selection
pks world extensions domain=example --backend praf

# MC sampling with tighter convergence
pks world extensions domain=example --backend praf \
  --praf-strategy mc --praf-epsilon 0.005 --praf-confidence 0.99

# Exact enumeration (for small frameworks)
pks world extensions domain=example --backend praf --praf-strategy exact

# DF-QuAD gradual semantics (neutral base scores)
pks world extensions domain=example --backend praf --praf-strategy dfquad_baf

# Reproducible MC with fixed seed
pks world extensions domain=example --backend praf \
  --praf-strategy mc --praf-seed 42
```

### Resolution with PrAF

```bash
# Resolve a conflicted concept using PrAF argumentation
pks world resolve concept1 domain=example \
  --strategy argumentation --reasoning-backend praf

# With MC tuning
pks world resolve concept1 domain=example \
  --strategy argumentation --reasoning-backend praf \
  --praf-strategy mc --praf-epsilon 0.01 --praf-confidence 0.95
```

### Worldline with PrAF

```bash
# Create a worldline definition using PrAF
pks worldline create my-scenario \
  --target concept1 --target concept2 \
  --strategy argumentation --reasoning-backend praf \
  --praf-strategy auto

# Materialize and inspect it
pks worldline run my-scenario
pks worldline show my-scenario

# Compare two worldlines
pks worldline diff scenario-a scenario-b
```

Available public `--praf-strategy` choices: `auto`, `mc`, `exact`, `dfquad_quad`, `dfquad_baf`.
Lower-level `compute_probabilistic_acceptance()` also accepts `exact_enum`, `exact_dp`, and `deterministic`.

## Known limitations

- **P_A conflated with tau in DF-QuAD mode.** Li et al. (2012) define P_A as
  argument existence probability; Rago (2016) and Freedman et al. (2025)
  define tau as intrinsic argument strength. These are conceptually distinct
  but currently share the same value at the propstore adapter boundary. This
  means DF-QuAD base scores are driven by existence probability rather than
  independent intrinsic strength.
- **Tree decomposition gated off.** The Popescu & Wallner (2024) DP backend exists but provides no asymptotic improvement in its current form. It remains disabled in auto dispatch.
- **Extension probability query limited to grounded semantics.** The MC extension probability loop computes P(grounded extension = queried set) but does not generalize to preferred or stable semantics.
- **P_A always dogmatic.** `p_arg_from_claim()` currently returns `Opinion.dogmatic_true()` for all claims. Variable argument existence would require evidence-count integration at the claim level.

## References

- Agresti, A. & Coull, B.A. (1998). Approximate is better than "exact" for interval estimation of binomial proportions. *The American Statistician*, 52(2), 119-126.
- Cayrol, C. & Lagasquie-Schiex, M.-C. (2005). On the acceptability of arguments in bipolar argumentation frameworks. *ECSQARU 2005*.
- Dung, P.M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321-357.
- Freedman, R., Borg, A., & Prakken, H. (2025). DF-QuAD: a gradual semantics for quantitative bipolar argumentation frameworks.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K.Q. (2017). On calibration of modern neural networks. *ICML 2017*.
- Hunter, A. & Thimm, M. (2017). Probabilistic reasoning with abstract argumentation frameworks. *Journal of Artificial Intelligence Research*, 59, 315-364.
- Josang, A. (2001). A logic for uncertain probabilities. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 9(3), 279-311.
- Li, H., Oren, N., & Norman, T.J. (2012). Probabilistic argumentation frameworks. *TAFA 2011*, LNAI 7132, 1-16.
- Popescu, C. & Wallner, J.P. (2024). Tree decomposition for probabilistic argumentation.
- Rago, A., Toni, F., Aurisicchio, M., & Baroni, P. (2016). Discontinuity-free decision support with quantitative argumentation debates. *KR 2016*.
- Sensoy, M., Kaplan, L., & Kandemir, M. (2018). Evidential deep learning to quantify classification uncertainty. *NeurIPS 2018*.
