# Workstream: Finish Remaining AF DS-PR Timeouts

Author: Codex
Date: 2026-05-03
Status: executable implementation workstream; reviewed twice by Claude before execution

## Scope

This workstream targets the eight AF `DS-PR` rows still timing out after
`reports/workstream-dspr-strong-learning.md`:

- ICCMA 2017:
  - `B/4/irvine-shuttle_20091229_1547.gml.80.apx`
  - `B/4/irvine-shuttle_20091229_1547.gml.80.tgf`
  - `D/2/BA_60_60_3.apx`
  - `D/2/BA_60_60_3.tgf`
- ICCMA 2019:
  - `instances/Small-result-b76.apx`
  - `instances/Small-result-b88.apx`
  - `instances/Small-result-b90.apx`
  - `instances/Small-result-b97.apx`

ABA remains out of scope until these AF rows are solved or explicitly deferred.

## Current Evidence

The previous workstream improved:

- 2017 full cap-100: `16 -> 4` timeouts.
- 2019 full cap-100: `7 -> 4` timeouts.
- Original 2017/2019 timeout fixture rows: `23/23` solved.

The remaining rows are classified as unique attacker/witness churn. Examples:

- `irvine-shuttle...80.apx`: `5946` unique attacker checks, `5945` learned
  witness regions.
- `BA_60_60_3.apx`: `5845` unique attacker checks, `5845` learned witness
  regions.
- `Small-result-b76.apx`: `4826` unique attacker checks, `4826` learned
  witness regions.

Conclusion: caching and exact duplicate suppression are exhausted. The next
fix must make each learned clause cover a larger semantic region.

## Claude Review Summary

Claude inspected the repo and identified two load-bearing issues:

- The current CDAS fallback extends an attacker with an arbitrary admissible
  witness, so `learn_witness_region` blocks a weak region.
- The solver runs on the whole AF before any grounded/SCC-local simplification.

Claude's strongest recommendation was to replace arbitrary admissible witness
learning with maximal preferred counter-witness learning first, then add safe
structural reductions. It also warned that full SCC-recursive preferred
semantics is easy to get wrong and should not be implemented as an approximate
shortcut.

Claude's adversarial review required these corrections, which this revision
adopts:

- call Phase 1 grounded acceptance/rejection shortcuts, not grounded reducts;
- use a checked-in remaining-eight manifest, not a selector over mutable latest
  run outputs;
- measure SAT-call count and wall-clock, not attacker-loop count alone;
- avoid a second persistent complete-labelling kernel in the CDAS loop;
- state the soundness obligation for switching from admissible witness
  existence to complete/preferred witness growth.

## Target Architecture

Keep one production `PreferredSkepticalTaskSolver`.

The fallback loop changes from:

1. find admissible attacker;
2. find any admissible extension containing attacker plus query;
3. learn a weak witness region.

to:

1. find admissible attacker;
2. find a complete/preferred-maximal query-compatible witness containing the
   attacker and query;
3. learn a maximal witness region.

Safe structural shortcuts run before CDAS:

- grounded-in query: accept.
- query attacked by grounded extension: reject.
- existing self-attacking, unattacked, acyclic, and preferred-super-core
  shortcuts remain.

Do not add a compatibility path or old/new dual solver. Update the existing
production path directly.

## Phase 0: Focused Remaining-Row Harness

Tests first:

- Add a checked-in manifest for the eight remaining rows.
- Add unit tests that prove the manifest is the source of truth.
- Add a batch runner invocation that can run only these eight rows at a fixed
  cap and write a summary.

Done when the eight-row gate is reproducible without manual row lists.

## Phase 1: Grounded Acceptance/Rejection Shortcuts

Tests first:

- Differential-test grounded-in and grounded-attacked shortcuts against native
  preferred enumeration on small generated AFs.
- Assert shortcuts emit:
  - `preferred_skeptical_shortcut_grounded_in`
  - `preferred_skeptical_shortcut_grounded_attacked`
