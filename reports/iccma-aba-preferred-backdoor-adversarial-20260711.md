# Adversarial review: ABA preferred backdoor/cutset conditioning

Date: 2026-07-11
Repository HEAD inspected: `7c4a8797007a557214d4e19ca792ffe73cba2d6f`
Mode: read-only source, report, and Git-object inspection; bounded semantic
contract only; no hard ICCMA row, holdout, benchmark, production source change,
or push

## Verdict

**KILL BEFORE PROBE.**

The candidate currently recorded as “branch on a small assumption/contrary
cutset with `IN/OUT/UNDEC`, then solve exact residual components” does not have
an exact boundary bounded by `3^k`, where `k` is the number of cutset
assumptions or contrary literals. The labels do not determine cross-boundary
Horn derivability, collective attacks, or whether a projected attack may be
used for defense. Preferred semantics also requires rejecting infeasible
cutset labels, preserving global defense obligations, deduplicating lifts, and
taking inclusion-maximal admissible lifts globally.

A finite exact boundary exists because the framework is finite, but its
explicit form contains the crossing collective tails (or an equivalent Horn
proof circuit), their active/defeated/mitigated status, attacked and candidate
sets, and global lift/maximality information. Its size is not bounded by the
cutset size. With a one-assumption cutset there can be arbitrarily many, and
explicitly exponentially many, crossing minimal supports. Materializing that
state therefore recreates the support-antichain surface that killed probe 5.
Keeping the Horn circuit compact avoids that materialization only by retaining
cross-residual coupling, so the claimed independent residual decomposition no
longer follows from the small assumption cutset.

This verdict kills this candidate before it consumes probe 6. It does not
invalidate a separately framed bounded-incidence-width or tree-decomposition
algorithm whose parameter includes the actual rule/proof boundary; that is a
different candidate and is not authorized here.

## Semantic authority

For ordinary finite flat ABA, every assumption subset is closed because an
assumption cannot be a rule head. A set is admissible iff it is conflict-free
and counterattacks every closed attacker; preferred extensions are exactly the
inclusion-maximal admissible sets (`src/argumentation/structured/aba/aba.py:40-67,
131-166,318-329`). The support oracle makes the same quantification explicit:
every minimal support of a selected assumption's contrary must contain some
assumption attacked by the candidate
(`src/argumentation/structured/aba/aba_support_model.py:51-85,108-164`).

The existing bounded collective-attack reference already records the state
that simple labels omit: selected and attacked assumptions, defeated and
provisionally defeated sets, candidates, conditioned attacks, and mitigated
attacks (`scripts/aba_scc_composition_reference.py:34-55,211-299`). Its named
contract covers collective cross-SCC tails, factual attacks, derived chains and
cycles, shared/assumption-valued contraries, defeated tails, mitigation, and
stable branch annihilation
(`tests/structured/aba/test_aba_scc_composition_contract.py:58-214`). The
focused contract was rerun at this HEAD:

```text
uv run pytest -q tests/structured/aba/test_aba_scc_composition_contract.py
..............                                                           [100%]
14 passed in 1.91s
```

No scientific paper was reread for this report; therefore no PDF text
extraction or paper-derived claim is used.

## Exact minimal counterexamples

Notation: `A` is the assumption set, `bar(a)` is the contrary of `a`, and
`h <- b1,...,bn` is a Horn rule. A contrary called `na`, `nb`, etc. is a fresh
literal with no deriving rule unless one is shown.

### 1. Collective tail split across cutset and residuals

```text
A = {x, b, c}
bar(x)=nx, bar(b)=nb, bar(c)=nc
nc <- x,b
cutset K = {x}
```

The sole preferred extension is `{x,b}`. Any set containing `c` must defend it
against the attacker `{x,b}`, but no set attacks `x` or `b`; `{x,b}` is
conflict-free, admissible, and maximal.

