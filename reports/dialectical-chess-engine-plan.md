# Dialectical Chess Engine Plan

## Intent

Build a real chess engine from this repository's argumentation machinery, accepting that it will not be Stockfish-fast and not treating existing engines as the design target. The point is to see whether chess search can be represented as adversarial argument construction: a move asserts a claim about a position, replies attack that claim, continuations defend it, and bounded search becomes dialectical proof.

This should live outside the package core while it is experimental. The core `argumentation` library stays a formal argumentation kernel; the chess engine can be a script, scratch package, or sidecar repo that imports it.

## Core Thesis

Chess already has the shape of an argument game:

- Proponent: side to move, asserting "this move is good."
- Opponent: replying side, attacking the move claim.
- Defense: follow-up moves that answer the attack.
- Terminal warrant: mate, stalemate, repetition/draw, material conversion, promotion, or bounded evaluation dominance.
- Defeaters: tactics, legal refutations, insufficient defense, rule constraints, and stronger alternative plans.

Minimax can be viewed as a special case of this dialectic: a move survives only if every opponent attack can be answered well enough. Argumentation lets us make the proof object explicit instead of collapsing everything into one scalar.

## Engine Shape

### 1. Chess State Layer

We need our own engine substrate, even if the first version is simple:

- Board representation: probably bitboards, but a mailbox board is acceptable for the first correctness pass.
- FEN parser and serializer.
- Legal move generation.
- Make/unmake move.
- Check, checkmate, stalemate, castling, en passant, promotion.
- Repetition and fifty-move bookkeeping eventually.
- Perft tests for legal move correctness.
- PGN output for smoke games and optional SVG rendering for debugging positions.

The first implementation can start with a clear Python board model before optimizing to bitboards. Correctness matters more than speed at this stage.

### 2. Bounded Game-Tree Layer

Represent bounded tactical search explicitly:

- `State`: board, side to move, castling rights, ep square, clocks.
- `Move`: legal transition from one state to another.
- `Line`: alternating sequence of moves.
- `OutcomeClaim`: mate, draw, material delta, king safety, promotion, passed pawn, etc.
- `Bound`: search depth, quiescence budget, or tactical motif budget.

The engine should answer bounded questions first:

- Is there a legal move that mates in `n`?
- Is there a legal move such that every reply allows material recovery?
- Is there a legal move that cannot be refuted within depth `d`?
- Which candidate has the strongest surviving dialectical line?

### 3. SMT Layer

SMT should model bounded existence/refutation, not the whole infinite game:

- Encode piece occupancy, side to move, and legal transition constraints for a bounded horizon.
- Query existence of tactical witnesses: forks, pins, discovered attacks, forced mate patterns, promotion races.
- Use iterative calls for alternation rather than pretending Z3 directly gives a cheap full-game QBF solver.

Useful query forms:

```text
exists move m:
  legal(s0, m, s1)
  and checkmate(s1)
```

```text
exists move m:
  legal(s0, m, s1)
  and for every legal reply r from s1:
    exists continuation c:
      legal(reply_state, c, s3)
      and material_gain(s3) >= threshold
```

In practice, the second form becomes counterexample-guided search:

1. Propose a move.
2. Ask for a refuting reply.
3. If a refutation exists, add an attacking argument.
4. If a defense exists, add a defending argument.
5. Repeat until depth/budget closes.

### 4. Argumentation Layer

Map search artifacts into formal argumentation:

- Move arguments: `play(move, state)`.
- Tactical support: `supports(fork, move)`, `supports(mate_threat, move)`.
- Refutation attacks: `reply_attacks(reply, move_claim)`.
- Defense attacks: `counter_reply_defends(counter, reply_attack)`.
- Preference rules: checkmate outranks material, legal refutation outranks heuristic development, forced draw may outrank losing continuation.
- Weighted attacks: shallow heuristics are cheap to defeat; hard legal tactics are expensive or absolute.

Candidate mappings:

- Dung AF: minimal move/reply/defense attack graph.
- ASPIC+: structured rules for chess concepts and undercutters for tactical exceptions.
- ABA: assumptions such as "the attacked piece cannot be defended" or "the opponent must recapture."
- ADF: acceptance of a move depends on an acceptance condition over all replies.
- Weighted AF: allow heuristic conflicts and rank cheapest refutations.
- Ranking/gradual semantics: order non-forcing candidates.

### 5. Selection Layer

A candidate move is acceptable if it survives the current dialectical burden:

- For forced tactics, use hard terminal predicates first.
- For all legal replies, require either no refutation or an accepted defense.
- For non-forcing positions, rank by accepted support strength minus surviving attacks.
- Tie-break by engine values: material, king safety, activity, pawn structure, space, initiative.

The engine can expose:

- `bestmove`: UCI-compatible move string.
- PGN-in to next-move PGN-out for quick analysis loops.
- `claim`: the accepted top-level move argument.
- `attackers`: strongest refutations considered.
- `defenses`: continuations that answer the refutations.
- `status`: proven mate, bounded-safe, heuristic, unresolved, or refuted.

## What We Need

### Source Components

- `scratch/dialectical_chess_probe.py`: standalone PEP 723 script for FEN rendering and early experiments.
- Later: `scratch/dialectical_chess/board.py` for the board model.
- Later: `scratch/dialectical_chess/movegen.py` for legal move generation.
- Later: `scratch/dialectical_chess/search.py` for bounded dialectical search.
- Later: `scratch/dialectical_chess/smt.py` for Z3 encodings.
- Later: `scratch/dialectical_chess/arguments.py` for AF/ASPIC/ADF construction.
- Later: `scratch/dialectical_chess/uci.py` for a basic UCI loop.

### Dependencies

Prototype-only dependencies can live in PEP 723 inline script metadata:

- `chess`: FEN parsing, legal move sanity checks, PGN writing, and optional SVG board rendering while we build our own board.
- `z3-solver`: bounded tactical constraints.

The package itself should not add these dependencies until the experiment proves useful.

### Test Assets

- FEN corpus for smoke tests.
- Perft positions and expected node counts.
- Mate-in-1, mate-in-2, and simple tactic suites.
- PGN traces for selected moves.
- JSON traces of dialectical proof graphs.

## First Concrete Milestone

Milestone 0 should not try to be clever:

1. Accept a supplied FEN and emit a one-move PGN for the selected move.
2. Accept a supplied PGN, replay the mainline to the final position, and emit a PGN with the selected next move appended.
3. List legal moves from the position.
4. Create one top-level argument per legal move.
5. Add hard attacks for illegal moves only if using generated pseudo-legal moves.
6. Add simple support/attack arguments for checks, captures, and checkmates.
7. Select checkmate immediately, otherwise rank captures/checks/development with a simple argument score.

This is enough to prove that chess positions can flow into argument graphs and back into a move choice.

## Example FEN

Use a mate-in-one smoke position:

```text
7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1
```

White to move has `Ra8#` available. The first engine should produce a hard accepted argument for `Ra8` because it is legal and immediately checkmates.

## Falsifiers

- If legal move generation is wrong, stop and fix it before touching argumentation.
- If mate-in-one is not always selected over heuristic moves, the hard tactical layer is wrong.
- If constructing the root argument graph takes longer than shallow search on simple positions, the graph surface is too broad.
- If SMT encodings become more complicated than ordinary search for shallow tactics, restrict SMT to motif detection and counterexample generation.
- If argumentation only reproduces a scalar evaluation without proof objects, the design is not using the repo's real strength.

## Near-Term CLI Shape

```powershell
uv run scratch/dialectical_chess_probe.py `
  --fen "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1" `
  --pgn scratch/dialectical_chess_mate_in_one.pgn `
  --list-legal
```

Later:

```powershell
uv run scratch/dialectical_chess_probe.py `
  --pgn-in scratch/input_game.pgn `
  --pgn-out scratch/input_game_next.pgn `
  --choose `
  --emit-af scratch/input_game_next.af.json
```

Also useful:

```powershell
uv run scratch/dialectical_chess_probe.py `
  --fen "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1" `
  --choose `
  --emit-af scratch/dialectical_chess_mate_in_one.af.json
```
