# Learned SAT singleton conflicts

Date: 2026-05-20

Status: abandoned with the learned SAT route.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `bc6233d` Require static learned SAT singleton conflicts.
- `ff1acd9` Preload learned SAT singleton conflicts.

Hypothesis: singleton conflict clauses could reduce learned SAT search before
candidate enumeration became expensive.

Gate: static singleton conflict contracts and focused sparse fixture replay.

Outcome: abandoned with the learned SAT route.

Reason: singleton conflict preloading was not enough to rescue the general
learned SAT path. The later completion SAT work kept the lesson that small
static support information can help, but not this route as a whole.
