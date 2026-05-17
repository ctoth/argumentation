# Dialectical Chess Positional Reason Audit And Gating

## Status

Status: executed.

Branch: `main`.

This workstream addresses the measured problem that positional reasons currently
hurt the fixed Lichess puzzle slice:

| Case | Solved |
| --- | ---: |
| `argument_d2` | 17/100 |
| `argument_d2_no_positional` | 21/100 |
| `optimizer_d2` | 17/100 |
| `optimizer_d2_no_positional` | 21/100 |

Working hypothesis:

- The current positional features are too shallow and too context-free.
- They are useful evidence in quiet positions, but they should not outrank
  tactical safety, direct threats, or puzzle-line forcing moves.
- The correct move is not to delete positional reasons; it is to make them
  answer to tactical context and to prove that with mined counterexamples.

## Non-Negotiables

- Work on `main` unless the user explicitly redirects branch state.
- Use `uv run ...` for every Python command.
- Add progress reporting to any newly created long-running runner.
- Keep generated diagnostics under `scratch/` uncommitted unless explicitly
  promoted.
- Commit each intentional source, test, or workstream edit atomically with
  explicit path-limited git commands.
- Do not remove positional reasons wholesale.
- Do not treat a better benchmark score as sufficient unless the changed
  decisions are explained by argument traces.
- If a new rule is paper-derived, read page images directly and cite the paper
  and page image in the test or code comment that encodes the rule.

## Owned Paths

Likely source paths:

- `scripts/dialectical_chess/probe.py`
- `scripts/dialectical_chess/arguments.py`
- `scripts/dialectical_chess/optimizer.py`
- `scripts/dialectical_chess/bench.py`
- `scripts/dialectical_chess/*.py` only as needed for reusable diagnostics

Likely test paths:

- `tests/test_dialectical_chess_evidence_ablation.py`
- `tests/test_dialectical_chess_engine_api.py`
- new focused test file only if the cases outgrow the existing tests

Likely generated diagnostic paths:

- `scratch/positional_reason_delta_*.json`
- `scratch/positional_reason_delta_*.md`

## Phase 0: Confirm Baseline Inputs

Goal: prove that the workstream starts from the same measured failure.

Commands:

```powershell
git branch --show-current
git status --short -- .\scripts .\tests .\workstreams .\scratch .\reports
Test-Path .\scratch\lichess_db_puzzle.csv
Test-Path .\scratch\lichess_1200_1600_matrix_core_100_optimizer.json
```

Acceptance criteria:

- Current branch is `main`.
- No tracked dirty task-owned files exist.
- `scratch\lichess_db_puzzle.csv` exists.
- Either the optimizer matrix JSON exists or Phase 1 reruns the fixed matrix.

If the matrix artifact is missing, rerun it before mining:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --experiment-matrix --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --matrix-preset core --progress-every 25 --json-out .\scratch\lichess_1200_1600_matrix_core_100_optimizer.json 1>$null
```

Timeout: `240s`, unless a newer measured baseline justifies a different value.

## Phase 1: Mine Positional Deltas

Goal: find the exact puzzles where positional reasons changed first-move
selection.

Implementation:

- Add or extend a diagnostic runner that compares two configurations over the
  same fixed puzzle slice:
  - positional on;
  - positional off.
- For each changed decision, emit:
  - puzzle id;
  - FEN;
  - expected first move;
  - selected move with positional reasons;
  - selected move without positional reasons;
  - solved flags for both;
  - selector mode;
  - dialectic depth;
  - selected move reasons;
  - selected move objections;
  - reply attacks;
  - optimizer trace when present.
- Include progress reporting every 5 or 10 puzzles.
- Write diagnostics to `scratch/`.

Suggested command shape:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --selector-mode argument --dialectic-depth 2 --compare-positional --progress-every 10 --json-out .\scratch\positional_reason_delta_argument_d2.json
```

If the existing benchmark runner should not own `--compare-positional`, create a
small script under `scripts/` with PEP 723 dependency metadata and equivalent
progress output.

Acceptance criteria:

- The diagnostic artifact identifies:
  - puzzles solved only with positional reasons off;
  - puzzles solved only with positional reasons on;
  - puzzles where both fail but choose different moves;
  - puzzles where both solve but choose different first moves.
- At least the `argument_d2` and `optimizer_d2` positional-on/off pairs are
  mined.
- Generated artifacts remain uncommitted.

## Phase 2: Classify Failure Modes

Goal: turn raw deltas into executable hypotheses.

For every positional-off-only success, classify the harmful positional reason:

