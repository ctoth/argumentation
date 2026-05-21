# Learned SAT singleton conflicts

Date: 2026-05-20

Status: abandoned with the learned SAT route.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `bc6233d` Require static learned SAT singleton conflicts.
- `ff1acd9` Preload learned SAT singleton conflicts.

Hypothesis: singleton conflict clauses could reduce learned SAT search before
candidate enumeration became expensive.

Gate: static singleton conflict contracts and focused sparse fixture replay.

Outcome: abandoned with the learned SAT route.

Reason: singleton conflict preloading was not enough to rescue the general
learned SAT path. The later completion SAT work kept the lesson that small
static support information can help, but not this route as a whole.

Profiled diagnosis:
- Relevant run artifact:
  `data\iccma\2025\runs\shape-profile-learned-sat.json`
- Relevant raw profile:
  `data\iccma\2025\profiles\aba-SE-ST-auto-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-d62d9f410a29.raw.txt`
- The observed route reaches
  `native_sparse_narrow_learned_sat_extension ->
  _native_sparse_narrow_learned_completion_stable_result -> stable_extension ->
  solve (pysat\solvers.py)`, with the main sampled stack at `959`.
- Static singleton/support setup appears only as small construction stacks.

Failure diagnosis: singleton conflict preloading was not the dominant cost, but
it also did not change the dominant solver-search behavior enough to solve the
hard row. The useful lesson is bounded static support information as a
controlled input to completion SAT, not the singleton-conflict learned route as
a winning solver.

## Retroactive protocol audit

Protocol status: `promotion no-go; profiled family-level diagnosis complete`.

This record is useful lineage for the learned SAT branch and now records the
mechanism-level failure: singleton preloading did not move the hard-row profile
away from CDCL solve time.

Required follow-up: singleton conflicts should only be revived with a route
contract that shows a measurable search-shape change on the focused row.
