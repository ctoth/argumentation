# Wave C3 — Adversarial correctness review: ABA preprocessing (C2a) + incremental CEGAR (C2b)

Date: 2026-05-12. Analyst subagent. Branch `experiment/graph-speedup-wave-a-preprocessing`, HEAD `b2cd74f`.
Read-only on source; ran the suite, pyright, and four independent oracle harnesses (now deleted).

## Verdict: **FIXES NEEDED**

No oracle disagreement that traces to a *new* logic error in `simplify_aba` or the CEGAR/`AbaIncrementalSolver` loops — those are sound (verified against the correct support-mask reference on ~2400 random instances, see below). But:

- **P1** — `AbaIncrementalSolver.grounded_extension()` delegates to the buggy `aba.grounded_extension`, so `solve_aba_with_backend(..., backend="asp"/"clingo", semantics="grounded", simplify=False)` returns a *non-conflict-free* "grounded extension" on frameworks where some assumption's contrary is a rule fact. This is a **regression** introduced by C2b's rerouting.
- **P2** — `tests/test_aba_preprocessing.py::test_preferred_cegar_matches_admissible_growth` is flaky: it fails in some full-suite runs (Z3 returns a different — but equally valid — admissible set on a re-run). The suite is therefore not green-deterministic; the prompt's "only `test_kernel_ideal_extension_is_admissible` fails" did not hold on the first full run.
- **P3 (doc/stale)** — the C2a perf report's `preferred`/`stable` regression rows describe the pre-C2b routing; C2b rerouted those for the `asp` backend. The regression on the *SAT* path (`auto` default) is real but bounded; recommendation: leave default-ON (below).

Everything else checks out.

---

## 1. Spec conformance

### C2a — `aba_preprocessing.py`

- `fixed_in` = the grounded assumption set, computed by `grounded_assumption_set_via_supports` (a polynomial support-mask `def`-operator fixpoint, `aba_preprocessing.py:114-161`) — **not** via `aba.def_operator`/`_all_subsets`. Verified equal to `aba.grounded_extension` on 600 random instances *except* on the fact-contrary cases where `aba.grounded_extension` is itself wrong (see "the pre-existing `aba.py` bug" below); `grounded_assumption_set_via_supports` gives the *correct* answer there. Conforms to spec UNRESOLVED-C.
- `fixed_out` = `{a : contrary(a) ∈ Th(fixed_in)}` (`aba_preprocessing.py:248-252`). Matches the spec.
- Residual = the **rule-rewriting** form (strip `fixed_in` antecedents, drop `fixed_out`-using rules), `aba_preprocessing.py:170-209` — *not* the conservative "pin the search space" form the spec recommended for v1. The module docstring acknowledges this. The rewriting is sound (verified by the oracle, §3): a `fixed_out` antecedent makes a rule dead in any conflict-free superset of `fixed_in`; a `fixed_in` antecedent is unconditionally derivable so stripping it is safe.
- Cheap `O(|rules|)` bail-out (`aba_preprocessing.py:236-243`): if every contrary is in `Th(all assumptions)` and no contrary is in `Th(∅)`, return trivial. Reasoning is correct (`def_operator(∅) = ∅` ⇒ grounded = ∅; and `fixed_out = {a : contrary(a) ∈ Th(∅)} = ∅`). Sound.
- `GROUNDED_REDUCT_ABA_SEMANTICS = {grounded, complete, preferred, stable, ideal}` (`aba_preprocessing.py:64-72`) — matches spec §1.4. `admissible` excluded; `ABAPlusFramework` is a genuine no-op (`simplify_aba` returns `AbaSimplification(base, base, ∅, ∅)` at `aba_preprocessing.py:225-227`). Confirmed by construction. `simplify=False` bypasses the layer entirely in every wired caller (`sat_support_extension`, `sat_support_acceptance`, `sat_stable_extension`, `sat_stable_acceptance`, `solve_aba_with_backend`).
- Lift rules in `aba_sat._simplified_support_acceptance` / `sat_stable_acceptance` / `aba_asp._solve_simplified_ds_pr`: assumption in `fixed_in` → accept; assumption in `fixed_out` → reject; sentence in `Th(fixed_in)` → accept; sentence not in `residual.language` (and not in `Th(fixed_in)`) → reject; else lift the residual answer. Matches spec §1.3 / UNRESOLVED-D. Verified against brute force (§3).