- `center_control:*`
- `development:*`
- `piece_activity:*`
- `file_control:*`
- `king_safety:*`
- `outpost:*`
- `pawn_structure:*`
- other

For every changed decision, classify the tactical context:

- winning move gives check;
- winning move captures material;
- winning move promotes;
- winning move creates or answers mate pressure;
- losing positional move has unresolved reply attacks;
- losing positional move has no immediate tactical warrant;
- losing positional move wins shallow material but misses the puzzle line;
- quiet position with no tactical winner.

Acceptance criteria:

- A markdown summary under `scratch/` names the dominant failure modes.
- The summary contains at least three exact regression candidates, unless the
  fixed slice contains fewer than three positional-off-only successes.
- Each candidate has enough data to become a deterministic unit test without
  rereading the CSV.

## Phase 3: Write Failing Tests First

Goal: encode the desired behavior before changing selection logic.

Required tests:

- A regression test for each mined puzzle where positional reasons made
  `argument_d2` fail and no-positional solved it.
- A regression test for each mined puzzle where positional reasons made
  `optimizer_d2` fail and no-positional solved it.
- A property-style test that positional support cannot outrank an unresolved
  tactical reply attack when there is a tactically safe alternative.
- A property-style test that positional reasons still appear in quiet opening
  or middlegame positions.
- A property-style test that the optimizer trace reports whether positional
  support was gated, reduced, or used normally.

Suggested command:

```powershell
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_evidence_ablation.py .\tests\test_dialectical_chess_engine_api.py
```

Acceptance criteria:

- The new tests fail before implementation for the right behavioral reason.
- Existing quiet-position coverage still proves that positional reasons are not
  removed.
- Test names mention the mined puzzle id or the tactical gating invariant.

Commit:

```powershell
git status --short -- .\tests
git diff -- .\tests
git commit -- .\tests\test_dialectical_chess_evidence_ablation.py .\tests\test_dialectical_chess_engine_api.py -m "Add failing positional gating tests"
```

Adjust explicit paths if a new test file is created.

## Phase 4: Implement Tactical Gating

Goal: make positional evidence defeasible under tactical pressure.

Target design:

- Keep positional reason labels as structured arguments.
- Split reason effects into at least:
  - tactical support;
  - positional support;
  - tactical objections or reply-risk objections.
- Add a tactical context classifier that is shared by the argument selector and
  optimizer adapter.
- In tactical contexts, positional support may explain a move but must not be
  enough to beat:
  - mate;
  - checkmate threat avoidance;
  - safe captures or promotions;
  - moves with fewer unresolved reply attacks;
  - moves with stronger accepted tactical support.
- In quiet contexts, positional support remains active and visible.

Likely implementation choices:

- Add a small value object for positional handling, for example:
  - `positional_mode="normal"`;
  - `positional_mode="gated_by_reply_attack"`;
  - `positional_mode="quiet"`.
- Reduce positional score contribution when tactical pressure is detected
  instead of deleting the reason labels.
- Add optimizer features for:
  - `positional_support_raw`;
  - `positional_support_effective`;
  - `positional_gated`.
- Ensure selector ordering uses effective positional support after tactical
  safety features, not raw count.

Acceptance criteria:

- Failing tests from Phase 3 pass.
- Quiet-position positional reason tests still pass.
- Optimizer traces expose the gating decision.
- No old positional-on behavior remains that can outrank unresolved tactical
  objections in the mined regressions.

Commit:

```powershell
git status --short -- .\scripts .\tests
git diff -- .\scripts .\tests
git commit -- .\scripts\dialectical_chess .\tests -m "Gate positional chess reasons under tactical pressure"
```

Use narrower explicit paths if fewer files changed.

## Phase 5: Benchmark The Gate

Goal: prove the fix on the same fixed slice and record what changed.

Run focused tests first:

```powershell
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_evidence_ablation.py .\tests\test_dialectical_chess_engine_api.py .\tests\test_dialectical_chess_cleanup.py .\tests\test_dialectical_chess_loss_mining.py
```

