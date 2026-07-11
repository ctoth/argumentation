# Exact assumption-cutset conditioning for finite flat ABA preferred enumeration

Date: 2026-07-11
Repository HEAD inspected: `7c4a8797007a557214d4e19ca792ffe73cba2d6f` (`main`)
Mode: read-only constructive research; this report is the only file written

## Verdict

**PROCEED TO SEMANTIC CONTRACT.**

There is a small exact theorem: after factual normalization, condition on a
bounded set of assumptions `K`; require `K` to separate the compact
rule/contrary incidence graph; and augment each `K` selection with the exact
attacked-`K` signature contributed by each residual component. Under that full
boundary state, admissibility is a conjunction of independent component
predicates. Union the component choices with the selected assumptions in `K`,
deduplicate, and apply one global inclusion-maximality filter. The result is
exactly the preferred-extension family.

This verdict does **not** authorize hard-row telemetry or a solver probe. The
bounded differential contract below must exist and pass first. The subsequent
pre-measurement contract must then find a useful cutset without enumerating
minimal supports. If either gate fails, the route fails closed.

Exact reasons to proceed only this far:

1. The direct oracle defines preferred extensions as all inclusion-maximal
   admissible assumption sets (`src/argumentation/structured/aba/aba.py:131-167`),
   while the independent support oracle implements the same collective-attack
   test over minimal support masks (`aba_support_model.py:25-95` and
   `aba_sat.py:61-97`). The theorem below factors those exact predicates; it
   does not weaken them and does not use post-hoc validation as its proof.
2. The compact separator is a conditioned generalization of, not a rename for,
   the kept undirected product planner. That planner permits only components in
   which every rule and contrary is already wholly internal and otherwise
   returns `component_plan_not_exact` (`aba_decomposition.py:40-80,191-245`).
   Here the only allowed cross-component vertices are explicitly branched
   assumptions in `K`.
3. The killed probe-5 route eagerly called `_minimal_supports` before its 4,096
   attack cap could be checked (`experiments/INDEX.md:208-227`; implementation
   at `aba_support_model.py:108-164`). This proposal discovers and certifies its
   separator on the linear-size rule-incidence input first. It must not revive
   the killed eager support-primal measurement.
4. No current measurement shows that either 600-assumption timeout has a useful
   `K`. The campaign ledger therefore requires the exact semantic and bounded
   structural contracts before any solver probe (`experiments/INDEX.md:237-240`).

## Scope and semantic authority

Let an ordinary finite flat ABA framework be

`F = (L, R, A, contrary)`,

where `R` is a finite set of Horn rules `h <- B`, every assumption has exactly
one contrary, and no assumption is a rule head. These are the constructor's
enforced conditions (`aba.py:40-71`). ABA+, non-flat ABA, infinite languages,
and non-Horn deduction are outside this theorem.

For `E subseteq A`, let `Cl(E)` be the least Horn closure. For each assumption
`a`, let

`Supp(a) = Min_subseteq {T subseteq A | contrary(a) in Cl(T)}`.

The induced collective-attack relation is

`H_F = {(T, a) | a in A and T in Supp(a)}`.

Write `Atk(E) = {a | exists (T,a) in H_F with T subseteq E}`. Then, exactly as
implemented by the two current oracles:

- `E` is conflict-free iff `E intersect Atk(E) = empty`;
- `E` defends selected `a` iff, for every `(T,a)`,
  `T intersect Atk(E) != empty`;
- `E` is admissible iff it is conflict-free and defends every `a in E`;
- `E` is preferred iff it is inclusion-maximal among admissible sets.

The defense equivalence includes the empty attacker: the direct oracle
deliberately enumerates it (`aba.py:318-329`), and the support oracle returns
false immediately for support mask zero (`aba_support_model.py:68-77`).

## Exact factual and rule normalization

Compute `Q = Cl(empty)` once. Let

`F0 = {a in A | contrary(a) in Q}`.

No admissible set contains an assumption in `F0`: selecting it is conflict, and
no set attacks the empty attacker. Normalize to `A' = A - F0` and:

1. delete every collective attack whose target is in `F0`;
2. delete every collective attack whose tail intersects `F0`;
3. retain all other attacks unchanged.

This preserves admissible and preferred extensions literally, because all
extensions already exclude `F0`. It also handles a fact-derived contrary chain,
not only a syntactic empty-body contrary rule. The existing SCC reference uses
the same semantic normalization (`scripts/aba_scc_composition_reference.py:106-133`).

