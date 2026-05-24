# Codex review: argumentation package reorg

Workflow actually used: read `prompts/codex-review-reorg.md`, the approved plan
`C:\Users\Q\.claude\plans\i-think-we-should-vivid-koala.md`, the migration
reports named by the prompt, current source/tests/docs/config, and current
verification output from `uv run lint-imports`, `uv run pyright src`, `uv
build`, targeted structural tests, targeted ABA regression tests, old-path
greps, and wheel inspection.

## 1. import-linter contract

### Layer contract matches the current DAG

Verdict: **OK**

Evidence:

- `pyproject.toml:104-111` orders the contract from top to bottom:
  `semantics`, `solving`, `solver_adapters`, `interop`,
  `structured.aba | probabilistic | dynamics`,
  `structured.aspic | frameworks | gradual | ranking`, `core`.
- `uv run lint-imports` passed currently:
  `Analyzed 72 files, 121 dependencies`; `Layered architecture KEPT`;
  `gradual and ranking are independent KEPT`; `Contracts: 2 kept, 0 broken`.
- Direct source import audit found the expected cross-layer edges, for example
  `src/argumentation/interop/iccma.py:13` imports
  `argumentation.structured.aba.aba`, and `src/argumentation/solving/solver.py`
  imports `structured.aba`, `frameworks`, `core`, and `solver_adapters`.

Recommended action: no action.

### Sanctioned upward exceptions are narrow

Verdict: **OK**

Evidence:

- `pyproject.toml:113-116` has exactly two `ignore_imports` entries:
  `argumentation.structured.aspic.aspic_encoding -> argumentation.solver_adapters.clingo`
  and `argumentation.structured.aba.aba_asp -> argumentation.solver_adapters.clingo`.
- Current source has the corresponding function-local imports at
  `src/argumentation/structured/aspic/aspic_encoding.py:206` and
  `src/argumentation/structured/aba/aba_asp.py:188`.

Recommended action: no action.

## 2. ABA-SAT correctness fix at `5c53816`

### `fixed_out` is handled at the decomposition boundary

Verdict: **OK**

Evidence:

- `src/argumentation/structured/aba/aba_decomposition.py:90-107` computes
  simplification/plan/telemetry, then short-circuits when
  `require_assumptions & simplification.fixed_out`.
- `src/argumentation/structured/aba/aba_decomposition.py:106-108` records
  validation success and lifted size, then returns `extension=frozenset()`.
- `src/argumentation/structured/aba/aba_sat.py:552-558` converts a decomposed
  result that does not satisfy `require_assumptions <= decomposed` into `None`.
- `src/argumentation/structured/aba/aba_preprocessing.py:176` removes both
  `fixed_in` and `fixed_out` from residual assumptions; `:248-255` defines
  `fixed_out` from contraries derivable from the grounded set.
- `_RealPrefSatSolver` still assumes valid residual keys and would raise on a
  bad caller: `src/argumentation/structured/aba/aba_sat.py:1432-1433` indexes
  `self.prefsat_in[assumption]`. That is appropriate for this lower-level
  primitive.
- Targeted verification passed currently:
  `uv run pytest -q tests\structured\aba\test_aba.py::test_preferred_support_sat_preserves_required_assumptions tests\structured\aba\test_aba.py::test_preferred_support_sat_fixed_out_required_assumption_is_unsatisfiable tests\structured\aba\test_aba.py::test_preferred_support_sat_fixed_out_requirement_is_always_unsatisfiable`
  -> `3 passed in 2.37s`.

Recommended action: no action.

### Regression and property coverage are adequate

Verdict: **OK**

Evidence:

- `tests/structured/aba/test_aba.py:456-510` pins the concrete fixed-out
  falsifying example, verifies `fixed_in={a3}`, `fixed_out={a2}`, verifies
  fixed-out requirements return `None`, fixed-in requirements still work, and
  the unconstrained result is the native preferred extension.
- `tests/structured/aba/test_aba.py:516-541` adds a Hypothesis property:
  whenever a drawn required set intersects `fixed_out`,
  `sat_support_extension(..., "preferred", require_assumptions=...)` returns
  `None` and no native preferred extension satisfies the required set.

Recommended action: no action.

## 3. Completeness of import rewrites

### Shipped encoding comment still names old `argumentation.aba_asp`

Verdict: **FIX**

Evidence:

- Old-path grep over active source/docs found a stale shipped string:
  `src/argumentation/encodings/aba_com_incremental.lp:6`:
  `% argumentation.aba_asp.encode_aba_theory emits).`
- That `.lp` file ships in the 0.3.0 wheel. Current wheel listing includes
  `argumentation/encodings/aba_com_incremental.lp`.
- The correct new path is documented in `CHANGELOG.md:55`:
  `argumentation.aba_asp` -> `argumentation.structured.aba.aba_asp`.

