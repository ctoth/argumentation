# ASPIC Completeness Fixed-Point Log - 2026-07-22

Target architecture:
- `build_arguments_for()` returns the package-owned typed
  `ArgumentBuildResult`.
- Exact goal-directed construction is unbounded by default.
- An explicit depth bound reports `MAX_DEPTH_EXHAUSTED` plus cutoff literals;
  finite cycle rejection remains complete.

Forbidden surfaces:
- Bare `frozenset[Argument]` return from `build_arguments_for()`.
- Silent `max_depth=10` default.
- Compatibility wrappers, aliases, iterable facades, result-unwrapping helpers,
  or parallel legacy construction APIs.

Search gates:
- `rg -n 'max_depth: int = 10|def build_arguments_for' src/argumentation/structured/aspic/aspic.py`
- `rg -n 'build_arguments_for\(' src tests`

Runtime gates:
- `uv run pytest tests/structured/aspic/test_backward_chaining.py -q`
- `uv run pyright src/argumentation/structured/aspic/aspic.py`
- `uv run ruff check src/argumentation/structured/aspic/aspic.py tests/structured/aspic/test_backward_chaining.py`
- `uv run ruff format --check src/argumentation/structured/aspic/aspic.py tests/structured/aspic/test_backward_chaining.py`

## Iteration 1 - `build_arguments_for`

Slice read:
- `src/argumentation/structured/aspic/aspic.py`
- `tests/structured/aspic/test_backward_chaining.py`

Surfaces:
- `build_arguments_for() -> frozenset[Argument]`
  - Disposition: rewrite
  - Owner after cleanup: `ArgumentBuildResult` in `aspic.py`
  - Action: replace the owner return type and rewrite all callers directly.
  - Evidence: the bare set cannot distinguish no derivation from cutoff.
- `max_depth: int = 10`
  - Disposition: rewrite
  - Owner after cleanup: the same function's explicit optional resource limit
  - Action: default to `None`; reject negative explicit limits; record cutoffs.
  - Evidence: existing `in_progress` cycle detection already terminates finite
    grounded theories, while ten silently truncates exact semantics.
- Package test callers treating the result as a set
  - Disposition: rewrite
  - Owner after cleanup: `ArgumentBuildResult.arguments`
  - Action: use the typed result directly and assert completeness evidence.
  - Evidence: tests are boundary contracts for the changed public result.

Gate results:
- Pass: focused backward-chaining suite, 28 tests.
- Baseline failure: `uv run pyright src` reports one unchanged error at
  `src/argumentation/solving/solver.py:831`; inferred kwargs exclude the
  existing `engine: str` value. The controlling plan now assigns that unrelated
  correction to a separate package gate-repair slice and commit.
- Pass: changed-owner Pyright, zero errors.
- Pass: focused Ruff check.
- Pass: focused Ruff format check after formatting the two touched files.
- Pass: the silent `max_depth: int = 10` signature has zero hits.
- Pass: all remaining package `build_arguments_for()` callers consume either
  `.arguments` or explicit result evidence; no compatibility surface exists.

Commit:
- `063910e feat(aspic): expose bounded construction status`.

Next slice:
- Package-owned solver status vocabulary.

## Iteration 2 - `ASPICQueryResult.status`

Slice read:
- `src/argumentation/structured/aspic/aspic_encoding.py` status result and all
  producers
- `tests/structured/aspic/test_aspic_encodings.py` status assertions
- `tests/structured/aspic/test_aspic_asp_differential.py` status assertions

Surfaces:
- `ASPICQueryResult.status: str`
  - Disposition: rewrite
  - Owner after cleanup: `ASPICQueryStatus` in `aspic_encoding.py`
  - Action: type the field and every producer with the package enum.
  - Evidence: the package already owns the exact four-value vocabulary.
- String-valued test assertions
  - Disposition: rewrite
  - Owner after cleanup: `ASPICQueryStatus` identity assertions
  - Action: import the package enum directly and cover all four members.
  - Evidence: these tests are public result-boundary contracts.
- ABA query status vocabulary
  - Disposition: keep
  - Owner after cleanup: ABA package surface
  - Action: none; it is a distinct backend and outside this slice.

