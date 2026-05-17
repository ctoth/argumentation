# ABA Paper-Driven Routing TDD Workstream

## Goal

Turn the new ABA paper corpus into executable solver-routing work. The output is
not another benchmark narrative. The output is a tested, paper-backed shape
system that can explain why an ABA instance should go to `asp`, `sat`, native
preprocessing, a future tree-decomposition backend, or a future dispute-search
backend.

The work runs on `main` because the user explicitly requested it. Keep every
slice small, tested, and committed before moving to the next slice.

## Source Papers

These papers are now local collection inputs for this workstream:

- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md)
- [Reasoning in Assumption-Based Argumentation Using Tree-Decompositions](../papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/notes.md)
- [On the Computational Complexity of Assumption-Based Argumentation for Default Reasoning](../papers/Dimopoulos_2002_ComputationalComplexityAssumption-basedArgumentation/notes.md)
- [A generalised framework for dispute derivations in assumption-based argumentation](../papers/Toni_2013_GeneralisedFrameworkDisputeDerivations/notes.md)
- [Computing ideal sceptical argumentation](../papers/Dung_2007_ComputingIdealScepticalArgumentation/notes.md)
- [An abstract, argumentation-theoretic approach to default reasoning](../papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/notes.md)
- [A Tutorial on Assumption-Based Argumentation](../papers/Toni_2014_TutorialAssumption-basedArgumentation/notes.md)

If a planned invariant is not grounded in one of these notes or a later paper
read from page images, do not present it as paper-backed.

## Current Empirical Baseline

The current cap-200 ABA shape run found:

- Large dense high-arity ABA is not the hard class.
- Large dense medium-arity ABA is the hard class.
- Stable rows inside the hard class are mixed: at least one row is solved by
  `sat` after `auto` and `asp` time out, while neighbors still time out.
- Preferred rows inside the hard class repeatedly all-timeout under current
  `auto`, `asp`, and `sat`.
- Existing buckets find the danger zone but are too coarse for production
  routing.

Therefore the next step is not a broad backend rule. It is a property-tested
shape layer plus a benchmark gate that can separate structural subclasses.

## Non-Negotiables

- No filename heuristics.
- No generator-name heuristics.
- No ICCMA-only routing behavior.
- No route predicate may read path text except to open the input.
- No speed claim may be promoted from a Hypothesis test alone.
- No production routing rule may land without both:
  - a paper-backed structural predicate with property tests;
  - counterexample-free benchmark evidence on held-out rows or the current
    cap-200 corpus.
- Generated JSON, CSV, profiles, page images, and logs stay uncommitted unless
  explicitly promoted.
- Python entrypoints and tests use `uv run ...`.

## Paper-Derived Design Truths

### Lehtonen 2021

- Direct ASP encodings cover ABA admissible, complete, preferred, stable,
  grounded, and ideal semantics in the flat logic-programming fragment.
- Grounded ABA is polynomial by bounded iteration over assumptions.
- Stable verification is cheaper than preferred-style maximality checks.
- ABA+ reverse attacks raise complexity; preference behavior must not be
  silently conflated with ordinary ABA.
- Direct encodings should avoid translating ABA to an exponentially larger AF.

### Popescu 2023

- Flat finite ABA reasoning for admissible, complete, stable, and preferred is
  fixed-parameter tractable by tree-width.
- The paper's executable clue is not "treewidth good" in the abstract. It is
  the `tau_ABA` relational shape: atoms, assumptions, rules, heads, bodies,
  contraries, and queries.
- Stable DP table state tracks witness assumptions, satisfied rules, defeated
  assumptions, and counterwitnesses.
- Low-width structure is a route candidate. High-density alone is not.

### Dimopoulos 2002

- Complexity depends on framework class: flat, normal, simple, and general
  frameworks are not interchangeable.
- In flat frameworks, the empty assumption set is admissible.
- In normal frameworks, preferred and stable extension computations coincide.
- Preferred/admissible reasoning can be harder than stable reasoning; do not
  assume "more local" means "faster."

### Toni 2013 and Dung 2007

- P-acyclic finite ABA gives completeness for dispute derivation procedures.
- Dispute derivations are proof-carrying, query-directed procedures over
  assumptions, culprits, defences, and unresolved failure checks.
