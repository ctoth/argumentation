# Dialectical Chess Engine Workstream

## Goal

Build a real, self-contained chess engine experiment that uses this repository's
argumentation machinery as a first-class decision layer. The target is not Elo
parity with Stockfish. The target is an engine that can:

- speak UCI well enough to be driven by a chess GUI or CLI;
- accept FEN and PGN inputs;
- generate legal moves through a chess-state substrate we can eventually own;
- choose a move by constructing and evaluating dialectical move arguments;
- introduce bounded search as refutation and defense generation;
- preserve argument graphs, chosen lines, and PGN traces as inspectable proof
  artifacts.

This workstream is intentionally sidecar-first. The current implementation
lives under `scripts/` while the design is still experimental. Do not promote it
into `src/argumentation` until the engine has stable tests, a clear API, and a
reason to be part of the package rather than a consumer of the package.

## Core Thesis

Chess has a native dialectical structure:

- a candidate move is a proponent claim;
- an opponent reply attacks that claim;
- a follow-up move defends against the attack;
- terminal facts such as mate, stalemate, promotion, or material conversion
  warrant or defeat the line;
- minimax is a scalar projection of a deeper attack/defense proof object.

The engine should make that proof object explicit. Search enters first as
"find refuting replies" and then as "find defenses to those replies," not as a
black-box alpha-beta loop bolted on after the fact.

## Current State

- `scripts/dialectical_chess_probe.py` is a PEP 723 script.
- The script depends on `chess>=1.11.0` and `z3-solver>=4.12`.
- It accepts a FEN through `--fen`.
- It accepts a PGN through `--pgn-in`, replays the mainline, chooses the next
  move, and writes an appended PGN through `--pgn-out` or `--pgn`.
- It can emit a simple AF JSON trace through `--emit-af`.
- It can print legal move probes through `--list-legal`.
- It speaks a minimal UCI protocol.
- It chooses through a root argument graph. Grounded acceptance and gradual
  ranking drive selection first; scalar chess scores are final tie-breaks.
- It supports bounded dialectical reply/defense expansion.
- It supports material negamax and alpha-beta search witnesses.
- It owns the runtime chess-state and legal-move substrate in
  `scripts/dialectical_chess_owned.py`; `python-chess` remains only for
  PGN/SAN/EPD parsing, display, and differential selftests.
- It uses Z3 by default for mate-in-one witnesses and exposes
  `--no-smt-mate` for comparison runs.
- It has an EPD/Lichess/perft/ablation/UCI-smoke benchmark runner in
  `scripts/dialectical_chess_bench.py`.

## Control Rules

- Keep the experiment sidecar until the completion criteria explicitly say it
  is ready for promotion.
- Use `uv run` for every Python command.
- Use PEP 723 inline metadata for prototype-only dependencies in scripts. Do
  not add prototype dependencies to `pyproject.toml`.
- Do not pin dependencies to local paths or local repositories.
- Commit every intentional source/report/config edit before starting the next
  edit slice.
- Generated PGNs, AF JSON traces, logs, and benchmark outputs are diagnostics;
  do not commit them unless the task explicitly asks for diagnostic artifacts.
- Every phase must have a direct smoke command and a correctness test plan.
- Legal move correctness is the first gate. Do not tune argumentation or search
  against illegal positions.
- Hard terminal facts outrank soft gradual/ranking semantics. Mate in one must
  never lose to a heuristic argument.
- Do not claim "SMT search" until a Z3-backed query actually contributes to
  move selection or proof generation.
- Do not claim "argumentation search" when the argument graph is only a
  post-hoc explanation of a scalar result.

## Architecture

### Chess Substrate

Current runtime substrate:

- `scripts/dialectical_chess_owned.py` for FEN, board state, legal moves,
  make/apply, check, checkmate/stalemate, castling, en passant, promotion, and
  perft.
- `python-chess` for PGN/SAN/EPD parsing, display notation, and differential
  correctness checks only.

Target owned substrate extensions:

- board representation, likely bitboards after a correctness-first mailbox
  version if needed;
- legal move generation;
- make/unmake;
- check/checkmate/stalemate;
- castling, en passant, promotion;
- repetition and fifty-move state;
- perft harness.

The owned substrate is a later milestone. The argumentation/search experiment
should not wait for bitboards.

### Argument Model

Use a layered representation:

- `MoveClaim`: candidate `play(move, state)`.
- `SupportArgument`: checkmate, check, capture, promotion, development, king
  safety, passed pawn, tactical motif.
- `ReplyAttack`: opponent move that attacks a move claim.
- `DefenseArgument`: our continuation that defeats a reply attack.
- `TerminalWarrant`: mate, draw, material threshold, promotion, or bounded
  evaluation dominance.
