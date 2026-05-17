# Dialectical Chess Reply Cache and Runtime Workstream

## Goal

Make dialectical reply analysis fast enough to run real Lichess samples without
losing the structured argument evidence that makes this engine interesting.

## Observed Baseline

- A 100-puzzle real Lichess run at `dialectic_depth=2` became pathologically
  slow.
- A 30-second `py-spy` speedscope sample of the active run showed:
  - `bounded_reply_attacks`: about `28.7/30s` inclusive;
  - `has_bounded_defense`: about `27.2/30s` inclusive;
  - repeated `legal_moves`, `owned_is_checkmate`, `in_check`, and king/square
    helpers dominate below that.

This is chess-side reply expansion and owned-board recomputation, not a generic
argumentation-framework bottleneck.

## Non-Negotiables

- Stay on the current branch.
- Keep diagnostic CSV/JSON/log/profile artifacts uncommitted.
- Do not delete structured reply evidence.
- If reply evidence is bounded or truncated, expose that explicitly in the
  argument trace.
- Keep UCI legality and benchmark JSON valid.

## Phases

### Phase 0: Control Surface

Status: complete.

Tasks:

- Add an explicit reply-analysis settings object.
- Thread it through probe and engine settings.
- Expose benchmark CLI knobs for reply budgets.

Acceptance criteria:

- Defaults preserve existing behavior for small positions.
- Settings serialize plainly.

Result:

- Added `ReplyAnalysisSettings(max_replies=128, max_defense_nodes=5000,
  min_defense_material=300)`.
- Threaded through `EngineSettings`, probe settings, UCI, benchmark JSON, and
  the PEP 723 probe script.
- Benchmark CLI knobs:
  - `--reply-max-replies`;
  - `--reply-max-defense-nodes`;
  - `--reply-min-defense-material`.

### Phase 1: Memoized Board Operations

Status: complete.

Tasks:

- Add a per-engine/per-analysis cache for owned-board legal moves,
  terminal/checkmate/stalemate, and child application.
- Keep cache lifetime local to one analysis/match decision so there is no stale
  state across game moves.
- Key cache entries by the immutable owned-board object and UCI move text.

Acceptance criteria:

- Repeated `owned_is_checkmate` and `legal_moves` checks reuse cached values
  inside one decision.
- A new engine decision gets a fresh cache.

Result:

- Added `ReplyAnalysisCache` for per-analysis legal moves, applied child boards,
  checkmate checks, defense-node counts, and truncation reasons.
- Cache is created in `probe_moves_with_settings`, so it is local to one engine
  decision and cannot go stale across game moves.
- Cache keys use immutable owned-board values plus UCI move text.

### Phase 2: Tactical Reply Filtering

Status: complete.

Tasks:

- Run expensive defense checks only for replies that matter:
  - reply mate;
  - reply captures the moved piece;
  - reply captures material at or above a threshold;
  - reply gives check.
- Keep non-relevant replies out of the defense recursion.

Acceptance criteria:

- Existing mate/capture reply labels remain.
- Quiet irrelevant replies do not call bounded defense.

Result:

- Defense recursion now runs only for reply mate, moved-piece captures,
  material captures at/above the threshold, and checking replies.
- Depth-1 defense no longer expands full child trees.
- Material recapture defense uses `OwnedBoard.is_square_attacked` instead of
  generating full legal moves for every candidate.
- Checkmate testing now checks `in_check` before generating legal moves.

### Phase 3: Explicit Budgets

Status: complete.

Tasks:

- Add maximum reply and defense-node budgets.
- Add explicit `reply_analysis:truncated:*` trace labels when budgets are hit.
- Keep result deterministic by preserving sorted move order.

Acceptance criteria:

- A low budget produces a truncation trace.
- Default budget is high enough for current smoke tests.

Result:

- Reply and defense-node budgets are implemented.
- Truncation emits explicit labels such as
  `reply_analysis:truncated:reply_budget`.
- Smoke tests pass under defaults.

### Phase 4: Progress and Profiling Loop

Status: complete.

Tasks:

- Keep benchmark progress reporting on stderr.
- Rerun the real Lichess 1200-1600 sample with `dialectic_depth=2`.
- Profile again if runtime remains suspicious.

Acceptance criteria:

- Real-data run emits progress.
- Runtime is bounded and materially faster than the aborted no-cache/no-budget
  run.
- Hot frames no longer show nearly all time in unbounded reply defense.

Result:

- Real-data input: `scratch\lichess_db_puzzle.csv`, downloaded from the official
  Lichess puzzle database archive.
- Baseline failure mode: the old `dialectic_depth=2`, 100-puzzle run was
  aborted after running for many minutes without progress output.
- First profile of the old path:
  - `bounded_reply_attacks`: about `28.7/30s` inclusive;
  - `has_bounded_defense`: about `27.2/30s` inclusive.
- Latest real 100-puzzle command:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py `
  --lichess-puzzles .\scratch\lichess_db_puzzle.csv `
  --rating-min 1200 `
  --rating-max 1600 `
  --limit 100 `
  --selector-mode argument `
  --dialectic-depth 2 `
  --progress-every 10 `
  --json-out .\scratch\lichess_1200_1600_argument_d2_fast3.json
```

- Latest result: `100` puzzles, `17` solved, hit-rate `0.17`,
  elapsed `9187.8877 ms`.
- Buckets: `1200-1399`: `6/47`; `1400-1599`: `11/53`.
- Progress emitted every 10 puzzles.
- Latest profile command:

```powershell
uv tool run py-spy record --subprocesses --format speedscope `
  --output .\scratch\lichess_d2_fast3_30.speedscope.json -- `
  uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py `
    --lichess-puzzles .\scratch\lichess_db_puzzle.csv `
    --rating-min 1200 `
    --rating-max 1600 `
    --limit 30 `
    --selector-mode argument `
    --dialectic-depth 2 `
    --progress-every 10
```

- Latest 30-puzzle profiled run: elapsed `2749.8398 ms`.
- Latest profile: `bounded_reply_attacks` dropped to about `0.5/2.9s`
  inclusive. Remaining heat is mostly owned-board square/check helpers and
  ordinary probe generation.

### Phase 5: Report

Status: complete.

Tasks:

- Update this workstream with commands, timings, hit rates, and profile result.
- State whether fixes belonged in generic argumentation or chess-specific code.

Acceptance criteria:

- The workstream records evidence, not vibes.

Result:

- The slowdown belonged in the chess sidecar, not the generic argumentation
  package. The argumentation selector/categoriser was not the hot path in any
  profile.
- The core fix was chess-specific: local board memoization, reply relevance
  filtering, explicit reply budgets, and cheaper direct recapture detection.
- Verification command:

```powershell
uv run --with chess --with z3-solver pytest `
  .\tests\test_dialectical_chess_evidence_ablation.py `
  .\tests\test_dialectical_chess_engine_api.py `
  .\tests\test_dialectical_chess_cleanup.py `
  .\tests\test_dialectical_chess_loss_mining.py
```

- Result: `30 passed`.
