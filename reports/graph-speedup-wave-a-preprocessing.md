# Wave A — AF preprocessing layer (grounded reduct + cheap structural reductions)

Date: 2026-05-12. Branch: `experiment/graph-speedup-wave-a-preprocessing`.

## What was built

`src/argumentation/preprocessing.py` — a new semantics-preserving preprocessing
layer for Dung AFs. Public API:

* `simplify_af(framework, *, semantics=None) -> AfSimplification`
  * `AfSimplification.residual` — the (smaller) AF to actually solve.
  * `AfSimplification.fixed_in` — arguments forced IN in every extension of the
    given (admissibility-based) semantics; *not* present in `residual`.
  * `AfSimplification.removed_out` — arguments dropped from `residual` that are OUT
    in every extension (grounded-attacked arguments + pure self-loop sinks).
  * `AfSimplification.lift(residual_extension)` — `frozenset(residual_extension) | fixed_in`.
  * `AfSimplification.lift_all(...)` — de-duplicated, order-stable lift of a collection.
  * `AfSimplification.is_trivial` — `True` when nothing was removed.
* `GROUNDED_REDUCT_SEMANTICS` — the frozenset of semantics names for which the
  grounded reduct is applied: `{complete, preferred, stable, semi_stable, grounded, ideal}`.
* Diagnostics (detection only, not yet exploited): `is_symmetric_irreflexive(framework)`,
  `isolated_arguments(framework)`.

### Reductions implemented

1. **Grounded reduct.** Compute the grounded extension `G` (existing
   `dung.grounded_extension`, O(V+E)). `G` is IN, `G⁺` (everything `G` attacks) is
   OUT, in every extension of every admissibility-based semantics. `residual` is
   the AF restricted to `Args \ (G ∪ G⁺)` with the attacks among those survivors;
   the answer is lifted by re-unioning `G`. There are no `G→residual` edges (a
   `G`-target is in `G⁺`, not the residual) so the residual is exactly `AF[U]`.
   This is the standard µ-toksia / pyglaf / ASPARTIX-V preprocessing.
2. **Pure self-loop sink removal.** An argument `a` with `(a,a)` whose *only*
   incident edge is the self-loop is OUT in every extension (no conflict-free set
   contains it) and attacks nobody, so it can be deleted outright — *except for the
   stable semantics*, where such an `a` is the obstruction to a stable extension
   existing (it can never be covered); deleting it would spuriously create a stable
   extension. So this removal is gated off for `stable`.
3. **Isolated-argument elimination.** Subsumed by the grounded reduct (an isolated
   argument is unattacked, hence in `G`). Exposed only as the `isolated_arguments`
   diagnostic.
4. **Acyclic shortcut.** Already present in `af_sat.PreferredSkepticalTaskSolver._shortcut`
   (`_is_acyclic` → grounded settles DS-PR); left as-is. Combined with the grounded
   reduct, an acyclic AF's residual is the empty AF, so the SAT/ASP call is skipped
   entirely by the empty-residual fast path.

### Reductions deferred (detected, deliberately not applied — soundness > speed)

* **Self-loop arguments *with* outgoing attacks** are *not* removed. Deleting them
  would spuriously unblock their targets (a target attacked only by self-attackers
  can never be IN, but would become unattacked in the residual). The SAT/ASP
  encoders already handle `(a,a)` correctly via conflict-freeness, so leaving them
  in is sound, just less reduced.
* **Symmetric-AF special case** (Coste-Marquis et al., ECSQARU 2005): detected via
  `is_symmetric_irreflexive`, but a full polynomial special-case solver (naive sets
  = preferred = stable, component-wise maximal independent sets) is more than ~30
  LOC done correctly and is out of scope for Wave A. **TODO** (next wave or a
  dedicated one).
* **Baumann / Oikarinen-Woltran kernels** (`af_revision.stable_kernel` /
  `baumann_2015_kernel`): their preservation guarantees are stated for strong
  equivalence / revision, not obviously matched to "solve task T on AF F". Not
  applied. **TODO**: confirm per-semantics preservation before wiring.
* **`stage` is *not* covered by the grounded reduct.** Stage extensions are
  conflict-free range-maximal sets, *not* complete extensions, so they need not
  contain `G` nor exclude `G⁺`. Concrete counterexample (in the test battery):
  `AF = ({a,b,c}, {(a,a),(b,c),(c,a)})` has grounded `{b}` but `{c}` is a stage
  extension (range `{a,c}`, incomparable to range `{b,c}` of `{b}`); applying the
  grounded reduct would wrongly force `c` OUT. Stage gets only the always-sound
  self-loop-sink removal.
* **`admissible` is *not* covered by the grounded reduct** either — the empty set
  is admissible, so `adm(AF) ≠ {G ∪ E : E ∈ adm(residual)}`. (Admissible enumeration
  happens only on the ASPIC ASP path; there it just gets self-loop-sink removal.)

