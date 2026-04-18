# Contributing

`argumentation` is a finite formal argumentation kernel. Contributions must
keep that boundary intact.

## Development

Run checks from the repository root:

```powershell
uv run pyright src
uv run pytest -vv
```

The optional Z3 backend is tested by the default development environment. Keep
the base package free of mandatory runtime dependencies unless a formal kernel
module genuinely requires one.

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
