# Baroni, Rago, Toni (2019) — From Fine-Grained Properties to Broad Principles for Gradual Argumentation

## Datestamp: 2026-03-30

## Bibliographic
- **Authors:** Pietro Baroni, Antonio Rago, Francesca Toni
- **Journal:** International Journal of Approximate Reasoning 105 (2019) 252-286
- **DOI:** 10.1016/J.IJAR.2018.11.019

## Summary

This paper provides a principled taxonomy of properties for gradual argumentation semantics. The literature had accumulated many fine-grained properties for evaluating argument strength, but these were scattered across different framework types and naming conventions. The authors unify them into 11 Groups of Principles (GP1-GP11) that capture the fundamental intuitions, then show that two overarching meta-principles — **balance** and **monotonicity** — subsume all 11 GPs. The paper classifies existing gradual semantics (h-categorizer, Euler-based, max-based, weighted max-based, weighted card-based, card-based, top-based, reward-based, aggregation-based, DF-QuAD, CMA, QuAD, Leite/Lottfo, complete labeling) against these principles.

## Key Definitions

### Framework Types
- **QBAF** (Quantitative Bipolar Argumentation Framework): Q = (X, R-, R+, tau) where X = set of arguments, R- = attack relation, R+ = support relation, tau: X -> [0,1] = base score function. Generalizes both weighted argumentation (Dunne et al. 2011) and bipolar argumentation (Cayrol & Lagasquie-Schiex 2005).
- **aQBAF**: acyclic QBAF (no directed cycles in R- union R+)
- **sQBAF**: simple QBAF (acyclic + each argument has at most one attacker and one supporter)

### Strength and Semantics
- **Strength function** sigma: X -> V where V is a totally ordered set (typically [0,1] or [-1,1])
- **Gradual semantics**: function mapping each QBAF to a strength function
- A strength function is **s-equivalent** to another if there exists an order-preserving bijection between their ranges

### Comparison Relations (crucial for GP parameterization)
The GPs are parameterized by two choices:
1. **sigma parameter** (*): either sigma_bot (strength can equal bottom) or sigma_not_bot (strength cannot equal bottom)
2. **Comparison operator** (<<): one of <, <_bot, <_top, <=

This yields up to 8 instantiations per GP per framework type, capturing all 29 properties from the literature.

## The 11 Groups of Principles

### GP1 — Vacuity / Neutrality
If an argument has no attackers and no supporters, its strength equals its base score.
- Formal: If R*-(alpha) = empty and R*+(alpha) = empty then sigma(alpha) = tau(alpha)

### GP2 — Weakening
In the absence of supporters, if there is at least one attacker, the strength is lower than the base score.
- Captures: attacks lower strength (basic soundness of attack)

### GP3 — Strengthening
In the absence of attackers, if there is at least one supporter, the strength is higher than the base score.
- Captures: supports raise strength (basic soundness of support)

### GP4 — Weakening Soundness
If strength is lower than the base score, the argument has at least one effective attacker: $\sigma(\alpha)<\tau(\alpha)\Rightarrow R^-_*(\alpha)\ne\emptyset$. This is one implication, not a biconditional. *(printed p.257, `pngs/page-005.png`)*

### GP5 — Strengthening Soundness
If strength is higher than the base score, the argument has at least one effective supporter: $\sigma(\alpha)>\tau(\alpha)\Rightarrow R^+_*(\alpha)\ne\emptyset$. *(printed p.257, `pngs/page-005.png`)*

### GP6 — Isomorphism / Equivalence
Arguments with identical base scores, identical attacker multisets (up to strength), and identical supporter multisets have the same strength.
- Captures: structural equivalence implies equal evaluation

### GP7 — Weakening Soundness (monotonic attack)
If R*-(alpha) is a strict subset of R*-(beta), with same base scores and supporters, then sigma(beta) < sigma(alpha).
- More attackers = weaker argument

### GP8 — Strengthening Soundness (monotonic support)
If R*+(alpha) is a strict subset of R*+(beta), with same base scores and attackers, then sigma(beta) > sigma(alpha).
- More supporters = stronger argument

### GP9 — Higher Base Score
For equivalent attacker groups and equivalent supporter groups, $\tau(\alpha)<\tau(\beta)$ implies $\sigma(\alpha)\ll\sigma(\beta)$. This GP compares base scores, not attacker quality. *(printed p.258, `pngs/page-006.png`)*

### GP10 — Weaker Attacker Group
If $R^-(\alpha)<_*R^-(\beta)$, the effective supporter groups are equal and the base scores are equal, then $\sigma(\beta)\ll\sigma(\alpha)$. This compares direct attacker groups by strength, not attackers of attackers. *(printed pp.258-259, `pngs/page-006.png`, `pngs/page-007.png`)*

### GP11 — Strict Counter-Transitivity (support)
If supporters of alpha are strictly stronger than supporters of beta (same cardinality, same base scores), then alpha is stronger.
- Quality of supporters matters

## Overarching Meta-Principles

### Balance (Section 4.1, Principle 1)
A strength function is **balanced** if, for every alpha:
1. $R^-(\alpha)=_*R^+(\alpha)\Rightarrow\sigma(\alpha)=\tau(\alpha)$.
2. $R^-(\alpha)>_*R^+(\alpha)\Rightarrow\sigma(\alpha)\ll\tau(\alpha)$.
3. $R^-(\alpha)<_*R^+(\alpha)\Rightarrow\sigma(\alpha)\gg\tau(\alpha)$.

**Strict balance** additionally requires that strength below/above the base score implies the corresponding attacker/supporter group dominance. Mere presence of an attacker or supporter is insufficient in a bipolar graph. Balance implies GP1-GP3; strict balance implies GP1-GP5. *(Principle 1 and Proposition 17, printed p.260, `pngs/page-008.png`)*

