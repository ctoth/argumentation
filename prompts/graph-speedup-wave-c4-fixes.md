# Wave C4 — Fix the analyst's findings (P1 soundness, P2 flaky test, P3 doc, cleanup)

You are a coding subagent. Working dir: `C:\Users\Q\code\argumentation`, branch `experiment/graph-speedup-wave-a-preprocessing` (HEAD `b2cd74f`). `git checkout` it; commit there; do NOT branch.

## Context

Read `reports/graph-speedup-wave-c3-analyst.md` (the analyst review) — it has the precise diagnoses with file:line. Also relevant: `reports/aba-incremental-spec.md`, `reports/graph-speedup-wave-c2a-aba-preprocessing.md`, `reports/graph-speedup-wave-c2b-aba-multishot.md`. Source: `src/argumentation/aba_incremental.py`, `src/argumentation/aba.py`, `src/argumentation/aba_preprocessing.py`, `src/argumentation/aba_sat.py`, `tests/test_aba_preprocessing.py`.

## Fixes to apply

### P1 — soundness regression in grounded ABA (the important one)
`AbaIncrementalSolver.grounded_extension()` (around `aba_incremental.py:163-164`) delegates to `aba.grounded_extension`, which is buggy: `aba._defends` skips the empty-attacker set, so an assumption whose contrary is derivable with no attackers is wrongly kept. Symptom: `solve_aba_with_backend(F, backend="asp"|"clingo", semantics="grounded", simplify=False)` returns a non-conflict-free set (analyst's repro: assumptions `{a0}`, contrary `{a0: p0}`, rule `p0 :- .` → returns `{a0}`, correct answer is `∅`).
- **Fix the call site**: have `AbaIncrementalSolver.grounded_extension()` (and any other ABA grounded path that goes through `aba.grounded_extension` / `aba._defends`) use the polynomial `grounded_assumption_set_via_supports` (in `aba_preprocessing.py`, per the C2a report) instead.
- **Also fix the root bug**: `aba._defends` should treat an argument/sentence with an empty attacker set as defended (vacuously). Fix it so `aba.grounded_extension` itself is correct, and confirm `test_kernel_ideal_extension_is_admissible` — the long-standing pre-existing failure — is or isn't related (it may be a *different* bug; don't claim it's fixed unless it actually goes green). If fixing `_defends` changes other results, run the oracle (`tests/test_aba_*`) and make sure everything that changes is changing toward *correct* (conflict-free, sound) — add a regression test for the analyst's exact repro framework.

### P2 — flaky/unsound test
`tests/test_aba_preprocessing.py::test_preferred_cegar_matches_admissible_growth` (around line 467-470) asserts strict set-equality between `_AdmissibleCegarSolver(F).solve()` and `_sat_admissible_cegar_extension(F)` — but Z3 can legitimately return different valid admissible sets, so this isn't a sound invariant. Replace the assertion with one that *is* sound: e.g. both results are admissible sets of `F` (use the existing admissibility checker), or both have the same status (some / none), rather than that they're the identical set. Keep the test's intent (the §2.3a refactor doesn't break the preferred-growth path).

### P3 — stale doc rows
`reports/graph-speedup-wave-c2a-aba-preprocessing.md` has `preferred`/`stable` benchmark rows that describe the pre-C2b routing (before `aba_asp` was rerouted through the multi-shot solver). Add a short note/correction in that report pointing to `reports/graph-speedup-wave-c2b-aba-multishot.md` for the current routing's numbers. Don't rewrite the whole report — just a clear "SUPERSEDED: see C2b" annotation on the affected rows.

### Cleanup
- Delete `bench_scc_b2.py` from the repo root (stray bench script from Wave B2). If there's an equivalent worth keeping, move it under `bench/`; otherwise just remove it.
- Check `git status` for any other stray files at the repo root (`tmp_*.py`, `tmp_work/`, scratch scripts) committed by earlier waves — if any are tracked, remove them; if untracked, leave them (not your job) but note them.

## Definition of done
1. P1 fixed at both the call site and the `aba._defends` root, with a regression test for the analyst's repro framework; P2 assertion replaced with a sound one; P3 annotation added; `bench_scc_b2.py` removed.
2. Full suite: `python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no` — run it twice (the analyst saw P2 flake intermittently) and confirm it's stable. Target: only the pre-existing `test_kernel_ideal_extension_is_admissible` fails (or it's now green if your `_defends` fix actually fixed it — verify, don't assume), nothing else, on both runs. Requires `z3-solver` + `clingo` (`pip install z3-solver clingo`; `pip install -e .`).
3. `ruff` + `pyright` clean on every file you touched — paste pyright output for touched files into the report.
4. `git add` + `git commit` on the feature branch. **Commit hash in the report.**
5. Report → `reports/graph-speedup-wave-c4-fixes.md`: each fix, what changed, the regression test added, suite results (both runs), pyright output, commit hash, and — explicitly — whether `test_kernel_ideal_extension_is_admissible` is still failing and why (your read).

## Hard stops
- Do NOT change the ABA semantics beyond fixing the identified bugs. Do NOT touch the AF preprocessing/SCC code. Do NOT redo any C2a/C2b feature work.
- If fixing `aba._defends` cascades into many test changes you can't confidently classify as "toward correct", STOP and report — don't push a sweeping change blind.
