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

Profile context:
- The later completion-SAT profile with support nogoods
  (`data\iccma\2025\runs\completion-sat-focused-row3-profile-after-support-nogoods.json`)
  still shows the remaining hard row dominated by
  `stable_extension -> solve (pysat\solvers.py)`, with construction/setup much
  smaller than the solve stack.
- That supports keeping the small-support boundary, but it does not prove the
  exact larger-support mechanism.

## Retroactive protocol audit

Protocol status: `promotion no-go; gate-only larger-support failure`.

The record identifies the kept boundary as small support nogoods, but it does
not include profiler or SAT-search telemetry proving exactly why the extended
support set hurt. The interaction with phase behavior is plausible but not
measured in this record, so this should be used as a boundary result, not a
full mechanism diagnosis.

Required follow-up: any larger support-nogood retry needs solver telemetry that
compares clause count, solve time, and phase/candidate behavior against the
small-support baseline.
