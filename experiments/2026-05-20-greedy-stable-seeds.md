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
