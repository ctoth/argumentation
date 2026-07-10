# Changelog

All notable changes to `formal-argumentation` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `GradualConvergenceError`, carrying the original `GradualStrengthResult`, is
  raised when explanation, contestation, revised-impact, Shapley-impact, or
  attack-sensitivity APIs would otherwise present a non-converged iterate as a
  final value.
- `OptionalDependencyUnavailable` distinguishes a genuinely absent optional
  Python package from solver invariant and implementation failures.

### Removed

- `iterated_graded_ranking` — removed because the exported implementation was
  not the Grossi-Modgil iterated graded semantics its name claimed.
- `argumentation.solving.backends` — deleted. Capability detection and the
  `backend="auto"` routing it once exposed (`has_clingo` / `has_z3` /
  `default_backend` / `backend_choice_reason`) are folded into
  `argumentation.solving.solver` (`_has_clingo()` plus the per-call `_auto_*`
  resolvers). Import errors fail cleanly with `ModuleNotFoundError`.
- The CNF apparatus in `argumentation.solving.sat_encoding` — removed. The
  module now only exposes `sat_extensions`, a scan-based enumerator that routes
  to the native Dung/SCC machinery; there is no longer a solver-independent
  Boolean-per-argument CNF encoding.

### Changed

- Discussion, burden, Tuple*, h-Categoriser, and counting rankings now implement
  their cited recurrences and comparison domains rather than scalar or capped
  heuristic substitutes.
- Structured naive semantics uses the full pre-preference attack relation.
  Stage, stage2, and CF2 now reject frameworks carrying distinct attack and
  defeat relations because their cited definitions require one relation;
  ordinary Dung and identical-relation frameworks are unchanged.
- Both compact and numeric ABA parsers reject repeated contrary declarations,
  including textually identical repeats, and identify the duplicated
  assumption and later source line.
- `argumentation.probabilistic.probabilistic_treedecomp` was split into three
  modules: `probabilistic_treedecomp_construction` (min-degree treewidth,
  tree-decomposition, nice-tree-decomposition), `probabilistic_grounded_td`
  (the adapted grounded edge-tracking `exact_dp` route), and
  `probabilistic_paper_td` (paper-faithful Popescu & Wallner). The old facade
  path raises `ModuleNotFoundError`.

### Fixed

- ADF link classification now follows acceptance-condition behavior over every
  assignment of the other parents, making it invariant under Boolean syntax.
- Solver entry points convert only typed optional-dependency absence to
  `SolverUnavailable`; SAT/ABA invariant `RuntimeError`s retain their original
  traceback and are not retried or mislabeled as missing Z3.
- High-level gradual APIs and derived impact calculations no longer discard
  convergence metadata.

### Documentation

- Added a `docs/` landing page, executable examples, and contributor-facing
  performance-research guidance for solver, routing, benchmark, and profiling
  work.
- Refreshed gap, backend, ICCMA, and SETAF documentation references after the
  layered 0.3.0 package and test layout changes.

## [0.3.0] - 2026-05-22

### Changed — BREAKING

The package was reorganized from a flat module layout (56 modules in one
directory) into layered subpackages. **Every import path changed.** The
distribution name (`formal-argumentation`) and the import root (`argumentation`)
are unchanged; only the dotted paths of individual modules changed.

- `import argumentation` no longer eagerly imports submodules, and
  `argumentation.__all__` was removed. Import the specific module you need by
  its new layered path (see the table below).
- The `iccma-cli` console-script entry point moved from
  `argumentation.iccma_cli:main` to `argumentation.solving.iccma_cli:main`.
  The `iccma-cli` command itself is unchanged; the `python -m` form is now
  `python -m argumentation.solving.iccma_cli`.
- The architecture is now enforced by an `import-linter` layered contract
  (`pyproject.toml` `[tool.importlinter]`): a module may import only from its
  own layer or a strictly lower layer. `uv run lint-imports` checks the DAG.

There are no compatibility shims and no re-exports from the old paths. Old
imports fail cleanly with `ModuleNotFoundError`. Update every import to its new
path using the table below.

`argumentation.semantics` stays a top-level module; the `argumentation.encodings`
data directory and the `argumentation.solver_adapters` subpackage
(`clingo`, `iccma_aba`, `iccma_af`) are unchanged.

#### Complete old → new import-path table

