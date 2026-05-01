# ASP vs Reference Benchmark Notes

Date: 2026-05-01

Harness:

```powershell
uv run python -m bench.asp_vs_sat --out out/asp-vs-reference.csv
```

Current scope:

- ABA: compares `support_reference` and `asp` on synthetic flat ABA chains.
- ASPIC+: compares `materialized_reference` and `asp` on synthetic ASPIC+
  chains.

Interpretation caveat: the current ASPIC+ ASP backend solves Dung semantics over
the materialized ASPIC+ projection. It validates the clingo backend surface and
semantics dispatch, but it is not the source-level Lehtonen assumption encoding
needed to reproduce the asymptotic scale claims from the workstream report.

External systems were not installed in this repository. `bench/README.md`
records the manual status and the reason they are not pinned as dependencies.
