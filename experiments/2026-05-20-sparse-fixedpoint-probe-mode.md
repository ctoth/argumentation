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

## Retroactive protocol audit

Protocol status: diagnostic infrastructure, not a solver-performance result.

The failure-analysis rule is not triggered because this record adds probe
support rather than claiming a failed optimization is complete. It should be
used as instrumentation for later experiments, not as a solved-row result.

Required follow-up: use the probe mode inside future metric/profile gates when
the fixedpoint behavior is part of the hypothesis.
