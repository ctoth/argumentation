# Wave C2a — ABA well-founded preprocessing + Z3 preferred-growth reuse

Date: 2026-05-12. Branch `experiment/graph-speedup-wave-a-preprocessing`.
Commit: **`e54facfa878c5c45c13440a131b54c9b11c99b3a`**.

Implements §1 (well-founded ABA preprocessing) and §2.3a (the contained Z3
preferred-growth incremental fix) of `reports/aba-incremental-spec.md`. **§2.3b
(clingo multi-shot) is deliberately not done — separate wave (C2b).**

## §1 — `simplify_aba`

New module `src/argumentation/aba_preprocessing.py`. (New module, not an
extension of `aba.py`/`preprocessing.py`: keeps the ABA layer self-contained and
keeps `aba.py`'s brute-force functions untouched as the differential oracle.)

Public API, mirroring Wave A's `simplify_af`/`AfSimplification`:

* `simplify_aba(framework, *, semantics=None) -> AbaSimplification`
  * `AbaSimplification.original` / `.residual` — the flat ABA framework that was
    simplified and the (smaller) one to actually solve.
  * `AbaSimplification.fixed_in` — the grounded/well-founded assumption set
    (`G_ABA`); forced IN in every extension of the gated semantics; *not*
    assumptions of `residual`.
  * `AbaSimplification.fixed_out` — `{a : contrary(a) ∈ Th(G_ABA)}` (the ABA
    analog of `G⁺`); forced OUT; *not* assumptions of `residual`.
  * `AbaSimplification.lift(residual_extension)` — `frozenset(residual_extension) | fixed_in`.
  * `AbaSimplification.lift_all(...)` — de-duplicated, order-stable.
  * `AbaSimplification.is_trivial` — `True` iff `fixed_in == fixed_out == ∅`.
* `GROUNDED_REDUCT_ABA_SEMANTICS = {grounded, complete, preferred, stable, ideal}`.
* `grounded_assumption_set_via_supports(framework)` — the polynomial support-mask
  grounded fixpoint (see UNRESOLVED-C below).

**Residual form (UNRESOLVED-B):** the conservative form the spec recommends, made
slightly more concrete than "pin the search space". The residual is a flat
`ABAFramework` over the surviving assumptions only, with the rules rewritten just
enough to keep the lift identity exact: every `fixed_in` assumption is
unconditionally derivable, so its occurrences as a rule antecedent are deleted;
any rule whose antecedents mention a `fixed_out` assumption can never fire in a
conflict-free superset of `fixed_in` (the assumption is OUT in every gated
extension), so the rule is dropped. The residual language is the literals actually
appearing in the rewritten rules plus the surviving assumptions and their
contraries. No further proof-system rewriting. (This is equivalent to keeping the
original rules and pinning `fixed_in` IN / `fixed_out` OUT at the solver, but it
also shrinks the framework, which lets the existing solver functions run on it
unchanged with no plumbing for a `forbid_assumptions` knob.)

**Gate (§1.4):** exactly `{grounded, complete, preferred, stable, ideal}`.
`admissible` is excluded (∅ is admissible). `ABAPlusFramework` ⇒ no-op (reverse
attacks via preferences break the `fixed_out` characterisation — UNRESOLVED-E).
A semantics outside the set ⇒ no-op. Also a cheap `O(|rules|)` bail-out: if every
assumption's contrary is forward-derivable from the *full* assumption set then no
assumption is initially unattacked ⇒ the grounded set is empty ⇒ the
simplification is trivial; this avoids building the support-mask machinery on the
common "everything attacks something" case (the no-help control below).

### UNRESOLVED items — how each was settled

* **UNRESOLVED-A (ideal ⊇ grounded; residual lift for ideal).** Settled in favour
  of including `ideal` in the gate. `simplify_aba(F, semantics="ideal").residual`'s
  ideal extension lifted back equals `aba.ideal_extension(F)` on the hand battery
  and 120 random instances (`test_oracle_equivalence_enumeration_battery/random`).
* **UNRESOLVED-B (residual rule construction).** Conservative rule-rewriting form
  above (strip `fixed_in` antecedents, drop `fixed_out`-using rules). Oracle-validated.
* **UNRESOLVED-C (`def_operator` is exponential).** Implemented
  `grounded_assumption_set_via_supports`: builds the `_SupportState`/`_minimal_supports`
  machinery once, then iterates the `def` operator over integer attack-support
  masks — each outer round computes `attacked_by(S)` once and tests each
  candidate's attack-support masks against it, so the loop is `O(rounds · n · s)`
  rather than `O(rounds · n³ · s²)` (the naive `state.defends`-per-assumption
  version was visibly the bottleneck in the first benchmark). Verified equal to
  `aba.grounded_extension` on the battery and 200 random instances. `aba.grounded_extension`
  and `aba.def_operator` are left untouched as the oracle.
* **UNRESOLVED-D (sentence vs assumption query lift).** Implemented in
  `aba_sat._simplified_support_acceptance` / `sat_stable_acceptance`: an
  assumption query in `fixed_in` ⇒ accepted (credulous iff an extension exists —
  always true for complete/preferred; for stable, vacuously skeptically true);
  in `fixed_out` ⇒ rejected credulously, and for skeptical a stable/preferred
  extension (if any) is a counterexample (vacuously skeptically true if none); a
  query (sentence or survivor assumption) not in `residual.language` is treated as
  not-derivable; otherwise the residual bakes in `fixed_in`'s closure (and drops
  `fixed_out`-using rules), so `derives(F, lift(E), q) ⇔ derives(residual, E, q)`
  and the residual acceptance decision lifts directly. Oracle-validated against
  the brute-force reference and the `simplify=False` path for `q` ranging over all
  assumptions, all contraries, and all language sentences, complete/preferred/stable,
  DC and DS.
