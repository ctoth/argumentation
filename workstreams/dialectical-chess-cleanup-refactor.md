# Dialectical Chess Cleanup and Refactor Workstream

## Goal

Make the chess sidecar code clean enough to extend deliberately. This workstream
comes before new strength work. The next "win harder" phase should build on
named engine components, not keep adding behavior to monolithic scripts.

The target is still sidecar code under `scripts/`; this is not package
promotion. The target is a small script package with stable seams:

- owned chess substrate;
- move probe and argument construction;
- UCI engine loop;
- PGN/SVG/CLI presentation;
- benchmark suite parsing;
- external match runner and baselines.

## Current Problems

- `scripts/dialectical_chess_probe.py` mixes CLI parsing, PGN/SVG presentation,
  UCI protocol, owned-board adapters, SMT witnesses, search, move probing,
  argument graph construction, grounded/ranking semantics, and final selection.
- `scripts/dialectical_chess_bench.py` mixes benchmark CLI, EPD parsing,
  Lichess CSV scoring, perft execution, internal UCI process control, external
  fast-chess command construction, baseline definitions, and runner-output
  parsing.
- Hidden compatibility flags remain in the probe script even though owned
  movegen is now the only runtime substrate.
- Data flowing between phases is mostly raw dicts and `argparse.Namespace`
  values instead of named settings/results.
- The argumentation layer is present but not visually or mechanically separated
  from chess heuristics and search.
- Benchmarks can run, but the code shape makes it too easy to add another
  special case instead of improving the model.

## Non-Negotiable Rules

- Keep existing behavior during cleanup unless a phase explicitly deletes an
  obsolete path.
- Use deletion-first replacement for old surfaces: remove obsolete flags or
  helper families first, then fix literal failures.
- Do not start strength experiments until this workstream's completion criteria
  pass.
- Do not move the sidecar into `src/argumentation` in this workstream.
- Keep PEP 723 script entrypoints runnable with `uv run`.
- Every phase must end with the relevant smoke commands passing.
- Generated benchmark logs, PGNs, AF dumps, and `config.json` remain
  uncommitted diagnostics.

## Target Layout

Use a package directory under `scripts/` while keeping thin PEP 723 entrypoint
scripts for `uv run`:

```text
scripts/
  dialectical_chess_probe.py          # thin CLI/UCI entrypoint
  dialectical_chess_bench.py          # thin benchmark entrypoint
  dialectical_chess_random_uci.py     # thin weak-baseline entrypoint
  dialectical_chess/
    __init__.py
    board.py                         # OwnedBoard / OwnedMove / movegen / perft
    adapters.py                      # PGN, EPD, python-chess notation bridges
    probe.py                         # MoveProbe production
    arguments.py                     # RootArgumentGraph construction/selection
    search.py                        # bounded reply search, negamax, alpha-beta
    smt.py                           # Z3 mate witnesses
    uci.py                           # UCI loop and process helpers
    bench.py                         # suite runners and scoring
    matches.py                       # fast-chess/cutechess command/result logic
    baselines.py                     # random, no-SMT, Stockfish definitions
```

If this layout proves too granular during implementation, merge adjacent files
only when the merged file still has one responsibility.

## Ordered Phases

### Phase 0: Lock Current Behavior

Status: completed.

Goal: capture the current behavior before moving code.

Tasks:

- Run owned selftest.
- Run EPD smoke.
- Run UCI mate smoke.
- Run internal UCI smoke.
- Run external Stockfish command emission.

Acceptance criteria:

- All commands pass.
- The command outputs needed for comparison are summarized in the commit or
  workstream update, not committed as generated artifacts.

Commands:

```powershell
uv run .\scripts\dialectical_chess_owned.py --selftest
uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_smoke.epd
@('uci','isready','position fen 7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1','go','quit') | uv run .\scripts\dialectical_chess_probe.py --uci
uv run .\scripts\dialectical_chess_bench.py --internal-uci-match --match-games 2 --match-max-plies 6
uv run .\scripts\dialectical_chess_bench.py --uci-match-command --match-baseline stockfish --match-games 2 --match-max-plies 6 --match-tc 10+0.1
```

### Phase 1: Create the Script Package Shell

Status: completed.

Goal: make imports explicit without changing behavior.

Tasks:

- Add `scripts/dialectical_chess/__init__.py`.
- Move no behavior yet.
- Add an import smoke that proves the package can be loaded by scripts.

