# Round 1 Probe Scout — working state (2026-07-11)

Role: `ward set researcher` applied (`ward: phase → researcher`). Read-only probe designer.
Deliverable: `reports/iccma-round1-probe-scout-20260711.md`.

## Read so far
- AGENTS.md perf-contract rule; campaign + experiment SKILL.md; experiments/INDEX.md;
  frame baseline; frame README; both 2026-07-11 negatives (N1 SAT route, N2 base-UNSAT);
  three scout reports (benchmark, git, history).

## The three dev timeouts (frame baseline)
1. `aba_2000_0.3_10_10_0.aba` SE-ST — timeout (Clingo solve 302/384 samples)
2. `aba_2000_0.3_10_10_0.aba` SE-PR — timeout
3. `aba_2000_0.3_10_10_1.aba` SE-PR — timeout
KEY ASYMMETRY: `aba_2000_0.3_10_10_1.aba` SE-ST **solves in ~1.2 s**. So within the
600-assumption stratum: row0 hard on both ST+PR; row1 easy on ST, hard on PR. Two
discriminators to explain: (a) instance row0 vs row1 within stable; (b) ST vs PR.

## Routing (verified in source)
- `aba_route_policy.py`: `sparse_narrow_native_sat_shape` requires **assumptions >= 700**
  → the 600 shape does NOT match → auto never routes it to SAT (N1 had to force `--backend sat`).
- `large_dense_flat_aba_shape`: flat + assumptions>150 + rule_density>25. aba_2000_0.3 has
  600 assumptions / 7867 rules ≈ density 13 → does NOT match dense gate either.
- Net: the 600 dev-timeout shape routes to **auto → ASP/Clingo** for both ST and PR.
- `_auto_aba_backend_for_framework` (solver.py:522): auto→sat only for
  preferred+single-ext+sparse_narrow(≥700) OR stable+single-ext+dense+sparse_narrow. Neither fires @600.

## Bottleneck classes seen in records/profiles
- N1: Clingo solve 302/384 (auto); forced SAT route → 391/399 in
  `_add_ranked_closure_constraints`/`_emit_ranked_closure_constraints` (Z3 never solved).
- N2: native CNF base UNSAT proof = 46.12 s (build 0.56 s); 47,648 vars / 64,928 clauses.
- history scout: ABA support materialization `_add_minimal_support` 92.7%, Cartesian blow-up
  at `aba_support_model.py:234`.

## Profile/telemetry hooks (benchmark scout)
- `--profile-workers-dir` + `--profile-workers-format raw|speedscope|...` + `--profile-worker-subtrack`
  → py-spy `--subprocesses` on REAL worker child.
- JSONL events via `--event-log-path`; `with_solver_metadata` records backend owner/route.
- `--jobs 1` mandatory for timing. `--max-aba-assumptions 1000000` (‑1 skips all ABA).
- Route contract: `tests/structured/aba/test_aba_sparse_narrow_route_contract.py` (shape-only, rejects locators).
- Calibrated wall: `tests/performance_contracts.py` (opt-in `ARGUMENTATION_PERF_CONTRACTS=1`).
- Diagnostic scripts: `scripts/diagnose_aba_stable_base_formula.py`.

## Dead ideas (do NOT re-propose)
- Auto SAT route for ABA-600 stable shape (N1): construction moved not shrank.
- Native-CNF base-UNSAT precheck ahead of Clingo (N2): 46 s > 5 s.
- Lazy-CNF acyc IPASIR-UP port: NO-GO ~4× too slow.
- Blind 964-row DC-CO 56-SCC predicate.
- cap-N 30s-gate phantom bottlenecks.
- route-on-graph-distance folklore.

## RESOLVED — the key mechanism
- SE-ST single-ext → `find_stable_extension` (aba_incremental.py:457): ONE solve
  (`:- out(X), not defeated(X).`). row1 = 1.2 s, row0 = timeout (hard SAT search, 302/384).
- SE-PR single-ext → `find_preferred_extension` (:591) → `enumerate_preferred(limit=1)` (:595):
  CEGAR loop — solve seed, `_grow_to_maximal_not_deriving` with repeated `ctl.ground` refinements.
  Many solver_calls + re-groundings. → explains SE-PR timing out on BOTH rows while SE-ST only row0.
- row1 SE-PR is the discriminator: SE-ST row1 cheap (1.2 s) ⇒ its timeout is the MAXIMIZATION LOOP,
  not a hard seed solve.
- Telemetry already deterministic + free: `_incremental_telemetry_metadata` → solver_calls,
  outer_iterations, inner_iterations, refinement_clauses; `collect_clingo_statistics` →
  clingo_grounding snapshot. Runner sets these via job dict (SE path, iccma2025_run_native.py:1024)
  but NO CLI flag exposes collect_clingo_statistics → probes call solver directly (read-only).
- SOUND CANDIDATE (not in dead list): stable⊆preferred → SE-PR single-ext can return a stable
  extension when one exists. row1 has a stable ext (SE-ST solved) → stable-first flips row1 SE-PR
  (+1). row0 has none cheap → no regression. #1 recommendation.

## TODO before writing report — DONE, writing report now
- Inspect aba_sat.py ranked-closure construction cost drivers (what scales it).
- Inspect aba_support_model.py:234 Cartesian blow-up + `_add_minimal_support`.
- Inspect aba_preprocessing.py simplify_aba (the 15s→0.824s hang fix history).
- Confirm ST vs PR code path divergence (why row1 ST solves, PR both timeout).
- Confirm the Clingo solve-timeout / check-budget plumbing (`clingo_solve_timeout_seconds`).
- Then: 4–6 probes (cmd, per-hypothesis expected obs, runtime bound, decision changed);
  ranked best first source experiment w/ prereg contract + kill threshold.
</content>
</invoke>
