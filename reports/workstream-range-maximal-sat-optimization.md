# Workstream: Paper-Backed Range-Maximal SAT Optimization

Author: Codex
Date: 2026-05-02
Status: executed on 2026-05-02

## Evidence Level

The original plan was based on the local `paper-reader` notes already present in
`papers/` plus the post-workstream ICCMA traces from May 2, 2026. I did not
reread PDF page images in this turn.

Execution note: implementation exposed an important correction to the initial
cardinality phrasing. Stage and semi-stable semantics are range-maximal by set
inclusion, not by range cardinality alone. The final implementation therefore
uses full/high/cardinality probes to order candidate seeds, but it only returns
a witness after a global strict-range-inclusion maximality check.

The key observed bottleneck is no longer preferred skeptical or ideal reasoning.
After the incremental AF SAT workstream, 2017 improved from 2572 solved / 278
timeouts to 2834 solved / 16 timeouts, while traces showed repeated expensive
`stage_seed` calls on instances such as `C/1/BA_80_20_4`,
`T/3/BA_80_70_5`, `D/1/WS_100_12_50_30`, and transport graphs. Range
maximality checks were often cheaper than seed rediscovery.

## Paper Basis

- Dvorak, Jarvisalo, Wallner, Woltran 2014, "Complexity-Sensitive Decision
  Procedures for Abstract Argumentation": range variables
  `x'_a <-> x_a or exists attacker in X`, base semantics
  `BASE-SEM(stg)=cf` and `BASE-SEM(sem)=com`, strict-range refinement, learned
  clauses excluding range subsets, and shortcut depth `d=2`.
- Bistarelli and Santini 2012, "ConArg": stage and semi-stable are modeled by
  explicit range variables plus a second optimization/maximality problem; this
  supports treating range maximization as the real objective rather than as
  repeated unconstrained seed discovery.
- Caminada 2006/2011 labelling work: semi-stable is minimal undecidedness,
  equivalently maximal range for complete/admissible labellings; stage is the
  analogous maximal-range semantics over conflict-free candidates.
- Charwat et al. 2015 survey / CEGARTIX system descriptions: implemented
  systems for hard AF tasks use iterative SAT-oracle procedures and
  incremental solving rather than native extension-family enumeration.

## Target Architecture

Replace open-ended range ascent with an exact range-maximality controller on
top of `AfSatKernel`.

The existing range formula stays:

```text
range[a] <-> in[a] or exists b in in such that b attacks a
```

The changed control surface is:

1. Maintain reusable base solvers for stage and semi-stable.
2. Search with full/high/cardinality seed probes plus range subset refinements,
   not by repeatedly asking for unconstrained old seed utilities.
3. Learn rejected range subsets within the task.
4. Keep the Dvorak/CEGARTIX shortcut procedure for high-range candidates:
   prioritize ranges missing at most `d` arguments before general search.
5. Use exact fallback only after the shortcut/cardinality path is exhausted.

## Phase 0: Slow-Row Regression Fixtures

Tests first:

- Add a tiny fixture generator that loads selected ICCMA AFs by path without
  depending on full-year runner state:
  - `data/iccma/2017/instances/C/1/BA_80_20_4.apx`
  - `data/iccma/2017/instances/T/3/BA_80_70_5.apx`
  - one `WS_100_*` row
  - one transportation graph row
- Add trace assertions for `SE-STG`, `DC-STG`, `DS-STG`, `SE-SST`,
  `DC-SST`, and `DS-SST`.
- Record structural counters only: SAT utility sequence, number of
  `stage_seed` / `semi_stable_seed` calls, and max range size found.

Done when targeted tests can fail on repeated unbounded seed rediscovery without
depending on wall-clock timing.

## Phase 1: Kernel Cardinality Primitives

Tests first:

- Compare `require_range_size_at_least(k)`, `require_range_size_exactly(k)`,
  and `model_range_size()` against native `range_of()` on generated AFs.
- Verify assumptions/push/pop do not leak cardinality constraints between SAT
  calls.
- Verify trace events include requested range bounds.

Implementation:

- Add pseudo-Boolean/cardinality helpers to `AfSatKernel` over `range_vars`.
- Add range-bound metadata to `SATCheck`.
- Keep the existing `require_range` and `require_any_range` APIs; they become
  building blocks, not the whole optimization strategy.

Done when cardinality-bounded stage/semi-stable candidates match native
predicates on small generated AFs.

## Phase 2: Exact Maximum Range Size

Tests first:

- For generated small AFs, compute maximum stage range size and maximum
  semi-stable range size; compare to native extension enumeration.
- Add monotonicity tests: if range size `k` is unsat, all larger `k` are unsat.
- Add solver-call-count tests on `BA_80_20_4` showing logarithmic or bounded
  cardinality probing, not linear seed ascent.

Implementation:

- Implement `max_range_size(base, required_in, required_out)` using binary
  search over `0..|A|` with SAT cardinality constraints.
- For semi-stable, use complete base semantics; for stage, use conflict-free.
- Cache the final maximum range size for the task.

Done when witness search starts at the exact maximum range size rather than
discovering it by repeated strict improvements.

## Phase 3: Witness and Acceptance by Max Range

Tests first:

- Differential-test `SE-STG`, `SE-SST`, `DC-STG`, `DC-SST`, `DS-STG`,
  and `DS-SST` against native enumeration on exhaustive-safe generated AFs.