Recommended action: update the comment to
`argumentation.structured.aba.aba_asp.encode_aba_theory`. This is not a runtime
import break, but it is a stale shipped string in the package and fails the
review prompt's string-reference check.

### Tracked code, tests, bench, and tools have no old flat imports

Verdict: **OK** except for the `.lp` finding above.

Evidence:

- PCRE old-path grep over `src tests bench tools README.md docs CHANGELOG.md
  pyproject.toml CONTRIBUTING.md` found no active Python import stragglers.
  Remaining old-path hits were the intentional `CHANGELOG.md:40-94` old-to-new
  table, layer names such as `argumentation.gradual` / `argumentation.ranking`,
  and two package-submodule imports in
  `tests/test_workstream_o_arg_gradual_done.py:10-11`.
- `bench/` and `tools/` imports are now layered in the current source audit,
  e.g. `tools/iccma2025_run_native.py` imports `argumentation.interop.iccma`
  and `argumentation.solving.solver`; `bench/asp_vs_sat.py` imports
  `argumentation.structured.aba.aba_asp` and
  `argumentation.structured.aspic.aspic_encoding`.

Recommended action: no action beyond the `.lp` comment.

### Untracked `scripts/` still contain old imports

Verdict: **DISCUSS**

Evidence:

- `git ls-files -- scripts` produced no tracked files; `git status --short --
  scripts` reports `?? scripts/`.
- The working tree nevertheless contains old imports:
  `scripts/probe_sensitivity_delta_sign.py:16-17` imports
  `argumentation.dung` and `argumentation.sensitivity`;
  `scripts/verify_sensitivity_expectations.py:8-9` imports the same old paths.

Recommended action: if these scripts are intended to become tracked or remain
usable as local utilities, update them to `argumentation.core.dung` and
`argumentation.gradual.sensitivity`. I am not classifying this as a PR blocker
because the files are untracked.

## 4. Tests for the breaking structure

### Structural coverage is present but indirect

Verdict: **DISCUSS**

Evidence:

- `tests/test_import_boundaries.py:12-27` AST-walks `src/argumentation/**/*.py`
  and checks import roots, not the exact subpackage layout.
- `tests/test_docs_surface.py:8-57` pins representative new dotted paths in
  README and architecture docs, including `argumentation.ranking.ranking`,
  `argumentation.gradual.gradual`,
  `argumentation.structured.aspic.subjective_aspic`, and
  `argumentation.probabilistic.epistemic`.
- Negative old-path assertions remain for the three explicitly allowed
  nonexistent modules:
  `tests/test_workstream_o_arg_dung_extensions_done.py:42`,
  `tests/core/test_dung_extensions_workstream.py:43`,
  `tests/test_dfquad_old_path_deleted.py:26`,
  `tests/test_workstream_o_arg_gradual_done.py:23`, and
  `tests/test_workstream_o_arg_vaf_ranking_done.py:39`.
- `tests/solving/test_iccma_cli.py` imports
  `from argumentation.solving import iccma_cli` and exercises CLI behavior, but
  it does not assert the installed console entry point resolves.
- Targeted structural/doc/CLI tests passed currently:
  `uv run pytest -q tests\test_docs_surface.py tests\test_import_boundaries.py tests\test_dfquad_old_path_deleted.py tests\solving\test_iccma_cli.py`
  -> `16 passed in 2.58s`.

Recommended action: optional hardening: add a tiny smoke test using
`importlib.metadata.entry_points()` for `iccma-cli` and a representative
`importlib.import_module("argumentation.core.dung")` / old-path
`ModuleNotFoundError` check. Existing coverage is probably enough for this
reorg, but the console-script resolution itself is not pinned by tests.

## 5. Collapsed `__init__.py`

### Documented break matches the removed public package attributes

Verdict: **OK**

Evidence:

- Pre-reorg `git show e79632c:src/argumentation/__init__.py` showed eager
  imports and `__all__` for 41 short module names.
- Current `src/argumentation/__init__.py` is exactly one docstring line:
  `"""Finite formal argumentation objects and algorithms."""`
- `CHANGELOG.md:15-18` documents that `import argumentation` no longer eagerly
  imports submodules and `argumentation.__all__` was removed.
- `CHANGELOG.md:40-94` gives the old-to-new table for every moved module and
  `CHANGELOG.md:96-98` states `solver_adapters` paths are unchanged.

Recommended action: no action.

## 6. Documentation accuracy

### Architecture docs match current structure and contract

Verdict: **OK**

Evidence:

- `docs/architecture.md:19-232` lists the current module groups by subpackage.
- `docs/architecture.md:236-254` describes the same layered architecture as
  `pyproject.toml:104-111`, including `interop` above the ABA/probabilistic/
  dynamics layer and `semantics` as the top layer.
