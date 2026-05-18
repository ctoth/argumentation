# ABA Decomposed PrefSat Composition Workstream

## Goal

Make preferred ABA solving faster by composing the real complete-labelling
PrefSat kernel with exact residual shrinking, certified decomposition, and
persistent SAT state.

The deliverable is not another preferred solver variant. The deliverable is a
production composition layer that proves, through properties and telemetry, that
large preferred ABA instances are reduced before the expensive real PrefSat
kernel is called, and that every lifted answer validates against the original
ABA framework.

## Exact Final State

Production code must expose these surfaces:

- `src/argumentation/aba_decomposition.py`
  - `AbaDecompositionPlan`
  - `AbaComponentJob`
  - `AbaDecomposedPrefSatResult`
  - `plan_decomposed_prefsat(framework: ABAFramework) -> AbaDecompositionPlan`
  - `decomposed_prefsat_extension(framework: ABAFramework) -> AbaDecomposedPrefSatResult`
- `src/argumentation/aba_sat.py`
  - `sat_support_extension(..., semantics="preferred", require_derived=None,
    require_not_derived=None, require_assumptions=frozenset())` routes through
    `decomposed_prefsat_extension`, not directly through `real_prefsat_extension`.
  - `real_prefsat_extension` remains the single-component kernel.
- `tools/aba_shape_benchmark.py`
  - shape routing emits a production `decomposed_prefsat` route entry for large
    dense preferred ABA shapes when the decomposition contract reports reduction.
- `tests/test_aba_decomposed_prefsat_contract.py`
  - properties below are implemented before production code is accepted.

The implementation is complete only when either:

- at least one primary preferred hard row is solved under 30 seconds by backend
  `sat` or `auto` with `validation.status == "valid"`, C1/C2/C3 controls remain
  solved, and the minimal final diff is promoted to `main`; or
- a failed-hypothesis record proves that the composition layer satisfied the
  contract, skipped the old bad paths, still failed the hard-row gate, and names
  the next concrete bottleneck from profiling.

## Non-Substitution Contract

This workstream is incomplete if production code does any of the following:

- routes large dense preferred ABA directly to full-instance
  `real_prefsat_extension` before trying the decomposition plan;
- uses filename, path, year, manifest id, target id, or ICCMA directory text for
  routing;
- translates the whole ABA framework to a Dung AF with `aba_to_dung`;
- materializes all ABA arguments, all minimal supports, or a full powerset of
  assumptions for large dense route decisions;
- calls the old support-aware preferred CEGAR route as the preferred no-query
  production path;
- treats a local component answer as complete before validating the lifted
  answer against the original framework;
- adds a wrapper around the direct real PrefSat call without proving residual or
  component reduction through telemetry.

## Exact Deletion Targets

Delete this production path from `src/argumentation/aba_sat.py`:

```python
if semantics == "preferred" and require_derived is None and require_not_derived is None:
    return real_prefsat_extension(...).extension
```

Replace it with a direct call to `decomposed_prefsat_extension`. The
single-component/no-reduction case lives inside `decomposed_prefsat_extension`
and emits no-reduction telemetry before calling `real_prefsat_extension` once.

Do not delete the query-constrained preferred route in this workstream:

```python
_sat_preferred_extension_satisfying(...)
```

That path is outside the no-query production surface owned here.

## Owner Boundaries

Owned source paths:

- `src/argumentation/aba_decomposition.py`
- `src/argumentation/aba_sat.py`
- `tools/aba_shape_benchmark.py`

Owned tests:

- `tests/test_aba_decomposed_prefsat_contract.py`
- targeted edits in `tests/test_aba_real_prefsat_contract.py` only when needed
  to assert composition does not weaken the existing PrefSat kernel contract.

Owned documentation:

- this workstream;
- `reports/aba-decomposed-prefsat-failure.md` only if the hard-row gate fails.

Generated JSON, CSV, logs, profiles, caches, screenshots, and timing exports
stay uncommitted. Commit them only when the user explicitly requests artifact
promotion.

## Required Telemetry

`AbaDecomposedPrefSatResult.telemetry` must contain these integer keys:

