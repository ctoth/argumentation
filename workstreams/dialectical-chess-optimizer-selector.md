# Argumentation Optimization Semantics for Dialectical Chess

## Goal

Build the chess optimizer as an instance of a generic optimization semantics in
`argumentation`, not as a chess-only selector.

The chess sidecar should still enumerate legal moves procedurally. The generic
library should provide the principled part: optimize over argument acceptance,
defeat, support, weights, and domain-supplied objective features.

## Paper Basis

Local processed notes read for this rewrite:

- `papers\Dung_1995_AcceptabilityArguments`: abstract AFs, admissibility,
  grounded/preferred/stable semantics, and the explicit link to n-person games.
- `..\propstore\papers\Modgil_2014_ASPICFrameworkStructuredArgumentation`:
  ASPIC+ as the structured argument layer with strict/defeasible rules,
  undercutting/rebutting/undermining, preferences, and Dung reduction.
- `papers\Dunne_2011_WeightedArgumentSystemsBasic`: weighted attacks and
  inconsistency budgets, including optimization formulations for disregarded
  attack weight.
- `papers\Bench-Capon_2003_PersuasionPracticalArgumentValue-based`: values and
  audience-specific value orderings as a principled model of practical
  decision priorities.
- `..\propstore\papers\Amgoud_2017_AcceptabilitySemanticsWeightedArgumentation`:
  weighted argument graphs and gradual acceptability degrees.
- `papers\Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks`: ranking
  semantics and discussion-depth rankings for arguments.
- `papers\Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation`: support as a
  first-class relation independent from defeat.
- `papers\Rago_2016_AdaptingDFQuADBipolarArgumentation`: quantitative
  attack/support aggregation for bipolar frameworks.
- `papers\Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers`: SAT encodings of
  complete labellings and optimization/search over labelling space.
- `..\propstore\papers\Bjorner_2014_MaximalSatisfactionZ3`: Z3 optimization,
  MaxSMT, and lexicographic/Pareto objective combinations.
- `..\propstore\papers\Sebastiani_2015_OptiMathSATToolOptimizationModulo`:
  OMT and multi-objective optimization over SMT formulas.
- `..\propstore\papers\Moura_2008_Z3EfficientSMTSolver`: Z3 as the underlying
  SMT infrastructure.

Execution rule for implementation:

- When coding a semantics detail from a paper, reread the relevant local page
  images where available before claiming the implementation matches the paper.
- Cite the source paper in code docstrings or comments where a public API,
  semantics constraint, or objective policy is paper-derived.
- If page images are unavailable for a needed detail, cite the processed local
  notes/abstract used and say that the page image was not reread.
- Do not use PDF text extraction as the basis for paper rereads.

Interpretation:

- Dung gives the semantics constraints.
- ASPIC+ gives structured reasons and preferences.
- Weighted, value-based, ranking, and bipolar argumentation justify objective
  features beyond binary in/out.
- SAT/SMT/OMT work justifies a solver-backed implementation surface.
- Chess supplies domain features, but should not own the optimization semantics.

## Non-Negotiables

- Stay on the current branch.
- Do not encode chess legality symbolically in the first implementation.
- Keep legal move generation procedural in the chess sidecar.
- Add a generic `argumentation.optimization` module first.
- Keep chess-specific scoring outside `src\argumentation`.
- Use Hypothesis-first TDD: read paper page images, extract semantic
  properties, write cited property tests, then write implementation code.
- Use `uv run`, not bare Python.
- Keep generated benchmark JSON/profile artifacts under `scratch` uncommitted.
- Preserve existing selector modes while adding `optimizer`.

## Target Architecture

### Generic Library Layer

Add:

- `src\argumentation\optimization.py`

Core types:

- `OptimizationFeature`
  - argument id;
  - feature name;
  - integer value;
  - objective direction.
- `OptimizationObjective`
  - name;
  - direction: maximize/minimize;
  - priority tier;
  - optional weight.
- `OptimizationPolicy`
  - semantics constraint: initially `conflict_free` or `admissible`;
  - objective list;
  - optional required/forbidden arguments;
  - optional candidate decision arguments.
- `OptimizationResult`
  - selected arguments;
  - selected candidate argument;
  - objective values;
  - solver status;
  - backend trace.

