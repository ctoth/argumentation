# Documentation Index

`argumentation` is a finite formal argumentation kernel. The public package
owns immutable framework objects, paper-cited algorithms, typed solver
boundaries, and benchmark tooling around those boundaries. It deliberately
does not own application storage, provenance systems, UI rendering, or
domain-specific workflow state.

Use this page as the stable map into the rest of the docs.

## Start here

| Need | Read |
|---|---|
| Package overview, install, and examples | [`../README.md`](../README.md) |
| Copy-pasteable current API examples | [`examples.md`](examples.md) |
| Layer contract and module catalogue | [`architecture.md`](architecture.md) |
| Solver backend strings and capability policy | [`backends.md`](backends.md) |
| Known limitations and closed historical gaps | [`gaps.md`](gaps.md) |
| Release migration notes | [`../CHANGELOG.md`](../CHANGELOG.md) |
| Contribution rules | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |

## Framework Families

The package surface is layered. Import concrete modules by their full
subpackage path; there are no compatibility re-exports from the old flat
layout.

| Family | Primary modules | Notes |
|---|---|---|
| Dung AFs | `argumentation.core.dung`, `argumentation.core.labelling`, `argumentation.semantics` | Grounded, complete, preferred, stable, semi-stable, stage, CF2, stage2, eager, ideal, and prudent helpers. |
| ASPIC+ | `argumentation.structured.aspic.aspic`, `argumentation.structured.aspic.aspic_encoding`, `argumentation.structured.aspic.aspic_incomplete` | Argument construction, attack/defeat computation, ASP-style facts, incomplete-premise reasoning. |
| ABA / ABA+ | `argumentation.structured.aba.aba`, `argumentation.structured.aba.aba_sat`, `argumentation.structured.aba.aba_asp`, `argumentation.structured.aba.aba_incremental` | Flat ABA reference algorithms, task-directed SAT enumeration, optional clingo paths, incremental preferred solving. |
| Specialized AFs | `argumentation.frameworks.adf`, `argumentation.frameworks.setaf`, `argumentation.frameworks.caf`, `argumentation.frameworks.vaf`, `argumentation.frameworks.partial_af` | ADF, collective attack, claim-augmented, value-based, and partial-AF semantics. |
| Quantitative | `argumentation.gradual.*`, `argumentation.ranking.*`, `argumentation.core.bipolar` | Gradual strength, DF-QuAD, equational scoring, rankings, weighted systems, bipolar support. |
| Probabilistic | `argumentation.probabilistic.probabilistic`, `argumentation.probabilistic.probabilistic_treedecomp_construction`, `argumentation.probabilistic.probabilistic_grounded_td`, `argumentation.probabilistic.probabilistic_paper_td`, `argumentation.probabilistic.epistemic` | PrAF routing, exact enumeration, Monte Carlo, tree-decomposition routes, epistemic constraints. |
| Dynamics | `argumentation.dynamics.af_revision`, `argumentation.dynamics.dynamic`, `argumentation.dynamics.enforcement`, `argumentation.dynamics.approximate` | AF revision, update streams, brute-force enforcement oracle, bounded approximations. |

## Deep Dives

- [`caf-semantics.md`](caf-semantics.md) documents claim-augmented AF
  inherited and claim-level semantics.
- [`setaf.md`](setaf.md) documents SETAF semantics plus ASPARTIX and compact
  SETAF I/O.
- [`backends.md`](backends.md) documents the `native`, `iccma`, `sat`, `asp`,
  `aspforaba`, `support_reference`, and `materialized_reference` backend
  strings.
- [`iccma-data.md`](iccma-data.md) documents multi-year ICCMA benchmark data
  preparation.
- [`iccma-2025-data.md`](iccma-2025-data.md) documents the 2025 archive
  metadata, task matrix, and native benchmark runner.

## Solver And Benchmark Work

Solver work has two contracts:

1. Semantic correctness: the result must match the formal semantics or return
   a typed unavailable/error result.
2. Operational shape: performance work must state and test a measurable route,
   telemetry, solver-call, residual-size, calibration, or profiling invariant
   before a benchmark gate becomes the first signal.

The second contract matters because a benchmark timeout alone does not explain
whether the bottleneck moved. Add focused operational tests next to the solver
surface, use `tools/perf_calibrate.py` for opt-in wall-clock budgets, and use
`py-spy` against the real worker or solver process before discarding a route.

See [`performance-research.md`](performance-research.md) for the full workflow.

## Documentation Rules

- Cite current layered source paths, not the pre-0.3.0 flat paths. The
  changelog is the only place that should preserve the old import table.
- Keep "documented in notes" separate from "present and runnable in the repo."
  When a doc names a script or tool, verify the file exists.
- New public APIs need at least one README, architecture, or deep-dive mention
  plus a focused test when the docs make a behavioral promise.
