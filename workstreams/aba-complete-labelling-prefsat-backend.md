# ABA Complete-Labelling PrefSat Backend Workstream

## Goal

Implement the actual preferred-semantics backend we now know we need:
a Cerutti/ArgSemSAT-style complete-labelling SAT search for flat ABA preferred
single-extension tasks.

This is not a profiling workstream. Profiling the failed support-CEGAR shortcut
again is explicitly out of scope. The next useful implementation is the target
architecture itself:

- three-valued labels over ABA assumptions;
- complete-labelling constraints over derived contraries and attacks;
- an inner SAT loop that grows a complete extension by forcing current `in`
  labels plus at least one additional `in`;
- an outer blocking clause that excludes each discovered preferred extension
  and its subsets;
- page-image-cited properties against the brute-force ABA oracle;
- hard-row benchmark proof that at least one current preferred all-timeout row
  now solves under the 30-second budget.

Because this is speculative, benchmark-driven implementation work, execution
slices must run on a dedicated experiment branch from a clean tracked base
unless the user explicitly overrides that branch rule.

## Control Surface

This workstream is controlled by:

- [ABA preferred maximality backend workstream](aba-preferred-maximality-backend-workstream.md)
- failed experiment branch `experiment/aba-preferred-maximality-backend`, commit
  `753f582 Record failed ABA preferred hypothesis`
- `tests/manifests/aba-hard-bucket-targets.json`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-001.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-002.png`

Generated JSON, CSV, py-spy output, logs, screenshots, caches, and temporary
manifests stay uncommitted unless the user explicitly asks to promote them.

## Non-Goals

- Do not profile the failed support-CEGAR shortcut before implementing the real
  complete-labelling backend.
- Do not add filename, generator, ICCMA-year, or path-text heuristics.
- Do not translate ABA to an exponentially larger AF as the main path.
- Do not keep old/new preferred SAT paths in production unless an explicit
  external constraint requires it.
- Do not promote a route based on Hypothesis tests alone.

## Target Rows

Primary preferred targets:

| Target | Instance | Subtrack | Required outcome |
|---|---|---|---|
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-PR` | solve or fail this hypothesis |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-PR` | solve or fail this hypothesis |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-PR` | solve or fail this hypothesis |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-PR` | solve or fail this hypothesis |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-PR` | solve or fail this hypothesis |

Controls:

| Control | Instance | Subtrack | Required handling |
|---|---|---|---|
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | stable hard row; do not regress or fake-fix |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | preserve solved behavior |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | preserve solved behavior |

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Clean Base and Experiment Branch.
3. Phase 2: Page-Image Design Extraction.
4. Phase 3: Deletion-First Backend Target.
5. Phase 4: Complete-Labelling Property Tests.
6. Phase 5: Implement Complete-Labelling SAT Core.
7. Phase 6: Implement PrefSat Grow and Block Search.
8. Phase 7: Wire Preferred SAT Route.
9. Phase 8: Targeted Benchmark Gate.
10. Phase 9: Full Hard-Bucket Gate.
11. Phase 10: Promote or Record Failure.

Every phase has a gate. Passing tests before the current phase gate does not
complete the workstream.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable before using it as the control
surface.

