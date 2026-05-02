# Workstream: Incremental SAT Kernel for Hard AF/ABA ICCMA Tasks

Author: Codex
Date: 2026-05-02
Status: implementation workstream; no solver code changed in this document
Scope: Replace repeated hard-semantics search with a paper-backed, test-first,
task-directed SAT kernel for abstract AFs and ABA lowered to AFs.

---

## 1. Diagnosis from the current ICCMA run

The cap-100 ICCMA run is not primarily blocked by runner overhead. The live
trace repeatedly shows the same pattern on hard rows:

- `SE-ID` / `DC-ID`: alternating `preferred_seed` and `preferred_grow` calls,
  often on the same instance, with little useful state carried between calls.
- `SE-PR` on larger ABA-lowered instances: repeated preferred witness search
  hits the row timeout.
- `SE-STG` / `SE-SST` and related acceptance tasks: seed search is the
  expensive part; range-maximality checks are often cheaper once a useful
  candidate exists.

This matches the literature's warning: hard AF tasks should not be implemented
as full preferred-extension enumeration, repeated seed discovery, or native
extension-family enumeration. They should be implemented as incremental SAT
oracle loops over a reusable base encoding, with learned blocking/refinement
clauses.

## 2. Paper-backed target architecture

### 2.1 Shared kernel

Build one per-instance `AfSatKernel` that owns:

- argument indices and attack indices;
- `in[a]` membership variables;
- optional complete-labelling variables `out[a]`, `undec[a]`;
- optional range variables `range[a]`;
- reusable base constraints for conflict-free, admissible, complete, stable,
  and range semantics;
- an incremental solver surface with scoped assumptions or `push`/`pop`;
- instrumentation for every SAT call, using the current streaming event shape.

This is directly supported by:

- ArgSemSAT: complete labellings are the central SAT surface for complete,
  grounded, preferred, stable, and acceptance tasks.
- PrefSat: preferred extensions can be found by iterative SAT search over
  complete labellings, growing `in` sets and blocking subsets.
- Dvorak/Jarvisalo/Wallner/Woltran: second-level tasks should use SAT as an
  NP oracle inside CEGAR-style refinement, not one monolithic encoding.
- Fudge: repeated related SAT checks should share an incremental SAT engine.

### 2.2 Preferred tasks

Preferred witness tasks use complete/admissible base constraints plus strict
superset growth:

- find a complete/admissible seed satisfying the task query;
- ask for a strict admissible or complete superset;
- repeat until no strict superset exists;
- learn a blocking clause excluding subsets of the discovered maximal set.

This follows PrefSat and Dvorak. It is acceptable for `SE-PR` and `DC-PR`, but
not sufficient as the final implementation for `DS-PR`.

### 2.3 Skeptical preferred

`DS-PR` must use the Thimm/Cerutti/Vallati CDAS route, not preferred-extension
enumeration:

- use admissibility-only SAT utilities such as `AdmExt`, `AdmArgAtt`, and
  `AdmExtAtt`;
- store seen admissible counter-patterns;
- answer skeptical preferred acceptance without constructing preferred
  extensions.

This is the main paper-backed correction to the current hard path. The
testable invariant is: `DS-PR` must not call the preferred extension enumerator
or preferred witness maximizer.

### 2.4 Ideal semantics

`SE-ID`, `DC-ID`, and `DS-ID` should use CDIS/Fudge-style ideal reasoning:

- compute the preferred super-core candidate by removing arguments attacked by
  admissible sets;
- remove arguments that are not internally defended by the remaining candidate;
- return the unique ideal extension as the maximal admissible subset of that
  core.

This targets the live `SE-ID` / `DC-ID` repeated `preferred_seed` bottleneck.
The testable invariant is: ideal computation must not loop over preferred
extensions.

### 2.5 Semi-stable and stage

Semi-stable and stage use range variables:

```text
range[a] <-> in[a] or exists b in in such that b attacks a
```

Then:

- stage base semantics is conflict-free;
- semi-stable base semantics is complete/admissible;
- maximality is strict range growth, not preferred-style set growth;
- learned clauses exclude candidates whose ranges are contained in an already
  exhausted range.