Gate results:
- Pass: focused ASPIC encoding/differential suite, 21 tests.
- Pass: changed-owner Pyright, zero errors.
- Pass: focused Ruff check and Ruff format check.
- Pass: no source/test constructor retains literal `success`,
  `unavailable_backend`, `backend_error`, or `protocol_error` status values.
- Pass: all existing result assertions use `ASPICQueryStatus` identity and the
  new process-failure regression proves `BACKEND_ERROR`.
- EOL note: `tests/structured/aspic/test_aspic_encodings.py` is tracked and
  checked out as CRLF (`git ls-files --eol` reports `i/crlf w/crlf`); preserve
  that existing policy and run diff whitespace checks with `cr-at-eol` rather
  than rewriting the whole file's line endings.

Commit:
- `25483a5 refactor(aspic): type query execution status`.

Next slice:
- Repair the pre-existing package-wide Pyright gate failure in a separate
  atomic commit.

## Iteration 3 - package solver formatting prerequisite

Slice read:
- `src/argumentation/solving/solver.py::_solve_sat_acceptance`
- `tests/solving/test_af_satcore_flat_routing.py`

Surfaces:
- Whole-file Ruff formatting diff around a one-line type repair
  - Disposition: rewrite
  - Owner after cleanup: repository-formatted `solver.py`
  - Action: restore the annotation before formatting, keep mechanical format
    changes separate, then reapply the annotation in the next commit.
  - Evidence: `uv run ruff format --check` would reformat the entire file.
- Unused `support_extensions as sat_aba_support_extensions` import
  - Disposition: delete
  - Owner after cleanup: none; no caller uses it
  - Action: remove the import exposed by the required focused Ruff gate.
  - Evidence: zero references beyond the import and Ruff F401.

Gate results:
- Pass: solver routing suite, 45 tests.
- Pass: focused Ruff check and Ruff format check after whole-file formatting.
- Expected: package Pyright reports exactly the one recorded heterogeneous
  `shared` mapping error, now at formatted line 835, and no additional errors.
- EOL note: `solver.py` is tracked and checked out as CRLF; the diff whitespace
  check passes with `cr-at-eol` while preserving that existing line-ending
  policy.

Commit:
- `51786f7 style(solving): format solver module`.

Next slice:
- Reapply the one-line package Pyright gate repair.

## Iteration 4 - package Pyright gate repair

Slice read:
- `src/argumentation/solving/solver.py::_solve_sat_acceptance`

Surfaces:
- Inferred heterogeneous `shared` kwargs dict
  - Disposition: rewrite
  - Owner after cleanup: the existing local kwargs mapping
  - Action: annotate it as `dict[str, object]` so the already-supported
    `engine: str` value is type-correct.
  - Evidence: package-wide Pyright reports exactly one error at the engine
    assignment; formatting and B2 source files are not causal.

Gate results:
- Pass: solver routing suite, 45 tests.
- Pass: package-wide Pyright, zero errors.
- Pass: focused Ruff check and Ruff format check.
- Pass: final source diff is the one planned annotation only.

Commit:
- `5233a27 fix(solving): type SAT finder kwargs`.

Next slice:
- Delete the obsolete Probe 7 red-contract scaffold exposed by the package full
  test gate.

## Iteration 5 - obsolete Probe 7 scaffold deletion

Slice read:
- `tests/structured/aba/test_aba_cadical2_eager_arc_contract.py`
- `experiments/2026-07-11-iccma2023-probe-7-cadical221-eager-arc.md`

Surfaces:
- Test import of `scripts.probe_iccma2023_cadical221_eager_arc`
  - Disposition: delete dead scaffold.
  - Classification: dead/test/scaffold surface.
  - Owner after cleanup: none; no diagnostic owner is valid for the frozen
    Probe 7 contract.
  - Action: delete the intentionally red preregistration test without adding a
    diagnostic implementation, alias, skip, or replacement.
  - Evidence: the recorded Probe 7 capability experiment proves pinned CaDiCaL
    2.2.1 cannot provide the frozen restart-statistic and signed-value
    semantics, so diagnostic implementation was deliberately abandoned.

Gate results:
- Pass: `uv run pytest --collect-only -q`, 3170 tests collected and no import
  error.
