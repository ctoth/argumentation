# Constructive exact SCC composition for finite flat ABA

Date: 2026-07-11
Repository HEAD inspected: `0d03790a0d62e06f013910898810a1fbf0538bdf` (`main`)
Mode: read-only semantic research; this report is the only file written

## Verdict

An exact directed SCC-conditioning theorem is viable for both ordinary finite
flat ABA stable and preferred extensions.

The same directed graph supports both semantics. Stable extensions can be
recognized component by component. Preferred extensions require componentwise
recognition of **admissible** candidates followed by one global
inclusion-maximality filter after lifting. That final filter is essential: this
report does not prove that independently choosing a locally preferred set in
each SCC preserves all globally preferred extensions.

This is a semantic theorem only. It neither establishes useful SCC shapes on
the campaign rows nor supplies performance evidence. The inventory freeze in
`experiments/INDEX.md:157-181` requires exactly this semantic contract before
any shape measurement. The committed SE-PR and SE-ST inventories distinguish
the target from the existing undirected independent-product planner,
SCC-local rank/foundedness encodings, and AF SCC recursion
(`reports/iccma-history-sepr-inventory-20260711.md:119-129,224-251` and
`reports/iccma-history-sest-inventory-20260711.md:385-411,565-590`).

## Semantic authority and scope

Let an ordinary finite flat ABA framework be

\[
F=(L,R,A,\bar{\cdot}),
\]

where (L) is a finite set of literals, (A\subseteq L) is the set of
assumptions, (R) is a finite set of Horn rules (h\leftarrow B) with finite
body (B\subseteq L), and each (a\in A) has exactly one contrary
\(\bar a\in L\). Flatness is the repository condition that no assumption is a
rule head (`src/argumentation/structured/aba/aba.py:40-67`). Rule bodies may
contain assumptions. Contraries may be shared and may themselves be
assumptions.

For (E\subseteq A), let (Cl_F(E)) be the least Horn closure obtained by
seeding (E), firing empty-body rules, and repeatedly firing every rule whose
body is derived. This is the repository oracle's closure
(`src/argumentation/structured/aba/_closure.py:19-59`). Define

\[
D_F(E)=\{a\in A\mid \bar a\in Cl_F(E)\}.
\]

Then (E) attacks (B\subseteq A) exactly when
\(D_F(E)\cap B\ne\varnothing\). Because the framework is flat, every subset of
assumptions is closed: assumptions cannot be newly derived by rules.

The direct semantic authorities are the exhaustive definitions in
`src/argumentation/structured/aba/aba.py:97-103,131-176`:

- (E) is stable iff (E\cap D_F(E)=\varnothing) and
  (A\setminus E\subseteq D_F(E)), equivalently
  \(E=A\setminus D_F(E)\).
- (E) is admissible iff it is conflict-free and counterattacks every set of
  assumptions that attacks it.
- (E) is preferred iff it is inclusion-maximal among admissible sets.

No ABA+, preference reversal, non-flat ABA, infinite framework, or non-Horn
deduction is covered.

## The one directed graph

Define the **semantic dependency graph** (G_F=(L,E_R\cup E_C)). Its nodes are
all language literals; assumption nodes are the distinguished subset (A).
There are two kinds of directed edge:

1. **Rule dependency:** for every rule (h\leftarrow B) and every
   (b\in B), add (b\to h). The rule remains a conjunctive hyperedge in the
   residual semantics; the ordinary edges are its dependency shadow and do
   not turn conjunction into disjunction.
2. **Contrary/attack dependency:** for every assumption (a\), add
   \(\bar a\to a\). This direction says that the derived status of the
   contrary must be known when acceptance, rejection, or defense of (a) is
   checked.

An empty-body rule has no incoming dependency edge, but its head is still a
node and the rule fires unconditionally in the head's component. No reverse
rule edges and no undirected incidence edges are added.

Let \({\cal C}\) be the SCCs of (G_F), and let (Q_F) be its condensation
DAG. Process any topological linearization

