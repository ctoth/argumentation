# Adversarial semantic review: directed ABA SCC composition

Date: 2026-07-11
Repository HEAD inspected: `0d03790a0d62e06f013910898810a1fbf0538bdf` (`main`)
Scope: ordinary finite flat ABA, stable and preferred extension enumeration
Mode: read-only source/Git/paper inspection plus generated toy frameworks; no ICCMA row, benchmark, solver worker, or holdout access

## Recommendation

**SURVIVE, but only the exact support-hypergraph/SETAF form. Proceed to shape
telemetry after an executable semantic contract passes. Kill every proposal
that uses the current direct-rule assumption SCC metric, blind SCC products,
plain projection, or the AF `D/U` state without SETAF mitigated attacks.**

Exact composition is not fundamentally impossible. Finite flat ABA over its
assumptions induces a collective-attack framework: for every assumption `a`
and every minimal assumption support `T` deriving `contrary(a)`, add the
hyperattack `T -> a`. The primal graph has an edge `t -> a` for every `t in T`.
Dvorak, Konig, Ulbricht, and Woltran prove that stable and preferred semantics
are SCC-recursive on this structure, but their local restriction is materially
richer than the current AF recursion. Preferred composition additionally needs
the candidate set `C` and the set `M` of mitigated local attacks.

This survives as a semantic target, not yet as an operational target. Explicit
minimal-support materialization and the branch product can both be exponential.
Shape telemetry must therefore measure support-primal SCC reduction and the
boundary obligations below before any source/solver experiment.

## Evidence boundary and prior-work check

The committed inventory freeze selects this exact question and forbids shape
measurement before the semantic contract (`experiments/INDEX.md:157-183`,
`reports/iccma-history-sepr-inventory-20260711.md:245-269`,
`reports/iccma-history-sest-inventory-20260711.md:565-590`). I did not use the
untracked prompt/report material in the checkout as evidence.

The selected family is distinct from all prior SCC/product work:

- The kept ABA decomposition is an **undirected independent product** over the
  proof/contrary incidence graph. Its exact certificate refuses every rule or
  contrary crossing a component (`aba_decomposition.py:191-245`). The hard
  preferred rows reported `component_plan_not_exact`; only T8 got the narrow
  win (`reports/iccma-history-sepr-inventory-20260711.md:119-130`). Directed
  conditioning is precisely the case that certificate declines.
- Static SCC loop preload and SCC-local founded levels changed a stable SAT
  encoding; both were removed. They did not compose component extensions
  (`reports/iccma-history-sepr-inventory-20260711.md:123-126` and
  `reports/iccma-history-sest-inventory-20260711.md:480-503`).
- The current AF implementation is the Baroni-Giacomin-Guida binary-attack
  recursion. It carries `D/U/UP` and `C`, then cross-products local results
  (`src/argumentation/core/scc_recursive.py:223-267`). It has no representation
  of a collective tail or a mitigated attack. Substituting it would repeat the
  known category error.
- The newer AF cone implementation is acceptance-only and explicitly treats
  stable lifting as one-sided because downstream no-extension components can
  destroy a global stable extension (`src/argumentation/solving/af_scc_cone.py:1-19`).
  It is useful as a warning, not as an ABA composition algorithm.

## Why the support hypergraph is the correct semantic object

The repository's ABA constructor enforces flatness by rejecting assumptions as
rule heads (`aba.py:40-71`). Consequently every assumption subset is closed;
attacks are exactly derivations of contraries (`aba.py:86-102`, `255-285`).
Preferred is inclusion-maximal admissibility and stable is conflict-free plus
attack of every excluded assumption (`aba.py:131-180`). The support oracle
computes minimal Horn supports and implements precisely these collective-attack
conditions (`aba_support_model.py:14-95`, `108-164`).

For fact-free frameworks this is a semantics-preserving reduction to a SETAF:

```text
A_aba       = assumptions
R_aba       = {(T, a) | T is a minimal support of contrary(a)}
primal edge = (t, a) for every (T, a) in R_aba and t in T
```