### Monotonicity (Section 4.2, Principle 2)
A strength function is **(strict) monotonic** if adding/strengthening attackers decreases strength and adding/strengthening supporters increases strength. Defined via multiset orderings on attacker/supporter sets.

Formally defined via comparison of "shaping triples" (tau, multiset of attacker strengths, multiset of supporter strengths) using lexicographic-style ordering on Definitions 8 and 9.

Monotonicity implies GP6; strict monotonicity implies GP6-GP11.

**Strict balance and strict monotonicity jointly imply all 11 GPs**, with the same parameter choices. The non-strict principles alone imply only GP1-GP3 and GP6. *(Propositions 17,19 and Table 4, printed pp.260,262, `pngs/page-008.png`, `pngs/page-010.png`)*

## Semantics Evaluated (Section 5)

### Semantics that satisfy both balance and strict monotonicity:
- **h-categorizer** (Besnard & Hunter 2001): $\sigma(\alpha)=1/(1+\sum_{\beta\in R^-(\alpha)}\sigma(\beta))$, fixed base score 1 and range (0,1]. Strictly balanced and strictly monotonic for either strength parameter and every comparison choice. The version with numerator tau is separately the weighted h-categorizer. *(printed pp.263,267, `pngs/page-011.png`, `pngs/page-015.png`)*
- **Weighted card-based:** attack-only semantics combining attacker cardinality and mean attacker strength; strictly balanced and strictly monotonic.
- **Aggregation-based support:** support-only semantics; balanced, strictly balanced, monotonic and strictly monotonic.

### Equational and Support Semantics
- **Inverse equational system** (Gabbay): $\sigma(\alpha)=\prod_{\beta\in R^-(\alpha)}(1-\sigma(\beta))$, fixed base score 1. Table 5 records balance, strict balance, monotonicity and strict monotonicity, with the stated parameter choices. *(printed p.263, `pngs/page-011.png`)*
- **Suspect equational system:** balanced and strictly balanced, but neither monotonic nor strictly monotonic.
- **Max equational system:** uses the strongest attacker; balanced, strictly balanced and monotonic, but not strictly monotonic.
- **Weighted h-categorizer:** balanced, strictly balanced, monotonic and strictly monotonic.
- **Top-based support:** balanced, strictly balanced and monotonic, but not strictly monotonic.
- **Reward-based support:** satisfies all four principles. *(All classifications: Table 5, printed p.263, `pngs/page-011.png`; framework/parameter choices in that table remain essential.)*

### Balanced Semantics Without Both Strict Properties
- **Restricted Euler-based:** balanced and strictly monotonic, but not strictly balanced.
- **Weighted max-based:** balanced, strictly balanced and monotonic, but not strictly monotonic.
- **DF-QuAD** (Rago et al. 2016): Table 5 records balance and monotonicity, but not their strict forms. QuAD also satisfies monotonicity, while violating balance. *(printed p.263, `pngs/page-011.png`)*
- **GTAA:** for attack-only frameworks, balanced and strictly balanced but not monotonic; its general bipolar version fails all four principles.
- **Complete labellings**: balanced, strictly balanced and monotonic, but not strictly monotonic. *(Table 5, printed p.263, `pngs/page-011.png`)*

### Classification in Table 5
The table distinguishes balance, strict balance, monotonicity and strict monotonicity, with explicit framework and parameter choices. For example, weighted max-based and weighted card-based differ on strict monotonicity; QuAD and DF-QuAD differ on balance. QuAD is monotonic but not balanced. *(printed p.263, `pngs/page-011.png`)*

## Relationship to Propstore

### Direct relevance to DF-QuAD implementation
Propstore implements DF-QuAD (Freedman et al. 2025, which extends Rago et al. 2016). This paper's Table 5 shows DF-QuAD satisfies balance and monotonicity with *= sigma_bot. The paper notes that **P_A is conflated with base score** in the propstore CLAUDE.md — this paper's framework makes that conflation precise: tau IS the base score, and DF-QuAD's aggregation function determines sigma from tau and the attacker/supporter structure.

### Principle validation for gradual semantics
The 11 GPs distinguish strict from non-strict principles. Balance plus monotonicity does not automatically imply all 11 GPs; the all-GP implication uses strict balance and strict monotonicity, with matching parameters. *(Table 4, printed p.262, `pngs/page-010.png`)*

### Properties NOT captured
The paper explicitly notes (Section 6) that its principles do NOT capture:
- Quality/priority of attacks/supporters (rather than strength; this is what ASPIC+ preference orderings handle)
- Maximality of strength range utilization
- Convergence/stability for cyclic graphs
- Proportionality

## New Leads
- Amgoud & Ben-Naim 2016 [1]: "Axiomatic foundations for ranking argumentation semantics" — defines many properties this paper unifies
- Amgoud & Ben-Naim 2018 [3]: Weighted and card-based semantics — several concrete semantics analyzed
- Bonzon et al. 2016 [6]: "A comparative study of ranking-based semantics" — earlier comparison work
- Baroni et al. 2015 [10]: "Automatic evaluation of design alternatives" — DF-QuAD precursor
- Rago et al. 2016 [21]: DF-QuAD original paper — directly relevant to propstore implementation
- Besnard et al. 2017 [24]: "Subsumption and incompatibility between principles" — extends this work's direction
- Bonzon et al. 2017 [25]: "Parametrized ranking-based semantics for persuasion"

## Provenance
- Source: sci-hub.st
- Retrieved: 2026-03-30
- Read by: Claude (paper-reader worker)
- Read date: 2026-03-30
- Pages: 35 (pp. 252-286)
- All pages read: Yes
