# ICCMA Round-1 H3 profile scout: SE-PR CEGAR re-grounding churn

Date: 2026-07-11
Status: **KILL — no churn-reduction source experiment authorized**
Scope: read-only analysis of existing development-only evidence. No benchmark,
new measurement, holdout access, source edit, or commit.

## Provenance and scope check

- Expected and observed tracked HEAD:
  `f701c2f19d7d8d6f770b233450c639c2786a7a14` on `main`.
- The checkout had many pre-existing untracked files. None was modified.
- Campaign frame:
  `experiments/2026-07-11-iccma2023-campaign-frame-baseline.md` and
  `reports/iccma-campaign-frame-worker-20260711.md`.
- Probe-1 record:
  `experiments/2026-07-11-iccma2023-stable-preferred-triage.md`.
- Probe-1 real-worker profile:
  `data/iccma/2023/profiles/round1-stable-preferred-triage/aba-SE-PR-aba_2000_0.3_10_10_1.aba-17dd9f6098c7.raw.txt`.
- Probe-1 telemetry/result:
  `data/iccma/2023/runs/iccma-2023-round1-stable-preferred-triage-20260711.json`.
- H3 proposal: `reports/iccma-round1-hotspot-scout-20260711.md`, H3.
- The profile is of the actual `iccma2025_run_native.py _worker` child and its
  live stack reaches `enumerate_preferred -> _grow_to_maximal_not_deriving ->
  _solve_one -> clingo.Control.solve`; it is not a wrapper-only profile.

The existing evidence is sufficient. I did not use the one permitted extra
development measurement.

## Finding

**Individual Clingo solve calls dominate. Re-grounding churn does not.**

The profiled development row was
`aba_2000_0.3_10_10_1.aba` / SE-PR, the same frozen 600-assumption row that
times out at the campaign's 10 s budget. With a 15 s diagnostic cap it solved
in **11.074908 s**, produced a preferred witness of size 350, and emitted:

| telemetry | value |
|---|---:|
| solver calls | 4 |
| outer iterations | 1 |
| inner iterations | 3 |
| refinement clauses | 3 |

Thus the supposed high-count churn is only three refinement rounds, not tens
or hundreds of rounds against the 600 assumptions.

Running the repository's existing `tools/collapsed_profile_summary.py` over
the existing raw profile accounts for **1,043 samples**:

| category | samples | share | interpretation |
|---|---:|---:|---|
| inside `clingo.Control.solve` | 968 | 92.81% | dominant |
| grounding, total | 30 | 2.88% | 27 initial; only 3 refinement grounding |
| program-add, total | 19 | 1.82% | initial program addition; refinement add was below sampling resolution |
| everything else outside solve/ground/add | at most 26 | at most 2.49% | Python orchestration, parsing, encoding, callbacks not already charged to solve |

The inner grow path itself contains 947 / 1,043 samples (90.79%). Probe 1's
stack-specific accounting places **928 samples in `Control.solve` while inside
that grow path**. The initial seed-solve path is small by comparison. The raw
profile does not assign elapsed time separately to each of the three inner
solve invocations, so it cannot say which one of those three is worst; it does
show that the solve invocations as a class, rather than the Python loop or its
incremental grounding, consume essentially the run.

Classification requested by H3:

- **Loop count:** not dominant; 3 inner iterations and 4 total solve calls.
- **Grounding/program-add:** not dominant; 49 / 1,043 samples even when all
  initial setup is generously charged to this category, and only 3 / 1,043
  samples are observed in refinement grounding itself.
- **Python orchestration:** not dominant; at most 26 / 1,043 samples outside
  solve/ground/add.
- **Individual Clingo solve calls:** dominant; 968 / 1,043 samples, principally
  the three calls inside grow-to-maximal.

## Maximum plausible benefit

The row must fall from 11.074908 s to below 10 s, a reduction greater than
**1.074908 s (9.71%)**, to change the campaign metric.

Three increasingly generous Amdahl ceilings all miss that requirement:

1. Removing the measured refinement grounding alone credits 3 / 1,043 samples
   (**0.29%**), about 0.032 s at this runtime.
2. Removing **all** grounding and program-add, including the initial control
   setup that an assumption-based grow loop cannot actually eliminate, credits
   49 / 1,043 samples (**4.70%**) and leaves an estimated **10.55 s**.
3. Impossibly removing every sample outside `Control.solve` credits 75 / 1,043
   (**7.19%**) and still leaves an estimated **10.28 s**.

Therefore a re-grounding/program-add/Python-churn-only change has a maximum
plausible campaign benefit of **0 newly solved rows on the profiled timeout**.
The frame has two SE-PR timeout rows, so the raw theoretical campaign headroom
remains +2, but no existing evidence supports either win from H3's stated
mechanism. A change that reduces the number or hardness of Clingo solve calls
would attack a different mechanism and needs a separately framed hypothesis;
it must not be counted as survival of re-grounding churn.

## Required executable contract for any attempted revival

H3 should not receive a source slice. If later evidence reopens it, the source
experiment must encode this contract **before** changing the algorithm:

1. Extend `IncrementalTelemetry` with `refinement_ground_calls`, incremented
   only for `ctl.ground([(refineN, [])])`, and surface it in solver metadata.
2. Add a deterministic flat-ABA SE-PR single-extension fixture whose current
   path needs at least three refinement rounds. Independently verify the
   returned witness against the native preferred semantics.
3. In a normally running focused test, require all of:

   ```text
   preferred witness is independently correct
   refinement_clauses >= 3
   refinement_ground_calls <= 1
   inner_iterations <= 1
   solver_calls <= 2
   ```

   The current path fails the operational bounds (`3` refinement grounds,
   `3` inner iterations, `4` calls). Merely batching three constraints into one
   ground while retaining four hard solves does not satisfy the contract,
   because the profile proves that shape cannot move the metric.
4. Run the focused gate with `uv run pytest -q` against the specific new test,
   then run one development-only real-worker telemetry/profile replay of the
   same frozen SE-PR row. Before any benchmark, that replay must preserve the
   independently checked witness, meet the same call/ground bounds, and move
   the dominant profile away from the current 968 / 1,043 solve-call shape.

This is an operational contract, not a semantic-only test or raw wall-clock
guess: it bounds the exact calls and refinement grounds that a genuine
batched-maximization mechanism claims to remove. The `solver_calls <= 2`
requirement is essential because the profile rules out grounding-only success.

## Decision

**KILL H3 as stated.** Existing real-worker evidence directly contradicts its
causal premise: the loop is short, refinement grounding is negligible, Python
orchestration is negligible, and Clingo solving dominates. No additional
measurement, benchmark, or source experiment is warranted for re-grounding
churn. The evidence-named next target is the search performed by the inner
Clingo solve calls, but pursuing that requires a new hypothesis with its own
pre-implementation operational contract.