- `decomp_original_assumptions`
- `decomp_original_rules`
- `decomp_residual_assumptions`
- `decomp_residual_rules`
- `decomp_component_count`
- `decomp_max_component_assumptions`
- `decomp_max_component_rules`
- `decomp_prefsat_component_calls`
- `decomp_full_instance_prefsat_calls`
- `decomp_solver_checks`
- `decomp_lifted_extension_size`
- `decomp_validation_success`

It must also contain this string key:

- `decomp_no_reduction_reason`

Allowed `decomp_no_reduction_reason` values:

- `reduced`
- `empty_residual`
- `single_component`
- `component_plan_not_exact`

Numeric invariants:

- `decomp_original_assumptions == len(framework.assumptions)`
- `decomp_original_rules == len(framework.rules)`
- `decomp_residual_assumptions <= decomp_original_assumptions`
- `decomp_residual_rules <= decomp_original_rules`
- if `decomp_no_reduction_reason == "reduced"`, then
  `decomp_full_instance_prefsat_calls == 0`
- if `decomp_no_reduction_reason != "reduced"`, then
  `decomp_full_instance_prefsat_calls == 1`
- `decomp_prefsat_component_calls == decomp_component_count` when
  `decomp_no_reduction_reason == "reduced"`
- `decomp_max_component_assumptions < decomp_original_assumptions` when
  `decomp_no_reduction_reason == "reduced"`
- `decomp_validation_success == 1` for every returned extension

## Exact Decomposition Certificate

The first production decomposition certificate is an exact independent-product
certificate over the residual ABA proof/contrary incidence graph.

Build an undirected graph whose nodes are residual assumptions and residual
non-assumption literals. Add edges:

- between every rule consequent and every rule antecedent;
- between every assumption and its contrary literal;
- between an assumption and every rule literal equal to that assumption.

A component job contains the residual assumptions in one connected component
and every residual rule whose literals are all in that component. The plan is
exact only when every residual rule belongs to exactly one component and every
residual assumption's contrary literal is in the same component as the
assumption. If this condition fails, the plan must set
`decomp_no_reduction_reason == "component_plan_not_exact"` and call
`real_prefsat_extension` once on the residual.

This certificate is deliberately narrower than full SCC-recursive ABA
conditioning. It is exact for independent residual products, and the hard-row
gate determines whether that exact product split plus persistent kernel reuse is
enough. A separate SCC-conditioning workstream must add a separate paper-derived
certificate before it can split cross-component attacks.

## Paper Stack

Read page images directly before writing paper-derived production code or
tests. Notes can guide rereading; they do not replace page images.

- Cerutti, Dunne, Giacomin, and Vallati 2013: complete-labelling PrefSat kernel,
  model growth, and subset blocking.
- Cerutti, Vallati, and Giacomin 2015: ArgSemSAT implementation surface.
- Niskanen and Jarvisalo 2020: persistent solver state and solver calls under
  assumptions.
- Lehtonen, Wallner, and Jarvisalo 2021: direct ABA facts and the warning
  against exponential AF translation.
- Egly, Gaggl, and Woltran 2010: fixed input/query separation and
  maximality/saturation discipline.

Required page-image outputs before implementation:

- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-001.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-002.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-005.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-006.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-012.png`
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-019.png`
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-020.png`

Phase 1 owns creating missing `pngs/page-*.png` outputs above for the exact
paper titles listed in the Paper Stack. Source implementation cannot start
until those files exist and have been read directly. Do not replace page-image
reading with text extraction.

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
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | remains solved; no preferred-route claim |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | remains solved by production portfolio |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | remains solved by production portfolio |

These rows are gates only. Production routing must use shape and decomposition
telemetry, never target identity.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Paper-Image and Asset Gate.
3. Phase 2: Hypothesis Contracts Before Code.
4. Phase 3: Experiment Branch.
5. Phase 4: Deletion-First Route Change.
6. Phase 5: Exact Decomposition Planner.
7. Phase 6: Decomposed PrefSat Composition.
8. Phase 7: Shape Routing Integration.
9. Phase 8: Property and Regression Gate.
10. Phase 9: Targeted Hard-Row Gate.
11. Phase 10: Promotion or Failed-Hypothesis Record.

## Phase 0: Workstream Order Guard

Goal: prove this checklist is mechanically ordered before implementation.

- [x] Run the order check after every edit to this workstream.
- [x] Before each subsequent phase, reread this file and identify the next unchecked
  item.

Execution status:

- Phase order gate passed.
- Next unchecked item is Phase 1: Paper-Image and Asset Gate.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-decomposed-prefsat-composition.md
```

