# Round 1 archaeology scout — working state

Role: `ward set researcher` (applied). Read-only. Deliverable:
`reports/iccma-round1-archaeology-scout-20260711.md`.

## Mission recap
Find 4–6 existing committed mechanisms / dormant routes / narrowly salvageable
ideas that could move the frozen **SE-ST / SE-PR timeout shape** WITHOUT reviving
recorded failures wholesale. Reject DC-CO-only or lazy-CNF work that can't
transfer. Per survivor: provenance, prerequisite operational contract, smallest
dev-only probe, expected impact, confidence, cost, semantic risk. Rank them.

## Frozen frame facts (established)
- Metric: solved rows over `population-dev.json`, 24 rows, backend auto, jobs 1,
  10 s per row. Baseline **21/24 @ `5f75a7c`**, deterministic 3×.
- The 3 non-solved dev rows (all `aba_2000_0.3`, 600-assumption stratum):
  - `aba_2000_0.3_10_10_0.aba` SE-ST — timeout
  - `aba_2000_0.3_10_10_0.aba` SE-PR — timeout
  - `aba_2000_0.3_10_10_1.aba` SE-PR — timeout
  - (`aba_2000_0.3_10_10_1.aba` SE-ST already solved ~1.2 s.)
- MME = +1 solved dev row (a baseline timeout → solved), holdout-confirmed.
- Any ABA routing change MUST extend shape route contract
  `tests/structured/aba/test_aba_sparse_narrow_route_contract.py` (fails on
  baseline, passes only on measured shape) BEFORE the benchmark gate.
- Budget: ≤8 triage probes, ≤3 full experiments. Kill: 2 consec no-survivor
  rounds; or a 3rd consecutive slice w/ no kept improvement (N1, N2 are the
  first two — one more makes three).

## Dominant cost on the target shape (profiler-backed, from records)
- auto/Clingo route: 302/384 py-spy samples in `clingo.Control.solve` (search).
- SAT route: 391/399 samples in `_add_ranked_closure_constraints` /
  `_emit_ranked_closure_constraints` (Z3 never reached). Construction cost is
  the NAMED next target for the 600-shape.
- native CNF base is UNSAT but proof took 46.12 s (build 0.56 s).
- ABA support: 92.7% in `_add_minimal_support` (`aba_support_model.py`),
  Cartesian blow-up at `aba_support_model.py:234` — proposed lazy/lower support
  gate, unstarted.

## Recorded DEAD (do not revive wholesale)
- Automatic SAT route for ABA-600 stable shape (N1) — construction moved, not shrank.
- Native-CNF base-UNSAT precheck (N2) — 46 s > 5 s.
- Lazy-CNF acyc port — NO-GO, IPASIR-UP correct but ~4× too slow (Python callback).
- Blind 964-row DC-CO 56-SCC predicate — dead until better features.
- cap-N 30 s-gate phantom bottlenecks — 28 experiments reverted.
- Route-on-graph-distance folklore — unsupported by paper evidence.

## D1 branch to inspect by Git object only
`exp/iccma-aba-dcco-100ba-acyc` @ `f21c22f`, +47 commits, base `7bc7fb7`.
DC-CO / 100ba-acyc route campaign. DC-CO is a DIFFERENT task/slice — must reject
DC-CO-only pieces; look for anything shape-general that transfers to SE-ST/SE-PR.

## Candidate survivor leads so far (to develop + cite)
1. ABA support Cartesian blow-up gate (`aba_support_model.py:234`, 92.7%) — named,
   unstarted, on the auto/Clingo hot path that IS the target's dominant cost.
2. Ranked-closure construction cost reduction (named next target from N1) — but
   only matters if SAT route is reconsidered; SAT route itself dead. Salvage =
   attack construction, not routing.
3. `exp/aba-satve` branch tip = recorded NO-GO SAT-VE (foundedness+acyclicity
   encoding) — inspect whether any encoding asset transfers.
4. ABA simplify_aba(stable) budget fix (`466d38d`/`exp/aba-simplify-stable-budget`,
   already promoted?) — check if the 600-shape benefits.
5. abcgen eager arc-acyclic foundedness (`exp/abcgen-arc-acyc`) — STABLE
   soundness derived; check transfer to SE-ST.
6. D1 branch route-shape discovery predicates / 100ba-acyc backend — salvage
   shape-general assets only.

## TODO
- git inspect D1 branch by object (log/show, no checkout).
- Inspect exp/aba-satve, exp/abcgen-arc-acyc, exp/aba-simplify-stable-budget tips.
- Read aba_support_model.py around 234 + _add_minimal_support.
- Read ranked-closure construction code.
- Pin exact commits/blobs for citations.
- Write report, rank 4–6 survivors.

## Guardrails honored
No checkout/stash/reset/clean/benchmark. Holdout untouched. Git object reads only.

## STATUS: COMPLETE
Report written: reports/iccma-round1-archaeology-scout-20260711.md.
Key routing finding: frame's 3 timeout rows (aba_2000_0.3, 600 asm, density ~13)
match NEITHER native shape (dense needs density>25; sparse-narrow needs asm>=700)
→ route to auto/Clingo; bottleneck is clingo.Control.solve UNSAT proof (302/384).
5 survivors ranked: S1 clingo-stats telemetry (enabler, on main); S2 flat_aba_core_facts
support-free encoding→SE-ST/SE-PR (best ceiling, on main + branch precedent 1.24s);
S3 cardinality _SupportAntichain (branch-only 543c334, weakly+, doubtful frame transfer);
S4 _MinimalSupportStats contract (branch-only d9d7796, enabler); S5 clingo control_args
config lever (on main, DC-CO out-biased heuristic reverted no-go).
Rejected: DC-CO 100ba-acyc/routing, lazy-CNF propagator (NO-GO ~4x), SAT-VE (NO-GO),
abcgen arc-acyc (already on main + wrong route), N1/N2 dead, all AF work (wrong slice).