* **UNRESOLVED-E (ABA+).** Not applied — `ABAPlusFramework` ⇒ no-op. Test
  `test_aba_plus_is_no_op`.
* **UNRESOLVED-F** is a §2.3b concern (clingo `.lp` Listing 1 diff) — not in this wave.

### Wiring

`simplify=True` by default, `simplify=False` opt-out, transparent (callers get
identical results — the hard correctness directive, validated by the oracle tests):

* `aba_sat.sat_support_extension(framework, semantics, *, simplify=True)` — when
  no internal `require_*` args are set, simplifies and recurses on the residual
  with `simplify=False`, lifting the witness.
* `aba_sat.sat_support_acceptance(..., simplify=True)` — delegates to
  `_simplified_support_acceptance` (the lift rules above).
* `aba_sat.sat_stable_extension(framework, *, simplify=True)` — same shape.
* `aba_sat.sat_stable_acceptance(framework, *, task, query, simplify=True)` — new
  function (the old `solver.py` stable-acceptance path called `sat_stable_extension`
  with `require_*`, which can't carry the simplification); `solver.py`'s
  `_solve_sat_stable_aba_acceptance` now calls it.
* `aba_asp.solve_aba_with_backend(..., simplify=True)` — for gated semantics on a
  flat framework, solves the residual with `task="enum"` and lifts every extension
  back before the post-filter / task projection (`_solve_simplified`).
* `solver.py`'s `auto` backend already routes ABA complete/preferred/stable to the
  Z3/clingo `sat` path, which is exactly the functions above — so the routing picks
  up the preprocessing without any change to `_auto_aba_backend`.

Per the hard stops: the Dung AF is **not** materialised, ABA is **not** routed
through the AF SCC layer, `admissible`/ABA+ are **not** gated, and
`preprocessing.py`/`scc_recursive.py` were only read, not touched.

## §2.3a — reuse the Z3 closure encoding across the preferred growth loop

`aba_sat._sat_admissible_cegar_extension` is refactored into a reusable
`_AdmissibleCegarSolver` class: the query-independent encoding (the ranked-closure
constraints from `_add_ranked_closure_constraints` + the per-assumption
conflict-freeness implications) is built **once** in `__init__`. `solve(*,
require_assumptions, require_any_assumption)` pushes the transient hypotheses,
runs the abstraction-refinement loop, and pops. The defense-counterexample
refinement clauses found during a call are globally valid (true of every
admissible set regardless of the transient hypotheses), so they are queued and
re-asserted at base level on the next `solve` call — they accumulate forever,
which is the incremental-CEGAR contract. `_sat_preferred_cegar_extension` now
builds one `_AdmissibleCegarSolver` per query and calls `.solve(...)` for the
seed and for each grow-step instead of constructing a fresh solver (and a fresh
`O(|literals| + |rules|)` ranked-closure encoding) every grow-step.
`_sat_admissible_cegar_extension` is kept as a thin one-shot wrapper. **No change
to what the algorithm computes** — verified against `aba.preferred_extensions` and
against a re-implementation of the old rebuild-every-step loop
(`test_preferred_cegar_matches_admissible_growth`).

Note: in the current `aba_sat.py`, `_sat_preferred_cegar_extension` is reached
only via the `require_assumptions`-only branch of `sat_support_extension` and via
tests — the no-`require_*` preferred path uses `AssumptionKernel.preferred_extension`
(clingo `#maximize`). The refactor is still the correct shape per the spec and is
exercised by the new tests; it becomes load-bearing if a future change routes more
of the preferred path through the Z3 CEGAR loop.

## Test results

* **New `tests/test_aba_preprocessing.py` — 129 tests, all pass** (~2 min; the
  random-instance tests use the brute-force `aba.py` oracle). Covers:
  * `simplify_aba` structural invariants on a 10-framework hand battery (trivial /
    full-collapse, empty grounded, non-trivial well-founded set, self-attacking
    assumption, 2-step derivable contrary, layered, flat attack-chain, conjunctive
    rule body, irrelevant sentences) + the `grounded_assumption_set_via_supports`
    ⇔ `aba.grounded_extension` identity on 200 random instances; ABA+ no-op;
    ungated-semantics no-op; the `GROUNDED_REDUCT_ABA_SEMANTICS` constant.
  * Oracle equivalence — for `{grounded, complete, preferred, stable, ideal}`,
    `lift_all(solve(residual)) == aba.{semantics}_extensions(F) == unsimplified-solver(F)`
    on the battery + 120 random instances; for `{complete, preferred}` (Z3) and
    `stable` (clingo), DC and DS acceptance with `simplify` on/off vs the
    brute-force reference, `q` over all assumptions / contraries / sentences, on
    the battery + 60 random instances; `solve_aba_with_backend(..., backend="support_reference")`
    enumeration and acceptance with `simplify` on/off vs the native oracle.
  * Single-extension finders (`sat_support_extension`, `sat_stable_extension`)
    return a valid extension of the right semantics on the battery + 120 random.
  * §2.3a — `_sat_preferred_cegar_extension` returns a genuine preferred set and
    `_AdmissibleCegarSolver(F).solve()` agrees with `_sat_admissible_cegar_extension(F)`
    on 80 random instances.
* **A `simplify=False` regression** is included for every acceptance/enumeration
  oracle test (the `simplify=False` arm is asserted alongside the `simplify=True`
  arm). No existing ABA telemetry test changed behaviour, so no `simplify=False`
  surgery was needed on the existing suite.
* **Full suite** (`python -m pytest tests/ --ignore=tests/test_datalog_grounding.py`,
  z3-solver + clingo installed): **`1 failed, 1620 passed, 2 skipped`**. The one
  failure is the documented pre-existing `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible`
  (a latent `find_ideal_extension` bug unrelated to ABA). Baseline before this
  change was `1 failed, 1491 passed, 2 skipped` with the same exclusion — i.e. no
  regression, +129 new tests.
* **Lint:** `ruff check` clean on every file touched (`aba_preprocessing.py`,
  `aba_sat.py`, `aba_asp.py`, `solver.py`, `tests/test_aba_preprocessing.py`).
  This change also fixed a pre-existing `pyright`-reported undefined name (`Rule`
  in `aba_sat._rules_by_consequent`) by adding it to that module's import.

### pyright output for touched files

```
$ pyright src/argumentation/aba_preprocessing.py src/argumentation/aba_sat.py \
          src/argumentation/aba_asp.py src/argumentation/solver.py \
          tests/test_aba_preprocessing.py
0 errors, 0 warnings, 0 informations
```

## Before/after benchmark

No ICCMA cap-100 corpus in-repo (recon: `bench/` is README + `asp_vs_sat.py` +
`instance_gen.py` only). Ad-hoc generators were used: (a) a deterministic
unattacked-derivation chain that fully collapses under the grounded reduct,
attached to a hard mutual-attack cycle component — the "chain into a hard core"
shape; (b) a no-help control (a single big mutual-attack cycle ⇒ empty grounded ⇒
`is_trivial`); (c) for §2.3a, `k` independent unattacked assumptions each carrying
a long derivation chain (so the ranked-closure encoding is big and the preferred
set is reached by `k` grow-steps). Wall-clock per task, min of 3–5 runs after
warm-up.

> **SUPERSEDED (Wave C2b, 2026-05-12):** the `preferred`/`stable` rows below
> measure the *pre-C2b* routing — when `backend="asp"` preferred/stable went
> through `AssumptionKernel`. C2b rerouted `backend ∈ {asp, clingo}` ×
> `{complete, stable, preferred, grounded}` through the multi-shot
> `AbaIncrementalSolver`; for the current routing's numbers see
> `reports/graph-speedup-wave-c2b-aba-multishot.md`. The `complete` rows and the
> regression *discussion* still apply to the `auto`/SAT path (`solve.py` →
> `sat_support_extension` / `sat_stable_extension`), which still routes preferred
> through `AssumptionKernel.preferred_extension` after `simplify_aba`.

### §1 — `simplify_aba` on the collapsing chain (Z3 `complete`; clingo `preferred`/`stable`)

| task | instance | residual | preproc | simplify=False (ms) | simplify=True (ms) | speedup |
|---|---|---:|---:|---:|---:|---:|
| complete | chain40 + hard-cyc10 | 10 | 4.4 | 107.6 | 93.7 | 1.15× |
| complete | chain120 + hard-cyc10 | 10 | 9.6 | 145.0 | 98.9 | 1.47× |
| complete | chain250 + hard-cyc12 | 12 | 24.5 | 270.4 | 176.7 | 1.53× |
| preferred *(SUPERSEDED — see C2b)* | chain120 + hard-cyc10 | 10 | 9.6 | 7.8 | 12.4 | 0.63× |
| stable *(SUPERSEDED — see C2b)* | chain120 + hard-cyc10 | 10 | 9.6 | 7.9 | 12.5 | 0.63× |
| preferred *(SUPERSEDED — see C2b)* | chain250 + hard-cyc12 | 12 | 24.5 | 15.0 | 28.7 | 0.52× |

**Honest reading:** `complete` (the Z3 path that itself recomputes `_minimal_supports`
and then solves a hard SAT instance over *all* assumptions) is a clean win — the
preprocessing collapses the 40–250-assumption chain to a ≤12-assumption residual.
`preferred`/`stable` go through `AssumptionKernel` (clingo `#maximize` / direct
ASP), which does **not** compute `_minimal_supports` and which solves these
deterministic-chain instances in single-digit ms; the preprocessing's cost (mostly
`_minimal_supports` for the grounded fixpoint) then exceeds the solve it replaces,
so it's a small *absolute* loss (~5–15 ms) on instances that were already fast. It
becomes a win for `preferred`/`stable` only when the clingo solve dominates that
fixed cost (a hard non-collapsing core much larger than these k≤12 cycles). The
gate keeps it transparent and correct in all cases; a caller that knows it's
solving easy clingo instances can pass `simplify=False`.