- The two sanctioned exceptions in docs match config:
  `docs/architecture.md:257-263` and `pyproject.toml:113-116`.
- Targeted docs tests passed: `tests/test_docs_surface.py` included in the
  `16 passed` run above.

Recommended action: no action.

### README snippets use current import paths

Verdict: **OK**

Evidence:

- `README.md:72` starts the quick-start snippet with
  `from argumentation.core.dung import (...)`.
- `README.md:254` uses `from argumentation.ranking.ranking import
  categoriser_ranking`.
- `README.md:302` uses `from argumentation.probabilistic.probabilistic import
  (...)`.
- `README.md:500-505` documents the `iccma-cli` command, and
  `pyproject.toml:72` points the script to
  `argumentation.solving.iccma_cli:main`.

Recommended action: no action.

### Changelog table spot-check passes

Verdict: **OK**

Evidence:

- Ten sampled table targets from `CHANGELOG.md:40-94` exist at their new paths:
  `src/argumentation/core/dung.py`,
  `src/argumentation/structured/aspic/aspic_encoding.py`,
  `src/argumentation/structured/aba/aba_sat.py`,
  `src/argumentation/frameworks/setaf_io.py`,
  `src/argumentation/gradual/gradual.py`,
  `src/argumentation/ranking/ranking_axioms.py`,
  `src/argumentation/probabilistic/probabilistic_treedecomp.py`,
  `src/argumentation/interop/iccma.py`,
  `src/argumentation/solving/solver.py`, and
  `src/argumentation/semantics.py`.

Recommended action: no action.

## 7. Hatch build config

### Wheel ships encodings without duplicate-name warning

Verdict: **OK**

Evidence:

- `pyproject.toml:78-79` has only `packages = ["src/argumentation"]` under the
  wheel target; there is no `force-include` table (`Select-String '[tool.hatch'`
  only found wheel and sdist tables at `pyproject.toml:78` and `:81`).
- Current `uv build` output:
  `Successfully built dist\formal_argumentation-0.3.0.tar.gz` and
  `Successfully built dist\formal_argumentation-0.3.0-py3-none-any.whl`; no
  duplicate-name warning appeared.
- Current wheel listing includes all 10 encoding files:
  `argumentation/encodings/aba_admissible.lp`,
  `aba_com_incremental.lp`, `aba_complete.lp`, `aba_stable.lp`,
  `aspic_admissible.lp`, `aspic_complete.lp`, `aspic_stable.lp`,
  `dung_admissible.lp`, `dung_complete.lp`, `dung_stable.lp`.

Recommended action: no action.

## 8. Mechanical rewrite regressions

### One shipped non-Python comment escaped the rewrite

Verdict: **FIX**

Evidence:

- Same stale path as Check 3:
  `src/argumentation/encodings/aba_com_incremental.lp:6` names
  `argumentation.aba_asp.encode_aba_theory`.
- This is classic mechanical-rewrite fallout: the Python imports were rewritten,
  but a package data comment was outside the likely import-rewrite sweep.

Recommended action: update the comment to the new path. Search package data
files, not only `.py`, in the fix verification.

### No pass-body vestigial export tests remain

Verdict: **OK**

Evidence:

- `rg -n -F -- "pass" tests\structured\aba\test_aba_asp_differential.py
  tests\frameworks\test_adf_acceptance_condition_ast.py` returned no matches.
- The files named by the prompt were deleted from the old locations and are
  absent as vestigial stubs:
  `test_aba_asp_module_is_exported_from_package` in C6 and
  `test_adf_module_is_exported` in C3.

Recommended action: no action.

## 9. Other findings

### Current verification is green except for the stale shipped comment

Verdict: **OK**

Evidence:

- `uv run pyright src` currently reports `0 errors, 0 warnings, 0 informations`
  (plus a pyright upgrade notice).
- `uv run lint-imports` currently reports 2 kept, 0 broken.
- Targeted structural/docs/CLI tests: `16 passed in 2.58s`.
- Targeted ABA tests: `3 passed in 2.37s`.
- I did not run the full pytest suite in this review turn; I read the final
  verification report showing `2824 passed, 3 skipped, 1 xfailed`, and I ran the
  targeted tests above.

Recommended action: after fixing the `.lp` comment, rerun the old-path grep and
the normal lightweight gates (`uv run lint-imports`, `uv run pyright src`, and
the targeted docs/structural tests). A full suite is optional for a comment-only
fix, but acceptable as a final gate.

## Overall verdict

**NOT-YET**: one FIX-class finding remains:
`src/argumentation/encodings/aba_com_incremental.lp:6` still contains the old
shipped path `argumentation.aba_asp.encode_aba_theory`. The untracked
`scripts/` old imports are DISCUSS-class because they are not tracked PR
content.
