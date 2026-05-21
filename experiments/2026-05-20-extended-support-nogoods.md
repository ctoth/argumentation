# Extended sparse support nogoods

Date: 2026-05-20

Status: failed and restored to the smaller kept behavior.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `51afae5` Extend sparse support nogoods.
- `be8b236` Prefer sparse stable SAT phases.
- `0c0ddec` Restore positive stable SAT phases.

Hypothesis: extending support nogoods beyond the small-support baseline would
prune more of the hard search space.

Gate: targeted tests and focused five-row fixture replay.

Outcome: failed.

Reason: the extended support set did not improve the hard-row gate and
interacted badly with phase behavior. The branch was restored to the smaller
support-nogood baseline.

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

The record identifies the kept boundary as small support nogoods, but it does
not include profiler or SAT-search telemetry proving why the extended support
set hurt. The interaction with phase behavior is plausible but not measured in
this record.

Required follow-up: any larger support-nogood retry needs solver telemetry that
compares clause count, solve time, and phase/candidate behavior against the
small-support baseline.