Initial backend:

- Z3 `Optimize`, with one Boolean variable per argument.
- Hard constraints over the AF:
  - selected set is conflict-free;
  - optional admissibility: selected arguments must be defended;
  - candidate selection: exactly one candidate decision argument is selected.
- Lexicographic objectives over accepted argument features.

This is a generic OMT-backed argumentation semantics:

```text
Given:
  AF = (arguments, defeats)
  candidate arguments C
  feature map f(argument, feature_name) -> int
  ordered objectives O

Find:
  an accepted set S and selected candidate c in C

Subject to:
  S satisfies the chosen argumentation constraints
  c in S, or c is selected under a declared candidate rule

Optimizing:
  O_1(S, c), then O_2(S, c), ...
```

### Chess Client Layer

Chess should translate `MoveProbe` and `RootArgumentGraph` into generic
optimization input:

- candidate arguments: `move:<uci>`;
- support features:
  - accepted support count;
  - categoriser score bucket;
  - terminal mate;
  - tactical material;
  - search score;
  - positional support count;
- penalty features:
  - unresolved reply attacks;
  - objections;
  - truncation labels;
  - unsafe tactical replies.

Then chess calls:

```python
optimize_framework(framework, policy, features)
```

and maps the selected candidate argument back to a `MoveProbe`.

## Phase 0: Generic Red Tests

Status: complete.

Tasks:

- Reread the relevant paper page images before writing tests:
  - Dung conflict-free/admissibility/defense pages;
  - Dunne weighted-attack budget pages if budget objectives are included;
  - Bjørner/Sebastiani objective-combination pages for lexicographic OMT.
- Extract implementation properties from those pages into test names and
  docstrings.
- Add tests for `argumentation.optimization`.
- Test conflict-free optimization with candidate arguments.
- Test admissibility rejects undefended selected arguments.
- Test lexicographic priority beats lower-tier numeric score.
- Test deterministic tie-breaking.
- Test unavailable Z3 produces explicit unavailable status, not a silent
  fallback.
- Add Hypothesis strategies for small AFs:
  - 0-8 arguments;
  - arbitrary defeat relations over those arguments;
  - non-empty candidate subsets;
  - integer feature values over bounded ranges.
- Add property tests, each citing the paper source/page-image basis in a
  docstring or adjacent comment:
  - selected set is conflict-free under `conflict_free` policy;
  - selected set is admissible under `admissible` policy;
  - selected candidate is exactly one of the declared candidates;
  - lexicographic dominance property holds for generated two-objective cases;
  - deterministic tie-break is stable under input order permutations.

Acceptance criteria:

- Tests fail because `argumentation.optimization` does not exist yet.
- The failing tests cite the paper property they encode.
- No implementation code is written before the red tests exist.

Result:

- Reread page images:
  - `papers\Dung_1995_AcceptabilityArguments\pngs\page-005.png`;
  - `papers\Dung_1995_AcceptabilityArguments\pngs\page-006.png`;
  - `..\propstore\papers\Bjorner_2014_MaximalSatisfactionZ3\pngs\page-006.png`;
  - `..\propstore\papers\Bjorner_2014_MaximalSatisfactionZ3\pngs\page-007.png`;
  - `..\propstore\papers\Sebastiani_2015_OptiMathSATToolOptimizationModulo\pngs\page-003.png`;
  - `..\propstore\papers\Sebastiani_2015_OptiMathSATToolOptimizationModulo\pngs\page-004.png`;
  - `papers\Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers\pngs\page-001.png`.
- Added `tests\test_optimization.py` with cited Hypothesis properties.
- Initial red test failed with
  `ModuleNotFoundError: No module named 'argumentation.optimization'`.

## Phase 1: Generic Optimizer Implementation

Status: complete.

Tasks:

- Add `src\argumentation\optimization.py`.
- Implement conflict-free constraints.
- Implement admissibility constraints using Dung defense.
- Implement exactly-one candidate selection.
- Implement lexicographic objectives using Z3 `Optimize`.
- Return objective values and selected candidate.
- After each implementation slice, rerun the cited property tests before moving
  to chess integration.

Acceptance criteria:

