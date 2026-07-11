# ICCMA 2023 probe 6 backdoor/cutset adjudication

Date: 2026-07-11

Repository HEAD adjudicated: `7c4a8797007a557214d4e19ca792ffe73cba2d6f`

Status: **PROCEED TO PROBE 6 SEMANTIC CONTRACT.** No semantic implementation,
shape measurement, solver call, benchmark, hard-row access, or holdout access
was performed in this adjudication slice.

## Decisive verdict

The strengthened constructive candidate remains the inventory's queued **small
backdoor/cutset conditioning into exact residual components**. It is not the
distinct bounded-incidence-width/tree-decomposition family.

The distinction is literal. This candidate chooses one bounded set `K` of
**assumption vertices**, deletes those vertices from the normalized compact
rule/contrary factor-incidence graph, and proceeds only when that single
deletion separates at least two assumption-bearing residual components. It then
conditions on `K`, solves the exact residual predicates independently under a
frozen boundary signature, lifts all admissible products, deduplicates them,
and applies global inclusion maximality. A tree-decomposition algorithm instead
requires a decomposition of the whole incidence graph and parameterizes
dynamic programming by bag width. No bags, running-intersection property, or
width-bounded whole-graph decomposition occurs in the frozen theorem.

The constructive report therefore wins the literal disagreement. The
adversarial report correctly kills the old unexplained `IN/OUT/UNDEC` product
and any claim that the entire semantic state is bounded by `3^|K|`; it does not
kill the strengthened separator theorem it reviewed as though every
assumption-labelled cutset qualified.

## Fixed-`k=1` family under the actual separator definition

For the adversarial family, let `K={x}` and, for each `i`, retain

```text
t_i <- u_i
t_i <- v_i
bar(c) <- x,t_1,...,t_m
```

with assumption pairs `u_i,v_i` and target assumption `c`. **`K={x}` is not a
valid separator.** After deleting the assumption vertex `x`, the factor vertex
for the final rule remains adjacent to every literal `t_i` and to `bar(c)`.
Each `t_i` remains connected through its two rule factors to `u_i` and `v_i`,
and `bar(c)` remains connected by the contrary edge to `c`. Thus all
`u_i,v_i,c` lie in one assumption-bearing connected component. The constructive
cutset definition requires at least two such components.

The family does establish `2^m` minimal supports for `bar(c)` while `|K|=1`.
Consequently it falsifies the naive queue claim that three labels per cut
assumption bound the complete semantic boundary, and it forbids eager support
materialization or a post-extraction cap. It does **not** falsify the frozen
theorem, because its `K` fails the theorem's antecedent. It also does not
falsify the operational contract: that contract must reject this family as
`route_disabled` for lack of a useful separator, before support extraction or
solver entry.

## Frozen theorem for probe 6

The semantic contract must encode this theorem without weakening it.

For every finite ordinary flat ABA framework `F=(L,R,A,contrary)`:

1. Compute factual closure `Q=Cl(empty)` and remove every assumption whose
   contrary lies in `Q`, together with attacks targeting it or using it in a
   tail. Preserve Horn conjunction and repeat least closure after conditioning.
2. Build the normalized compact factor-incidence graph with literal vertices,
   one vertex per stored Horn rule connected to its head and body literals, and
   each assumption connected to its contrary. No minimal supports are needed
   for this certificate.
3. Choose `K` only from normalized assumption vertices. `K` qualifies only if
   deleting it leaves at least two assumption-bearing components `C_i`.
   Every collective attack's non-`K` tail/target vertices must then have unique
   residual-component ownership; ambiguity falsifies the contract.
4. For each selected/rejected cut assignment `X subseteq K`, freeze the exact
   per-component attacked-`K` signatures `B_i`, their global union `Z` including
   pure-cut attacks, and every remaining defense obligation against a selected
   cut assumption. `B_i` equality is required; a Boolean summary or subset
   approximation is not exact.
5. Under that fixed state, each component independently enumerates all and only
   local choices satisfying exact boundary contribution, conflict freedom,
   defense of selected local assumptions against every original attacker, and
   discharge of its cut-defense obligations.
