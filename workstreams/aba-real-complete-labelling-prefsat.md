# ABA Real Complete-Labelling PrefSat Workstream

## Goal

Implement the real paper-defined ABA preferred SAT backend, not a nearby
existing-code approximation.

The deliverable is a three-valued complete-labelling PrefSat architecture for
ABA preferred reasoning, with operational contracts and benchmark gates that
make substitutes fail. A SAT-ish preferred route, a renamed CEGAR path, a greedy
growth loop, ASP optimization over complete extensions, or any other
semantically valid but structurally different path does not complete this
workstream.

## Non-Substitution Contract

This workstream is incomplete unless production code exposes the target
architecture itself:

- explicit `in`, `out`, and `undec` labelling variables or a documented
  one-to-one equivalent internal representation;
- complete-labelling constraints over the ABA structure;
- preferred maximality by paper-backed grow/block, subset blocking,
  counterexample search, or an explicitly cited equivalent;
- no eager minimal-support materialization for dense flat ABA rows;
- no filename, path, generator, year, ICCMA directory, or manifest-id routing;
- no wrapper that merely forwards preferred SAT to the old support-aware CEGAR
  maximality route;
- no ASP optimization route as a substitute for this SAT workstream.

Passing semantic preferred tests is not sufficient. Passing route tests is not
sufficient. Passing broad regression tests is not sufficient. Completion
requires the target architecture plus at least one benchmark-backed hard-row
improvement or an explicit failed-hypothesis record.

## Control Surface

- `reports/aba-preferred-salvage-inventory.md`
- `workstreams/aba-preferred-salvage-with-perf-contracts.md`
- `tests/test_performance_contracts.py`
- `tests/test_aba_route_properties.py`
- `tools/run_aba_hard_bucket.py`
- `tests/manifests/aba-hard-bucket-targets.json`

Generated JSON, CSV, logs, profiles, screenshots, caches, and timing exports
stay uncommitted unless explicitly requested.

## Paper Stack

Read page images directly before writing paper-derived production code or
tests. Notes can guide the reread; they are not a substitute.

- Cerutti, Dunne, Giacomin, and Vallati 2013: complete-labelling SAT,
  preferred maximality, candidate improvement, and subset blocking.
- Cerutti, Vallati, and Giacomin 2015: ArgSemSAT implementation surface for
  ICCMA-style complete, preferred, grounded, and stable tasks.
- Niskanen and Jarvisalo 2020: persistent SAT solver state, assumptions,
  iterative calls, and solver-engineering discipline.
- Lehtonen, Wallner, and Jarvisalo 2021: direct ABA fact surface and the
  warning against exponential AF translation.
- Egly, Gaggl, and Woltran 2010: maximality/saturation discipline and fixed
  input/query separation.
- Baroni and Giacomin 2005: SCC-recursive conditioning and directionality if
  the route needs structural decomposition.

Minimum page-image reread set before implementation:

- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-001.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-002.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png`
- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000005.png`
- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000006.png`
- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000012.png`

## Target Rows

Primary preferred hard rows:

| Target | Instance | Subtrack | Required signal |
|---|---|---|---|
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-PR` | preferred hard-row improvement |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-PR` | preferred hard-row improvement |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-PR` | preferred hard-row improvement |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-PR` | preferred hard-row improvement |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-PR` | preferred hard-row improvement |

Controls:

| Control | Instance | Subtrack | Required handling |
|---|---|---|---|
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | no fake SAT-only repair claim |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | preserve solved behavior |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | preserve solved behavior |

## Rejected Substitutes

The following are already known not to complete this workstream:

- greedy preferred growth from `experiment/aba-greedy-preferred-growth`;
- eager minimal-support complete-labelling from
  `experiment/aba-complete-labelling-prefsat-backend`;
- ranked native rule-closure refinement from
  `experiment/aba-native-rule-closure-prefsat`;
- ASP `#maximize` preferred search from
  `experiment/aba-asp-saturation-preferred`;
- removing the stable precheck and forwarding into existing support-aware CEGAR
  from `experiment/aba-preferred-maximality-backend`.

If any of these ideas is revisited, it must be introduced as a new hypothesis
with new operational contracts. It cannot be counted as this workstream's
complete-labelling PrefSat implementation.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Architecture Lock.
3. Phase 2: Paper-Image Reread.
4. Phase 3: Operational Contracts Before Code.
5. Phase 4: Experiment Branch.
6. Phase 5: Deletion-First Implementation.
7. Phase 6: Property and Regression Gate.
8. Phase 7: Targeted Hard-Row Gate.
9. Phase 8: Promotion or Failed-Hypothesis Record.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable before using it.