- P-acyclicity and local derivation structure are route candidates for future
  query-shaped proof search, not arbitrary metadata.

## Target Architecture

Build three source surfaces:

1. `argumentation` ABA shape extraction.
2. Hypothesis property tests proving the shape fields are structural,
   semantics-preserving, and route-safe.
3. Benchmark proposal gates that consume only shape fields plus solver class.

Do not add a production route until all three surfaces agree.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Paper-Derived Shape Contract.
3. Phase 2: Hypothesis Framework Generators.
4. Phase 3: Shape Extractor Properties.
5. Phase 4: Semantic Oracle Properties.
6. Phase 5: Metamorphic Route-Safety Properties.
7. Phase 6: Benchmark Feature Emission.
8. Phase 7: Cap-200 Rerun and Counterexample Gate.
9. Phase 8: Route Proposal or Algorithm Work Item.
10. Phase 9: Optional Production Routing.

Every phase has an explicit gate. Passing tests before the current phase gate
does not complete the workstream.

## Phase 0: Workstream Order Guard

Goal: make the checklist itself executable enough that dependency mistakes are
caught before implementation.

- [x] Add or update a lightweight order check for this workstream if a local
  workstream-check tool already exists.
- [x] Existing `tools\check_workstream_phase_order.py` covered this workstream;
  no fallback documentation path was needed.
