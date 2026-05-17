# Dialectical Chess Evidence and Ablation Workstream

## Goal

Resolve the current evidence-layer issues before claiming the argumentation
engine is stronger:

- SMT currently exercises plumbing but does not add decision power.
- Quiet middlegame positions have too few reasons, so argumentation often falls
  back to material score.
- `categoriser_scores` is always used when available, but we have not measured
  whether it improves selection.
- Lichess puzzle evaluation exists, but only the tiny committed sample has been
  run; it does not answer rating-bucket or theme questions.

This workstream makes those claims measurable and then improves the evidence
vocabulary.

## Current Observations

- `smt_mate_in_one_moves` enumerates legal moves, checks mate procedurally, and
  then asks Z3 to satisfy an unconstrained disjunction over already-known mate
  move labels. That is not an SMT search.
- In quiet positions, many moves have no support reasons and only
  `objection:no_immediate_tactical_warrant`, so grounded acceptance and ranking
  are not informative.
- `bounded_reply_attacks` is useful because it keeps reply/refutation structure
  visible instead of collapsing it into a score.
- Loss mining is the right accountability loop: every full-game failure should
  become a typed regression artifact.

## Required Outcomes

- Selector/ranking ablation exists and is benchmarkable.
- Real Lichess sample evaluation by rating bucket and theme exists.
- SMT witness code is either made substantive or explicitly relabeled as
  procedural mate witness plumbing.
- Positional reason types exist and appear in argument traces.
- We can say whether categoriser ranking helps on at least one real suite.

## Non-Negotiable Rules

- Do not use tiny committed samples for strength claims.
- Do not call a procedural legal-move enumeration an SMT solver contribution.
- Keep generated Lichess CSV slices, benchmark JSON, logs, and PGNs
  uncommitted unless explicitly promoted.
- Every new evidence type must appear in benchmark JSON and AF/trace output.
- Every selector mode must preserve UCI legality and pass smoke tests.

## Phases

### Phase 0: Baseline and Fixture Inventory

Status: pending.

Tasks:

- Record current committed sample behavior.
- Identify available external Lichess puzzle CSV paths, if any.
- If no external CSV exists, document the blocker and keep this phase blocked
  rather than inventing synthetic strength data.
- Record current loss-mined suite status.

Acceptance criteria:

- Workstream has exact input-suite paths or an explicit missing-data blocker.

### Phase 1: Selector and Ranking Modes

Status: pending.

Tasks:

- Add selector/ranking settings to `EngineSettings`.
- Implement modes:
  - `argument`: current argument-first selector;
  - `score`: scalar score then UCI;
  - `grounded`: grounded acceptance then score;
  - `support`: accepted support/defense counts then score;
  - `categoriser`: categoriser ranking then support/score.
- Make the mode visible in benchmark JSON and UCI info string.

Acceptance criteria:

- Existing default behavior is preserved as `argument` or `categoriser`, with
  the chosen default named explicitly.
- Tests prove at least two modes can choose different moves on a synthetic
  position/probe set.

### Phase 2: Ranking Ablation Harness

Status: pending.

Tasks:

- Extend benchmark ablation to include selector/ranking mode.
- Report hit rate, avoid rate, ms/position, and selected-move deltas.
- Add compact summary by rating bucket and theme for Lichess runs.

Acceptance criteria:

- A single command compares selector modes on an EPD or Lichess CSV suite.
- Output identifies where modes disagree.

### Phase 3: Real Lichess Evaluation

Status: pending.

Tasks:

- Run Lichess CSV evaluation for at least:
  - 1200-1600 rating bucket;
  - tactical themes: mate, hangingPiece, fork, pin, discoveredAttack,
    defensiveMove if present.
- Compare dialectic depth 0 vs 1 vs 2.
- Compare selector modes.

Acceptance criteria:

- Results include total positions per bucket/theme.
- Claims are labeled sample-based unless the full dataset was run.

### Phase 4: SMT Honesty Gate

Status: pending.

Tasks:

- Rename current mate witness if it remains procedural.
- Add tests showing the current witness behavior is equivalent to procedural
  mate enumeration.
- Decide one of:
  - implement a real SMT query for a constrained tactical pattern; or
  - explicitly document SMT as future plumbing and remove it from strength
    claims.

Acceptance criteria:

- No output implies Z3 discovered a move unless Z3 actually solved a constrained
  move/position problem.

### Phase 5: First Real SMT Witness

Status: pending.

Tasks:

- Pick one tractable pattern:
  - fork existence;
  - skewer/pin line existence;
  - discovered attack;
  - mate-in-one without pre-enumerating mate moves.
- Encode move variables and target constraints.
- Verify solver result by applying the move on the owned board.

Acceptance criteria:

- At least one SMT witness can discover a move not preclassified by procedural
  mate enumeration.
- Solver result is independently verified before becoming an argument.

### Phase 6: Positional Reason Vocabulary

Status: pending.

Tasks:

- Add reason types:
  - `development`;
  - `center_control`;
  - `king_safety`;
  - `pawn_structure`;
  - `open_file_control`;
  - `outpost`;
  - `piece_activity`.
- Keep each reason simple and testable.
- Add corresponding objections where the reason creates a tradeoff.

Acceptance criteria:

- Quiet opening/middlegame positions produce non-empty support reasons.
- Argument traces show conflicting positional reasons.

### Phase 7: Positional Reason Ablation

Status: pending.

Tasks:

- Run benchmarks with positional reasons off/on.
- Compare selector modes with positional reasons off/on.
- Record where categoriser ranking changes a move because of positional
  conflicts.

Acceptance criteria:

- We can answer whether categoriser ranking adds value once the graph is less
  sparse.

### Phase 8: Report and Next Workstream Link

Status: pending.

Tasks:

- Update this workstream with:
  - Lichess bucket results;
  - selector/ranking ablation results;
  - SMT honesty decision;
  - positional reason examples.
- Link concrete findings into:
  - refutation filtering;
  - search witnesses;
  - king-safety defeaters;
  - ADF acceptance.

Acceptance criteria:

- Every major claim has a command and input suite.
- Next strength workstream has explicit data to target.

## Commands

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --lichess-puzzles C:\path\to\lichess_db_puzzle.csv `
  --rating-min 1200 `
  --rating-max 1600 `
  --limit 1000

uv run .\scripts\dialectical_chess_bench.py `
  --ablation `
  --epd .\scripts\dialectical_chess_smoke.epd

uv run --with chess --with z3-solver pytest `
  .\tests\test_dialectical_chess_cleanup.py `
  .\tests\test_dialectical_chess_loss_mining.py `
  .\tests\test_dialectical_chess_engine_api.py
```

## Completion Criteria

- Selector/ranking modes exist and are measured.
- Real Lichess bucket/theme results are recorded or explicitly blocked by
  missing dataset.
- SMT contribution is truthful.
- Quiet positions get positional arguments.
- Categoriser ranking has an evidence-backed verdict: useful, neutral, or not
  yet meaningful.
