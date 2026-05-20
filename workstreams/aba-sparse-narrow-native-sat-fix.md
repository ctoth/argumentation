# ABA Sparse/Narrow Native SAT Fix Workstream

Status: executable.

## Literal Goal

Fix the ABA sparse-assumption/narrow-rule hard class identified by structural
telemetry. The fix is not another profile run. The final repository state routes
this class away from clingo multishot ASP and into a native SAT/CEGAR path with
paper-cited semantics contracts and measurable timeout reduction.

## Evidence Already Established

- The hard class is structural: `sparse_assumption_language|narrow_rule_bodies`.
  It is characterized by flat ABA, low assumption-to-atom ratio, rule bodies of
  width at most 2 in the 10x10 fixture, many assumptions, many rules, and high
  rule-dependency SCC count.
- The hard class is not filename-based. Production route predicates must not
  inspect archive names, basenames, filenames, paths, years, or ICCMA labels.
- Py-spy profiles for representative timeout and solved rows show the hot path
  is clingo C time under:
  `_solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot
  -> find_preferred_extension/find_stable_extension -> _solve_one ->
  clingo.Control.solve`.
- Current route truth:
  `src/argumentation/solver.py::_auto_aba_backend` chooses ASP for ABA
  single-extension preferred and stable whenever clingo is installed, except for
  the existing dense-flat stable carveout. The existing native CNF preferred
  route in `src/argumentation/aba_sat.py` is dense-only via
  `src/argumentation/aba_route_policy.py::native_cnf_prefsat_dense_shape`.

## Paper Page Anchors Read For This Workstream

- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-002.png`
  defines ABA frameworks, assumptions, contraries, derivability, and attacks.
- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-003.png`
  defines conflict-free, admissible, complete, preferred, and stable semantics.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-023.png`
  states the direct ASP approach uses clingo and ASPRIN optimization for
  subset-maximal preferred assumption sets.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-024.png`
  gives the ABA fact representation: assumptions, rule heads, rule bodies, and
  contraries.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png`
  gives the common ABA module: guess `in/out`, forward support propagation,
  defeat via contraries, and conflict-freeness.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png`
  gives stable, admissible, complete, and preferred constraints; stable is
  `out` implies defeated, admissibility checks attacks from undefeated
  assumptions, and preferred is subset-maximal admissible/complete.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-027.png`
  gives bounded grounded iteration over assumptions; use this as the shape for
  deterministic fixed-point contracts, not as the target backend for this class.
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-012.png`
  gives the AF stable encoding: every out argument must be defeated.
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-020.png`
  gives the preferred saturation correspondence and shows why preferred needs a
  maximality test rather than mere admissibility.
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
  gives the PrefSat loop over complete labellings and iterative strengthening.
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png`
  gives PrefSat termination/correctness through repeated model refinement.
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png`
  anchors complete-labelling SAT and SAT solver use for preferred reasoning.
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-006.png`
  gives the SAT-based complexity-sensitive framework and no-good learning.
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-007.png`
  gives propositional base encodings for conflict-free, admissible, complete,
  and preferred refinement using a SAT oracle.
- `papers/deKleer_1986_AssumptionBasedTMS/pngs/page-001.png` and
  `papers/deKleer_1986_AssumptionBasedTMS/pngs/page-002.png` motivate caching
  assumption-context consequences instead of repeating derivations.

## Final State

- `backend="auto"` routes flat sparse/narrow ABA `single-extension` tasks for
  `preferred` and `stable` to native SAT before the ASP/clingo route.
- The route is selected from `argumentation.aba_telemetry` structural features:
  flat ABA, `max_rule_body_width <= 2`, bounded contrary fan-in/fan-out,
  `assumption_to_atom_ratio <= 0.45`, `assumptions >= 700`, and
  `rule_to_assumption_ratio >= 4.0`. The predicate uses framework shape only.
- Stable semantics has a native SAT path over assumptions and derived-literal
  reachability. It enforces conflict-freeness and the Lehtonen/Egly stable rule:
  every out assumption is attacked by the selected assumptions.
- Preferred semantics has a native SAT/CEGAR path over assumptions and support
  closure. It enforces conflict-freeness and admissibility from Lehtonen's ABA
  module, then applies Cerutti/Dvorak maximality refinement with learned clauses.
- Native sparse/narrow telemetry reports solver checks, learned clauses, closure
  propagations, routed semantics, and `clingo_solver_calls == 0`.
- The old sparse/narrow production route to ASP is gone. ASP remains available
  for shapes and tasks outside this route.
- No generated benchmark logs, profiles, screenshots, or JSONL diagnostics are
  committed.

## Owned Paths

- `src/argumentation/aba_route_policy.py`
- `src/argumentation/aba_sat.py`
- `src/argumentation/solver.py`
- `tests/test_aba_sparse_narrow_route_contract.py`
- `tests/test_aba_sparse_narrow_native_sat.py`
- `tools/run_aba_10x10_fixture.py`
- `workstreams/aba-sparse-narrow-native-sat-fix.md`

## Deletion Targets

- Delete the sparse/narrow fallthrough to ASP in auto routing for
  `single-extension` `preferred` and `stable`.
- Delete any implementation condition that keys the new route on `abcgen`,
  ICCMA year, manifest path, basename, filename, archive, or row id.
- Delete any use of Z3 main solving or support materialization as the main
  sparse/narrow path.
- Delete any compatibility wrapper that routes sparse/narrow rows to both ASP
  and SAT and chooses the faster answer after the fact.

## Ordered Execution

1. Start from a clean tracked-file `main`. For implementation, create
   `exp/aba-sparse-narrow-native-sat-fix` from `main` because this is a gated
   benchmark-driven slice. Promote only a passing final diff back to `main`.
2. Add failing Hypothesis route contracts:
   - Generated flat ABA frameworks with the sparse/narrow structural shape route
     to native SAT for `single-extension` `stable` and `preferred`.
   - Renaming files or changing path metadata cannot change route selection.
   - Route metadata contains the paper-page anchors above.
   - The selected route reports `clingo_solver_calls == 0`.
3. Add failing Hypothesis semantic contracts:
   - On small generated sparse/narrow ABA frameworks, native stable equals the
     existing oracle for stable extensions.
   - On small generated sparse/narrow ABA frameworks, native preferred returns a
     subset-maximal admissible extension and matches the existing preferred
     oracle membership.
   - Telemetry bounds solver checks and learned clauses before any wall-clock
     benchmark is run.
4. Add `tools/run_aba_10x10_fixture.py` with progress reporting. It reads
   `tests/manifests/iccma2025-abcgen-10x10.json`, runs each row through the real
   ICCMA runner path with a 30-second row timeout, and writes uncommitted JSON
   summary output.
5. Implement the structural route predicate in `aba_route_policy.py` using only
   telemetry/framework shape. Wire `solver.py` so the sparse/narrow route is
   checked before the ASP auto branch.
6. Implement native sparse/narrow stable in `aba_sat.py`:
   - compile assumptions and literal reachability once;
   - propagate narrow Horn bodies with bitsets;
   - encode selected assumptions in PySAT;
   - reject internal attacks;
   - require every out assumption's contrary in selected closure;
   - return one stable extension or no extension with telemetry.
7. Implement native sparse/narrow preferred in `aba_sat.py`:
   - reuse the same closure kernel;
   - encode admissibility through attack/defense checks over assumption masks;
   - run a Cerutti/Dvorak refinement loop for strict supersets;
   - learn no-good clauses for rejected models;
   - return a subset-maximal admissible extension with telemetry.
8. Run the targeted tests:
   `uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py tests\test_aba_structural_telemetry.py tests\test_aba_native_cnf_prefsat.py tests\test_iccma_runner_timeout_contract.py`
9. Run the fixture metric gate with a 750-second command timeout:
   `uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-10x10.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\sparse-narrow-fix-10x10.json`
10. Metric gate:
    - all 20 fixture rows route through native SAT;
    - `clingo_solver_calls == 0` for all 20 rows;
    - the 10 previously solved rows remain solved under 30 seconds;
    - at most 4 of the 10 previous timeout rows remain timed out;
    - every solved row validates under the existing runner validation.
11. Search gates:
    - `rg -n -F -- "abcgen" src tools tests` shows production matches only in
      fixture/test documentation paths.
    - `rg -n -F -- "clingo_solver_calls" src tests` shows the sparse/narrow
      contracts and native telemetry.
    - `rg -n -F -- "native_sparse_narrow" src tests tools` shows one route
      family, not parallel duplicate implementations.
12. Commit each owned source/test/tool slice atomically with explicit pathspecs.
    Keep generated JSON, logs, profiles, and benchmark outputs uncommitted.

## Required Completion Claim

Completion can be reported only with:

- the exact workflow used;
- the paper page anchors listed above;
- the passing targeted test command;
- the 10x10 fixture summary with timeout count and solved count;
- confirmation that the route is structural and not ICCMA/filename-based;
- confirmation that generated diagnostics were not committed.
