# Greedy stable seeds

Date: 2026-05-20

Status: failed and removed.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `6a09fe4` Try validated greedy stable seeds.
- `26a36c1` Remove failed greedy stable seed.

Hypothesis: a validated greedy stable seed could give the solver a useful
initial candidate and reduce later completion SAT work.

Gate: focused sparse fixture replay.

Outcome: failed.

Reason: validation kept the seed semantically safe, but it did not improve
the operational gate. Correct seeds are not automatically useful solver
guidance.

## Retroactive protocol audit

Protocol status: `promotion no-go; gate-only seed failure`.

The record proves that validated seeds did not improve the gate, but it does
not profile or otherwise measure whether seeding failed because it did not
change the first model, later refinement, clause learning, or candidate
validation cost. Do not use this as proof against all seed strategies; use it
only as proof that this validated greedy seed did not pass the focused gate.

Required follow-up: do not revive seed work without telemetry showing which
solver phase the seed is expected to affect and whether that phase actually
changes.
