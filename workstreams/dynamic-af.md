# Dynamic AF Workstream

## Goal

Add actual incremental dynamic argumentation algorithms while keeping the
existing recompute-from-scratch implementation as the correctness oracle.

## Primary Papers and Sources

- Alfano, Greco, and Parisi (2017), "Efficient Computation of Extensions for
  Dynamic Abstract Argumentation Frameworks: An Incremental Approach".
- Alfano, Greco, and Parisi (2019), dynamic skeptical preferred acceptance.
- Niskanen and Jarvisalo IPAFAIR/API material for incremental dynamic tracks.
- ICCMA 2023 report dynamic-track input/API sections.

Reread page images directly before implementing affected-subframework
definitions, update classes, or API behavior.

## Current State

- `argumentation.dynamic` supports update streams and keeps
  `DynamicRecomputeOracle` as the recompute-from-scratch correctness oracle.
- Single attack additions/deletions can use the Alfano-Greco-Parisi influenced
  set and reduced AF algorithm for grounded, complete, preferred, and stable
  semantics.
- The stateful incremental wrapper reports whether the reduced-AF path was used
  or whether a recompute fallback occurred.
- It does not implement incremental SAT or IPAFAIR-style mutable external
  solver state.

## Execution Mode

Use TDD with recompute as oracle:

1. Reread the paper page defining the update/affected-region behavior.
2. Add a failing paper example or Hypothesis property under the stated
   preconditions.
3. Implement the incremental step.
4. Differential-test incremental answers against recompute for generated update
   streams.

Properties must come from paper claims, API specifications, or semantic
equivalence requirements, not from local performance guesses.

## Phases

### Phase 1: Update Model and Baseline Oracle

- Pin the current recompute implementation as `DynamicRecomputeOracle` or an
  equivalent clearly named path.
- Add generated tests for add/delete argument and add/delete attack streams.
- Assert recompute results match direct construction of the final AF.

Paper/source-derived properties:

- Applying an add-argument update only changes the argument set by that
  argument.
- Deleting an argument removes all incident attacks.
- Adding/removing attacks leaves the argument set unchanged.
- Update streams are order-sensitive exactly as specified by the dynamic-track
  input/API.

Acceptance criteria:
- Recompute oracle is trusted by tests before incremental logic is added.
- Status: complete.

### Phase 2: Affected Subframework Detection

- Reread Alfano et al.'s reduced affected-part definition.
- Implement affected-region computation for single updates.
- Add generated properties comparing affected-region membership against the
  paper's reachability/defense conditions.

Paper-derived properties:

- Arguments outside the affected part retain their status when the paper states
  they do.
- The reduced subframework contains every argument whose acceptance may change
  under the update.
- If the update is irrelevant under the paper's conditions, the previous
  extension remains valid.

Acceptance criteria:
- Tests include both fixed paper examples and generated small AF/update cases.
- Status: complete for the Alfano-Greco-Parisi influenced set used by the
  single-attack incremental algorithm.

### Phase 3: Incremental Extension Update

- Implement incremental update for grounded, complete, preferred, and stable
  semantics in the order the paper supports.
- Use the previous extension as input.
- Fall back to recompute only through an explicit, tested fallback path with a
  reason.

Paper-derived properties:

- Incremental result equals recompute result for every generated small AF and
  update stream under supported semantics.
- If the paper specifies conditions for reusing the previous extension, assert
  those conditions and reuse behavior directly.

Acceptance criteria:
- Tests can detect whether the incremental path was used, not just whether the
  answer is correct.
- Status: complete for single attack updates under grounded, complete,
  preferred, and stable semantics. Unsupported update kinds fall back through
  explicit metadata.

### Phase 4: Dynamic Acceptance Queries

- Add credulous and skeptical query APIs that operate over incremental state.
- Align query behavior with IPAFAIR where the source specifies it.
- Support multiple assumed query arguments only if the API/paper does.

Source-derived properties:

- Credulous query answers true iff at least one current extension contains the
  query argument.
- Skeptical query answers true iff all current extensions contain the query
  argument.
- IPAFAIR-style return codes, if exposed, match the source documentation.

Acceptance criteria:
- Query APIs have fixtures for YES/NO and witness/counterexample extraction
  where supported.
- Status: complete for the package-native stateful wrapper; queries return
  witness/counterexample extensions.

### Phase 5: Performance Guardrails

- Add instrumentation that reports affected-region size and whether fallback
  recompute occurred.
- Add tests proving unsupported cases fall back honestly.
- Do not claim asymptotic or empirical speedups without benchmarks.

Acceptance criteria:
- Documentation distinguishes correctness, incremental execution, and measured
  performance.
- Status: complete. No performance speedup claim is made without benchmarks.

## Tests

Targeted command:

```powershell
uv run pytest tests\test_dynamic.py -q
```

Full verification:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- Recompute oracle remains available and tested.
- Incremental path is implemented for the explicitly supported semantics.
- Hypothesis differential tests compare incremental results to recompute.
- Tests prove incremental code is actually exercised.
- Docs no longer describe recompute-only support as a dynamic SOTA algorithm.

## Known Traps

- Correct answers from recompute do not prove an incremental algorithm exists.
- Do not hide recompute fallback behind the same success result without
  metadata.
- Dynamic deletion cases are easy to under-test; generate incident-attack cases
  aggressively.
