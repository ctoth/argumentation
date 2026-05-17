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

- explicit Boolean labelling variables named or surfaced as
  `prefsat_in[assumption]`, `prefsat_out[assumption]`, and
  `prefsat_undec[assumption]` for every assumption in the SAT solver universe;
- exactly-one labelling constraints for every assumption:
  `prefsat_in[a] xor prefsat_out[a] xor prefsat_undec[a]`;
- complete-labelling constraints over the ABA attack/defence relation:
  every `in` assumption is defended, every `out` assumption is attacked by an
  `in` assumption, and every defended undecided assumption can be forced `in`
  by a maximality check;
- preferred maximality through a SAT grow/block loop with subset-blocking
  clauses over the `prefsat_in[...]` variables;
- no eager minimal-support materialization for dense flat ABA rows;
- no filename, path, generator, year, ICCMA directory, or manifest-id routing;
- no wrapper that merely forwards preferred SAT to the old support-aware CEGAR
  maximality route;
- no ASP optimization route as a substitute for this SAT workstream.

Passing semantic preferred tests is not sufficient. Passing route tests is not
sufficient. Passing broad regression tests is not sufficient. Completion
requires the target architecture plus at least one primary preferred hard row
with `status == "solved"` and `validation.status == "valid"` under 30 seconds,
or an explicit failed-hypothesis record.

An implementation that uses different internal names must expose an adapter in
`src/argumentation/aba_sat.py` that returns these exact architecture fields for
tests. Without that adapter, the implementation fails Phase 1.

## Required Telemetry Fields

The implementation must emit these integer telemetry keys for every preferred
SAT solve attempt:

- `prefsat_labelling_variables`
- `prefsat_exactly_one_clauses`
- `prefsat_complete_clauses`
- `prefsat_support_materializations`
- `prefsat_solver_checks`
- `prefsat_candidate_models`
- `prefsat_candidate_blocks`
- `prefsat_rejected_supersets`
- `prefsat_max_in_count_seen`
- `prefsat_final_in_count`

The no-eager-support contract is literal:
`prefsat_support_materializations == 0` for dense flat ABA route candidates.

The small-family operational contract is numeric:
for generated flat ABA frameworks with at most 8 assumptions, at most 16 rules,
and rule bodies of size at most 3,
`prefsat_solver_checks <= 2 * prefsat_candidate_blocks + 4`,
`prefsat_candidate_models <= prefsat_candidate_blocks + 2`, and
`prefsat_candidate_blocks <= len(assumptions) + 2`.

The clause-growth contract is numeric:
`prefsat_exactly_one_clauses == len(assumptions)`,
`prefsat_labelling_variables == 3 * len(assumptions)`, and
`prefsat_complete_clauses <= 24 * (len(assumptions) + len(rules) + attack_edge_count)`.
If `attack_edge_count` is not already computable without exponential
translation, Phase 3 must add a reusable structural counter before production
implementation.

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
  preferred maximality, candidate grow steps, and subset-blocking clauses.
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
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-PR` | `sat` or `auto` solved under 30s with validation status `valid` |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-PR` | `sat` or `auto` solved under 30s with validation status `valid` |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-PR` | `sat` or `auto` solved under 30s with validation status `valid` |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-PR` | `sat` or `auto` solved under 30s with validation status `valid` |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-PR` | `sat` or `auto` solved under 30s with validation status `valid` |

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

- [x] Run the order check after every edit to this workstream.
- [x] Before each later phase, reread this file and identify the next unchecked
  item.

Execution status:

- Phase order gate passed.
- Next unchecked item is Phase 1: Architecture Lock.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-real-complete-labelling-prefsat.md
```

Expected result: every listed phase matches a phase heading in order.

## Phase 1: Architecture Lock

Goal: make the real target architecture a testable requirement.

- [x] Add `tests/test_aba_real_prefsat_contract.py`.
- [x] Add `test_real_prefsat_exposes_three_valued_labelling_surface`, asserting
  the architecture fields `prefsat_in`, `prefsat_out`, and `prefsat_undec`
  exist and contain one entry per assumption.
- [x] Add `test_real_prefsat_rejects_old_cegar_forwarding`, monkeypatching the
  old support-aware CEGAR preferred entrypoint and asserting the real PrefSat
  route does not call it.