### §1 — no-help control (empty grounded ⇒ trivial)

| task | instance | trivial? | simplify=False (ms) | simplify=True (ms) | speedup |
|---|---|---|---:|---:|---:|
| complete | nohelp-cyc14 | yes | 13.6 | 13.8 | 0.99× |
| preferred | nohelp-cyc14 | yes | 1.29 | 1.45 | 0.89× |
| stable | nohelp-cyc14 | yes | 1.30 | 1.46 | 0.89× |

≈1.0× — the cheap `O(|rules|)` bail-out (two `closure` passes) detects the trivial
case before building the support-mask machinery; the residual short-circuit then
returns the original framework. The ~0.15 ms overhead only shows against
sub-2-ms clingo solves.

### §2.3a — preferred CEGAR growth loop (Z3)

| instance | rebuild-every-step (ms) | reuse-one-solver (ms) | speedup |
|---|---:|---:|---:|
| k=6, chain=8 | 192.7 | 39.4 | 4.9× |
| k=10, chain=12 | 670.0 | 134.0 | 5.0× |
| k=14, chain=15 | 1522.5 | 259.8 | 5.9× |
| k=20, chain=20 | 4097.0 | 692.9 | 5.9× |

≈5–6× — removes the `×(#assumptions in the final preferred set)` rebuild factor
from the ranked-closure encoding, exactly as the spec predicts. Identical results
(asserted in the benchmark and in `test_preferred_cegar_matches_admissible_growth`).