- [x] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
git status --short -- workstreams\aba-paper-driven-routing-tdd.md
```

Expected result: only intentional workstream edits are dirty, then commit them.

## Phase 1: Paper-Derived Shape Contract

Goal: define the exact fields the extractor must compute before testing
generators or routing.

Add fields to the shape model only when they are computable from the parsed ABA
framework:

- `is_flat`
- `is_normal`
- `assumption_count`
- `atom_count`
- `rule_count`
- `contrary_count`
- `max_rule_arity`
- `avg_rule_arity`
- `rule_density`
- `dependency_scc_count`
- `dependency_scc_max_size`
- `dependency_cycle_count_or_flag`
- `p_acyclic`
- `contrary_target_in_degree_max`
- `contrary_target_in_degree_avg`
- `contrary_target_entropy`
- `assumption_incidence_width_proxy`
- `rule_body_overlap_max`
- `rule_body_overlap_avg`
- `closure_growth_sample`
- `grounded_iteration_count`
- `grounded_in_count`
- `grounded_out_count`
- `stable_obstruction_count`
- `tau_aba_primal_width_proxy`

Field meanings:

- `p_acyclic` follows Toni/Dung: dependency graph after deleting assumptions
  from rule premises must be acyclic.
- `tau_aba_primal_width_proxy` approximates Popescu's relational structure, not
  an AF translation.
- `stable_obstruction_count` is a cheap count of assumptions that cannot be in a
  stable set without failing conflict-free or outside-attack obligations.
- `closure_growth_sample` measures how quickly deductive closure expands from
  generated or sampled assumption sets.

Tests to write first:

- [x] `test_shape_contract_has_no_path_fields`
- [x] `test_p_acyclic_ignores_assumption_premises`
- [x] `test_tau_aba_proxy_uses_atoms_rules_heads_bodies_contraries`
- [x] `test_normal_framework_marks_preferred_stable_coincidence_candidate`
- [x] `test_flat_framework_marks_empty_set_admissible_candidate`

Gate:

```powershell
uv run pytest -q tests\test_aba_shape_contract.py
```

## Phase 2: Hypothesis Framework Generators

Goal: build reusable small ABA generators before expanding shape logic.

Create generators for:

- flat ABA frameworks;
- non-flat ABA frameworks;
- p-acyclic frameworks;
- cyclic dependency frameworks;
- normal frameworks where stable/preferred coincidence can be checked on small
  exhaustive examples;
- dense medium-arity frameworks resembling the hard bucket without using
  filenames or generator labels;
- low-width relational ABA structures for tree-decomposition candidates.

Generator constraints:

- Generate atom names independently of any path.
- Generate rule order randomly.
- Generate contraries independently of rule order.
- Keep small exhaustive cases small enough to enumerate semantics.
- Keep large benchmark-shaped cases for shape extraction only.

Properties to write first:

- [x] generated frameworks parse back into equivalent framework objects;
- [x] generated rule order is not semantically meaningful;
- [x] generated atom renaming maps are bijective;
- [x] generated flat frameworks contain no assumptions in rule bodies when the
  flat generator says they are flat;
- [x] generated p-acyclic frameworks satisfy the paper definition, not a weaker
  "no cycles anywhere" shortcut.

Gate:

```powershell
uv run pytest -q tests\test_aba_hypothesis_generators.py
```

## Phase 3: Shape Extractor Properties

Goal: prove the extractor is structural.

Hypothesis properties:

- [ ] Renaming atoms and assumptions preserves every bucketed shape field.
- [ ] Permuting rules preserves every shape field except optional stable
  deterministic tie-break metadata.
- [ ] Permuting contrary declarations preserves every shape field.
- [ ] Adding an unreachable rule changes only global size/width fields and not
  query-local closure fields.
- [ ] Duplicating an identical rule changes duplicate-sensitive density fields
  but not Boolean acyclicity/flatness.
- [ ] Removing zero-body facts cannot increase closure size.
- [ ] P-acyclicity is equivalent to acyclicity of the assumption-deleted
  dependency graph.
- [ ] SCC count and max SCC size agree with an independent graph construction.
- [ ] Contrary-target in-degree is invariant under renaming and declaration
  order.
- [ ] Closure growth is monotone with respect to adding assumptions to the
  starting set.

Gate:

```powershell
uv run pytest -q tests\test_aba_shape_properties.py
```

## Phase 4: Semantic Oracle Properties

Goal: connect shape features to semantics on tiny exhaustive frameworks.

Use small generated frameworks where exhaustive semantics are feasible. These
tests do not prove backend speed. They prove that our predicates mean what the
papers say they mean.

Properties:

- [ ] Stable assumption set is closed, conflict-free, and attacks every
  assumption outside it.
- [ ] Admissible assumption set is closed, conflict-free, and counterattacks
  every attacker.
- [ ] Preferred sets are maximal admissible sets.
- [ ] Every preferred set is admissible.
- [ ] In flat frameworks, the empty assumption set is admissible.
- [ ] In normal frameworks, preferred and stable sets coincide on exhaustive
  small cases.
- [ ] Grounded iteration reaches a fixpoint in at most `assumption_count`
  iterations for ordinary ABA.
- [ ] P-acyclic finite frameworks generated for dispute tests do not require a
  cyclic support proof for any derived atom.
- [ ] Stable obstruction count is zero for every enumerated stable set and
  positive for generated impossible-stable witnesses.

Gate:

```powershell
uv run pytest -q tests\test_aba_semantic_properties.py
```

## Phase 5: Metamorphic Route-Safety Properties

Goal: make it hard to accidentally route on fake signal.

Route predicates must be pure functions of:

- shape fields;
- solver class;
- explicit user/backend availability;
- timeout budget class, if present.

Route predicates must not use:

- path text;
- filename;
- parent directory;
- ICCMA year;
- row order;
- generator name;
- benchmark manifest identity.

Properties:

- [ ] Renaming the instance file path does not change route decision.
- [ ] Moving the same file to a different directory does not change route
  decision.
- [ ] Shuffling manifest row order does not change route decision.
- [ ] Atom renaming does not change route decision.
- [ ] Rule-order permutation does not change route decision.
- [ ] Route predicate cannot fire unless all required shape fields are present.
- [ ] Route predicate emits a reason object naming paper-backed fields.
- [ ] Any route predicate marked `production` has a benchmark evidence id.

Gate:

```powershell
uv run pytest -q tests\test_aba_route_properties.py
```

## Phase 6: Benchmark Feature Emission

Goal: emit the new shape fields in the benchmark output and keep diagnostics
separate from source progress.

Update `tools/aba_shape_benchmark.py` so each row includes:

- all Phase 1 fields;
- shape bucket id;
- route predicate candidates;
- backend outcome;
- witness validation result;
- route evidence id when a route is proposed;
- counterexamples per candidate route.

Run:

```powershell
uv run pytest -q tests\test_aba_shape_benchmark.py tests\test_aba_shape_properties.py tests\test_aba_route_properties.py
```

Then run the cap-200 feature emission:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --year 2025 --subtrack SE-PR --subtrack SE-ST --backend auto --backend asp --backend sat --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-shape-cap200-paper-features.json --output-csv data\iccma\2025\runs\aba-shape-cap200-paper-features.csv
```

