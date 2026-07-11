# H3 semantic scout: SE-PR CEGAR grow-to-maximal churn

Date: 2026-07-11
Role: read-only Round-1 campaign scout
Tracked baseline inspected: `f701c2f19d7d8d6f770b233450c639c2786a7a14` (`main`)
Holdout: not read or run
Source changes / solver runs / commits: none

## Decision

**KILL H3 as “grow-to-maximal churn.”**

The profiled hard development row does not show excessive Python looping,
program addition, or re-grounding. It completes one outer iteration with only
three inner iterations and three refinement constraints. The real-worker
profile attributes 928 samples to `clingo.Control.solve` inside the growth
loop, versus 27 to initial grounding, 19 to program addition, and 3 to
refinement grounding. The observed `4 solver calls / 1 outer / 3 inner / 3
refinements` is a short exact-maximality search whose individual Clingo solves,
not its orchestration count, dominate.

Removing the three refinement-ground operations could at best remove the
profile's three observed refinement-grounding samples. Reducing four API solve
calls to one may still be worth a *different*, preregistered one-shot
maximality/search hypothesis, but the present evidence does not show call or
re-ground churn as the bottleneck. H3 therefore does not survive to a source
experiment under the campaign's performance-contract rule.

The two hard development SE-PR rows are:

- `benchmarks/aba/aba_2000_0.3_10_10_0.aba` — 600 assumptions, 7,867 rules,
  baseline timeout in all three 10 s repeats;
- `benchmarks/aba/aba_2000_0.3_10_10_1.aba` — 600 assumptions, 7,699 rules,
  baseline timeout in all three 10 s repeats; its 15 s diagnostic completed
  with a preferred witness of size 350 and the 4/1/3/3 telemetry above.

## What the current algorithm proves

`aba_com_incremental.lp` represents complete assumption sets as answer sets.
For SE-PR, `find_preferred_extension()` calls
`enumerate_preferred(limit=1)` (`aba_incremental.py:591-635`):

1. One outer solve obtains a complete seed.
2. For current set `I`, `constr(out(I))` is added and grounded. The constraint
   blocks exactly `I` and its subsets, as checked by
   `test_lehtonen_p6_refinement_blocks_candidate_and_subsets`.
3. Assumptions `in(a)=true` for every `a in I` restrict the next solve to
   supersets. With the refinement active, any model is a **strict** complete
   superset.
4. A satisfiable solve advances the chain. An unsatisfiable solve proves that
   no strict complete superset exists, so the returned complete set is
   subset-maximal and therefore preferred.

The final unsatisfiable growth solve is not incidental overhead: it is the
current maximality certificate. On the profiled row the four calls are exactly
one seed call plus three growth calls; three refinements imply two successful
strict growth steps followed by the final no-superset proof.

This semantics is already checked against independent surfaces:

- `test_multishot_enumeration_matches_native_and_support_reference` compares
  preferred enumeration with the powerset-native and support-mask references
  over the fixed battery and seeded random frameworks;
- `test_aba_asp_matches_support_reference_on_generated_frameworks` provides
  generated differential coverage;
- `test_preferred_sets_are_maximal_admissible_sets` states the defining
  admissibility/maximality property;
- `test_preferred_single_extension_uses_limited_multishot_witness` confirms
  that SE-PR asks for only one preferred extension;
- the fixed multishot battery contains cases needing multiple refinements and
  multiple outer iterations, so those steps cannot be erased generally.

## Changes that are semantically possible

These are design classes, not proposed source changes.

1. **One-shot cardinality-optimal complete model.** For SE-PR, any complete set
   of globally maximum cardinality is inclusion-maximal and hence preferred.
   A correctly encoded `#maximize`/MaxSAT objective may therefore return one
   sound SE-PR witness without the external growth chain. This is safe only if
   optimality is proved before returning; a merely high-cardinality or
   heuristic model is not enough. It also changes the hypothesis from
   “remove orchestration churn” to “replace repeated subset-maximal search with
   exact optimization,” and one API call may conceal substantial internal
   search.

2. **One-shot exact maximality encoding.** A saturation, disjunctive, QBF, or
   other encoding can search for a complete set while proving that no strict
   complete superset exists. It is semantically admissible if differential
   tests establish the same preferred witness contract. Its operational cost
   is unknown and cannot be inferred from a smaller public solve-call count.

3. **Ground-once reusable growth activation.** Candidate membership could be
   represented by externals/assumptions in a pre-grounded generic
   strict-superset constraint, provided each activated state is logically
   equivalent to the current `constr(out(I))` plus `in(I)` assumptions. This
   can remove per-step `ctl.add`/`ctl.ground`, but not the final maximality
   solve or necessarily any solver call. Existing profiling gives it a
   negligible ceiling on the hard row.

4. **A sound sufficient preferred certificate.** A stable witness is safe to
   return because stable implies preferred. Other polynomial sufficient
   certificates (admissible plus maximal-conflict-free, for example) are also
   safe when actually satisfied. They must fall through to exact preferred
   search when the certificate is absent. Probe 1 found no stable witness on
   the profiled row, so that particular shortcut is already killed there.