Then rerun the fixed matrix:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --experiment-matrix --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --matrix-preset core --progress-every 25 --json-out .\scratch\lichess_1200_1600_matrix_core_100_positional_gated.json 1>$null
```

Timeout: start with `240s`; adjust only from measured runtime.

Acceptance criteria:

- `argument_d2` with positional reasons is no worse than
  `argument_d2_no_positional` on the fixed slice.
- `optimizer_d2` with positional reasons is no worse than
  `optimizer_d2_no_positional` on the fixed slice.
- If either gate fails, stop and report the exact failed row and changed puzzle
  ids; do not claim completion.
- If the gate passes, record sorted matrix rows in this workstream.

Generated artifacts stay under `scratch/` and uncommitted unless explicitly
promoted.

## Phase 6: Explain The Result

Goal: decide what the positional layer now means.

Record:

- which reason families were harmful;
- which reason families survived quiet-position checks;
- how many puzzles were recovered;
- how many puzzles regressed;
- whether the argument selector and optimizer now agree more often;
- whether the fix improved puzzle solving, explanation quality, or both;
- whether positional reasons should remain enabled by default.

Acceptance criteria:

- This workstream is updated with a final results section.
- The final note distinguishes:
  - tactical puzzle strength;
  - general chess-play plausibility;
  - argument-trace interpretability.
- The recommendation is specific:
  - keep positional reasons enabled;
  - keep enabled only with tactical gating;
  - disable for puzzle mode only;
  - or continue to a named next workstream.

Commit:

```powershell
git status --short -- .\workstreams\dialectical-chess-positional-reason-audit-and-gating.md
git diff -- .\workstreams\dialectical-chess-positional-reason-audit-and-gating.md
git commit -- .\workstreams\dialectical-chess-positional-reason-audit-and-gating.md -m "Record positional chess gating workstream"
```

## Completion Definition

This workstream is complete only when:

- positional-on/off deltas are mined from the fixed 100-puzzle slice;
- regression tests encode the mined failures;
- tactical gating is implemented without deleting quiet positional reasons;
- focused tests pass;
- the fixed matrix rerun passes the positional-on versus no-positional gate;
- final benchmark numbers and interpretation are written here;
- all intentional source, test, and workstream edits are committed.

## Execution Results

Status: complete.

Workflow actually used:

- Confirmed `main` and task-owned cleanliness.
- Added `--compare-positional` to the benchmark runner.
- Added reusable scratch-summary scripts for positional deltas and matrix rows.
- Mined positional-on/off deltas for `argument_d2` and `optimizer_d2`.
- Added failing tests from mined regressions.
- Implemented tactical positional gating in argument selectors and optimizer
  features.
- Found and fixed a related tactical witness instability: `smt_fork_moves`
  returned one arbitrary model witness instead of all satisfying fork witnesses.
- Reran the focused suite and fixed matrix.

Generated diagnostics:

- `scratch\positional_reason_delta_argument_d2.json`
- `scratch\positional_reason_delta_optimizer_d2.json`
- `scratch\positional_reason_delta_summary.md`
- `scratch\positional_reason_delta_optimizer_d2_gated.json`
- `scratch\positional_reason_delta_optimizer_d2_gated.md`
- `scratch\lichess_1200_1600_matrix_core_100_positional_gated.json`
- `scratch\lichess_1200_1600_matrix_core_100_positional_gated.md`

These are diagnostic artifacts and were not committed.

### Mined Failure Modes

Initial positional-off-only successes:

| Selector | Changed | Positional on only | Positional off only |
| --- | ---: | ---: | ---: |
| `argument_d2` | 66/100 | 4 | 7 |
| `optimizer_d2` | 17/100 | 1 | 2 |

Dominant harmful families:

- `center_control`
- `piece_activity`
- `file_control`
- `development`

Dominant tactical context:

- the move recovered by disabling positional reasons had concrete tactical
  evidence: material capture, check, promotion, or SMT fork witness;
- the bad positional move was usually not unsafe by reply analysis, so the
  problem was not unresolved reply attacks;
- the problem was evidence ordering: shallow positional supports were counted
  too early, before tactical value.

Regression candidates encoded in tests:

- `000Zo`: argument selector must prefer `e5f6` over positional rook movement.
- `00B3B`: argument selector must prefer `d7d8q` over center-control bishop
  movement.
- `002IE`: optimizer must prefer `c6e5` over the positional alternative.
- `00H1C`: optimizer must not return the mined positional blunder `f7h5`;
  after the later tactical witness stabilization, the exact no-positional move
  was no longer stable, so this became a gating invariant rather than an exact
  Lichess-solution invariant.

### Implementation Notes

Argument selectors now split support into tactical and positional evidence:

- tactical reason prefixes:
  - `terminal:`
  - `tactical:`
  - `material:`
  - `procedural:`
  - `smt:`
  - `search:`
- positional reason prefixes:
  - `center_control:`
  - `development:`
  - `file_control:`
  - `king_safety:`
  - `outpost:`
  - `pawn_structure:`
  - `piece_activity:`

When any accepted tactical reason exists in the graph, positional support mode
is `tactical_gated`:

- positional reason labels remain in traces;
- positional support has zero effective count;
- positional score bonus is removed from effective score;
- unresolved reply attacks still outrank tactical gain;
- concrete material or promotion gain outranks defended-reply count and generic
  effective score.

When no accepted tactical reason exists, positional support mode is `quiet`:

- positional supports remain active;
- quiet-position tests still verify opening development, castling, and passed
  pawn structure labels.

Optimizer adapter changes:

- exposes `positional_support_mode`;
- reports `positional_support_effective` in objective values;
- uses effective score after positional gating;
- orders material gain before accepted defenses in tactical contexts.

SMT fork witness change:

- `smt_fork_moves` now returns every satisfying fork witness after the solver
  proves the candidate set satisfiable;
- it no longer filters down to one arbitrary model-selected move.

### Verification

Focused tests:

```powershell
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_evidence_ablation.py .\tests\test_dialectical_chess_engine_api.py .\tests\test_dialectical_chess_cleanup.py .\tests\test_dialectical_chess_loss_mining.py -q
```

Result:

- `42 passed in 3.68s`.

Fixed matrix command:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --experiment-matrix --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --matrix-preset core --progress-every 25 --json-out .\scratch\lichess_1200_1600_matrix_core_100_positional_gated.json 1>$null
```

