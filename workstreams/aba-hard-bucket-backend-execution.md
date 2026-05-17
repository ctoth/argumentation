# ABA Hard-Bucket Backend Execution Workstream

## Goal

Turn the ABA hard-bucket work item into an executable backend program that
measurably improves the exact all-timeout rows without filename heuristics or
ICCMA-specific routing.

The outcome is not another note. The outcome is one of:

- a source-backed backend change that solves at least one current all-timeout
  target row under the same 30-second budget while preserving controls; or
- a failed experiment branch with a recorded gate failure and profiler evidence
  precise enough to choose the next backend hypothesis.

This execution runs directly on `main` because the user explicitly requested
full execution on `main` on 2026-05-17.

## Control Surface

This workstream is controlled by:

- [ABA hard-bucket backend work item](aba-hard-bucket-backend-work-item.md)
- `data/iccma/2025/runs/aba-shape-cap200-paper-features-rerun.json`
- `data/iccma/2025/runs/aba-route-evidence-rerun-analysis.json`

Generated diagnostics remain uncommitted unless explicitly requested.

## Required Target Rows

Primary targets:

| Target | Instance | Subtrack | Gate role |
|---|---|---|---|
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-PR` | preferred all-timeout |
| T2 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-ST` | stable all-timeout |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-PR` | preferred all-timeout |
| T4 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-ST` | stable all-timeout |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-PR` | preferred all-timeout |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-PR` | preferred all-timeout |
| T7 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-ST` | stable all-timeout |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-PR` | preferred all-timeout |
| T9 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-ST` | stable all-timeout |

Control rows:

| Control | Instance | Subtrack | Must preserve |
|---|---|---|---|
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | solved by `sat` |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | solved by `asp` |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | solved by `auto` |

No benchmark command may select rows by this filename family in production
logic. Filenames are allowed only in manifests and diagnostics naming the
benchmark rows.

## Paper-Image Rule

Before coding any new backend idea, read the relevant paper page images
directly and record the cited page numbers in the test or metadata surface.
Notes files may guide where to look, but they are not enough for a new
implementation claim.

Required page-image anchors for the first implementation hypothesis:

- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000005.png`: ABA(F)
  fact surface and Algorithm 1.
- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000006.png`: `pi_com`
  Listing 1 and `constr(out(I))` refinement behavior.
- `papers/Lehtonen_2021_IncrementalASP_ABA_pngs/page-000012.png`: Clingo
  incremental Python interface and empirical setup.
- Baroni/Giacomin SCC-recursive pages must be read from page images before any
  SCC-conditioned backend is implemented. If page images are absent, retrieve or
  generate them first; do not claim SCC-recursive implementation support from
  text notes alone.
- Egly/Gaggl/Woltran saturation pages must be read from page images before any
  saturation rewrite is implemented.
- Cerutti/PrefSat or Niskanen/mu-toksia pages must be read from page images
  before any SAT/maximality backend is implemented.

## Dependency-Sorted Execution Order

1. Phase 0: Workstream Order Guard.
2. Phase 1: Hard-Row Manifest and Reproducer.
3. Phase 2: Baseline Profiling Harness.
4. Phase 3: Backend Invariant Properties.
5. Phase 4: First Hypothesis, Lehtonen Incremental ASP Tightening.
6. Phase 5: SCC-Conditioned Experiment.
7. Phase 6: Preferred Maximality Experiment.
8. Phase 7: Hard-Row Benchmark Gate.
9. Phase 8: Promotion or Failed-Experiment Record.

Every phase has a gate. Do not substitute passing unit tests for a benchmark
gate, and do not substitute a benchmark run for paper-cited implementation
properties.

## Phase 0: Workstream Order Guard

Goal: make the checklist executable before implementation.

- [x] Run or add an order check proving each dependency appears before its
  dependent phase.
- [x] Verify tracked files are clean before implementation.
- [x] Record explicit user override to execute this workstream directly on
  `main` instead of creating an experiment branch.

Gate:

```powershell
git status --short --untracked-files=no
git branch --show-current
```

Expected result: clean tracked files, on `main` for this user-directed
execution.

## Phase 1: Hard-Row Manifest and Reproducer

Goal: make T1-T9 and C1-C3 executable without hand-copying command lines.

- [x] Add a text-source manifest for T1-T9 and C1-C3 under `tests/manifests/`.
- [x] Add a small tool or option that runs exactly that manifest against
  `auto`, `asp`, and `sat` with `--timeout-seconds 30`.
- [x] Add tests proving the manifest contains exactly 12 rows and no duplicate
  `(instance, subtrack)` pairs.
- [x] Add tests proving production backend selection cannot inspect manifest
  row paths or generator names.

Gate:

```powershell
uv run pytest -q tests\test_aba_hard_bucket_manifest.py tests\test_aba_route_properties.py
```

## Phase 2: Baseline Profiling Harness

Goal: know what is slow on the exact hard rows before changing algorithms.

- [x] Integrate a stable profiler launcher path for hard-row commands.
- [x] Prefer `uvx py-spy` or a checked tool dependency. Do not rely on an ad
  hoc cache path.
- [x] Capture wall time, backend status, solver metadata, refinement counts,
  solver-call counts, and Python-side profiling output for at least T1, T2,
  T3, T4, and C1-C3.
- [x] If `py-spy` fails with an unfamiliar error, search the exact error before
  changing approach.
- [x] Record findings in an uncommitted diagnostic artifact unless explicitly
  asked to promote it.

Phase 2 finding:

- Diagnostic artifact:
  `data/iccma/2025/runs/aba-hard-bucket-phase2-profile-findings.md`
  (intentionally uncommitted).
- T1-T4 status evidence: all timed out across `auto`, `asp`, and `sat` in
  `data/iccma/2025/runs/aba-hard-bucket-phase2-profile.json`.
- T1/T2 bounded profiles show the hard ASP rows spend nearly the whole sampled
  window in clingo C calls under `_solve_multishot`, not Python frame
  extraction.
- C1 did not preserve under the profiled 30s status run: `sat` timed out; its
  bounded profile spends nearly the whole sampled window in
  `Z3_solver_check_assumptions`.
- Next code hypothesis: reduce the encoded first-solver problem for ASP
  preferred/stable single-extension, and separately repair or reroute the C1
  SAT stable witness path from `_sat_ranked_stable_extension`, using structural
  features only.

Before launching the profiling command, state a timeout derived from the 30s
per-row budget plus modest harness overhead. Do not manually stop it unless it
exits, hits the configured timeout, the user asks to stop, or it causes concrete
external harm.

Gate:

- a profiler artifact exists for at least one all-timeout preferred row;
- a profiler artifact exists for at least one all-timeout stable row;
- a profiler artifact exists for every control row;
- the next code hypothesis names the specific hot path it intends to reduce.

## Phase 3: Backend Invariant Properties

Goal: write properties before changing the backend.

Required properties:

- [x] ABA(F) fact emission remains structural and page-cited to Lehtonen p.5.
- [x] `constr(out(I))` blocks exactly a candidate and its subsets, page-cited
  to Lehtonen pp.5-6.
- [x] incremental backend metadata carries the page-image source used for the
  algorithm.
- [x] any SCC-conditioned optimization preserves complete, stable, and preferred
  answers on generated small frameworks.
- [x] any maximality optimization returns only subset-maximal admissible or
  complete candidates on generated small frameworks.
- [x] no new production predicate reads path text, filename, parent directory,
  ICCMA year, row order, or generator name.

Phase 3 note:

- Lehtonen page images 5, 6, and 12 were reread directly before Phase 4 work.
- SCC-conditioned and maximality-specific properties are vacuously satisfied
  for Phase 4 because no SCC-conditioned or maximality optimization is active
  yet. Phases 5 and 6 still require fresh page-image reads and additional
  page-cited properties before those optimizations can be implemented.
- Gate passed on 2026-05-17:
  `uv run pytest -q --timeout=180 tests\test_aba_incremental_paper_properties.py tests\test_aba_route_properties.py`.

Gate:

```powershell
uv run pytest -q tests\test_aba_incremental_paper_properties.py tests\test_aba_route_properties.py
```

## Phase 4: First Hypothesis, Lehtonen Incremental ASP Tightening

Goal: reduce Python and grounding overhead in the existing direct ASP path.

Hypothesis:

The current multishot path is correct but may still spend too much time in
Python-side model extraction, per-refinement grounding, or repeated complete-set
search. The first implementation should tighten that path before adding a new
solver family.

Possible implementation moves, selected only after Phase 2 profiling:

- reduce model-symbol scanning to shown atoms or direct `in/1` extraction;
- batch or intern refinement parts to reduce Python/clingo overhead;
- expose telemetry in benchmark output so hard-row runs show refinement clauses,
  inner iterations, outer iterations, solver calls, and selected algorithm;
- add a single-extension stable path that avoids unnecessary complete/preferred
  machinery if profiling shows stable rows are burning in the wrong path;
- avoid materializing support facts for `asp`/`clingo` paths.

Gate:

```powershell
uv run pytest -q tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py
```

Then run the hard-row manifest with the same 30-second solver budget.

Pass condition:

- at least one of T1-T9 solves under the same 30-second budget; and
- C1-C3 remain solved; and
- no correctness regression appears in witness validation.

If this gate fails, leave the experiment branch unmerged and record the failed
gate result. Do not create revert noise on `main`.

Phase 4 result:

- Property gate passed on 2026-05-17:
  `uv run pytest -q --timeout=240 tests\test_aba_incremental_paper_properties.py tests\test_aba_multishot.py tests\test_aba_shape_benchmark.py`
  with 1050 passing tests.
- Benchmark gate failed on 2026-05-17:
  `uv run tools\aba_shape_benchmark.py --timeouts tests\manifests\aba-hard-bucket-targets.json --year 2025 --instance-kind aba --timeout-seconds 30 --output-json data\iccma\2025\runs\aba-hard-bucket-phase4-direct-stable.json --output-csv data\iccma\2025\runs\aba-hard-bucket-phase4-direct-stable.csv --backend auto --backend asp --backend sat --subtrack SE-PR --subtrack SE-ST`.
- Result: T1-T9 all remained all-timeout; C2 and C3 solved; C1 remained
  all-timeout. Level 1 was not reached.
- Because this workstream was explicitly forced to execute directly on `main`,
  there is no failed experiment branch to leave unmerged for this slice.
  Continue with the next paper-gated hypothesis rather than claiming Phase 4
  succeeded.

## Phase 5: SCC-Conditioned Experiment

Goal: test the Baroni/Giacomin directionality hypothesis on the giant cyclic
dependency component.

Precondition:

- read the relevant SCC-recursive paper pages from page images;
- add page-cited Hypothesis properties before implementation.

Hypothesis:

The hard rows have one giant cyclic SCC plus smaller surrounding structure.
Conditioning or simplifying upstream/downstream acyclic structure before the
preferred/stable core search may reduce the candidate space without changing
semantics.

Required properties:

- SCC-conditioned solving agrees with the unconditioned reference on generated
small frameworks.
- Adding unrelated non-ancestor structure does not change the conditioned answer
for a component-local query.
- The optimization key is graph structure, not filename or benchmark row.

Gate:

Run the hard-row manifest. Pass condition is the Phase 4 pass condition plus
at least one solved preferred/stable pair on the same instance if Phase 4 already
solved a single isolated row.

## Phase 6: Preferred Maximality Experiment

Goal: attack preferred maximality directly if profiling shows DS-PR/SE-PR burns
there.

Precondition:

- read relevant Egly saturation pages or Cerutti/Niskanen SAT/maximality pages
  from page images;
- add page-cited Hypothesis properties before implementation.

Candidate directions:

- ASP saturation rewrite for maximality checks;
- SAT complete-labelling maximality growth or persistent SAT assumptions;
- hybrid ASP candidate generation plus SAT maximality verification.

Required properties:

- every returned preferred witness is admissible;
- no returned preferred witness has a strict admissible superset;
- skeptical preferred answers match brute-force on generated small frameworks;
- route selection remains structural and backend-availability based.

Gate:

Run the hard-row manifest. Pass condition:

- at least one preferred all-timeout row T1/T3/T5/T6/T8 solves under 30s; and
- C1-C3 remain solved; and
- no stable row regresses.

## Phase 7: Hard-Row Benchmark Gate

Goal: decide whether the experiment is a real improvement.

Run exactly the T1-T9 plus C1-C3 manifest against `auto`, `asp`, and `sat`.

Required reporting fields:

- `(target_id, instance, subtrack)`;
- backend;
- status;
- wall time;
- witness validation;
- selected algorithm;
- paper/page metadata;
- telemetry counts where available;
- profiler artifact id if profiling was active.

Pass levels:

- Level 1: at least one T row solved under 30s, C1-C3 preserved.
- Level 2: one preferred/stable pair on the same instance solved under 30s,
  C1-C3 preserved.
- Level 3: at least three distinct target instances improved or solved,
  C1-C3 preserved.

Only Level 1 is required for first promotion. Level 2 and Level 3 define the
next iterations.

## Phase 8: Promotion or Failed-Experiment Record

If the gate passes:

- [ ] minimize the diff;
- [ ] rerun the targeted property and benchmark gates;
- [ ] switch to `main`;
- [ ] promote by clean merge or minimal commit;
- [ ] leave generated diagnostics uncommitted unless explicitly requested.

If the gate fails:

- [x] record that there is no failed experiment branch because this workstream
  was explicitly forced to run on `main`;
- [x] record the exact failed gate and profiler conclusion in this workstream
  or a linked report;
- [x] record that the failed backend code is already on `main` because of the
  explicit main-only execution override;
- [x] choose the next hypothesis from the profiler evidence.

Failed-experiment record:

- There is no failed experiment branch to preserve because the user explicitly
  required execution directly on `main`.
- The failed backend slice is the direct stable ASP witness path:
  `src/argumentation/aba_incremental.py` and `src/argumentation/aba_asp.py`.
  It passed the property gate but did not solve any T row in the hard-row
  benchmark.
- The profiler conclusion is Phase 2's conclusion: hard preferred/stable ASP
  rows burn in the first clingo solve, and C1 burns in Z3 stable SAT checking.
- The next executable hypothesis should not be another Python micro-optimization.
  It should be one of:
  - preferred maximality attack using Egly/Cerutti/Niskanen page-image-backed
    properties; or
  - C1 SAT stable repair/reroute for `_sat_ranked_stable_extension`, because the
    declared C1 control is not preserved in current measured runs.
  SCC decomposition is not the next implementation target for these rows unless
  a later structural measure finds a decomposable assumption-level cut; the
  current hard rows have one giant dependency SCC plus small fringe components.

## Definition of Done

This workstream is complete only when one of these is true:

- Level 1 hard-row gate passes and the minimal source diff is promoted to
  `main`; or
- the active experiment fails its gate and records enough profiler evidence to
  select the next backend hypothesis without guessing.

Passing unit tests alone is not completion. Page citations alone are not
completion. A benchmark run without a kept backend improvement is not
completion.
