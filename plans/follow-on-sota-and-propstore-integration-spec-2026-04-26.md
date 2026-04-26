# Follow-On SOTA And Propstore Integration Spec

Date: 2026-04-26

Status: package tracks executed; propstore integration gated by Semantic OS readiness

This spec picks up the work that remains after
`plans/package-first-argumentation-sota-workstream-2026-04-26.md`.

Verdict: the package is now substantially stronger, but it is not SOTA yet. The
remaining high-payoff work is:

- replace the adapted probabilistic tree-decomposition backend with the
  paper-faithful Popescu and Wallner I/O/U witness-table dynamic program;
- add direct ASPIC+ solver encodings so larger structured theories do not always
  require materializing the whole abstract AF first;
- add ASPIC+ incomplete-information reasoning with explicit stable, relevant,
  unknown, and witness results;
- mature the numeric/value/accrual helpers where the current implementations are
  intentionally narrow package surfaces;
- integrate into propstore only after propstore's Semantic OS plan reaches the
  situated assertion and projection boundary.

## Execution Ledger

Package-first execution completed Tracks A through D in this repository:

- Track A landed the paper-faithful Popescu and Wallner I/O/U witness-table
  dynamic program behind the explicit `paper_td` probabilistic strategy.
- Track B landed deterministic ASPIC+ encoding objects, a materialized
  reference grounded query surface, and typed backend absence metadata.
- Track C landed a package-native incomplete ASPIC+ completion oracle with
  stable, relevant, unknown, and unsupported classifications plus witnesses.
- Track D landed exact Shapley-style gradual attack impact, accrual grounded
  labelling, and Wallner-style subjective ASPIC+ theory projection.

Propstore readiness was checked against
`../propstore/plans/epistemic-os-workstreams-2026-04-25.md`,
`../propstore/plans`, `../propstore/proposals`, and the
`../propstore/papers` inventory. The gate is not open: the active propstore
control surface still places argumentation behind situated assertions and the
typed projection boundary, and it does not delegate this argumentation child
scope now. No propstore production code was changed by this workstream.

## Control Rules

- Red/green TDD remains the control surface. Each production slice starts with a
  failing test commit and is followed by the smallest green implementation
  commit.
- Commit after each edit slice. Do not begin another slice while edited files in
  the current repo remain uncommitted.
- Scientific-paper details require page-image rereads before implementation.
  Existing notes, claims, or extracted text may guide prioritization, but they
  are not source of truth for algorithms, invariants, or edge-case examples.
- Keep `argumentation` package-first. It must not import `propstore`, know about
  propstore storage, or know about Semantic OS identity machinery.
- Keep heavy solvers optional. SAT, ASP, clingo, Datalog, or tree-decomposition
  libraries must be behind typed adapters or extras.
- Every backend absence path returns deterministic typed metadata rather than an
  import crash.
- Every milestone acceptance gate includes:
  - `uv run pytest -q`
  - `uv run pyright src`
  - `git diff --check`
  - `git status --short`

## Track A: Paper-Faithful Probabilistic AF TD DP

Goal: implement the Popescu and Wallner exact tree-decomposition algorithm as a
verified package surface, then retire or quarantine the current adapted grounded
edge-tracking backend if it conflicts with the paper-faithful surface.

Mandatory page-image gate:

- Reread Popescu and Wallner 2024 algorithm, table-state, witness, and theorem
  pages directly from page images before writing tests that claim conformance.
- Record the pages reread and the exact definitions implemented in the red or
  green commit message.

Target behavior:

- Exact constellation PrAF inference over package-native argument IDs.
- Dynamic-programming rows with explicit I/O/U-style state and witness metadata.
- Table diagnostics whose size is governed by bag-local state, not global edge
  tracking.
- Enumeration remains the oracle for small AFs and differential tests.

TDD slices:

1. Red tests for typed row states and tiny leaf/introduce/forget/join table
   transitions.
2. Green implementation of the row-state model and the smallest transition
   subset that passes those tests.
3. Red differential tests comparing TD results to enumeration on generated
   low-treewidth PrAFs.
