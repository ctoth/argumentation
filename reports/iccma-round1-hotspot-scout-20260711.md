# ICCMA 2023 ABA Campaign — Round 1 Hotspot Scout

Date: 2026-07-11
Agent: direct Claude CLI scout. `ward set researcher` applied → `ward: phase → researcher`.
Scope: **read-only.** No source edited, no benchmark run, no holdout touched, no
Git mutation. Every number below is quoted from a committed record/profile or from
source I read; where I did not run something I say so.

Baseline commit: `5f75a7c` (`main`, clean). Frame:
`experiments/2026-07-11-iccma2023-campaign-frame-baseline.md`, ledger
`experiments/INDEX.md`. Budget for this frame: ≤ 8 triage probes / ≤ 3 full
experiments; two negatives (N1, N2) already recorded; one more no-improvement
slice fires campaign kill criterion (c).

---

## 0. The single fact that reframes the whole round

The mission names `_add_ranked_closure_constraints` as the target. **On the
baseline `--backend auto` route it is never called.** All three frozen dev
timeouts route to the Clingo multishot solver, not the Z3 ranked-SAT path.

Routing proof (source, not intuition):

- `_auto_aba_backend_for_framework` (`src/argumentation/solving/solver.py:522-546`)
  sends `stable`/`preferred` single-extension to the native/Z3 SAT path **only**
  when `sparse_narrow_native_sat_shape` (and, for stable, also
  `large_dense_flat_aba_shape`) holds.
- `sparse_narrow_native_sat_shape` (`src/argumentation/structured/aba/aba_route_policy.py:52-74`)
  requires **`assumptions >= 700`**. The frozen shape `aba_2000_0.3_10_10_*` has
  **600 assumptions** → predicate is `False`.
- `large_dense_flat_aba_shape` (`aba_route_policy.py:29-49`) requires
  **`rule_density > 25.0`**. This shape is `7867 rules / 600 assumptions ≈ 13.1`
  → `False`.
- Both gates fail, so `_auto_aba_backend` (`solver.py:504-519`) returns **`"asp"`**
  for `stable`+single-extension and `preferred`+single-extension when clingo is
  present. Confirmed both subtracks land on `asp`.

So the shape sits in a **routing gap**: below the 700-assumption sparse-narrow
threshold *and* below the density-25 dense threshold → auto always keeps it on
Clingo. The Z3 ranked construction cost (391/399 samples,
`experiments/2026-07-11-iccma2023-aba-600-stable-sat-route.md:55`) is the cost of
the **rejected N1 alternative**, reached only under a forced `--backend sat`.
Ranked-closure construction is therefore a *dead-end next-target*, not the live
baseline hotspot (see H5).

Second reframing fact, from N2
(`experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md:27-31`): the
stable **base formula for `aba_2000_0.3_10_10_0.aba` is UNSAT** (build 0.56 s,
solve 46.12 s), even with cycle-blocking removed. Relaxing the formula and still
getting UNSAT means the full stable formula is UNSAT → **row_0 SE-ST has no
stable extension**; its timeout is a hard *unsatisfiability proof*, not a
model search. Paired evidence: `aba_2000_0.3_10_10_1.aba` SE-ST *solves* in
~1.2 s (a witness exists), while `..._0` SE-ST times out — same shape, opposite
satisfiability
(`experiments/2026-07-11-iccma2023-campaign-frame-baseline.md:100-127`).

### The three frozen timeouts split into two distinct bottleneck classes

| Row | Subtrack | Baseline route | True nature | Live hotspot |
|-----|----------|----------------|-------------|--------------|
| `aba_2000_0.3_10_10_0` | SE-ST | clingo `find_stable_extension` (single solve) | **UNSAT** (no stable ext.) | clingo UNSAT proof, 302/384 samples in `clingo.Control.solve` |
| `aba_2000_0.3_10_10_0` | SE-PR | clingo `find_preferred_extension` → `enumerate_preferred(limit=1)` | SAT (preferred always exists) | CEGAR **grow-to-maximal** loop + per-step re-grounding |
| `aba_2000_0.3_10_10_1` | SE-PR | same as above | SAT | same CEGAR loop |