- Guard that stage does not use admissible/complete base constraints.
- Guard that semi-stable does not use conflict-free-only base constraints.

Implementation:

- `SE`: find any base candidate with `range_size == max_range`.
- `DC`: find any base candidate with query constraint and
  `range_size == max_range`.
- `DS`: search for a counterexample base candidate with query excluded and
  `range_size == max_range`.

Done when all range-maximal tasks use the same exact max-range size instead of
running independent range-ascent loops.

## Phase 4: Dvorak Shortcut Layer

Tests first:

- Construct cases where a stable extension exists and verify semi-stable/stage
  shortcut to full range.
- Construct cases with `|A \ range| <= d` and verify shortcut candidates are
  attempted before general cardinality search.
- Verify increasing/decreasing `d` changes only search order, not answers.

Implementation:

- Add the CEGARTIX-style high-range candidate set `U` for small missing-range
  sets, default `d=2`.
- For each candidate missing set, query whether a base candidate realizes that
  range under the task condition.
- Learn exclusions for impossible or irrelevant high-range sets.
- Fall back to exact cardinality max-range search if shortcuts do not decide.

Done when ICCMA traces show high-range shortcut utility names before general
binary/cardinality search on stage/semi-stable rows.

## Phase 5: Incremental Task Solver Reuse

Tests first:

- Assert one solver object is reused across range-bound checks within a task.
- Assert learned range no-goods survive between related checks in a task.
- Assert no state leaks between distinct queries/rows.

Implementation:

- Add a `RangeMaximalTaskSolver` wrapper owning:
  - the `AfSatKernel`;
  - base semantics name;
  - required query labels;
  - learned impossible ranges;
  - cached maximum range size;
  - trace metadata.
- Replace direct calls to `_range_maximal_extension()` from public stage and
  semi-stable paths.

Done when production stage/semi-stable paths no longer call the old open-ended
range ascent helper.

## Phase 6: Benchmark Gate

Tests first:

- Add `tools/iccma_compare_range_traces.py` or extend the existing comparison
  tooling to summarize utility counts by semantics and instance.
- Add selected-slice commands for the named slow rows.

Execution:

1. Run targeted tests.
2. Run selected 2017 slow-row slices with old and new labels.
3. Only if those improve, run cap-100 2017/2019/2023/2025 comparison.

Success criteria:

- Keep correctness identical against native tests.
- Reduce `stage_seed`/`semi_stable_seed` counts on slow rows.
- Reduce or preserve total SAT calls.
- Improve 2017 post-workstream timeouts below 16 without regressing 2019,
  2023, or 2025 solved counts.

## Non-Goals

- Do not raise the ICCMA cap as part of this workstream.
- Do not switch to approximate MaxSAT/optimization.
- Do not introduce a second solver stack unless a paper-backed exact backend is
  selected in a separate workstream.
- Do not use wall-clock-only tests.
- Do not claim PDF rereads unless page images are actually read.

## Executed Result

Implemented commits:

- `145b866` through `1378479`: TDD coverage, cardinality primitives, task
  solver extraction, streamed SAT telemetry, comparison tooling, and selected
  row runner.
- `8535eda`: bounded Dvorak-style high-range shortcut probes with depth `d=2`
  and a probe budget.
- `0281031`: correctness fix restoring set-inclusion range maximality; the
  cardinality path remains a seed-ordering heuristic, not the semantic oracle.

Verification:

- `uv run pytest tests\test_solver_encoding.py tests\test_solver_availability.py tests\test_iccma_runner.py tests\test_iccma_range_trace_compare.py tests\test_iccma_run_selected.py -q`
  passed with `84 passed`.
- `uv run pytest -q` passed with `761 passed, 2 skipped in 71.80s`.

Selected 2017 slow rows after the correctness fix:

- `C/1/BA_80_20_4.apx`, `SE-STG`: solved via one
  `stage_full_range_shortcut` check; witness size 56.
- `T/3/BA_80_70_5.apx`, `SE-STG`: solved via one
  `stage_full_range_shortcut` check; witness size 44.
- `D/1/WS_100_12_50_30.tgf`, `SE-STG`: solved via bounded
  `stage_high_range_shortcut` checks plus one `stage_range_maximality` check;
  witness size 21.

Cap-100 comparison against the previous post-workstream run:

| Year | Previous solved | Previous timeout | New solved | New timeout |
| --- | ---: | ---: | ---: | ---: |
| 2017 | 2834 | 16 | 2834 | 16 |
| 2019 | 2558 | 7 | 2558 | 7 |
| 2023 | 486 | 84 | 487 | 83 |
| 2025 | 199 | 54 | 199 | 54 |

Run artifacts:

- `data/iccma/2017/runs/iccma-2017-range-max-inclusion-cap100-summary.json`
- `data/iccma/2019/runs/iccma-2019-range-max-inclusion-cap100-summary.json`
- `data/iccma/2023/runs/iccma-2023-range-max-inclusion-cap100-summary.json`
- `data/iccma/2025/runs/iccma-2025-range-max-inclusion-cap100-summary.json`

## Expected Result

The expected improvement is concentrated in `STG` and some `SST` rows. The
previous workstream made preferred skeptical and ideal fast enough that range
maximality now dominates. This workstream attacks that dominant cost directly
by turning stage/semi-stable into exact maximum-range tasks with Dvorak-style
shortcuts and reusable SAT state.
