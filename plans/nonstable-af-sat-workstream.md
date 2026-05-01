# Non-Stable AF SAT Workstream

## Scope
Build a task-directed Dung AF SAT backend for ICCMA-style non-stable reasoning. The target is not faster native enumeration; the target is solver procedures that answer the requested task directly:

- witness tasks: find one extension when one exists;
- credulous acceptance: find one accepting witness;
- skeptical acceptance: find one rejecting counterexample, or prove none exists;
- enumeration: only enumerate when the public API explicitly asks for enumeration.

## Paper Inventory

### Read
- [Skeptical Reasoning with Preferred Semantics in Abstract Argumentation without Computing Preferred Extensions](../papers/Thimm_2021_SkepticalReasoningPreferredSemantics/notes.md)
- [Fudge: A light-weight solver for abstract argumentation based on SAT reductions](../papers/Thimm_2021_FudgeLight-weightSolverAbstract/notes.md)
- [ArgSemSAT-1.0: Exploiting SAT Solvers in Abstract Argumentation](../papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/notes.md)
- [argmat-sat: Applying SAT Solvers for Argumentation Problems based on Boolean Matrix Algebra](../papers/Pu_2017_ArgmatSatApplyingSATSolver/notes.md)

### Retrieved, Reader Pending
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract`
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures`
- `papers/Bistarelli_2012_ConArgToolSolveWeighted`

## Current Implemented Baseline
- `ST`: SAT stable witness and acceptance path exists.
- `CO`: SAT complete witness and complete acceptance path exists.
- `PR`: SAT preferred witness growth and credulous preferred acceptance exist.
- `SST/STG`: SAT range-maximal witness search exists for single-extension tasks.
- `DS-PR`, `SST/STG` acceptance, and `ID`: still native unless explicitly routed otherwise.

## Phase 1: Incremental SAT Surface
Replace ad hoc helper construction with a reusable AF SAT object.

### Target API
- `AFSatProblem(framework)`
- Shared variables:
  - `in[a]`
  - `out[a]`
  - optional/derived `undec[a]`
  - `range[a]`
- Shared constraints:
  - conflict-freeness
  - admissibility
  - complete labelling
  - stable coverage
  - range definition
- Solver operations:
  - `push()` / `pop()`
  - `require_in(args)`
  - `require_out(args)`
  - `require_any_in(args)`
  - `require_range(args)`
  - `require_any_range(args)`
  - `block_extension(ext)`
  - `model_extension()`

### Evidence
- ArgSemSAT uses complete labellings as the shared surface.
- Fudge explicitly benefits from incremental SAT calls.
- argmat-sat uses assumption-space clauses for maximality.

### Tests
- Differential generated-AF tests against native semantics up to small sizes.
- Regression tests proving `auto` does not call native enumeration for supported task-directed paths.

## Phase 2: Complete and Stable Consolidation
Port current stable and complete helpers onto `AFSatProblem`.

### Deliverables
- `SE-ST`, `DC-ST`, `DS-ST` through the shared SAT object.
- `SE-CO`, `DC-CO`, `DS-CO` through the shared SAT object.
- Delete duplicated one-off solver construction.

### Done Criteria
- Same public results as current helpers.
- No native enumeration for default stable/complete single or acceptance tasks.
- Full tests pass.

## Phase 3: Preferred Witness and Credulous Acceptance
Move current preferred witness growth onto the incremental surface.

### Algorithm
1. Find a complete/admissible witness satisfying required membership.
2. Repeatedly ask for a strict admissible or complete superset.
3. Stop when no strict superset exists.
4. Return the maximal set as a preferred witness.

### Routes
- `SE-PR`: SAT preferred witness.
- `DC-PR`: SAT preferred witness with query required in.
- `EE-PR` or extension enumeration: native or explicit SAT enumeration only, not default for decision tasks.

### Evidence
- ArgSemSAT and Cerutti et al. preferred SAT search.
- Fudge keeps standard reductions for easy tasks and special algorithms for hard ones.

## Phase 4: Direct Skeptical Preferred (`DS-PR`)
Implement CDAS from Thimm/Cerutti/Vallati 2021.

