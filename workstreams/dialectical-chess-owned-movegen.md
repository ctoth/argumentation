# Dialectical Chess Owned Movegen Workstream

## Goal

Replace the bootstrap dependency on `python-chess` for board state and legal
move generation with an owned, tested chess substrate. This is not an
optimization project first. It is a correctness project. The owned substrate
must pass perft and differential legal-move checks before the dialectical engine
is allowed to depend on it for UCI, PGN, SMT, search, or benchmarks.

## Current State

- `scripts/dialectical_chess_owned.py` parses and serializes six-field FEN.
- It exposes square lookup and coordinate helpers.
- It computes material balance.
- It generates pseudo-legal and legal moves.
- It filters legal moves by king safety.
- It applies moves immutably.
- It implements check, checkmate/stalemate move absence, castling, en passant,
  promotion, perft, divide, and differential oracle checks.
- The probe and UCI engine use the owned board as their runtime substrate.
- `python-chess` remains the differential correctness oracle and PGN/SAN
  substrate.

## Non-Negotiable Rules

- Do not route engine move selection through owned movegen until perft depth 3
  passes on standard fixtures.
- Do not claim owned movegen is complete without castling, en passant,
  promotion, check evasions, pinned pieces, and double-check fixtures.
- Curated generated legal move sets must continue to be compared against
  `python-chess` in selftests after promotion.
- Perft failures block every downstream task. Do not compensate in
  argumentation, SMT, search, or benchmarks.
- Keep diagnostics uncommitted unless the task explicitly asks to promote a
  benchmark/perft artifact.
- Use `uv run`, not bare `python`.

## Target Module Shape

The sidecar remains under `scripts/` until any package promotion:

- `scripts/dialectical_chess_owned.py`
  - `OwnedBoard`
  - `OwnedMove`
  - FEN parse/serialize
  - make/unmake or immutable apply
  - pseudo-legal generation
  - legal generation
  - attack detection
  - check/game-over detection
  - perft
- later split, only if needed:
  - `scripts/dialectical_chess/board.py`
  - `scripts/dialectical_chess/movegen.py`
  - `scripts/dialectical_chess/perft.py`

### Phase 0: FEN and Board Invariants

Status: complete.

Tasks:

- Parse six-field FEN.
- Serialize back to six-field FEN.
- Reject invalid piece placement:
  - not eight ranks;
  - rank width not eight;
  - illegal piece symbol;
  - invalid side-to-move;
  - invalid castling field;
  - invalid en-passant square;
  - invalid clocks.
- Validate exactly one white king and one black king for legal-game mode.
- Keep a permissive parse mode only if a benchmark suite requires illegal
  analysis positions; mark it explicitly.

Acceptance criteria:

- Roundtrip standard start FEN exactly.
- Roundtrip mate smoke FEN exactly.
- `piece_at("a1")` returns the expected piece on fixtures.
- Material balance agrees with `python-chess` on at least 20 curated FENs.

Commands:

```powershell
uv run .\scripts\dialectical_chess_owned.py "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
uv run .\scripts\dialectical_chess_owned.py "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1" --square a1
```

### Phase 1: Move Type and Coordinate Operations

Status: complete.

Tasks:

- Add `OwnedMove(from_square, to_square, promotion=None, kind="normal")`.
- Support UCI parse/format:
  - normal moves: `e2e4`;
  - promotions: `a7a8q`;
  - castling still encoded as king move (`e1g1`).
- Add square helpers:
  - file/rank conversion;
  - board bounds;
  - color of piece;
  - piece type;
  - same-side/opponent tests.

Acceptance criteria:

- UCI roundtrip fixtures pass for normal moves, promotions, and castling moves.
- Invalid UCI strings are rejected.
- Coordinate helpers agree with known squares: `a1=0`, `h1=7`, `a8=56`,
  `h8=63`.

### Phase 2: Pseudo-Legal Non-King Moves

Status: complete.

Tasks:

- Generate pawn pushes and captures, including double pushes from initial rank.
- Generate knight moves.
- Generate bishop rays.
- Generate rook rays.
- Generate queen rays.
- Generate king one-square moves, but not castling yet.
- Include promotions for pawn moves to the last rank: queen, rook, bishop,
  knight.
- Do not filter self-check in this phase.

Acceptance criteria:

- Start-position pseudo-legal move count is at least the 20 legal moves and
  contains exactly the legal pawn/knight moves for that position.
- Sliding pieces stop at blockers and include opponent capture squares.
- Promotion fixture emits four promotion choices.
- Pseudo-legal output is deterministic sorted UCI.

### Phase 3: Attack Detection and Check

Status: complete.

Tasks:

- Implement `is_square_attacked(square, by_color)`.
- Implement `king_square(color)`.
- Implement `in_check(color)`.
- Handle attack detection by:
  - pawns;
  - knights;
  - bishops/queens diagonally;
  - rooks/queens orthogonally;
  - kings.