Model-selection heuristics that tend to choose more `in/1` atoms may shorten a
chain, but they do not remove the need for an exact maximality proof. The
Round-1 configuration probe also retained 4/1/3/3 for every successful arm, so
there is no current evidence that generic Clingo configuration changes this
shape.

## Unsafe shortcuts and counterexamples

- **Return the first complete/admissible seed.** In the two-assumption mutual
  attack framework already present in `test_aba_multishot.py`, the empty set is
  complete but is strictly contained in the preferred sets `{a}` and `{b}`.
  A first-seed return can therefore emit a non-preferred witness.
- **Treat stable UNSAT as SE-PR UNSAT.** With one self-attacking assumption
  `d` and rule `d -> contrary(d)`, there is no stable extension, while the
  empty set is admissible and has no admissible strict superset, hence is
  preferred. Stable failure must fall through; it cannot answer SE-PR.
- **Stop after a fixed number of growth steps.** The test battery already has
  a concrete case requiring at least two refinement clauses, and preferred
  growth chains are not globally bounded by a small constant. Stopping before
  the final strict-superset UNSAT result returns an unproved candidate.
- **Use a heuristic or locally large model as if it were optimum.** A model
  with many `in/1` atoms is not preferred merely because no model seen so far
  is larger. Only proved global cardinality optimality or proved absence of a
  strict admissible/complete superset supplies the needed certificate.
- **Strengthen a refinement without an equivalence proof.** The current
  constraint deliberately blocks only the proved candidate and its subsets.
  A broader clause may discard an incomparable preferred extension or the
  strict superset needed to demonstrate that the candidate is not preferred.
- **Count API calls as work.** A single optimize/saturation call can perform
  more internal solving than four incremental calls. `solver_calls == 1` is an
  operational shape signal, not performance proof.

## Required deterministic semantic contract for any replacement

Before any hard-row measurement, add a normally running contract such as
`test_se_pr_single_extension_preserves_preferred_maximality`:

For every framework in the existing fixed multishot battery and a bounded,
deterministically generated flat-ABA corpus (including the mutual-attack,
self-attack/no-stable, multi-refinement, and multiple-outer-iteration cases),
invoke the candidate SE-PR single-extension path and assert:

1. exactly one witness `S` is returned;
2. `S <= framework.assumptions` and `native_aba.admissible(framework, S)`;
3. exhaustive reference checking finds no admissible `T` with `S < T`;
4. equivalently, `S in native_aba.preferred_extensions(framework)`;
5. the result is accepted by the existing independent preferred checker; and
6. the candidate neither equates “no stable witness” with “no preferred
   witness” nor returns an intermediate complete seed.

The contract should compare membership rather than require the same canonical
witness as the current solver: SE-PR permits any preferred extension. If the
candidate is cardinality optimization, add the stronger candidate-specific
assertion that no complete/admissible extension has cardinality greater than
`|S|`; do not weaken preferred membership to cardinality alone.

## Operational survivor gate for the two hard development rows

The gate must run only on the two named development SE-PR instances, with
`backend=asp`, `jobs=1`, and telemetry captured independently for each row.
Witnesses must first pass the semantic contract and independent preferred
checker. Then a purported **churn-reduction** candidate survives only if all of
the following deterministic shape conditions hold on **both** rows:

- it returns a valid preferred witness rather than timing out inside the
  bounded diagnostic solve;
- `outer_iterations <= 1`;
- `solver_calls <= 3`, `inner_iterations <= 2`, and
  `refinement_clauses <= 2`, or an explicitly identified exact one-shot path
  reports zero CEGAR outer/inner/refinement activity;
- the aggregate counts over the two rows are strictly lower than an unmodified
  paired control captured by the same diagnostic; and
- if the claimed mechanism is re-ground elimination, telemetry separately
  demonstrates zero refinement-ground operations rather than inferring that
  from elapsed time.

These thresholds make the contract fail on the known 4/1/3/3 row before a
full benchmark. The second row currently has no completed loop-count baseline
in the campaign record, so its counts must be paired, not invented. A timeout
or missing telemetry is a gate failure, not zero work.

Only after that gate passes would the campaign's existing wall/metric gate be
relevant: same frozen 24-row development population, 10 s per row, and at
least one of these two baseline SE-PR timeouts flipping to independently valid
`solved`. A lower call count without that paired solved-row gain is not a
campaign survivor.

## Telemetry adjudication

The 4/1/3/3 record establishes that preferred growth is entered and that two
strict supersets are found before maximality is proved. It does **not**
establish pathological churn:

- one outer iteration is the minimum nonempty preferred search shape;
- three inner calls are a short chain, with the last call required to prove
  maximality;
- three refinement constraints each have the exact subset-blocking semantics;
- refinement grounding accounts for only 3 profile samples;
- the dominant 928 samples are inside the individual Clingo solve operation.

Therefore the telemetry kills the stated mechanism. The next candidate, if
Round 1 continues, must target the search performed *inside* those solves and
preregister a concrete exact-maximality encoding plus the semantic and
two-row operational contracts above. It must not be described as a
re-grounding/churn fix unless new paired evidence first contradicts this
profile.