Expected result: every listed phase matches a phase heading in order.

## Phase 1: Paper-Image and Asset Gate

Goal: verify the cited paper pages exist before coding from them.

- [x] Create missing page-image outputs for the exact paper titles in the Paper
  Stack.
- [x] Verify every required page-image output path in this workstream exists.
- [x] Read the listed page images directly.
- [x] Add `DECOMPOSED_PREFSAT_PAGE_IMAGES` to
  `tests/test_aba_decomposed_prefsat_contract.py` and assert every listed path
  exists.

Execution status:

- Existing `pngs/page-*.png` page images were found with filesystem inventory,
  including ignored/generated files.
- Required page images were read directly.
- Page-image contract gate passed.
- Next unchecked item is Phase 2: Hypothesis Contracts Before Code.

Gate:

```powershell
uv run pytest -q --timeout=120 tests\test_aba_decomposed_prefsat_contract.py -k page_image
```

Expected result: page-image contract passes, or implementation stops before
source edits.

## Phase 2: Hypothesis Contracts Before Code

Goal: make cheating and non-operational substitutes fail before implementation.

- [x] Add `tests/test_aba_decomposed_prefsat_contract.py`.
- [x] Add `layered_independent_aba_for_decomposition` Hypothesis strategy with
  2 to 5 independent residual components, at most 8 assumptions total, and at
  most 18 rules total.
- [x] Add `single_component_aba_for_no_reduction` Hypothesis strategy with one
  connected proof/contrary incidence component.
- [x] Add `test_decomposed_prefsat_matches_preferred_oracle_on_small_products`.
- [x] Add `test_decomposition_reports_required_telemetry`.
- [x] Add `test_reduced_product_never_calls_full_instance_prefsat`, monkeypatching
  `aba_sat.real_prefsat_extension` to fail when called with the original
  framework identity and asserting component calls still happen.
- [x] Add `test_no_reduction_calls_real_prefsat_once_and_reports_reason`.
- [x] Add `test_decomposition_never_calls_aba_to_dung`, monkeypatching
  `argumentation.aba.aba_to_dung` to fail.
- [x] Add `test_lifted_answer_validates_against_original_framework`.
- [x] Add `test_decomposed_route_ignores_filename_manifest_year_and_path`.
- [x] Add operational assertions for the telemetry numeric invariants listed
  above.

Execution status:

- Phase 2 contract tests were committed before source implementation.
- Phase 2 gate failed before implementation because `argumentation.aba_decomposition`
  does not exist yet: 6 failed, 2 passed.
