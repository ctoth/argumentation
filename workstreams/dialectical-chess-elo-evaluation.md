# Dialectical Chess Elo Evaluation Workstream

## Goal

Evaluate playing strength honestly. A two-game smoke match is not Elo. This
workstream builds from protocol validity to relative Elo estimates, then to
absolute-ish calibration against external engines when suitable anchors are
available.

## Current State

- `scripts/dialectical_chess_bench.py --run-uci-match` can run a bounded
  `fast-chess` smoke match.
- The smoke match completed two games between the engine and its no-SMT
  ablation with no crashes or illegal moves.
- That smoke produced `0/0/2` and no meaningful Elo.
- There is no committed weak baseline engine yet.
- There is no committed opening set for rating matches yet.
- There is no statistically meaningful SPRT or fixed-game match result yet.

## Evaluation Rules

- Do not report absolute Elo without a calibrated external anchor.
- Report relative Elo as `engine A vs engine B under this exact command`.
- Every rating claim must include:
  - commit;
  - command;
  - runner;
  - engines and settings;
  - openings;
  - time control;
  - game count;
  - W/D/L;
  - crashes, illegal moves, time losses;
  - Elo and confidence interval if the runner reports one.
- Generated PGN/log/config/report artifacts stay uncommitted unless explicitly
  promoted.
- Smoke matches prove harness viability only; they do not prove strength.

### Phase 0: External Match Smoke

Status: complete.

Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-games 2 `
  --match-max-plies 4
```

Observed result:

- Runner: `fast-chess`.
- Games: 2.
- Result: 2 draws by adjudication.
- Return code: 0.
- Interpretation: UCI match harness works; Elo remains unknown.

### Phase 1: Committed Weak Baseline

Goal: add a deliberately weak legal UCI baseline so relative Elo can be measured
without relying on a local third-party engine.

Tasks:

- Add `scripts/dialectical_chess_random_uci.py`.
- The baseline must:
  - speak enough UCI for `fast-chess`;
  - never emit illegal moves;
  - return `bestmove 0000` on game-over positions;
  - be deterministic under a seed or deterministic position hash.
- Add a runner option to compare against that baseline.

Acceptance criteria:

- `fast-chess` can complete a bounded match against the baseline.
- Result reports W/D/L and runner output.
- No illegal moves or crashes.

### Phase 2: Opening Set

Goal: avoid measuring only one deterministic start-position line.

Tasks:

- Add a small committed EPD opening suite.
- Use standard legal positions after common opening moves.
- Pass that suite to `fast-chess -openings file=... format=epd`.

Acceptance criteria:

- External match command uses the opening suite.
- Match output identifies games from varied starting positions.

### Phase 3: Fixed-Game Relative Rating

Goal: produce the first meaningful relative-strength estimate.

Initial required run:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline random `
  --match-games 20 `
  --match-max-plies 80 `
  --match-tc 5+0.05
```

Acceptance criteria:

- At least 20 games complete.
- No illegal moves or crashes.
- Output contains W/D/L and Elo estimate from `fast-chess`.
- Result is reported as relative Elo versus the committed weak baseline, not
  absolute Elo.

### Phase 4: Ablation Rating

Goal: measure whether SMT and dialectical depth help.

Required comparisons:

- default engine vs `--no-smt-mate`;
- default engine vs dialectic depth 0;
- default engine vs shallow search variants once UCI options expose them.

Acceptance criteria:

- Same openings and time control across variants.
- Report says whether the result is inconclusive when confidence is wide.

### Phase 5: SPRT

Goal: run sequential testing only after fixed-game matches are stable.

Tasks:

- Use `fast-chess -sprt elo0=0 elo1=10 alpha=0.05 beta=0.05`.
- Start with the random baseline or an ablation, not Stockfish.
- Save output as diagnostics unless a report is explicitly requested.

Acceptance criteria:

- SPRT terminates or is reported as inconclusive with exact game count.
- No crash/time-forfeit contamination.

### Phase 6: External Anchor

Goal: estimate an absolute-ish Elo only when an anchor engine is installed and
configured to a known weak level.

Tasks:

- Detect candidate external engines explicitly.
- Prefer a weak, configurable UCI engine over Stockfish default strength.
- Run enough games to bridge from the committed random baseline to the external
  anchor.

Acceptance criteria:

- Absolute-ish number is labeled with the anchor engine and configuration.
- If no anchor exists, say Elo is unknown rather than inventing one.

## Completion Criteria

- Weak baseline exists and is committed.
- Opening set exists and is committed.
- External `fast-chess` match against the weak baseline completes.
- At least one fixed-game relative rating run is recorded.
- Workstream documentation distinguishes smoke, relative Elo, SPRT, and
  absolute-ish calibration.