- [x] Add `test_real_prefsat_rejects_asp_and_greedy_substitutes`, asserting the
  route metadata has `backend == "sat"` and
  `algorithm == "complete-labelling-prefsat"`.
- [x] Add `test_real_prefsat_route_ignores_filename_and_manifest_identity`,
  asserting route decisions are identical when only path, year, target id, and
  generator-like text change.
- [x] Add `test_dense_flat_real_prefsat_does_not_materialize_minimal_supports`,
  asserting `prefsat_support_materializations == 0`.
- [x] Store page-image citations in a test constant named
  `REAL_PREFSAT_PAGE_IMAGES` and assert it contains every page listed in this
  workstream's minimum reread set.

Execution status:

- Added `tests/test_aba_real_prefsat_contract.py`.
- Contract file collection passed: `10 tests collected in 0.60s`.
- Phase 1 gate passed: `18 passed, 1 skipped in 2.86s`.
- Next unchecked item is Phase 2: Paper-Image Reread.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: these named tests exist. Before implementation, tests that
require the real PrefSat surface may fail with `NotImplementedError` or an
explicit missing-route assertion. They must not be skipped, xfailed, or written
as semantic-only tests.

## Phase 2: Paper-Image Reread

Goal: code from the page images, not memory or previous branch shape.

- [x] Reread the Cerutti 2013 page images for complete-labelling variables,
  preferred maximality, and subset blocking.
- [x] Reread the Cerutti 2015 page images for the ArgSemSAT implementation
  surface.
- [x] Reread the Niskanen/Jarvisalo page images before using persistent SAT
  state, assumptions, preprocessing, or iterative calls.
- [x] Reread the Lehtonen page images for the ABA input surface and direct ABA
  solving constraints.
- [x] Record the exact page-image paths in `REAL_PREFSAT_PAGE_IMAGES`.
- [x] For each paper-derived assertion in
  `tests/test_aba_real_prefsat_contract.py`, include the page-image path in the
  assertion message or parametrization id.

Execution status:

- Reread all required page images directly.
- Cerutti 2013/2015 pages confirm complete-labelling SAT, inner strict grow,
  and outer subset-blocking structure.
- Niskanen/Jarvisalo pages confirm persistent SAT state and assumption-style
  iterative solver use.
- Lehtonen pages confirm direct ABA fact/complete-set surface and avoiding
  argument-construction blow-up.
- Phase 2 diff gate was clean before production solver implementation.
- Next unchecked item is Phase 3: Operational Contracts Before Code.

Gate:

```powershell
git diff -- tests src workstreams
```

Expected result: `tests/test_aba_real_prefsat_contract.py` is the only changed
test file in this phase, and no production solver implementation has been
added yet.

## Phase 3: Operational Contracts Before Code

Goal: make performance learning executable before implementation.

- [x] Add a Hypothesis strategy named `small_flat_aba_for_real_prefsat` covering
  at most 8 assumptions, at most 16 rules, body size at most 3, cycles,
  contrary chains, empty bodies, unused literals, and multiple complete
  extensions.
- [x] Add a contract asserting
  `prefsat_solver_checks <= 2 * prefsat_candidate_blocks + 4`,
  `prefsat_candidate_models <= prefsat_candidate_blocks + 2`, and
  `prefsat_candidate_blocks <= len(assumptions) + 2` on that family.
- [x] Add a clause-growth contract asserting
  `prefsat_labelling_variables == 3 * len(assumptions)`,
  `prefsat_exactly_one_clauses == len(assumptions)`, and
  `prefsat_complete_clauses <= 24 * (len(assumptions) + len(rules) + attack_edge_count)`.
- [x] Add a dense-flat contract asserting
  `prefsat_support_materializations == 0`.
- [x] Add residual-reduction checks asserting every accepted grow/block
  iteration either increases `prefsat_max_in_count_seen` or increments
  `prefsat_candidate_blocks`; two consecutive iterations with neither change
  fail the test.
- [x] Keep wall-clock checks calibrated or benchmark-only; do not make brittle
  uncalibrated time assertions.

Execution status:

