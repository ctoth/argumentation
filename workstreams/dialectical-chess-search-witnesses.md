# Dialectical Chess Search Witness Workstream

## Goal

Use search to produce argument witnesses. Search should not replace the
dialectical decision layer. It should discover reply attacks, defenses,
terminal warrants, and bounded proof lines that the argument graph can inspect.

## Witness Types

- `mate_witness(depth, line)`
- `material_win_witness(depth, line, swing)`
- `defense_witness(reply, defense_move, line)`
- `escape_witness(check_line, escape_move)`
- `compensation_witness(refutation, counter_threat, line)`

## Phases

### Phase 0: Normalize Search Results

Status: pending.

Tasks:

- Replace ad hoc search tuples with typed witness records.
- Keep existing `negamax` and `alphabeta` behavior available.
- Include depth, score, principal line, and witness kind.

Acceptance criteria:

- Existing search-depth options still work.
- Benchmark JSON exposes witness records without breaking old fields.

### Phase 1: Reply-Attack Search

Status: pending.

Tasks:

- For each candidate move, search opponent replies for hard tactical wins.
- Emit reply-attack witnesses instead of only changing score.

Acceptance criteria:

- A bad candidate has explicit `reply_attack` reasons tied to search lines.

### Phase 2: Defense Search

Status: pending.

Tasks:

- For each reply attack, search legal continuations for a defense.
- Emit defense witnesses when the reply attack is neutralized.

Acceptance criteria:

- Argument traces show defended and undefended reply attacks separately.

### Phase 3: Bounded Proof Export

Status: pending.

Tasks:

- Include witness lines in AF JSON.
- Include witness lines in benchmark result JSON.
- Keep PGN/trace artifacts diagnostic by default.

Acceptance criteria:

- A loss-suite failure can be explained by a concrete line, not just a score.

### Phase 4: Performance Gate

Status: pending.

Tasks:

- Measure ms/position at depths 1, 2, and 3.
- Add depth/time controls so UCI does not time out.

Acceptance criteria:

- Internal UCI smoke has 0 timeouts.
- Short Stockfish smoke has 0 timeouts.

## Commands

```powershell
uv run .\scripts\dialectical_chess_bench.py --ablation --epd .\scripts\dialectical_chess_smoke.epd
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_loss_regressions.epd --search-depth 2 --search-backend alphabeta
```

## Completion Criteria

- Search produces named argument witnesses.
- Selection still flows through argument acceptance/ranking.
- Runtime stays inside UCI smoke time controls.