### Required SAT Utilities
- `adm_ext(required_in)`: admissible set extending a required set.
- `adm_ext_att(required_in, excluded_extensions)`: admissible set containing the query that is attacked by another admissible set and is not covered by stored exclusions.
- `adm_attacks_set(target_set)`: admissible attacker of at least one member of target set.

### CDAS Shape
1. Try to extend `{query}` to an admissible set. If impossible, answer `False`.
2. Maintain stored extended admissible sets `E`.
3. Search for an admissible set attacking an admissible set containing `query`, excluding patterns already in `E`.
4. If no such attacker exists, answer `True`.
5. If the attacker cannot be extended together with `query`, answer `False`.
6. Otherwise store the extension and continue.

### Routes
- `DS-PR`: SAT CDAS by default.

### Done Criteria
- Differential tests against native `preferred_extensions` for generated small AFs.
- A monkeypatch test proves `auto DS-PR` does not call native enumeration.
- ICCMA runner shows fewer `DS-PR` timeouts under the same cap.

## Phase 5: Ideal Semantics
Implement CDIS from Thimm/Cerutti/Vallati 2021.

### Algorithm
1. Start with candidate preferred-super-core `P = A`.
2. Repeatedly find an admissible set attacking a member of `P`.
3. Remove attacked arguments from `P`.
4. Remove arguments attacked but not defended inside `P`.
5. Return remaining admissible set as the ideal extension.

### Routes
- `SE-ID`: SAT CDIS witness.
- `DC-ID` / `DS-ID`: membership in the unique ideal extension after CDIS.

### Done Criteria
- Differential tests against native `ideal_extension`.
- Default `auto` routes ideal tasks through SAT.
- No preferred-extension enumeration for ideal.

## Phase 6: Range-Maximal Acceptance (`SST` / `STG`)
Upgrade range witness search into task-directed acceptance.

### Required SAT Utilities
- `range_of(extension)` variables or constraints.
- `grow_range(candidate, base_semantics)`.
- `find_range_maximal(require_in=query)`.
- `find_range_maximal(require_out=query)`.

### Routes
- `SE-SST`: SAT range-maximal complete/admissible witness.
- `DC-SST`: SAT range-maximal witness containing query.
- `DS-SST`: SAT range-maximal counterexample excluding query.
- `SE-STG`: SAT range-maximal conflict-free witness.
- `DC-STG` / `DS-STG`: analogous stage acceptance paths.

### Evidence
- argmat-sat Table 2 and maximal-range assumption-space algorithm.
- Dvorak/Jarvisalo/Wallner/Woltran complexity-sensitive framework still needs full reader notes before final algorithm lock.

### Done Criteria
- Differential tests against native `semi_stable_extensions` and `stage_extensions` for generated small AFs.
- `auto` acceptance routes do not call native enumeration for supported range tasks.
- ICCMA runner reports improvement on `SST` and `STG` decision tracks.

## Phase 7: Solver Telemetry
Add structured per-SAT-call logging.

### Fields
- instance id/path
- task and semantics
- argument count
- attack count
- SAT utility name
- assumptions count
- result: `sat`, `unsat`, `unknown`, error
- elapsed milliseconds
- model extension size

### Runner Integration
- Stream solver-call events into the existing runner progress JSONL.
- Keep final summaries as aggregate artifacts only.

## Phase 8: ICCMA Benchmark Loop
Run capped sweeps after each algorithm phase.

### Required Reports
- solved/timeouts by year
- solved/timeouts by problem code
- median/P90/P99 runtime by problem code
- comparison against the previous pushed solver SHA

## Routing Target
- `ST`: SAT.
- `GR`: native polynomial path unless a simpler direct function is added.
- `CO`: SAT complete labelling.
- `PR`: SAT for `SE`/`DC`; CDAS SAT for `DS`.
- `SST`: SAT range-maximal complete/admissible.
- `STG`: SAT range-maximal conflict-free.
- `ID`: SAT CDIS.
- Native remains a correctness oracle and explicit fallback, not the ICCMA default for hard decision tasks.
