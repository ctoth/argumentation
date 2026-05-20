# Sparse narrow fixedpoint fast path

Date: 2026-05-20

Status: kept on `main`.

Branch: `main`.

Evidence commits:
- `7bda98b` Add sparse narrow ABA fixedpoint fast path.
- `8a988c1` Validate sparse narrow fixedpoint witnesses.

Hypothesis: some sparse narrow ABA rows have a quickly checkable fixedpoint
witness, so SAT search can be skipped when the witness validates.

Gate: fixedpoint witness validation contracts.

Outcome: kept.

Reason: the fast path was guarded by witness validation rather than trusted
by shape alone. It is a real reduction when the witness exists, but the later
hard rows were not solved solely by this path.