For compact, support-free discovery, apply the equivalent rule normalization:

- discard a rule whose body contains an assumption in `F0`;
- delete every body literal in `Q`;
- retain an empty residual body as a fact;
- retain Horn conjunction: stripping a true boundary literal never splits the
  remaining body into singleton alternatives;
- iterate least closure after each later `K` assignment, because selected `K`
  assumptions can turn residual rules into new facts and rejected `K`
  assumptions can make rules dead.

The later `K`-conditioned discard applies only to closure/attacks made by the
candidate. The unconditioned attack-proof circuit remains available to generate
the defense obligations described below; rejection from the candidate is not
proof that an external attacker cannot select that assumption.

Rules with duplicate syntax are sets in the current model; rule order has no
semantic meaning. Assumptions remain forbidden as rule heads.

## Cutset definition

Build the **normalized proof/contrary incidence graph** `I_F` without computing
minimal supports:

- vertices are every normalized literal, every normalized rule (as its own
  factor vertex), and every assumption in `A'`;
- connect a rule vertex to its head and to each body literal;
- connect each assumption `a` to `contrary(a)`;
- treat the graph as undirected only for separation.

An **assumption cutset** is `K subseteq A'` such that deleting the assumption
vertices in `K` leaves at least two connected components containing assumptions.
Let their assumption sets be `C1,...,Cm`; literal/rule-only components may be
dropped after their factual closure is accounted for.

This is deliberately a conservative separator. Every Horn proof tree for a
contrary is connected in `I_F`, including multi-step derivations and shared
intermediate literals. Therefore, for every normalized collective attack
`r=(T,a)`, the non-cut vertices `(T union {a}) - K` are empty or lie in exactly
one `Ci`. The compact graph may merge true support-primal components, but it
cannot falsely separate a collective tail. This certificate is checkable in
time linear in the stored rule/body incidence once `K` is given.

Assign each attack to bucket `R0` when `(T union {a}) subseteq K`; otherwise
assign it to the unique `Ri` whose component contains
`(T union {a}) - K`. This assignment is a semantic definition for the theorem;
the bounded differential reference may materialize supports, while operational
discovery must use the compact certificate above.

## Full branch state on `K`

A mere IN/OUT choice on `K` is not enough. Components can attack assumptions in
`K`, and those facts affect both conflict-freeness of selected `K` assumptions
and defense through `K` tail members.

For a cut selection `X subseteq K`, define rejected assumptions `N = K - X`.
For a component choice `Yi subseteq Ci`, define

`Ai(X,Yi) = {a in K union Ci | exists (T,a) in Ri, T intersect K subseteq X,
                                      and T intersect Ci subseteq Yi}`.

Define the pure-cut attack set analogously:

`A0(X) = {a in K | exists (T,a) in R0 and T subseteq X}`.

The smallest explicit exact branch state is

`sigma = (X, N, B1,...,Bm, Z, O0,O1,...,Om)`,

where:

- `X` and `N` are selected and rejected `K` assumptions, with `N=K-X`;
- `Bi subseteq K` is the **exact** attacked-`K` signature contributed by
  component `i`, constrained by `Bi = Ai(X,Yi) intersect K`;
- `Z` is the global attacked-`K` set,
  `Z = (A0(X) intersect K) union B1 union ... union Bm`;
- `O0` contains pure-cut attacks `(T,k) in R0` with `k in X` and
  `T intersect Z = empty`;
- `Oi` contains component attacks `(T,k) in Ri` with `k in X` and
  `T intersect Z = empty`.

`O0` must be empty. Each obligation in `Oi` must be discharged by a locally
attacked member of `T intersect Ci`. The obligation sets are derived from
`X,Z`, and the original attacks; they are recorded explicitly so an
implementation cannot silently forget defense of selected cut assumptions.

The attacked signatures `Bi` are essential. Replacing them with one Boolean
"a cross-cut attack exists", or requiring only `Bi subseteq Z`, is unsound.
Exact equality prevents one component from taking credit for an attack produced
only by another component. `Z` may overlap `N`; it must not overlap `X` on a
conflict-free branch.

For computing attacks **made by the candidate**, a collective tail crossing
`K` has only two states in a residual component:

- if every cut member of the tail is in `X`, remove those members and retain
  the remaining conjunctive tail;
- if any cut member is in `N`, discard the attack as inactive.