- `Preference`: hard ordering among warrants, e.g. checkmate defeats all
  non-terminal heuristics.

Framework mappings:

- Dung AF for minimal move/reply/defense attack graphs.
- ASPIC+ for structured chess rules and undercutters.
- ADF for acceptance conditions over all legal replies.
- Weighted AF for soft heuristic conflicts.
- Ranking/gradual semantics for non-forcing positions only.

### Search Model

Search is introduced through one bounded dialectical expansion mechanism:

1. At bound 0, evaluate legal moves from the current state.
2. At bound 1, for each candidate, enumerate opponent replies and construct
   attacks from replies that mate, win material, or erase the candidate's
   warrant.
3. At bound 2+, recursively search continuations that defend against reply
   attacks.

Only after these are correct should generic negamax/alpha-beta enter. When it
does, it should serve as a witness generator for attacks and defenses, not as a
replacement for the dialectical proof object.

### SMT Model

SMT is a bounded witness engine:

- mate-in-one and mate-in-two existence;
- piece attack constraints;
- fork/pin/skewer/discovered-attack witnesses;
- promotion-race constraints;
- counterexample generation for candidate moves.

The first Z3 queries should be small and falsifiable. Prefer:

```text
exists legal move m from state s such that checkmate(apply(s, m))
```

before attempting alternating quantified search. For alternation, use iterative
counterexample-guided calls:

1. propose candidate move;
2. ask for a refuting reply;
3. add the reply as an attack if found;
4. ask for a defending continuation;
5. add the continuation as a defense if found.

## Phases

### Phase 0: Sidecar Probe Baseline

Status: complete.

Tasks:

- Keep `scripts/dialectical_chess_probe.py` as the executable bootstrap.
- Support FEN input.
- Support PGN input and PGN output.
- Support AF JSON trace output.
- Support legal move listing.
- Select mate-in-one over every non-mating move.

Acceptance criteria:

- A mate-in-one FEN produces the mating move.
- A PGN whose final position is the same mate-in-one position gets the mating
  move appended.
- AF JSON contains move arguments, reason arguments, objection arguments, and a
  package-local ranking result.

Smoke command:

```powershell
uv run .\scripts\dialectical_chess_probe.py `
  --pgn-in .\scratch\dialectical_chess_input_smoke.pgn `
  --pgn-out .\scratch\dialectical_chess_input_smoke_next.pgn `
  --emit-af .\scratch\dialectical_chess_input_smoke_next.af.json `
  --list-legal `
  --choose
