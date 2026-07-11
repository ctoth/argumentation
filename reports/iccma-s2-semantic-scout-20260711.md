# ICCMA 2023 S2 semantic scout — support-free/core-fact preprocessing

Date: 2026-07-11
Role: read-only semantic scout
Decision: **KILL**

## Executive finding

The earlier S2 premise was wrong in two separate ways.

1. The production ASP path for flat-ABA SE-ST and SE-PR already uses the
   support-free `flat_aba_core_facts` representation. It does not materialize
   `_minimal_supports` or emit `support_*` facts. This is not a dormant
   acceptance-only mechanism waiting to be extended to single-extension tasks.
2. The only generally safe support-free/core-fact *semantic preprocessing* is
   already subsumed by the production grounded ABA reduct: compute the grounded
   set, fix it IN, fix assumptions attacked by it OUT, solve the residual, and
   lift. On both development instances that contain all campaign headroom, that
   reduct removes **zero assumptions and zero rules**.

Therefore there is neither an unimplemented semantic shortcut nor operational
reduction headroom on this target. A source probe would repeat existing behavior.
No holdout instance was read or run, and no solver/benchmark run was performed.

## Evidence boundary

I read `AGENTS.md`, the committed campaign frame and baseline, the prior campaign
history and Round-1 archaeology/probe reports, current implementation and tests,
the ABA incremental spec, and the relevant paper page images. In particular, I
read these images directly rather than extracting PDF text:

- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-008.png`
  (printed p.273): definitions of preferred and stable semantics for flat ABA;
- `.../page-013.png` and `.../page-014.png` (printed pp.278-279): attacked-set
  characterization of defense/admissibility and the grounded fixpoint;
- `.../page-025.png` (printed p.290): the common ASP module computes forward
  derivability from `assumption/head/body/contrary` facts;
- `.../page-026.png` (printed p.291): stable adds the all-OUT-defeated constraint,
  while preferred is subset-maximal admissible (equivalently maximal complete);
- `.../page-027.png` (printed p.292): explicit grounded iteration.

Current checkout: `main` at `56a946eed4845f3190a4e6be9200cc834c1b0e3a`.
The worktree contained extensive unrelated user-owned untracked material. This
report is the only file written.

## The exact safe semantic claims

There are two distinct claims hidden by the phrase “support-free/core-fact.” They
must not be conflated.

### Claim A — materialized minimal supports are unnecessary for the direct ASP encoding

Let `F = (L, R, A, contrary)` be a finite flat ABA framework and let `E` be the
guessed IN assumptions. From only:

- `assumption(a)`;
- `head(r, x)` and `body(r, y)` for every rule;
- `contrary(a, x)`;

the common ASP program computes `supported(x)` exactly when
`x in Th_F(E)`. Consequently it can compute attacks (`defeated`) without a
pre-enumerated relation of minimal supports. Stable adds
`:- out(X), not defeated(X).`; preferred uses admissibility/completeness plus
subset maximization. Omitting `support_concludes/support_member/support_count`
facts is therefore semantics-preserving for these direct ASP programs.

“Support-free” here means **no materialized minimal-support table**. It does not
mean that rule derivations or support semantics may be discarded. All core rule
facts and the forward-closure program remain load-bearing.

This is already the production path:

- `aba_asp.py:146-147` sets `include_supports=False` for both `asp` and `clingo`;
- `aba_asp.py:271,313,315` constructs `AbaIncrementalSolver` and dispatches
  single-extension stable/preferred to it;
- `aba_incremental.py:300` independently defaults to
  `encode_aba_theory(..., include_supports=False)`;
- `test_aba_incremental_paper_properties.py:28-40` checks the paper's core fact
  surface; and
- `test_aba_multishot.py:317-335` makes `_minimal_supports` raise if called and
  proves preferred single-extension still succeeds with
  `encoding == "flat_aba_core_facts"`.

Thus the Round-1 archaeology report's S2 description (“extend” core facts to
SE-ST/SE-PR) and its statement that soundness was unverified are stale/incorrect
against both the cited code and its existing property/differential tests.

### Claim B — support-free and fact-attacked assumptions are a special case of the grounded reduct

Let:

- `Th_F(S)` be the Horn forward closure of assumptions `S`;
- `U = {a in A | contrary(a) not in Th_F(A)}` (assumptions whose contraries have
  no possible support at all);
- `C = Th_F(empty)` (unconditional/core-fact closure); and
- `O0 = {a in A | contrary(a) in C}` (assumptions attacked unconditionally).

For ordinary flat ABA:

- `U` is defended by the empty set, hence `U` enters the first grounded
  iteration and `U subseteq G`, where `G` is the grounded assumption set;
- `O0` is attacked by every set, including `G`, hence
  `O0 subseteq {a | contrary(a) in Th_F(G)}`.

The strongest safe polynomial reduction is therefore the existing one:

```
G = grounded(F)
O = {a in A - G | contrary(a) in Th_F(G)}
R = residual(F, fixed_in=G, fixed_out=O)
```

For `sigma in {preferred, stable}`:

```
Ext_sigma(F) = {G union E | E in Ext_sigma(R)}.
```

The residual construction removes fixed assumptions from the choice space,
deletes fixed-IN antecedents, and drops rules containing fixed-OUT assumption
antecedents. This is safe because every preferred/stable extension contains
`G`, excludes `O`, and is conflict-free. It reduces solver work only when the
residual is strictly smaller.

This too is already production behavior: `aba_preprocessing.py:67-75` gates the
reduct for preferred and stable, `:145-181` computes grounded by Horn closures,
and `:233-283` computes and installs `fixed_in`, `fixed_out`, and the residual.
`aba_asp.py:115-133` invokes it before the ASP solve. The implementation also
correctly no-ops for ABA+ and for ungated semantics.

## Necessary preconditions

Both claims require all of the following.

1. **Finite ordinary flat ABA.** No assumption may be a rule head. The repository
   enforces this at construction (`aba.py:40-68`). Non-flat ABA needs closed-set
   handling that this residual does not supply.
2. **No ABA+ preference/reverse-attack semantics.** Ordinary forward derivability
   is not enough to characterize `<`-attacks. The current simplifier therefore
   no-ops on `ABAPlusFramework`.
3. **Core facts retain the complete proof system.** Every rule head/body,
   assumption, and contrary must remain. Only the *enumerated minimal-support
   relation* may be omitted from the direct ASP representation.
4. **Semantics gate.** The constant grounded offset is safe for complete,
   preferred, stable, grounded, and ideal, but not for admissible enumeration.
   The empty set is always admissible in flat ABA, so forcing `G` into every
   admissible result would lose valid admissible sets.
5. **Exact residual and lift.** Fixed-IN assumptions must remain unconditionally
   available to rule derivations, rules depending on fixed-OUT assumptions may be
   removed only because those assumptions cannot occur, and every returned
   residual extension must be lifted with `G`.
6. **Query projection for acceptance.** For sentence queries, membership in
   `fixed_out` does not by itself imply non-derivability: the sentence may have
   another derivation. DC/DS must be preserved through lifted extension closure,
   not guessed from assumption status alone.

## Stable, preferred, credulous, and skeptical are not interchangeable

- **SE-ST** asks for one stable extension. A finite flat ABA framework may have
  no stable extension. Stable requires a conflict-free set that attacks every
  assumption outside it.
- **SE-PR** asks for one preferred extension. A finite flat ABA framework always
  has at least one preferred extension because the finite family of admissible
  sets is nonempty (it contains the empty set) and therefore has a maximal member.
- Every stable extension is preferred, so an actual stable witness may safely be
  returned for SE-PR. The converse is false, and failure to find any stable
  extension says nothing about preferred existence.
- **Credulous acceptance** is existential over the extension family. Under stable
  semantics it is false when no stable extension exists, even for an assumption
  forced IN conditional on stable existence.
- **Skeptical acceptance** is universal. The repository implements it with
  `all(...)`/counterexample absence, so it is vacuously true when the stable
  extension family is empty (`aba_asp.py:606-620` and
  `test_aba_preprocessing.py:462-470`). Preferred skeptical acceptance is not
  vacuous because preferred extensions exist.
- For arbitrary sentence `q`, preserving the extension sets is insufficient
  unless derivability is also evaluated in the original/lifted framework. The
  current acceptance oracle battery does exactly that.

The campaign already supplies a concrete non-implication counterexample. On
development instance `aba_2000_0.3_10_10_1.aba`, stable single-extension
completed with **no witness**, while preferred single-extension produced a
preferred witness of size **350** after four solver calls
(`experiments/2026-07-11-iccma2023-stable-preferred-triage.md:68-109`). This is
why the stable-first shortcut was correctly killed.

## Counterexamples to broader shortcuts

1. **“If a contrary has any support, force its assumption OUT” is false.** Let
   assumptions be `{a,b}`, with `contrary(a)=ca`, `contrary(b)=cb`, and rules
   `ca <- b`, `cb <- a`. Both contraries have support, yet `{a}` and `{b}` are
   the stable and preferred extensions. Only support from the fixed grounded
   core, not support from an optional assumption set, justifies fixed OUT.
2. **“No direct contrary rule means support-free” is false.** A contrary may be
   reached through an arbitrarily long or conjunctive rule chain. The closure,
   not a direct-head scan, decides support-freedom. The preprocessing battery's
   `a -> p -> contrary(b)` case exists specifically for this boundary.
3. **“Drop rule facts and keep assumptions/contraries only” is false.** In the
   mutual-attack framework above, deleting the two rules erases both attacks and
   changes the extension family. Core-facts encoding includes rule heads/bodies;
   it is not an attack-free abstraction.
4. **“Support-free assumptions are in every admissible set” is false.** With one
   unattacked assumption and no rules, the empty set is admissible, while the
   preferred/stable extension is `{a}`. The reduction is semantics-gated.
5. **“No stable extension means no preferred extension” is false.** A directed
   three-cycle in flat ABA has no stable extension but still has a preferred
   extension (the empty admissible set). The real development row above is a
   larger concrete instance of the same separation.
6. **The ordinary-ABA reduction cannot be copied to ABA+.** Preference reversal
   can change which attacks succeed even though the underlying forward supports
   are unchanged.

## Executable contracts

### Semantic contract

Name: `test_support_free_core_fact_reduct_preserves_stable_preferred_and_acceptance`

For generated finite flat ABA frameworks, compute the candidate residual `R`
and lift `L(E)=G union E`. Assert:

```
{L(E) | E in stable(R)}    == stable(F)
{L(E) | E in preferred(R)} == preferred(F)
```

Then, for queries drawn from assumptions, contraries, intermediate literals,
fact-derived literals, and literals outside the residual, assert credulous and
skeptical answers from lifted extensions equal the unsimplified native oracle.
The battery must include: empty support, unconditional contrary, multi-step
support, conjunctive support, mutual attack, self-attack, directed odd cycle,
and no-stable-extension cases.

This contract substantially already exists:
`test_aba_preprocessing.py:402-453` checks extension-family equality and
`:462-538` checks DC/DS equality for complete/preferred/stable; the multishot
differential battery additionally compares direct core-fact ASP with the native
and support-reference semantics. Any stronger proposed reduction must extend
these tests and fail on the current baseline before implementation.

### Cheap operational contract

Name: `test_support_free_core_fact_preprocessing_shrinks_campaign_target`

Before any solver or benchmark call, parse only the preregistered development
target and require both:

```
encoding == "flat_aba_core_facts"
not any(fact.startswith("support_") for fact in encoding.facts)
```

and a measurable solver-input reduction:

```
residual_assumptions < original_assumptions
or residual_rules < original_rules
or residual_body_literals < original_body_literals
```

Record all original/residual counts. This fails cheaply if the candidate merely
renames an already-active encoding or if preprocessing is a no-op. It is a better
pre-benchmark gate than wall clock because it tests the claimed mechanism
directly.

I exercised the existing read-only `tools/aba_iccma_probe.py --mode
simplify-stable` diagnostic on the two development instances only. Preferred and
stable share the same grounded-reduct gate, so the residual is the same for both:

| development instance | elapsed | fixed IN | fixed OUT | residual assumptions | residual rules |
|---|---:|---:|---:|---:|---:|
| `aba_2000_0.3_10_10_0.aba` | 0.272 s | 0 | 0 | 600 / 600 | 7867 / 7867 |
| `aba_2000_0.3_10_10_1.aba` | 0.269 s | 0 | 0 | 600 / 600 | 7699 / 7699 |

The encoding half already passes in production; the reduction half fails with
exactly zero shrinkage. No solver was invoked by this mode.

## Campaign decision

**KILL S2 as a campaign candidate.** The safe semantic claim is real, but it is
not new: the direct core-facts encoding and the stronger grounded residual are
already implemented, tested, and on the SE-ST/SE-PR production path. On the
three timeout rows' two underlying development frameworks, the reduction is an
exact no-op. The 21/24 campaign metric therefore cannot move through this
candidate without inventing a stronger reduction whose semantic premise is not
established.

Do not spend a source slice or benchmark probe on:

- removing materialized supports from ASP SE-ST/SE-PR (already removed);
- forcing IN every assumption whose contrary merely lacks a direct rule;
- forcing OUT every assumption whose contrary has some optional support;
- using stable nonexistence to answer SE-PR; or
- rebranding the existing grounded reduct as new support-free preprocessing.

A future candidate would need a genuinely stronger, independently proved fixed
core than `G`/`att(G)` and must first make the semantic contract fail on baseline
and the residual-size contract pass on the development target. No such claim is
supported by the current implementation, tests, specs, paper pages, or campaign
history.
