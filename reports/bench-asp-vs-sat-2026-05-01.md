# ASP vs Reference Benchmark Notes

Date: 2026-05-01

Harness:

```powershell
uv run python -m bench.asp_vs_sat --out reports/asp-vs-reference.csv
```

Current scope:

- ABA: compares `support_reference` and `asp` on synthetic flat ABA chains.
- ASPIC+: compares `materialized_reference` and `asp` on synthetic ASPIC+
  chains.

Interpretation caveat: the non-preferential ASPIC+ ASP backend now solves over
source-level premise/defeasible-rule selections. Preferential ASPIC+ still uses
the materialized projection fallback while last-link preference filtering is
ported to source-level ASP.

External systems were not installed in this repository. `bench/README.md`
records the manual status and the reason they are not pinned as dependencies.
