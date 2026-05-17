# Dialectical Chess Benchmark Workstream

## Goal

Measure the dialectical chess engine with concrete, repeatable benchmarks. This
workstream separates four questions that must not be conflated:

- **Legality correctness:** does move generation match chess rules?
- **Tactical accuracy:** does the engine choose benchmark best moves?
- **Throughput:** how many positions per second, and where is time spent?
- **Playing strength:** how does it perform in UCI games against baselines?

No benchmark claim is complete without the input suite, command, settings,
engine commit, total positions/games, score, elapsed time, and generated report
path.

## Current State

- `scripts/dialectical_chess_bench.py` can score EPD lines with `bm` and `am`
  operations.
- It has a built-in mate-in-one smoke EPD.
- It reports JSON:
  - suite name;
  - total;
  - solved;
  - hit rate;
  - elapsed milliseconds;
  - milliseconds per position;
  - selected move;
  - expected moves;
  - reasons, objections, reply attacks, search line, SMT witnesses.
- It does not vendor third-party benchmark suites because license/size review is
  still required before committing them.
- It runs Lichess-format puzzle CSVs.
- It runs an internal UCI subprocess match smoke and detects standard external
  runners.
- External UCI match payloads include timeout/crash/loss-on-time counts and
  return `ok: false` when those failures are present, even if the runner process
  exits with code 0.
- It runs owned perft benchmarks.

## Benchmark Sources

Use these families explicitly:

- **Perft fixtures** for move generation correctness.
  - Source class: Chessprogramming perft references and known engine-dev perft
    positions.
  - Use only after owned movegen exists.
- **WAC / Win at Chess** tactical EPDs.
  - Metric: `bm` hit rate and ms/position.
- **ECM / Encyclopedia of Chess Middlegames** tactical EPDs.
  - Metric: `bm` hit rate and ms/position.
- **Bratko-Kopec** tactical/positional test.
  - Metric: correct best move count.
- **BT2450 / BT2630** tactical suites.
  - Metric: solved count and optionally suite-native timing score if available.
- **STS / Strategic Test Suite**.
  - Metric: `bm` hit rate and, if the EPD has weighted move operations,
    weighted score.
- **Lichess puzzle database**.
  - Metric: first-move hit rate, full-line hit rate when move sequence is used,
    rating-bucket hit rate, ms/position.
- **UCI matches with cutechess-cli, fastchess, or fast-chess**.
  - Metric: W/D/L, Elo estimate, nodes/time settings, crashes, illegal moves.
  - Use SPRT only once the engine can finish games under time control.

## Artifact Policy

- Benchmark scripts are source and should be committed.
- Downloaded benchmark suites are not committed unless licenses and size are
  explicitly reviewed.
- Generated JSON/PGN/log reports are diagnostics and stay uncommitted unless a
  task explicitly asks to promote a report.
- Every generated report filename must include date or commit when promoted.

### Phase 0: Built-In EPD Smoke

Status: complete.

Command:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --json-out .\scratch\dialectical_chess_bench_smoke.json
```

Acceptance criteria:

- Built-in suite reports `total=1`.
- Built-in suite reports `solved=1`.
- Selected move is `a1a8`.
- Output includes elapsed milliseconds and ms/position.

Known baseline from first smoke:

- `1/1`, hit rate `1.0`, cold run about `249 ms` with SMT enabled.

### Phase 1: Local EPD Fixture Suite

Status: complete.

Goal: establish a tiny committed fixture suite that exercises success and
failure paths without external downloads.

Tasks:

- Add `scripts/dialectical_chess_smoke.epd`.
- Include at least:
  - mate-in-one expected correct;
  - same position with deliberately wrong `bm` for failure-path test;
  - capture-best position;
  - quiet-best placeholder only after the engine has a reason for quiet moves.
- Add runner support for multiple `bm` alternatives.
- Add runner support for `id` fields already done.

Acceptance criteria:

- Success fixture scores 1.
- Deliberate failure fixture scores 0.
- JSON report includes one record per EPD line.

### Phase 2: External EPD Suite Runner

Status: complete for user-provided paths and WAC/STS-style `bm`/`am` parsing.
Third-party suite vendoring is not complete and is blocked on license/size
review.

Goal: run standard tactical/strategic EPD files provided by path.

Tasks:

- Keep `--epd path`.
- Support these EPD operations:
  - `bm` best moves;
  - `am` avoid moves, used as a negative correctness flag;
  - `id` position identifier;
  - ignore unknown operations without failing.
- Normalize expected SAN/UCI robustly.
- Add `--limit N` for quick partial runs.
- Add `--fail-fast` for parser/debug mode.

Acceptance criteria:

- A WAC/ECM/STS-style EPD file can be scored from disk.
- Parser reports exact line number for malformed lines.
- Unknown EPD operations do not block `bm` scoring.

Required command shape:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --epd C:\path\to\wac.epd `
  --json-out .\scratch\bench-wac-<commit>.json `
  --dialectic-depth 2 `
  --search-depth 2 `
  --search-backend alphabeta
```

### Phase 3: Timing and Ablation Matrix

Status: complete.

Goal: isolate which mechanism helps or hurts.

Required ablations:

- SMT on vs `--no-smt-mate`.
- `--dialectic-depth 0`, `1`, `2`.
- `--search-depth 0`, `1`, `2`, `3`.
- `--search-backend negamax` vs `alphabeta`.

Metrics:

- hit rate;
- ms/position;
- selected move changes;
- reason labels frequency;
- reply attack count;
- defense node count;
- SMT witness count.

