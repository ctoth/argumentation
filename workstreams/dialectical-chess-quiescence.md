# Dialectical Chess Quiescence Workstream

## Goal

Prevent the argument graph from accepting tactically unstable leaf positions.
If a line ends while checks, captures, promotions, or direct mate threats are
available, the leaf claim is not quiet and should be extended or marked
defeasible.

## Quietness Conditions

A leaf is quiet only when none of these are present for the side to move:

- legal check;
- legal capture above pawn threshold;
- legal promotion;
- mate-in-one;
- hanging queen or rook capture;
- unresolved check on own king.

## Phases

### Phase 0: Quietness Predicate

Status: pending.

Tasks:

- Add a named quietness predicate in `search.py`.
- Return the reason a position is not quiet.

Acceptance criteria:

- Unit tests cover quiet and non-quiet leaves.

### Phase 1: Quiescence Extension

Status: pending.

Tasks:

- Extend only checks, captures, promotions, and mate threats.
- Keep depth and node caps explicit.
- Return witness lines, not only scores.

Acceptance criteria:

- Quiescence does not explode on smoke positions.
- UCI smokes stay within time controls.

### Phase 2: Argument Integration

Status: pending.

Tasks:

- Convert non-quiet leaf findings into objections.
- Convert quiescence-resolved tactics into support or defense witnesses.

Acceptance criteria:

- AF traces distinguish quiet support from volatile support.

### Phase 3: Benchmark Gate

Status: pending.

Tasks:

- Compare loss-suite avoid rate with quiescence off/on.
- Compare ms/position.

Acceptance criteria:

- No strength claim is accepted without runtime cost.

## Commands

```powershell
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_loss_regressions.epd --search-depth 1
uv run .\scripts\dialectical_chess_bench.py --ablation --epd .\scripts\dialectical_chess_loss_regressions.epd
```

## Completion Criteria

- Tactical leaf volatility is visible in arguments.
- Quiescence improves at least one promoted loss regression without breaking
  smoke benchmarks.
- Runtime is measured and reported.
