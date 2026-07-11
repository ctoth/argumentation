# ICCMA Round-1 H2 Stable-Only Semantic Scout

Date: 2026-07-11

Role: read-only semantic scout. Baseline: `main` at
`9873b4729f0b0c13c7d8362491dd0fee8bac1ee9` (`9873b47`). The tracked tree was
clean before this report; pre-existing untracked files were not used as
evidence. The sealed holdout was not read or run. No solver, benchmark, source
edit, or PDF text extraction was used.

## Decision

**KILL H2 as a Round-1 campaign candidate.**

The semantic core is sound: on finite ordinary **flat** ABA, the proposed
stable-only program is sound and complete, and the complete-semantics
`derived_from_undefeated` closure is redundant once conflict-freeness and
every-OUT-assumption-defeated are both enforced.

The campaign premise is nevertheless invalid. H2 is not "untouched territory"
as claimed in `reports/iccma-round1-hotspot-scout-20260711.md:140-179`. The
committed record
`experiments/2026-05-21-aba-se-st-direct-stable-encoding.md` documents the same
stable-only deletion, a direct page-image semantics check, red-then-green
correctness contracts, a five-row probe, and a real-worker profile. It solved
0/5 timeout rows; the direct path had 2,440 samples in `clingo.Control.solve`
versus 2,450 on the complete-module path, and the record concludes **No-go**
(`:142-221`). Git history identifies the implementation commit as `4b6ee26`
(`Use direct stable ABA ASP encoding`) and the retained diagnosed record as
`4deb85d` (`Promote diagnosed direct stable record`). The production delta was
correctly abandoned.

Thus H2 passes a semantic admissibility screen but fails campaign triage as an
already-performed, diagnosed negative experiment. Reimplementing it would
retry a dead idea without changed evidence. No source slice is authorized.

## Exact semantic claim

Let a finite ordinary ABA framework be `F = (L, R, A, contrary)` and let
`Cl(S)` be the least Horn closure of assumptions `S` under `R`. For an
assumption `a`, define:

```text
S attacks a  iff  contrary(a) is in Cl(S).
```

For flat ABA, no assumption is a rule head. Hence every `S subseteq A` is
closed at the assumption level:

```text
Cl(S) intersect A = S.
```

The repository enforces exactly this boundary by rejecting assumption heads
with `NotFlatABAError` (`src/argumentation/structured/aba/aba.py:62-67`). Its
native stable oracle says that `S` is stable iff it is closed,
conflict-free, and attacks every assumption in `A - S`
(`src/argumentation/structured/aba/aba.py:170-181`).

For the proposed encoding, fix one guessed IN set `S`:

1. `supported` is the least positive-rule closure seeded by the IN
   assumptions, so `supported(x)` iff `x` is in `Cl(S)`.
2. `defeated(a)` iff `supported(contrary(a))`, hence iff `S` attacks `a`.
3. `:- in(A), defeated(A).` (equivalently the proposal's contrary/support
   constraint) enforces conflict-freeness.
4. `:- out(A), not defeated(A).` enforces attack coverage of every outsider.
5. Flatness makes a separate assumption-closure constraint unnecessary.

These are the only semantic ingredients needed for stable extensions.

## Soundness

Take an answer set of the stable-only program and decode its IN assumptions as
`S`.

- The IN/OUT choice places every assumption on exactly one side.
- Positive Horn recursion gives exactly `Cl(S)`, not an arbitrary supported
  superset.
- The conflict constraint implies that no member of `S` is attacked by `S`.
- The OUT constraint implies that every member of `A - S` is attacked by `S`.
- Because the input is flat, `S` is closed.

Therefore `S` satisfies the repository's native definition of a stable
extension. Every decoded answer set is sound.

## Completeness

Let `S` be any stable extension of a finite ordinary flat ABA framework. Choose
exactly `S` as IN and `A - S` as OUT. The positive `supported` rules have the
unique least model `Cl(S)`. Stability gives:

- no `a` in `S` has `contrary(a)` in `Cl(S)`, so conflict-freeness passes; and
- every `a` in `A - S` has `contrary(a)` in `Cl(S)`, so OUT coverage passes.

The guessed partition plus its least Horn closure therefore extends to an
answer set. Every native stable extension is represented, so the encoding is
complete.

## Why the undefeated closure is redundant

The current complete module defines `defeated`, then seeds a second closure
from every assumption that is **not** defeated, and derives
`attacked_by_undefeated` from that closure
(`src/argumentation/encodings/aba_com_incremental.lp:21-28`).

For a stable IN set `S`, let

```text
U = {a in A | S does not attack a}.
```

Conflict-freeness gives `S subseteq U`: no selected assumption is defeated.
Outsider coverage gives `U subseteq S`: every unselected assumption is
defeated. Hence `U = S`. It follows immediately that:

```text
derived_from_undefeated = Cl(U) = Cl(S) = supported
attacked_by_undefeated(a) iff U attacks a iff S attacks a iff defeated(a)
```

Consequently the complete-module constraints collapse to the already-retained
stable constraints. There is no in-scope counterexample to the redundancy
claim for finite ordinary flat ABA.

This equivalence depends on keeping **both** conflict-freeness and complete
OUT coverage. Dropping either breaks `U = S`; the deletion is not justified for
complete, admissible, or preferred semantics.

## Edge cases

### Empty attackers and rule facts