That discard does not erase a possible attacker for defense. Admissibility asks
whether the candidate counterattacks every attacking set, including a tail
containing assumptions rejected by the candidate. Therefore every original
tail remains in the defense constraints below, and its cut members are tested
against `Z`, not `X`. There is no provisional third state and no
mitigated-attack `M` state: total cut selection plus exact attacked-cut set `Z`
fully determines whether an omitted cut tail member discharges defense. The
`M` state was necessary for sequential SCC recursion with not-yet-decided
predecessors (`iccma-aba-scc-composition-adversarial-20260711.md:169-248`).

## Independent exact residual predicate

For fixed `sigma`, component `i` independently enumerates `Yi subseteq Ci` and
keeps it iff all of the following hold:

1. **Exact boundary contribution:** `Ai(X,Yi) intersect K = Bi`.
2. **Local conflict freedom:** `Yi intersect Ai(X,Yi) = empty` and
   `X intersect Ai(X,Yi) = empty`.
3. **Defense of selected local assumptions:** for every `a in Yi` and every
   `(T,a) in Ri`, whether or not `T` is selected by the candidate,
   `T intersect (Ai(X,Yi) union Z) != empty`.
4. **Boundary defense obligations:** for every attack in `Oi`,
   `(T intersect Ci) intersect Ai(X,Yi) != empty`.

Pure-cut validity is checked once: `X intersect A0(X)=empty`, `O0=empty`, and
the union equation defining `Z` holds. No residual predicate reads another
component's selected assumptions or attack set; it reads only fixed `sigma`.
Thus its extension family `Adm_i(sigma)` is exact and independent.

## Exact preferred-conditioning theorem

Let `Valid` be all branch states satisfying the partition, pure-cut, union, and
obligation conditions above. Define admissible lifts

`L_Adm(F,K) = {X union Y1 union ... union Ym |
               sigma in Valid and Yi in Adm_i(sigma) for every i}`.

Then, for every finite ordinary flat ABA framework and every assumption cutset
`K` of its normalized proof/contrary incidence graph:

`L_Adm(F,K) = Admissible(F)`

and therefore

`Max_subseteq(L_Adm(F,K)) = Preferred(F)`.

### Proof

Fix any candidate `E subseteq A'`, put `X=E intersect K` and
`Yi=E intersect Ci`, and derive its unique exact `Bi`, `Z`, and `Oi` values.
By the separator property, every attack is pure-cut or belongs to exactly one
component bucket. Hence `Atk(E)` is exactly

`A0(X) union A1(X,Y1) union ... union Am(X,Ym)`.

Global conflict freedom is therefore equivalent to the pure-cut and component
conflict clauses. For a selected local assumption, every attacking tail lies
in its component plus `K`; whether its cut members are attacked is exactly `Z`,
and whether its local members are attacked is exactly `Ai`. For a selected cut
assumption, each attacking tail is pure-cut or belongs to one component; `O0`
and `Oi` express exactly the otherwise-unsatisfied defense cases. Thus the
global defense predicate is equivalent to the conjunction of the pure-cut and
component defense predicates. This proves both inclusions for admissibility.
The current preferred definition is precisely inclusion-maximal admissibility,
so taking all and only maximal lifts proves the second equality. QED.

### Global maximality, lift, and deduplication

Do not choose independently locally preferred/maximal `Yi`. A larger local set
can change `Bi`, hence `Z`, hence the validity and defense obligations of other
components and selected `K`. Enumerate admissible residual choices under exact
states, lift by set union, canonicalize every lift as a `frozenset` of original
assumptions, deduplicate identical lifts, and only then remove every lift that
is a strict subset of another lift. Auxiliary rule/literal vertices, attack
signatures, and normalized fact-attacked assumptions are never lifted.

Exact `Bi` makes the semantic state induced by a fixed lift unique, but explicit
deduplication remains required for enumerator robustness and for any later
witness-owner compression of the union equation.

## Edge cases required by the theorem

- **Empty assumption universe:** after normalization, `K` and every `Ci` are
  empty; the only admissible and preferred lift is the empty set.
- **Factual/empty attacker:** every target in `F0` is removed before cutset
  discovery and never lifted. A framework with `contrary(a) <- empty` has the
  preferred family `{empty}`.
- **Self attack:** `(T,a)` with `a in T` remains in its bucket. Any selection
  activating it fails conflict freedom, including `contrary(a)=a`, whose
  assumption-valued contrary yields tail `{a}`.
