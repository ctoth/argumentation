# Backend selection

Solver entry points take a `backend=` string and route the query to a package
or external backend. There is no separate backend-policy module: capability
detection and auto-selection both live inside
`argumentation.solving.solver`. Callers either pass an explicit backend string
(`native`, `sat`, `asp`, `iccma`, …) or pass `backend="auto"` and let `solver`
choose per semantics/task.

## Capability detection

Capability detection is internal to `solver`; it is not surfaced as a public
function.

- clingo: `argumentation.solving.solver._has_clingo()` returns `True` when the
  `clingo` Python package is importable (`importlib.util.find_spec("clingo")`).
  It is consulted only by the `auto` ABA routing (see below).
- z3: the SAT kernel lazily imports `z3` through
  `argumentation.core.optional_deps.load_z3(feature)`, which raises a
  feature-specific `RuntimeError` ("… requires z3-solver") when the `[z3]`
  extra is not installed. There is no standalone `has_z3()` probe; an
  unavailable z3 surfaces as `SolverBackendUnavailable` at solve time.

When `clingo` is available only as a Python package, the subprocess adapter
invokes the current Python executable with `-m clingo`
(`solver_adapters/clingo.py:_resolve_command`).

## Auto selection (`backend="auto"`)

`backend="auto"` is the default on the `solve_dung_*` / `solve_aba_*` entry
points. The chosen string is resolved by per-call helpers in
`argumentation.solving.solver`:

| Entry point | Resolver | `auto` behaviour |
|---|---|---|
| `solve_dung_extensions` | `_auto_dung_extension_backend` | `sat` for `complete`/`stable`, else `native` |
| `solve_dung_single_extension` | `_auto_dung_single_backend` | `sat` for `complete`/`ideal`/`preferred`/`semi-stable`/`stable`/`stage`, else `native` |
| `solve_dung_acceptance` | `_auto_dung_acceptance_backend` | `sat` for `complete`/`ideal`/`semi-stable`/`stable`/`stage` and credulous/skeptical `preferred`, else `native` |
| `solve_aba_*` | `_auto_aba_backend` / `_auto_aba_backend_for_framework` | `asp` when `_has_clingo()` and the semantics/task qualifies; otherwise `sat` for `complete`/`preferred`/`stable`, else `native`. `_auto_aba_backend_for_framework` additionally promotes some single-extension shapes to `sat`. |

An explicit non-`auto` backend string is passed through unchanged by every
resolver, so `backend="native"` (etc.) always overrides the policy.

A query with `backend="auto"` end to end:

```python
from argumentation.core.dung import ArgumentationFramework
from argumentation.solving.solver import solve_dung_extensions

af = ArgumentationFramework({"a", "b"}, {("a", "b"), ("b", "a")})
result = solve_dung_extensions(af, semantics="stable", backend="auto")
# auto -> "sat" for stable; result is an ExtensionEnumerationSuccess
print(sorted(tuple(sorted(e)) for e in result.extensions))
# [('a',), ('b',)]
```

## Backend identifiers

The canonical set of backend strings consumers should compare against:

| String | Where used | Implemented by |
|---|---|---|
| `"asp"` | ASPIC+ grounded path, large-theory routing | `solver_adapters/clingo.py` |
| `"sat"` | AF acceptance (Z3-backed) | `argumentation.solving.af_sat` |
| `"materialized_reference"` | Pure-Python reference projection | `argumentation.structured.aspic.aspic_encoding` |
| `"support_reference"` | ABA reference path (alias accepted by `aba_asp`) | `argumentation.structured.aba.aba_asp` |
| `"native"` | In-package native enumeration | `argumentation.solving.solver` |
| `"iccma"` | External ICCMA-protocol subprocess | `solver_adapters/iccma_af`, `solver_adapters/iccma_aba` |
| `"aspforaba"` | Recognized as an unavailable direct backend; real ASPFORABA binaries are passed as `backend="iccma"` with `ICCMAConfig(binary=...)` | `argumentation.solving.solver`, `solver_adapters/iccma_aba.py` |

`aba_asp.run_aba_query` accepts `{"support_reference", "materialized_reference"}`
interchangeably for the reference path.

## Entry points that consume a backend choice

- `argumentation.structured.aspic.aspic_encoding.solve_aspic_with_backend(theory, *, backend, ...)`.
- `argumentation.structured.aba.aba_asp.run_aba_query(framework, *, backend, ...)`.
- `argumentation.solving.solver.solve_dung_extensions / solve_dung_single_extension /
  solve_dung_acceptance / solve_aba_extensions / solve_aba_single_extension /
  solve_aba_acceptance / solve_adf_models / solve_setaf_extensions`.

For ICCMA and SAT paths, the binary, timeout, and trace-sink configuration
flow through:

```python
from argumentation.solving.solver import ICCMAConfig, SATConfig
```

## ICCMA subprocess adapters

`argumentation.solver_adapters/`:

| Adapter | Module | Supports |
|---|---|---|
| `clingo` | `solver_adapters/clingo.py` | Subprocess driver for ASPIC+/ABA/AF clingo encodings; parses `accepted_arg(...)` / `accepted_lit(...)` lines from stdout, deterministic sort |
| `iccma_aba` | `solver_adapters/iccma_aba.py` | ICCMA-protocol flat-ABA solvers (`SUPPORTED_ABA_PROBLEMS = DC-CO, DC-ST, DS-PR, DS-ST, SE-PR, SE-ST`) |
| `iccma_af` | `solver_adapters/iccma_af.py` | ICCMA-protocol AF solvers (`DC-CO, DC-ST, DC-SST, DC-STG, DS-PR, DS-ST, DS-SST, DS-STG, SE-PR, SE-ST, SE-SST, SE-STG, SE-ID`) |

The adapters do not read environment variables. ICCMA smoke tests read
`ICCMA_AF_SOLVER` and `ASPFORABA_SOLVER` / `ICCMA_ABA_SOLVER` in
`tests/solving/test_solver_adapters.py` to locate optional real solver
binaries, then construct explicit adapter calls or an `ICCMAConfig(binary=...)`.

## SAT paths

The `"sat"` backend for Dung AFs uses `argumentation.solving.af_sat`'s incremental
Z3 kernel:

- `AfSatKernel` — reusable Z3 solver bound to one AF, supporting per-task
  CNF assertion and retraction.
- `SATCheck` — typed result wrapper.
- `SATTraceSink` — opt-in telemetry hook for benchmark instrumentation.

`argumentation.structured.aba.aba_sat` is a separate, pure-Python (no Z3) bitmask-based
support enumerator for ABA stable, complete, and preferred extensions. It is
not the `"sat"` backend choice; it is its own task-directed surface.

## Debugging

1. Re-run the query with the same facts and semantics. Backends are
   deterministic given the same inputs.
2. On backend failures:
   - `aba_asp` / `aspic_encoding` paths populate `metadata["stdout"]` and
     `metadata["stderr"]` on the result object.
   - `solver_results` dataclasses (`SolverProcessError`, `SolverProtocolError`)
     expose `.stdout` and `.stderr` directly as attributes.
3. For reducer work, write the generated facts and packaged `.lp` module
   under `argumentation.encodings/` to a standalone program and run
   `uv run python -m clingo program.lp 0`.