### C2b — `aba_incremental.py` + `aba_com_incremental.lp` + `aba_asp` rerouting

- `encodings/aba_com_incremental.lp` is a **verbatim** transcription of L21-TPLP Listing 1 (module π_com): all 13 rules (`in/out` guess, `supported/triggered_by_in`, the conflict-freeness constraint, `defeated/derived_from_undefeated/triggered_by_undefeated/attacked_by_undefeated`, the two complete-set constraints) match the paper, `←` rendered as `:-`. `#show in/1. #show supported/1.` added (harmless). Conforms; resolves spec UNRESOLVED-F (a new `.lp` was the right call — the existing `aba_complete.lp` is the enumeration variant).
- Multi-shot loop: one `clingo.Control`, `ABA(F) ∪ π_com` added & grounded once per query (`_new_control`, `aba_incremental.py:99-106`); transient `in(I)` / `supported(s)` checks via `solve(assumptions=[...])`; permanent `constr(out(I)) = :- out(a1),...,out(ak).` accumulated by adding a fresh `#program refine{n}` part and re-grounding just that part (`aba_incremental.py:231-243`, `299-310`). That is **correct** multi-shot usage: re-grounding a new program part adds rules permanently and does not perturb the already-grounded base; refinement clauses accumulate within a query and do **not** leak across queries because each preferred query builds a fresh `Control`. The complete/stable enumeration paths also build a fresh `Control` per call (so the docstring's claim that they "reuse the same Control across calls" is inaccurate — harmless).
- `is_skeptically_accepted_preferred` implements Algorithm 1 lines 2–9 faithfully: seed = complete set not deriving `s`; inner `_grow_to_maximal_not_deriving` adds `constr(out(I))` then searches for a superset still not deriving `s`; on inner termination, line 8 checks whether `Control ∪ in(I)` is SAT (a deriving proper superset) — if so, loop back; else `in(I)` is a preferred counterexample → NO. The `permanently_unsat` path for empty `out(I)` (constraint `:-`) is handled. `query not in language` → NO with a preferred witness. Matches spec §2.2/§2.3b.
- `enumerate_preferred` = Algorithm 4 (omit query and line 8, collect each maximal). `enumerate_complete`/`enumerate_stable` = single grounded solve (`+ ":- out(X), not defeated(X)."` for stable). Matches §2.3b. `is_credulously_accepted_complete`/`_stable` = single solve with `assumptions=[(supported(s), True)]` (+ stable constraint). Matches §2.4.
- `aba_asp.solve_aba_with_backend` routes `backend ∈ {asp,clingo}` × `semantics ∈ {complete,stable,preferred,grounded}` to `_solve_multishot`; DS-PR (`preferred` + `skeptical` + query) gets the Algorithm-1 fast path; `backend="clingo_subprocess"` keeps the legacy enumerate-then-filter path (oracle); `admissible` keeps the subprocess path. Composes with `simplify_aba` via `_solve_simplified` / `_solve_simplified_ds_pr` (residual solve + lift). Matches spec §2.3b/§2.4.

### §2.3a refactor (`_AdmissibleCegarSolver`)

- `_sat_admissible_cegar_extension` now just calls `_AdmissibleCegarSolver(framework).solve(...)` (`aba_sat.py` diff). `_sat_preferred_cegar_extension` builds one `_AdmissibleCegarSolver` and re-uses it across grow-steps via `solve(require_assumptions=..., require_any_assumption=...)`. The class builds the ranked-closure encoding + conflict-freeness implications **once** (`__init__`); each `solve()` does `_flush_permanent()` → `push()` → add transient `require_*` literals → run the `while check()==sat:` refinement loop (counterexample clauses go to `_pending_permanent` *and* `solver.add` at the current push level) → `finally: pop()`. The push-level `add`s are discarded by `pop`, but the same clauses are in `_pending_permanent` and re-flushed at base level on the next `solve()`. Net: refinement clauses accumulate across grow-steps; transient hypotheses don't leak. The layering is **correct**. The existing ABA-preferred tests pass (in isolation and in most full runs). One caveat: `_AdmissibleCegarSolver.solve()` returns *some* admissible set (often `∅` if Z3's model is all-false); two independent fresh-solver calls can return different valid sets — see the P2 flake below. Semantics preserved.