- [ ] Run the order check after every edit to this workstream.
- [ ] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-real-complete-labelling-prefsat.md
```

Expected result: every listed phase matches a phase heading in order.

## Phase 1: Architecture Lock

Goal: make the real target architecture a testable requirement.

- [ ] Write an architecture contract section in the tests or a source-adjacent
  module that names the required `in/out/undec` labelling surface.
- [ ] Add a test that fails if preferred SAT delegates directly to the old
  support-aware CEGAR maximality route.
- [ ] Add a test that fails if the route is ASP optimization, greedy growth, or
  filename/path/generator/ICCMA-based.
- [ ] Add a test or explicit code invariant that dense flat ABA rows do not
  eagerly materialize all minimal supports before invoking the SAT search.
- [ ] Cite the page-image paths that justify each architecture requirement.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: architecture-lock tests exist and fail only for missing real
PrefSat implementation, not for unrelated code.

## Phase 2: Paper-Image Reread

Goal: code from the page images, not memory or previous branch shape.

- [ ] Reread the Cerutti 2013 page images for complete-labelling variables,
  preferred maximality, and subset blocking.
- [ ] Reread the Cerutti 2015 page images for the ArgSemSAT implementation
  surface.
- [ ] Reread the Niskanen/Jarvisalo page images before using persistent SAT
  state, assumptions, preprocessing, or iterative calls.
- [ ] Reread the Lehtonen page images for the ABA input surface and direct ABA
  solving constraints.
- [ ] Record the exact page-image paths in the tests that encode each claim.

Gate:

```powershell
git diff -- tests src workstreams
```

Expected result: paper-cited tests/contracts are present before production
solver implementation.

## Phase 3: Operational Contracts Before Code

Goal: make performance learning executable before implementation.

- [ ] Add small Hypothesis families where complete-labelling PrefSat must make
  bounded candidate/blocking progress.
- [ ] Add a clause-growth or support-materialization contract that prevents the
  eager minimal-support explosion seen in failed branches.
- [ ] Add telemetry for SAT calls, candidate blocks, model candidates, and
  rejected supersets.
- [ ] Add residual-reduction checks for grow/block loops.
- [ ] Keep wall-clock checks calibrated or benchmark-only; do not make brittle
  uncalibrated time assertions.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_aba_route_properties.py
```

Expected result: operational contracts constrain the implementation path before
new preferred SAT production code exists.

## Phase 4: Experiment Branch

Goal: isolate speculative solver implementation.

- [ ] Confirm tracked files are clean.
- [ ] Create a dedicated experiment branch from `main`.
- [ ] Do not create worktrees, temporary clones, shadow repositories, or
  alternate checkouts.
- [ ] Leave unrelated untracked diagnostics alone.

Gate:

```powershell
git branch --show-current
git status --short --untracked-files=no
```

Expected result: clean tracked files on a dedicated experiment branch.

## Phase 5: Deletion-First Implementation

Goal: replace the overlapping failed production surface with real
complete-labelling PrefSat.

- [ ] Delete or disconnect the old preferred SAT production path that overlaps
  this route before adding compatibility wrappers.
- [ ] Implement explicit three-valued labelling variables or a documented
  one-to-one equivalent.
- [ ] Implement complete-labelling constraints directly over the ABA structure
  without exponential AF translation.
- [ ] Implement preferred maximality through paper-backed grow/block, subset
  blocking, counterexample search, or an explicitly cited equivalent.
- [ ] Use persistent solver state and assumptions only where justified by the
  reread Niskanen/Jarvisalo pages.
- [ ] Return the existing public ABA solver result shape.
- [ ] Keep implementation telemetry wired to the Phase 3 contracts.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: semantic, architecture, and operational contracts pass without
reviving any rejected substitute path.

## Phase 6: Property and Regression Gate

Goal: prove the implementation is correct before benchmark claims.

- [ ] Compare preferred witnesses and skeptical preferred answers against the
  brute-force oracle on generated small flat ABA frameworks.
- [ ] Check hand-built examples for maximality blocking and complete-labelling
  corner cases.
- [ ] Preserve C2 and C3 solved behavior in targeted status runs.
- [ ] Do not claim C1 is fixed unless the current branch actually solves it.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: correctness and route contracts pass before hard-row timing is
used as evidence.

## Phase 7: Targeted Hard-Row Gate

Goal: prove the real PrefSat path changes the measured hard class.

- [ ] Run T1/T3/T5/T6/T8 and C1/C2/C3 with `--no-profile` under the declared
  budget.
- [ ] Validate every newly solved preferred answer with the existing answer
  checker surface.
- [ ] If no primary preferred target improves, profile one representative
  changed SAT timeout with py-spy before recording failure.
- [ ] Record whether time is in Python, SAT solving, parsing, validation, model
  construction, or answer checking.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-real-prefsat-targeted.json --output-csv data\iccma\2025\runs\aba-real-prefsat-targeted.csv
```

Expected result: at least one primary preferred hard row improves under budget,
C2/C3 remain solved, and any generated diagnostics remain uncommitted unless
explicitly promoted.

## Phase 8: Promotion or Failed-Hypothesis Record

Goal: finish with either a real win or a precise failure.

If gates pass:

- [ ] Minimize the final diff to the real implementation, contracts, and
  deliberate documentation.
- [ ] Re-run Phase 6 and Phase 7 gates.
- [ ] Promote the minimal final diff to `main` with a clean commit or
  fast-forward merge.
- [ ] Keep generated diagnostics uncommitted unless explicitly requested.

If gates fail:

- [ ] Do not promote the experiment branch.
- [ ] Record the exact failed paper claim, contract, target row, profiler
  attribution, and next hypothesis.
- [ ] Make clear whether true complete-labelling PrefSat failed, or whether the
  implementation still did not meet the architecture lock.

Gate:

```powershell
git status --short --untracked-files=no
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: a promoted real PrefSat implementation, or an explicit failed
hypothesis record that cannot be confused with a completed substitute.

## Definition of Done

This workstream is complete only when one of these is true:

- the real complete-labelling PrefSat architecture is implemented, at least one
  primary preferred hard row improves under the benchmark budget, C2/C3 are
  preserved, and the minimal diff is promoted to `main`; or
- a failed-hypothesis record proves that the implementation satisfied the
  architecture lock and still failed, with profiler evidence and the next
  concrete hypothesis.

If production code does not satisfy the architecture lock, the workstream is
not a failed PrefSat experiment. It is an implementation failure and must not be
counted as evidence against the paper architecture.
