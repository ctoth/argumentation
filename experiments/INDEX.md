# Campaign: ICCMA 2023 ABA solver throughput (SE-ST / SE-PR slice)

Goal: solve more ICCMA 2023 ABA instances within a fixed per-instance wall
budget, without leakage or benchmark substitution. One metric, one frozen
population, one sealed holdout.

**Goal metric:** count of `solved` rows over the frozen development population
(`experiments/iccma2023-frame/population-dev.json`, 24 rows = 12 ABA instances ×
{SE-ST, SE-PR}), fail-closed, backend auto, `--jobs 1`, per-row budget **10 s**.
Baseline **21 / 24 solved at commit `5f75a7c`**, deterministic across 3 repeats —
full command, per-row table, and noise rule in
`experiments/2026-07-11-iccma2023-campaign-frame-baseline.md`.

**Minimum meaningful effect:** +1 solved dev row (a baseline timeout turned
`solved`), paired, confirmed on the holdout at promotion. Wall-clock speedups on
already-solved rows are exploratory only (inside wall noise; no ICCMA-score
effect).

**Holdout:** `experiments/iccma2023-frame/population-holdout.json` — 24 disjoint
rows, same derivation, **sealed**. Excluded from all triage and tuning; run once,
at promotion, by the verifier. Not measured at baseline (protocol does not
require a pre-candidate holdout baseline).

**Budget:** this frame is worth **≤ 8 triage probes and ≤ 3 full experiments**
before a synthesis/stop decision. Probes touch dev only, never the holdout.
Usage after Round 1 probe 4: **4 / 8 triage probes; 0 / 3 full experiments**.

**Campaign kill criteria:** stop and write the final synthesis when any holds —
(a) two consecutive triage rounds with no surviving candidate; (b) triage/
experiment budget exhausted; (c) a third consecutive slice with no kept metric
improvement (the two 2026-07-11 negatives below are already the first two — one
more makes three, and the exact-convergence line does not widen).

**Operational-contract gate (AGENTS.md):** the shape-based route contract
`tests/structured/aba/test_aba_sparse_narrow_route_contract.py` (8 tests, runs
normally, rejects locator metadata) + opt-in wall-clock contract are verified at
`5f75a7c`. Every candidate that changes ABA routing must extend this contract
with a shape predicate failing on baseline and passing only on its measured
shape, *before* the benchmark gate.

## Ledger

Prior 2023 records are reconciled here, not replaced. "unpromoted" = committed
evidence that never landed on `main` as a kept improvement.

