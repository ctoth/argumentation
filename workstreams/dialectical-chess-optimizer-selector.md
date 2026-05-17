# Dialectical Chess Optimizer Selector Workstream

## Goal

Add an optimizer-backed selector that keeps procedural chess move generation but
uses Z3 `Optimize` to choose among legal move probes from structured tactical,
search, and argumentation evidence.

This is option 1: enumerate legal moves first, attach evidence, then optimize
over the candidate set. It deliberately does not try to encode chess legality
symbolically.

## Premise

The current engine already produces one `MoveProbe` per legal move. Each probe
has:

- scalar `score`
- tactical flags and material deltas
- reason labels
- objection labels
- reply attack labels
- search score and principal line
- SMT witness labels
- argument graph acceptance/ranking information

The missing piece is a principled optimization selector that treats those fields
as hard constraints and lexicographic objectives instead of relying on one tuple
sort.

## Non-Negotiables

- Stay on the current branch.
- Keep legal move generation procedural.
- Do not remove existing selector modes.
- Add `optimizer` as a normal selector mode and matrix case.
- Keep the optimizer result explainable in benchmark JSON and UCI output.
- Use TDD: red tests for optimizer objective ordering before implementation.
- Use `uv run`, not bare Python.
- Keep generated benchmark outputs under `scratch` uncommitted.

## Target Architecture

Introduce a chess-side optimizer module:

- `scripts\dialectical_chess\optimizer.py`

Responsibilities:

- Build one Z3 Boolean decision variable per `MoveProbe`.
- Add hard constraints:
  - exactly one move variable is selected;
  - terminal checkmate moves dominate all non-checkmate moves;
  - optionally reject moves with undefeated tactical refutations once we expose
    that as a hard selector setting.
- Add lexicographic optimization objectives:
  1. maximize terminal mate;
  2. minimize unresolved reply attacks;
  3. maximize accepted argument support;
  4. maximize accepted defenses;
  5. maximize tactical material gain;
  6. maximize search score when present;
  7. maximize base probe score;
  8. deterministic UCI tie-break.
- Return both the selected probe and an `OptimizerTrace`.

The selector should consume the already-built `RootArgumentGraph` rather than
recomputing argumentation.

## Phase 0: Tests Define Objective Semantics

Status: pending.

Tasks:

- Add tests for the `optimizer` selector mode.
- Prove it prefers checkmate over material.
- Prove it avoids unresolved reply attacks when material score is higher.
- Prove accepted support can break ties.
- Prove UCI tie-break is deterministic.
- Prove `EngineSettings(selector_mode="optimizer")` is accepted.

Acceptance criteria:

- Tests fail before implementation because `optimizer` is unknown or missing.

## Phase 1: Optimizer Module

Status: pending.

Tasks:

- Add `optimizer.py`.
- Implement `OptimizerTrace`.
- Implement `choose_optimized_move(probes, graph)`.
- Keep all Z3 interaction isolated to this module.
- If Z3 is unavailable, return an explicit unavailable trace and fall back to
  the existing `argument` selector only through a deliberate caller path.

Acceptance criteria:

- Focused optimizer tests pass.
- The optimizer trace records objective values for the selected move.

## Phase 2: Selector Integration

Status: pending.

Tasks:

- Add `optimizer` to `SELECTOR_MODES`.
- Route `choose_move(... selector_mode="optimizer")` through the optimizer.
- Thread optimizer trace into engine analysis payloads without breaking current
  benchmark JSON.
- Print a short UCI `info string selector_mode=optimizer` and selected objective
  summary.

Acceptance criteria:

- Existing selector tests pass.
- UCI accepts `--selector-mode optimizer`.
- Benchmark JSON identifies optimizer settings and selected objective values.

## Phase 3: Matrix Integration

Status: pending.

Tasks:

- Add `optimizer_static` to the core experiment matrix.
- Add `optimizer_d2` if optimizer uses argumentation features from
  `dialectic_depth=2`.
- Add `optimizer_mate_theme_depth` if the mate-theme dynamic depth case remains
  useful after the latest run.

Acceptance criteria:

- Matrix output includes optimizer cases.
- The sample metadata still records line lengths and mate theme counts.

## Phase 4: Benchmark Run

Status: pending.

Tasks:

- Run the same fixed 100-puzzle Lichess slice:

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

- Choose timeout from the current 14-case baseline plus modest slack.
- Summarize optimizer rows against:
  - `score_static`
  - `argument_d2`
  - `grounded_d2`
  - `argument_d2_no_positional`

Acceptance criteria:

- Runtime is bounded.
- Notes record solved count, hit rate, elapsed time, and whether optimizer beats
  the current `21%` best row.

## Phase 5: Interpret and Tighten

Status: pending.

Tasks:

- If optimizer loses to static score, inspect objective ordering on misses.
- If optimizer beats argument modes, promote its objective ordering as the next
  default candidate.
- If positional reasons hurt optimizer too, add a follow-up workstream for
  tactical gating of positional objectives.
- If Z3 Optimize overhead is high, compare against an equivalent pure-Python
  lexicographic selector to prove whether Z3 is buying anything.

Acceptance criteria:

- We know whether optimizer is adding strength, explainability, both, or just
  overhead.

## Open Design Questions

- Should unresolved tactical reply attacks be a hard constraint or the second
  lexicographic objective?
- Should accepted grounded support count more than categoriser score, or should
  categoriser score be the direct optimizer objective?
- Should search score be lexicographically late, or should it dominate all
  non-terminal positional terms?
- Should mate-theme depth control optimizer evidence generation by default for
  Lichess puzzle runs?

## Initial Hypotheses

- Optimizer should beat `score_static` because it can encode tactical objections
  before material.
- Optimizer may beat `argument_d2` if it prevents noisy positional reasons from
  outranking tactical safety.
- Optimizer will not automatically beat `argument_d2_no_positional` unless the
  objective order sharply devalues positional support under tactical conflict.
- Z3 Optimize is useful first as an auditable objective surface; raw speed is a
  secondary question until the benchmark says otherwise.