---

## 2. Suite + pyright

- `pyright src/argumentation/aba_preprocessing.py aba_incremental.py aba_sat.py aba_asp.py solver.py tests/test_aba_preprocessing.py tests/test_aba_multishot.py` → **0 errors, 0 warnings**. Clean (no stray new-diagnostics noise).
- `python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no` → **2 failed, 2631 passed, 2 skipped** (309 s):
  - `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible` — documented pre-existing.
  - `tests/test_aba_preprocessing.py::test_preferred_cegar_matches_admissible_growth` — **NOT documented; flaky**. Passes in isolation, passes in `pytest tests/test_aba_preprocessing.py`, passed in a separate `-k "...aba...solver..."` run, but failed once in the full run (`_AdmissibleCegarSolver(framework).solve()` returned `frozenset()` vs `_sat_admissible_cegar_extension(framework)` returning `frozenset({a2})` — both valid admissible sets; the strict-equality assertion at `tests/test_aba_preprocessing.py:467-470` is not a sound invariant since admissible sets aren't unique and Z3's model choice is not stable across process state). **P2.**
- `bench_scc_b2.py` at repo root — pre-existing stray from Wave B2, **not** from C2a/C2b. C2a/C2b left no stray root files or `tmp_work/`.

---

## 3. Oracle comparisons (actually run)

Independent harnesses (deleted after use). Reference of record = `aba_sat.support_extensions` (support-mask brute force, which handles empty supports / fact-contraries correctly) — *not* `aba.py`'s brute force, which has a pre-existing bug (next section).

| Comparison | instances | result |
|---|---|---|
| `grounded_assumption_set_via_supports` vs `aba.grounded_extension` | 600 random | 26 mismatches — **all are the `aba.py` bug** (`grounded_assumption_set_via_supports` is correct) |
| `grounded_assumption_set_via_supports` vs `∩ support_extensions(complete)` | 800 random | **0 mismatches** |
| `simplify_aba`-path enumeration vs `support_extensions` (complete / preferred / stable) | 800 random × 3 | **0 mismatches** |
| `AbaIncrementalSolver` enumeration vs `support_extensions` (complete / stable / preferred) | 800 random × 3 | **0 mismatches** |
| `solve_aba_with_backend(backend="asp")` enumeration vs `support_extensions` (complete / stable / preferred) | 800 random × 3 | **0 mismatches** |
| `AbaIncrementalSolver.is_skeptically_accepted_preferred` (DS-PR) vs `support_extensions(preferred)`-intersection, over assumptions + contraries + missing-sentence | 800 random | **0 mismatches**; counterexamples valid; 32 queries needed ≥2 outer CEGAR rounds |
| `solve_aba_with_backend(backend="asp", task="skeptical")` DS-PR, simplify on **and** off, vs the same reference | 800 random | **0 mismatches** |
| `solve_aba_with_backend(backend="asp", simplify=False)` vs `backend="clingo_subprocess"` — complete / stable / preferred enumeration + DS-PR | 200 random | **3 disagreements, all `grounded`** — multishot says grounded `{a0}` / `{a0,a1}`, subprocess says `∅` (subprocess is right). Root cause = the P1 bug below. Complete/stable/preferred/DS-PR: 0 disagreements. |