In the `x=IN` branch the residual projection `{b}->c` is active. In an
`x=OUT` or `x=UNDEC` branch, deleting that projection is unsound: `{x,b}` is
still a possible attacker against `c`, even though `x` is not selected in the
candidate. The projection must remain as a mitigated defense obligation and
must not be usable as a counterattack. A residual product that deletes it
returns the spurious lift `{b,c}`. This is the three-assumption minimum for a
two-member collective tail attacking a distinct target and already appears as
the contract's `multi_body_cross_scc` shape
(`tests/structured/aba/test_aba_scc_composition_contract.py:62-67,139-153`).

### 2. Factual attack and infeasible branch

```text
A = {a}
bar(a)=na
na <-
K = {a}
```

The sole preferred extension is `{}`. The empty attacker cannot be
counterattacked, so `a=IN` has no completion. There is no tail vertex for a
graph cutset to label. Exact conditioning must normalize the fact or carry an
explicit empty-tail attack; treating “no incoming assumption” as “unattacked”
returns `{a}`. The direct oracle explicitly includes the empty attacker
(`src/argumentation/structured/aba/aba.py:318-329`), and the existing contract
asserts factual normalization
(`tests/structured/aba/test_aba_scc_composition_contract.py:68-72,156-162`).

### 3. Derived chain and seeded/unseeded cycle

```text
A = {x, b, c}
bar(x)=nx, bar(b)=nb, bar(c)=nc
p  <- x
q  <- p
p  <- q
nc <- q,b
K = {x}
```

The least Horn closure gives the same exact collective attacker `{x,b}->c`,
and the sole preferred extension is `{x,b}`. With `x` absent, the positive
`p/q` cycle derives neither literal; with `x` present, it derives both. A label
on `x` plus inspection of only contrary-headed rule bodies sees `b` but misses
the mediated prerequisite and the least-fixpoint distinction. Exact state must
carry boundary derivability through arbitrary chains and cycles, not merely
assumption labels. The committed contract separately pins seeded derived chains
and unseeded positive cycles
(`tests/structured/aba/test_aba_scc_composition_contract.py:73-91`).

### 4. Shared, assumption-valued contrary

```text
A = {a, b, c}
bar(a)=c, bar(b)=c, bar(c)=nc
no rules
K = {c}
```

The sole preferred extension is `{c}`. Selecting the assumption `c` also
derives the shared contrary of both `a` and `b`; neither `a` nor `b` can defend
itself against attacker `{c}`. Thus one boundary literal simultaneously has
membership, derivability, and two attack effects. Duplicating it per target or
treating “contrary literal” and “assumption label” as independent creates
inconsistent branches. The repository explicitly permits shared and
assumption-valued contraries (`ABAFramework` requires only that contrary values
belong to the language), and the named contract exercises this case
(`src/argumentation/structured/aba/aba.py:40-67`;
`tests/structured/aba/test_aba_scc_composition_contract.py:107-113`).

### 5. Defense obligation spanning cutset and two residual regions

```text
A = {x, b, c, d}
bar(x)=nx, bar(b)=nb, bar(c)=nc, bar(d)=nd
nc <- x,b
nb <- d
K = {x}
```

The sole preferred extension is `{x,c,d}`. Assumption `c` is attacked by
`{x,b}` but is defended because `d` attacks member `b` of that attacker.
Assumption `b` is never admissible because attacker `{d}` cannot be
counterattacked. A local solver for `c` needs both the cutset prerequisite `x`
and the counterattack derived in `d`'s residual region. An `IN/OUT/UNDEC` label
for `x` contains neither obligation. Solving the `b`, `c`, and `d` regions
independently therefore either rejects the valid `c` or accepts an undefended
one.

### 6. Locally admissible lift is not globally preferred

```text
A = {x, a}
bar(x)=nx, bar(a)=na
no rules
K = {x}
```