Acceptance criteria:

- Existing entrypoints still run.
- No circular import debt is introduced.

### Phase 2: Move Owned Board Into `board.py`

Status: completed.

Goal: make the owned chess substrate the named foundation.

Tasks:

- Move `OwnedMove`, `OwnedBoard`, square helpers, attack detection, legal
  movegen, apply, perft, divide, and oracle selftest code into
  `scripts/dialectical_chess/board.py`.
- Keep `scripts/dialectical_chess_owned.py` as a thin PEP 723 CLI wrapper.
- Delete importlib loading of owned code from the probe; import the package
  module directly.

Acceptance criteria:

- Owned selftest passes.
- Probe and benchmark scripts no longer dynamically load
  `dialectical_chess_owned.py`.
- The wrapper contains CLI only.

### Phase 3: Extract Probe Data and Argument Selection

Status: completed.

Goal: separate "what moves mean" from "how the CLI is invoked."

Tasks:

- Move `MoveProbe`, `RootArgumentGraph`, support/reply/defense labels,
  argument payload construction, grounded extension, gradual ranking, and
  `selection_key` into `arguments.py`.
- Move `probe_moves` and owned capture/terminal helpers into `probe.py`.
- Keep selection explicitly argument-first: grounded/ranking/support/defense,
  then scalar fallback.
- Delete hidden `--owned-movegen` and `--allow-owned-divergence` flags from the
  probe entrypoint.

Acceptance criteria:

- EPD smoke still reports `movegen: owned`.
- UCI mate smoke still emits `info score cp ... pv ...` and `bestmove a1a8`.
- No production code path can select a `python-chess` legal move oracle.

### Phase 4: Extract Search and SMT

Status: completed.

Goal: make tactical witnesses explicit and replaceable.

Tasks:

- Move Z3 mate-in-one logic into `smt.py`.
- Move `SearchResult`, static evaluation, negamax, alpha-beta, bounded reply
  attacks, and defense checks into `search.py`.
- Define named settings dataclasses for dialectic depth, search depth,
  backend, and SMT enablement.

Acceptance criteria:

- `--no-smt-mate` still removes SMT witnesses.
- `--search-backend negamax` and `--search-backend alphabeta` still work.
- Ablation runner still runs without changing output schema.

### Phase 5: Extract UCI and Presentation

Status: completed.

Goal: make the engine loop and file-format presentation thin and boring.

Tasks:

- Move UCI parsing, `position` handling, `go`, `stop`, and UCI output into
  `uci.py`.
- Move PGN load/build and SVG output bridges into `adapters.py`.
- Keep `dialectical_chess_probe.py` as argument parsing plus calls into package
  functions.

Acceptance criteria:

- UCI mate smoke passes.
- PGN-in to PGN-out still appends the selected move.
- SVG output still renders the final board.

### Phase 6: Extract Benchmarks and Match Runners

Status: completed.

Goal: make benchmark scoring and match orchestration separately testable.

Tasks:

- Move EPD parsing, Lichess CSV scoring, and perft benchmark wrappers into
  `bench.py`.
- Move UCI subprocess helpers and fast-chess/cutechess command building into
  `matches.py`.
- Move baseline definitions into `baselines.py`.
- Replace ad hoc dict construction with named result/settings dataclasses
  where it reduces ambiguity.

Acceptance criteria:

- EPD smoke passes.
- Internal UCI match passes.
- Stockfish command emission includes `UCI_LimitStrength=true` and
  `UCI_Elo=1320`.
- External match output still marks timeouts/crashes/losses-on-time as
  `ok: false`.

### Phase 7: Add Focused Tests Where Scripts Are Too Coarse

Status: completed.

Goal: stop relying only on full script smoke tests for refactor safety.

Tasks:

- Add targeted tests for:
  - UCI position parsing;
  - EPD `bm`/`am` parsing;
  - Stockfish baseline command construction;
  - argument selection key ordering;
  - no legal moves returns `bestmove 0000`.
- Keep full script smokes as integration tests.

Acceptance criteria:

- `uv run pytest` targeted tests pass.
- Full script smoke commands from Phase 0 pass.

### Phase 8: Final Cleanup Gate

Status: completed.

Goal: make the codebase ready for the next strength phase.

Tasks:

- Remove obsolete compatibility flags and dead imports.
- Confirm no dynamic import remains except where intentionally needed for
  script execution.
