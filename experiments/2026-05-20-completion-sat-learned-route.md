# Completion SAT learned route

Date: 2026-05-20

Status: kept on experiment branch; not promoted to `main` in the verified state.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `bb46498` Add completion SAT learned route workstream.
- `52ad3b2` Require completion SAT learned route contracts.
- `dd9667e` Use completion SAT for learned sparse ABA route.
- `5512441` Preload completion SAT singleton attacks.
- `7886f75` Account for completion SAT singleton probes.
- `721a967` Use CaDiCaL for sparse completion SAT.
- `c1f8c4d` Optimize completion SAT loop clauses.

Hypothesis: completion SAT, seeded with singleton attack information and using
CaDiCaL, would be the strongest known route for the sparse narrow hard class.

Gate: targeted learned SAT contract tests and focused five-row fixture replay.

Outcome: kept on the branch baseline.

Reason: this became the strongest verified branch path: targeted tests passed
and the focused gate reached four solved rows with one remaining timeout in
the prior run record. It was not yet merged to `main` when this file was
written.

Profiled remaining failure:
- Command family:
  `uv run tools\aba_shape_benchmark.py ... --profile-format raw --profile-duration-seconds 10`
- Relevant run artifacts:
  `data\iccma\2025\runs\completion-sat-focused-row3-profile.json`,
  `data\iccma\2025\runs\completion-sat-focused-row3-profile-after-support-nogoods.json`.
- Relevant raw profile:
  `data\iccma\2025\profiles\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.raw.txt`
- The profile enters
  `native_sparse_narrow_learned_sat_extension ->
  _native_sparse_narrow_learned_completion_stable_result -> stable_extension ->
  solve (pysat\solvers.py)`, with the dominant sampled stack at `897`.
- Completion-clause construction and static support-nogood setup are present
  only in small stacks, including `_add_completion_clauses` and
  `_add_static_assumption_attack_clauses`.

Failure diagnosis: the one remaining completion-SAT failure is a real solver
search failure on the learned completion formula, not primarily Python setup,
route telemetry, completion-clause construction, or support-nogood generation.
Further work has to change the CDCL search shape or the formula semantics that
drive it; another local construction micro-optimization is not the next
principled move.

## Retroactive protocol audit

Protocol status: kept branch baseline; remaining failure diagnosis complete.

The record supports completion SAT as the strongest branch path at the time,
and the one remaining timeout is now diagnosed by the raw profile. The kept
baseline is a real comparative result; the unsolved remainder is dominated by
PySAT/CDCL solve time on the completion formula.

Required follow-up: do not add another completion-SAT refinement unless it has
an operational contract that predicts a changed CDCL search shape, not merely a
smaller or differently assembled formula.