\[
C_1,\ldots,C_k
\]

of (Q_F). For every rule with head in (C_i), each body literal lies either
in (C_i) or in a strict predecessor: this follows immediately from the
edge (b\to h). For every assumption (a\in C_i), its contrary lies in
(C_i) or a predecessor because of \(\bar a\to a\).

This graph is deliberately stronger than a singleton-attack graph. A rule
\(\bar a\leftarrow b,c\) creates both dependencies (b\to\bar a) and
(c\to\bar a), while the residual retains the joint requirement
\(b\wedge c\). Thus collective attacks are not lost.

## Predecessor boundary and local residual

After processing the downward-closed prefix

\[
P_i=C_1\cup\cdots\cup C_i,
\]

a branch carries the exact boundary state

\[
\sigma_i=(I_i,T_i),
\]

where (I_i\subseteq A\cap P_i) records selected assumptions for lifting and
(T_i\subseteq P_i) records derived literals. The attacked flags are derived,
not independent state:

\[
D_i=\{a\in A\mid \bar a\in T_i\}.
\]

An implementation may project (T_i) to literals used across the remaining
cut and retain only needed attack flags, but that projection is an optimization
obligation, not part of the theorem.

Given predecessor state \(\sigma_{i-1}\) and a local choice
\(X_i\subseteq A\cap C_i\), form the boundary-conditioned residual rule module
\(R_i^{\sigma}\) from every original rule (h\leftarrow B) with
\(h\in C_i\):

- discard the rule if some strict-predecessor body literal is absent from
  (T_{i-1});
- otherwise delete all strict-predecessor body literals and retain the
  same-component body (B\cap C_i);
- preserve an empty remaining body as a fact.

Let (U_i) be the least local Horn closure of (X_i) under
\(R_i^{\sigma}\). Extend the boundary by

\[
I_i=I_{i-1}\cup X_i,\qquad T_i=T_{i-1}\cup U_i.
\]

Contrary edges affect SCC ordering only; they are not deduction rules.

The lift of a complete branch is simply

\[
Lift(X_1,\ldots,X_k)=\bigcup_i X_i.
\]

No auxiliary literal is lifted into the extension.

## Local semantic tests

For each (a\in A), let \({\cal M}(a)) be the finite family of
inclusion-minimal supports of its contrary:

\[
{\cal M}(a)=Min_{\subseteq}\{S\subseteq A\mid \bar a\in Cl_F(S)\}.
\]

At component (C_i), after computing (T_i), use one of these local tests.

### Stable local test

Keep the branch iff, for every (a\in A\cap C_i),

\[
a\in X_i\quad\Longleftrightarrow\quad \bar a\notin T_i.
\tag{ST-i}
\]

The left-to-right direction is conflict-freeness; the right-to-left direction
requires every unselected assumption to be attacked.

### Admissible local test

Keep the branch iff, for every selected (a\in X_i),

\[
\bar a\notin T_i
\quad\text{and}\quad
\forall S\in{\cal M}(a): S\cap D_i\ne\varnothing.
\tag{ADM-i}
\]

The first conjunct is conflict-freeness. The second says that every minimal
attacker of (a) contains an assumption counterattacked by the candidate.
Unselected assumptions impose no admissibility condition.

Let `SCC-ST(F)` be all lifts of complete branches surviving every `(ST-i)`.
Let `SCC-ADM(F)` be all lifts surviving every `(ADM-i)`, and define

\[
SCC\text{-}PR(F)=Max_{\subseteq}(SCC\text{-}ADM(F)).
\]

## Exact composition theorem

For every ordinary finite flat ABA framework (F):

\[
SCC\text{-}ST(F)=Stable(F),
\]

\[
SCC\text{-}ADM(F)=Admissible(F),
\]

and therefore

\[
SCC\text{-}PR(F)=Preferred(F).
\]