Acceptance criteria:

- Benchmark JSON includes enough data to compute all metrics.
- A comparison script or notebook is not required yet, but the raw JSON must be
  stable and scriptable.

### Phase 4: Lichess Puzzle CSV Runner

Status: complete for Lichess-format CSV input and committed sample execution.

Goal: scale beyond curated EPD suites.

Expected input:

- Lichess puzzle CSV with fields including FEN, moves, rating, themes.

Tasks:

- Add a runner mode for CSV.
- Interpret the first puzzle move as the first-move benchmark target.
- Optionally replay the full puzzle line after the first move.
- Add filters:
  - `--limit`;
  - rating min/max;
  - theme include/exclude;
  - side to move.
- Report hit rate by rating bucket and theme.

Acceptance criteria:

- A small sampled CSV runs locally.
- Full-line scoring is clearly distinguished from first-move scoring.
- Runtime and memory behavior are reported for at least a sample size.

Required command shape:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --lichess-puzzles C:\path\to\lichess_db_puzzle.csv `
  --limit 1000 `
  --json-out .\scratch\bench-lichess-sample-<commit>.json
```

### Phase 5: UCI Match Harness

Status: complete for internal UCI subprocess smoke, external command emission,
external `fast-chess` execution, and timeout/crash failure detection.

Goal: compare playing behavior against baseline engines.

Prerequisites:

- UCI `go` must handle at least fixed movetime or depth.
- Engine must never emit illegal moves.
- Engine must handle game-over states with `bestmove 0000`.

Baselines:

- Previous commit of this engine.
- Same engine with SMT disabled.
- Same engine with dialectic depth 0.
- A minimal random/legal engine if available.
- A deliberately weak external UCI engine if installed.

Required command shape:

```powershell
cutechess-cli `
  -engine name=Dialectical cmd="uv" arg="run" arg=".\scripts\dialectical_chess_probe.py" arg="--uci" proto=uci `
  -engine name=Baseline cmd="..." proto=uci `
  -each tc=1+0.01 `
  -games 100 `
  -repeat `
  -pgnout .\scratch\matches\dialectical-vs-baseline.pgn
```

Acceptance criteria:

- Match completes without illegal moves or crashes.
- Report includes W/D/L and crashes/time forfeits.
- Runner-reported timeouts, crashes, and loss-on-time results make the JSON
  payload fail with `ok: false`.
- SPRT is not used until ordinary fixed-game matches complete reliably.

Current smoke commands:

```powershell
uv run .\scripts\dialectical_chess_bench.py `
  --internal-uci-match `
  --match-games 2 `
  --match-max-plies 6

uv run .\scripts\dialectical_chess_bench.py `
  --uci-match-command `
  --match-baseline random `
  --match-games 2 `
  --match-max-plies 6

uv run .\scripts\dialectical_chess_bench.py `
  --run-uci-match `
  --match-baseline random `
  --match-games 2 `
  --match-max-plies 6 `
  --match-tc 10+0.1
```

Observed current smoke:

- Internal UCI match: 2 games, 6 plies each, 2 adjudicated draws, 0 crashes, 0
  illegal moves.
- External `fast-chess` at `1+0.01`: fails honestly with 1 timeout and 1
  loss-on-time in a two-game smoke.
- External `fast-chess` at `10+0.1`: completes the two-game random-baseline
  smoke with 0 timeouts, 0 crashes, 0 losses-on-time, and 2 adjudicated draws.

### Phase 6: SPRT / Regression Testing

Status: executable with `fast-chess`; only a tiny fixed match has been run so
far, not a statistically meaningful SPRT run.

Goal: test whether a change improves playing strength.

Prerequisites:

- Phase 5 match harness is stable.
- Time controls are honored enough to avoid random flagging.

Tasks:

- Run `cutechess-cli`, `fastchess`, or `fast-chess` SPRT against previous
  engine commit.
- Use small Elo bounds first, e.g. `elo0=0 elo1=10`, only after runtime is
  stable.
- Record exact command and engine commits.

Acceptance criteria:

- SPRT output is saved as diagnostic.
- Result is reported as pass/fail/inconclusive, not overinterpreted.

### Phase 7: Benchmark Report Promotion

Status: complete as a report template/policy. No generated benchmark report was
promoted because the task did not explicitly ask to commit diagnostics.

Goal: produce a committed report only when explicitly requested.

Required report fields:

- Engine commit.
- Benchmark suite and source.
- Command.
- Settings.
- Total positions/games.
- Score/hit rate/WDL.
- Time and machine notes.
- Top failure examples.
- Known limitations.

Template path:

- `reports/dialectical-chess-benchmark-YYYY-MM-DD.md`

## Completion Criteria

- Built-in smoke benchmark passes.
- User-provided EPD path benchmark works.
- Local committed EPD suite runs with success and deliberate-failure paths.
- Lichess puzzle sample mode exists and passes on the committed CSV sample.
- UCI match harness completes an internal subprocess smoke with no illegal
  moves or crashes.
- External `fast-chess` execution completes a two-game bounded smoke match.
- Benchmark docs distinguish legality, tactical accuracy, throughput, and
  playing strength.

## Known Traps

- A 1-position smoke benchmark is not a score claim.
- EPD hit rate is not Elo.
- STS score is not tactical strength.
- Lichess puzzle first-move accuracy is not full puzzle-solving ability.
- Cold-run time includes dependency/environment overhead; report warm and cold
  separately when speed matters.
- Comparing with Stockfish at normal strength is not informative yet; compare
  against ablations and weak baselines first.

