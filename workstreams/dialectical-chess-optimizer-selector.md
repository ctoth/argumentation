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

Status: pending.

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

## Phase 1: Generic Optimizer Implementation

Status: pending.

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

## Phase 2: Chess Adapter

Status: pending.

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

## Phase 3: Objective Policy

Status: pending.

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

## Phase 4: Matrix Integration

Status: pending.

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

## Phase 5: Benchmark Run

Status: pending.

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

## Phase 6: Decide What Is Principled Enough

Status: pending.

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
