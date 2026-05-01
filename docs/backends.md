# Backend Selection

The default backend rule is implemented in `argumentation.backends`.

```python
default_backend(semantics, theory_size, has_preferences, weakest_link)
```

Current rule:

```text
if weakest_link:                       materialized_reference
if semantics == "grounded":            asp
if theory_size > 30 and has_clingo():  asp
if has_z3():                           sat
else:                                  materialized_reference
```

`has_clingo()` accepts either a `clingo` executable on `PATH` or an installed
Python `clingo` package, which the subprocess adapter invokes as
`python -m clingo`.

Users can still pass an explicit `backend=` argument to the solver entry points.
The selection helper is a policy function, not a forced dispatch layer.

Debugging clingo programs:

1. Re-run the query with the same facts and semantics.
2. Inspect `metadata["stdout"]` or `metadata["stderr"]` on backend failures.
3. For reducer work, write the generated facts and packaged `.lp` module to a
   standalone program and run `uv run python -m clingo program.lp 0`.