```

### Phase 1: UCI Shell

Goal: make the probe a real chess-engine process.

Status: complete.

Tasks:

- Add `--uci`.
- Implement UCI commands:
  - `uci`
  - `isready`
  - `ucinewgame`
  - `position startpos`
  - `position startpos moves ...`
  - `position fen <six-field fen>`
  - `position fen <six-field fen> moves ...`
  - `go`
  - `quit`
- Return `bestmove <uci>` from `go`.
- Ignore unsupported time controls honestly at first; do not crash on them.
- Keep the same one-ply chooser behind `go` until Phase 2.

Acceptance criteria:

- A UCI smoke transcript reaches `uciok`, `readyok`, and `bestmove`.
- `position fen 7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1` followed by `go`
  returns `bestmove a1a8`.
- Invalid UCI moves are rejected or reported without corrupting board state.

Tests:

- Unit-test command parsing without starting a subprocess.
- Subprocess smoke test can be manual at first, then automated once stable.

### Phase 2: Root Argument Graph API

Goal: make move selection genuinely argumentation-owned rather than only
score-sorted.

Status: complete.

Tasks:

- Introduce internal dataclasses for move claims, support arguments, objections,
  and defeat edges.
- Build a Dung AF from root candidate moves.
- Represent checkmate support as a hard attacker against all rival move claims.
- Represent "no immediate warrant" as a defeasible objection, not as a scalar
  only.
- Select through an argumentation result where possible, with scalar ordering
  only as a deterministic tie-break.

Acceptance criteria:

- The selected move can be traced to an accepted move claim.
- Mate-in-one is accepted and all rival move claims are defeated by the mate
  reason.
- AF JSON is a serialization of the internal graph, not rebuilt separately by a
  parallel code path.

Tests:

- Mate-in-one fixture.
- Non-terminal fixture where captures outrank quiet moves only through
  support/objection structure.
- Empty/no-legal-move fixture reports game-over state rather than crashing.

### Phase 3: Depth-2 Refutation Search

Goal: search begins as opponent attack generation.

Status: complete for the generic bounded-expansion path at reply bound 1.

Tasks:

- For each candidate move, apply it and enumerate opponent replies.
- Classify opponent replies:
  - reply checkmates;
  - reply wins material;
  - reply captures the moved piece;
  - reply neutralizes the candidate's check/threat.
- Add each classified reply as a `ReplyAttack` against the candidate move
  claim or its support reason.
- Penalize candidates with unanswered hard attacks.

Acceptance criteria:

- A move that allows immediate mate is rejected even if it gives check.
- A hanging queen capture is surfaced as an attacking reply.
- The emitted AF JSON shows candidate -> reply attack structure.

Tests:

- Fixture where a checking move blunders mate next move.
- Fixture where a quiet legal move avoids the mate.
- Generated tiny positions are optional here; start with curated tactical
  fixtures.

### Phase 4: Depth-3 Defense Search

Goal: extend the same bounded dialectical expansion to complete the first true
dialectical loop: claim, attack, defense.

Status: complete for recapture and immediate-mate defense witnesses under the
generic bounded-expansion path.

Tasks:

- For each `ReplyAttack`, enumerate our continuations.
- Classify continuations that:
  - mate;
  - recapture;
  - block/check-escape;
  - preserve or restore material threshold;
  - renew a stronger threat.
- Add `DefenseArgument` nodes that attack `ReplyAttack` nodes.
- Select moves whose hard reply attacks are defended.

Acceptance criteria:

- A candidate move with a refutation is accepted only if a searched defense
  defeats that refutation.
- The selected move includes at least one displayed claim/attack/defense line
  when the position is tactical.
- The engine can report unresolved attacks when depth is insufficient.

Tests:

- Mate-in-two fixture.
- Capture-recapture fixture.
- A deliberately unresolved fixture where the engine reports bounded
  uncertainty rather than overclaiming.

### Phase 5: Bounded Evaluation and Negamax Witnesses

Goal: add conventional bounded search as an argument witness source.

Status: complete for material evaluation, plain negamax witnesses, and an
alpha-beta backend that agrees on the mate smoke fixture.

Tasks:

- Add a material-only static evaluation.
- Add depth-limited negamax without alpha-beta first.
- Use negamax results to generate support/attack facts:
  - `line_evaluates_at_least(move, threshold)`;
  - `reply_refutes_below(move, threshold)`;
  - `continuation_restores(move, reply, threshold)`.
- Add alpha-beta only after the plain search has fixture coverage.

Acceptance criteria:

- Negamax output never bypasses terminal mate checks.
- Argument graph records the line/evaluation witness that influenced selection.
- Alpha-beta and plain negamax agree on selected move and score for small fixed
  depths.

Tests:

- Depth-1, depth-2, depth-3 comparison fixtures.
- Alpha-beta equivalence to plain negamax for small positions.
- Time-budget arguments are explicit when search is cut off.

### Phase 6: SMT Tactical Witnesses

Goal: introduce Z3 as a bounded tactic and counterexample engine.

Status: complete for default-on Z3 mate-in-one witnesses checked against
`python-chess` before becoming support arguments.

Tasks:

- Add a second PEP 723 script or optional path with `z3-solver`.
- Encode a tiny board-state relation for one tactical query first.
- Start with mate-in-one or piece-attack existence.
- Use SMT output to create support/attack arguments.
- Do not replace legal move generation with SMT until query correctness is
  pinned.

Acceptance criteria:

- At least one chosen move is supported by an SMT-produced witness.
- SMT mate witnesses are enabled by default in the sidecar script; comparison
  runs can disable them explicitly.
- SMT witnesses are checked against `python-chess` before becoming arguments.

Tests:

- SMT mate-in-one agrees with legal move generation on curated fixtures.
- Malformed/unavailable SMT path does not crash UCI or PGN mode.

### Phase 7: Benchmark Harness

Goal: measure what the engine actually does before optimizing or replacing the
substrate.

Status: complete for built-in smoke EPD, committed local EPD, user-provided
EPD, perft, Lichess-format CSV, ablation matrix, external UCI runner detection,
and internal UCI subprocess match smoke.

Control surface: `workstreams/dialectical-chess-benchmarks.md`.

Standard benchmark families:

- **Perft** for legal move generation correctness once an owned move generator
  exists.
- **Tactical EPD suites** such as Win at Chess (WAC), Encyclopedia of Chess
  Middlegames (ECM), Bratko-Kopec, BT2450/BT2630, and similar `bm`-annotated
  suites.
- **Strategic Test Suite (STS)** for long-term positional move choice.
- **Lichess puzzle database** for large-scale real-game tactical positions.
- **Engine matches** through UCI runners such as `cutechess-cli` or `fastchess`,
  with SPRT once the engine can complete games reliably.

Tasks:

- Add an EPD benchmark runner that reads `bm` best-move operations.
- Report solved count, total count, hit rate, elapsed time, and milliseconds per
  position.
- Record chosen move, expected best moves, SAN, UCI, and reason labels per
  position.
- Keep generated benchmark reports uncommitted unless explicitly promoted.
- Add UCI match guidance for `cutechess-cli` once time controls are handled.

Acceptance criteria:

- A built-in smoke EPD suite runs without external files.
- A user-provided EPD file can be scored.
- Benchmark output is JSON so later comparisons are scriptable.
- The report distinguishes tactical-suite score from match strength.

Tests:

- Built-in mate-in-one EPD gives 1/1.
- A deliberately wrong expected move gives 0/1.
- Runtime fields are present and numeric.

### Phase 8: Owned Chess Substrate

Goal: begin replacing `python-chess` as the engine's core state layer only
after the dialectical architecture is proven.

Status: complete for correctness-first owned move generation.
`scripts/dialectical_chess_owned.py` owns FEN parsing/serialization, legal move
generation, make/apply, attack detection, check, castling, en passant,
promotion, perft, and differential oracle checks.

Control surface: `workstreams/dialectical-chess-owned-movegen.md`.

Tasks:

- Add an owned FEN parser.
- Add owned pseudo-legal move generation.
- Add legality filtering by king safety.
- Add perft fixtures.
- Differential-test against `python-chess` until the owned layer is trusted.

Acceptance criteria:

- Standard perft positions match expected counts for shallow depths.
- Differential tests agree with `python-chess` on legal move sets for generated
  or curated positions.
- PGN/UCI modes can still use the stable bootstrap path while the owned
  substrate matures.

Tests:

- Perft depth 1-3 on standard fixtures.
- Special-move fixtures: castling, en passant, promotion, check evasions.
- Differential fixture suite against `python-chess`.

### Phase 9: Promotion Out of Scratch

Status: complete for sidecar relocation to `scripts/`. The engine is still not
promoted into `src/argumentation`.

Goal: decide whether this remains a sidecar experiment or becomes a package
surface.

Promotion criteria:

- UCI shell works.
- PGN-in/PGN-out works.
- EPD benchmark harness works.
- Depth-3 dialectical search works on fixtures.
- Argument graphs are the actual selection control surface.
- Generated diagnostics remain optional and uncommitted by default.
- Dependencies are optional and not local-path pinned.
- Documentation states the engine's limits plainly.

Possible target surfaces:

- `scripts/dialectical_chess_probe.py` while it remains an executable sidecar.
- separate sidecar package if it grows beyond example scope.
- `src/argumentation` only for reusable argumentation abstractions that are not
  chess-specific.

## Test And Verification Commands

Current smoke:

```powershell
uv run .\scripts\dialectical_chess_probe.py `
  --fen "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1" `
  --choose `
  --list-legal
```

