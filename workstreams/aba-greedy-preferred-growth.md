# ABA Greedy Preferred Growth Workstream

## Goal

Replace preferred single-extension enumeration with a constructive complete-set
growth search that avoids global optimum solving and avoids enumerating every
preferred extension.

The previous ASP global-maximality experiment proved the small semantics but
timed out on T1/T3/T5/T6/T8. This hypothesis keeps the Lehtonen `pi_com`
complete-extension surface and grows one complete set by repeated constrained
complete-superset queries. If no outside assumption can be added, there is no
strict complete superset; in finite flat ABA, maximal complete sets are
preferred.

## Paper-Image Evidence

Read directly before this workstream:

- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000005.png`: ABA(F)
  fact surface, `pi_com` answer sets as complete assumption sets, and
  `in/out/supported` meaning.
- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000006.png`: constrained
  ASP calls with `in(I)` and proper complete supersets in Algorithm 1.
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-018.png`:
  preferred extensions require an additional maximality test.
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-019.png`:
  a non-preferred admissible candidate has a strict admissible superset.

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
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | preserve current solved behavior or explicitly rebaseline |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | preserve solved behavior |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | preserve solved behavior |

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Clean Base and Experiment Branch.
3. Phase 2: Hypothesis-First Properties.
4. Phase 3: Greedy Growth Backend Slice.
5. Phase 4: Targeted Benchmark Gate.
6. Phase 5: Promote or Record Failure.

## Phase 0: Workstream Order Guard

Goal: make this checklist mechanically executable.

- [ ] Run the order check after every edit to this workstream.
- [ ] Before each later phase, reread this file and identify the next unchecked
  item.

Gate:

```powershell
uv run tools\check_workstream_phase_order.py workstreams\aba-greedy-preferred-growth.md
```

Expected result: every listed phase matches a phase heading in the same order.

## Phase 1: Clean Base and Experiment Branch

Goal: isolate this speculative benchmark-driven slice.

- [x] Confirm tracked files were clean on the failed prior experiment branch.
- [x] Switch to `main`.
- [x] Create `experiment/aba-greedy-preferred-growth`.
- [x] Leave unrelated untracked files and paper artifacts untouched.

Gate:

```powershell
git branch --show-current
git status --short --untracked-files=no
```

Expected result: clean tracked files on `experiment/aba-greedy-preferred-growth`.

## Phase 2: Hypothesis-First Properties

Goal: write the semantic contract before source changes.

- [ ] Test that greedy preferred growth returns a native preferred extension on
  generated small flat ABA frameworks.
- [ ] Test that no returned greedy witness has a strict admissible or complete
  superset.
- [ ] Test that the no-attack case grows to all assumptions.
- [ ] Test that preferred single-extension production does not enumerate every
  preferred set.
- [ ] Test metadata cites Lehtonen and Egly page-image evidence.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py::test_preferred_single_extension_uses_greedy_growth
```

Expected result: new properties fail only for the missing greedy backend.

## Phase 3: Greedy Growth Backend Slice

Goal: implement one constructive preferred witness path.

- [ ] Add a reusable complete-superset query over the already-grounded
  Lehtonen `pi_com` control.
- [ ] Start from one complete extension and greedily adopt satisfiable strict
  complete supersets until no outside assumption can be added.
- [ ] Route preferred single-extension through this path.
- [ ] Preserve public result shape and structural routing.
- [ ] Do not use filename, generator, ICCMA-year, row-order, or path-text
  predicates.

Gate:

```powershell
uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
```

Expected result: property and regression tests pass before any speed claim.

## Phase 4: Targeted Benchmark Gate

Goal: measure actual hard-row effect.

- [ ] Run T1/T3/T5/T6/T8 and C1/C2/C3 under 30 seconds.
- [ ] Validate every solved answer with the existing checker surface.
- [ ] If no preferred target solves, record failure; do not run the full bucket
  as a substitute.
- [ ] Keep generated diagnostics uncommitted unless explicitly requested.

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --target-id T3 --target-id T5 --target-id T6 --target-id T8 --target-id C1 --target-id C2 --target-id C3 --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-greedy-preferred-growth-targeted.json --output-csv data\iccma\2025\runs\aba-greedy-preferred-growth-targeted.csv
```

Expected result: at least one preferred hard target solves under 30 seconds,
C2/C3 remain solved, and C1 is preserved or explicitly rebaselined.

## Phase 5: Promote or Record Failure

If the gate passes:

- [ ] Minimize the diff.
- [ ] Re-run targeted tests and the targeted benchmark gate.
- [ ] Promote the minimal passing diff to `main`.
- [ ] Leave generated diagnostics uncommitted unless explicitly requested.

If the gate fails:

- [ ] Do not promote the experiment branch.
- [ ] Record the failed hypothesis, page citations, property result, target
  rows, benchmark evidence, and next concrete hypothesis.
- [ ] Leave the failed branch in place unless the user asks for branch cleanup.

## Definition of Done

This workstream is complete only when one of these is true:

- the greedy preferred-growth backend solves at least one preferred hard target
  under 30 seconds, preserves controls, and is promoted cleanly; or
- the hypothesis fails and the failure record names the exact page-image claim,
  property result, target rows, benchmark result, and next backend hypothesis.