Code paths:
`find_stable_extension` `src/argumentation/structured/aba/aba_incremental.py:457-461`;
`find_preferred_extension`/`enumerate_preferred` `aba_incremental.py:591-637`;
inner growth `_grow_to_maximal_not_deriving` `aba_incremental.py:487-519` (permanent
refinement grounded per iteration at `:546-547` and `:614-615`);
ground-once control build `_new_control` `aba_incremental.py:322-344`;
default control args `DEFAULT_CLINGO_CONTROL_ARGS = ("--models=0", "--warn=none")`
`aba_incremental.py:44` (no `--configuration`, single thread, no restart tuning);
the completion encoding `src/argumentation/encodings/aba_com_incremental.lp`
(pi_com: `supported` + a redundant-for-stable `derived_from_undefeated` /
`attacked_by_undefeated` layer). Runner plumbs `clingo_control_args` and the
in-process solve budget: `tools/iccma2025_run_native.py:1024-1037`.

Any candidate that turns a frozen timeout `solved` within 10 s must therefore
either (a) accelerate the **SE-ST UNSAT proof**, or (b) shorten the **SE-PR
CEGAR maximization**. Routing to native/Z3 is closed by N1 (construction) **and**
N2 (46 s native solve). The hypotheses below attack (a) and (b) directly.

---

## Hypotheses (ranked)

Each states: suspected cost · location · existing evidence · a deterministic
operational contract that **must fail on baseline** (AGENTS.md gate) · cheapest
dev-only falsifying probe · expected impact · confidence · implementation cost ·
conflict with recorded dead ideas.

### H1 — Clingo configuration/portfolio cracks the SE-ST UNSAT proof (rank 1)

- **Suspected cost.** The SE-ST row_0 timeout is a single clingo solve that must
  prove UNSAT; the default config (`--models=0 --warn=none`, one thread, default
  heuristic/restart, `aba_incremental.py:44`) is search-order-unlucky on this one
  instance. UNSAT proofs are notoriously configuration-sensitive. The paired
  row_1 SE-ST proves SAT in 1.2 s under the *same* config — the config is fine
  for SAT, unproven for this UNSAT.
- **Location.** `AbaIncrementalSolver.__init__`/`_new_control`
  `aba_incremental.py:315,322-344`; args reach it via
  `solve_aba_with_backend(..., clingo_control_args=...)`
  (`aba_asp.py:99-181`) and the runner job field `clingo_control_args`
  (`iccma2025_run_native.py:1035`). The knob is already plumbed end-to-end and
  currently empty.
- **Existing evidence.** N1 baseline profile: **302/384 samples in
  `clingo.Control.solve`**, 38 grounding, 30 program-add
  (`experiments/2026-07-11-iccma2023-aba-600-stable-sat-route.md:24,54`) — the
  cost is *search*, not grounding. N2: the formula is genuinely UNSAT
  (`...-base-unsat-screen.md:27-31`). Same-shape row_1 solves in 1.2 s
  (`...-frame-baseline.md:127`).
- **Operational contract that must fail on baseline.** A telemetry contract on
  `IncrementalTelemetry.clingo_statistics` (populated via
  `collect_clingo_statistics=True`, `aba_incremental.py:358-364`): assert the
  default-config solve on row_0 exceeds a conflict/restart bound (e.g.
  `conflicts > C_max`) or reports `clingo_interrupted=True` at the 9 s in-process
  budget — true on baseline, false only if the candidate config closes the proof
  under budget. This is a deterministic solver-statistics contract, not a
  wall-clock guess (AGENTS.md-compliant).
- **Cheapest falsifying probe.** One dev row, one process: run row_0 SE-ST with
  `--backend auto` and `collect_clingo_statistics` on, then re-run passing
  `clingo_control_args` = a small sweep (`--configuration=trendy`, `=handy`,
  `=crafty`; `-t 4` parallel; `--restart-on-model`). If **no** config closes the
  UNSAT proof < 10 s, H1 is dead for row_0. Read-only to source; uses the
  existing `--jobs 1` harness on a dev instance only.
- **Expected impact.** +1 solved dev row (row_0 SE-ST). Portfolio/parallel could
  also help the SE-PR rows if their inner solves are the cost (partial overlap
  with H3).
- **Confidence.** Medium. UNSAT-proof configuration sensitivity is real and the
  knob is free, but there is no guarantee any stock config beats 10 s on a proof
  the native CNF needed 46 s for.
- **Implementation cost.** Low. Config-only; no encoding or algorithm change. A
  promoted change needs a shape-gated route/config contract per the frame rule
  (`experiments/INDEX.md:33-38`).
- **Conflict with dead ideas.** None. N1 (SAT route) and N2 (native precheck)
  changed the *backend*; H1 keeps the Clingo backend and changes only its
  configuration. Not previously tried.