- Pass: no test or script path still references
  `probe_iccma2023_cadical221_eager_arc`.
- The first complete package test proceeded past collection and completed with
  3156 passed, 4 skipped, 1 xfailed, and 9 failed. Six failures are stale test
  monkeypatches of the earlier-deleted solver alias; one is a missing ignored
  paper-image fixture; two are a missing ignored CaDiCaL binary. None is caused
  by the Probe 7 deletion, and each is classified for a following slice or the
  final clean-worktree gate setup.

Commit:
- `test(aba): delete obsolete Probe 7 contract`.

Next slice:
- Rewrite stale enumeration instrumentation to patch its true ABA SAT owner.

## Iteration 6 - ABA solver-test formatting prerequisite

Slice read:
- `tests/structured/aba/test_aba.py`

Surfaces:
- Thirteen pre-existing Ruff formatting hunks around a two-line caller repair
  - Disposition: rewrite mechanically in a separate commit.
  - Owner after cleanup: the existing ABA solver test module.
  - Action: restore the two uncommitted owner-target changes, format the whole
    file, then reapply the two semantic lines in the next commit.
  - Evidence: `uv run ruff format --diff` reports 13 hunks unrelated to the
    monkeypatch target strings.

Gate results:
- Expected red: focused ABA solver tests report exactly the six
  already-classified stale monkeypatch failures and 24 passes; formatting adds
  no failure.
- Pass: focused Ruff check.
- Pass: focused Ruff format check.
- Pass: the current source diff is mechanical formatting only.

Commit:
- `style(aba): format solver tests`.

Next slice:
- Reapply the two-line true-owner monkeypatch repair.

## Iteration 7 - stale enumeration instrumentation repair

Slice read:
- `tests/structured/aba/test_aba.py`
- `src/argumentation/structured/aba/aba_sat.py::support_extensions`

Surfaces:
- Two monkeypatch targets naming the deleted solver alias
  - Disposition: rewrite the callers to the already-owned capability.
  - Classification: already-owned capability that must use its true owner
    directly.
  - Owner after cleanup:
    `argumentation.structured.aba.aba_sat.support_extensions`.
  - Action: patch the enumeration function at its defining module so the tests
    retain their no-enumeration assertion without a solver alias.
  - Evidence: `solver.py` calls the singular SAT APIs; the plural enumeration
    capability is defined only in `aba_sat.py`.

Gate results:
- Pass: focused ABA solver suite, 30 tests.
- Pass: focused Ruff check.
- Pass: focused Ruff format check.
- Pass: source diff is exactly two monkeypatch target strings.

Commit:
- `test(aba): patch enumeration owner directly`.

Next slice:
- Populate the verified ignored clean-worktree gate inputs and run all package
  gates.

## Iteration 8 - package-wide formatting prerequisite

Slice read:
- The exact output of `uv run ruff format --check .`.

Surfaces:
- 198 Python files predating the active Ruff format policy
  - Disposition: rewrite mechanically in one isolated repository-format commit.
  - Owner after cleanup: each existing module; no symbol or capability moves.
  - Action: run `uv run ruff format .` with a clean tracked worktree.
  - Evidence: the package-wide format gate named exactly 198 files and 96 files
    were already formatted.

Gate environment:
- The 13 required ignored paper page images and ignored CaDiCaL 2.2.1 binary
  were copied from the primary package checkout to matching clean-worktree
  paths.
- `C:\Users\Q\scoop\apps\mingw-winlibs\current\bin` is prepended only to test
  processes. The isolated CaDiCaL routing suite passes, 7 tests.

Gate results:
- Pass: package full suite, 3165 passed, 4 skipped, 1 xfailed.
- Pass: package-wide Pyright, zero errors.
- Pass: package-wide Ruff format check, 294 files formatted.
- Expected red: package-wide Ruff check retains exactly 19 non-format findings
  across production, tests, scripts, and tools; they are deferred to explicit
  classified repair slices.
- Pass: formatting changed only Python layout; no semantic repair is mixed into
  this slice.

Commit:
- `style: format package`.

Next slice:
- Classify and repair the 19 package-wide Ruff findings in atomic owner slices.
