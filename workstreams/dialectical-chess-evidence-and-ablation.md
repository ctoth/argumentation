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

Status: complete, with external-data blocker.

Tasks:

- Record current committed sample behavior.
- Identify available external Lichess puzzle CSV paths, if any.
- If no external CSV exists, document the blocker and keep this phase blocked
  rather than inventing synthetic strength data.
- Record current loss-mined suite status.

Acceptance criteria:

- Workstream has exact input-suite paths or an explicit missing-data blocker.

Result:

- Committed smoke EPD: `scripts/dialectical_chess_smoke.epd`.
- Committed Lichess-shaped sample: `scripts/dialectical_chess_puzzles_sample.csv`.
- Generated full-game loss-mining diagnostics exist under `scratch/`, but are
  diagnostic artifacts and were not promoted.
- No real external Lichess puzzle CSV is present in the repository. Strength
  claims against the requested 1200-1600/themed Lichess buckets are blocked
  until a real CSV path is supplied.

### Phase 1: Selector and Ranking Modes

Status: complete.

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

Result:

- `EngineSettings.selector_mode` supports `argument`, `score`, `grounded`,
  `support`, and `categoriser`.
- Default is explicitly `argument`.
- Benchmark JSON includes `selector_mode`.
- UCI emits `info string selector_mode=...`.
- Tests prove `argument` and `score` can choose different synthetic probes.

### Phase 2: Ranking Ablation Harness

Status: complete.

Tasks:

- Extend benchmark ablation to include selector/ranking mode.
- Report hit rate, avoid rate, ms/position, and selected-move deltas.
- Add compact summary by rating bucket and theme for Lichess runs.

Acceptance criteria:

- A single command compares selector modes on an EPD or Lichess CSV suite.
- Output identifies where modes disagree.

Result:

- `--selector-mode-ablation` expands ablation over all selector modes.
- Ablation rows report hit rate, avoid rate, elapsed ms, and
  `selected_move_deltas_vs_first`.
- Lichess-shaped output reports solved/total by rating bucket and theme.
- Smoke command:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py `
  --ablation `
  --epd .\scripts\dialectical_chess_smoke.epd `
  --selector-mode-ablation
```

- Smoke result: all selector/depth/backend/SMT rows scored `2/3`, avoid-rate
  `1.0`, and selected-move deltas `0`. This suite is too small and too
  tactical to show categoriser value.

### Phase 3: Real Lichess Evaluation

Status: blocked for real data; committed sample verified.

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

Result:

- Real requested evaluation is blocked: no external Lichess puzzle CSV was
  found in the repo.
- Committed sample command:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py `
  --lichess-puzzles .\scripts\dialectical_chess_puzzles_sample.csv `
  --selector-mode argument
```

- Sample result: `2/2`, hit-rate `1.0`.
- Buckets: `800-999`: `1/1`; `1200-1399`: `1/1`.
- Themes: `hangingPiece`: `1/1`; `mate`: `1/1`; `mateIn1`: `1/1`.
- This is sample plumbing evidence only, not a strength claim.

### Phase 4: SMT Honesty Gate

Status: complete.

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

Result:

- Mate-in-one witness labeling is now `procedural:mate_in_one` with witness
  `procedural_mate_in_one`.
- Tests prove the existing mate witness equals procedural legal-move mate
  enumeration.
- The old `smt:mate_in_one` strength implication is gone.

### Phase 5: First Real SMT Witness

Status: complete.

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

Result:

- Added `smt_fork_moves`.
- It uses Z3 to choose a legal move satisfying fork target constraints, then
  verifies the move through the owned board before exposing it.
- Test fixture: `r3k3/8/8/1N6/8/8/8/4K3 w - - 0 1`.
- Witness: `b5c7`, exposed as `smt:fork:2:500`.

### Phase 6: Positional Reason Vocabulary

Status: complete.

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

Result:

- Added positional reason families: `development`, `center_control`,
  `king_safety`, `pawn_structure`, `file_control`, `outpost`, and
  `piece_activity`.
- Example opening traces:
  - `development:e2e4:center_pawn`
  - `center_control:e2e4:1`
  - `development:g1f3:minor_piece`
  - `piece_activity:g1f3:mobility_gain:5`
- Example castling trace: `king_safety:e1g1:castle`.
- Example structure trace: `pawn_structure:e4e5:passed_pawn`.

### Phase 7: Positional Reason Ablation

Status: complete on committed smoke/sample suites; blocked for real verdict.

Tasks:

- Run benchmarks with positional reasons off/on.
- Compare selector modes with positional reasons off/on.
- Record where categoriser ranking changes a move because of positional
  conflicts.

Acceptance criteria:

- We can answer whether categoriser ranking adds value once the graph is less
  sparse.

Result:

- Positional reasons are controlled by `EngineSettings.positional_reasons` and
  `--no-positional-reasons`.
- UCI emits `info string positional_reasons=...`.
- Sample positional-on command scored `2/2`; positional-off command also scored
  `2/2`.
- Difference on sample is trace/score quality:
  - with positional reasons, `d1d2` has material, center-control,
    piece-activity, and file-control reasons, score `975`;
  - without positional reasons, `d1d2` only has material, score `900`.
- Categoriser ranking verdict on available committed suites: neutral. The
  smoke/sample suites show no selected-move deltas, so they do not answer the
  real categoriser-value question.

### Phase 8: Report and Next Workstream Link

Status: complete for this workstream.

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

Result:

- Commands and input suites are recorded above.
- Next strength workstream targets:
  - refutation filtering for noisy positional reasons;
  - search witnesses that produce structured arguments instead of scalar-only
    scores;
  - king-safety defeaters for castling/open-file tradeoffs;
  - ADF acceptance for richer non-binary evidence combination;
  - a real Lichess CSV run once the dataset path is supplied.

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

Completion evidence:

- Chess-focused tests:

```powershell
uv run --with chess --with z3-solver pytest `
  .\tests\test_dialectical_chess_engine_api.py `
  .\tests\test_dialectical_chess_evidence_ablation.py `
  .\tests\test_dialectical_chess_cleanup.py `
  .\tests\test_dialectical_chess_loss_mining.py
```

Result: `26 passed`.

- Full repository suite was run once during this workstream:

```powershell
uv run --with chess --with z3-solver pytest .\tests --timeout=120
```

Result: `2758 passed`, `2 skipped`, `1 failed`. The failure was
`tests/test_solver_availability.py::test_sat_backend_acceptance_matches_native_backend`
with a SAT/native preferred-semantics witness mismatch outside the chess-owned
paths.
