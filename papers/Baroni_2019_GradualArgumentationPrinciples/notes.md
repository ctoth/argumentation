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

### GP4 — Weakening Completeness
Strength is lower than base score if and only if the argument has at least one attacker.
- Stronger than GP2: biconditional rather than one-directional

### GP5 — Strengthening Completeness
Strength is higher than base score if and only if the argument has at least one supporter.
- Stronger than GP3: biconditional rather than one-directional

### GP6 — Isomorphism / Equivalence
Arguments with identical base scores, identical attacker multisets (up to strength), and identical supporter multisets have the same strength.
- Captures: structural equivalence implies equal evaluation

### GP7 — Weakening Soundness (monotonic attack)
If R*-(alpha) is a strict subset of R*-(beta), with same base scores and supporters, then sigma(beta) < sigma(alpha).
- More attackers = weaker argument

### GP8 — Strengthening Soundness (monotonic support)
If R*+(alpha) is a strict subset of R*+(beta), with same base scores and attackers, then sigma(beta) > sigma(alpha).
- More supporters = stronger argument

### GP9 — Strict Counter-Transitivity (attack)
If attackers of alpha are strictly weaker than attackers of beta (same cardinality, same base scores), then alpha is stronger.
- Quality of attackers matters, not just quantity

### GP10 — Strict Counter-Transitivity (support via attack)
If the attackers of alpha's attackers are weaker than the attackers of beta's attackers (with otherwise identical structure), then strength ordering follows.
- Captures indirect effect: weaker attacks on your attackers = you are weaker

### GP11 — Strict Counter-Transitivity (support)
If supporters of alpha are strictly stronger than supporters of beta (same cardinality, same base scores), then alpha is stronger.
- Quality of supporters matters

## Overarching Meta-Principles

### Balance (Section 4.1, Principle 1)
A strength function is **balanced** if:
1. sigma(alpha) = tau(alpha) when no attackers or supporters (vacuity)
2. sigma(alpha) < tau(alpha) iff there exists an attacker with strength > bottom
3. sigma(alpha) > tau(alpha) iff there exists a supporter with strength > bottom

Balance implies GP1, GP2, GP3, GP4, GP5.

### Monotonicity (Section 4.2, Principle 2)
A strength function is **(strict) monotonic** if adding/strengthening attackers decreases strength and adding/strengthening supporters increases strength. Defined via multiset orderings on attacker/supporter sets.

Formally defined via comparison of "shaping triples" (tau, multiset of attacker strengths, multiset of supporter strengths) using lexicographic-style ordering on Definitions 8 and 9.

Monotonicity implies GP6, GP7, GP8, GP9, GP10, GP11.

**Together, balance + monotonicity imply ALL 11 GPs** (Propositions 17-21 prove this).

## Semantics Evaluated (Section 5)

### Semantics that satisfy both balance and strict monotonicity:
- **h-categorizer** (Besnard & Hunter 2001): sigma is fixed point of sigma(alpha) = tau(alpha) / (1 + sum of attacker strengths). Strictly balanced and strictly monotonic with *= sigma_bot and <<= <.
- **Weighted card-based** (Amgoud & Ben-Naim 2018): Based on cardinality of attackers/supporters weighted by strength. Strictly balanced and strictly monotonic.
- **Aggregation-based** (Amgoud & Ben-Naim 2018): Based on aggregation function over attacker/supporter strengths.

### Semantics that are balanced but NOT strictly monotonic:
- **Inverse equational system** (Amgoud et al. 2017): sigma(alpha) = tau(alpha) / (1 + sum of attacker strengths - sum of supporter strengths). Balanced and monotonic but not strictly.
- **Trusted equational system**: Special treatment for self-defeating arguments.
- **Max equational system**: Uses max instead of sum.
- **Card-based** (Amgoud & Ben-Naim 2018): Based on raw counts.
- **Top-based** (Amgoud & Ben-Naim 2018)
- **Reward-based** (Amgoud & Ben-Naim 2018)

### Semantics that are NOT balanced:
- **Euler-based** (Amgoud et al. 2017): Not strictly balanced (violation occurs when max attacker strength < max supporter strength)
- **Weighted max-based** (Amgoud & Ben-Naim 2018): Not strictly monotonic
- **DF-QuAD** (Rago et al. 2016): Balanced and monotonic with *= sigma_bot, but QuAD algorithm is NOT balanced (not monotonic either). The DF-QuAD algorithm is "discontinuity-free" development of QuAD.
- **CMA** (Gabbriellini & Santini 2016): Strictly balanced with *= sigma_bot and <<= <. NOT strictly monotonic.
- **Complete labeling** (Grossi & Modgil 2015): Strictly balanced and monotonic.

### Key finding from Section 5 (Table 5):
The parametric values of the GPs and the principles turn out NOT to provide a finer advantage as a classifier: they do not reveal more distinctions than balance/monotonicity alone. The main discriminating power comes from the choice of *= (sigma_bot vs sigma_not_bot) and/or the aggregated effects of attackers and supporters.

## Relationship to Propstore

### Direct relevance to DF-QuAD implementation
Propstore implements DF-QuAD (Freedman et al. 2025, which extends Rago et al. 2016). This paper's Table 5 shows DF-QuAD satisfies balance and monotonicity with *= sigma_bot. The paper notes that **P_A is conflated with base score** in the propstore CLAUDE.md — this paper's framework makes that conflation precise: tau IS the base score, and DF-QuAD's aggregation function determines sigma from tau and the attacker/supporter structure.

### Principle validation for gradual semantics
The 11 GPs provide a checklist for verifying any gradual semantics implementation. If propstore's DF-QuAD implementation satisfies balance + monotonicity, it automatically satisfies all 11 GPs.

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
