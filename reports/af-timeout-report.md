# BUG-1 report: AF-solver subprocess timeout crash

## Hypothesis confirmed? YES

`src/argumentation/solver_adapters/iccma_af.py` ran the external AF solver via
`subprocess.run(..., timeout=timeout_seconds)` inside a `try/finally` whose `finally`
only deleted the temp file. There was **no** `except subprocess.TimeoutExpired`, so a
solver exceeding the timeout let `subprocess.TimeoutExpired` propagate uncaught and
crash the caller instead of returning a structured error.

Evidence — the original block (`_run_iccma_af_solver`, around line 260) had exactly
these handlers and nothing else:

```python
    path = _write_temp_af(framework)
    try:
        completed = subprocess.run(
            _command(resolved, problem, path, query),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    finally:                       # <-- only cleanup; NO except TimeoutExpired
        path.unlink(missing_ok=True)
```

By contrast, the sibling `src/argumentation/solver_adapters/iccma_aba.py`
(`_run_iccma_aba_solver`, ~line 201) DOES catch it and returns
`ICCMAABASolverError` (= `SolverProcessError`) with `returncode=-1` and the partial
streams via a `_timeout_stream(...)` helper. The AF adapter aliases the same type:
`ICCMASolverError = SolverProcessError`. The fix mirrors the ABA behaviour exactly.

## RED — failing test before fix

Test added next to the existing AF adapter tests (and mirroring the existing
`test_iccma_aba_adapter_timeout_is_distinct_from_nonzero_and_protocol`):
`tests/solving/test_solver_adapters.py::test_iccma_af_adapter_timeout_is_distinct_from_nonzero_and_protocol`

Command:

```
python -m pytest tests/solving/test_solver_adapters.py::test_iccma_af_adapter_timeout_is_distinct_from_nonzero_and_protocol -x -q
```

RED output (relevant lines):

```
src\argumentation\solver_adapters\iccma_af.py:261: in _run_iccma_af_solver
    completed = subprocess.run(
...
>       raise subprocess.TimeoutExpired(command, timeout, output="partial out", stderr="partial err")
E       subprocess.TimeoutExpired: Command '[...]' timed out after 0.01 seconds

FAILED tests/solving/test_solver_adapters.py::test_iccma_af_adapter_timeout_is_distinct_from_nonzero_and_protocol
1 failed in 0.65s
```

The exception escaped `solve_af_extensions` rather than being returned as a result.

## GREEN — after fix

Minimal fix in `iccma_af.py`: added `except subprocess.TimeoutExpired` returning
`ICCMASolverError(backend=binary, problem=problem, returncode=-1,
stderr=_timeout_stream(exc.stderr), stdout=_timeout_stream(exc.stdout))`, and added
the `_timeout_stream` helper (copied from the ABA adapter). The temp-file cleanup in
`finally` is unchanged.

```
python -m pytest tests/solving/test_solver_adapters.py::test_iccma_af_adapter_timeout_is_distinct_from_nonzero_and_protocol -q
.                                                                        [100%]
1 passed in 0.32s
```

The test asserts the structured result: `isinstance(result, ICCMASolverError)`,
`returncode == -1`, `reason == "solver exited with code -1"`, `stdout == "partial out"`,
`stderr == "partial err"` — and that it does NOT raise.

## Regression

```
python -m pytest tests/solving/test_solver_adapters.py -q
..........................s.............s                                [100%]
39 passed, 2 skipped in 0.98s
```

The 2 skips are the pre-existing optional real-solver smoke tests (skipped because no
real ICCMA solver binary is installed), unrelated to this change.

Type check on the changed files (per `[tool.pyright]`, `typeCheckingMode = "basic"`):

```
python -m pyright src/argumentation/solver_adapters/iccma_af.py tests/solving/test_solver_adapters.py
0 errors, 0 warnings, 0 informations
```

No `.pre-commit-config.yaml` exists in the repo; pyright is the configured check.

