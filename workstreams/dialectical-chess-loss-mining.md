# Dialectical Chess Loss Mining Workstream

## Goal

Convert full-game Stockfish losses into concrete regression positions. The
engine currently loses 10/10 full games to Stockfish 1320 by mate. We need the
first losing decision in each game, not just the final result.

## Output

- A generated diagnostic PGN for the anchor match.
- A generated diagnostic JSON summary of loss turning points.
- A committed small EPD regression suite only after manual review of extracted
  positions.

## Phases

### Phase 0: Add PGN/Log Capture

Status: pending.

Tasks:

- Extend match runner options to accept diagnostic PGN output path.
- Keep PGN output uncommitted by default under `scratch/`.
- Record command, engine settings, and commit in the JSON payload.

Acceptance criteria:

- A Stockfish match can emit PGN without changing match behavior.
- Generated PGN is ignored unless explicitly promoted.

### Phase 1: Mine Candidate Turning Points

Status: pending.

Tasks:

- Parse match PGNs.
- For every loss, replay moves and identify candidate bad decisions:
  - first move after which Stockfish has mate in N within a small bound;
  - first move after which material loss exceeds a threshold;
  - first move that permits an immediate mate or forced queen loss.
- Emit FEN, played move, side to move, result, and suggested avoid move.

Acceptance criteria:

- Each lost game yields at least one candidate turning point or a clear
  "not found within bound" marker.
- The miner never uses generated text summaries as source truth; it replays the
  PGN.

### Phase 2: Review and Promote Regression EPDs

Status: pending.

Tasks:

- Select the clearest mined positions.
- Add `am` avoid moves for obviously losing engine choices.
- Add `bm` defensive moves only when verified by replay/search.
- Keep the initial suite small: 5-20 positions.

Acceptance criteria:

- Regression EPD runs through the existing benchmark runner.
- Current engine fails at least one promoted position before fixes.

### Phase 3: Baseline Report

Status: pending.

Tasks:

- Run current engine on the promoted loss suite.
- Record hit rate, avoid rate, and representative failures.

Acceptance criteria:

- Workstream has a baseline number that later strength work can improve.

## Commands

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline stockfish `
  --match-games 10 `
  --match-max-plies 400 `
  --match-tc 30+0.2
```

## Completion Criteria

- Loss PGN capture exists.
- Turning-point miner exists.
- Reviewed regression EPD exists.
- Current engine baseline on that suite is recorded.