If `contrary(a)` is a zero-body rule fact, the empty set derives it and attacks
`a`. The least positive closure includes the fact even when no assumption is
IN. Thus `a` cannot be IN, while it is legitimately covered when OUT. If every
assumption's contrary is fact-derived, the empty set is stable. This is the
correct treatment of empty attackers; the repository explicitly records their
importance in `aba.py:321-325`.

### Self-attack

For the one-assumption framework with rule `contrary(a) <- a`, `{a}` fails
conflict-freeness and the empty set fails outsider coverage. The encoding has
no answer set, matching the native oracle. A self-attacker may be OUT only when
some derivation available without selecting it attacks it.

### Positive cycles

A cycle such as `c <- d; d <- c` with no selected or factual seed derives
nothing in the least Horn closure. Positive ASP recursion therefore cannot use
an unfounded cycle to fake an attack. With a selected/factual seed, the same
cycle is reached normally. Differential contracts must retain both cases
because completion-style encodings can be wrong here without loop/foundedness
constraints.

### Unsupported contraries

If `contrary(a)` has no derivation, `a` cannot remain OUT: the OUT constraint
forces it IN. This is correct. For a single unattacked assumption, `{a}` is the
stable extension; the empty set is not. Unsupported contraries do not warrant
an extra default-negation shortcut.

### Non-flat exclusion and concrete counterexample

The proof does not extend to non-flat ABA. Let assumptions be `{a,b}`, with
rules

```text
b  <- a
cb <- a
```

and contraries `contrary(a)=ca`, `contrary(b)=cb`, where `ca` is unsupported.
The lean program accepts `S={a}`: it is conflict-free and derives `cb`, so it
attacks the OUT assumption `b`. But `Cl({a})` contains `b`, so `{a}` is not
closed and is not a stable extension of the non-flat framework. This is a
direct counterexample outside H2's valid scope.

Therefore the production boundary must remain fail-closed: construction must
raise `NotFlatABAError` before encoding or routing. The same plain-defeat proof
also does not license ABA+ preferences, where attacks may be reversed or
blocked by preference.

## Executable semantic contracts required before any source slice

The existing generated ASP differential is insufficient as the sole H2 gate:
`tests/structured/aba/test_aba_asp_differential.py:34-58` generates only
non-empty rule bodies aimed directly at contraries. It does not systematically
cover zero-body facts, auxiliary chains, unfounded cycles, or the non-flat
boundary. Before any new source slice, write contracts with these exact
decision surfaces:

1. **Exhaustive bounded flat-ABA model equivalence.** Enumerate all small flat
   frameworks over 0-3 assumptions plus auxiliary literals, including empty
   bodies, multi-step rules, contrary aliases, and cycles. Enumerate every
   stable-only answer set and assert exact extension-family equality with both
   `aba.stable_extensions` and `aba_support_model._SupportState.stable` (through
   a public/reference helper). Equality, not merely witness validity, proves
   soundness and completeness.
2. **Old/new ASP differential.** On the same bounded family, compare the
   extension family from `pi_com + :- out(X), not defeated(X).` with the lean
   program. This directly tests the claimed redundancy rather than only
   comparing two implementation routes at their final API.
3. **Empty-attacker fixtures.** Require the empty extension when all contraries
   are fact-derived; require a fact-attacked assumption OUT when another
   unattacked assumption remains IN; independently validate each result with
   the native oracle.
4. **Self-attack fixtures.** Cover the impossible one-node self-attacker and a
   self-attacker attacked by a distinct selected assumption. Assert exact
   SAT/UNSAT and extension contents.
5. **Founded-cycle fixtures.** Require no attack from an unseeded positive
   contrary cycle, and require derivation once the cycle is seeded. These must
   catch completion models that admit cyclic self-support.
6. **Unsupported-contrary fixtures.** Assert that an unattacked assumption is
   forced IN and that mutually incompatible forced-IN assumptions correctly
   yield no stable extension.
7. **Flatness/variant fail-closed contract.** The concrete non-flat framework
   above must raise `NotFlatABAError` before the direct encoding is loaded;
   ABA+ must not enter the ordinary flat stable-only route.
8. **Single-witness API oracle.** For every bounded framework, `None` iff the
   oracle extension family is empty; otherwise the returned witness must be a
   member of that family. This guards the ICCMA SE-ST surface separately from
   full enumeration.

The repository's performance-contract rule also requires a normally running
operational contract before implementation. The proposal's observer contract
is suitable only as a structural deletion check: the stable grounding must
contain no `derived_from_undefeated`, `triggered_by_undefeated`, or
`attacked_by_undefeated` predicates and must have fewer grounded rules than the
current complete-module route. It is not survival evidence by itself. The
committed prior experiment already showed that deleting those predicates did
not materially change the hard `Control.solve` profile, so a repeat source
slice would additionally need new evidence explaining why the old diagnosis
no longer applies.

## Triage accounting

- Semantic redundancy claim: **confirmed within ordinary flat ABA**.
- Soundness/completeness of the stated lean program: **confirmed**, subject to
  least-Horn-closure encoding and strict flat/ordinary routing.
- In-scope semantic counterexample: **none found**.
- Boundary counterexample: **non-flat framework above**; ABA+ also excluded.
- Novelty premise: **false against committed Git history**.
- Prior operational result: **diagnosed no-go, 0/5, solve bottleneck unchanged**.
- Source experiment authorized: **no**.
- Holdout access: **none**.
- Final Round-1 disposition: **KILL H2; do not spend a fifth probe or reopen the
  abandoned direct-stable slice without evidence that invalidates the
  committed diagnosis.**
