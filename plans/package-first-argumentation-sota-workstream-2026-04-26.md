# Package-First Argumentation SOTA Workstream

Date: 2026-04-26

This workstream upgrades `argumentation` first, then integrates only stable package
surfaces into `propstore` after propstore's Semantic OS work reaches the projection
boundary described in `../propstore/plans/epistemic-os-workstreams-2026-04-25.md`.

The current package is a useful formal kernel, not state of the art. It already has
Dung AFs, ASPIC+ construction, probabilistic AFs, and an experimental tree
decomposition path. The next useful work is to make those surfaces broader, more
testable, and solver-friendly without making this package depend on propstore.

## Control Rules

- Red/green TDD is the control surface. Each implementation slice starts with a
  failing test commit, followed by the smallest implementation commit that makes
  the target tests pass.
- Commit frequently and mechanically: red test commit first, green implementation
  commit second, then no new slice while edited files remain uncommitted.
- After every green implementation commit, reread this workstream before reporting
  status or choosing the next slice. The next unchecked workstream item, not local
  momentum, controls what happens next.
- Do most work here first. `argumentation` must not import `propstore`, know about
  propstore storage, or know about Semantic OS situated assertions.
- Propstore integration is deferred until propstore has its assertion/projection
  boundary ready. Until then, propstore is a consumer we design for, not a codebase
  we change.
- Paper-derived implementation details require a paper-reading checkpoint. Existing
  `../propstore/papers/*/description.md`, `notes.md`, and `claims.yaml` may guide
  prioritization, but formal algorithms, complexity claims, and edge-case examples
  must be checked against page images before being treated as source of truth.
- Each paper-sensitive slice gets its own short reading log in the commit or PR
  notes: which paper pages were reread, what definitions/examples were implemented,
  what was intentionally left out, and what remains uncertain.
- If a paper reread changes the plan, update and commit this workstream before
  continuing implementation.
- Keep optional heavy dependencies optional. SAT, ASP, clingo, or external solver
  integration should live behind extras or adapters, with pure-Python references
  where feasible.
- Preserve package quality gates after each green slice:
  - `uv run pytest -q`
  - `uv run pyright src`
  - `git diff --check`
  - `git status --short`

## Propstore Boundary

Propstore's Semantic OS plan makes situated assertions the central carrier:
relations, role bindings, context, condition, and provenance. Argumentation is a
projection service over that substrate, not the owner of identity, storage, belief
revision, merge policy, or provenance.

That means this package should expose pure formal services:

- AF and ASPIC+ semantics over package-native data structures.
- Stable result objects that can carry external IDs without interpreting them.
- Optional explanation/witness structures that propstore can lift back to situated
  assertion IDs.
- Deterministic encodings and solver interfaces that propstore can call later.

It should not expose propstore-specific adapters until propstore's projection
boundary is ready.

## Phase 0: Baseline And Paper Gate

Goal: freeze the current baseline and make the next slices auditable.

Red tests:

- Add no behavior tests in this phase unless an existing advertised behavior is
  missing coverage.

Green work:

- Record the current semantic inventory and package boundaries.
- Add a paper-reading checklist for every paper-sensitive slice.
- Keep the baseline commands passing.

Acceptance:

- `uv run pytest -q`
- `uv run pyright src`

Paper leads already identified from `../propstore/papers`:

- Dung 1995 and Caminada 2006 for labellings, reinstatement, and semi-stable
  semantics.
- Dung, Mancarella, and Toni 2007 for ideal semantics.
- Gaggl and Woltran 2013 for CF2 semantics.
- Niskanen, Wallner, and Järvisalo 2020 for modern solver-backed AF reasoning.
- Fichte, Hecher, and Meier 2021 for decomposition-guided reductions.
- Lehtonen, Niskanen, and Järvisalo 2024 for preferential ASPIC+ via ASP.
- Diller, Strass, and Wyner 2025 for grounding rule-based argumentation with
  Datalog.
- Odekerken, Diller, and Borg 2025 for ASPIC+ under incomplete information.
- Popescu and Wallner 2024 for probabilistic constellation AF tree decomposition.
- Wallner 2024 and Prakken 2019 for value-based and accrual-aware ASPIC+.
- Dunne et al. 2011, Potyka 2018, and Al Anaissy et al. 2024 for weighted,
  gradual, and impact-explanation surfaces.
- Brewka and Woltran 2013 for ADFs as a later non-Dung generalization.

## Phase 1: Labellings And Missing Dung Semantics

Goal: make the abstract AF layer competitive enough to be a dependable substrate.

Target package surfaces:

- `argumentation.labelling`: immutable labelling model, status enum, conversion
  between labellings and extensions.
- `argumentation.dung`: semi-stable, stage, ideal, and CF2 extension APIs.
- `argumentation.semantics`: stable public names and result containers.

Red tests:

- Complete, grounded, preferred, and stable extension-to-labelling round trips.
- Semi-stable and stage behavior on frameworks where range maximization matters.
- Ideal semantics examples where preferred extensions disagree.
- CF2 examples with strongly connected components.
- Property tests on small AFs comparing brute-force definitions to package APIs.

