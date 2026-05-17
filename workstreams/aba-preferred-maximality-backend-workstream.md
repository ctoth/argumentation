# ABA Preferred Maximality Backend Workstream

## Goal

Solve the measured ABA hard-row problem by changing the search formulation, not
by adding filename routes or shaving Python overhead that profiling already
showed is not the bottleneck.

This workstream starts from the current `main` state after removal of the failed
direct-stable experiment. The expected output is one of:

- a paper-backed backend change that solves at least one preferred hard target
  under the 30-second budget while resolving the C1 stable-control issue and
  preserving C2/C3; or
- a failed experiment branch with page-image citations, property tests,
  benchmark output, and profiler evidence precise enough to choose the next
  backend hypothesis.

Because this is speculative, benchmark-driven implementation work, run
implementation slices on a dedicated experiment branch from a clean tracked
base unless the user explicitly overrides that branch rule.

## Control Surface

This workstream is controlled by:

- [ABA hard-bucket backend work item](aba-hard-bucket-backend-work-item.md)
- [ABA hard-bucket backend execution record](aba-hard-bucket-backend-execution.md)
- `tests/manifests/aba-hard-bucket-targets.json`
- `data/iccma/2025/runs/aba-hard-bucket-phase2-profile-findings.md`
- `data/iccma/2025/runs/aba-hard-bucket-phase4-direct-stable.json`

Generated JSON, CSV, speedscope profiles, logs, screenshots, caches, and other
diagnostic artifacts stay uncommitted unless the user explicitly asks to promote
them.

## Current Evidence

The prior profiling result is a routing constraint:

- preferred hard rows spend almost all sampled time under clingo C calls from
  the current multishot ASP route;
- the direct stable ASP witness experiment preserved property tests but did not
  solve any T1-T9 row under the hard-bucket benchmark gate;
- C1 stable control is not currently preserved by the measured hard-bucket
  status runs and must be treated as a real issue, not ignored;
- therefore the next winning move is a preferred maximality/search-formulation
  slice, with C1 repaired or explicitly rebaselined from evidence.

No production predicate may inspect filenames, generator names, ICCMA year, or
directory text except to open the input file. Filenames may appear only in
manifests, diagnostics, tests that identify benchmark rows, and this workstream.

## Target Rows

Primary preferred targets:

| Target | Instance | Subtrack | Role |
|---|---|---|---|
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-PR` | preferred all-timeout |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-PR` | preferred all-timeout |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-PR` | preferred all-timeout |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-PR` | preferred all-timeout |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-PR` | preferred all-timeout |

Stable rows are secondary regression targets:

| Target | Instance | Subtrack | Role |
|---|---|---|---|
| T2 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-ST` | stable all-timeout |
| T4 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-ST` | stable all-timeout |
| T7 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-ST` | stable all-timeout |
| T9 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-ST` | stable all-timeout |

Mandatory controls:

| Control | Instance | Subtrack | Required handling |
|---|---|---|---|
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | repair, reroute with evidence, or explicitly rebaseline |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | preserve solved behavior |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | preserve solved behavior |

## Paper Stack

Read page images directly before coding claims from a paper. Notes may guide
where to look; notes are not a substitute for rereading the relevant pages.

- Lehtonen, Wallner, and Jarvisalo 2021: direct ABA ASP fact surface,
  incremental solving, complete/stable/preferred encodings, and the warning
  against exponential AF translation.
- Egly, Gaggl, and Woltran 2010: ASPARTIX modular encodings, saturation for
  maximality-style semantics, fixed input/query separation, and splitting
  discipline.
- Cerutti, Dunne, Giacomin, and Vallati 2013: complete-labelling SAT,
  preferred-extension maximality, candidate blocking, and empirical sensitivity
  to encoding details.
- Cerutti, Vallati, and Giacomin 2015: ArgSemSAT implementation surface for
  ICCMA-style complete, preferred, grounded, and stable tasks.
- Niskanen and Jarvisalo 2020: persistent SAT solver state, assumptions,
  iterative calls, unit-propagation preprocessing, and ICCMA solver engineering.
- Baroni and Giacomin 2005: SCC-recursive directionality, conditioning sets,
  and the limits of solving a framework as one undifferentiated component.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Clean Base and Experiment Branch.
3. Phase 2: Paper-Image Preflight.
4. Phase 3: Baseline and Runner Reliability.
5. Phase 4: Property Tests Before Backend Code.
6. Phase 5: Preferred Maximality Backend Slice.
7. Phase 6: C1 Stable Control Resolution.
8. Phase 7: Targeted Benchmark Gate.
9. Phase 8: Full Hard-Bucket Gate.
10. Phase 9: Promotion or Failed-Hypothesis Record.

Every phase has a gate. Passing tests before the current phase gate does not
complete the workstream.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable before using it as a control
surface.

- [ ] Run the order check after every edit to this workstream.
- [ ] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-preferred-maximality-backend-workstream.md
```