This follows Dvorak's strict-range refinement and argmat-sat's range-vector
assumption-space procedure.

### 2.6 ABA

ABA should lower to the same AF kernel once per instance/task batch. The ABA
CLI and runner should not contain a second hard-semantics implementation. Once
the lowered AF is built, the default path is the same `AfSatKernel`.

## 3. Test-first implementation order

### Phase 0: Lock down current failure signatures

Tests first:

- Add a focused regression fixture from a small generated AF where current
  ideal repeats preferred seed/grow work.
- Add instrumentation assertions that hard semantics emit per-SAT-call events
  with utility names.
- Add a runner-level golden test proving row timeout is applied around a whole
  row while SAT-call events still stream before timeout.

Implementation:

- No algorithm change.
- Add fixtures and small profiling assertions only.

Done when:

- Tests fail if ideal or preferred paths stop emitting SAT-call events.
- Tests record the current repeated-call shape without requiring wall-clock
  timing.

### Phase 1: Introduce `AfSatKernel`

Tests first:

- On generated AFs up to small size, compare kernel conflict-free,
  admissible, complete, stable, and range model predicates against native
  predicates.
- Verify complete labelling one-to-one correspondence with complete
  extensions.
- Verify stable equals complete labelling with no undecided arguments.

Implementation:

- Add the kernel object.
- Move existing ad hoc SAT helpers onto the kernel surface.
- Keep native only as an oracle/fallback, not as the production hard path.

Done when:

- Existing public solver calls still pass.
- New kernel tests pass under `uv run pytest`.
- Search shows hard AF code uses the kernel rather than constructing fresh
  solver state per utility call.

### Phase 2: Preferred `SE-PR` and `DC-PR`

Tests first:

- Differential-test `SE-PR` and `DC-PR` against native semantics on generated
  AFs up to the current exhaustive-safe bound.
- Assert discovered preferred witnesses are admissible and have no admissible
  strict superset.
- Assert repeated discovery blocks subsets of already found maximal sets.

Implementation:

- Implement strict-superset preferred growth over the kernel.
- Use learned subset-blocking clauses.
- Route `SE-PR` and `DC-PR` through this path in `auto`.

Done when:

- No `SE-PR` / `DC-PR` route uses full preferred enumeration.
- ICCMA smoke run shows per-row SAT call count lower or equal on selected
  previous timeout fixtures.

### Phase 3: Direct `DS-PR` via CDAS

Tests first:

- Encode the Figure 1-style examples from Thimm/Cerutti/Vallati notes:
  arguments skeptically accepted under preferred must match the paper example.
- Property-test `DS-PR` against native enumeration on small AFs.
- Add a guard test that `DS-PR` does not call preferred-extension enumeration
  or preferred maximization helpers.

Implementation:

- Add `AdmExt`, `AdmArgAtt`, and `AdmExtAtt` utilities on `AfSatKernel`.
- Implement CDAS with stored admissible counter-patterns.
- Route `DS-PR` through CDAS in `auto`.

Done when:

- `DS-PR` is task-directed and enumeration-free.
- Differential tests pass.

### Phase 4: Direct ideal via CDIS

Tests first:

- Validate that the ideal extension is admissible.
- Validate that it is the maximal admissible subset of the preferred
  super-core on generated small AFs.
- Add a guard test that `SE-ID`, `DC-ID`, and `DS-ID` do not enumerate
  preferred extensions.

Implementation:

- Implement preferred-super-core pruning with admissible attacker queries.
- Implement internal defense cleanup.
- Route `SE-ID`, `DC-ID`, and `DS-ID` through CDIS/Fudge-style ideal.

Done when:

- Live-style ideal fixtures avoid repeated preferred seed/grow loops.
- All ideal tasks match native enumeration on small AFs.

### Phase 5: Range-maximal semi-stable and stage

Tests first:

- Differential-test `SE-SST`, `DC-SST`, `DS-SST`, `SE-STG`, `DC-STG`, and
  `DS-STG` against native semantics on generated small AFs.
- Assert every returned stage extension is conflict-free and range-maximal.
- Assert every returned semi-stable extension is admissible/complete and
  range-maximal.