- Assert no shortcut fires when the grounded extension does not decide the
  query.
- Assert shortcut priority:
  - self-attacking and unattacked remain first;
  - grounded checks run before acyclic and before preferred-super-core;
  - super-core-decided cases do not enter CDAS.

Implementation:

- In `PreferredSkepticalTaskSolver._shortcut`, compute grounded extension after
  the existing trivial self/unattacked checks.
- If query is in grounded, return true.
- If the query is attacked by the grounded extension, return false.

Done when targeted solver tests pass and the eight-row harness does not
regress.

## Phase 2: Maximal Preferred Witness Learning

Tests first:

- Add a reduced fixture where arbitrary admissible witness learning needs more
  loops than maximal preferred witness learning.
- Assert CDAS fallback emits `preferred_skeptical_extend_attacker_maximal`.
- Assert `preferred_skeptical_learn_witness_region` learns from the maximal
  witness fingerprint, not the arbitrary witness.
- Assert seed-unsat still returns false before constructing or using growth
  utilities.
- Assert when preferred-super-core decides the query, no
  `preferred_skeptical_extend_attacker_maximal` events occur.
- Differential-test DS-PR against native preferred enumeration on generated
  small AFs.

Implementation:

- Keep the existing admissible seed and attacker solver.
- For each attacker, first check whether an admissible extension containing
  `attacker ∪ {query}` exists, exactly as today.
- If no such admissible extension exists, return false.
- If it exists, grow that admissible witness toward a preferred witness using a
  complete-labelling kernel only inside the growth helper.
- Use utility name `preferred_skeptical_extend_attacker_maximal`.
- Learn the maximal witness region.

Soundness obligation:

- An admissible attacker `A` is a counter-witness iff no admissible extension
  contains `A ∪ {q}`.
- Every admissible set is contained in a complete extension, and every complete
  extension is contained in a preferred extension.
- Therefore, if the arbitrary admissible witness exists, growing it to a
  preferred witness preserves soundness and strengthens only the learned block.

Done when at least one of the eight remaining rows solves or the same cap shows
a kept 3x reduction in SAT-call count with no wall-clock regression on the
smaller selected BA row.

## Phase 3: Eight-Row Gate

Execution:

1. Run `uv run pytest tests\test_solver_encoding.py -q`.
2. Run ICCMA harness tests:
   `uv run pytest tests\test_iccma_timeout_corpus.py tests\test_iccma_run_selected.py tests\test_iccma_run_timeout_rows.py tests\test_iccma_trace_classify.py -q`.
3. Run the eight-row gate at 20 seconds.
4. If any row still times out at 20 seconds, run those rows at 60 seconds only
   to classify whether they are near completion or still unbounded churn.

Success criteria:

- Partial success: at least one of eight remaining rows newly solves.
- Full success: all eight rows solve.
- No regression in the previously solved selected fixture rows.
- Remaining failures, if any, are classified by trace family and exact utility
  counts:
  - last loop index;
  - learned count;
  - unique attacker fingerprints;
  - unique witness fingerprints;
  - total SATCheck events.

## Phase 4: Full AF Gate

Execution:

1. Run full cap-100 for 2017 and 2019 with a new label.
2. Compare against `dspr-strong-learning-cap100`.

Success criteria:

- 2017 full cap-100: `4 -> 0` timeouts.
- 2019 full cap-100: `4 -> 0` timeouts.

If the full gate fails, stop and classify the remaining rows. Do not proceed to
ABA.

## Stop Conditions

Stop immediately and report if:

- Maximal preferred witness learning does not solve a row and does not reduce
  SAT-call count by at least 3x on any remaining row.
- A shortcut fails differential testing against native preferred enumeration.
- A change worsens a previously solved selected timeout row.
- Full SCC-recursive semantics appears necessary. In that case, write a
  separate paper-reread workstream before implementing it.