Gate:

- tests pass;
- benchmark completes or reaches the configured timeout naturally;
- generated JSON/CSV are inspected but not committed unless explicitly
  requested;
- output contains no path-derived feature fields.

## Phase 7: Cap-200 Rerun and Counterexample Gate

Goal: determine whether new structural predicates make the hard bucket routable.

Analyze the generated JSON for:

- `asp` wins with zero counterexamples;
- `sat` wins with zero counterexamples;
- `auto` wins because preprocessing already solved the class;
- all-timeout classes;
- mixed classes that need a new backend rather than routing.

Candidate route promotion requires:

- at least two supporting rows unless explicitly marked as a one-off diagnostic;
- zero counterexamples in the current cap-200 run;
- no evidence that the predicate encodes a filename/generator artifact;
- a paper-backed reason:
  - direct ASP route from Lehtonen-style compact ABA encoding;
  - treewidth/low-width route from Popescu-style structure;
  - stable/preferred coincidence from Dimopoulos normal-framework property;
  - p-acyclic/query-proof route from Toni/Dung dispute completeness.

Gate:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --year 2025 --subtrack SE-PR --subtrack SE-ST --backend auto --backend asp --backend sat --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-shape-cap200-paper-features-rerun.json --output-csv data\iccma\2025\runs\aba-shape-cap200-paper-features-rerun.csv
```

Do not interrupt this command except on natural exit, configured timeout, user
stop request, or concrete external harm.

## Phase 8: Route Proposal or Algorithm Work Item

Goal: turn benchmark learning into one of two concrete outputs.

If a counterexample-free route exists:

- [ ] add a route proposal in source;
- [ ] add route property tests;
- [ ] add benchmark evidence id;
- [ ] keep the predicate structural;
- [ ] run route tests and a targeted benchmark rerun.

If the hard bucket remains mixed/all-timeout:

- [ ] do not add production routing;
- [ ] create a backend work item with exact structural signature:
  - high/medium arity;
  - SCC profile;
  - width proxy;
  - contrary concentration;
  - closure growth;
  - stable obstruction count;
  - preferred maximality risk.
- [ ] choose the next backend hypothesis:
  - Popescu-style low-width DP;
  - Lehtonen-style direct ASP encoding refinement;
  - Toni/Dung dispute search for p-acyclic query-shaped instances;
  - SAT/QBF/decomposition-guided route only after a source-backed paper is read
    into this collection or explicitly accepted from `../propstore/papers`.

Gate:

- either a route proposal with zero counterexamples exists;
- or a no-route algorithm work item exists with the exact hard-shape signature.

## Phase 9: Optional Production Routing

Goal: land only routes that survived the previous gates.

Required tests:

```powershell
uv run pytest -q tests\test_aba_route_properties.py tests\test_aba_shape_benchmark.py
```

Required benchmark:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts tests\manifests\iccma2025-cap200-timeouts.json --year 2025 --subtrack SE-PR --subtrack SE-ST --backend auto --backend asp --backend sat --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-shape-cap200-route-validation.json --output-csv data\iccma\2025\runs\aba-shape-cap200-route-validation.csv
```

Gate:

- route has no counterexamples;
- route reason names shape fields and paper source;
- witness validation still passes;
- non-ABA solver behavior is unchanged;
- generated outputs remain uncommitted unless explicitly promoted.

## Definition of Done

This workstream is complete only when one of these is true:

- A production route lands with paper-backed predicates, Hypothesis properties,
  benchmark evidence, and zero counterexamples.
- The current hard bucket is proven not routable by available features, and a
  concrete backend work item is recorded with the structural signature that
  defeated `auto`, `asp`, and `sat`.

Partial completion is allowed only as a committed checkpoint. Do not report the
workstream complete because tests pass, because a benchmark ran, or because a
shape field was added.

## Immediate Next Slice

Start with Phase 1 and Phase 2 together only if the existing code already has a
clear framework factory. Otherwise do Phase 1 first.

First implementation target:

- add `tests\test_aba_shape_contract.py`;
- add the missing shape fields behind tests;
- add no routing rule;
- run `uv run pytest -q tests\test_aba_shape_contract.py`;
- commit only the source/test files for that slice.
