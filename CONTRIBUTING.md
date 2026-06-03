# Contributing

`argumentation` is a finite formal argumentation kernel. Contributions must
keep that boundary intact.

## Development

Run checks from the repository root:

```powershell
uv run pyright src
uv run lint-imports
uv run pytest -vv
```

The optional Z3 backend is tested by the default development environment. Keep
the base package free of mandatory runtime dependencies unless a formal kernel
module genuinely requires one.

## Solver Performance Work

Solver, routing, optimization, benchmark, and worker-process changes need an
operational contract before a full benchmark gate is used as the first signal.
Add at least one focused invariant that can fail early: bounded solver calls,
route selection, residual-size reduction, skipped bad path, telemetry shape,
or calibrated wall-clock budget.

Use `tools/perf_calibrate.py` and `tests/performance_contracts.py` for opt-in
wall-clock contracts. Deterministic route and telemetry contracts should run
normally. If a benchmark misses, use `py-spy` against the real hot worker or
solver process before declaring the experiment complete. A missed benchmark
without profiler-backed diagnosis is only "promotion no-go; diagnosis
incomplete."

See `docs/performance-research.md` for the full workflow.

## Package layout

`argumentation` is organized into layered subpackages. A module imports only
from its own layer or a strictly lower layer. From the base upward:

1. `argumentation.core` — Dung, labelling, preference, bipolar, accrual, and
   shared solver-result and preprocessing primitives.
2. `argumentation.structured.aspic`, `argumentation.frameworks`,
   `argumentation.gradual`, `argumentation.ranking` — framework families built
   on `core`. `gradual` and `ranking` are additionally independent of each
   other.
3. `argumentation.structured.aba`, `argumentation.probabilistic`,
   `argumentation.dynamics` — built on `core` and the layer-2 families.
4. `argumentation.interop` — exchange-format I/O.
5. `argumentation.solver_adapters` — external-solver subprocess adapters.
6. `argumentation.solving` — solver orchestration and SAT encodings.
7. `argumentation.semantics` — the topmost generic dispatcher.

A new module goes in the subpackage of its correct layer. `uv run lint-imports`
enforces the DAG via the `[tool.importlinter]` contract in `pyproject.toml`: an
upward import (a lower layer importing a higher one) fails CI. See
`docs/architecture.md` for the full layer contract and the two sanctioned
function-local `solver_adapters.clingo` exceptions.

## Boundary

Package code and tests must not import application-layer storage, provenance,
calibration, source workflow, worldline, sidecar, or CLI code.

Use `argumentation` for Dung abstract argumentation frameworks, ASPIC+
structured arguments, Cayrol-style bipolar frameworks, partial AFs, AF-level
revision, probabilistic AF kernels, gradual semantics, and generic formal
helper code.

Do not add application provenance, source calibration, subjective-logic
opinion calculus, persistent storage, repository workflow, or CLI ownership to
this package. Convert those concerns to finite formal argumentation objects at
the caller boundary.

## Citation Discipline

Formal behavior should be anchored to the relevant literature in docstrings,
tests, or docs. If implementation behavior intentionally diverges from a cited
definition, document the reason and add a focused test for that behavior.
