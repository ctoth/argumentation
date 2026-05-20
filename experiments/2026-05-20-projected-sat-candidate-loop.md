# Projected SAT candidate-loop tightening

Date: 2026-05-20

Status: failed and reverted with projection route.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `bde9d06` Tighten projected SAT candidate loop.
- `f875e35` Revert "Tighten projected SAT candidate loop".
- `93741ea` Record failed assumption projection workstream.

Hypothesis: after projection, tightening the candidate loop would remove
Python overhead and make the projected route viable.

Gate: focused five-row fixture replay and py-spy evidence from the projected
route.

Outcome: failed.

Reason: cleanup did not change the fundamental route failure. The profile
still pointed into SAT solving, closure/support work, and candidate/coverage
materialization; the route was reverted instead of polished further.
