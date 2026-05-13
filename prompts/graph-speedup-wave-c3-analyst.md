# Wave C3 — Adversarial correctness review of the ABA preprocessing + incremental work

You are an analyst subagent. Read-only on source; you may run tests/benchmarks. You find problems, you do not fix them. Working dir: `C:\Users\Q\code\argumentation`, branch `experiment/graph-speedup-wave-a-preprocessing` (HEAD `b2cd74f`).

## What you're reviewing

Two waves added ABA-side speedups:
- **C2a** — `src/argumentation/aba_preprocessing.py`: `simplify_aba` (well-founded/grounded ABA preprocessing, semantics-gated, ABA+ no-op) + a Z3 `_AdmissibleCegarSolver` refactor in `aba_sat.py`. Report: `reports/graph-speedup-wave-c2a-aba-preprocessing.md`.
- **C2b** — `src/argumentation/aba_incremental.py` (`AbaIncrementalSolver`, clingo multi-shot, Algorithm 1/4) + `encodings/aba_com_incremental.lp` + rerouting of `aba_asp.solve_aba_with_backend`. Report: `reports/graph-speedup-wave-c2b-aba-multishot.md`.
- Spec for both: `reports/aba-incremental-spec.md` (based on `papers/Lehtonen_2021_IncrementalASP_ABA.pdf`).
- Precedent: `reports/graph-speedup-wave-a-preprocessing.md` (the AF `simplify_af` whose API shape `simplify_aba` mirrors).

## Your job — verify, don't trust

1. **Spec conformance.** Read `aba_preprocessing.py` and `aba_incremental.py` against `reports/aba-incremental-spec.md` and the paper. Is `fixed_in` really the grounded assumption set and `fixed_out` really `{a : contrary(a) ∈ Th(fixed_in)}`? Is the grounded fixpoint actually polynomial (no hidden `_all_subsets`)? Is the residual sound (the conservative rule-rewriting form — does stripping `fixed_in` antecedents and dropping `fixed_out`-using rules preserve the gated semantics)? Is `aba_com_incremental.lp` a faithful transcription of Listing 1? Does the multi-shot loop implement Algorithm 1 (the refinement-clause `constr(out(I))` mechanism via re-grounded program parts — is that *correct* clingo multi-shot usage, or does it accidentally make refinements transient / leak across queries)? Quote file:line for anything suspicious.
2. **Soundness gating.** Confirm `GROUNDED_REDUCT_ABA_SEMANTICS` = {grounded, complete, preferred, stable, ideal} and that admissible and `ABAPlusFramework` are genuine no-ops (construct an ABA+ framework and an admissible query and check the preprocessing does nothing). Confirm the lift rules for sentence vs assumption queries (fixed_in → accept, fixed_out / not-in-residual-language → reject, else lift) — find a case for each. Confirm `simplify=False` truly bypasses the layer.
3. **Break it.** For grounded/complete/preferred/stable/ideal, check `simplify_aba`-path result == brute-force `aba.py` reference, on adversarial ABA frameworks: non-trivial well-founded set; a framework where `fixed_out` is non-empty; a framework where the residual becomes empty; ABA+ frameworks (must be untouched); frameworks with no stable extension (vacuous DS/DC); cyclic support; mutually-contrary assumptions; plus a few hundred random ABA instances of varied size. Then the same for the C2b multi-shot path: `AbaIncrementalSolver` result == `aba_sat` support reference == brute-force `aba.py` == legacy `clingo_subprocess`, especially DS-PR on instances needing ≥2 CEGAR rounds. Any disagreement = P0: report the exact framework, all the results, your read of which step is wrong.
4. **§2.3a refactor.** Confirm `_sat_preferred_cegar_extension` via `_AdmissibleCegarSolver` produces results identical to what it did before (the existing ABA-preferred tests cover this; verify they pass and that the refactor didn't change semantics — e.g. push/pop scoping of transient hypotheses vs base-level refinement clauses is correct, no clause leaks).
5. **Suite + lint reality check.** `python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no` → only the documented pre-existing `test_kernel_ideal_extension_is_admissible` fails, `~2632 passed`. `pyright` on `aba_preprocessing.py`, `aba_incremental.py`, `aba_sat.py`, `aba_asp.py`, `solver.py`, `tests/test_aba_preprocessing.py`, `tests/test_aba_multishot.py` → 0 errors (the new-diagnostics noise from the coders' runs should be absent in the committed state; if not, that's a finding). Check for stray files committed to the repo root (the previous wave left `bench_scc_b2.py`; C2a/C2b may have left bench scripts or `tmp_work/`) — note them.
6. **The C2a perf regression.** C2a's report flags a ~0.5–0.6× regression on already-fast clingo `preferred`/`stable` instances with a non-trivial grounded set (preprocessing pays `_minimal_supports` cost the `AssumptionKernel` path otherwise skips). Confirm whether this is real, characterize when it bites (does the cheap empty-grounded bail-out cover the common case? is the regression bounded to small absolute time?), and give a recommendation: leave default-ON, or gate the wiring (e.g. only the Z3 `complete` path, or only when `fixed_in ∪ fixed_out` is non-empty AND the instance is non-trivial).

## Deliverable

`reports/graph-speedup-wave-c3-analyst.md`:
- Verdict: **SOUND** / **FIXES NEEDED** (severity-ranked list, file:line, repro) / **BROKEN** (oracle disagreement — P0).
- Spec-conformance findings for C2a and C2b.
- Any oracle disagreements (exact frameworks + results).
- Suite + pyright results as observed.
- Recommendation on the C2a regression (default-ON vs gated, with reasoning).
- Minor cleanup items (stray root files, etc.) separate from correctness.

Be adversarial. Actually run the oracle comparisons — "looks fine" without running them is not acceptable. This is the last gate before the workstream wraps.