Green work:

- Implement the labelling primitives first.
- Implement one semantics family per slice.
- Keep existing extension APIs intact unless a deliberate interface replacement is
  part of a red/green slice.

Acceptance:

- `uv run pytest -q tests/test_dung.py tests/test_labelling.py tests/test_semantics.py`
- `uv run pytest -q`
- `uv run pyright src`

Why first:

These semantics are directly useful to propstore later, but they are also package
fundamentals. They should not wait for propstore's Semantic OS migration.

## Phase 2: Solver-Ready Abstract AF Reasoning

Goal: support larger AFs and standard solver workflows without replacing the
reference algorithms.

Target package surfaces:

- Pure encoders for admissible, complete, grounded, preferred, stable,
  semi-stable, stage, ideal, and CF2 queries.
- Optional SAT/QBF/ASP backends behind adapter protocols.
- ICCMA-style input/output support if it stays cleanly package-local.

Red tests:

- For generated small AFs, solver-backed answers match brute-force reference
  semantics exactly.
- Encoders produce deterministic variables/clauses and stable external IDs.
- Backend absence is reported as a typed unavailable-backend result, not an import
  crash.

Green work:

- Start with a pure encoding object and a tiny in-process reference evaluator.
- Add optional backends only after the encoding contract is tested.
- Keep solver results liftable to package argument IDs.

Acceptance:

- `uv run pytest -q tests/test_solver_encoding.py tests/test_dung.py`
- `uv run pyright src`

Paper gate:

- Page-image reread for Niskanen et al. 2020 before claiming solver parity with
  µ-toksia-style behavior.
- Page-image reread for Fichte et al. 2021 before implementing treewidth-sensitive
  reductions.

## Phase 3: ASPIC+ Scalability And Incomplete Information

Goal: make ASPIC+ usable beyond tiny constructed theories while keeping semantics
faithful.

Target package surfaces:

- A direct ASPIC+ reasoning interface that can avoid materializing the full
  abstract AF when a backend supports it.
- Optional ASP/clingo or Datalog encoders behind adapters.
- Incomplete-information result types: stable, relevant, unknown, and witness
  metadata where supported.
- Preference strategy interfaces for last-link, weakest-link, value-based, and
  accrual-aware comparison.

Red tests:

- Small ASPIC+ theories where direct backend results match current constructed-AF
  results.
- Preference edge cases for strict vs defeasible rules.
- Incomplete-information examples with stable/relevant/unknown statuses.
- Backend absence tests.

Green work:

- First make the current ASPIC+ construction easier to test through stable
  intermediate objects.
- Add direct encodings only after equivalence tests exist.
- Treat weakest-link, accrual, and value-based behavior as separate slices.

Acceptance:

- `uv run pytest -q tests/test_aspic.py tests/test_aspic_encodings.py`
- `uv run pyright src`

Paper gate:

- Page-image reread for Lehtonen et al. 2024 before implementing preferential
  ASPIC+ ASP encodings or quoting scale claims.
- Page-image reread for Diller et al. 2025 before implementing Datalog grounding.
- Page-image reread for Odekerken et al. 2025 before implementing incomplete
  ASPIC+ status algorithms.

## Phase 4: Probabilistic AF Tree Decomposition

Goal: turn the current probabilistic tree-decomposition path into a verified exact
algorithm or replace it with one.

Target package surfaces:

- Exact constellation PrAF inference by tree decomposition.
- Witness/table diagnostics sufficient to explain intermediate dynamic-programming
  states.
- A clear fallback to exact enumeration for small cases and unavailable
  decomposition support.

Red tests:

- Exact DP equals enumeration on generated low-treewidth PrAFs.
- Witness metadata identifies enough support to audit accepted/rejected/unknown
  outcomes.
- Known cyclic and disconnected cases.

Green work:

- Implement the paper-faithful DP in a narrow module.
- Keep enumeration as the executable oracle.
- Delete or quarantine experimental paths that conflict with the verified surface.

Acceptance:

- `uv run pytest -q tests/test_probabilistic.py tests/test_probabilistic_treedecomp.py`
- `uv run pyright src`

Paper gate:

- Page-image reread for Popescu and Wallner 2024 before changing the exact DP
  algorithm or claiming implementation conformance.

## Phase 5: Values, Weights, Rankings, And Explanations

Goal: add useful non-binary argumentation services without blurring them into
propstore belief revision.

Target package surfaces:

- Ranking semantics over AFs.
- Weighted argument systems with inconsistency budgets.
- Gradual semantics for weighted bipolar graphs.
- Impact/explanation measures for gradual semantics.
- Value-based ASPIC+ preference filtering.

Red tests:

- Ranking examples where accepted/rejected status alone is insufficient.
- Weighted-budget examples with changing inconsistency tolerance.
- Gradual fixed-point convergence and monotonicity examples.
- Impact-measure examples where contribution attribution is checkable.

Green work:

- Split ranking, weighted, gradual, and value-based ASPIC+ into separate slices.
- Keep all numeric semantics explicit about normalization, convergence tolerance,
  and tie handling.

Acceptance:

- `uv run pytest -q tests/test_ranking.py tests/test_weighted.py tests/test_gradual.py`
- `uv run pyright src`

Paper gate:

- Page-image rereads before each numeric or value-preference implementation:
  Dunne et al. 2011, Potyka 2018, Al Anaissy et al. 2024, Wallner 2024, and
  Prakken 2019 as applicable.

## Phase 6: Documentation And Package Release Surface

Goal: make the new functionality usable without propstore knowledge.

Red tests:

- Doctest or example tests for the public APIs that propstore is expected to call
  later.
- Import-boundary tests confirming `argumentation` does not import `propstore`.

Green work:

- Update README/API docs.
- Add examples for AF semantics, ASPIC+, PrAF, and optional solver backends.
- Stabilize result object names before propstore consumes them.

Acceptance:

- `uv run pytest -q`
- `uv run pyright src`

## Phase 7: Deferred Propstore Integration Plan

This phase does not begin until propstore's Semantic OS work has completed the
situated assertion and projection-boundary phases needed by argumentation
consumers.

Expected propstore integration targets:

- `propstore.world.types.ArgumentationSemantics`: add new package semantics names.
- `propstore.core.analyzers`: call package AF/PrAF services through stable result
  objects.
- `propstore.structured_projection`: project situated assertions into package
  inputs and lift results back by external IDs.
- `propstore.merge.structured_merge`: use argumentation results as merge evidence,
  not as the owner of belief revision.

Integration tests should live in propstore, not this package, and should prove:

- Situated assertion IDs survive projection and result lifting.
- Argumentation does not own propstore merge/revision decisions.
- Missing optional solver backends degrade to deterministic typed results.

## Execution Ledger

Status as of this package-first pass:

- Phase 1 landed labellings plus semi-stable, stage, ideal, and CF2 Dung
  semantics, with property checks against brute-force definitions.
- Phase 2 landed deterministic stable-CNF encoding, ICCMA AF I/O, and typed
  solver backend availability results.
- Phase 3 landed an ASPIC+ abstract projection object that exposes arguments,
  attacks, defeats, and deterministic IDs for downstream consumers.
- Phase 4 landed table diagnostics, grounded outcome probabilities, outcome
  witnesses, cyclic/disconnected coverage, backend metadata, and documentation
  that the current exact-DP implementation is an adapted grounded
  edge-tracking TD backend, not the full Popescu and Wallner I/O/U
  witness-table DP.
- Phase 5 landed ranking semantics, weighted attack-budget semantics, gradual
  quadratic-energy semantics, revised direct-impact attribution, value-based
  ASPIC+ filtering helpers, and accrual applicability helpers.
- Phase 6 landed README/API surface documentation, architecture documentation,
  and an import-boundary guard proving `argumentation` does not import
  `propstore`.
- Phase 7 remains intentionally deferred. No propstore code was modified.

Page-image checkpoints used during execution:

- Caminada labelling and semi-stable definitions were checked from web page
  images; local page images were not available for that checkpoint.
- Dung, Mancarella, and Toni 2007 ideal semantics, and Gaggl and Woltran 2013
  CF2 semantics, were checked from page images before implementation.
- Popescu and Wallner 2024 pages 5-6 were checked from local page images before
  changing probabilistic tree-decomposition diagnostics. The full paper-faithful
  I/O/U witness DP remains future work.
- Bonzon et al. 2016 pages 2-4 were checked from local page images before
  implementing Categoriser and Burden ranking semantics.
- Dunne et al. 2011 pages 5-6 were checked from local page images before
  implementing weighted attack-budget semantics.
- Potyka 2018 pages 1-2 and 5 were checked from local page images before
  implementing quadratic-energy gradual semantics.
- Al Anaissy et al. 2024 pages 3-4 were checked from local page images before
  implementing revised direct-impact attribution.
- Wallner et al. 2024 pages 2, 5, and 6 were checked from local page images
  before implementing value-based ASPIC+ filtering helpers.
- Prakken 2019 pages 4-5 were checked from local page images before
  implementing accrual applicability helpers.

Latest full package gate after Phase 6:

- `uv run pytest -q --timeout=300`: 356 passed in 63.61s.
- `uv run pyright src`: 0 errors, 0 warnings, 0 informations.
- `git diff --check`: passed.
- `git status --short`: only pre-existing untracked `notes/`, `out`, and
  `pyghidra_mcp_projects/` remained.

## First Executable Slice

Target: Phase 1, labelling primitives only.

Write set:

- `src/argumentation/labelling.py`
- `tests/test_labelling.py`
- Minimal exports in `src/argumentation/__init__.py` only if the package already
  exports comparable public surfaces.

Red commit:

- Tests for immutable labellings, legal status values, range computation, and
  extension/labelling round trips for complete, grounded, preferred, and stable
  semantics.

Green commit:

- Implement the smallest labelling module that satisfies those tests.

Do not implement semi-stable, stage, ideal, CF2, solver backends, or propstore
integration in the first slice.

First-slice acceptance:

- `uv run pytest -q tests/test_labelling.py tests/test_dung.py`
- `uv run pyright src`
- `git diff --check`
- `git status --short`
