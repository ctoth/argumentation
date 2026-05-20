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
