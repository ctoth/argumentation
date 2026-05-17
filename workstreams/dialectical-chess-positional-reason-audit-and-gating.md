# Dialectical Chess Positional Reason Audit And Gating

## Status

Status: proposed.

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