| ID | Hypothesis / item | Status | Evidence | Cause of death / result |
|----|-------------------|--------|----------|-------------------------|
| 00 | Campaign frame + baseline (this commit) | framed | `experiments/2026-07-11-iccma2023-campaign-frame-baseline.md`; `experiments/iccma2023-frame/` | Baseline 21/24 solved @ `5f75a7c`, deterministic 3×; frame ready for triage |
| N1 | ABA-600 stable direct-SAT route beats Clingo in 5 s | triaged-out (negative) | `experiments/2026-07-11-iccma2023-aba-600-stable-sat-route.md` | `aba_2000_0.3_10_10_0` SE-ST still `timeout>5 s`; py-spy shows bottleneck **moved** Clingo-solve → `_add_ranked_closure_constraints` (391/399 samples), did not shrink. Kept only the runner SAT-select instrumentation (`000ae2c`). |
| N2 | Native-CNF base-UNSAT precheck ahead of the 5 s Clingo worker | triaged-out (negative) | `experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md` (`5f75a7c`) | Base **is** UNSAT but the proof took **46.12 s** (build 0.56 s) — a 46 s precheck cannot front a 5 s worker. Kept diagnostic `scripts/diagnose_aba_stable_base_formula.py`. Recorded as the **second consecutive slice without a kept improvement**. |
| R1-P1 | Stable-first shortcut for SE-PR single-extension | triaged-out (killed before source experiment) | `experiments/2026-07-11-iccma2023-stable-preferred-triage.md` | Flat and Clingo-routed; stable query completed in 0.834 s but returned **no extension/witness**, so no exact witness could pass the independent preferred verifier. Current SE-PR solved in 10.180 s with 4 calls / 1 outer / 3 inner / 3 refinements; real-worker profile remained Clingo-solve bound (928 samples). |
| R1-P2 | Clingo built-in configuration discriminator for SE-PR | triaged-out (no survivor; no source experiment) | `experiments/2026-07-11-iccma2023-clingo-config-triage.md` | Fixed 3× interleaved default/handy/crafty/trendy sweep: fastest `trendy` median **9.759 s**, every run **>9.0 s**; `handy` only 2/3 correct with one timeout. All successful arms retained 4 / 1 / 3 / 3 telemetry. Zero arms cleared the ≤8.0 s median + <9.0 s every-run gate; no loser profiled. |
| R1-P3 | Support-free/core-fact preprocessing for SE-ST/SE-PR | triaged-out (diagnosed negative; no source experiment) | `experiments/2026-07-11-iccma2023-support-free-core-fact-preprocessing.md`; `reports/iccma-s2-semantic-scout-20260711.md`; `reports/iccma-s2-operational-scout-20260711.md` | Candidate already exists: production Clingo uses `flat_aba_core_facts` without materialized supports and stable/preferred already use the grounded reduct. Both 600-assumption headroom instances retain 600/600 assumptions and all rules (0/2 reduced, covering 0/3 timeout rows). Existing real-worker profile remains preferred-growth solve-bound; no production slice or benchmark rerun. |
| R1-P4 | SE-PR CEGAR grow-to-maximal re-grounding churn | triaged-out (diagnosed negative; no source experiment) | `experiments/2026-07-11-iccma2023-cegar-regrounding-churn-triage.md`; `reports/iccma-round1-hotspot-scout-20260711.md`; `reports/iccma-h3-cegar-semantic-scout-20260711.md`; `reports/iccma-h3-cegar-profile-scout-20260711.md` | Completed hard-row telemetry is only 4 solver calls / 1 outer / 3 inner / 3 refinements. The committed real-worker profile places 928 samples in `clingo.Control.solve` on the growth stack versus 3 in refinement grounding. Exact maximality requires the final no-superset proof; re-grounding churn is not the bottleneck. Expected gain from the stated mechanism: 0 solved rows. |
| H2 | Delete the complete/admissibility undefeated layer for SE-ST | invalid premise; superseded (no probe) | `reports/iccma-h2-stable-semantic-scout-20260711.md`; `experiments/2026-05-21-aba-se-st-direct-stable-encoding.md` (`4deb85d`) | The earlier "untouched territory" premise was wrong. The exact lean stable-only deletion was implemented at `4b6ee26`, passed semantic contracts, solved 0/5, and was abandoned after its real-worker profile remained in `clingo.Control.solve` (2,440 samples versus 2,450 for the complete-module path). The retained record names the exact profile at `data/iccma/2025/profiles/aba-se-st-direct-stable-encoding/small/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`. |
| D1 | DC-CO / 100ba-acyc route campaign | unpromoted evidence (branch-only) | branch `exp/iccma-aba-dcco-100ba-acyc` @ `f21c22f` (**+47 commits, unmerged**; base `7bc7fb7`) | 47 commits of routing-shape discovery + acyc SAT propagator/lazy-CNF prototypes + 100ba-acyc backend, **never landed on `main`**. Not a frame candidate as-is: DC-CO is a different task/slice and the lazy-CNF port is a recorded NO-GO (IPASIR-UP correct but ~4× too slow). Promote-with-contract or salvage-then-drop is a foreman decision, out of this frame's scope. |

Note: the DC-CO stocktake diagnostic `experiments/2026-06-29-iccma-uncapped-aba-dcco-profile.md`
(`diagnosis-incomplete`, explicit "do not tune DC-CO through routing or Z3 yet")
is the committed rationale that D1's branch work has not been promoted.

## Round log

### Round 0 — Frame — 2026-07-11
Deliverable: goal metric + exact command, deterministic dev population + sealed
holdout, baseline, budget, kill criteria, operational-contract verification.
Candidates: 0 (framing only). Baseline: **21/24 solved @ `5f75a7c`**, identical
across 3 repeats. Dominant cost entering the campaign (from prior profiles): ABA
SE-ST/SE-PR Clingo solve search on the 600-assumption `aba_2000_0.3` shape (the
three baseline timeouts), with `_add_ranked_closure_constraints` construction the
named next target for any SAT alternative on that shape. Ideate/triage begins in
Round 1. Yield so far: 0 promoted; 2 recorded negatives (N1, N2); 1 unpromoted
branch (D1).

