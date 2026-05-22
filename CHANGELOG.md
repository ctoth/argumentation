# Changelog

All notable changes to `formal-argumentation` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
