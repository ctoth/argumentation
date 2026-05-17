# Dialectical Chess King-Safety Defeaters Workstream

## Goal

Stop making moves that collapse the king position. The full-game Stockfish
anchor ended 10/10 by mate. King-safety failures should become defeaters in the
argument graph, not vague evaluation penalties.

## Defeater Types

- `exposes_king_line`: move opens a rook/bishop/queen line to own king.
- `abandons_pinned_defender`: move removes a defender that was shielding a
  king line or mate square.
- `allows_back_rank_mate`: move leaves back-rank mate pattern unresolved.
- `allows_queen_invasion`: move permits queen/rook entry near king with no
  defense.
- `weakens_escape_square`: move removes a critical king escape square.
- `ignores_check_threat`: move does not answer an existing mate/check threat.

## Phases

### Phase 0: Mine Mate Patterns

Status: pending.

Tasks:

- Use loss-mined games to classify mate patterns.
- Record which pattern appears in each loss.

Acceptance criteria:

- At least three concrete mate-pattern FENs are identified.

### Phase 1: King-Line Exposure

Status: pending.

Tasks:

- Detect moves that expose sliding attacks toward own king.
- Add proper defeaters against the candidate move.

Acceptance criteria:

- A move that opens a direct king line is defeated unless it has a forcing
  override.

### Phase 2: Mate-Square and Escape-Square Defeaters

Status: pending.

Tasks:

- Identify mate squares adjacent to the king.
- Track whether candidate moves defend or abandon those squares.
- Track king escape squares and whether candidate moves remove them.

Acceptance criteria:

- Loss-suite positions with one-move mate threats are avoided.

### Phase 3: Defeasible Overrides

Status: pending.

Tasks:

- Allow checkmate, forced material win, or verified defense witnesses to defeat
  king-safety objections.
- Keep overrides explicit in `arguments.py`.

Acceptance criteria:

- The engine can still play a forcing tactical move that temporarily weakens
  king safety when the tactic is verified.

## Verification

```powershell
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_loss_regressions.epd
uv run .\scripts\dialectical_chess_bench.py --run-uci-match --match-baseline stockfish --match-games 2 --match-max-plies 400 --match-tc 30+0.2
```

## Completion Criteria

- King-safety defeaters appear in AF JSON traces.
- Loss-suite avoid rate improves.
- Full-game Stockfish losses either decrease or move to later, different
  failure modes that are recorded.