Acceptance criteria:

- Attack detection agrees with `python-chess` on curated fixtures.
- Pinned pieces still attack according to chess attack rules where appropriate;
  legal filtering is a later phase.
- Check fixtures cover knight check, sliding check, pawn check, adjacent king
  illegality, and discovered line opening.

### Phase 4: Make/Unmake or Immutable Apply

Status: complete with immutable apply.

Tasks:

- Implement move application.
- Preserve and update:
  - side to move;
  - castling rights;
  - en-passant square;
  - halfmove clock;
  - fullmove number.
- Handle:
  - captures;
  - promotions;
  - en passant capture;
  - castling rook movement.

Acceptance criteria:

- Applying UCI fixture sequences reaches exact expected FENs.
- Applying a move never mutates the source board if using immutable apply.
- If mutable make/unmake is chosen, make followed by unmake restores exact FEN.

### Phase 5: Legal Move Filtering

Status: complete.

Tasks:

- Filter pseudo-legal moves that leave own king in check.
- Generate check evasions.
- Handle double check.
- Reject king moves into attacked squares.
- Reject castling through, out of, or into check.
- Reject en passant moves that expose king to rook/bishop/queen line attack.

Acceptance criteria:

- Owned legal move set equals `python-chess` legal move set on all curated
  fixtures.
- Checkmate fixture has zero legal moves and `in_check=True`.
- Stalemate fixture has zero legal moves and `in_check=False`.

### Phase 6: Castling, En Passant, Promotion Completion

Status: complete.

Tasks:

- Castling:
  - rights from FEN;
  - clear path;
  - king not currently in check;
  - transit and destination squares not attacked;
  - rook lands correctly.
- En passant:
  - target square from FEN;
  - legal capture generation;
  - captured pawn removal;
  - discovered-check illegality filter.
- Promotion:
  - quiet and capture promotions;
  - four promotion pieces;
  - SAN/PGN integration later remains outside owned substrate if still using
    `python-chess` for notation.

Acceptance criteria:

- Curated castling fixtures match `python-chess`.
- Curated en-passant fixtures match `python-chess`.
- Curated promotion fixtures match `python-chess`.

### Phase 7: Perft Harness

Status: complete.

Tasks:

- Implement `owned_perft(board, depth)`.
- Add JSON output for perft diagnostics.
- Add divide output for root move counts.
- Compare owned perft to expected counts and optionally to `python-chess`.

Required initial perft fixtures:

| Name | FEN | Depth 1 | Depth 2 | Depth 3 |
|---|---|---:|---:|---:|
| startpos | `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` | 20 | 400 | 8902 |
| kiwipete | `r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1` | 48 | 2039 | 97862 |
| promotion | `4k3/P7/8/8/8/8/8/4K3 w - - 0 1` | 9 | 41 | 500 |

The non-startpos values are pinned in `scripts/dialectical_chess_owned.py`.

Acceptance criteria:

- Startpos perft depth 1-3 matches exactly.
- At least one castling/en-passant/promotion perft fixture matches exactly.
- Divide output identifies the first mismatching root move when a fixture
  fails.

### Phase 8: Differential Corpus

Status: complete.

Tasks:

- Build a curated FEN corpus:
  - start position;
  - mate;
  - stalemate;
  - single check;
  - double check;
  - pinned piece;
  - castling both sides;
  - en passant legal;
  - en passant illegal due to discovered check;
  - promotion quiet;
  - promotion capture;
  - underpromotion.
- For each FEN, compare owned legal UCI set to `python-chess`.
- Record missing and extra moves on failure.

Acceptance criteria:

- All curated FENs match exactly.
- Failure output names the FEN, missing moves, and extra moves.

### Phase 9: Engine Integration Gate

Status: complete.

Tasks:

- Promote owned board/legal moves into the default probe and UCI runtime path.
- Keep `python-chess` out of move selection; use it only for notation,
  external format parsing, and selftest oracle checks.
- Leave hidden compatibility flags only where old command lines may still pass
  them; they must not select between runtime move generators.

Acceptance criteria:

- Default engine behavior uses owned movegen.
- UCI startpos and mate smoke choose legal moves from the owned board.
- Benchmark settings report `"movegen": "owned"` and no benchmark command
  depends on `--owned-movegen`.

## Completion Criteria

- Owned FEN roundtrip works.
- Owned legal move sets match `python-chess` on curated corpus.
- Perft depth 1-3 passes on startpos and special-move fixtures.
- Probe and UCI paths use owned movegen by default.
- Benchmark runner records owned movegen in settings and no longer exposes the
  bootstrap comparison flags.

## Known Traps

- Pseudo-legal move counts are not legal move counts.
- En passant discovered-check bugs are common and must have fixtures.
- Castling bugs often pass startpos perft; special fixtures are required.
- Promotion tests must include underpromotion, not only queen promotion.
- `python-chess` agreement is an oracle for this workstream, not a permanent
  architecture decision.