In the `x=OUT` branch, the residual's locally preferred/admissible choice is
`{a}`. Its lift `{a}` is globally admissible but not preferred, because
`{x,a}` is a strict admissible superset. The `OUT` and `UNDEC` branches have no
globally preferred completion; only `x=IN` does. Hence local maximality does
not establish global maximality, and branch-local success does not establish a
preferred lift. The production enumerator's semantics is global inclusion
maximality (`src/argumentation/structured/aba/aba.py:157-166`); the SCC
reference likewise enumerates admissible lifts and only then filters strict
subsets (`scripts/aba_scc_composition_reference.py:151-190`).

### 7. Duplicate lifts from support-witness branching

```text
A = {a, b, c}
bar(a)=na, bar(b)=nb, bar(c)=z
z <- a
z <- b
```

The sole preferred extension is `{a,b}`. Assumption `c` has two distinct
minimal attackers, `{a}` and `{b}`; it cannot defend against either. A
conditioning scheme that branches on which support establishes `z` produces
two successful proof branches for the same selected assumption set `{a,b}`.
The extension family must be canonicalized by assumption set, and branch count
cannot be reported as extension count. The support model intentionally retains
both minimal supports (`aba_support_model.py:108-164`), while the reference
sorter deduplicates complete lifts
(`scripts/aba_scc_composition_reference.py:445-453`).

### 8. A cutset branch with no useful residual reduction

```text
A = {x, a, b}
bar(x)=nx, bar(a)=na, bar(b)=nb
na <- b
nb <- a
K = {x}
```

The preferred extensions are `{x,a}` and `{x,b}`. Since `x` is unattacked,
only `x=IN` is feasible. Removing it fixes no residual assumption, removes no
residual rule, and does not split or shrink the mutually attacking `{a,b}`
core; `OUT` and `UNDEC` merely create infeasible branches. Counting deletion of
the chosen cutset itself as “strict reduction” would make every cutset pass
without reducing the hard residual. The operational contract must require a
strict decrease in the largest non-cutset exact residual/component on every
feasible branch, not `|A|-k < |A|`.

## Why `3^k` is not an exact state bound

The queued hypothesis states that branch count is bounded by `3^k`
(`workstreams/aba-next-optimization-possibilities.md:181-204`). That bounds
only label assignments. It does not bound the semantic boundary that each
assignment must carry.

Fix `k=1` with cutset `{x}`. For arbitrary `m`, introduce assumptions
`u_i,v_i` (`1 <= i <= m`) and `c`, derived literals `t_i`, and rules

```text
t_i <- u_i
t_i <- v_i
bar(c) <- x,t_1,...,t_m
```

The contrary of `c` has exactly `2^m` inclusion-minimal assumption supports:
`{x}` plus one choice from each pair `{u_i,v_i}`. All are crossing collective
attackers of `c`. Exact defense of `c` quantifies over every one of them. Thus
an explicit tail/mitigation boundary has size at least `2^m` while `k=1`.
There is no function of this cutset size alone that bounds those explicit
items.

The Horn rules are a compact circuit for the same family, so exactness does not
mathematically require eager support enumeration. But retaining that circuit
also retains a rule whose truth depends jointly on every residual pair; the
residual regions are not independent under the assumption cutset. To recover a
bounded dynamic program, the parameter must cover the literal/rule incidence
boundary (and its width), not just `{x}`. That is the distinct tree/incidence-
width family already separated from the small-candidate list in
`reports/iccma-history-sepr-inventory-20260711.md:224-242`.

Probe 5 supplies the operational corroboration for the explicit form: eager
`_minimal_supports` antichain construction consumed about 13 minutes and 2.3 GB
before the post-extraction 4,096-attack cap could execute
(`experiments/2026-07-11-iccma2023-probe-5-scc-operational-measurement.md:41-70,
75-105`). Reusing explicit collective tails here would repeat that diagnosed
surface, not avoid it.

## Exact finite boundary that would restore correctness

For each complete branch, an exact residual composition must preserve at
least:

1. selected cutset assumptions and consistency of their `IN/OUT/UNDEC`
   labels with the global least Horn closure;
