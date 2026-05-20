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