### H2 — Leaner stable-only ASP encoding shrinks the UNSAT proof (rank 2)

- **Suspected cost.** `find_stable_extension` solves `pi_com` (the *complete*-set
  module) **plus** the add-on `:- out(X), not defeated(X).`
  (`aba_incremental.py:458`). For stable semantics the `derived_from_undefeated`
  / `triggered_by_undefeated` / `attacked_by_undefeated` layer of `pi_com` is
  redundant (in a stable model undefeated = in, so it collapses onto
  `supported`), yet it is grounded and propagated, roughly doubling the
  derivation program the solver must refute to prove UNSAT.
- **Location.** Encoding `src/argumentation/encodings/aba_com_incremental.lp`
  (the `derived_from_undefeated` / `attacked_by_undefeated` block and the two
  `:- in/out ... attacked_by_undefeated` constraints); consumed at
  `aba_incremental.py:336-340,458`.
- **Existing evidence.** 302/384 samples in solve with only 38 in grounding
  (`...-sat-route.md:54`) → the cost is propagation/search over the grounded
  program, exactly what a smaller program reduces. The redundancy is visible by
  reading the `.lp`: `supported` already encodes IN-derivation; the second
  derivation layer re-derives the same closure under a different name for the
  completeness constraints that stability subsumes.
- **Operational contract that must fail on baseline.** A grounded-size contract
  using `AbaGroundingObserver.rule_count` / `by_body_predicate`
  (`aba_incremental.py:167-187`, surfaced as `clingo_grounding`): assert the
  baseline stable grounding **contains** the `derived_from_undefeated/1` and
  `attacked_by_undefeated/1` predicate families (present on baseline; the leaner
  encoding emits neither). Deterministic, shape-independent, fails on baseline.
- **Cheapest falsifying probe.** Author the stable-only `.lp` as a scratch string
  (conflict-free `:- in(X), contrary(X,Y), supported(Y).` + all-out-attacked
  `:- out(X), not defeated(X).` over `supported` only), ground+solve row_0 in one
  process, compare grounded rule count and solve conflicts to baseline. If the
  grounded program and conflict count do not shrink, or UNSAT still > 10 s, H2 is
  dead. Correctness for stable must be re-derived before any promotion.
- **Expected impact.** +1 (row_0 SE-ST); possibly assists SE-PR only indirectly.
- **Confidence.** Low-medium. Smaller programs usually help, but a hard UNSAT
  core may survive the trim.
- **Implementation cost.** Medium: new encoding module + a soundness/completeness
  derivation for stable (empty-attacker and self-attack edge cases) before code,
  per the experiment protocol's fast-contract-first rule.
- **Conflict with dead ideas.** None. Distinct from N1/N2 (backend swaps) and
  from the lazy-CNF acyc NO-GO (that was an IPASIR-UP propagator, `INDEX.md`/history
  scout §4). This trims the *ASP* encoding, untouched territory.

### H3 — SE-PR CEGAR grow-to-maximal re-grounding churn (rank 3, widest headroom)

- **Suspected cost.** `find_preferred_extension` runs
  `enumerate_preferred(limit=1)` (`aba_incremental.py:591-637`), which even for a
  single extension pays the full inner growth loop
  `_grow_to_maximal_not_deriving` (`:487-519`). Each growth step adds a
  **permanent** `constr(out(I))` via `ctl.add(part,[],constraint); ctl.ground(...)`
  (`:544-547`, mirrored `:612-615`) — an incremental *re-ground* per iteration.
  With up to ~600 OUT assumptions the loop can re-ground and re-solve many times,
  so wall cost is dominated by repeated grounding + solves, not one hard solve.
- **Location.** `aba_incremental.py:487-519,591-637`; refinement grounding at
  `:546-547,614-615`.
- **Existing evidence.** Structural (I read the loop). **Both** SE-PR rows time
  out while only one SE-ST row does
  (`...-frame-baseline.md:114-115,126`), consistent with preferred being the
  harder, more-iterative path. No prior profile isolates this loop for the 2023
  shape — that gap is exactly what the probe closes (this is a
  `diagnosis-incomplete` area under AGENTS.md until profiled).
- **Operational contract that must fail on baseline.** A telemetry contract on
  `IncrementalTelemetry.{outer_iterations, inner_iterations, solver_calls,
  refinement_clauses}` (`aba_incremental.py:76-88,366-384`): assert the row_0
  SE-PR run performs `refinement_clauses > R_max` (i.e. > R re-groundings) or
  `solver_calls > S_max` before the budget — true on baseline, false only when a
  batched/assumption-based maximization removes the per-step re-grounding.
