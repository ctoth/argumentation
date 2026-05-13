# Wave C2a — ABA preprocessing + Z3 preferred-growth fix

2026-05-12. Branch `experiment/graph-speedup-wave-a-preprocessing` (correct, already on it). HEAD b882a25.

## Task
- §1 of `reports/aba-incremental-spec.md`: `simplify_aba` (well-founded ABA preprocessing), conservative residual form, support-mask grounded fixpoint, gated by `GROUNDED_REDUCT_ABA_SEMANTICS = {grounded,complete,preferred,stable,ideal}`, ABA+ no-op.
- §2.3a: refactor `_sat_preferred_cegar_extension` so the ranked-closure encoding is built once per query, push/pop for transient hypotheses. NOT §2.3b.
- Wire into aba_sat.py Z3 path + solve_aba_with_backend. Default ON, simplify=False opt-out.
- New tests/test_aba_preprocessing.py. Benchmark. ruff+pyright. Commit. Report.

## Observed
- Baseline `pytest -k aba --ignore=tests/test_datalog_grounding.py`: 65 passed, 1 skipped. z3+clingo installed.
- `aba.py`: grounded_extension = least fixpoint of def_operator (def_operator uses _defends which is exponential via _all_subsets) — need support-mask version.
- `aba_sat.py`: `_SupportState` has `.defends(mask, assumption)` (line 822), `.from_framework` builds supports from `_minimal_supports`. Use this for grounded fixpoint.
- `aba_sat.sat_support_extension`/`sat_support_acceptance`/`sat_stable_extension` = Z3 path. `_sat_preferred_cegar_extension` (481) calls `_sat_admissible_cegar_extension` (508) fresh per grow-step.
- `solver.py` `_auto_aba_backend`: auto→sat for {complete,preferred,stable}, else native. native grounded = aba.grounded_extension (fast). Leave native.
- `aba_asp.solve_aba_with_backend` — has backend support_reference/asp/clingo.
- Rule dataclass needs `kind` + optional `name`. ABAFramework.__post_init__ validates flatness, contrary keys == assumptions.

## Plan
1. New `src/argumentation/aba_preprocessing.py`: `AbaSimplification` (original, residual, fixed_in, fixed_out, lift, lift_all, is_trivial), `simplify_aba`, `GROUNDED_REDUCT_ABA_SEMANTICS`, `grounded_assumption_set_via_supports`.
   Residual: assumptions'=survivors; contrary' restricted; rules'=drop rules with fixed_out antecedent, else strip fixed_in antecedents; language' = literals in rules' ∪ survivors ∪ their contraries.
2. Wire `simplify=True` into aba_sat: sat_support_extension, sat_support_acceptance, sat_stable_extension. Lift on the way out. Sentence-acceptance: if query is assumption in fixed_in→YES; in fixed_out→NO; else solve on residual (note: residual still has same rules so a sentence derivable from fixed_in is still derivable).
3. Wire into solve_aba_with_backend (simplify=True), lift extensions before post-filter.
4. §2.3a: `_AdmissibleCegarSolver` class.
5. tests/test_aba_preprocessing.py.

## Status (2026-05-12 mid)
DONE: aba_preprocessing.py written. Wired simplify into aba_sat.sat_support_extension/sat_support_acceptance/sat_stable_extension + new sat_stable_acceptance. §2.3a done: _AdmissibleCegarSolver class, _sat_preferred_cegar_extension reuses one solver. solver.py uses sat_stable_acceptance. aba_asp.solve_aba_with_backend has simplify=True + _solve_simplified.
NEXT: run pytest; write tests/test_aba_preprocessing.py; ruff/pyright; benchmark; commit; report.
Watch: import cycle aba_preprocessing<->aba_sat (lazy import inside fn — ok). residual ABAFramework construction (language must cover survivors+contraries+rule literals — covered).

## Status (2026-05-12 late)
- Full suite: 1 failed (pre-existing test_kernel_ideal_extension_is_admissible), 1491 passed, 2 skipped — matches baseline.
- New tests/test_aba_preprocessing.py: 129 passed (~2min, brute-force oracle on random instances).
- Bug found+fixed during testing: skeptical-stable acceptance when query in fixed_in but no stable extension exists → must be vacuously True (was returning False).
- TODO: ruff+pyright on touched files; benchmark; commit; report.
Touched: src/argumentation/aba_preprocessing.py (new), aba_sat.py, aba_asp.py, solver.py, tests/test_aba_preprocessing.py (new).

## Status (2026-05-12, perf round)
- First benchmark showed simplify=ON consistently SLOWER (preprocessing overhead, esp. O(n^3) grounded fixpoint via state.defends). Rewrote grounded_assumption_set_via_supports to compute attacked_by(S) once per round + test attack-support masks against it -> O(n^2(s+t)). Re-benchmark pending.
- DONE: re-benchmark (complete up to 1.5x win; preferred/stable ~0.5-0.6x on collapsing-chain because clingo path doesn't pay _minimal_supports cost — small absolute loss; trivial no-help ~0.9x via cheap closure bail-out). §2.3a: ~5-6x on preferred CEGAR growth.
- Full suite: 1 failed (pre-existing test_kernel_ideal_extension_is_admissible), 1620 passed, 2 skipped. ruff+pyright clean on all touched files (also fixed pre-existing `Rule` undefined in aba_sat.py by adding it to the import).
- TODO: write report, commit.