- [ ] Run the order check after every edit to this workstream.
- [ ] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-complete-labelling-prefsat-backend.md
```

Expected result: every listed phase matches an actual phase heading in the same
order.

## Phase 1: Clean Base and Experiment Branch

Goal: isolate the benchmark-driven implementation.

- [ ] Check tracked-file cleanliness.
- [ ] If tracked files are dirty, stop and report the exact paths.
- [ ] Create a dedicated experiment branch from the clean base.
- [ ] Do not add unrelated untracked files.

Gate:

```powershell
git status --short --untracked-files=no
git switch -c experiment/aba-complete-labelling-prefsat-backend
git status --short --untracked-files=no
```

Expected result: a clean tracked base on the experiment branch.

## Phase 2: Page-Image Design Extraction

Goal: extract the exact target algorithm from page images before coding.

- [ ] Reread Cerutti 2013 page 8 image for Algorithm 1 variable operations.
- [ ] Reread Cerutti 2013 page 9 image for the correctness proof that returned
  candidates are maximal complete extensions.
- [ ] Reread Cerutti 2013 page 10 image for inner strict-superset growth and
  outer subset-blocking behavior.
- [ ] Reread Cerutti 2015 page 2 image for the ArgSemSAT complete-labelling SAT
  search surface.
- [ ] Reread Cerutti 2015 page 3 image for implementation skeleton details.
- [ ] Reread Niskanen 2020 pages 1-2 images for persistent SAT solver state and
  assumptions only where that API shape is used.
- [ ] Write a short design note in this workstream naming the chosen variable
  families and blocking clauses.

Gate:

```powershell
git diff -- workstreams\aba-complete-labelling-prefsat-backend.md
uv run tools\check_workstream_phase_order.py workstreams\aba-complete-labelling-prefsat-backend.md
```

Expected result: paper-image design recorded, no backend code yet.

## Phase 3: Deletion-First Backend Target

Goal: define the production surface that will replace the incomplete preferred
SAT shortcut.

- [ ] Identify the exact preferred SAT entry points in `src\argumentation\aba_sat.py`.
- [ ] Delete or bypass the support-CEGAR preferred witness path for the target
  route instead of adding a compatibility wrapper around it.
- [ ] Name the target implementation surface, for example
  `CompleteLabellingPrefSatSolver`, only if that is the real shared abstraction
  used by callers.
- [ ] Keep stable SAT paths untouched unless a failing test proves they are
  directly affected.

Gate:

```powershell
rg -n -- "sat_support_extension|preferred|_sat_preferred" src\argumentation\aba_sat.py
git diff -- src\argumentation\aba_sat.py
```

Expected result: the target production surface is explicit and the old
preferred shortcut is not the implementation path being optimized.

## Phase 4: Complete-Labelling Property Tests

Goal: make the exact semantics executable before implementation.

- [ ] Add tests that every generated labelling assigns each assumption exactly
  one of `in`, `out`, or `undec`.
- [ ] Add tests that `in` assumptions are conflict-free through ABA derivation
  of contraries.
- [ ] Add tests that `out` assumptions are attacked by the current `in` set.
- [ ] Add tests that assumptions attacked by the current `in` set are labelled
  `out`.
- [ ] Add tests that `in` assumptions are defended against admissible attackers,
  matching the existing flat ABA semantics.
- [ ] Add tests that complete labellings correspond to native
  `complete_extensions` on small generated ABA frameworks.
- [ ] Add tests that preferred witnesses are maximal complete extensions, not
  merely cardinality-maximal models.
- [ ] Add tests for the PrefSat outer blocking clause: after a preferred
  extension `E` is found, future seeds must include at least one assumption
  outside `E`, so `E` and all subsets of `E` are blocked.
- [ ] Add skeptical preferred tests against the brute-force ABA oracle.
- [ ] Cite the page-image paths in the tests or metadata.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_route_properties.py
```

Expected result: tests fail only for the missing complete-labelling backend, not
for unrelated existing semantics.

## Phase 5: Implement Complete-Labelling SAT Core

Goal: implement the reusable SAT object for complete ABA labellings.

- [ ] Create Boolean variables for `in(a)`, `out(a)`, and `undec(a)` for each
  ABA assumption.
- [ ] Add exactly-one label constraints per assumption.
- [ ] Add ranked or otherwise well-founded closure constraints for derivability
  from the `in` assumptions.
- [ ] Add attack predicates from derived contraries to assumptions.
- [ ] Encode complete-labelling conditions so the `in` set corresponds to a
  native complete extension on small generated frameworks.
- [ ] Use persistent solver state only for base constraints that are independent
  of a specific PrefSat iteration.