4. Green full nice-TD evaluator with deterministic diagnostics.
5. Red tests proving witness metadata is sufficient to audit accepted,
   rejected, and unknown outcomes.
6. Green witness lifting and public result metadata.
7. Red tests that prevent accidental use of the old edge-tracking backend when
   the paper-faithful backend is requested.
8. Green deletion, quarantine, or explicit backend naming for the old path.

Acceptance:

- `uv run pytest -q tests/test_probabilistic.py tests/test_treedecomp.py`
- `uv run pytest -q tests/test_probabilistic_treedecomp.py`
- `uv run pyright src`

## Track B: Direct ASPIC+ Solver Encodings

Goal: support direct ASPIC+ reasoning surfaces that can avoid constructing a full
abstract AF when a backend supports the query.

Mandatory page-image gates:

- Reread Lehtonen, Niskanen, and Jarvisalo 2024 before implementing preferential
  ASPIC+ ASP encodings or solver-parity claims.
- Reread Diller, Strass, and Wyner 2025 before implementing Datalog grounding
  claims or interfaces.
- Reread Niskanen, Wallner, and Jarvisalo 2020 before claiming parity with
  modern solver-backed abstract AF behavior.

Target package surfaces:

- Immutable ASPIC+ encoding objects with deterministic identifiers.
- Optional backend adapter protocols for ASP/clingo, Datalog, or SAT-derived
  encodings.
- Typed backend result objects for success, unavailable backend, unsupported
  query, timeout, and solver error.
- Direct query functions for grounded, complete, preferred, stable, credulous,
  and skeptical checks where the encoding supports them.

TDD slices:

1. Red tests proving deterministic encoding identities for small ASPIC+ theories.
2. Green immutable encoding object and stable identifier assignment.
3. Red equivalence tests against the current
   `build_arguments -> compute_attacks -> compute_defeats -> Dung semantics`
   path on tiny theories.
4. Green reference direct evaluator or pure encoding evaluator for the smallest
   supported query set.
5. Red tests for optional backend absence and unsupported-query metadata.
6. Green typed backend adapter result layer.
7. Red tests for preference edge cases: strict rules, defeasible rules,
   last-link, weakest-link, value-based, and accrual-aware comparison hooks.
8. Green preference-aware encoding expansion.

Acceptance:

- `uv run pytest -q tests/test_aspic.py tests/test_aspic_encodings.py`
- `uv run pytest -q tests/test_value_based.py tests/test_accrual.py`
- `uv run pyright src`

## Track C: ASPIC+ Under Incomplete Information

Goal: add package-native incomplete-information reasoning for ASPIC+ without
making propstore belief revision part of this package.

Mandatory page-image gate:

- Reread Odekerken, Diller, and Borg 2025 pages containing the formal status
  definitions, examples, and algorithms before writing conformance tests.

Target behavior:

- Inputs express unknown premises, rules, preferences, or facts as package-native
  partial theories.
- Results classify requested conclusions or arguments as stable, relevant,
  unknown, or unsupported under the selected semantics.
- Witness metadata identifies completions or counter-completions where the
  algorithm supports them.
- Exact enumeration over tiny completions remains the oracle until a direct
  algorithm is verified.

TDD slices:

1. Red tests for a tiny partial theory with one unknown premise.
2. Green partial-theory model and exhaustive completion oracle.
3. Red tests for stable, relevant, unknown, and unsupported outcomes.
4. Green result classification and witness metadata.
5. Red equivalence tests between direct incomplete-information evaluation and
   exhaustive completion on generated tiny theories.
6. Green direct evaluator or backend adapter for the first paper-faithful query.
7. Red tests for backend absence and unsupported semantics.
8. Green typed degradation paths.

Acceptance:

- `uv run pytest -q tests/test_aspic_incomplete.py tests/test_aspic.py`
- `uv run pyright src`

## Track D: Numeric, Value, And Accrual Maturation

Goal: deepen the new helper surfaces without pretending they already implement
the full literature.

Mandatory page-image gates:

