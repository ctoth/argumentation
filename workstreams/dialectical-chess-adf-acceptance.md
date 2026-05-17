# Dialectical Chess ADF Acceptance Workstream

## Goal

Make move acceptance depend on the set of legal opponent replies. This is the
natural chess/game-tree fit: a candidate move is acceptable only if critical
reply attacks are defeated or no better candidate exists. Scalar evaluation is
only a final preference among accepted candidates.

## Acceptance Shape

For candidate move `m`:

```text
accept(m) :=
  terminal_win(m)
  OR (
    has_support(m)
    AND no_undefeated_hard_reply_attack(m)
    AND all_critical_replies_answered(m)
  )
```

Critical replies are replies that checkmate, create mate threats, win decisive
material, or defeat the move's main warrant.

## Phases

### Phase 0: ADF Data Model

Status: pending.

Tasks:

- Add explicit acceptance-condition records.
- Keep Dung AF export for compatibility.
- Export ADF JSON alongside AF JSON when requested.

Acceptance criteria:

- Every selected move has an inspectable acceptance condition.

### Phase 1: Critical Reply Quantification

Status: pending.

Tasks:

- For each candidate, enumerate legal replies.
- Mark replies as critical/non-critical.
- Require defenses for critical replies.

Acceptance criteria:

- Candidate moves with undefended critical replies are not accepted when a
  defended alternative exists.

### Phase 2: Defeasible Acceptance

Status: pending.

Tasks:

- Add override ordering:
  - terminal mate support;
  - forced defense witness;
  - hard refutation;
  - king-safety defeater;
  - soft heuristic support.
- Represent overrides in acceptance explanations.

Acceptance criteria:

- The engine can explain why a risky move was accepted or rejected.

### Phase 3: Selection Replacement

Status: pending.

Tasks:

- Make ADF acceptance the primary selector.
- Keep grounded/ranking semantics as support for compatibility and soft
  ordering.
- Keep scalar score only as final tie-break.

Acceptance criteria:

- Selection code names ADF acceptance before score.
- Tests cover accepted, rejected, and accepted-by-override moves.

### Phase 4: Full-Game Gate

Status: pending.

Tasks:

- Run loss suite.
- Run 10-game full Stockfish 1320 anchor.
- Compare against 0/10 baseline.

Acceptance criteria:

- Improvement is measured honestly.
- If W/D/L does not improve, mate length or failure class must be reported.

## Completion Criteria

- ADF acceptance conditions are emitted in traces.
- Selection depends on reply-set acceptance.
- Full-game Stockfish result is remeasured without shallow adjudication hiding
  failures.
