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