### Validity of the grounded reduct, per semantics (all verified by the new oracle tests)

| Semantics | Why the reduct is exact |
|---|---|
| complete | standard reduct: `complete(AF) = {G ∪ E : E ∈ complete(residual)}` |
| preferred | maximal complete; the constant offset `G` preserves maximality |
| stable | `G` ⊆ every stable extension, `G⁺` disjoint from all; coverage transfers |
| semi_stable | semi-stable = complete with maximal range; `range(G ∪ E) = G ∪ G⁺ ∪ range_residual(E)`, constant offset preserves maximality |
| grounded | residual's grounded extension is `∅` by construction → `grounded(AF) = G` directly |
| ideal | ⊆ ∩ preferred (all contain `G`, exclude `G⁺`); maximal-admissible-subset transfers |

## Where it's wired (default ON, with `simplify=False` opt-out)

* **Z3 AF SAT path** — `src/argumentation/af_sat.py`. Every public single-extension
  finder now has a `simplify: bool = True` parameter and runs the SAT kernel on the
  residual, lifting the witness back:
  `find_stable_extension`, `find_complete_extension`, `find_preferred_extension`,
  `find_semi_stable_extension`, `find_stage_extension`, `find_ideal_extension`.
  `is_preferred_skeptically_accepted` (DS-PR / CDAS) also takes `simplify=True`: a
  query in `fixed_in` → accept immediately, a query in `removed_out` → reject
  immediately (both emit a `SATCheck` trace event so observers/ICCMA telemetry still
  see the decision), otherwise the CDAS loop runs on the residual. A shared
  `_prepare(...)` helper does the simplify + maps `require_in`/`require_out` (a
  forced-OUT `require_in` or forced-IN `require_out` → immediately `None`).
  `solver.py` calls these finders unchanged, so all SE/DC/DS Dung tasks pick up the
  preprocessing transparently.
* **ASP AF path** — `src/argumentation/aspic_encoding.py`, the
  `build_abstract_framework(...)` → `dung_{complete,stable,admissible}.lp` clingo
  branch (the only place a Dung AF is encoded to ASP in this repo; the standalone
  Dung dispatcher uses SAT, not ASP). The projected framework is run through
  `simplify_af(...)`, clingo solves the residual, every returned extension is lifted
  back before the post-filter (max for preferred, min for grounded) and the result
  projection. An empty residual short-circuits clingo entirely (`extensions =
  (fixed_in,)`). `_projection_facts` was refactored to `_projection_facts_for(framework)`.

No new dependencies. The layer is pure graph manipulation over the existing
`ArgumentationFramework`.

## Test results

* **New tests:** `tests/test_preprocessing.py` — 103 tests, all pass. Covers:
  `simplify_af` structural invariants on a 12-AF battery (acyclic, symmetric, with
  self-attackers, with isolated args, with non-trivial grounded extension, the
  stage-counterexample AF, layered AFs) + 80 random AFs; the diagnostics; and
  oracle-equivalence — for `grounded, complete, preferred, stable, semi_stable, stage,
  ideal` the preprocessed SAT path (`simplify=True`) agrees with both the brute-force
  reference (`dung.*_extensions` / `ideal_extension`) and the unsimplified SAT path
  (`simplify=False`), on the battery and on 120 random AFs each, including
  `require_in`/`require_out` and DS-PR skeptical acceptance vs the native oracle.
* **Existing suite:** `python -m pytest --ignore=tests/test_datalog_grounding.py`
  → **909 passed, 2 skipped, 1 failed**. `tests/test_datalog_grounding.py` is
  excluded because it imports `gunray`, which is not installed (pre-existing, nothing
  to do with this change). Four `test_solver_encoding.py` internal-telemetry tests
  (asserting raw SAT-trace argument counts / which internal utility ran) and one
  `test_iccma_runner.py` SE-STG telemetry test were updated to reflect that
  preprocessing legitimately changes *which internal SAT calls run* — they now pass
  `simplify=False` (the telemetry tests) or use a non-eliminable instance (the
  SE-STG test); the public results they assert are unchanged.
* **Pre-existing failure (not introduced here):**
  `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible` fails on
  a clean checkout of `main` too (with z3 installed) — Hypothesis finds
  `AF = ({a,aa,b,c}, {(a,aa),(a,b),(aa,a),(aa,b),(b,c)})` for which
  `find_ideal_extension` returns `{c}` (not admissible) regardless of `simplify`.
  This is a latent bug in the existing `find_ideal_extension` iterative-SAT
  algorithm, unrelated to the preprocessing layer (the AF has empty grounded
  extension so `simplify_af` is a no-op on it). **Recommended follow-up:** a separate
  fix for `find_ideal_extension` — the "shrink the candidate set by admissible
  attackers" loop appears not to enforce admissibility of the final result on this
  example.