6. Union `X` with one admissible choice from every component, canonicalize and
   deduplicate the assumption sets, and only then apply one global strict-
   inclusion maximality filter.

The frozen equality is

```text
all conditioned admissible lifts = Admissible(F)
Max_subseteq(all conditioned admissible lifts) = Preferred(F).
```

The contract must compare the complete preferred-extension family in both
directions against both current exhaustive authorities: the direct native ABA
oracle and the independent support-model oracle. Post-hoc witness validation,
locally maximal component choices, or one successful lift is not a substitute.

## Frozen semantic bounds

Probe 6 is a bounded diagnostic/reference contract only:

- ordinary flat frameworks with `0..5` assumptions, at most `4`
  non-assumption literals, at most `8` rules, and rule-body width `0..3`;
- every qualifying `K` with `|K| <= min(3, |A'|)`, including `K=empty` for an
  already-independent framework and exercised nonempty cutsets;
- at least `300` deterministic Hypothesis examples with `deadline=None`;
- complete family equality against both oracles;
- named/path coverage for factual normalization, selected and rejected cut
  states, attacked-cut signatures, created and discharged cut-defense
  obligations, inactive and activated collective tails, two independent
  residual components, deduplication, and incomparable preferred maxima;
- fail closed on cap overflow, missing path coverage, oracle disagreement,
  ambiguous ownership, exception, or missing/unparseable output; never fall
  back to full-framework solving inside the reference contract.

The ten named fixtures in the constructive report are frozen as the minimum
fixture set, including the empty framework, fact-derived cut target, collective
activation, cut conflict, cut defense, two-component attack union, self/shared/
assumption-valued contraries, cross-state global maximality, and the existing
independent-product `K=empty` case.

## Frozen operational bounds after the semantic gate

These bounds survive adjudication but are **not authorized for execution in
this slice**. After probe 6's semantic contract passes, a separate support-free
pre-measurement contract must enforce all of them before any permitted
development-row shape telemetry:

- at most `100,000` compact graph vertices plus incidences and `50,000` tested
  candidate cutsets, enumerated by increasing size and deterministic order;
- `|K| <= 4`, hence at most `2^|K| <= 16` selected/rejected cut assignments;
- a conservative complete boundary-signature bound of at most `4,096`, checked
  before residual enumeration or solver entry;
- strict reduction of the largest non-cutset residual component in every
  feasible cut assignment, measured against that assignment's pre-split
  residual, not merely by subtracting `|K|`;
- at least one assignment with two nonempty assumption components, with every
  rule factor and contrary link certified as pure boundary or wholly owned by
  one residual component;
- at most `256` stored boundary items per component/state and `4,096` across a
  complete branch, counting cut decisions, exact attacked-`K` bits and
  per-component signatures, active/inactive cross-cut rule factors, symbolic
  proof state, and boundary defense obligations while generated;
- no call to `_minimal_supports`, `build_collective_framework`, SAT/ASP/Z3,
  production preferred solving, any hard row, or the holdout;
- fail closed with the exact failed field and completed partial counts on cap
  overflow, no separator, ambiguous ownership, non-strict reduction, excessive
  boundary state, timeout, exception, or missing output.

The compact-circuit counts do not revive the `3^k` claim: label assignments and
semantic boundary state are reported and capped separately. Any later evidence
that exact boundary state cannot be bounded during construction kills the route
before solver probe and points, at most, to a separately framed incidence-width
or tree-decomposition candidate.

## Budget and next action

This adjudication spends no probe. Campaign usage remains **5 / 8 triage
probes** and **0 / 3 full experiments**. No campaign kill criterion fires.

Exact next action: implement **probe 6's bounded semantic diagnostic/reference
contract and the ten named fixtures**, with no source route, hard-row access,
shape measurement, solver call, benchmark, or holdout access. Only a complete
pass of the frozen semantic contract can authorize the separately bounded
support-free pre-measurement contract.