| Old path | New path |
|---|---|
| `argumentation.dung` | `argumentation.core.dung` |
| `argumentation.labelling` | `argumentation.core.labelling` |
| `argumentation.preference` | `argumentation.core.preference` |
| `argumentation.solver_results` | `argumentation.core.solver_results` |
| `argumentation.preprocessing` | `argumentation.core.preprocessing` |
| `argumentation.scc_recursive` | `argumentation.core.scc_recursive` |
| `argumentation.bipolar` | `argumentation.core.bipolar` |
| `argumentation.accrual` | `argumentation.core.accrual` |
| `argumentation.aspic` | `argumentation.structured.aspic.aspic` |
| `argumentation.aspic_encoding` | `argumentation.structured.aspic.aspic_encoding` |
| `argumentation.aspic_incomplete` | `argumentation.structured.aspic.aspic_incomplete` |
| `argumentation.subjective_aspic` | `argumentation.structured.aspic.subjective_aspic` |
| `argumentation.datalog_grounding` | `argumentation.structured.aspic.datalog_grounding` |
| `argumentation.aba` | `argumentation.structured.aba.aba` |
| `argumentation.aba_sat` | `argumentation.structured.aba.aba_sat` |
| `argumentation.aba_asp` | `argumentation.structured.aba.aba_asp` |
| `argumentation.aba_decomposition` | `argumentation.structured.aba.aba_decomposition` |
| `argumentation.aba_incremental` | `argumentation.structured.aba.aba_incremental` |
| `argumentation.aba_preprocessing` | `argumentation.structured.aba.aba_preprocessing` |
| `argumentation.aba_route_policy` | `argumentation.structured.aba.aba_route_policy` |
| `argumentation.aba_telemetry` | `argumentation.structured.aba.aba_telemetry` |
| `argumentation.adf` | `argumentation.frameworks.adf` |
| `argumentation.setaf` | `argumentation.frameworks.setaf` |
| `argumentation.setaf_io` | `argumentation.frameworks.setaf_io` |
| `argumentation.caf` | `argumentation.frameworks.caf` |
| `argumentation.vaf` | `argumentation.frameworks.vaf` |
| `argumentation.vaf_completion` | `argumentation.frameworks.vaf_completion` |
| `argumentation.partial_af` | `argumentation.frameworks.partial_af` |
| `argumentation.practical_reasoning` | `argumentation.frameworks.practical_reasoning` |
| `argumentation.gradual` | `argumentation.gradual.gradual` |
| `argumentation.dfquad` | `argumentation.gradual.dfquad` |
| `argumentation.equational` | `argumentation.gradual.equational` |
| `argumentation.gradual_principles` | `argumentation.gradual.gradual_principles` |
| `argumentation.llm_surface` | `argumentation.gradual.llm_surface` |
| `argumentation.sensitivity` | `argumentation.gradual.sensitivity` |
| `argumentation.ranking` | `argumentation.ranking.ranking` |
| `argumentation.ranking_axioms` | `argumentation.ranking.ranking_axioms` |
| `argumentation.weighted` | `argumentation.ranking.weighted` |
| `argumentation.matt_toni` | `argumentation.ranking.matt_toni` |
| `argumentation.probabilistic` | `argumentation.probabilistic.probabilistic` |
| `argumentation.probabilistic_components` | `argumentation.probabilistic.probabilistic_components` |
| `argumentation.probabilistic_treedecomp` | `argumentation.probabilistic.probabilistic_treedecomp` |
| `argumentation.epistemic` | `argumentation.probabilistic.epistemic` |
| `argumentation.enforcement` | `argumentation.dynamics.enforcement` |
| `argumentation.dynamic` | `argumentation.dynamics.dynamic` |
| `argumentation.af_revision` | `argumentation.dynamics.af_revision` |
| `argumentation.approximate` | `argumentation.dynamics.approximate` |
| `argumentation.optimization` | `argumentation.dynamics.optimization` |
| `argumentation.iccma` | `argumentation.interop.iccma` |
| `argumentation.af_sat` | `argumentation.solving.af_sat` |
| `argumentation.sat_encoding` | `argumentation.solving.sat_encoding` |
| `argumentation.backends` | `argumentation.solving.backends` |
| `argumentation.solver` | `argumentation.solving.solver` |
| `argumentation.solver_differential` | `argumentation.solving.solver_differential` |
| `argumentation.iccma_cli` | `argumentation.solving.iccma_cli` |
| `argumentation.semantics` | `argumentation.semantics` (unchanged — top-level module) |

The `argumentation.solver_adapters.clingo`, `argumentation.solver_adapters.iccma_aba`,
and `argumentation.solver_adapters.iccma_af` paths are unchanged.

[0.3.0]: https://github.com/ctoth/argumentation/releases/tag/v0.3.0
