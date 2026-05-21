# Support-derived SAT phases

Date: 2026-05-20

Status: failed and removed.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `96e25cd` Seed stable SAT phases from support attacks.
- `368ed45` Remove failed support-derived SAT phases.

Hypothesis: setting SAT phases from support-attack structure would steer
CaDiCaL toward stable candidates faster.

Gate: focused sparse fixture replay.

Outcome: failed.

Reason: phase steering from support attacks did not improve the focused hard
class and was removed.

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

The record captures a valid removal decision, but it does not measure why the
phase hints failed. It does not show whether the hints were ignored, increased
conflicts, or steered the solver toward worse candidates.

Required follow-up: any future phase-steering experiment must record solver
telemetry comparing the hinted and unhinted search on the same hard row.
