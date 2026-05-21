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

Profiled diagnosis:
- Event artifact:
  `data\iccma\2025\runs\projection-row1-profile-events.jsonl`
- Relevant raw profile:
  `data\iccma\2025\profiles\aba-SE-PR-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-1554a482f39a.raw.txt`
- The profile reached
  `native_sparse_narrow_learned_sat_extension ->
  _native_sparse_narrow_learned_completion_stable_result -> stable_extension`.
- It did not become a cheap projected problem. The profile still shows
  `solve (pysat\solvers.py)` with a `321` sample stack, plus substantial
  Python-side projected/reachability work including `_add_coverage_clauses`
  (`187` samples), `_attacked_from_closure` (`139`), closure/support stacks,
  and candidate extraction stacks.

Failure diagnosis: assumption projection failed because the projected route
did not remove the hard operational work. It kept a nontrivial CDCL solve and
added enough coverage/closure/candidate machinery that the hard row still
profiled for the full window. This is a true operational failure of the
projection shape, not just a missing semantic test.

## Retroactive protocol audit

Protocol status: `promotion no-go; profiled failure diagnosis complete`.

This record captures a valid revert decision and now includes a profiler-backed
explanation of why projection remained too weak: it preserved solver search and
introduced substantial coverage/closure work.

Required follow-up: do not revive projection-style routing unless the
operational contract shows a real residual-size reduction and separately
bounds projection/coverage overhead before the benchmark gate.