Consequently one graph (G_F), one SCC order, one residual construction, and
one lifting operation support both stable and preferred semantics. Only the
local acceptance predicate and preferred's final maximality filter differ.

## Proof

### Lemma 1: closure factorizes over the SCC order

Fix any (E\subseteq A), and set (X_i=E\cap C_i). After component (C_i),
the recursive construction satisfies

\[
T_i=Cl_F(E)\cap P_i.
\]

Proof is by induction over the topological order. A rule headed in (C_i) has
no body literal in a successor component. If a predecessor body is globally
false, discarding the rule is exact. If every predecessor body is globally
true, stripping those bodies leaves exactly the same firing condition on
same-component literals. Taking the least fixpoint inside (C_i) therefore
reproduces precisely the restriction of the global least Horn fixpoint. This
argument permits arbitrary same-component self-loops and cycles. Empty-body
rules are retained as local facts. QED.

### Lemma 2: defense information is available no later than its target

If (S\in{\cal M}(a)) and (b\in S), then there is a rule-dependency path

\[
b\leadsto\bar a.
\]

Otherwise (b) is unused by every finite Horn proof of \(\bar a\) from (S),
so (S\setminus\{b\}) also derives \(\bar a\), contradicting minimality.
Together with \(\bar a\to a\), this places (b) no later than (a). The edge
\(\bar b\to b\) places the truth of \(\bar b\), hence whether the candidate
attacks (b), no later than (b). Thus every bit needed to evaluate
\(S\cap D_F(E)\) is known when (a)'s component is checked. Empty supports
make the statement vacuous and are handled directly. QED.

### Lemma 3: the minimal-support defense test is exact

For any (E\subseteq A), (E) defends (a) iff

\[
\forall S\in{\cal M}(a):S\cap D_F(E)\ne\varnothing.
\]

If a minimal support (S) has empty intersection with (D_F(E)), then (S)
attacks (a) and (E) does not attack (S). Conversely, every attacker
(B\) deriving \(\bar a\) contains a minimal support (S\subseteq B). If each
minimal support meets (D_F(E)), then (B) does too, so (E) counterattacks
every attacker. This includes the oracle's empty-attacker requirement at
`src/argumentation/structured/aba/aba.py:321-328`: if
\(\varnothing\in{\cal M}(a)\), no set can defend (a). QED.

### Stable soundness and completeness

For a surviving complete branch, Lemma 1 makes `(ST-i)` equivalent, over all
assumptions, to (E=A\setminus D_F(E)). Hence its lift is conflict-free and
attacks every outsider: it is stable.

Conversely, for any stable (E), choose (X_i=E\cap C_i). Lemma 1 supplies
the exact closure at every step, and the global stable equivalence makes every
local `(ST-i)` pass. The branch lifts to (E). QED.

### Admissible and preferred soundness and completeness

For a surviving admissible branch, Lemma 1 makes the first part of `(ADM-i)`
global conflict-freeness. Lemmas 2 and 3 make its second part exact defense of
every selected assumption. Flatness supplies closure of the assumption set.
Thus the lift is admissible.

Conversely, every admissible (E) induces the choices (X_i=E\cap C_i), and
the same lemmas make every local test pass. Therefore `SCC-ADM(F)` is exactly
the set of admissible extensions. Taking all and only its inclusion-maximal
members is exactly the direct oracle definition of preferred semantics. The
filter retains every incomparable maximal extension. QED.

## Required edge cases

- **Cross-SCC multi-body rules:** each predecessor body truth is conditioned
  independently, but the residual fires only when all bodies are true. No
  collective attack is split into singleton attacks.
- **Derived contrary chains:** every rule-chain edge is directed toward the
  derived contrary, followed by \(\bar a\to a\); closure factorization and
  attack timing therefore remain exact.
- **Facts and empty attackers:** facts fire in their head component. If a fact
  or fact-derived chain proves \(\bar a\), then
  \(\varnothing\in{\cal M}(a)\); (a) is excluded from every admissible and
  stable extension. Stable may still exclude and attack it.