Expected result: every listed phase matches an actual phase heading in the same
order.

## Phase 1: Clean Base and Experiment Branch

Goal: isolate speculative implementation from `main` unless the user explicitly
overrides the branch rule.

- [ ] Check tracked-file cleanliness.
- [ ] If tracked files are dirty, stop and report the exact paths.
- [ ] Create a dedicated experiment branch from the clean base.
- [ ] Do not add unrelated untracked files.

Gate:

```powershell
git status --short --untracked-files=no
git switch -c experiment/aba-preferred-maximality-backend
git status --short --untracked-files=no
```

Expected result: a clean tracked base on the experiment branch.

## Phase 2: Paper-Image Preflight

Goal: choose one backend hypothesis from paper pages, not from memory or notes.

- [ ] Read the relevant Lehtonen page images for ABA facts, incremental
  complete/stable/preferred behavior, and empirical setup.
- [ ] Read the relevant Egly page images before choosing an ASP saturation
  implementation.
- [ ] Read the relevant Cerutti 2013/2015 page images before choosing a SAT
  complete-labelling/maximality implementation.
- [ ] Read the relevant Niskanen/Jarvisalo page images before using persistent
  SAT assumptions or unit-propagation preprocessing.
- [ ] Read the Baroni/Giacomin page images before using SCC conditioning or
  directionality.
- [ ] Record the exact page-image paths in the new property tests or test
  metadata that exercise the chosen algorithm.
- [ ] Select exactly one implementation hypothesis for Phase 5:
  `sat-complete-labelling-maximality` or `asp-saturation-maximality`.

Gate:

```powershell
git diff -- tests src tools workstreams
```

Expected result: no backend implementation code yet; only deliberate paper
metadata/test scaffolding edits if the phase records them in source.

## Phase 3: Baseline and Runner Reliability

Goal: verify the current hard-row facts with a runner that does not confuse
status runs with py-spy profile plumbing.

- [ ] If `tools\run_aba_hard_bucket.py` cannot run target-id status checks
  without profiling, add a `--no-profile` or equivalent explicit status mode
  first.
- [ ] Reproduce current T1/T3/T5/T6/T8 and C1/C2/C3 behavior under the
  30-second budget.
- [ ] If a baseline contradicts this workstream, update the target table before
  implementing backend code.
- [ ] If C1 is already solved in the current clean baseline, record the command
  and treat C1 as a preservation control.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-preferred-maximality-baseline.json --output-csv data\iccma\2025\runs\aba-preferred-maximality-baseline.csv
```

Expected result: status evidence for each target/control row, with generated
diagnostics left uncommitted.

## Phase 4: Property Tests Before Backend Code

Goal: make the semantic and routing invariants executable before optimizing.

- [ ] Add Hypothesis generators for small flat ABA frameworks that exercise
  cycles, contraries, empty bodies, multi-body rules, unused literals, and
  multiple complete extensions.
- [ ] Add a brute-force small-framework oracle for admissible, complete,
  stable, and preferred semantics if no existing oracle covers the needed
  assertions.
- [ ] Test that any returned preferred witness is admissible and complete.
- [ ] Test that any returned preferred witness has no strict admissible or
  complete superset, matching the selected paper definition.
- [ ] Test skeptical preferred answers against the brute-force oracle on small
  generated flat ABA frameworks.
- [ ] Test candidate-blocking or saturation clauses against hand-built examples
  from the paper pages.
- [ ] Test that backend selection uses structural shape fields only, not
  filename, generator, year, or path text.
- [ ] If Phase 5 touches stable SAT code, add C1-shaped stable witness
  preservation properties before making that code change.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_route_properties.py
```

Expected result: new tests fail only for the missing backend behavior, not for
unrelated existing semantics.

## Phase 5: Preferred Maximality Backend Slice

Goal: implement one chosen preferred-maximality search formulation and no
parallel competing backend in the same slice.

If Phase 2 selects `sat-complete-labelling-maximality`:

- [ ] Implement complete-labelling variables and constraints over the ABA
  structure without translating to an exponentially larger AF.
- [ ] Use persistent solver state and assumptions only where the page-read
  Niskanen/Cerutti evidence justifies it.
- [ ] Implement maximality by iterative candidate improvement or blocking
  clauses, matching the paper-backed property tests.
