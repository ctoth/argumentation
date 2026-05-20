# Sparse fixedpoint ABA probe mode

Date: 2026-05-20

Status: kept on experiment branch.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commit:
- `87f3410` Add sparse fixedpoint ABA probe mode.

Hypothesis: exposing a probe mode for sparse fixedpoint behavior would make
later solver experiments easier to gate and diagnose.

Gate: targeted tests.

Outcome: kept on the branch.

Reason: this is diagnostic/test support, not the final solver path. It
improves the ability to characterize future route behavior.
