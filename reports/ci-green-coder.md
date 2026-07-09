# ci-green coder report

Branch: `exp/ci-green` from `main@cc50c4a`, in isolated worktree
`.claude/worktrees/agent-a862a3c79133f6a92`. Ward phase: experiment-worker.
Diagnosis followed: `reports/ci-red-investigation.md` (main tree). No push, no
merge; recommend-only.

## Commits

| Fix | Commit | Files |
|---|---|---|
| 1. stale contract test | `2cd96ac` | `tests/test_performance_contracts.py` |
| 2. docs regression | `96e23ed` | `docs/argumentation-package-boundary.md` |
| 3. hashseed flake | `0bfb172` | `tools/collapsed_profile_summary.py`, `scripts/run_hashseed_matrix.py` |
| docs: experiment + report | (this commit) | `experiments/2026-07-08-ci-green.md`, `reports/ci-green-coder.md` |

## Per-fix diff summary

### Fix 1 — `2cd96ac` (test-only; src routing untouched, as planned)

- RED: `test_large_dense_stable_auto_route_uses_sat_without_asp` failed at
  `tests/test_performance_contracts.py:129` (forbidden-ASP AssertionError) —
  the pre-`bc140ba` expectation.
- Renamed to `test_large_dense_stable_auto_route_uses_asp_when_not_sparse_narrow`:
  same 151-assumption large-dense fixture, now forbids
  `sat_aba_stable_extension` and mocks `_solve_asp_aba_single_extension`,
  asserting the full-solve path dispatches to ASP — mirroring
  `test_large_dense_aba_stable_single_extension_auto_uses_asp_when_not_sparse_narrow`
  in `tests/solving/test_solver_availability.py` (updated by `bc140ba`).
- Kept the SAT contract: refactored the fixture builder to
  `dense_flat_stable_framework(size)` (151 = large-dense-only; 700 = also
  sparse-narrow: width-1 rule bodies, distinct contraries, 26 rules/assumption,
  assumptions/language = 700/19600 < 0.45) and added
  `test_sparse_narrow_stable_auto_route_uses_sat_without_asp` asserting
  `_auto_aba_backend_for_framework("auto","stable",task="single-extension",...)
  == "sat"`, mirroring the sibling's backend-level sparse-narrow test.
- GREEN: `uv run pytest -q tests/test_performance_contracts.py` -> `7 passed,
  1 skipped in 0.64s`.

### Fix 2 — `96e23ed` (docs-only; test not weakened)

- RED locally showed **five** offenders, not one — the CI excerpt in the
  diagnosis was truncated. All in `argumentation-package-boundary.md`:
  `src/argumentation/{af_revision,dung,preference,probabilistic,probabilistic_treedecomp}.py`.
- Traced current homes (verified on disk / via `git log --follow`):
  `core/dung.py`, `core/preference.py`, `dynamics/af_revision.py`,
  `probabilistic/probabilistic.py`, and the treedecomp split
  `probabilistic/probabilistic_treedecomp_construction.py` (`d05a438`) /
  `probabilistic_paper_td.py` (`1a3fb16`) / `probabilistic_grounded_td.py`
  (`ea8ded0`). `semantics.py` genuinely still lives at the flat path — kept.
- Judgment call (noted, contained to the one doc section): the other 11 file
  entries and the adjacent kernel-module import block were equally stale flat
  paths; fixing only the 5 guard-flagged strings would leave the list half
  old-layout. Refreshed the whole "Extracted Formal Kernel" section to paths
  that exist today.
- GREEN: `uv run pytest -q tests/test_docs_surface.py` -> `7 passed in 0.28s`.

### Fix 3 — `0bfb172` (source fix, not test; prover script added)

- Root cause: `serializable_top` used `Counter.most_common(limit)`, whose
  tie-break is insertion order; the inclusive counter is populated from
  `set(frames)` iteration (`hot_frames`), so equal-share rows order per
  PYTHONHASHSEED.
- Fix in `tools/collapsed_profile_summary.py`: new `top_frames(counter, limit)`
  ranking by `(-samples, frame)`; `serializable_top` refactored onto it.
- Prover: `scripts/run_hashseed_matrix.py` runs the target once per seed in a
  fresh interpreter (PYTHONHASHSEED only binds at startup), disabling
  pytest-randomly to isolate the hash effect.

## Hashseed matrix (test_collapsed_profile_summary)

| Seed | Pre-fix | Post-fix |
|---|---|---|
| 0 | FAIL | PASS |
| 1 | FAIL | PASS |
| 2 | FAIL | PASS |
| 3 | FAIL | PASS |
| 4 | FAIL | PASS |
| 5 | PASS | PASS |
| 6 | FAIL | PASS |
| 7 | PASS | PASS |
| 8 | FAIL | PASS |
| 9 | PASS | PASS |

Pre-fix 3/10 passed (RED evidence on 7 seeds, matching the known debt);
post-fix 10/10.

## CI-equivalent gate results (final tree)

`uv run pytest -q --timeout=600` (exact test.yml step), tail of
`logs/ci-green-full-pytest.log`:

```
..........................................................s............. [ 99%]
.                                                                        [100%]
2948 passed, 4 skipped, 1 xfailed in 279.46s (0:04:39)
EXIT=0
```

- `uv run pyright src`: 0 errors, 0 warnings, 0 informations.
- `uv run pyright tools/collapsed_profile_summary.py
  scripts/run_hashseed_matrix.py tests/test_performance_contracts.py`:
  0 errors, 0 warnings.
- `uv run lint-imports`: Contracts: 2 kept, 0 broken.
- `uv build`: built `formal_argumentation-0.3.0` sdist + wheel.

## Recommendation

Merge `exp/ci-green` into `main`. Exactly the three diagnosed failures were
fixed; no skips, no deselection, no test weakened or deleted; the intended
`bc140ba` routing behaviour is preserved and now double-pinned. Local suite is
fully green and all four test.yml steps pass locally.