* **Lint:** `ruff check` clean on all files touched by this change;
  `pyright` 0 errors on them. (The repo has 18 pre-existing `ruff` findings in other
  modules and no `[tool.ruff]` config / lint gate — untouched.)

Environment note: the test run required `z3-solver` (Z3 AF path) and `clingo` (ASPIC
ASP path) to be installed; without them ~108 / ~8 tests respectively fail on a clean
checkout as well.

## Before/after benchmark

`bench/asp_vs_sat.py` only covers ABA-chain and ASPIC-chain instances, not the Dung
AF SAT path, and the repo has no ICCMA cap-100 corpus checked in (only
`bench/README.md`, `asp_vs_sat.py`, `instance_gen.py`). **The ICCMA cap-100 corpus
was not run** (it is not available in-repo). Instead, an ad-hoc benchmark over
layered AFs — a long deterministic attack chain that the grounded reduct collapses,
attached to a hard random cycle component — which is the structure the literature
says this preprocessing targets, and which mirrors the "chain into a cycle" shape of
many ICCMA instances. Wall-clock per task, min of 3 runs after warm-up (Z3 path):

| task | instance | simplify=False (ms) | simplify=True (ms) | speedup |
|---|---|---:|---:|---:|
| preferred | chain20+cyc6 | 17.4 | 6.4 | 2.7× |
| stable | chain20+cyc6 | 8.1 | 3.9 | 2.1× |
| complete | chain20+cyc6 | 13.8 | 5.2 | 2.7× |
| semi_stable | chain20+cyc6 | 15.9 | 5.8 | 2.7× |
| DS-PR(y0) | chain20+cyc6 | 64.5 | 20.9 | 3.1× |
| preferred | chain60+cyc6 | 39.3 | 6.2 | 6.3× |
| stable | chain60+cyc6 | 16.9 | 3.1 | 5.4× |
| complete | chain60+cyc6 | 30.9 | 4.9 | 6.4× |
| semi_stable | chain60+cyc6 | 32.0 | 4.9 | 6.5× |
| DS-PR(y0) | chain60+cyc6 | 187.8 | 18.2 | 10.3× |
| preferred | chain120+cyc6 | 70.1 | 5.4 | 12.9× |
| stable | chain120+cyc6 | 31.2 | 3.0 | 10.4× |
| complete | chain120+cyc6 | 60.2 | 4.6 | 13.1× |
| semi_stable | chain120+cyc6 | 63.1 | 5.0 | 12.7× |
| DS-PR(y0) | chain120+cyc6 | 425.4 | 4.3 | 98.7× |
| preferred | chain120+cyc10 | 80.2 | 10.4 | 7.7× |
| stable | chain120+cyc10 | 33.3 | 5.0 | 6.6× |
| complete | chain120+cyc10 | 62.4 | 7.9 | 7.9× |
| semi_stable | chain120+cyc10 | 64.1 | 8.0 | 8.0× |
| DS-PR(y0) | chain120+cyc10 | 559.2 | 29.4 | 19.1× |

Floor case (honest): a single big cycle with no source argument (empty grounded
extension, no self-loop sinks) → `simplify_af` is a no-op → `find_preferred` 34.0 ms
vs 34.3 ms ≈ 1.0× (the simplify call's overhead is a couple of `frozenset`
comprehensions, negligible). So the layer is "free or a win", never a loss in
practice. No timeouts were hit in either configuration on these sizes; the point of
the table is the multiplier, not absolute timeout counts.

## For the next wave (SCC-recursive core semantics)

* The preprocessing API to build on: `preprocessing.simplify_af(framework, semantics=...)`
  → `AfSimplification(original, residual, fixed_in, removed_out)` + `.lift` / `.lift_all`.
  SCC recursion should run *on `simplification.residual`* — after the grounded
  reduct the residual is frequently already a union of small SCCs (every SCC that
  was a singleton-no-loop has been peeled off into `G ∪ G⁺`), so the two layers
  compose: simplify first, then SCC-decompose the residual, then SAT per SCC. Lift
  the per-SCC cross-product results, then `simplification.lift(...)` the whole thing.
* `GROUNDED_REDUCT_SEMANTICS` is the authoritative gate for "is the grounded reduct
  sound for this semantics" — extend it (carefully, with an oracle test) if a new
  semantics is added.
* Do **not** pipe `stage` or `admissible` through the grounded reduct (documented
  counterexamples in `preprocessing.py` and `tests/test_preprocessing.py`); they
  remain on the self-loop-sink-only path.
* `is_symmetric_irreflexive` and `isolated_arguments` are already there as cheap
  graph diagnostics if the SCC wave (or a portfolio selector) wants them.
* `find_ideal_extension` has a pre-existing soundness bug (see test results) —
  worth fixing before relying on it inside an SCC recursion.

## Commit

`f827ff1db7bc7700686cf66d61cdda2954b2f5cd` (this is the parent; this line was updated in a follow-up commit -- see git log)
