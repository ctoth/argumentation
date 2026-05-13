# Wave C1 — Spec: well-founded preprocessing + incremental CEGAR for ABA solving

You are a research subagent. Read-only on source; you may run things. You produce a report, not code. Working dir: `C:\Users\Q\code\argumentation`.

## Goal

Produce `reports/aba-incremental-spec.md` — an implementation-ready spec for two speedups to the library's flat (assumption-level) ABA solver, targeting the ABA ICCMA timeouts (the scout recon says 54-83 ABA rows time out at cap-100):

1. **Well-founded / grounded preprocessing for ABA** — the ABA analog of the AF grounded reduct that Wave A added for Dung AFs. Determine which assumptions are *necessarily accepted* and which are *necessarily rejected* under the semantics being solved, fix them, and reduce the ABA framework before the SAT/ASP solve. (For ABA this is roughly: the well-founded extension / the assumptions in every complete assumption-set.)
2. **Incremental solving for the ABA CEGAR loop** — the existing solver (the scout says `aba_sat.py` has `_sat_preferred_cegar_extension` and `AssumptionKernel._solve_selected`, `aba_asp.py` has a clingo path, commit `8ab2a6f` wired clingo) appears to do CEGAR. Determine whether it rebuilds the solver per iteration / per query, and specify how to make it reuse a single incremental solver (Z3 push/pop, or IPASIR-style assumptions, or clingo's incremental/multi-shot API) across CEGAR iterations and across related queries.

## Sources to read

- `papers/Lehtonen_2021_IncrementalASP_ABA.pdf` (arXiv:2108.04192 — ASPforABA, the ICCMA ABA-track winner; incremental-ASP CEGAR for ABA). Read it. Cite sections.
- Also relevant if you can get them (web): Lehtonen, Wallner & Järvisalo AAAI 2019 "Declarative Algorithms and Complexity Results for Assumption-Based Argumentation" (direct ASP encodings); their JAIR 2021 extended version. Cite what you actually read.
- The existing code: `src/argumentation/aba.py` (`ABAFramework`), `src/argumentation/aba_sat.py`, `src/argumentation/aba_asp.py`, `src/argumentation/aba_asp.py`'s clingo glue, `src/argumentation/solver_adapters/` (clingo adapter). Report exactly what's there: does it materialize the Dung AF? does it precompute minimal supports? is there CEGAR? is the solver rebuilt each iteration? what semantics have which path (SAT vs ASP)?
- `notes/graph-theory-recon-codebase-2026-05-12.md` (the scout's recon — section on ABA/construction).
- `reports/graph-speedup-wave-a-preprocessing.md` (the AF grounded-reduct precedent — the ABA preprocessing should mirror its API shape: a `simplify` returning a residual + fixed sets + a `lift`).
- `reports/scc-recursive-algorithm.md` and `reports/graph-speedup-wave-b2-scc-impl.md` (the SCC layer is outside the kernel — note from B2 that this shape is reusable for ABA).

## Deliver in the report

1. **Well-founded ABA preprocessing**: the exact definition of the set of assumptions to fix IN and to fix OUT, per semantics (which ABA semantics — complete, preferred, stable, grounded, ideal — does this soundly apply to? gate it like Wave A gated stage/admissible). How to compute it (algorithm, complexity). How the residual ABA framework is formed and how a solution on the residual lifts back. Soundness argument / citation. Flag anything UNRESOLVED rather than guessing.
2. **Incremental CEGAR**: the current loop structure (cite `aba_sat.py` line numbers), where it rebuilds vs could reuse, the exact change to make it incremental (which solver API), and whether the same incremental solver can be reused across multiple queries on the same ABA framework (DC/DS for different assumptions). Expected win.
3. **What to keep flat / not touch**: anything in the ABA path that should be left alone.
4. **Test oracle**: the existing ABA tests + the existing flat ABA solver as the differential oracle (`solver_differential.py` exists per the recon). Spell out the equivalence the coder must assert.
5. **Effort estimate** and a recommended split (one coder, or two).

## Hard rule

Don't guess. Every algorithm step traces to a source you read (paper section or code file:line). Unresolved steps → flag them for the coder to settle against the oracle, don't invent.
