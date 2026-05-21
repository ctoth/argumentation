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

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

The record captures a long sequence of bounded/cached refinements, but it does
not contain a mechanism-level profile explaining why coverage refinement still
missed the hard-row gate. It is branch history, not a fully diagnosed failure.

Required follow-up: do not add another coverage-refinement variant without a
profile showing whether the cost is SAT solving, closure proof reuse,
candidate materialization, or coverage-clause generation.