So: `simplify_aba` (and its wiring), the `_AdmissibleCegarSolver` refactor, `AbaIncrementalSolver`'s complete/stable/preferred enumeration, DS-PR (Algorithm 1, including ≥2-round CEGAR), and DC are **all sound**. Only `grounded` via the multishot path is wrong, and only because it delegates to a buggy primitive.

### The P1 bug

`AbaIncrementalSolver.grounded_extension()` (`aba_incremental.py:163-164`) returns `aba.grounded_extension(self.framework)`. `aba.grounded_extension` → `aba.def_operator` → `aba._defends`, and `_defends` (in `aba.py`) iterates `for attacker in _all_subsets(...): if attacker and ...:` — it **skips the empty attacker set**. So an assumption `a` whose contrary is a rule fact (attacked by `∅`) is wrongly treated as "defended by everything", lands in the grounded set, and you get a non-conflict-free "grounded extension":

```
assumptions={a0}, contrary={a0:p0}, rules={ p0 :- . }
aba.grounded_extension(F)                                            -> frozenset({a0})   # WRONG, not conflict-free
solve_aba_with_backend(F, backend="asp", semantics="grounded",
                       simplify=False).extensions                    -> (frozenset({a0}),) # WRONG (C2b regression)
solve_aba_with_backend(F, backend="clingo_subprocess", ...)          -> (frozenset(),)     # correct
grounded_assumption_set_via_supports(F)                              -> frozenset()        # correct
```

`aba.grounded_extension` being buggy is **pre-existing** (the native backend has always used it). But C2b *newly* routed `backend ∈ {asp,clingo}` grounded through `AbaIncrementalSolver.grounded_extension()` → it inherited the bug, where the old subprocess path was correct → **regression on the `asp`/`clingo` grounded backend** when `simplify=False`. With `simplify=True` (default) the residual never has a fact-contrary among survivors (such an assumption is in `fixed_out`), so the default path is unaffected — but `simplify=False` is a documented public option, and the C2b test `tests/test_aba_multishot.py::test_multishot_enumeration_matches_native_and_support_reference` checks `grounded` only via `solver.grounded_extension()` vs `native_aba.grounded_extension` (both buggy → they agree → the test passes and masks it).

**Fix (do not apply here):** make `AbaIncrementalSolver.grounded_extension` call `argumentation.aba_preprocessing.grounded_assumption_set_via_supports(self.framework)` (the correct primitive already in the repo). Separately, `aba._defends` should not skip the empty attacker — that fixes `aba.grounded_extension`, `aba.well_founded_extension`, `aba.complete_extensions` (it currently returns `()` — no complete set — for the example above, which is also wrong) and would let the differential tests use `aba.py` as a trustworthy oracle again. Out of scope for this wave but worth filing.

---

## 4. C2a perf regression — recommendation: **leave default-ON**