- Generic optimizer tests pass.
- No chess imports exist under `src\argumentation`.
- The API accepts any `ArgumentationFramework`, not only chess graphs.
- Hypothesis tests pass with the committed example database ignored/uncommitted.

Result:

- Added `src\argumentation\optimization.py`.
- Implemented:
  - `OptimizationFeature`;
  - `OptimizationObjective`;
  - `OptimizationPolicy`;
  - `OptimizationResult`;
  - `optimize_framework`.
- Backend:
  - Z3 `Optimize`;
  - one Boolean variable per argument;
  - conflict-free constraints;
  - admissibility constraints;
  - exactly-one candidate selection;
  - lexicographic objective order;
  - explicit `unavailable` result when Z3 cannot be imported.
- Generic property tests: `7 passed`.

## Phase 2: Chess Adapter

Status: complete.

Tasks:

- Add a small chess adapter module under `scripts\dialectical_chess`.
- Convert `MoveProbe` plus `RootArgumentGraph` into optimizer features.
- Add `optimizer` to `SELECTOR_MODES`.
- Route `choose_move(... selector_mode="optimizer")` through the generic
  optimizer.
- Preserve existing `argument`, `score`, `grounded`, `support`, and
  `categoriser` modes.

Acceptance criteria:

- `EngineSettings(selector_mode="optimizer")` is accepted.
- Optimizer selection is visible in benchmark JSON.
- UCI can run with `--selector-mode optimizer`.

Result:

- Added `optimizer` to `SELECTOR_MODES`.
- Added `optimizer_trace` to `MoveProbe`.
- Added `scripts\dialectical_chess\optimizer.py`.
- The adapter maps `MoveProbe` and `RootArgumentGraph` into generic
  optimization features.
- Benchmark JSON now includes `optimizer_trace`.
- UCI emits `info string optimizer_status=...` when the selected probe has an
  optimizer trace.
- UCI smoke:

```powershell
@('uci', 'isready', 'position fen 7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1', 'go', 'quit') |
  uv run --with chess --with z3-solver .\scripts\dialectical_chess_probe.py --selector-mode optimizer --uci
```

- Result included `info string optimizer_status=optimal` and `bestmove a1a8`.

## Phase 3: Objective Policy

Status: complete.

Initial chess policy:

1. maximize terminal checkmate;
2. minimize unresolved reply attacks;
3. maximize accepted tactical support;
4. maximize accepted defense count;
5. maximize material gain;
6. maximize search score when present;
7. maximize accepted positional support;
8. maximize base probe score;
9. minimize deterministic UCI rank.

Tasks:

- Keep this policy data-driven in the chess adapter.
- Split tactical and positional features so positional noise can be ablated.
- Record objective values for the selected move.

Acceptance criteria:

- The optimizer can run with positional objectives enabled or disabled.
- The selected move trace explains which objective tiers decided the move.

Result:

- Implemented the initial chess policy in `scripts\dialectical_chess\optimizer.py`.
- The matrix has both positional and no-positional optimizer rows.
- Selected probe traces include status, selected candidate, selected arguments,
  objective values, and backend trace.

## Phase 4: Matrix Integration

Status: complete.

Tasks:

- Add matrix rows:
  - `optimizer_static`;
  - `optimizer_d2`;
  - `optimizer_d2_no_positional`;
  - `optimizer_mate_theme_depth`.
- Keep the existing sample metadata:
  - line move counts;
  - mate theme counts;
  - first-engine-move scoring target.

Acceptance criteria:

- Matrix output includes optimizer rows.
- Existing rows remain comparable to previous runs.

Result:

- Added core matrix rows:
  - `optimizer_static`;
  - `optimizer_d2`;
  - `optimizer_d2_no_positional`;
  - `optimizer_mate_theme_depth`.
- Existing sample metadata is unchanged.

## Phase 5: Benchmark Run

Status: complete.

Run the fixed 100-puzzle Lichess slice:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py `
  --experiment-matrix `
  --lichess-puzzles .\scratch\lichess_db_puzzle.csv `
  --rating-min 1200 `
  --rating-max 1600 `
  --limit 100 `
  --matrix-preset core `
  --progress-every 25 `
  --json-out .\scratch\lichess_1200_1600_matrix_core_100_optimizer.json