- **Shared contrary:** the same minimal support is copied to every assumption
  having that contrary; each `(T,target)` remains a distinct attack and defense
  obligation.
- **Assumption-valued contrary:** flatness permits the contrary literal to be an
  assumption even though assumptions cannot be rule heads. Its minimal support
  is its singleton, producing the corresponding ordinary or self attack.
- **Collective tail crossing `K`:** conjunctive activation is retained. A tail
  with two residual non-cut assumptions cannot span two `Ci` by the incidence
  separator certificate.
- **No admissible local result:** that `sigma` contributes no lift. It is not
  converted into an empty local choice.
- **Incomparable maxima:** all survive the single global maximality filter.

## Bounded differential semantic contract

The next artifact should be a diagnostic/reference test, not production code.
It may materialize minimal supports only under the existing small-framework
bound. It must:

1. Generate ordinary flat ABA frameworks with `0..5` assumptions, at most `4`
   non-assumption literals, at most `8` rules, body width `0..3`, arbitrary rule
   order, shared intermediate literals, shared and assumption-valued
   contraries, and no assumption heads.
2. Enumerate every `K subseteq A'` with `|K| <= min(3,|A'|)` that satisfies the
   incidence-cutset definition; include `K=empty` for already-independent
   frameworks and require exercised nonempty cutsets.
3. Enumerate every valid full boundary state and every residual choice, then
   lift, deduplicate, and globally maximize exactly as above.
4. For at least `300` deterministic Hypothesis examples with `deadline=None`,
   assert complete family equality in both directions against both
   `aba.preferred_extensions(framework)` and
   `aba_sat.support_extensions(framework, "preferred")`. These are independent
   current exhaustive oracles (`aba.py:157-167`; `aba_sat.py:61-97`). Witness
   membership alone is insufficient.
5. Assert path counters showing: nonempty `K`; selected and rejected cut states;
   an attacked cut assumption; a boundary defense obligation created and
   discharged; an inactive tail discarded due to rejected `K`; an activated
   collective residual tail; at least two independent residual components; a
   fact-attacked normalization; deduplication; and at least two incomparable
   preferred lifts.
6. Fail on cap overflow, missing path coverage, oracle disagreement, exception,
   or unparseable output. Do not replace a failed exact branch with direct
   full-framework solving.

Candidate named fixtures:

1. `empty_framework`: zero assumptions and rules.
2. `fact_derived_cut_target`: a multi-step fact chain derives `contrary(k)`.
3. `selected_cut_collective_activation`: `{k,a} -> b` with `K={k}`; selected
   `k` activates residual `{a}->b`, rejected `k` discards it.
4. `cut_attack_conflict`: `{a}->k` with `K={k}`; a component's exact `Bi`
   invalidates the branch selecting `k`.
5. `cut_defense_obligation`: `{a}->k` and `{b}->a`, with `K={k}`; selecting `k`
   is admissible only when the component attacks `a`.
6. `two_component_cut_attack_union`: `{a}->k` and `{b}->k`, with residual
   assumptions `a` and `b` in distinct components; exercises exact per-component
   `Bi`, union into `Z`, and lift deduplication.
7. `self_and_assumption_contrary`: `contrary(a)=a` plus an independent component.
8. `shared_contrary_targets`: two targets share a contrary derived by a
   collective tail crossing `K`.
9. `global_maximality_across_states`: two admissible lifts from different
   boundary signatures where one strictly contains the other, plus a third
   incomparable maximum; proves maximality happens after the union.
10. `already_independent_k_empty`: matches the current exact-product case and
    proves the cutset theorem conservatively subsumes it.

## Operational pre-measurement contract

Only after the semantic contract passes may a support-free shape tool inspect
the frozen development timeout frameworks. Before any solver, hard ICCMA row,
benchmark, or holdout access, it must satisfy all clauses below on its permitted
development inputs:

1. **Bounded deterministic discovery.** Build normalized `I_F` directly from
   stored rules with caps of `100,000` total vertices plus incidences and
   `50,000` tested candidate cutsets. Enumerate assumption combinations by
   increasing size, then lexicographic `repr`, stopping at `|K|=4`. Exhausting
   either cap returns `route_disabled: discovery_cap_exceeded`; it does not
   claim that no cutset exists.