The C2a report (`reports/graph-speedup-wave-c2a-aba-preprocessing.md` §"Before/after benchmark") flags a 0.52×–0.63× regression on `preferred`/`stable` on collapsing-chain instances that the `AssumptionKernel` path solves in single-digit ms — the preprocessing pays `_minimal_supports` (for the grounded fixpoint) which the kernel path otherwise skips. I re-measured on chain-into-hard-core shapes with derivation depth (so `_minimal_supports` isn't free):

```
chain40 +cyc10  preferred: simplify=False 18.9ms  simplify=True  6.9ms  2.77x
chain120+cyc10  preferred: simplify=False 46.5ms  simplify=True  7.6ms  6.08x
chain200+cyc12  preferred: simplify=False  7.7ms  simplify=True  6.2ms  1.25x
chain40 +cyc10  complete:  simplify=False 19.2ms  simplify=True 12.8ms  1.50x
chain120+cyc10  complete:  simplify=False 36.3ms  simplify=True 13.9ms  2.61x
chain200+cyc12  complete:  simplify=False 54.6ms  simplify=True 17.1ms  3.19x
```

i.e. on the timeout-cluster shape (long unattacked chain into a hard cycle) preprocessing is a clean win for both. The regression the report describes is confined to instances that were *already* < 20 ms and have a non-collapsing grounded set whose `_minimal_supports` cost exceeds a trivial solve — a small *absolute* loss (~5–15 ms). The cheap two-`closure` bail-out (`aba_preprocessing.py:236-243`) covers the truly-trivial (`is_trivial`) case at ≈1.0×. So:

- **Recommendation: leave the wiring default-ON.** The win on the recon's stated timeout cluster (83 ABA SE-PR/SE-ST in ICCMA-2023 — long-chain shapes) dominates; the regression is bounded to small absolute time on already-fast instances; the `simplify=False` opt-out exists for callers that know they're solving easy instances. Gating it (e.g. "only when `fixed_in ∪ fixed_out` non-empty AND instance non-trivial") would add a heuristic to a layer whose gate (the per-semantics whitelist) is already the safety net, and the bail-out already handles the trivial-grounded case.

Note: the C2a report's `preferred`/`stable` rows are now **stale** for `backend="asp"` (C2b rerouted those through `_solve_multishot`, not `AssumptionKernel`). The regression discussion remains accurate for the `auto`/SAT path (`solve.py` → `sat_support_extension`/`sat_stable_extension`), which still routes preferred through `AssumptionKernel.preferred_extension` after `simplify_aba`. Worth a one-line note in that report.

---

## 5. Minor / cleanup (not correctness)

- `bench_scc_b2.py` at repo root — stray from Wave B2, predates this work; should be moved under `bench/` or deleted.
- `aba_incremental.py` docstring: the complete/stable enumeration methods build a fresh `Control` per call; the claim "reuse the same `Control` across calls" (`aba_incremental.py:69-72`) is inaccurate (harmless).
- `simplify_aba(ABAPlusFramework)` returns `AbaSimplification` with `original` = the *inner* `ABAFramework`, not the `ABAPlusFramework` — fine because callers only ever see `is_trivial == True` for it, but slightly surprising.
- `tests/test_aba_preprocessing.py` and `tests/test_aba_multishot.py` use `aba.py`'s brute force as an oracle in several places; because their random generators never emit zero-body rules whose head is a contrary, they don't hit the `aba.py` bug — but that means those tests also can't catch the P1 regression. Once `aba._defends` is fixed, tightening the generators would close the gap.

---

## Files

- `src/argumentation/aba_preprocessing.py` — C2a preprocessing (sound).
- `src/argumentation/aba_sat.py` — `_AdmissibleCegarSolver` refactor + `simplify=` wiring (sound).
- `src/argumentation/aba_incremental.py` — C2b multi-shot solver; **`grounded_extension()` at line 163-164 is the P1 bug** (delegates to buggy `aba.grounded_extension`).
- `src/argumentation/aba_asp.py` — `_solve_multishot` / `_solve_simplified` / `_solve_simplified_ds_pr` rerouting (sound; inherits the P1 bug only on `semantics="grounded"`).
- `src/argumentation/encodings/aba_com_incremental.lp` — verbatim L21-TPLP Listing 1 (faithful).
- `src/argumentation/solver.py` — `auto` ABA routing through `sat_support_*` with `simplify=True` default (sound).
- `src/argumentation/aba.py` — pre-existing bug in `_defends` (skips empty attacker) → wrong `grounded_extension`/`well_founded_extension`/`complete_extensions` on fact-contrary frameworks; root cause of P1, not introduced by this wave.
- `tests/test_aba_preprocessing.py:467-470` — flaky strict-equality assertion (P2).
- `bench_scc_b2.py` — stray root file (pre-existing).