- [ ] Return the same public result shape expected by the existing ABA solver
  callers.

If Phase 2 selects `asp-saturation-maximality`:

- [ ] Implement the saturation/maximality encoding as a replacement candidate
  for preferred hard rows, not as a filename special case.
- [ ] Keep input facts separate from query/semantics rules.
- [ ] Add only structural route predicates, such as giant cyclic component,
  high preferred-maximality risk, or complete-extension explosion indicators.
- [ ] Return the same public result shape expected by the existing ABA solver
  callers.

For either hypothesis:

- [ ] Delete or replace obsolete production surface touched by the change
  instead of adding compatibility wrappers.
- [ ] Keep generated diagnostics uncommitted.
- [ ] Commit source/test edits atomically by intentionally owned paths.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
```

Expected result: property and regression tests pass before any speed claim.

## Phase 6: C1 Stable Control Resolution

Goal: resolve the known C1 discrepancy as a first-class issue.

- [ ] Re-run C1 alone under `auto`, `asp`, and `sat` with the current branch.
- [ ] If C1 fails only through the SAT stable path, inspect the SAT stable
  witness construction and repair it with a property test.
- [ ] If C1 is better handled by another existing backend, add a structural
  route only if it is not filename/generator/year/path based.
- [ ] If the earlier C1 premise was wrong in current repo state, stop this
  phase, record the exact command output, and update this workstream instead of
  coding a fake fix.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id C1 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-c1-resolution.json --output-csv data\iccma\2025\runs\aba-c1-resolution.csv
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_shape_benchmark.py
```

Expected result: C1 is solved, rerouted from structural evidence, or explicitly
rebaselined with proof that the old premise no longer applies.

## Phase 7: Targeted Benchmark Gate

Goal: prove the new backend changes real hard-row runtime, not just tests.

- [ ] Run preferred targets T1/T3/T5/T6/T8 and controls C1/C2/C3 under 30
  seconds.
- [ ] Validate every solved answer with the existing answer checker surface.
- [ ] Capture backend, algorithm, elapsed time, validation status, and page
  metadata in the diagnostic output.
- [ ] If the run times out, profile one representative row with py-spy and
  summarize whether the time is in Python, clingo, SAT, validation, parsing, or
  answer construction.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-preferred-maximality-targeted.json --output-csv data\iccma\2025\runs\aba-preferred-maximality-targeted.csv
```

Expected result: at least one of T1/T3/T5/T6/T8 solves under 30 seconds, C2 and
C3 remain solved, and C1 is resolved as required by Phase 6.

## Phase 8: Full Hard-Bucket Gate

Goal: make sure the targeted win does not break the rest of the hard bucket.

- [ ] Run T1-T9 and C1-C3 under `auto`, `asp`, and `sat` as applicable.
- [ ] Compare against the phase-2 and phase-4 diagnostics.
- [ ] Keep any generated JSON/CSV/profile output uncommitted unless explicitly
  requested.
- [ ] If two consecutive implementation slices on the same target produce no
  kept improvement, stop and report that plainly instead of broadening the
  search surface.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-preferred-maximality-full-hard-bucket.json --output-csv data\iccma\2025\runs\aba-preferred-maximality-full-hard-bucket.csv
```

Expected result: at least one current preferred all-timeout row is solved under
30 seconds, controls are resolved/preserved, and no solved control regresses.

## Phase 9: Promotion or Failed-Hypothesis Record

Goal: finish the experiment cleanly.

If the gates pass:

- [ ] Minimize the final diff to source, tests, and deliberate documentation.
- [ ] Re-run the targeted tests and hard-bucket gate.
- [ ] Promote the minimal final diff to `main` with a clean commit or clean
  merge, respecting unrelated worktree changes.
- [ ] Leave diagnostic artifacts uncommitted unless explicitly requested.

If the gates fail:

- [ ] Do not promote the experiment branch.
- [ ] Record the failed hypothesis, page citations, failing targets, profiler
  attribution, and the next concrete hypothesis in this workstream or a new
  workstream.
- [ ] Switch away from the failed experiment branch only when doing so does not
  overwrite tracked or untracked work.

Gate:

```powershell
git status --short --untracked-files=no
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
```

Expected result: either a promoted passing implementation or a clearly recorded
failed hypothesis with no failed optimization left on `main`.

## Definition of Done

This workstream is complete only when one of these is true:

- a paper-image-cited backend implementation solves at least one preferred hard
  target under 30 seconds, C1 is resolved, C2/C3 are preserved, and the source
  changes are promoted cleanly; or
- the selected backend hypothesis fails and the failure record names the exact
  paper claim, property, target row, profiler finding, and next hypothesis.
