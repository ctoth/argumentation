# Wave C4 — Fixing the C3 analyst's findings (P1 soundness, P2 flake, P3 doc, cleanup)

Date: 2026-05-12. Coder subagent. Branch `experiment/graph-speedup-wave-a-preprocessing` (from HEAD `b2cd74f`).
Source review: `reports/graph-speedup-wave-c3-analyst.md`.

## Commit

`559b24d` — "Fix empty-attacker ABA grounded bug + C4 cleanups" (on `experiment/graph-speedup-wave-a-preprocessing`).
Files: `src/argumentation/aba.py`, `src/argumentation/aba_incremental.py`, `tests/test_aba_multishot.py`,
`tests/test_aba_preprocessing.py`, `reports/graph-speedup-wave-c2a-aba-preprocessing.md`,
`reports/graph-speedup-wave-c4-fixes.md`, deletion of `bench_scc_b2.py`.

## P1 — soundness regression in grounded ABA (the important one)

**Root bug (`src/argumentation/aba.py`, `_defends`):** the loop `for attacker in _all_subsets(...): if attacker and closed(...) and _attacks(...)` skipped the empty attacker set. An assumption whose contrary is derivable from no premises (e.g. a rule fact `p0 :- .` where `contrary(a0) = p0`) is attacked by `∅`; nothing can counter-attack `∅`, so such an assumption is not defended — but the guard let it through, so `aba.grounded_extension` returned a non-conflict-free set. **Fix:** dropped the `attacker and` guard (`_attacks(defender, ∅)` is always false, so the early-`return False` fires correctly). This also corrects `aba.well_founded_extension` and `aba.complete_extensions` on fact-contrary frameworks (the analyst noted `complete_extensions` was returning `()` there).

**Call site (`src/argumentation/aba_incremental.py`, `AbaIncrementalSolver.grounded_extension`):** was `return aba.grounded_extension(self.framework)` (exponential `_all_subsets` *and* inherited the bug). **Fix:** now `return grounded_assumption_set_via_supports(self.framework)` — the polynomial support-mask fixpoint from `aba_preprocessing.py` (the C2a reference of record, correct on fact-contrary frameworks). No circular import (`aba_preprocessing` only imports from `aba`/`aspic`). Removed the now-unused `from argumentation.aba import grounded_extension as _native_grounded_extension`.

`aba_asp.solve_aba_with_backend`: the multishot path (`semantics="grounded"` → `solver.grounded_extension()`) now picks up the support primitive; the subprocess/native fallback path (`aba_asp.py:511`, `aba_semantics.grounded_extension`) picks up the fixed `_defends`. Both ends fixed; no further ABA grounded paths exist.

**Regression test added** (`tests/test_aba_multishot.py`): `_fact_contrary_frameworks()` — the analyst's exact repro (`assumptions={a0}, contrary={a0:p0}, rules={p0 :- .}`) plus two siblings (a second free assumption; a fact contrary reached via a derived sentence). `test_grounded_fact_contrary_is_conflict_free` checks `aba.grounded_extension`, `AbaIncrementalSolver.grounded_extension`, all equal to the grounded reference (= the least complete extension via `aba_sat.support_extensions(framework, "complete")` — `support_extensions` has no `"grounded"` mode) and all conflict-free. `test_solve_aba_grounded_fact_contrary_via_backend` checks `solve_aba_with_backend(backend="asp"|"clingo", semantics="grounded", simplify=False)`. 9 cases, all pass. Before the fix, the analyst's repro returned `{a0}` (non-conflict-free); now returns `∅`.

## P2 — flaky/unsound strict-equality assertion

`tests/test_aba_preprocessing.py::test_preferred_cegar_matches_admissible_growth` asserted `_AdmissibleCegarSolver(framework).solve() == _sat_admissible_cegar_extension(framework)`. Admissible sets are not unique and Z3's model choice is not stable across process state, so this is not a sound invariant — it failed intermittently in full-suite runs (the analyst observed `frozenset()` vs `frozenset({a2})`, both valid). **Fix:** replaced with `assert native_aba.admissible(framework, reused)` and `assert native_aba.admissible(framework, oneshot)` (each result is a genuine admissible set; the `cegar in preferred_ref` assertion above already covers the §2.3a refactor's correctness). Both runs of the full suite below: no flake.

## P3 — stale doc rows

`reports/graph-speedup-wave-c2a-aba-preprocessing.md`: added a `> **SUPERSEDED (Wave C2b, 2026-05-12):** ...` block before the `### §1 — simplify_aba on the collapsing chain` table pointing to `reports/graph-speedup-wave-c2b-aba-multishot.md` for the current `backend="asp"` routing, and annotated the three `preferred`/`stable` rows with *(SUPERSEDED — see C2b)*. The `complete` rows and the regression discussion (still accurate for the `auto`/SAT path) were left intact.

## Cleanup

- `bench_scc_b2.py` (repo root, stray from Wave B2) — `git rm`'d. No equivalent worth keeping under `bench/` (it was a one-off SCC-B2 timing script).
- `git ls-files | grep '^[^/]+\.py$'` after removal → empty. `bench_scc_b2.py` was the only tracked stray root file. (Many untracked `notes/*.md`, `prompts/*.md`, `reports/*.md` from prior waves sit at/under the repo root — untracked, not committed, not my job per the prompt.)

## Suite results

`python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no` (requires `z3-solver` + `clingo`, both installed):

- **Run 1:** `1 failed, 2641 passed, 2 skipped in 323.17s`
- **Run 2:** `1 failed, 2641 passed, 2 skipped in 304.17s`

Identical on both runs. The only failure is `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible` (the pre-existing one). The previously-flaky `test_preferred_cegar_matches_admissible_growth` passed on both runs. +10 new tests from the C4 regression battery, all pass. (Pre-fix baseline per the C3 analyst was `2 failed, 2631 passed` with the P2 flake intermittent; net here: P2 flake eliminated, regression battery added, count up by 10.)

## `test_kernel_ideal_extension_is_admissible` — still failing, why

**Still fails.** It is *not* related to the `_defends` fix and is *not* an ABA test. It's an **abstract-AF** Hypothesis property test (`tests/test_solver_encoding.py:733`): the AF kernel's `ideal_extension` returns a non-admissible set on a 4-argument framework (falsifying example: ideal `{c}`, args `{a,aa,b,c}`, defeats `{(a,aa),(a,b),(aa,a),(aa,b),(b,c)}` — `{c}` is attacked by `b` which is not counter-attacked by `{c}`, so it's not admissible). That's a bug in the AF preprocessing/kernel code, which this wave was explicitly told not to touch. Out of scope; left as-is.

## ruff + pyright

`ruff check src/argumentation/aba.py src/argumentation/aba_incremental.py tests/test_aba_multishot.py tests/test_aba_preprocessing.py` → **All checks passed!**

`pyright src/argumentation/aba.py src/argumentation/aba_incremental.py tests/test_aba_multishot.py tests/test_aba_preprocessing.py`:

```
0 errors, 0 warnings, 0 informations
```

## Out of scope / not done

- Did not change ABA semantics beyond the two identified bugs. The `_defends` fix did **not** cascade — the full ABA test suite (`test_aba*.py`) is green; the only failure is the unrelated AF ideal test, which was already failing.
- Did not touch AF preprocessing/SCC code.
- Did not redo any C2a/C2b feature work.
- Minor items the analyst flagged as harmless (the inaccurate `aba_incremental.py` docstring about reusing `Control` across calls; `simplify_aba(ABAPlusFramework)` returning the inner `ABAFramework` as `original`) — left as-is, not soundness issues.
