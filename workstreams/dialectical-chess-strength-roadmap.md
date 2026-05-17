# Dialectical Chess Strength Roadmap

## Goal

Turn the cleaned dialectical chess sidecar into an engine that can survive full
games and then start winning. The current full-game anchor is 0/10 against
Stockfish 18 configured as `UCI_Elo=1320`; all losses were by mate. The next
work is not generic evaluation tuning. It is making bad moves defeasible and
making refutations first-class arguments.

## Current Baseline

- Full-game Stockfish 1320 anchor:
  - `--match-games 10`
  - `--match-max-plies 400`
  - `--match-tc 30+0.2`
  - W/D/L from our side: 0/0/10
  - failures: 0 timeouts, 0 crashes, 0 losses-on-time
- Cleanup complete enough to work in named modules:
  - `arguments.py`
  - `probe.py`
  - `search.py`
  - `smt.py`
  - `uci.py`
  - `bench.py`
  - `matches.py`

## Workstream Order

Execute these in order:

1. `dialectical-chess-loss-mining.md`
2. `dialectical-chess-refutation-filtering.md`
3. `dialectical-chess-search-witnesses.md`
4. `dialectical-chess-king-safety-defeaters.md`
5. `dialectical-chess-quiescence.md`
6. `dialectical-chess-adf-acceptance.md`

The order matters. Loss mining creates concrete failing positions. Refutation
filtering is the first survival gate. Search witnesses make refutations and
defenses explainable. King safety adds chess-specific defeaters. Quiescence
stabilizes tactical leaf claims. ADF acceptance then replaces ad hoc survival
logic with acceptance conditions over reply sets.

## Global Rules

- Every strength change must have a before/after benchmark.
- Do not report Elo from capped adjudication smokes.
- Generated PGNs, JSON reports, AF dumps, and logs are diagnostics unless
  explicitly promoted.
- Keep Stockfish full-game runs separate from fast smokes.
- Search is not allowed to silently replace argumentation. Search must produce
  arguments, attacks, defenses, or acceptance facts.
- A move that allows immediate mate must lose unless every legal move also
  allows immediate mate.

## Global Smoke Commands

```powershell
uv run .\scripts\dialectical_chess_owned.py --selftest
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_smoke.epd
@('uci','isready','position fen 7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1','go','quit') | uv run .\scripts\dialectical_chess_probe.py --uci
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_cleanup.py
```

## Completion Criteria

- Loss-mined regression suite exists.
- Engine rejects known losing moves from the full-game losses.
- Full-game Stockfish 1320 result improves from 0/10 or loss lengths increase
  with an explicit no-regression explanation.
- Argument traces show the reason bad moves were defeated.