- **Cheapest falsifying probe.** Run row_0 SE-PR with `collect_clingo_statistics`
  on and read `inner_iterations`, `refinement_clauses`, and grounding-vs-solve
  split from `clingo_statistics`/`clingo_grounding`. If the loop makes few
  iterations and time is inside a single solve, the churn theory is falsified and
  SE-PR reduces to H1/H2-style single-solve hardness instead.
- **Expected impact.** Up to **+2** solved dev rows (both SE-PR timeouts) — the
  largest headroom in the frame — if the bottleneck is grounding churn amenable
  to a transient-assumption maximization (grow via `solve(assumptions=...)`
  instead of permanent re-grounding, the mechanism `_solve_one` already supports
  at `:387-426`).
- **Confidence.** Medium. Strong structural motive; unmeasured on this shape, so
  the probe is mandatory before any experiment.
- **Implementation cost.** Medium: reformulate maximization to avoid per-step
  re-grounding while preserving Algorithm-4 correctness; fast contract on the
  telemetry counters before the benchmark.
- **Conflict with dead ideas.** None. This is the L21-TPLP Alg-1/Alg-4 clingo
  path (`aba_incremental.py` docstring), orthogonal to the dead SAT route (N1),
  base-UNSAT precheck (N2), DC-CO predicate, and lazy-CNF port.

### H4 — Grounded-reduct / reachability preprocessing shrinks the residual (rank 4)

- **Suspected cost.** `simplify_aba` runs before the solve
  (`aba_asp.py:114-134`, `aba_preprocessing.py:233-279`) and can fix
  definitely-in/definitely-out assumptions and drop dead atoms/rules, handing a
  smaller residual to clingo. If the residual for row_0 is barely smaller than
  the original (2000 atoms / 7867 rules), the solver still faces the full hard
  core; if it collapses substantially, both the UNSAT proof (SE-ST) and the
  CEGAR loop (SE-PR) get cheaper.
- **Location.** `aba_preprocessing.py:233-279` (`simplify_aba`, `_residual_framework`,
  `is_trivial`); grounded-core primitive `grounded_assumption_set_via_closures`
  used by the solver at `aba_incremental.py:463-471`; Horn fixpoint
  `src/argumentation/structured/aba/_closure.py:19-60`.
