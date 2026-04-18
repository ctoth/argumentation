# Contributing

`argumentation` is the finite formal argumentation kernel extracted from
propstore. Contributions must keep that boundary intact.

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

Package code and tests must not import `propstore`.

Use `argumentation` for Dung abstract argumentation frameworks, ASPIC+
structured arguments, Cayrol-style bipolar argumentation frameworks, and
generic formal helper code. Do not add propstore storage, provenance, CEL,
worldline, sidecar, source workflow, or CLI code here.

## Citation Discipline

Formal behavior should be anchored to the relevant literature in docstrings,
tests, or docs. If implementation behavior intentionally diverges from a cited
definition, document the reason and add a focused test for that behavior.
