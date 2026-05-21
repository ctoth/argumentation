# Completion SAT support-core reduction

Date: 2026-05-20

Status: failed and reverted.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `633b72a` Reduce completion SAT support core.
- `9f3e827` Revert "Reduce completion SAT support core".

Hypothesis: reducing the completion SAT support core would shrink the formula
and therefore speed the solver.

Gate: targeted tests and focused five-row fixture replay.

Outcome: failed.

Reason: smaller formula shape did not mean easier solving. The focused gate
regressed and the change was reverted.

## Retroactive protocol audit

Protocol status: `promotion no-go; gate-only failure record`.

The record says the smaller formula regressed, but it does not measure where
the time moved or whether CDCL search, clause quality, or Python-side
construction changed. This is not a mechanism-diagnosed experiment failure and
must not be used as proof that all support-core reductions are bad.

Required follow-up: if support-core reduction is revisited, compare solver
profiles or solver telemetry before and after the reduction on the same hard
row.
