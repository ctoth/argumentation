# Completion SAT direction research

Date: 2026-05-20

Status: kept as research direction on the experiment branch.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commit:
- `590ee7e` Research ABA completion SAT direction.

Hypothesis: the hard sparse narrow rows should be represented through the
ABA completion structure rather than only through candidate coverage repair.

Gate: research note plus subsequent implementation experiments.

Outcome: kept as the direction that produced the best branch baseline.

Reason: later completion SAT commits improved the focused gate relative to
the failed projection and inprocessing attempts. This note does not by itself
prove the final solver; it records the pivot that subsequent gates tested.