- Next unchecked item is Phase 3: Experiment Branch.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_decomposed_prefsat_contract.py
```

Expected result before implementation: tests fail because the production
surfaces do not exist or still route directly to full-instance PrefSat.

## Phase 3: Experiment Branch

Goal: isolate this benchmark-driven implementation slice.

- [x] Confirm tracked files are clean with
  `git status --short --untracked-files=no`.
- [x] Create an experiment branch from the clean tracked-file base.
- [x] Commit Phase 2 tests before source implementation.

Execution status:

- Tracked files were clean before branch creation.
- Created `experiment/aba-decomposed-prefsat-composition` from the clean tracked
  base.
- Next unchecked item is Phase 4: Deletion-First Route Change.

Gate:

```powershell
git status --short --untracked-files=no
git branch --show-current
```

Expected result: implementation proceeds only on an experiment branch, with
tests committed separately from source.

## Phase 4: Deletion-First Route Change

Goal: remove the direct full-instance preferred no-query path before adding the
new path.

- [x] Delete the direct preferred no-query `real_prefsat_extension(...).extension`
  return in `sat_support_extension`.
- [x] Replace it with `decomposed_prefsat_extension(...).extension`.
- [x] Do not change `_sat_preferred_extension_satisfying`.
- [x] Add a temporary import or local lazy import only for
  `decomposed_prefsat_extension`; do not add a wrapper function in
  `aba_sat.py`.

Execution status:

- Preferred no-query SAT support now calls `decomposed_prefsat_extension`.
- `rg -n -F "return real_prefsat_extension(" src\argumentation\aba_sat.py`
  returned no matches.
- `_sat_preferred_cegar_extension` and `aba_to_dung` searches showed only
  pre-existing definitions, not a new production edge.
- Next unchecked item is Phase 5: Exact Decomposition Planner.

Old-path search gate:

```powershell
rg -n -F "return real_prefsat_extension(" src\argumentation\aba_sat.py
rg -n -F "_sat_preferred_cegar_extension(" src\argumentation\aba_sat.py
rg -n -F "aba_to_dung(" src\argumentation
```

Expected result: no preferred no-query direct full-instance return remains; no
old CEGAR production edge is introduced; `aba_to_dung` is not used by the new
composition path.

## Phase 5: Exact Decomposition Planner

Goal: implement the exact independent-product certificate and nothing broader.

- [x] Add `src/argumentation/aba_decomposition.py`.
- [x] Implement the proof/contrary incidence graph exactly as specified above.
- [x] Implement connected component extraction deterministically by `repr`.
- [x] Implement `plan_decomposed_prefsat`.
- [x] For an empty residual, return `decomp_no_reduction_reason ==
  "empty_residual"` and no component jobs.
- [x] For one exact component equal to the residual, return
  `decomp_no_reduction_reason == "single_component"`.
- [x] For multiple exact components, return `decomp_no_reduction_reason ==
  "reduced"` and component jobs whose assumption/rule sets partition the
  residual.
- [x] If any rule or contrary crosses components, return
  `decomp_no_reduction_reason == "component_plan_not_exact"` and no component
  jobs.

Execution status:

- Added the exact incidence-graph planner in `src/argumentation/aba_decomposition.py`.
- Phase 5 gate passed: 4 passed, 4 deselected in 208.33s.
- Next unchecked item is Phase 6: Decomposed PrefSat Composition.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_decomposed_prefsat_contract.py -k "decomposition_reports or no_reduction or never_calls"
```

Expected result: planner tests pass; composition/oracle tests still fail until
Phase 6 is implemented.

## Phase 6: Decomposed PrefSat Composition

Goal: solve exact product components with real PrefSat and lift to the original
framework.

- [x] Implement `decomposed_prefsat_extension`.
- [x] Apply `simplify_aba(framework, semantics="preferred")` before planning.
- [x] For `empty_residual`, return `fixed_in` and validate it against the
  original framework.
- [x] For `single_component` and `component_plan_not_exact`, call
  `real_prefsat_extension` exactly once on the residual, lift through
  `AbaSimplification.lift`, and validate against the original framework.
- [x] For `reduced`, call `real_prefsat_extension` once per component job, union
  component extensions, lift through `AbaSimplification.lift`, and validate
  against the original framework.
- [x] Validation uses `argumentation.aba.preferred_extensions` only in tests and
  small validation gates. Production validation in hard-bucket runs remains
  `tools/aba_shape_benchmark.py::validate_result`.
- [x] Aggregate `prefsat_solver_checks` from component results into
  `decomp_solver_checks`.

Execution status:

- Implemented composition, simplification, lifting, component solving, and
  solver-check aggregation.