- Confirm `python-chess` appears only in PGN/SAN/EPD adapters, benchmark
  parsing, random baseline legality, and differential tests.
- Update workstream docs with the final module map.

Acceptance criteria:

- Phase 0 commands pass.
- External two-game Stockfish smoke passes with no warnings/timeouts/crashes.
- `rg -F "--owned-movegen" scripts workstreams` has no live command surface
  except historical notes if intentionally retained.
- The next workstream can refer to `arguments.py`, `search.py`, and `smt.py`
  directly when adding defeasible machinery.

## Strength Work Is Explicitly Deferred

Do not start these until the cleanup gate passes:

- richer defeasible rules for tactical motifs;
- ADF acceptance over all legal replies;
- argument-backed move ordering;
- SMT beyond mate-in-one;
- learned or tuned preference weights;
- deeper Stockfish/random baseline matches for rating claims.

The cleanup is not cosmetic. It is the prerequisite for making the next
argumentation changes observable, testable, and reversible.

## Completed Module Map

Workflow used: cleanup/refactor workstream in this document.

- `dialectical_chess_probe.py`: thin PEP 723 probe entrypoint for CLI output,
  PGN/SVG writes, AF emission, and UCI delegation.
- `dialectical_chess_bench.py`: thin PEP 723 benchmark entrypoint.
- `dialectical_chess_owned.py`: thin PEP 723 owned-board entrypoint.
- `dialectical_chess/board.py`: owned board, legal move generation, perft,
  divide, and oracle selftest diagnostics.
- `dialectical_chess/arguments.py`: `MoveProbe`, `RootArgumentGraph`, argument
  payloads, grounded/ranking calls, and argument-first move selection.
- `dialectical_chess/probe.py`: move probing and named probe settings.
- `dialectical_chess/search.py`: static evaluation, negamax, alpha-beta,
  bounded reply attacks, defense checks, and search settings.
- `dialectical_chess/smt.py`: Z3 mate-in-one witnesses and SMT settings.
- `dialectical_chess/uci.py`: UCI command loop, position parsing, and bestmove
  output.
- `dialectical_chess/adapters.py`: PGN, SVG, and python-chess presentation
  bridges.
- `dialectical_chess/bench.py`: EPD, Lichess CSV, perft, ablation, and scoring
  runners.
- `dialectical_chess/matches.py`: internal UCI games and external
  fast-chess/cutechess orchestration.
- `dialectical_chess/baselines.py`: no-SMT, random, and Stockfish baseline
  command definitions.
- `tests/test_dialectical_chess_cleanup.py`: focused cleanup safety tests.

Verification recorded during completion:

- `uv run .\scripts\dialectical_chess_owned.py --selftest`: passed.
- `uv run .\scripts\dialectical_chess_bench.py --perft`: passed, 9/9.
- `uv run .\scripts\dialectical_chess_bench.py --epd .\scripts\dialectical_chess_smoke.epd`:
  passed, 2/3 with the deliberate wrong fixture failing.
- UCI mate smoke: passed, emitted `info score cp 2001000 pv a1a8` and
  `bestmove a1a8`.
- `uv run .\scripts\dialectical_chess_probe.py --choose --no-smt-mate`:
  passed and removed the SMT witness.
- `uv run .\scripts\dialectical_chess_probe.py --choose --search-depth 1 --search-backend alphabeta`:
  passed.
- `uv run .\scripts\dialectical_chess_bench.py --ablation`: passed on the
  built-in smoke suite.
- PGN/SVG output smoke: passed.
- `uv run .\scripts\dialectical_chess_bench.py --internal-uci-match --match-games 2 --match-max-plies 6`:
  passed with 0 crashes and 0 illegal moves.
- `uv run .\scripts\dialectical_chess_bench.py --uci-match-command --match-baseline stockfish --match-games 2 --match-max-plies 6 --match-tc 10+0.1`:
  passed and includes `UCI_LimitStrength=true` and `UCI_Elo=1320`.
- `uv run .\scripts\dialectical_chess_bench.py --run-uci-match --match-baseline stockfish --match-games 2 --match-max-plies 6 --match-tc 10+0.1`:
  passed with 0 timeouts, 0 crashes, and 0 losses on time.
- `uv run pytest .\tests\test_dialectical_chess_cleanup.py`: passed with
  dependency-specific tests skipped when PEP 723 dependencies are not installed
  in the project environment.
- `uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_cleanup.py`:
  passed, 5/5.
