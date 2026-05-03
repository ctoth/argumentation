# Backend selection

`argumentation.backends` exposes capability detection and the default
backend selection policy. Solver entry points consume the chosen backend
string; `default_backend(...)` is a policy function, not a forced dispatch
layer — callers may always override with an explicit `backend=` argument.

## Capability detection

```python
from argumentation.backends import has_clingo, has_z3

has_clingo()   # True if `clingo` is on PATH or the `clingo` Python package is importable
has_z3()       # True if `z3-solver` is installed (the [z3] extra)
```

When `clingo` is available only as a Python package, the subprocess adapter
invokes it as `python -m clingo` (`solver_adapters/clingo.py:_resolve_command`).

## Default backend rule

```python
from argumentation.backends import default_backend, backend_choice_reason

backend: str = default_backend(
    semantics="grounded",
    theory_size=42,
    has_preferences=False,
    weakest_link=False,
)
```

Current rule (verified at `backends.py:23-33`):

```text
if weakest_link:                       materialized_reference
if semantics == "grounded":            asp
if theory_size > 30 and has_clingo():  asp
if has_z3():                           sat
else:                                  materialized_reference
```

Notes:

- The grounded branch returns `"asp"` unconditionally — it is **not**
  guarded by `has_clingo()`. A caller without clingo will receive
  `SolverUnavailable` at solve time, not at policy time.
- `has_preferences` is currently unused (`del has_preferences` at
  `backends.py:24`). It is reserved for future preference-aware routing.
- `weakest_link` is a boolean indicating ASPIC+ weakest-link defeat; when
  set it forces `materialized_reference`.

`backend_choice_reason(...)` returns a debug string with the inputs plus
observed `has_clingo`/`has_z3` values, useful for routing diagnostics.

## Backend identifiers

The canonical set of backend strings consumers should compare against:

| String | Where used | Implemented by |
|---|---|---|
| `"asp"` | ASPIC+ grounded path, large-theory routing | `solver_adapters/clingo.py` |
| `"sat"` | AF acceptance (Z3-backed) | `argumentation.af_sat` |
| `"materialized_reference"` | Pure-Python reference projection | `argumentation.aspic_encoding` |
| `"support_reference"` | ABA reference path (alias accepted by `aba_asp`) | `argumentation.aba_asp` |
| `"native"` | In-package native enumeration | `argumentation.solver` |
| `"iccma"` | External ICCMA-protocol subprocess | `solver_adapters/iccma_af`, `solver_adapters/iccma_aba` |
| `"aspforaba"` | Recognized but currently unimplemented; returns typed `SolverUnavailable` | `argumentation.solver` |

`aba_asp.run_aba_query` accepts `{"support_reference", "materialized_reference"}`
interchangeably for the reference path.

## Entry points that consume a backend choice

- `argumentation.aspic_encoding.solve_aspic_with_backend(theory, *, backend, ...)`.
- `argumentation.aba_asp.run_aba_query(framework, *, backend, ...)`.
- `argumentation.solver.solve_dung_extensions / solve_dung_single_extension /
  solve_dung_acceptance / solve_aba_extensions / solve_aba_single_extension /
  solve_aba_acceptance / solve_adf_models / solve_setaf_extensions`.

For ICCMA and SAT paths, the binary, timeout, and trace-sink configuration
flow through:

```python
from argumentation.solver import ICCMAConfig, SATConfig
```

## ICCMA subprocess adapters

`argumentation.solver_adapters/`:

| Adapter | Module | Supports |
|---|---|---|
| `clingo` | `solver_adapters/clingo.py` | Subprocess driver for ASPIC+/ABA/AF clingo encodings; parses `accepted_arg(...)` / `accepted_lit(...)` lines from stdout, deterministic sort |
| `iccma_aba` | `solver_adapters/iccma_aba.py` | ICCMA-protocol flat-ABA solvers (`SUPPORTED_ABA_PROBLEMS = DC-CO, DC-ST, DS-PR, DS-ST, SE-PR, SE-ST`) |
| `iccma_af` | `solver_adapters/iccma_af.py` | ICCMA-protocol AF solvers (`DC-CO, DC-ST, DC-SST, DC-STG, DS-PR, DS-ST, DS-SST, DS-STG, SE-PR, SE-ST, SE-SST, SE-STG, SE-ID`) |

The adapters do not read environment variables. ICCMA test fixtures read
`ICCMA_AF_SOLVER` and `ASPFORABA_SOLVER` / `ICCMA_ABA_SOLVER` (see
`tests/test_solver_adapters.py:565,829`) to locate solver binaries, then
construct an `ICCMAConfig(binary=...)` passed explicitly.

## SAT paths

The `"sat"` backend for Dung AFs uses `argumentation.af_sat`'s incremental
Z3 kernel:

- `AfSatKernel` — reusable Z3 solver bound to one AF, supporting per-task
  CNF assertion and retraction.
- `SATCheck` — typed result wrapper.
- `SATTraceSink` — opt-in telemetry hook for benchmark instrumentation.

`argumentation.aba_sat` is a separate, pure-Python (no Z3) bitmask-based
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