### Round 1 — Probe 1: stable-first SE-PR — 2026-07-11
Development-only probe on `aba_2000_0.3_10_10_1.aba` SE-PR. The shape is flat
and routes to Clingo, but the capped stable query returned no extension/witness;
therefore the stable-first shortcut cannot produce a preferred witness and is
**killed before a source experiment**. Current SE-PR entered its maximization
path (4 solver calls, 1 outer iteration, 3 inner iterations, 3 refinements), and
the real-worker profile was dominated by 928 samples in `clingo.Control.solve`
inside `_grow_to_maximal_not_deriving`, not grounding. Probe budget used:
**1 / 8**; full experiments used: **0 / 3**. Round 1 remains open with seven
probe slots; the next candidate must target the observed Clingo search cost.

### Round 1 — Probe 2: Clingo configuration discriminator — 2026-07-11
Development-only fixed sweep on `aba_2000_0.3_10_10_1.aba` SE-PR, using the
live direct solver API and independently validating every returned preferred
witness. Default, `handy`, `crafty`, and `trendy` ran three times each in the
preregistered interleaved order. No arm survived: `trendy` was fastest at
9.759 s median with a 9.852 s maximum, still beyond the ≤8.0 s / <9.0 s gate;
`handy` timed out once; default and `crafty` were slower. Every successful arm
kept the same 4 solver calls / 1 outer / 3 inner / 3 refinements, so the
preferred-growth operational invariant did not shrink. Per the frozen rule, no
loser was profiled and no source experiment is authorized. Probe budget used:
**2 / 8**; full experiments used: **0 / 3**. Round 1 remains open with six
probe slots; do not spend one on another generic built-in configuration sweep.

### Round 1 — Probe 3: support-free/core-fact preprocessing — 2026-07-11
Evidence-only adjudication of the semantic and operational scouts against the
committed frame, current source/tests, prior probes, and recorded real-worker
py-spy evidence. The candidate is already the production path: Clingo omits
materialized support facts, and stable/preferred already use the grounded
reduct. The reduct fixed 0 assumptions IN/OUT and retained 600/600 assumptions
plus 7867/7867 and 7699/7699 rules on the two hard development instances, so
0/2 headroom frameworks and 0/3 timeout rows shrink. The profile remains
Clingo-solve bound inside the unchanged 4/1/3/3 preferred-growth shape. The
candidate is killed without a source slice or benchmark rerun. Probe budget
used: **3 / 8**; full experiments used: **0 / 3**. No campaign kill criterion
fires: Round 1 remains open with five probe slots, and this read-only probe does
not advance the consecutive production-source-slice criterion. The next
candidate must preregister a new semantic claim and prove strict hard-instance
search-space reduction before any solver or benchmark call.

### Round 1 — Probe 4: SE-PR CEGAR re-grounding churn — 2026-07-11
Evidence-only adjudication of the authorized hotspot proposal and H3 semantic/
profile scouts against current code/tests and the committed probe-1 telemetry
and real-worker py-spy record. The completed hard preferred row has the short
exact shape 4 solver calls / 1 outer iteration / 3 inner iterations / 3
refinements. Its profile attributes 928 samples to `clingo.Control.solve`
inside grow-to-maximal and only 3 to refinement grounding; even removing all
observed non-solve work cannot move 11.074908 s below the 10 s campaign budget.
The refinement chain is semantically exact: strict supersets are sought until
the final unsatisfiable solve proves maximality. H3 is killed as stated without
a source slice, solver/benchmark rerun, redundant profile, or holdout access.
Probe budget used: **4 / 8**; full experiments used: **0 / 3**. No campaign
kill criterion fires because Round 1 remains open, budget remains, and this
evidence-only probe does not advance the consecutive production-source-slice
count. The next candidate must separately preregister an exact one-shot
preferred-maximality/search hypothesis with semantic and operational contracts
that target work inside the inner Clingo solves.

### Round 1 — H2 invalidity correction: stable-only deletion — 2026-07-11
The earlier claim that H2 was untouched territory was wrong. The exact
stable-only deletion, semantic contracts, 0/5 result, and unchanged solve
profile were already retained in
`experiments/2026-05-21-aba-se-st-direct-stable-encoding.md` at `4deb85d` after
the `4b6ee26` implementation was abandoned. H2 is superseded and killed; this
history correction is not probe 5 and creates no new experiment record. Probe
budget remains **4 / 8**; full experiments remain **0 / 3**.