2. **Cut/branch cap.** Require `|K| <= 4`, hence at most `2^|K| <= 16`
   selected/rejected cut assignments. Before residual enumeration, compute a
   conservative full boundary-signature upper bound; require it to be at most
   `4,096`. No lazy overflow after solver entry is allowed.
3. **Strict reduction in every cut assignment.** After conditioning rules and
   recomputing factual closure for each of the at most 16 assignments, every
   surviving branch must have
   `max_i |Ci_branch| < |A'_branch_before_component_split|`. A branch with one
   residual component containing all remaining assumptions fails this clause.
4. **Useful independent residuals.** At least one cut assignment must have at
   least two nonempty assumption components, and every reported component split
   must pass the structural certificate that each conditioned rule factor and
   contrary link is pure boundary or wholly inside one component. Literal-only
   components and empty branches do not count as useful.
5. **Bounded boundary obligations.** Count exact cut selections/rejections,
   attacked-`K` bits, component `Bi` bits, active/inactive cross-cut rule factors,
   and boundary defense obligations. Require at most `256` stored boundary items
   in any component/state and at most `4,096` across a complete branch. Counts
   are over the compact rule circuit, not post-hoc minimal supports.
6. **No killed-route substitution.** Discovery and cap checks must not call
   `_minimal_supports`, `build_collective_framework`, a SAT/ASP/Z3 solver, the
   production preferred path, or the holdout. The probe-5 cap failed precisely
   because support extraction preceded its check
   (`experiments/2026-07-11-iccma2023-probe-5-scc-operational-measurement.md:38-106`).
7. **Fail closed.** Missing input, cap overflow, ambiguous component ownership,
   a cross-component factor, non-strict residual, excessive boundary state,
   semantic-contract failure, exception, timeout, or missing output disables
   the route and spends no solver probe. It must emit the exact failed field and
   completed partial counts; no inferred metric and no fallback success.

Passing this pre-measurement contract would authorize only deterministic shape
telemetry on the allowed development rows. It would not itself authorize a
production slice, hard solve, benchmark, or holdout access.

## Git-history audit: not a renamed tried route

The audit used current `git log --all`, content searches for `backdoor`,
`cutset`, `separator`, and SCC/ABA terms, path history, and branch containment.
The material history is:

- `3536db3` introduced the current independent-product planner and `dff109c`
  routed it. Its exactness certificate rejects every crossing rule/contrary
  (`aba_decomposition.py:191-245`); this theorem conditions the crossing
  assumptions instead.
- The SE-PR inventory records that product decomposition was a kept narrow win
  but returned `component_plan_not_exact` on T1/T3/T5/T6, and separately lists
  small backdoor/cutset conditioning as unimplemented
  (`iccma-history-sepr-inventory-20260711.md:119-130,219-237`).
- The SE-ST inventory distinguishes full cutset conditioning from SCC-local
  ranks, SCC-local founded levels, static loop preload, and SCC-local
  arc-acyclicity, and finds no committed full stable decomposition/cutset solver
  (`iccma-history-sest-inventory-20260711.md:388-412,486-508`).
- `82072ee` added exact support-hypergraph SCC semantics, `2dba279` pinned its
  mitigation counterexample, and `7c4a879` recorded its operational kill. That
  route topologically conditions every SCC after eagerly materializing minimal
  supports (`aba_scc_composition_reference.py:106-208`); this candidate instead
  branches on a bounded assumption separator found from compact rule incidence.
- `fd36cd7` contains planning text for a small cutset and a `3^k` sketch
  (`workstreams/aba-next-optimization-possibilities.md:181-204`), but no source,
  executable semantic contract, or measurement. The present theorem corrects
  that sketch: ordinary preferred admissibility needs selected/rejected `K`
  plus exact attacked-`K` component signatures and defense obligations, not an
  unexplained independent IN/OUT/UNDEC label product.

No visible commit or ref implements the theorem above. It is therefore a
genuinely distinct candidate, while reuse of eager support extraction, blind
products, local preferred maxima, or SCC `D/P/U/UP/C/M` under a new name is
explicitly excluded.

## Final gate

Proceed only to the bounded semantic contract and the ten named fixtures. Kill
before probe if the contract cannot reproduce the complete preferred family of
either current oracle, if exact attacked-`K` signatures or defense obligations
cannot be bounded even on the synthetic domain, or if the compact incidence
certificate does not make residual component ownership unique. If it passes,
the next decision is made solely by the operational pre-measurement contract;
there is currently no evidence that a useful hard-row cutset exists.