- Operational contracts are in `tests/test_aba_real_prefsat_contract.py`.
- Contract file collection passed: `10 tests collected in 0.59s`.
- Phase 3 gate passed: `18 passed, 1 skipped in 2.29s`.
- No production solver implementation diff existed before Phase 4.
- Next unchecked item is Phase 4: Experiment Branch.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_performance_contracts.py tests\test_aba_route_properties.py
```

Expected result: all required telemetry field names are asserted by tests
before new preferred SAT production code exists.

## Phase 4: Experiment Branch

Goal: isolate speculative solver implementation.

- [ ] Confirm tracked files are clean.
- [ ] Create the dedicated experiment branch
  `experiment/aba-real-complete-labelling-prefsat` from `main`.
- [ ] Do not create worktrees, temporary clones, shadow repositories, or
  alternate checkouts.
- [ ] Leave unrelated untracked diagnostics alone.

Gate:

```powershell
git branch --show-current
git status --short --untracked-files=no
```

Expected result: clean tracked files on
`experiment/aba-real-complete-labelling-prefsat`.

## Phase 5: Deletion-First Implementation

Goal: replace the overlapping failed production surface with real
complete-labelling PrefSat.

- [ ] Delete or disconnect the old preferred SAT production path that overlaps
  this route before adding compatibility wrappers. The first implementation
  commit must remove that call edge, and tests/search failures become the work
  queue.
- [ ] Implement explicit three-valued labelling variables exposed as
  `prefsat_in`, `prefsat_out`, and `prefsat_undec`.
- [ ] Implement complete-labelling constraints directly over the ABA structure
  without exponential AF translation.
- [ ] Implement preferred maximality through a SAT grow/block loop over
  `prefsat_in[...]` variables, adding one subset-blocking clause per rejected
  candidate.
- [ ] Use persistent solver state and assumptions only where justified by the
  reread Niskanen/Jarvisalo pages.
- [ ] Return the existing public ABA solver result shape.
- [ ] Keep implementation telemetry wired to the Phase 3 contracts.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: semantic, architecture, and operational contracts pass; `rg`
confirms the real preferred route does not call the rejected old CEGAR
preferred entrypoint.

## Phase 6: Property and Regression Gate

Goal: prove the implementation is correct before benchmark claims.

- [ ] Compare preferred witnesses and skeptical preferred answers against the
  brute-force oracle on generated small flat ABA frameworks.
- [ ] Check hand-built examples for maximality blocking and complete-labelling
  corner cases.
- [ ] Preserve C2 and C3 solved behavior in targeted status runs using:
  `uv run tools\run_aba_hard_bucket.py --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-real-prefsat-controls.json --output-csv data\iccma\2025\runs\aba-real-prefsat-controls.csv`.
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
- [ ] Validate every newly solved preferred answer through
  `tools/aba_shape_benchmark.py::validate_result`, as recorded in each
  hard-bucket JSON row's `validation` field.
- [ ] A primary hard row counts as solved only if its row has
  `status == "solved"` and `validation.status == "valid"` for backend `sat` or
  `auto`.
- [ ] If `validation.status` is `not_checked`, that row does not count as a
  win; add or fix validation before promotion.
- [ ] If no primary preferred target counts as solved, profile T1 with the
  exact profiling command below before recording failure.
- [ ] Record whether time is in Python, SAT solving, parsing, validation, model
  construction, or answer checking.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-real-prefsat-targeted.json --output-csv data\iccma\2025\runs\aba-real-prefsat-targeted.csv
```

Profile command if no primary row counts as solved:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --backend sat --subtrack SE-PR --timeout-seconds 30 --profile-duration-seconds 25 --profile-format speedscope --profile-dir data\iccma\2025\profiles\aba-real-prefsat --output-json data\iccma\2025\runs\aba-real-prefsat-t1-profile.json --output-csv data\iccma\2025\runs\aba-real-prefsat-t1-profile.csv
```

Expected result: at least one primary preferred hard row has `status ==
"solved"` and `validation.status == "valid"` under 30 seconds for backend
`sat` or `auto`, C2/C3 remain solved, and generated diagnostics remain
uncommitted unless explicitly promoted.

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
  attribution, and next hypothesis in
  `reports/aba-real-prefsat-failure.md`.
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
  primary preferred hard row has `status == "solved"` and
  `validation.status == "valid"` under 30 seconds for backend `sat` or `auto`,
  C2/C3 are preserved, and the minimal diff is promoted to `main`; or
- a failed-hypothesis record proves that the implementation satisfied the
  architecture lock and still failed, with profiler evidence and the next
  concrete hypothesis.

If production code does not satisfy the architecture lock, the workstream is
not a failed PrefSat experiment. It is an implementation failure and must not be
counted as evidence against the paper architecture.
