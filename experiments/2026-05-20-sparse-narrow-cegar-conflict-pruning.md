# Sparse narrow CEGAR conflict pruning

Date: 2026-05-20

Status: kept on `main` as a measured route refinement.

Branch: `main`.

Evidence commits:
- `e176c6c` Add validated conflict pruning for sparse narrow ABA.
- `faf20de` Strengthen sparse narrow ABA CEGAR route.
- `848ccec` Defer sparse narrow ABA conflict learning.

Hypothesis: validated conflicts could prune the sparse narrow route without
changing semantics, and learning should be deferred when it is not yet shown
to pay for itself.

Gate: validation of pruned conflicts plus focused fixture replay.

Outcome: kept, with conflict learning deferred.

Reason: validated pruning is admissible evidence; eager conflict learning was
not yet justified by the gate and was kept out of the main path.