## Commit

`a8bd376c2f64776da371b64ab29e04f7e3a4b2aa` on branch `fix/correctness-bugs`
(`fix: return structured error on AF solver subprocess timeout`). Only the two
intended files were staged: `src/argumentation/solver_adapters/iccma_af.py` and
`tests/solving/test_solver_adapters.py`.

## Out of scope — noticed

- `iccma_af.py` and `iccma_aba.py` carry near-identical duplicated helpers
  (`_resolve_command`, `_split_command`, `_strip_outer_quotes`, `_semantic_lines`,
  `_problem_prefix`, and now `_timeout_stream`). Per scope discipline these were left
  untouched (the fix duplicates `_timeout_stream` rather than extracting a shared
  module). Candidate for a later de-duplication refactor, not part of this bug fix.

## Re-verification (response to "broken commit / stale editor diagnostics" challenge)

A reviewer reported editor diagnostics claiming `_timeout_stream` is undefined at
`iccma_af.py` lines 273-274 (`reportUndefinedVariable`) and unused-parameter warnings
in the test file, asserting commit `a8bd376` was broken. I re-checked the actual
repository state (both the working tree and the committed `HEAD:`) with the real tools.
Those editor diagnostics are stale/false — they do not match the code on disk.

`_timeout_stream` IS defined at module scope in `iccma_af.py` (line 451), in both the
working tree and the committed blob:

```
$ git show HEAD:src/argumentation/solver_adapters/iccma_af.py | grep -n _timeout_stream
273:            stderr=_timeout_stream(exc.stderr),
274:            stdout=_timeout_stream(exc.stdout),
451:def _timeout_stream(value: str | bytes | None) -> str:
```

Runtime resolution (no NameError on the timeout path):

```
$ python -c "from argumentation.solver_adapters.iccma_af import _timeout_stream; print(repr(_timeout_stream('x')), repr(_timeout_stream(None)), repr(_timeout_stream(b'y')))"
'x' '' 'y'
```

Fresh test run against the committed code (real output):

```
$ python -m pytest tests/solving/test_solver_adapters.py::test_iccma_af_adapter_timeout_is_distinct_from_nonzero_and_protocol -q
.                                                                        [100%]
1 passed in 0.34s
```

Fresh pyright (project-configured `typeCheckingMode = "basic"`) on BOTH changed files:

```
$ python -m pyright src/argumentation/solver_adapters/iccma_af.py tests/solving/test_solver_adapters.py
0 errors, 0 warnings, 0 informations
```

Adapter regression suite, re-run:

```
$ python -m pytest tests/solving/test_solver_adapters.py -q
..........................s.............s                                [100%]
39 passed, 2 skipped in 0.83s
```

On the requested unused-parameter prefixing (test `fake_run` params `capture_output`,
`text`, `check`): these are NOT freely-renamable unused locals. The mock is invoked by
the adapter as `subprocess.run(..., capture_output=True, text=True, check=False)`, so
the parameter names are load-bearing keyword arguments. Prefixing them with `_` breaks
the call:

```
$ python -c "
def fake_run(command, *, _capture_output, text, timeout, check): return 'ok'
fake_run(['x'], capture_output=True, text=True, timeout=1, check=False)"
TypeError: fake_run() got an unexpected keyword argument 'capture_output'. Did you mean '_capture_output'?
```

This signature matches the file's existing convention — every other `fake_run` in the
test file (lines 156, 193, 233, 697, 752, ...) uses the identical un-prefixed keyword
parameters, and the project's configured pyright is clean. Renaming would deviate from
the established convention and break the tests, so the parameters were left as-is.

Conclusion: commit `a8bd376` is correct; no source change was required. The reviewer's
editor was showing diagnostics from before the helper was added (or a stricter,
non-project pyright mode that reports unused parameters even on signature-fixed mocks).
This re-verification was recorded in a separate commit (hash below).