Timeout:

- `300s`, adjusted from the measured `255s` prior matrix runtime.

Result:

- completed successfully;
- elapsed: `259529.37 ms`;
- sample: `100` puzzles;
- line move counts: `2`: 9, `4`: 63, `6`: 26, `8`: 2;
- mate themes: `mateIn1`: 9, `mateIn2`: 10, `mateIn3`: 3.

Sorted rows:

| Case | Solved | Hit Rate | Elapsed ms |
| --- | ---: | ---: | ---: |
| `argument_d2_search1` | 23/100 | 0.23 | 17855.40 |
| `argument_d2_no_smt` | 22/100 | 0.22 | 11908.96 |
| `argument_d2_no_positional` | 22/100 | 0.22 | 12785.30 |
| `argument_d2` | 22/100 | 0.22 | 13963.71 |
| `optimizer_d2_no_positional` | 21/100 | 0.21 | 20705.91 |
| `optimizer_d2` | 21/100 | 0.21 | 22333.81 |
| `argument_d1` | 20/100 | 0.20 | 13212.92 |
| `argument_mate_theme_depth` | 20/100 | 0.20 | 16632.56 |
| `optimizer_mate_theme_depth` | 19/100 | 0.19 | 24431.31 |
| `argument_d0` | 18/100 | 0.18 | 5754.38 |
| `optimizer_static` | 18/100 | 0.18 | 12558.07 |
| `grounded_d1` | 18/100 | 0.18 | 13182.08 |
| `categoriser_d2` | 16/100 | 0.16 | 13822.33 |
| `support_d2` | 16/100 | 0.16 | 14003.87 |
| `grounded_d2` | 14/100 | 0.14 | 13940.81 |
| `support_d1` | 13/100 | 0.13 | 13187.39 |
| `categoriser_d1` | 13/100 | 0.13 | 13233.09 |
| `score_static` | 12/100 | 0.12 | 6014.42 |

Positional gates:

- `argument_d2` versus `argument_d2_no_positional`: pass, `22/100` versus
  `22/100`.
- `optimizer_d2` versus `optimizer_d2_no_positional`: pass, `21/100` versus
  `21/100`.

### Interpretation

Tactical puzzle strength:

- Positional reasons no longer hurt the fixed puzzle slice relative to disabling
  them.
- `argument_d2` improved from the earlier `17/100` positional-on baseline to
  `22/100`.
- `optimizer_d2` improved from the earlier `17/100` positional-on baseline to
  `21/100`.
- The strongest current matrix row is still `argument_d2_search1` at `23/100`.

General chess-play plausibility:

- Positional reasons are still too shallow to be a full strategic evaluator.
- They are now usable as quiet-position evidence instead of global tactical
  tiebreakers.
- The next positional work should add phase/context-specific strategic features
  rather than increasing the weight of the current shallow labels.

Argument-trace interpretability:

- Keeping raw positional labels while exposing effective gating gives better
  traces than deleting positional reasons.
- The trace can now say both what a move claimed positionally and whether those
  claims were allowed to affect selection.

Recommendation:

- Keep positional reasons enabled only with tactical gating.
- Do not make optimizer default yet: it ties its no-positional row but remains
  slower than the argument selector.
- Next workstream should target search/tactical witness quality, especially
  noisy SMT fork witnesses and why `argument_d2_search1` is still the best row.