- Guard against preferred-style set maximality being used for stage.

Implementation:

- Add range variables to the kernel.
- Implement strict-range growth and range containment blocking.
- Route semi-stable and stage tasks through the kernel in `auto`.

Done when:

- No production `SST`/`STG` ICCMA route uses full native extension-family
  enumeration.
- Range-maximal tasks stream SAT-call events with range utility names.

### Phase 6: ABA default integration

Tests first:

- ABA CLI tests prove `uv run python -m argumentation...` uses `auto` by
  default.
- ABA runner tests prove lowered AF tasks route through `AfSatKernel`.
- Differential tests compare ABA semantics against existing small native ABA
  behavior before and after lowering.

Implementation:

- Lower ABA once per instance/task batch.
- Pass lowered AFs into the same kernel routing.
- Keep ABA-specific code limited to parsing/lowering/query mapping.

Done when:

- ABA has no separate preferred/stable hard-loop implementation.
- ICCMA ABA rows use the same utility names as AF rows after lowering.

### Phase 7: Benchmark gate

Tests first:

- Add deterministic benchmark fixtures from observed timeout families:
  `Small-result-*`, `T-1-afinput_exp_*`, `WS_100_*`, and ABA `aba_100/500`.
- Tests assert only structural metrics: solved/timeout status under a generous
  local cap is not a unit-test requirement.

Implementation:

- Add `tools/iccma_compare_solver_runs.py` to compare summaries and SAT-call
  utility counts between labels.
- Re-run cap-20 and cap-100 selected slices, then full year runs if the
  selected slices improve.

Done when:

- At least one kept benchmark reduction is measured before widening scope.
- If two consecutive slices produce no kept improvement on the same target,
  stop and report the failed target rather than switching randomly.

## 4. Paper map

- Cerutti, Dunne, Giacomin, Vallati 2013, "Computing Preferred Extensions in
  Abstract Argumentation: a SAT-based Approach": complete-labelling SAT and
  preferred strict-superset enumeration.
- Cerutti, Vallati, Giacomin 2015, "ArgSemSAT-1.0": complete labellings as the
  common SAT surface for complete, preferred, grounded, and stable.
- Dvorak, Jarvisalo, Wallner, Woltran 2014, "Complexity-Sensitive Decision
  Procedures for Abstract Argumentation": CEGAR-style SAT oracle loops,
  preferred strict-superset tests, and strict-range tests for semi-stable/stage.
- Pu, Ya, Luo 2017, "argmat-sat": range variables and assumption-space loops
  for preferred, ideal, semi-stable, and stage.
- Thimm, Cerutti, Vallati 2021, "Skeptical Reasoning with Preferred Semantics
  ... without Computing Preferred Extensions": CDAS for `DS-PR`, CDIS for
  ideal.
- Thimm, Cerutti, Vallati 2021, "Fudge": compact SAT solver architecture,
  incremental SAT, direct `DS-PR` and ideal encodings.

## 5. Papers still worth retrieving or rereading

- The online appendix for Thimm/Cerutti/Vallati 2021, especially the precise
  proof obligations for `AdmExtAtt` and CDIS.
- Longer ArgSemSAT papers cited by the 2015 system description, for complete
  labelling encoding choices.
- Fudge source, to compare its utility API and blocking strategy against the
  planned Python kernel.
- Recent mu-toksia descriptions, to compare direct skeptical preferred and
  ideal handling against the Fudge route.

## 6. Non-goals

- Do not add a second ABA hard-semantics solver.
- Do not add compatibility wrappers around old hard-semantics helpers.
- Do not route hard ICCMA tasks through native extension enumeration except as
  a small-instance oracle or explicit fallback.
- Do not optimize by raising row timeouts before reducing repeated SAT work.
- Do not claim paper rereads unless the page images are read directly.

## 7. Execution rule

Every implementation phase starts by adding failing tests or guard tests. Every
phase ends with:

```powershell
uv run pytest <targeted tests> -q
uv run pytest -q
```

and a path-limited commit for the exact files changed. Broad ICCMA runs happen
only after a targeted benchmark slice shows a kept improvement.