```

Timeout:

- Choose from the latest 14-case baseline plus modest slack.

Compare against:

- `score_static`: `13/100`;
- `argument_d2`: `17/100`;
- `grounded_d2`: `19/100`;
- `argument_d2_no_positional`: `21/100`.

Acceptance criteria:

- Runtime is bounded.
- Results note whether the generic optimizer beats the current `21%` best row.
- Results note whether Z3 overhead is acceptable.

Result:

- Command output was redirected on stdout and progress was kept on stderr.
- Timeout chosen before launch: `240s`.
- Result artifact:
  - `scratch\lichess_1200_1600_matrix_core_100_optimizer.json`.
- Runtime:
  - `163321.8446 ms`.
- Sample:
  - `100` puzzles;
  - line move counts: `2`: 9, `4`: 63, `6`: 26, `8`: 2;
  - mate themes: `mateIn1`: 9, `mateIn2`: 10, `mateIn3`: 3.

Comparison rows:

| Case | Solved | Hit Rate | Elapsed ms |
| --- | ---: | ---: | ---: |
| `argument_d2_no_positional` | 21/100 | 0.21 | 8195.96 |
| `optimizer_d2_no_positional` | 21/100 | 0.21 | 12875.01 |
| `optimizer_static` | 19/100 | 0.19 | 7469.51 |
| `grounded_d2` | 19/100 | 0.19 | 8779.18 |
| `argument_d2_search1` | 18/100 | 0.18 | 11367.07 |
| `argument_d2` | 17/100 | 0.17 | 8753.11 |
| `optimizer_d2` | 17/100 | 0.17 | 14038.81 |
| `optimizer_mate_theme_depth` | 15/100 | 0.15 | 15116.14 |
| `score_static` | 13/100 | 0.13 | 3773.04 |

Interpretation:

- Optimizer improves over static score: `19%` vs `13%`.
- Optimizer ties the current best only with positional reasons disabled:
  `optimizer_d2_no_positional` and `argument_d2_no_positional` both solve
  `21/100`.
- Optimizer does not beat the current best row.
- Z3 overhead is visible: `optimizer_d2_no_positional` takes about `12.9s`
  versus `8.2s` for `argument_d2_no_positional` on the same sample.

## Phase 6: Decide What Is Principled Enough

Status: complete.

Questions to answer from evidence:

- Does OMT-backed argumentation improve selection, or only make the tuple sort
  auditable?
- Does admissibility as a hard constraint help or hurt puzzle solving?
- Should weighted attacks follow Dunne-style attack budgets instead of direct
  objective penalties?
- Should chess use value-based priorities for game phase or tactical context?
- Should support move from ad hoc reason counts to a bipolar/DF-QuAD-style
  strength function?
- Does pure Python lexicographic optimization match Z3 exactly and run faster?

Acceptance criteria:

- The workstream ends with a concrete recommendation:
  - keep generic optimizer and use it in chess;
  - keep generic optimizer but leave chess on existing selector;
  - or remove the optimizer path as non-useful overhead.

Result:

- Recommendation: keep the generic optimizer and keep the chess optimizer
  selector as an experimental matrix row, but do not make it the default chess
  selector yet.
- It is principled and useful as an auditable OMT-backed argumentation
  semantics.
- It improves over raw static score, so it is not empty ceremony.
- It does not beat `argument_d2_no_positional`, and it is slower than the
  equivalent non-optimizer row, so it is not yet a clear strength win.
- The next workstream should compare the same objective policy against a pure
  Python lexicographic implementation. If the pure Python selector matches Z3
  move-for-move and is materially faster, keep Z3 as the generic semantics
  backend but use the pure Python selector in chess hot paths.

## Why This Is More Principled Than the First Draft

The first draft put Z3 Optimize directly in the chess selector. That would work,
but it would make optimization a chess-specific trick.

This rewrite puts the reusable semantics in `argumentation`:

- Dung constraints define legal accepted sets.
- ASPIC+ and preferences explain where structured chess arguments should come
  from later.
- Weighted and value-based argumentation justify costs, priorities, and
  audience/context-sensitive objectives.
- Ranking and gradual semantics justify numeric argument features.
- OMT provides the backend for choosing an optimal accepted candidate.

Chess becomes a demanding client and benchmark, not the owner of the idea.
