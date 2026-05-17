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

Tasks:

- Add an explicit reply-analysis settings object.
- Thread it through probe and engine settings.
- Expose benchmark CLI knobs for reply budgets.

Acceptance criteria:

- Defaults preserve existing behavior for small positions.
- Settings serialize plainly.

### Phase 1: Memoized Board Operations

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

### Phase 2: Tactical Reply Filtering

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

### Phase 3: Explicit Budgets

Tasks:

- Add maximum reply and defense-node budgets.
- Add explicit `reply_analysis:truncated:*` trace labels when budgets are hit.
- Keep result deterministic by preserving sorted move order.

Acceptance criteria:

- A low budget produces a truncation trace.
- Default budget is high enough for current smoke tests.

### Phase 4: Progress and Profiling Loop

Tasks:

- Keep benchmark progress reporting on stderr.
- Rerun the real Lichess 1200-1600 sample with `dialectic_depth=2`.
- Profile again if runtime remains suspicious.

Acceptance criteria:

- Real-data run emits progress.
- Runtime is bounded and materially faster than the aborted no-cache/no-budget
  run.
- Hot frames no longer show nearly all time in unbounded reply defense.

### Phase 5: Report

Tasks:

- Update this workstream with commands, timings, hit rates, and profile result.
- State whether fixes belonged in generic argumentation or chess-specific code.

Acceptance criteria:

- The workstream records evidence, not vibes.
