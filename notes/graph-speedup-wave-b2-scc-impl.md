# Wave B2 — SCC-recursive solving (complete/preferred/stable)

2026-05-12. Branch `experiment/graph-speedup-wave-a-preprocessing`.

## State
- Spec: `reports/scc-recursive-algorithm.md`. Implemented `src/argumentation/scc_recursive.py`:
  `scc_extensions(framework, semantics, decompose=True)` + DC/DS wrappers + `LAST_SOLVE` telemetry.
  Base `(AF,C)` solve done by brute force over SCC subsets per BG&G05 defs (resolved UNRESOLVED #1 this way —
  the Z3 finders can't enumerate and only expose force-OUT). DC/DS by enumeration (UNRESOLVED #2 deferred).
- Pipeline: simplify_af(semantics) → SCC-decompose residual → if ≤1 SCC flat base solve on residual → else GF recursion → lift_all.
- TODO: wire as default in solver._dung_extensions + sat_encoding.sat_extensions; tests/test_scc_recursive.py; full suite; bench; pyright; commit; report.

## Observations
- `sat_encoding.sat_extensions` for complete/preferred already just calls `dung.complete_extensions`/`preferred_extensions`; stable uses CNF enumerator.
- `af_sat.py` flat path = single-extension Z3 finders, not enumerators.
- dung._strongly_connected_components: Tarjan, recursive, sorts components (loses topo order) → wrote own topo sort.
- Baseline suite per Wave A report: `1 failed, 909 passed, 2 skipped` (--ignore tests/test_datalog_grounding.py); the 1 fail (test_kernel_ideal_extension_is_admissible) pre-existing.

## Progress 2026-05-12 (cont)
- WIRED: solver._dung_extensions + sat_encoding.sat_extensions route complete/preferred/stable through scc_extensions.
  Full suite after wiring: `1 failed, 909 passed, 2 skipped` — unchanged baseline. Good.
- Wrote tests/test_scc_recursive.py (hand battery + 180 random + recursion-path-exercised + fast-path/opt-out tests).
- Verified offline: 400 + 800 random AFs all match brute force for all 3 sems, both decompose modes; recursion path hit 474/2400.
- TODO: run test_scc_recursive.py; bench (before/after + no-help control); pyright on touched files; commit; report with hash.
- Touched files: src/argumentation/scc_recursive.py (new), src/argumentation/solver.py, src/argumentation/sat_encoding.py, tests/test_scc_recursive.py (new), notes + report.