PGN next-move smoke:

```powershell
uv run .\scripts\dialectical_chess_probe.py `
  --pgn-in .\scratch\dialectical_chess_input_smoke.pgn `
  --pgn-out .\scratch\dialectical_chess_input_smoke_next.pgn `
  --emit-af .\scratch\dialectical_chess_input_smoke_next.af.json `
  --choose
```

Future targeted tests:

```powershell
uv run pytest tests\test_dialectical_chess_probe.py -q
```

Full repo verification, only when the workstream touches package code:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- A UCI client can ask the engine for a move.
- A PGN can be replayed and extended with the engine's next move.
- Search has at least claim/attack/defense depth.
- The move-selection trace includes the argument graph that controlled the
  choice.
- Mate-in-one, mate-in-two, capture-refutation, and no-legal-move fixtures pass.
- Any SMT-backed result is independently checked against legal chess state.
- The workstream documentation says exactly which parts are implemented and
  which remain planned.

## Known Traps

- Treating `python-chess` as the final engine substrate too early. It is the
  bootstrap oracle, not necessarily the destination.
- Writing a bitboard engine before the argument/search idea is proven.
- Letting a scalar evaluation silently replace the argument graph.
- Calling a PGN annotation an engine before UCI works.
- Calling UCI support complete without handling `position ... moves ...`.
- Letting soft ranking choose a non-mating move over mate.
- Producing AF JSON as a decorative artifact that did not affect selection.
- Claiming SMT contributed when it only duplicates a Python legality check.
- Committing generated PGNs or AF traces as progress when the task did not ask
  to promote diagnostics.