2. truth of every boundary literal needed by a crossing rule, including facts
   and seeded versus unseeded cycles;
3. every crossing collective attacker, or an equivalent symbolic proof
   circuit, with residual tail and three-way status: active, defeated, or
   mitigated/provisional;
4. the globally attacked set used to decide conflict and counterattack;
5. every defense obligation whose attacker spans regions, including the rule
   that a mitigated projection may attack but may not be used as a defense;
6. branch feasibility and annihilation when no exact completion exists;
7. canonical selected-assumption lifts, independent of proof/support witness;
8. all admissible lifts until a global inclusion-maximality filter has removed
   dominated sets.

The existing reference's `ComponentBoundary` is a concrete finite instance of
items 1-5, and its final filter/deduplication supplies items 7-8
(`scripts/aba_scc_composition_reference.py:43-55,151-190,211-299,445-453`).
That state restores exactness on bounded inputs, but its measured item count is
explicitly separate from branch count (`scripts/aba_scc_composition_reference.py:
263-285`). It is not bounded by `k`.

Post-hoc validation of each lifted set against the full framework is necessary
as a guard but is not a decomposition theorem: complete enumeration plus full
admissibility/maximality validation recreates the original preferred problem.
The current independent-product implementation avoids this only when every
rule and contrary is confined to one incidence component; otherwise it reports
`component_plan_not_exact` and falls back to the full instance
(`src/argumentation/structured/aba/aba_decomposition.py:40-81,191-245`).

## Git-history audit

The audit used all visible refs:

```text
git log --all --oneline --regexp-ignore-case --grep="backdoor|cutset|conditioning|separator|decomposition"
git log --all --oneline -G"backdoor|cutset|conditioned|conditioning|separator" -- . ":(exclude)papers"
git log --all --oneline -S"backdoor" -- . ":(exclude)papers"
git log --all --oneline -S"cutset" -- . ":(exclude)papers"
```

No Git object implements assumption-backdoor/cutset conditioning for ABA
preferred enumeration. The matching history consists of:

- the proposal queue at `fd36cd7`, which states the unproved `3^k` contract;
- the exact independent-product planner at `3536db3` and its route/metadata
  follow-ups, which deliberately reject crossing rules/contraries;
- stable-only SCC-local encoding attempts, not residual composition;
- the collective-attack SCC semantic reference at `82072ee` and its probe-5
  operational kill at `7c4a879`.

This confirms the inventory's novelty statement
(`reports/iccma-history-sepr-inventory-20260711.md:224-235`) but does not supply
missing exactness or an operational bound. The candidate is novel and still
dead as framed.

## Contracts that would have been necessary

These are kill conditions, not authorization for probe 6:

- **Bidirectional family equality:** all lifted preferred extensions equal both
  direct native and support-oracle families, not merely “every returned lift
  validates.”
- **Pinned counterexamples:** all eight cases above, including rejection of
  infeasible labels and equality of deduplicated extension families.
- **Boundary sufficiency:** two partial branches with the same declared state
  must have exactly the same sets of admissible residual completions; a found
  distinguishing completion falsifies the state.
- **Executable bound:** before any hard row, cap boundary construction while it
  is generated, including proof/support states, mitigated attacks, and defense
  obligations. A cap checked after extraction is invalid by probe 5's record.
- **Useful reduction:** every feasible branch must strictly reduce the largest
  non-cutset exact residual/component and must not call the full preferred
  oracle merely to establish composition.
- **Accounting:** separately report label branches, infeasible branches,
  boundary items, symbolic proof-state size, residual component sizes, local
  admissible lifts, unique lifted sets, and globally preferred lifts.

The fixed-`k=1` exponential-support family falsifies the proposed
cutset-only bound before such a contract can be satisfied. Therefore the
correct campaign action is **KILL BEFORE PROBE**, with probe usage remaining
`5 / 8` and full experiments `0 / 3` as recorded at HEAD
(`experiments/INDEX.md:22-30,202-240`).