- **Self-dependency and cycles:** rule and contrary cycles collapse into one
  SCC and are solved by the least local Horn fixpoint plus exhaustive local
  assumption choices. A positive rule cycle without a seed derives nothing.
- **No-stable branches:** any inconsistent local equivalence kills that branch.
  If every branch dies, the result is the empty extension family `()`, not an
  empty extension witness.
- **Incomparable preferred extensions:** all admissible lifts are retained
  until global maximality; distinct incomparable maxima all survive.
- **Shared or assumption-valued contraries:** the literal node is shared, and
  its derived/selected truth feeds every corresponding contrary edge.

## Limit of the theorem and missing stronger obligation

The theorem proves semantic composition, but not useful reduction. It may
enumerate (2^{|A|}) local-choice combinations, store large boundary states,
and enumerate minimal attack supports. A single giant SCC yields no structural
reduction. None of those facts invalidates exactness; all prevent treating this
report as performance evidence.

The unproved stronger claim is:

> selecting only locally inclusion-maximal admissible choices at each SCC,
> under the current predecessor boundary, preserves exactly all global
> preferred extensions.

That claim needs a boundary-equivalence/dominance theorem showing that a locally
dominated choice can never yield a globally incomparable or maximal completion.
The current state records exact predecessor membership and derivability, and
future defense can distinguish those states. Without such a theorem, local
preferred pruning is unsound as an implementation assumption. The exact safe
construction is admissible enumeration followed by global maximality.

## Executable bounded-generated differential contract

The next authorized artifact can be a normally running semantic test, with no
ICCMA data and no solver backend:

```python
# tests/structured/aba/test_aba_scc_composition_contract.py
from hypothesis import given, settings

from argumentation.structured.aba import aba as direct
from argumentation.structured.aba.aba_scc_composition import (
    preferred_extensions as scc_preferred_extensions,
    stable_extensions as scc_stable_extensions,
)
from tests.aba_scc_composition_generators import scc_contract_frameworks


@given(scc_contract_frameworks(
    min_assumptions=0,
    max_assumptions=5,
    max_non_assumption_literals=6,
    max_rules=9,
    max_body_size=3,
))
@settings(max_examples=300, deadline=None)
def test_scc_composition_is_bidirectionally_exact(framework):
    # Set equality is both soundness and completeness, not witness-only validity.
    assert set(scc_stable_extensions(framework)) == set(
        direct.stable_extensions(framework)
    )
    assert set(scc_preferred_extensions(framework)) == set(
        direct.preferred_extensions(framework)
    )
```

The dedicated generator must allow assumptions in rule bodies while prohibiting
assumption heads, shared and assumption-valued contraries, zero assumptions,
zero/empty-body rules, bodies of size two or three spanning predecessor SCCs,
derived contrary chains, self-loops, positive cycles, and arbitrary rule order.
It should use only bounded synthetic literals and the current exhaustive direct
oracles.

Generation alone is not enough to guarantee rare cases. The same test module
must include deterministic fixtures for:

1. a two-predecessor rule \(\bar a\leftarrow b,c\) where neither singleton
   attacks (a);
2. a fact-derived contrary and its empty minimal support;
3. a seeded derived-contrary chain crossing at least three SCCs;
4. an unseeded positive rule cycle;
5. a self-attacking assumption with no stable extension;
6. mutual attack with two incomparable preferred extensions;
7. a framework with no stable extension but at least one preferred extension;
8. shared and assumption-valued contraries.

For every fixture, assert exact family equality for both semantics. Also assert
that at least one generated/fixture framework has more than one SCC and at
least one has a cross-SCC multi-body rule, so a silently degenerate
single-component implementation cannot satisfy the contract by accident.

Passing this contract would establish the executable semantic signal required
by the inventory freeze. It would still authorize no hard-row measurement until
a separate deterministic operational contract requires a bounded branch count
and strict largest-residual reduction on the selected development shapes.
