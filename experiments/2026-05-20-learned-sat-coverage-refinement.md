# Learned SAT coverage refinement

Date: 2026-05-20

Status: abandoned with the learned SAT route.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `fa18d08` Reuse learned SAT candidate closure proofs.
- `a198b40` Add learned SAT coverage clauses directly.
- `07cdc14` Cache learned SAT coverage frontiers.
- `d055c5c` Require validated learned SAT seed fast path.
- `77cc524` Seed learned SAT with validated stable pruning.
- `1c45e01` Strengthen native CNF defense refinement.
- `1b46db5` Correct native CNF block contract.
- `ad317cc` Bound learned SAT coverage clauses.
- `2158f2f` Limit learned SAT coverage refinement.
- `d2c1e5b` Use first learned SAT coverage gap.

Hypothesis: coverage gaps and cached frontiers would keep candidate refinement
small enough for the learned SAT route.

Gate: focused sparse fixture replay plus contracts bounding coverage clauses.

Outcome: abandoned with the route.

Reason: bounding and caching made the route better controlled but did not turn
it into the winning hard-row solver. Completion SAT became the more concrete
direction.

Profiled diagnosis:
- Run artifacts:
  `data\iccma\2025\runs\shape-profile-learned-sat-reuse.json`,
  `data\iccma\2025\runs\shape-profile-learned-sat-bounded-coverage.json`,
  `data\iccma\2025\runs\shape-profile-learned-sat-direct.json`.
- Relevant raw profile:
  `data\iccma\2025\profiles\aba-SE-ST-auto-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-d62d9f410a29.raw.txt`
- The dominant stack after the coverage/reuse/bounded variants is still
  `native_sparse_narrow_learned_sat_extension ->
  _native_sparse_narrow_learned_completion_stable_result -> stable_extension ->
  solve (pysat\solvers.py)`, with the main sampled stack at `959`.
- Coverage and reuse machinery did not show up as the dominant runtime shape in
  the profile window.

Failure diagnosis: the coverage refinements controlled some Python-side
candidate machinery, but they did not make the underlying learned SAT formula
easy. The failure was therefore a true experiment failure at the search-shape
level, not merely an unprofiled timeout.

## Retroactive protocol audit

Protocol status: `promotion no-go; profiled family-level diagnosis complete`.

The record captures a long sequence of bounded/cached refinements and now ties
them to the profile evidence: the hard row still spent the profile window in
SAT solving rather than coverage-clause generation or closure proof reuse.

Required follow-up: do not add another coverage-refinement variant unless it
states how it changes the SAT search shape and carries a contract that can fail
before the full benchmark.
