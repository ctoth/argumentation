# Architecture

`argumentation` is a finite, formal argumentation kernel. The library owns
data types and algorithms over argumentation frameworks. It does not own
application-level concepts (storage, persistence, schedulers, application
CLIs) — see [Non-goals](#non-goals).

The distribution name is `formal-argumentation`; the import root is
`argumentation`. The package is organized into layered subpackages. The
module catalogue below is grouped by subpackage; the
[Layered architecture](#layered-architecture) section states the import DAG
and the `import-linter` contract that enforces it. Per-family deep dives live
in dedicated docs (see [See also](#see-also)).

## Modules

### `core/` — Dung, labelling, preference, dispatch primitives

- `argumentation.core.dung` — Dung 1995 abstract argumentation frameworks and
  extension semantics. Core: grounded, complete, preferred, stable.
  Extended: naive, semi-stable (Caminada 2011), stage, CF2 (Gaggl &
  Woltran 2013), stage2, eager, ideal (Dung, Mancarella & Toni 2007), and
  prudent-semantics helpers.
- `argumentation.core.labelling` — Three-valued IN / OUT / UNDEC labelling and
  the extension-to-labelling bridge used by accrual and quantitative
  services.
- `argumentation.core.preference` — Strict-partial-order helpers and elitist /
  democratic preference comparisons (Modgil & Prakken 2018 Def 19).
- `argumentation.core.bipolar` — Cayrol-style bipolar argumentation frameworks
  with derived defeats and d/s/c-admissibility semantics.
- `argumentation.core.accrual` — Prakken-style weak/strong applicability
  helpers and same-conclusion accrual envelopes.
- `argumentation.core.preprocessing` — Framework-simplification helpers shared
  by the solver and encoding layers.
- `argumentation.core.scc_recursive` — SCC-recursive extension computation
  shared by the Dung semantics.
- `argumentation.core.solver_results` — Shared result dataclasses
  `SolverUnavailable`, `SolverProcessError`, `SolverProtocolError`.
- `argumentation.semantics` — Generic set-returning semantics dispatch
  over argumentation-owned Dung, bipolar, and partial-AF dataclasses. This is
  a single top-level module, not a subpackage; it is the topmost layer.

### `structured/aspic/` — ASPIC+ structured argumentation

- `argumentation.structured.aspic.aspic` — ASPIC+ literals, rules,
  premise/strict/defeasible arguments, attacks, defeats, and CSAF
  construction (Modgil & Prakken 2018).
- `argumentation.structured.aspic.aspic_encoding` — Deterministic ASP-style
  fact encoding of ASPIC+ theories (Lehtonen, Niskanen & Järvisalo 2024) and
  a typed grounded query surface with a backend-dispatch entry point
  (`solve_aspic_with_backend`).
- `argumentation.structured.aspic.aspic_incomplete` — ASPIC+ reasoning with
  optional ordinary premises by exact completion enumeration; classifies a
  query as `stable`, `relevant`, `unknown`, or `unsupported`.
- `argumentation.structured.aspic.subjective_aspic` — Wallner-style value
  filtering helpers for ASPIC+ subjective knowledge bases and defeasible
  rules.
- `argumentation.structured.aspic.datalog_grounding` — Grounding of Gunray
  `DefeasibleTheory` instances into propositional ASPIC+ via
  `ground_defeasible_theory(theory) -> GroundedDatalogTheory`. Requires
  the `[grounding]` extra. Consumes Gunray rather than redefining the
  defeasible-theory schema; Diller (2025) Definition 12 NAP analysis is
  not implemented (see `gaps.md`).

### `structured/aba/` — assumption-based argumentation

- `argumentation.structured.aba.aba` — Flat ABA and ABA+ frameworks over
  ASPIC literals, with constructor-level rejection of non-flat frameworks via
  `NotFlatABAError` and preference-aware attack reversal (Bondarenko et
  al. 1997; Čyras & Toni 2016).
- `argumentation.structured.aba.aba_asp` — Clingo-backed flat ABA extension
  queries encoding `ABAFramework` into deterministic ASP facts. Requires the
  `[asp]` extra. ABA+ ASP is not yet implemented.
- `argumentation.structured.aba.aba_sat` — Pure-Python (no Z3) task-directed
  support-mask SAT enumeration for flat ABA stable, complete, and preferred
  extensions.
- `argumentation.structured.aba.aba_decomposition` — SCC-style decomposition
  planning for ABA preferred-extension SAT enumeration.
- `argumentation.structured.aba.aba_incremental` — Incremental multi-shot ABA
  solving with clingo, plus an incremental-telemetry record.
- `argumentation.structured.aba.aba_preprocessing` — Flat-ABA simplification
  and grounded-reduct helpers.
- `argumentation.structured.aba.aba_route_policy` — Shape-driven route policy
  for choosing the sparse-narrow native SAT path.
- `argumentation.structured.aba.aba_telemetry` — Structural telemetry keys and
  derivations for ABA frameworks.

### `frameworks/` — specialized framework families

- `argumentation.frameworks.adf` — Abstract dialectical frameworks with typed
  acceptance-condition ASTs, three-valued operator semantics, structural
  link classification, and Dung bridges (Brewka & Woltran 2010; Brewka et
  al. 2013).
- `argumentation.frameworks.setaf` — SETAFs with collective attacks; grounded
  / complete / preferred / stable / semi-stable / stage semantics. See
  [`setaf.md`](setaf.md).
- `argumentation.frameworks.setaf_io` — ASPARTIX SETAF facts plus
  package-local compact SETAF parser/writer.
- `argumentation.frameworks.caf` — Claim-augmented AFs with inherited and
  claim-level views plus concurrence checks. See
  [`caf-semantics.md`](caf-semantics.md).
- `argumentation.frameworks.vaf` — Bench-Capon value-based argumentation
  frameworks, audience-specific defeat, and objective/subjective acceptance.
- `argumentation.frameworks.vaf_completion` — Value-based argument-chain
  construction, line classification, fact-first audiences, and two-value
  cycle completion helpers.
- `argumentation.frameworks.partial_af` — Partial argumentation frameworks
  with a three-way attack/ignorance/non-attack partition, completion
  enumeration, skeptical and credulous acceptance, and Sum / Max / Leximax
  merge operators.
- `argumentation.frameworks.practical_reasoning` — Atkinson and Bench-Capon
  AATS-backed AS1 practical arguments with CQ5, CQ6, and CQ11 objection
  generation.

### `gradual/` — gradual and weighted-bipolar semantics

- `argumentation.gradual.gradual` — Potyka-style quadratic-energy gradual
  strengths for weighted bipolar graphs, revised direct-impact attribution,
  and exact Shapley-style per-attack impact scores (Al Anaissy et al. 2024).
- `argumentation.gradual.gradual_principles` — Executable balance,
  directionality, and monotonicity checks over gradual strength functions.
- `argumentation.gradual.dfquad` — DF-QuAD aggregation/combination and
  strength propagation for quantitative bipolar graphs.
- `argumentation.gradual.equational` — Iterative equational fixpoint scoring
  schemes over weighted bipolar graphs.
- `argumentation.gradual.sensitivity` — Sensitivity analysis over gradual
  strength functions.
- `argumentation.gradual.llm_surface` — Dependency-free QBAF construction,
  Shapley-style explanation, and contestation witnesses for externally
  supplied argumentative LLM proposition graphs.

### `ranking/` — ranking-based semantics

- `argumentation.ranking.ranking` — Categoriser, Burden, and related
  ranking-based semantics over Dung AFs.
- `argumentation.ranking.ranking_axioms` — Executable ranking postulate checks
  over `RankingResult` outputs.
- `argumentation.ranking.weighted` — Dunne-style weighted argument systems
  with inconsistency-budget grounded semantics and deleted-attack witnesses.
- `argumentation.ranking.matt_toni` — Finite zero-sum game strengths for small
  AFs, with explicit intractability signalling for oversized matrices.

### `probabilistic/` — probabilistic and epistemic argumentation

- `argumentation.probabilistic.probabilistic` — Probabilistic argumentation
  frameworks (PrAFs) with primitive-relation uncertainty. Auto-routing
  strategy dispatcher across `deterministic`, `exact_enum`, `mc` (Li, Oren &
  Norman 2012), `exact_dp`, `paper_td` (Popescu & Wallner 2024), and
  DF-QuAD gradual semantics (Freedman et al. 2025).
- `argumentation.probabilistic.probabilistic_components` — Connected component
  decomposition over the primitive semantic dependency graph (Hunter &
  Thimm 2017, Proposition 18).
- `argumentation.probabilistic.probabilistic_treedecomp` — Min-degree
  treewidth estimation, tree decomposition computation,
  nice-tree-decomposition conversion, and an adapted grounded edge-tracking
  DP. Exact for the supported grounded route, but not the full Popescu &
  Wallner I/O/U witness-table DP. See `gaps.md` for the asymptotic
  limitation.
- `argumentation.probabilistic.epistemic` — Hunter-style epistemic language
  and belief distributions, labelled epistemic graphs with
  positive/negative/dependent labels, Potyka-style linear atomic constraints
  over probability labellings, and explicitly approximate belief-grid
  helpers. The Z3-backed surface in the package; install the `[z3]` extra.

### `dynamics/` — revision, enforcement, dynamic update

- `argumentation.dynamics.af_revision` — AF-level revision: kernel union
  expansion (Baumann 2015), revise-by-formula and revise-by-framework
  (Diller 2015), and grounded-argument-addition classification
  (`cayrol_2014_classify_grounded_argument_addition`, cited to Cayrol, de
  Saint-Cyr & Lagasquie-Schiex 2010, JAIR 38).
- `argumentation.dynamics.dynamic` — Dynamic AF update streams with a named
  recompute oracle, Alfano-Greco-Parisi-style single-attack incremental
  influenced/reduced-AF updates for grounded, complete, preferred, and
  stable semantics, and query results with explicit fallback metadata.
- `argumentation.dynamics.enforcement` — Brute-force minimal-change argument
  and extension enforcement with separate typed witnesses for unconstrained
  fixed-argument edits, conservative Baumann-style normal/strong/weak
  expansions, and explicit liberal source-to-target semantics changes.
  See `gaps.md` for the brute-force-vs-Baumann scope.
- `argumentation.dynamics.approximate` — k-stable semantics, bounded grounded
  iteration, and budgeted semi-stable approximation with exactness
  metadata.
- `argumentation.dynamics.optimization` — Optimisation helpers over AF
  enforcement and revision.

### `interop/` — exchange-format I/O

- `argumentation.interop.iccma` — ICCMA-style AF, ADF, and ABA I/O for interop
  with external argumentation solvers.

### `solving/` — solver orchestration and SAT encodings

- `argumentation.solving.solver` — Typed solver-result wrappers for Dung, ABA,
  ADF, and SETAF tasks. Entry points: `solve_dung_extensions /
  solve_dung_single_extension / solve_dung_acceptance`, `solve_aba_extensions
  / solve_aba_single_extension / solve_aba_acceptance`, `solve_adf_models`,
  `solve_setaf_extensions`. Configuration dataclasses: `ICCMAConfig`,
  `SATConfig`.
- `argumentation.solving.solver_differential` — Hosts
  `solver_capability_matrix` and task-aware comparison helpers for native,
  ICCMA, SAT, clingo, ADF, SETAF, and unsupported backend combinations.
- `argumentation.solving.backends` — Capability detection (`has_clingo`,
  `has_z3`), `default_backend(...)` policy, and `backend_choice_reason(...)`
  diagnostics. See [`backends.md`](backends.md).
- `argumentation.solving.sat_encoding` — Solver-independent CNF encoding of
  stable extensions, plus a reference scan-based enumerator.
- `argumentation.solving.af_sat` — Incremental Z3-backed SAT kernel for Dung
  AF acceptance with telemetry (`AfSatKernel`, `SATCheck`, `SATTraceSink`).
- `argumentation.solving.iccma_cli` — Argparse `main(argv)` for the ICCMA
  AF/ABA CLI, registered as the `iccma-cli` console script. Dispatches to
  `argumentation.solving.solver`.

### `solver_adapters/` — external-solver subprocess adapters

- `argumentation.solver_adapters.clingo` — Subprocess driver for
  ASPIC+/ABA/AF clingo encodings; parses `accepted_arg(...)` /
  `accepted_lit(...)` lines.
- `argumentation.solver_adapters.iccma_aba` — ICCMA-protocol flat-ABA solvers.
- `argumentation.solver_adapters.iccma_af` — ICCMA-protocol AF solvers, with
  typed DC/DS/SE output parsing.

### `encodings/` — prebuilt clingo encodings

- `argumentation.encodings/` — Prebuilt clingo `.lp` modules
  (admissible / complete / stable for AF, ASPIC+, and ABA) shipped in the
  wheel and concatenated with facts by the clingo subprocess adapter.

## Layered architecture

The package is partitioned into layers. A module may import only from its own
layer or a strictly lower layer; an upward import is forbidden. From the base
upward:

1. **`core`** — `dung`, `labelling`, `preference`, `bipolar`, `accrual`,
   `preprocessing`, `scc_recursive`, `solver_results`. Depends on nothing
   else in the package.
2. **`structured.aspic`, `frameworks`, `gradual`, `ranking`** — framework
   families built directly on `core`. These four are siblings; `gradual` and
   `ranking` are additionally constrained to be independent of each other.
3. **`structured.aba`, `probabilistic`, `dynamics`** — built on `core` and
   the layer-2 families.
4. **`interop`** — exchange-format I/O over the framework layers.
5. **`solver_adapters`** — external-solver subprocess adapters.
6. **`solving`** — solver orchestration (`solver`, `solver_differential`,
   `backends`, `sat_encoding`, `af_sat`, `iccma_cli`).
7. **`semantics`** — the topmost generic dispatcher.

The DAG is enforced mechanically by `import-linter`. The
`[tool.importlinter]` contracts in `pyproject.toml` declare a `layers`
contract (base `argumentation.core` up to `argumentation.semantics`) and an
`independence` contract pinning `argumentation.gradual` and
`argumentation.ranking` apart. `uv run lint-imports` checks both; an upward
import fails CI.

Two function-local imports are sanctioned exceptions, listed in the
contract's `ignore_imports`:

- `argumentation.structured.aspic.aspic_encoding -> argumentation.solver_adapters.clingo`
- `argumentation.structured.aba.aba_asp -> argumentation.solver_adapters.clingo`

Both are deferred (function-local) imports of the optional clingo subprocess
adapter, used only when the `[asp]` extra is installed. They are deliberate
and explicitly whitelisted; no other upward import is permitted.

## Backend policy

Pure-Python algorithms are the reference implementation. Dung extension
*enumeration* has one package-owned execution path: finite set enumeration
in `argumentation.core.dung`, with `argumentation.core.labelling` used by the
semantic implementations that require labelling projections.

`argumentation.solving.solver.solve_dung_extensions` exposes that path
through the backend name `native`. Other extension-enumeration backend names
return `SolverUnavailable`; this includes the deleted `argumentation.dung_z3`
module name. `backend="iccma"` is supported only for single-extension and
acceptance tasks (one ICCMA witness is not full enumeration).

ABA, ADF, SETAF, and ASPIC+ have their own native execution paths through
`argumentation.solving.solver`; the SAT backend for AFs uses
`argumentation.solving.af_sat` and the ASP backends for ABA / ASPIC+ route
through `argumentation.structured.aba.aba_asp` /
`argumentation.structured.aspic.aspic_encoding`. The `default_backend(...)`
policy function in `argumentation.solving.backends` picks among these without
forcing dispatch — see [`backends.md`](backends.md) for the rule body and the
canonical backend-string set.

## Solver contracts

Solver calls are separated by task result type:

- `ExtensionEnumerationSuccess` — complete extension enumeration.
- `SingleExtensionSuccess` — zero or one witness extension.
- `AcceptanceSuccess` — credulous or skeptical acceptance plus any
  backend-supplied witness or counterexample.

unsupported combinations return typed unavailable results before subprocess
invocation. `argumentation.solving.solver_differential` hosts
`solver_capability_matrix`, the package-owned record of which combinations
are live for native, ICCMA, SAT, clingo, ADF, SETAF, and unsupported backend
combinations.

ICCMA subprocess integration is intentionally routed through task-specific
surfaces. Full enumeration callers use native enumeration; single-extension
and acceptance callers can use ICCMA subprocesses through
`ICCMAConfig(...)`. Optional smoke-test binaries are named by the
environment variables `ICCMA_AF_SOLVER`, `ICCMA_ABA_SOLVER`, and
`ASPFORABA_SOLVER`, which the optional smoke tests in
`tests/solving/test_solver_adapters.py` read before constructing explicit
adapter calls or an `ICCMAConfig`. The `solver_adapters` package itself does
not read environment variables.

External callers supply already-projected frameworks, theories, or benchmark
manifests and consume package result objects; this package does not own caller
identity, storage, merge policy, provenance, or rendering policy.

## Z3 usage

`z3-solver` is an optional package dependency (the `[z3]` extra) and a
development dependency for tests; it is not used for Dung extension
enumeration. The Z3-backed package surfaces are:

- `argumentation.probabilistic.epistemic.constraints_satisfiable` /
  `constraints_entail` — linear real constraints over argument
  probability labels.
- `argumentation.solving.af_sat` — incremental SAT kernel for Dung AF
  acceptance.

Without `z3-solver`, those entry points raise a runtime error naming the
missing dependency (`epistemic.py`, `af_sat.py`).

## Probabilistic backend routing

`compute_probabilistic_acceptance` selects among **seven** strategies:
`deterministic`, `exact_enum`, `mc`, `exact_dp`, `paper_td`,
`dfquad_quad`, and `dfquad_baf`. The `auto` policy is:

1. If every argument and every relevant edge has a deterministic
   probability (within `1e-12` of 0 or 1), fall through to standard Dung
   evaluation in a single sampled world.
2. Otherwise, if the framework has at most thirteen arguments, enumerate
   induced Dung frameworks exactly (Li et al. 2012).
3. Otherwise, if the framework requires relation-rich worlds (explicit
   support relations, or `attacks != defeats`), use Monte Carlo with
   Agresti–Coull stopping.
4. Otherwise, estimate primal-graph treewidth via the min-degree
   heuristic. If treewidth is at most the cutoff (default twelve,
   `probabilistic.py:659`) and the query is credulous-grounded acceptance,
   run the adapted edge-tracking tree-decomposition DP.
5. Otherwise, fall back to Monte Carlo.

`paper_td` is the paper-faithful Popescu & Wallner (2024) Algorithm 1 for
exact extension-probability queries. It is opt-in only, distinct from
`exact_dp`, and rejects queries other than
`query_kind="extension_probability"`.

`dfquad_quad` and `dfquad_baf` are gradual semantics rather than Dung
semantics; they are never selected by `auto` and require explicit
selection. The `exact_dp` backend currently supports only credulous
grounded acceptance on defeat-only frameworks; calling it on richer
queries raises. Its current implementation tracks full edge sets and
forgotten arguments in table keys, so its asymptotic cost is not better
than brute-force enumeration; it is effective in practice for primal-graph
treewidth ≤ ~15. It is not the full Popescu & Wallner I/O/U witness-table DP.

## Generic semantics dispatch

`argumentation.semantics.extensions` returns extension sets for Dung,
bipolar, and partial AFs under their supported semantics names.
`accepted_arguments` derives credulous or skeptical accepted-argument
sets from that extension relation. The dispatcher is intentionally
limited to argumentation-owned dataclasses and does not accept
application records, storage rows, projection contexts, or presentation
flags.

## Invariants

- Frameworks, rules, arguments, and extensions are immutable frozen
  dataclasses over frozensets. Equality is structural.
- `PartialArgumentationFramework` enforces at construction that
  `attacks`, `ignorance`, and `non_attacks` are pairwise disjoint and
  partition A × A.
- `ExtensionRevisionState` rebuilds its ranking on construction so that
  every named extension has rank zero and every non-extension has a
  strictly greater rank.
- Conflict-freeness is checked against the pre-preference attack relation
  when present (Modgil & Prakken 2018 Def 14); defence is checked against
  defeats (Dung 1995 Def 6). `ArgumentationFramework` carries both as
  separate fields.

## Non-goals

The package does not own application provenance, source calibration,
subjective-logic opinion calculi, persistent storage, repository workflow,
or application-level CLI presentation. The `iccma-cli` console script is
a thin solver-protocol shim, not an application CLI. Those concerns
belong outside the formal kernel and must be projected into finite
argumentation objects before calling these algorithms.

See [`gaps.md`](gaps.md) for the canonical list of currently-known
limitations.

## Citation discipline

Every public algorithm names its source paper, definition, and (where
useful) page in its docstring. When an implementation deliberately
diverges from a cited definition, the divergence is documented and a
focused test pins the chosen behaviour.

## See also

- [`backends.md`](backends.md) — capability detection and backend
  selection rule, with the canonical backend-string set.
- [`gaps.md`](gaps.md) — currently-known limitations and non-goals.
- [`caf-semantics.md`](caf-semantics.md) — claim-augmented AF semantics
  and dispatcher.
- [`setaf.md`](setaf.md) — SETAF semantics and ASPARTIX I/O.
- [`iccma-data.md`](iccma-data.md) — multi-year ICCMA benchmark
  preparation tooling.
- [`iccma-2025-data.md`](iccma-2025-data.md) — ICCMA 2025 data and
  native runner.
- [`performance-research.md`](performance-research.md) — operational
  contracts, calibration, profiling, and experiment records for solver
  performance work.
- [`../CHANGELOG.md`](../CHANGELOG.md) — release history, including the
  0.3.0 layered-subpackage reorganization.
