# Assumption projection SAT route

Date: 2026-05-20

Status: failed and reverted.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `9763468` Add assumption projection SAT workstream.
- `35a54fb` Require assumption projection learned SAT contracts.
- `59a224b` Use assumption projection for learned stable SAT.
- `6799be9` Revert "Use assumption projection for learned stable SAT".
- `54bd9c4` Revert "Require assumption projection learned SAT contracts".

Hypothesis: projecting search onto assumption variables would cut the hard
rows down to a smaller SAT problem while preserving validation.

Gate: targeted tests and focused five-row fixture replay.

Outcome: failed.

Reason: the projected route was too weak operationally; prior evidence showed
the focused gate timed out across the hard rows even though semantic tests
could pass. This is exactly the class of failure the operational contracts
must catch.

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

This record captures a valid revert decision, but it does not include a
profiler-backed explanation of why projection remained too weak. Treat it as a
negative gate result, not a completed performance experiment.

Required follow-up: use the projected-route profile evidence, or rerun a
focused `py-spy` profile, before using this failure to choose another
projection-style optimization.
