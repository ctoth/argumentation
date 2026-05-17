# Dialectical Chess Elo Evaluation Workstream

## Goal

Evaluate playing strength honestly. A two-game smoke match is not Elo. This
workstream builds from protocol validity to relative Elo estimates, then to
absolute-ish calibration against external engines when suitable anchors are
available.

## Current State

- `scripts/dialectical_chess_bench.py --run-uci-match` can run a bounded
  `fast-chess` smoke match.
- The current random-baseline smoke at `10+0.1` completed two games with 0
  crashes, 0 timeouts, and 0 losses-on-time.
- The current random-baseline smoke at `1+0.01` fails honestly with 1 timeout
  and 1 loss-on-time in a two-game run.
- `scripts/dialectical_chess_random_uci.py` is a committed deterministic weak
  legal baseline.
- `scripts/dialectical_chess_openings.epd` is a committed small opening set.
- Historical fixed-game relative matches were run before timeout/loss-on-time
  failure counts were promoted into the benchmark payload:
  - default vs random baseline: 20 games, `13/7/0`, +269.37 +/- 89.78 Elo
    relative to the committed random baseline;
  - default vs no-SMT ablation: 20 games, `5/10/5`, 0.00 +/- 0.00 Elo under
    this exact setup.
- Current absolute Elo remains unknown.

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

Status: complete for a lenient two-game random-baseline smoke; blitz smoke
currently exposes a timeout and is not a clean strength measurement.

Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-games 2 `
  --match-max-plies 4
```

Observed current clean result:

- Runner: `fast-chess`.
- Games: 2.
- Time control: `10+0.1`.
- Result: 2 draws by adjudication against the committed random baseline.
- Return code: 0.
- Failures: 0 timeouts, 0 crashes, 0 losses-on-time.
- Interpretation: UCI match harness works; Elo remains unknown.

Observed current contaminated result:

- Command shape: same two-game random-baseline smoke at `1+0.01`.
- Result: JSON `ok: false`.
- Failures: 1 timeout, 0 crashes, 1 loss-on-time.
- Interpretation: do not use this run as a strength estimate.

### Phase 1: Committed Weak Baseline

Status: complete.

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

Status: complete.

Goal: avoid measuring only one deterministic start-position line.

Tasks:

- Add a small committed EPD opening suite.
- Use standard legal positions after common opening moves.
- Pass that suite to `fast-chess -openings file=... format=epd`.

Acceptance criteria:

- External match command uses the opening suite.
- Match output identifies games from varied starting positions.

### Phase 3: Fixed-Game Relative Rating

Status: historical only for the first 20-game random-baseline run. Re-run under
the current timeout/loss-on-time checks before treating it as current strength.

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

Observed historical first run:

- Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline random `
  --match-games 20 `
  --match-max-plies 80 `
  --match-tc 1+0.01
```

- Runner: `fast-chess`.
- Openings: `scripts/dialectical_chess_openings.epd`.
- Games: 20.
- W/D/L: 13/7/0 from the dialectical engine's perspective.
- Score: 16.5/20, 82.50%.
- Reported relative Elo: +269.37 +/- 89.78.
- Interpretation: the engine was clearly stronger than this deterministic weak
  baseline under that setup. Because timeout/loss-on-time checks were added
  later, this must be re-run before being used as the current rating.

### Phase 4: Ablation Rating

Status: historical only for the first no-SMT fixed-game run. Re-run under the
current timeout/loss-on-time checks before treating it as current strength.

Goal: measure whether SMT and dialectical depth help.

Required comparisons:

- default engine vs `--no-smt-mate`;
- default engine vs dialectic depth 0;
- default engine vs shallow search variants once UCI options expose them.

Acceptance criteria:

- Same openings and time control across variants.
- Report says whether the result is inconclusive when confidence is wide.

Observed historical no-SMT run:

- Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline nosmt `
  --match-games 20 `
  --match-max-plies 80 `
  --match-tc 1+0.01
```

- Runner: `fast-chess`.
- Openings: `scripts/dialectical_chess_openings.epd`.
- Games: 20.
- W/D/L: 5/10/5.
- Score: 10.0/20, 50.00%.
- Reported relative Elo: 0.00 +/- 0.00.
- Interpretation: this run found no playing-strength difference between
  default SMT and `--no-smt-mate`; because all wins/losses paired symmetrically,
  this is a narrow historical statement about that setup, not proof that SMT
  never matters.

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

Status: Stockfish 18 detected and smoke-tested at its minimum exposed UCI Elo.
No absolute Elo has been established.

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

Observed anchor smoke:

- Detected executable:
  `C:\Users\Q\AppData\Local\Microsoft\WinGet\Links\stockfish.exe`.
- UCI identity: Stockfish 18.
- Weak-level configuration:
  - `option.UCI_LimitStrength=true`;
  - `option.UCI_Elo=1320`;
  - `option.Threads=1`;
  - `option.Hash=16`.
- Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline stockfish `
  --match-games 2 `
  --match-max-plies 6 `
  --match-tc 10+0.1
```

- Runner: `fast-chess`.
- Result: 2 draws by adjudication against `StockfishElo1320`.
- Failures: 0 timeouts, 0 crashes, 0 losses-on-time.
- Interpretation: Stockfish anchoring is wired and executable. This is not an
  Elo estimate because the match is only two games and ends by shallow
  adjudication.

Observed bounded sample:

- Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline stockfish `
  --match-games 4 `
  --match-max-plies 20 `
  --match-tc 30+0.2
```

- Runner: `fast-chess`.
- Baseline: Stockfish 18 with `UCI_LimitStrength=true`, `UCI_Elo=1320`,
  `Threads=1`, `Hash=16`.
- Games: 4.
- W/D/L from the dialectical engine's perspective: 0/3/1.
- Score: 1.5/4, 37.50%.
- Reported relative Elo: -88.74 +/- 136.27.
- Failures: 0 timeouts, 0 crashes, 0 losses-on-time.
- Interpretation: the engine is below this Stockfish 1320 anchor in this small
  bounded sample, but the confidence interval is wide and the max-ply cap still
  makes this a calibration smoke rather than a stable absolute rating.

Observed full-game sample:

- Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline stockfish `
  --match-games 10 `
  --match-max-plies 400 `
  --match-tc 30+0.2
```

- Runner: `fast-chess`.
- Baseline: Stockfish 18 with `UCI_LimitStrength=true`, `UCI_Elo=1320`,
  `Threads=1`, `Hash=16`.
- Games: 10.
- Effective cap: `fast-chess -maxmoves 200`, high enough that every game ended
  by mate before adjudication.
- W/D/L from the dialectical engine's perspective: 0/0/10.
- Score: 0.0/10, 0.00%.
- Reported relative Elo: `-inf +/- nan`.
- Failures: 0 timeouts, 0 crashes, 0 losses-on-time.
- Runtime: about 7 minutes 10 seconds.
- Interpretation: the capped/adjudicated samples were misleading. In full-game
  play, the current engine loses every game to Stockfish 1320 by mate under
  this setup.

## Completion Criteria

- Weak baseline exists and is committed.
- Opening set exists and is committed.
- External `fast-chess` match against the weak baseline completes.
- At least one fixed-game relative rating run is recorded.
- At least one ablation rating run is recorded.
- Workstream documentation distinguishes smoke, relative Elo, SPRT, and
  absolute-ish calibration.
