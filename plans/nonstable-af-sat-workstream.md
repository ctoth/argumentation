# Dung AF SAT Kernel Workstream

## Aim
Make the Dung AF solver architecture boring in the good way: one explicit SAT
kernel, task-directed algorithms over that kernel, native Dung semantics as the
correctness oracle, and ICCMA execution paths that answer the task being asked.

This is not a compatibility migration. The target interface replaces the current
one-off SAT helper surface. Existing callers in this repository move to the new
surface in the same workstream. `../propstore` is only updated if it imports a
changed public surface; current inspection found no `argumentation.sat_encoding`
or `solve_dung*` imports there, so the expected propstore action is pin update
after this repository is pushed.

## Architectural Rule
Delete the old production SAT helper family first, then make compiler, tests,
and search failures the implementation queue.

The old production surface is the helper-shaped API in `argumentation.sat_encoding`
that rebuilds ad hoc Z3 solvers per task:

- `sat_stable_extension`
- `sat_complete_extension`
- `sat_preferred_extension`
- `sat_semi_stable_extension`
- `sat_stage_extension`
- private `_sat_complete_extension`
- private `_sat_conflict_free_extension`
- private range-variable helpers coupled to those functions

The stable CNF encoding API can remain only if it is still used as an explicit
CNF artifact API. It must not be the production execution path for ICCMA tasks.

## Target Kernel
Create `argumentation.af_sat` as the single Dung AF SAT kernel module.

### Core Types
- `AFSatProblem`
  - owns one `z3.Solver`;
  - owns ordered argument identity;
  - owns argument membership variables `in[a]`;
  - owns labelling variables `out[a]` and derived undecided state;
  - owns range variables `range[a]`;
  - owns cached attack/attacker indexes;
  - owns telemetry emission for every `check`.
- `SATCheck`
  - records utility name, assumptions count, result, elapsed time, model size,
    task metadata, and optional instance id/path.
- `SATTraceSink`
  - callable or protocol used by the ICCMA runner to stream per-check JSONL
    events while the run is still active.

### Kernel Constraint Builders
- `add_conflict_free()`
- `add_admissible_labelling()`
- `add_complete_labelling()`
- `add_stable_coverage()`
- `add_range_definition()`
- `require_in(arguments)`
- `require_out(arguments)`
- `require_any_in(arguments)`
- `require_range(arguments)`
- `require_any_range(arguments)`
- `require_attacks_any(targets)`
- `exclude_extension(extension)`
- `exclude_range_subset(range_set)`
- `check(utility_name, assumptions=())`
- `model_extension()`
- `model_range()`

All task algorithms use these operations. New task code must not instantiate
`z3.Solver()` directly.

## Paper-Backed Design Decisions
- Use complete labellings as the shared surface for complete, preferred,
  semi-stable, and ideal tasks.
  - Sources: ArgSemSAT notes; PrefSat notes.
- Use incremental SAT calls for loops and maximality checks.
  - Sources: Fudge notes; Dvorak/Jarvisalo/Wallner/Woltran CEGARTIX notes.
- Treat preferred skeptical acceptance as its own SAT procedure, not as
  enumeration plus universal quantification.
  - Source: Thimm/Cerutti/Vallati CDAS notes.
- Treat ideal semantics as preferred-super-core pruning, not preferred-extension
  enumeration.
  - Source: Thimm/Cerutti/Vallati CDIS notes.
- Treat semi-stable and stage as base-semantics plus range-maximality, with
  range variables and assumption/exclusion loops.
  - Sources: argmat-sat notes; Dvorak/Jarvisalo/Wallner/Woltran notes.
- Keep ConArg out of the first AF ICCMA kernel except as a later reference for
  weighted/soft-constraint architecture.

## Execution Order
This order is dependency-sorted. Do not start a later phase until the earlier
phase is committed or explicitly blocked.

### Phase 1: Replace the Helper Surface with the Kernel
1. Add `argumentation.af_sat` with `AFSatProblem`, `SATCheck`, and trace sink
   support.
2. Delete production use of the one-off SAT helper functions from
   `argumentation.sat_encoding`.
3. Update `argumentation.solver` to call task functions built over
   `AFSatProblem`.
4. Keep public solver behavior stable for supported tasks:
   - `SE-ST`, `DC-ST`, `DS-ST`;
   - `SE-CO`, `DC-CO`, `DS-CO`;
   - `SE-PR`, `DC-PR`;
   - `SE-SST`, `SE-STG`.
5. Add tests that monkeypatch native enumeration and prove `auto` does not use
   it for the supported routes above.
6. Run targeted solver tests, then the full test suite.

Done means no production Dung SAT task path directly constructs a fresh
task-local Z3 solver.

### Phase 2: Preferred and Complete Kernel Correctness
1. Differential-test kernel complete/stable/preferred witness routes against
   native semantics on generated small AFs.
2. Add direct model-shape tests for:
   - conflict-freeness;
   - admissibility;
   - complete labelling;
   - stable coverage;
   - required-in and required-out assumptions.
3. Make preferred witness growth use one incremental kernel loop.
4. Remove any duplicate preferred-growth implementation.

Done means preferred witness and credulous acceptance are kernel-only and still
match native preferred extensions on the differential envelope.

### Phase 3: Direct Skeptical Preferred Acceptance
Implement CDAS for `DS-PR`.

Required kernel utilities:
- `adm_ext(required_in)`;
- `adm_ext_att(query, excluded_extensions)`;
- `adm_attacks_set(target_set)`.