- Reread Al Anaissy et al. 2024 Shapley or attribution pages before adding
  Shapley-style impact measures.
- Reread Prakken 2019 pages defining accrual labellings and characteristic
  operators before implementing full accrual labelling semantics.
- Reread Wallner et al. 2024 value-based construction pages before adding
  subjective argumentation-theory builders beyond the current filtering helper.

Candidate slices:

- Shapley-style gradual impact attribution with exact enumeration for tiny
  graphs and approximation metadata for larger graphs.
- Full accrual labelling semantics rather than only weak/strong applicability
  envelopes.
- Value-based subjective theory construction that returns a complete projected
  ASPIC+ or AF object, not only filtered defeats.
- Ranking/weighted/gradual result explanations that share a small, typed witness
  vocabulary where that reduces duplication.

Acceptance:

- `uv run pytest -q tests/test_gradual.py tests/test_accrual.py tests/test_value_based.py`
- `uv run pytest -q tests/test_ranking.py tests/test_weighted.py`
- `uv run pyright src`

## Track E: Propstore Integration Gate

Goal: specify how propstore will use the new package functionality, without
starting propstore code until its Semantic OS projection boundary is ready.

Current gate from `../propstore/plans/epistemic-os-workstreams-2026-04-25.md`:

- Propstore's active trunk is relation concepts, situated assertions, context
  lifting, projection round trips, import-ready provenance, and epistemic state
  machinery.
- Before deep rewrites, propstore must have WS0 preflight, architecture tests,
  old-surface enumeration, `ConditionRef`, `ProvenanceGraphRef`, and relevant
  page-image gates.
- No new propstore plan file should be created unless the active workstream
  delegates that scope.

Propstore is ready for argumentation integration only when:

- situated assertions are the stable projection carrier;
- projection round trips preserve source assertion IDs, relation IDs, roles,
  context, condition references, and provenance graph references;
- propstore has a typed argumentation projection boundary that can call package
  services and lift package results back to situated assertions;
- propstore's active plan explicitly delegates the argumentation child scope or
  is edited to include it.

Expected integration after the gate:

- `propstore.world.types.ArgumentationSemantics` adds package semantics names
  for the new AF, PrAF, ASPIC+, incomplete-information, ranking, weighted,
  gradual, value-based, and accrual surfaces that propstore chooses to expose.
- `propstore.structured_projection` maps situated assertions to package AF,
  PrAF, and ASPIC+ inputs while preserving external IDs.
- `propstore.core.analyzers` calls package result objects and converts them to
  propstore reports without changing package semantics.
- `propstore.merge.structured_merge` may use argumentation results as merge
  evidence, but argumentation does not own merge policy or belief revision.
- `argumentation` still must not import `propstore`; propstore is the consumer.

Expected propstore TDD after the gate:

1. Red projection tests proving situated assertion IDs survive package projection
   and result lifting.
2. Green projection adapter using package-native external-ID fields.
3. Red analyzer tests proving missing optional solver backends degrade to typed
   reports.
4. Green analyzer adapter and report conversion.
5. Red merge tests proving argumentation evidence does not override merge
   ownership or provenance.
6. Green merge-policy wiring.

Propstore acceptance after the gate:

- Use propstore's logged pytest wrapper and active plan gates, not this package's
  bare test commands.
- Keep argumentation package gates green after any public API change needed by
  propstore.

## Milestones

1. Spec validation: commit this file and confirm no code changed.
2. Track A package implementation: paper-faithful Popescu and Wallner DP.
3. Track B package implementation: direct ASPIC+ encodings and backend metadata.
4. Track C package implementation: incomplete-information ASPIC+ reasoning.
5. Track D package implementation: numeric/value/accrual maturation slices.
6. Propstore readiness check: only after propstore's active Semantic OS plan
   delegates the argumentation projection scope.
7. Propstore integration: execute as a propstore TDD child workstream under
   propstore's active control surface.

## Spec Acceptance

This spec slice is documentation-only. Acceptance is:

- `git diff --check`
- `git status --short`
- commit this file atomically before any implementation work starts.