- **Existing evidence.** The kept fix `2026-07-08-aba-simplify-stable-budget`
  cut one ABA row 15 s → 0.824 s by fixing a simplify blow-up (history scout §2
  #5) — proof that residual size moves this metric. Countervailing risk: SE/*
  single-extension queries carry **no query literal** to anchor query-directed
  reachability, so the reduct may be near-trivial here.
- **Operational contract that must fail on baseline.** A residual-size-reduction
  contract: assert `|residual.rules| / |original.rules| >= ρ` (near 1.0) on
  baseline for this shape — i.e. baseline preprocessing does *not* shrink it —
  and require a candidate to push the ratio below a target. (If the probe shows
  the residual is already tiny, the "hotspot" is mislocated and H4 is falsified
  in the cheapest possible way.)
- **Cheapest falsifying probe.** Call `simplify_aba(framework, semantics="stable")`
  and `="preferred"` on row_0 in one process; print residual assumptions/atoms/
  rules and `is_trivial`. One import, no solve. Instantly tells whether there is
  any reduction headroom.
- **Expected impact.** +1, possibly across both subtracks of row_0, *iff* the
  residual shrinks materially.
- **Confidence.** Low — no query to drive reachability on SE tasks; likely
  near-trivial reduct. Cheapest to falsify, so worth running first as a gate.
- **Implementation cost.** Low to probe; medium if a new no-query reachability
  prune (attack-graph reachability from contraries of assumptions) must be built.
- **Conflict with dead ideas.** None. Distinct from N1/N2. Reuses the existing,
  already-promoted preprocessing surface rather than a new backend.

### H5 — Rank-free closure encoding kills the `_add_ranked_closure_constraints` cost — but is dominated (rank 5, likely dead)

- **Suspected cost.** The mission's named target. In the Z3 SAT route,
  `_emit_ranked_closure_constraints` (`src/argumentation/structured/aba/aba_sat.py:1477-1557`)
  allocates one **Int `rank`** per literal (~2600) with `0 <= rank <= |literals|`
  and, per rule antecedent, a `ranks[antecedent] < ranks[literal]` term — roughly
  **29,631 Int-comparison AST nodes** (the dependency-edge count from N2,
  `...-base-unsat-screen.md:30`). Building that AST in Python is the 391/399
  bottleneck; the Int/LIA theory then makes the Z3 solve far harder than pure SAT.
  A rank-free encoding — precompute the deterministic Horn closure per candidate
  IN set (`_closure.horn_closure`, monotone least fixpoint, `_closure.py:19-60`)
  or reuse the existing pure-SAT acyclicity clauses `_add_arc_acyclic_clauses`
  (`aba_sat.py:1010`) — removes both the Int ranks and the construction blow-up.
- **Location.** `aba_sat.py:1477-1569` (`_emit_/_add_ranked_closure_constraints`),
  caller `_sat_ranked_stable_extension` `aba_sat.py:1427-1456`; alternative
  encodings already in-file at `:936-1010`.
- **Existing evidence.** N1: **391/399 samples in ranked construction**, Z3 never
  reached solve (`...-sat-route.md:55-56`). N2: the pure-SAT acyclicity/completion
  owner builds row_0 in 0.56 s but **solves in 46.12 s**
  (`...-base-unsat-screen.md:27-31`).
- **Operational contract that must fail on baseline.** An AST-construction contract:
  assert the ranked encoder emits `Int` rank vars and > N construction nodes (or
  takes > t s to build) for this shape before any `solver.check()` — true on the
  ranked baseline, false for the rank-free encoding.
- **Cheapest falsifying probe.** Build both encodings for row_0, count Z3 AST
  nodes / construction time, then `solver.check()` with a hard 9 s limit. Falsified
  the moment the rank-free encoding still misses 10 s.
- **Expected impact.** Nominally +1 (row_0 SE-ST) — but **N2 already measured the
  rank-free / native-CNF stable solve at 46 s** on this exact row, so removing the
  construction cost only exposes an UNSAT solve that is itself ~5× over budget.
- **Confidence.** Low. High chance it is dominated: fixing construction moves the
  bottleneck back into the 46 s solve N2 recorded.
- **Implementation cost.** Medium-high (new encoder + soundness re-derivation for
  the well-foundedness the ranks currently guarantee).
- **Conflict with dead ideas.** **Direct partial conflict.** N1 killed the Z3 SAT
  route for this shape and named ranked-closure construction as the "next target";
  N2 killed the pure-CNF stable solve at 46 s. H5 addresses N1's named target but
  runs straight into N2's wall. It should only be revived if a probe shows the
  rank-free solve (not just construction) beats 10 s — which contradicts N2 unless
  the encoding is materially different from the one N2 measured. **Recommend not
  spending a full experiment on H5** without that probe result first; it is listed
  because the mission named it and the record must state why it is dominated.

---

## Ranking and recommended triage order

1. **H1 (clingo config/portfolio)** — lowest cost, knob already plumbed, directly
   targets the SE-ST UNSAT proof; run first.
2. **H3 (SE-PR CEGAR churn profile)** — widest headroom (+2 possible) but needs a
   profile before an experiment; run its telemetry probe in the same round as H1.
3. **H2 (leaner stable encoding)** — structural, medium cost, attacks the same
   SE-ST proof from the encoding side; run if H1 stalls.
4. **H4 (preprocessing residual)** — cheapest possible falsification (one import,
   no solve); run its probe as a gate before H2/H5, since a near-trivial reduct
   would also bound H2's ceiling.
5. **H5 (rank-free closure)** — the named target, but evidence says it is
   dominated by N2's 46 s solve; do **not** open a full experiment without a
   solve-time probe that contradicts N2.

Probe budget note: H1, H3, and H4 probes are three cheap dev-only measurements
that together either surface a live candidate or confirm the third
no-improvement slice — either way they respect the frame's ≤ 8-probe budget and
never touch the sealed holdout
(`experiments/iccma2023-frame/population-holdout.json`).

## What I did NOT do / verify

- Ran **no** benchmark, profile, or clingo invocation; every count is quoted from
  N1/N2 records or read from source. The H1/H3/H4 contracts and probes are
  *proposed*, not executed.
- Did not confirm the exact per-config clingo behavior (H1) or the SE-PR iteration
  counts (H3) — those are the probes' jobs.
- Did not re-derive the N2 UNSAT result; I rely on
  `experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md:26-31`.
- Did not enter or disturb sibling worktrees; no stash/checkout/reset/clean; no
  Git mutation. `ward set researcher` was the only state change (phase set).
