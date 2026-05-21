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

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

This record is useful lineage for the learned SAT branch, but it does not
profile why singleton conflict preloading failed to rescue the route. It should
not be used as a complete mechanism-level failure result.

Required follow-up: if singleton conflicts are revived, compare solver search
telemetry before and after preloading on the same focused row.
