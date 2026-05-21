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

## Retroactive protocol audit

Protocol status: true diagnosed no-go.

This record includes the missing kind of evidence: focused gate failure plus
`py-spy`/profile interpretation showing the route still spent time in SAT
solving, closure/support work, and candidate/coverage materialization. It is a
usable negative experiment result for projected SAT candidate-loop cleanup.

Required follow-up: none for this cleanup slice; any new projected route must
change the profiled dominant work, not only polish the loop.