- [ ] Do not translate to a generated Dung AF as the main path.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
```

Expected result: complete-labelling properties pass before preferred
maximality/search is wired into production.

## Phase 6: Implement PrefSat Grow and Block Search

Goal: implement the actual preferred search loop.

- [ ] Implement the inner grow loop: starting from a complete labelling, force
  all current `in` assumptions and require at least one additional `in`.
- [ ] Stop the inner loop only when no strict complete superset exists.
- [ ] Treat the final inner-loop candidate as a preferred witness only after the
  maximality check fails to find a strict complete superset.
- [ ] Implement the outer blocking clause requiring future seeds to include at
  least one assumption outside the discovered preferred extension.
- [ ] Return `{empty}` only when the complete-extension search proves no
  non-empty preferred witness exists, matching the paper behavior.
- [ ] Expose single preferred witness and skeptical preferred acceptance without
  enumerating every preferred extension unless the task explicitly needs it.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
```

Expected result: preferred witness and skeptical preferred properties pass
against brute-force ABA on generated small frameworks.

## Phase 7: Wire Preferred SAT Route

Goal: make production use the new backend for the intended solver class.

- [ ] Wire `backend="sat"`, `semantics="preferred"`, `task="single-extension"`
  to the complete-labelling PrefSat solver.
- [ ] If skeptical preferred can use the same backend without enumerating all
  preferred extensions, wire it only after properties prove the behavior.
- [ ] Keep route selection structural; no filenames, generator names, years, or
  path text.
- [ ] Preserve existing public result shapes and metadata.
- [ ] Include page-image citations in the returned metadata or trace where the
  existing solver surface supports it.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
```

Expected result: production SAT preferred calls use the new complete-labelling
backend and regression tests pass.

## Phase 8: Targeted Benchmark Gate

Goal: measure whether the actual backend solves the problem.

- [ ] Run T1/T3/T5/T6/T8 and controls C1/C2/C3 under the 30-second budget.
- [ ] Stop as soon as the gate has a decisive no-kept-improvement signal; do
  not keep polling a failed slice for ceremony.
- [ ] Validate every solved answer through the existing checker surface.
- [ ] Keep generated diagnostics uncommitted unless explicitly requested.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-complete-labelling-prefsat-targeted.json --output-csv data\iccma\2025\runs\aba-complete-labelling-prefsat-targeted.csv
```

Expected result: at least one of T1/T3/T5/T6/T8 solves under 30 seconds, C2/C3
remain solved, and C1 remains treated as a stable hard row unless separately
solved.

## Phase 9: Full Hard-Bucket Gate

Goal: check that the targeted win generalizes across the hard bucket.

- [ ] Run T1-T9 and C1-C3 under the 30-second budget.
- [ ] Compare against the baseline and failed support-CEGAR shortcut results.
- [ ] Keep generated diagnostics uncommitted unless explicitly requested.
- [ ] If the targeted gate already failed, do not run this full gate as a
  substitute for progress.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-complete-labelling-prefsat-full-hard-bucket.json --output-csv data\iccma\2025\runs\aba-complete-labelling-prefsat-full-hard-bucket.csv
```

Expected result: the new backend solves at least one current preferred
all-timeout row and does not regress solved controls.

## Phase 10: Promote or Record Failure

Goal: finish the experiment cleanly.

If the gates pass:

- [ ] Minimize the final diff to source, tests, and deliberate documentation.
- [ ] Re-run the targeted tests and benchmark gate.
- [ ] Promote the minimal final diff to `main` with a clean commit or clean
  merge, respecting unrelated worktree changes.
- [ ] Leave diagnostic artifacts uncommitted unless explicitly requested.

If the gates fail:

- [ ] Do not promote the experiment branch.
- [ ] Record the failed hypothesis, page citations, failing targets, and next
  concrete backend hypothesis.
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

- the real complete-labelling PrefSat/ArgSemSAT-style backend solves at least
  one preferred hard target under 30 seconds, preserves C2/C3, and is promoted
  cleanly; or
- the actual complete-labelling backend hypothesis fails and the failure record
  names the page-image claim, property, target row, benchmark evidence, and next
  backend hypothesis.
