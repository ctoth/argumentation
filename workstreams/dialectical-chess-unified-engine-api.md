# Dialectical Chess Unified Engine API Workstream

## Goal

Converge the chess sidecar around one reusable engine API. The CLIs should be
thin adapters. They should not each own fragments of engine behavior.

The target is a package-level engine surface:

```python
engine = DialecticalChessEngine(settings)
decision = engine.choose_move(board)
analysis = engine.analyze(board)
```

The engine owns move probing, argument construction, selection, search
witnesses, SMT witnesses, and trace assembly. UCI, benchmark, PGN, SVG, and
loss-mining code call the engine; they do not reimplement decision flow.

## Current Problem

Cleanup split the monolith into modules, but it did not yet create a single
engine control surface. Today the behavior is still distributed across:

- `probe.py` for move probes;
- `arguments.py` for selection;
- `search.py` and `smt.py` for tactical witnesses;
- `uci.py` for UCI move choice;
- `bench.py` for benchmark scoring;
- `adapters.py` for PGN/SVG bridges.

That is cleaner than the old scripts, but it is not yet a unified chess engine.

## Target Files

- `scripts/dialectical_chess/engine.py`
  - `EngineSettings`
  - `EngineDecision`
  - `EngineAnalysis`
  - `DialecticalChessEngine`
- Existing modules remain as implementation helpers:
  - `board.py`
  - `probe.py`
  - `arguments.py`
  - `search.py`
  - `smt.py`
  - `adapters.py`
  - `uci.py`
  - `bench.py`

## Rules

- Do not create another CLI.
- Do not duplicate selection logic in UCI or benchmark code.
- Delete old caller-side decision orchestration once `engine.py` exists.
- Keep PEP 723 entrypoints runnable with `uv run`.
- Preserve all current smoke behavior before doing strength work.
- Do not start refutation/king-safety/quiescence changes in this workstream.

## Phases

### Phase 0: Lock Current Behavior

Status: completed.

Commands:

```powershell
uv run .\scripts\dialectical_chess_owned.py --selftest
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_smoke.epd
@('uci','isready','position fen 7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1','go','quit') | uv run .\scripts\dialectical_chess_probe.py --uci
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_cleanup.py .\tests\test_dialectical_chess_loss_mining.py
```

Acceptance criteria:

- Current smoke behavior is recorded before engine API edits.

### Phase 1: Add Engine Data Model

Status: completed.

Tasks:

- Add `EngineSettings`.
- Add `EngineDecision`.
- Add `EngineAnalysis`.
- Keep data classes plain and serializable.

Acceptance criteria:

- Existing probe output can be represented by `EngineDecision`.
- Existing benchmark result fields can be populated from `EngineDecision`.

### Phase 2: Add `DialecticalChessEngine`

Status: completed.

Tasks:

- Implement `analyze(board) -> EngineAnalysis`.
- Implement `choose_move(board) -> EngineDecision`.
- Internally call:
  - `probe_moves`;
  - `build_root_argument_graph`;
  - `choose_move`.
- Include argument graph/ranking in analysis.

Acceptance criteria:

- Engine chooses `a1a8` in the mate smoke.
- Engine returns `0000` equivalent for no legal moves.

### Phase 3: Update UCI Adapter

Status: completed.

Tasks:

- Make `uci.py` construct and call `DialecticalChessEngine`.
- Remove UCI-local decision orchestration.
- Keep `info score cp ... pv ...` behavior.

Acceptance criteria:

- UCI smoke still emits `bestmove a1a8`.
- No selection logic remains in `uci.py` beyond adapter formatting.

### Phase 4: Update Benchmark Adapter

Status: completed.

Tasks:

- Make `bench.py` score positions through `DialecticalChessEngine`.
- Remove benchmark-local decision orchestration.
- Preserve JSON schema.

Acceptance criteria:

- EPD smoke remains `2/3` with the deliberate wrong fixture failing.
- Loss-mining CLI remains available.

### Phase 5: Update PGN/SVG/FEN Probe Adapter

Status: completed.

Tasks:

- Make `dialectical_chess_probe.py` call engine APIs for choose/list/trace.
- Keep PGN and SVG behavior in adapters.
- Remove caller-side graph construction from the script.

Acceptance criteria:

- FEN `--choose` smoke matches current JSON decision fields.
- PGN-out and SVG smoke still work.

### Phase 6: Tests

Status: completed.

Tasks:

- Add focused tests for:
  - engine mate selection;
  - no-legal-move decision;
  - benchmark adapter uses engine;
  - UCI adapter uses engine.

Acceptance criteria:

- Tests pass with `uv run --with chess --with z3-solver pytest`.

### Phase 7: Final Cleanup Gate

Status: completed.

Tasks:

- Search for duplicate calls to `build_root_argument_graph` and `choose_move`
  outside engine/tests.
- Keep only engine and tests constructing decisions directly.
- Run smokes.

Acceptance criteria:

- UCI, benchmark, probe, PGN/SVG, and loss mining are adapters over the engine.
- No strength behavior changed.
- Task-owned paths are clean after commit.

## Completion Criteria

- `DialecticalChessEngine` is the single move-decision API.
- All existing CLIs still work as thin adapters.
- Existing cleanup and loss-mining tests pass.
- Strength workstreams can target `engine.py`, `arguments.py`, `search.py`, and
  `smt.py` without chasing CLI-specific decision paths.