The primary SETAF paper defines this primal graph in Definition 2.5, defines
the component restriction in Definition 6.5, proves stable SCC-recursiveness in
Theorem 6.11, and proves preferred SCC-recursiveness in Theorem 6.22. I checked
the paper's page images directly (proceedings pp. 122, 126-129), not extracted
text: [Dvorak et al., KR 2022](https://proceedings.kr.org/2022/13/kr2022-0013-dvorak-et-al.pdf).

### Factual/empty attackers

The paper's SETAF definition excludes empty tails, while ABA permits them and
the native oracle deliberately enumerates the empty attacker (`aba.py:318-329`).
This is a real proof obligation, not grounds to discard the target.

Let `F = {a | contrary(a) is in closure(empty)}`. Every stable or admissible
set excludes every `a in F`: selecting `a` conflicts with the empty attack, and
no set can counterattack the empty set. Normalize before SCC recursion by:

1. deleting `F` from the assumption universe;
2. deleting attacks whose target is in `F`;
3. deleting every attack whose tail intersects `F`.

Step 3 is exact for both semantics. Such a tail can never activate because its
fact-attacked member can never be selected; for defense, that member is already
attacked by the empty set, so the whole attacking tail is already defeated.
Extensions lift unchanged because no extension contains `F`. The one-assumption
framework `not_a <- []` has exactly `{}` as both its stable and preferred
extension in both current oracles.

## Minimal falsifications of plausible weaker schemes

I used the reusable temporary script
`%TEMP%/aba_scc_semantic_probe_20260711.py` with `uv run`; it imports only the
native enumerators, the support oracle, and Horn minimal-support model. The
native and support extension sets agreed on every case below. No SAT/ASP solver
or ICCMA data was invoked.

### 1. Blind product fails on the smallest collective cross-body case

```text
assumptions: a, b, c
contrary rule: not_c <- a, b
hyperattack: {a,b} -> c
support-primal SCCs: {a}, {b}, {c}
```

Both native oracles return the single stable extension `{a,b}` and the single
preferred extension `{a,b}`. Solving each singleton SCC as an independent
framework and taking the product returns `{a,b,c}` for both semantics. This is
not a bad SCC graph: the primal graph is correct. It kills **unconditioned
composition**. The downstream component must know whether all external members
of a collective tail have been selected, whether any was defeated, or whether
the tail is only partially live.

Three assumptions are cardinality-minimal for a genuinely collective
two-member tail attacking a distinct target.

### 2. Direct contrary-headed rule graphs miss mediated attacks and SCCs

```text
x     <- a        y     <- b
not_b <- x        not_a <- y
```

The exact hyperattacks are `{a} -> b` and `{b} -> a`, so the correct primal SCC
is `{a,b}` and both semantics return `{a}` and `{b}`. A graph that only adds an
edge when an assumption occurs directly in a contrary-headed rule body sees no
edge and splits the assumptions incorrectly.

That is exactly the limitation of the existing telemetry helper: it only
examines antecedents of rules whose **immediate consequent** is a contrary and
only records antecedents that are assumptions
(`src/argumentation/structured/aba/aba_telemetry.py:104-124`). Therefore
`assumption_dependency_scc_count/max_size` is not admissible telemetry for this
candidate. A rule/literal reachability graph may conservatively over-merge, but
it must preserve every support-primal influence edge through arbitrarily long
Horn derivations.

Two assumptions are cardinality-minimal for a mediated mutual-attack SCC.

### 3. Empty attacks are invisible to a graph-only SCC implementation

```text
assumptions: a
fact: not_a <- []
hyperattack: {} -> a
```

There is no primal source vertex for the empty tail. Any implementation that
equates “no incoming primal edge” with “unattacked” selects `a` and is wrong.
The native and support oracles both return `{}` for stable and preferred. This
is the one-assumption minimum and requires the factual normalization above or
explicit empty-tail semantics.

### 4. Plain projection and AF-style `D/U` are insufficient for preferred

```text
assumptions: a, b, c
attacks: {a} -> a, {a,b} -> c, {c} -> b
support-primal SCCs: {a}, {b,c}
```

The source SCC chooses `{}` under preferred semantics because `a` self-attacks.
Projecting the downstream collective attack to `{b,c}` turns `{a,b} -> c` into
`{b} -> c`; together with `{c} -> b`, an ordinary local preferred solve returns
both `{b}` and `{c}`. Composing `{b}` is spurious: globally, `b` does not attack
`c` because the omitted `a` was not selected, so `b` cannot defend itself from
`{c} -> b`. The exact global preferred set is only `{c}`.

The projected `{b} -> c` cannot simply be deleted: it remains an attack against
`c` for acceptability. It must instead be marked **mitigated**, meaning it may
create a defense obligation but may not be used as a counterattack. With
`M = {{b} -> c}`, the local preferred result becomes exactly `{c}`. This is the
smallest witness I found that separates projection-only preferred composition
from projection plus `M`, and it directly exercises preferred maximality across
components.

This is the SETAF-specific failure illustrated by Definitions 6.13-6.16 of the
KR 2022 paper. The current AF recursion has no `M`, so copying it is unsound.

### 5. A no-extension component must annihilate the stable branch

```text
assumptions: a, b
attack: {a} -> a
SCCs: {a}, {b}
```

The isolated `b` component has local stable extension `{b}`, but the self-loop
component has none; the global stable extension set is empty. Any enumerator
that returns a partial/lifted witness after one component, or treats “no local
stable extension” as an empty local choice, is wrong. This is the ABA analogue
of the downstream stable-vacuity warning already encoded in the AF cone path.

## Exact boundary state that repairs the failures

After factual normalization, let `SF=(A,R)` be the induced SETAF, `S` a primal
SCC, `E` a complete branch assignment outside/currently before `S`, and `E+`
the assumptions attacked by `E`. The executable reference recursion must carry
the following state exactly (notation follows Dvorak et al. Definitions
6.3, 6.5, 6.13-6.16):

```text
D(S,E)  = {a in S | E\S attacks a}
P(S,E)  = {a in S | A\(S union E+) attacks a} \ D(S,E)
U(S,E)  = S \ (D(S,E) union P(S,E))
UP(S,E) = U(S,E) union P(S,E)
```

The local restriction deletes externally defeated targets, discards every
attack whose tail contains a defeated external assumption, and partially
evaluates every remaining collective tail by removing already selected
external members. This repairs the cross-body case.

Stable then recursively solves the restricted framework on `UP`; no `P`
arguments survive on a genuine stable branch. An empty local result kills that
branch.

Preferred additionally carries:

- `C := U(S,E) intersect parent_C`, restricting which local assumptions may be
  selected/required by maximal admissibility; and
- `M`, the projected attacks for which no original attack with that projection
  has all omitted external tail members selected. An attack in `M` still
  attacks its local head, but it is forbidden as the counterattack used to
  establish defense.

For ABA implemented without materialized supports, the equivalent boundary
must still distinguish three cases for every cross-component proof obligation:

1. all external prerequisites selected: partially activate the residual tail;
2. some prerequisite defeated/impossible: discard the attack;
3. prerequisites neither selected nor defeated: retain the defense obligation
   but mark its local projection mitigated.

A Boolean “cross-SCC attack exists” count, selected predecessor assumptions
alone, or derived-literal truth alone cannot distinguish cases 2 and 3.

## Exponential/global-state assessment

The semantic boundary is **ancestor-local, not whole-framework-global**: the
SETAF theorem needs only earlier SCC choices and their attacked set. That is
enough to reject a fundamental-impossibility verdict.

The obvious ABA realization is nevertheless exponential in two independent
ways:

- a Horn ABA can have exponentially many minimal supports, so materializing
  `R_aba`, every cross-SCC tail, and `M` can be exponential in the rule input;
- stable/preferred can have exponentially many branch extensions, so an exact
  cross-product enumerator can be exponential even when each SCC is small.

A compact rule-circuit implementation may avoid enumerating all supports, but
it must preserve the same three-way boundary status for each cross-component
derivation and the non-mitigated-counterattack test. Until such a compact state
has an executable equivalence contract, it is only an implementation idea.
Conservative rule/literal SCC over-approximation is semantically acceptable if
it only merges true support-primal SCCs; it may erase all operational benefit.

## Required executable contract before telemetry

The next implementation artifact should be a bounded, normally running
semantic contract—not hard-row telemetry—with these clauses:

1. Generate finite flat ABA frameworks with at most 5-6 assumptions and bounded
   rules, including zero-body rules, multi-antecedent bodies, multi-step Horn
   derivations, shared derived literals, and branches with no stable extension.
2. Build the **reference** support hypergraph from the existing minimal-support
   model, normalize empty attacks, and compute SCCs on its primal graph. Do not
   call `aba_to_dung`.
3. Implement the paper reference recursion with restriction, `D/P/U/UP`, and
   preferred `C/M`; enumerate all lifted extensions, not one witness.
4. Assert set equality in both directions against both
   `aba.stable_extensions` / `aba.preferred_extensions` and
   `aba_sat.support_extensions` for every generated framework.
5. Pin the four counterexamples above as named tests. Also assert that the
   mediated-mutual case is one SCC, the cross-body case actually crosses SCCs,
   the projection-only preferred variant produces the known spurious `{b}`, and
   the corrected `M` variant removes it.
6. Add path-exercising counters: at least one generated case must use more than
   one SCC, partially evaluate a collective tail, discard a tail due to a
   defeated member, create a nonempty `M`, normalize an empty attack, and
   annihilate a stable branch.

Only after all six clauses pass should shape telemetry be authorized. The first
telemetry must report: factual-normalized assumption/rule counts, exact or
conservative support-primal SCC count and maximum size, number and maximum width
of cross-SCC tails, boundary assumptions, per-branch `D/P/U/M` sizes, maximum
conditioned residual, branch count/bound, and whether support or `M`
materialization exceeded a deterministic cap. The current direct-rule
`assumption_dependency_*` fields must not stand in for these measurements.

## Final kill/survive line

- **Survive:** exact SCC recursion over the induced collective-attack primal
  graph, with factual normalization, collective-tail restriction, and
  preferred `C/M` conditioning.
- **Kill:** blind local products; singleton/direct-rule attack graphs; literal
  projection without defeated-tail handling; AF SCC recursion copied without
  `M`; any proposal whose only proof is post-hoc full-framework validation.
- **Operational status:** semantic route survives to the executable contract.
  Shape telemetry is the next phase only after that contract passes. If exact
  support/mitigation state is unbounded on the bounded contract or requires
  materializing exponential supports without a cap, record that explicitly and
  kill the operational route even though the semantic theorem remains true.
