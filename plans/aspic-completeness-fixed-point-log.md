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
- Pending `refactor(aspic): type query execution status`.

Next slice:
- Repair the pre-existing package-wide Pyright gate failure in a separate
  atomic commit.
