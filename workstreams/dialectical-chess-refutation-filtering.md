# Dialectical Chess Refutation Filtering Workstream

## Goal

Make the engine reject moves with obvious tactical refutations before scalar
score tie-breaks. This is the first survival workstream. A candidate move that
allows immediate mate or decisive material loss should be defeated unless all
legal candidates are equally refuted.

## Argumentation Shape

- Candidate move: `move:<uci>`.
- Opponent refutation: `reply_attack:<move>:<reply>:<kind>`.
- Defense: `defense:<move>:<reply>:<defense_move>:<kind>`.
- Defeat relation:
  - refutation attacks candidate move;
  - defense attacks refutation;
  - un-defended hard refutation defeats soft support.

## Refutation Kinds

Start with hard, testable refutations:

- `reply_mate`: opponent reply checkmates.
- `reply_mate_threat`: opponent reply creates mate-in-one threat.
- `reply_wins_queen`: opponent reply wins queen with no recapture in bound.
- `reply_wins_rook_or_more`: material swing at or above rook value.
- `reply_forcing_check_sequence`: bounded check sequence with no legal escape.

## Phases

### Phase 0: Loss-Suite Baseline

Status: pending.

Tasks:

- Use the loss-mined EPD suite.
- Record current avoid/hit rates.

Acceptance criteria:

- At least one failing position demonstrates a refuted move currently selected.

### Phase 1: Immediate Mate Refutations

Status: pending.

Tasks:

- For each candidate move, enumerate legal opponent replies.
- If a reply checkmates, add a hard reply attack.
- Candidate is acceptable only if no non-refuted alternative exists.

Acceptance criteria:

- Engine avoids moves that allow immediate mate when an alternative exists.
- Existing mate-in-one smoke still chooses own mate.

### Phase 2: Mate-Threat Refutations

Status: pending.

Tasks:

- Detect replies that create an unavoidable mate-in-one threat.
- Add defense arguments for candidate continuations that eliminate the threat.

Acceptance criteria:

- Regression tests include at least one "ignore mate threat" position.
- Argument trace identifies the mate threat and defense, if any.

### Phase 3: Decisive Material Refutations

Status: pending.

Tasks:

- Detect opponent replies that win queen or rook-level material.
- Allow defenses that recapture or produce superior forcing compensation.
- Keep thresholds explicit and configurable.

Acceptance criteria:

- Engine stops hanging queen/rook in loss-suite positions.
- Capture-best smoke still chooses the queen capture.

### Phase 4: Selection Integration

Status: pending.

Tasks:

- Feed refutations into `arguments.py`.
- Make un-defended hard refutations outrank heuristic support.
- Keep scalar scores as final tie-breaks only after argument status.

Acceptance criteria:

- `selection_key` or successor ordering names hard refutation status explicitly.
- AF JSON traces include refutation and defense nodes.

## Verification

```powershell
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_smoke.epd
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_loss_regressions.epd
@('uci','isready','position fen <loss-fen>','go','quit') | uv run .\scripts\dialectical_chess_probe.py --uci
```

## Completion Criteria

- Loss-suite avoid rate improves.
- No legal move selected by the engine allows immediate mate when a safe legal
  move exists in the tested positions.
- Refutations are represented as argument attacks, not hidden scalar penalties.
