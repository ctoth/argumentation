# ASP Backend Benchmarks

Run the in-repo benchmark harness with:

```powershell
uv run python -m bench.asp_vs_sat --out reports/asp-vs-reference.csv
```

The harness compares:

- flat ABA `support_reference` vs `asp`
- ASPIC+ `materialized_reference` vs `asp`

The `asp` backend invokes clingo through the packaged Python module when no
`clingo` executable is on `PATH`.

External systems from the workstream, including ASPforABA, ASPforASPIC, TOAST,
ANGRY, and ICCMA 2023 ASPIC+ instances, require separate local installation and
format adapters. They are not pinned as repository dependencies because the
available distributions are not clean Python package dependencies and several
are platform-sensitive on Windows.