## What Wave C2b (clingo multi-shot, §2.3b) needs to know

* `aba_preprocessing.simplify_aba(F, semantics=...).residual` is a plain flat
  `ABAFramework`, so the multi-shot solver should run *on the residual* and lift
  with `simplification.lift` / `lift_all` — the two layers compose, same as
  Wave A's AF reduct + SCC recursion. `simplify_aba` is already wired into
  `solve_aba_with_backend` (the dispatcher Wave C2b will extend), so the multi-shot
  backend will see the residual automatically when added there with `simplify=True`.
* The `auto` backend (`solver.py:_auto_aba_backend`) routes ABA complete/preferred/stable
  to `"sat"` today; C2b's multi-shot clingo path will need its own backend name and
  routing, and should accept the same `simplify` knob.
* UNRESOLVED-F still stands: diff `encodings/aba_complete.lp` against L21-TPLP
  Listing 1 before deciding whether a new `encodings/aba_com_incremental.lp` is
  needed. Do not edit the existing enumeration `.lp` files (the subprocess path is
  the oracle).
* The `_AdmissibleCegarSolver` push/pop pattern (transient hypotheses in a pushed
  frame, monotone refinement clauses re-asserted at base level) is the same shape
  the clingo multi-shot loop should use: `Π = ABA(F) ∪ com` grounded once,
  `solve(assumptions=[...])` for the transient `in(I)`/`supported(s)` checks, a
  re-grounded `#program refine` part for the permanent `constr(out(I))` accumulation.
* For `preferred`-2ᴾ queries the refinement clauses are query-specific (they encode
  "dominated w.r.t. *this* s"), so cross-query reuse of the `ctl` is unsafe there —
  keep one persistent `ctl` for the NP queries (complete/stable/admissible DC/DS/SE)
  and spin a fresh one per preferred-2ᴾ query, as the spec §2.4 notes.
