# ICCMA 2023 ABA Stable Base-UNSAT Screen

Date: 2026-07-11

Status: measured on `main`; no production source change made.

Hypothesis: the ICCMA 2023 `aba_2000_0.3_10_10_0.aba` stable base formula is UNSAT before acyclicity, and the existing native CNF owner can prove that cheaply enough to skip the automatic Clingo solve within the five-second worker budget.

Single variable: omit only cycle-blocking constraints from the existing `_NativeSparseNarrowStableSolver` construction, then solve its completion/stability base CNF. Do not change clauses, solver engine, preprocessing, or timeout target.

Baseline:
- Automatic ASP/Clingo `SE-ST` result: `timeout>5.0`.
- Real-worker profile: 302 of 384 principal samples inside `clingo.Control.solve`.
- SAT ranked-closure alternative: `timeout>5.0`; 391 of 399 profile samples in ranked-constraint construction before Z3 solve.

Instrumentation:
- Script: `scripts/diagnose_aba_stable_base_formula.py`.
- It uses the existing native CNF stable owner and disables only elementary-cycle clauses for the diagnostic construction.
- It separately records build and base-solve wall time plus variables, clauses, recursive rules, and dependency edges.

Fast operational contract:
- The base screen must return a definite SAT/UNSAT result before the five-second worker budget.
- A result after the budget is an immediate promotion no-go even if it is semantically useful.

Metric result:
- Instance: `data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_0.aba`.
- Base status: `unsat`.
- Build: `0.558465s`.
- Solve: `46.121030s`.
- Shape: 600 assumptions, 2,000 atoms, 7,867 parsed rules, 47,648 variables, 64,928 clauses, 7,550 recursive rules, and 29,631 dependency edges.

Failure analysis:
- Compared against: the five-second Clingo baseline and SAT-ranked profile above.
- Dominant cost before: Clingo solver search.
- Dominant cost after: native CNF base UNSAT proof; construction is only about 1.2% of measured diagnostic time.
- Interpretation: the bottleneck stayed in solver search and expanded far beyond the gate. Removing acyclicity did not make the UNSAT proof cheap.
- Next target from evidence: a different UNSAT-capable engine or a smaller base encoding, but the current exact-convergence campaign may not widen because this is the second consecutive slice without a kept metric improvement.

Outcome: negative.

Decision: abandon the current native-CNF base-screen precheck. Do not put a 46-second precheck ahead of a five-second Clingo worker.

Generated diagnostics:
- No generated benchmark/profile output is committed.
- The reusable diagnostic script is committed; its measured output is recorded above.