- Full decomposed PrefSat contract gate passed: 8 passed in 172.58s.
- Next unchecked item is Phase 7: Shape Routing Integration.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_decomposed_prefsat_contract.py
```

Expected result: all decomposed PrefSat contract tests pass.

## Phase 7: Shape Routing Integration

Goal: route by argument shape and measured decomposition effect, not identity.

- [ ] Add shape metadata for decomposition planning:
  `decomp_component_count`, `decomp_max_component_assumptions`, and
  `decomp_no_reduction_reason`.
- [ ] Add a production route entry with backend `sat`, predicate
  `decomposed_prefsat_reduced_product`, and evidence id
  `aba-decomposed-prefsat-composition-2026-05-18`.
- [ ] The production route entry appears only when the solver class is
  `aba/single-extension/preferred`, the framework is flat, and
  `decomp_no_reduction_reason == "reduced"`.
- [ ] Filename, path, year, generator name, and manifest id must not affect the
  route entry.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_decomposed_prefsat_contract.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: decomposition route properties and existing route properties
pass together.

## Phase 8: Property and Regression Gate

Goal: prove the new path preserves existing behavior before timing evidence.

- [ ] Run the decomposed PrefSat contract tests.
- [ ] Run the real PrefSat contract tests.
- [ ] Run the ABA regression and routing tests.
- [ ] Run old-path search gates again.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_decomposed_prefsat_contract.py tests\test_aba_real_prefsat_contract.py tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: all listed tests pass and old production paths stay deleted.

## Phase 9: Targeted Hard-Row Gate

Goal: prove the composition changes the measured hard class or record that it
does not.

- [ ] Run T1/T3/T5/T6/T8 and C1/C2/C3 with `--no-profile` under the declared
  budget.
- [ ] A primary hard row counts as solved only if its row has
  `status == "solved"` and `validation.status == "valid"` for backend `sat` or
  `auto`.
- [ ] C1/C2/C3 must remain solved by the production portfolio.
- [ ] If no primary preferred target counts as solved, profile T1 with backend
  `sat` before recording failure.
- [ ] Record whether time is in decomposition planning, residual simplification,
  component PrefSat solving, SAT checks, parsing, validation, model
  construction, or answer checking.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-decomposed-prefsat-targeted.json --output-csv data\iccma\2025\runs\aba-decomposed-prefsat-targeted.csv
```

Profile command if no primary row counts as solved:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --backend sat --subtrack SE-PR --timeout-seconds 30 --profile-duration-seconds 25 --profile-format speedscope --profile-dir data\iccma\2025\profiles\aba-decomposed-prefsat --output-json data\iccma\2025\runs\aba-decomposed-prefsat-t1-profile.json --output-csv data\iccma\2025\runs\aba-decomposed-prefsat-t1-profile.csv
```

Expected result: at least one primary preferred hard row has `status ==
"solved"` and `validation.status == "valid"` under 30 seconds for backend `sat`
or `auto`, controls remain solved, and generated diagnostics remain
uncommitted.

## Phase 10: Promotion or Failed-Hypothesis Record

Goal: finish with either a real win or a precise failure.

If gates pass:

- [ ] Minimize the final diff to source, tests, and deliberate documentation.
- [ ] Re-run Phase 8 and Phase 9 gates.
- [ ] Promote the minimal final diff to `main` with a clean commit or
  fast-forward merge.
- [ ] Keep generated diagnostics uncommitted. Commit them only when the user
  explicitly requests artifact promotion.

If gates fail:

- [ ] Do not promote the experiment branch.
- [ ] Record the exact failed paper claim, contract, target row, decomposition
  telemetry, profiler attribution, and next hypothesis in
  `reports/aba-decomposed-prefsat-failure.md`.
- [ ] State whether the exact independent-product certificate failed to reduce
  the hard rows, or whether it reduced them and PrefSat/SAT checks still
  dominated.

Gate:

```powershell
git status --short --untracked-files=no
uv run pytest -q --timeout=240 tests\test_aba_decomposed_prefsat_contract.py tests\test_aba_real_prefsat_contract.py tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py tests\test_performance_contracts.py
```

Expected result: a promoted decomposition+PrefSat win, or an explicit failed
hypothesis record that cannot be confused with a completed substitute.

## Definition of Done

This workstream is complete only when one of these is true:

- decomposition+PrefSat contracts pass, old production paths are deleted, at
  least one primary preferred hard row has `status == "solved"` and
  `validation.status == "valid"` under 30 seconds for backend `sat` or `auto`,
  C1/C2/C3 are preserved, and the minimal diff is promoted to `main`; or
- a failed-hypothesis record proves that the composition layer satisfied the
  exact independent-product contract and still failed, with decomposition
  telemetry, profiler evidence, and the next concrete hypothesis.

If the implementation splits across a non-exact component boundary, calls the
old production paths, or validates only component-local answers, the workstream
is not a failed decomposition experiment. It is an implementation failure and
must not be counted as evidence against the paper architecture.