Algorithm shape:
1. Find an admissible set extending `{query}`. If none exists, return `False`.
2. Maintain stored admissible-with-query extensions `E`.
3. Search for an admissible attacker of a query-containing admissible set,
   excluding patterns already covered by `E`.
4. If no attacker exists, return `True`.
5. If the attacker cannot be extended together with `query`, return `False`.
6. Store the extended set and continue.

Routes:
- `DS-PR` defaults to SAT under `backend="auto"`.
- Native preferred enumeration remains only explicit `backend="native"` and as
  test oracle.

Tests:
- Differential generated-AF tests against native `preferred_extensions`.
- A monkeypatch test proving `auto DS-PR` does not call `_dung_extensions`.
- ICCMA runner sample showing per-call streaming and no final-only logging.

### Phase 4: Ideal Semantics without Preferred Enumeration
Implement CDIS for ideal semantics.

Algorithm shape:
1. Start with preferred-super-core candidate `P = all arguments`.
2. Repeatedly find an admissible set attacking some member of `P`.
3. Remove attacked arguments from `P`.
4. Remove arguments attacked but not defended inside `P`.
5. Return the remaining admissible set as the unique ideal extension.

Routes:
- `SE-ID` uses SAT CDIS.
- `DC-ID` and `DS-ID` evaluate membership in the CDIS extension.
- `auto` routes ideal Dung tasks to SAT.

Tests:
- Differential generated-AF tests against native `ideal_extension`.
- A monkeypatch test proving ideal `auto` does not enumerate preferred
  extensions.
- Full solver availability tests updated to expect SAT, not native, for ideal.

### Phase 5: Range-Maximal Acceptance for Semi-Stable and Stage
Replace witness-only range growth with task-directed range-maximal decision
procedures.

Base semantics:
- semi-stable uses complete/admissible kernel constraints plus range variables;
- stage uses conflict-free kernel constraints plus range variables.

Required algorithms:
- `find_range_maximal(base, require_in=query)`;
- `find_range_maximal(base, require_out=query)`;
- range subset exclusion clauses;
- optional shortcut depth knob matching the CEGARTIX idea, disabled by default
  until benchmarked.

Routes:
- `SE-SST`, `DC-SST`, `DS-SST` use SAT.
- `SE-STG`, `DC-STG`, `DS-STG` use SAT.
- Native remains explicit and test-only for these default routes.

Tests:
- Differential generated-AF tests against native `semi_stable_extensions` and
  `stage_extensions`.
- Monkeypatch tests proving default acceptance routes do not enumerate native
  extensions.
- Regression tests for counterexample/witness polarity in credulous and
  skeptical acceptance.

### Phase 6: Streaming Solver Telemetry
Make every SAT `check` emit an event as it happens.

Required event fields:
- instance id/path;
- ICCMA year if known;
- problem code;
- semantics and task;
- argument count;
- attack count;
- utility name;
- assumptions count;
- result: `sat`, `unsat`, `unknown`, or `error`;
- elapsed milliseconds;
- model extension size when available.

Runner integration:
- stream SAT events into the existing ICCMA progress JSONL;
- keep final summaries as aggregate artifacts;
- add tests that observe multiple events before final completion.

### Phase 7: ICCMA Benchmark Loop
After each algorithmic phase, run capped ICCMA sweeps and keep comparable
reports.

Reports:
- solved/timeouts by year;
- solved/timeouts by problem code;
- median/P90/P99 runtime by problem code;
- SAT-call count distributions;
- comparison against the previous pushed solver SHA.

Done means we can say which phase actually improved which ICCMA tracks, with
evidence.

### Phase 8: Public Surface and Propstore Pin
1. Search `../propstore` for imports of changed public argumentation APIs.
2. Update propstore callers only if this workstream changed a public surface
   they import.
3. Push `argumentation`.
4. Pin `../propstore` to the pushed argumentation commit SHA.
5. Run propstore architecture pin tests that mention argumentation.
6. Commit and push the propstore pin.

Current inspection: propstore imports public `argumentation.dung`,
`argumentation.aspic`, `argumentation.probabilistic`, and solver adapter modules,
but not `argumentation.sat_encoding` or `solve_dung*`. Expected propstore change
is therefore only the dependency pin, unless implementation deliberately changes
public Dung or solver-adapter APIs.

## Routing Target
- `ST`: SAT kernel.
- `CO`: SAT kernel complete labelling.
- `PR`: SAT kernel for `SE`/`DC`; CDAS for `DS`.
- `ID`: SAT CDIS.
- `SST`: SAT range-maximal complete/admissible.
- `STG`: SAT range-maximal conflict-free.
- `GR`: native polynomial path unless a direct grounded helper is added.
- `CF2`: native unless separately scoped.
- Enumeration APIs: explicit enumeration only; decision APIs must not enumerate
  unless the semantics truly has no task-directed implementation yet.

## Non-Goals
- Do not introduce an external solver binary requirement for the in-package
  backend.
- Do not preserve old Dung SAT helper names as compatibility wrappers.
- Do not optimize ABA, ADF, SETAF, CAF, or ASPIC in this workstream.
- Do not use ConArg weighted semantics in the first AF ICCMA implementation.

## Completion Definition
The workstream is complete only when:

- all listed default Dung ICCMA routes use the SAT kernel or an explicit native
  polynomial path;
- old production Dung SAT helper functions are gone;
- native extension enumeration is not used by default decision routes covered by
  this workstream;
- per-SAT-call telemetry streams during runner execution;
- differential tests pass against native semantics;
- full argumentation tests pass;
- `argumentation` is pushed;
- `../propstore` is pinned to the pushed commit and its relevant pin tests pass.
