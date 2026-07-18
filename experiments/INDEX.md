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
Current usage after Probe 8 Gate B: **7 / 8 triage probes; 0 / 3 full
experiments**. Gate A passed free; Gate B's first permitted-row access consumed
Probe 8 and then failed closed at the frozen 5.0-second row wall cap.

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
| R1-P5 | Exact collective-attack SCC conditioning for stable/preferred | triaged-out (promotion no-go diagnosed; no source experiment) | `experiments/2026-07-11-iccma2023-probe-5-scc-semantic-contract.md`; `experiments/2026-07-11-iccma2023-probe-5-scc-operational-measurement.md`; `experiments/artifacts/2026-07-11-probe-5-scc-shape.json`; `scripts/measure_aba_scc_composition_shape.py`; `tests/structured/aba/test_aba_scc_composition_shape.py` | Six focused shape tests passed, but the exact frozen dev command did not complete its first support extraction or emit partial output after about 13 minutes. Real-process `py-spy` localized the active stack to eager `_minimal_supports` antichain construction before `require_cap`; the 4,096 collective-attack cap does not bound extraction, so frozen clause 2 did not become executable. No row metrics, holdout, source slice, solver timing, benchmark, or full experiment. |
| R1-P6 | Small assumption backdoor/cutset conditioning into exact residual components | triaged-out (semantic kill; no operational work) | `experiments/2026-07-11-iccma2023-probe-6-backdoor-semantic-contract.md`; `scripts/aba_backdoor_cutset_reference.py`; `tests/structured/aba/test_aba_backdoor_cutset_contract.py` | The bounded reference and 300 fixed-seed examples agree with both authorities on every qualifying cutset, but the frozen `two_component_cut_attack_union` fixture is not a separator: both attack-rule factors remain joined through the shared `contrary(k)` literal after deleting `k`, leaving one assumption-bearing component. The exact frozen fixture/path contract is unsatisfiable and fails closed. |
| R1-P7 | Direct CaDiCaL 2.2.1 on the unchanged eager-arc one-shot stable CNF | blocked before probe; dependency/API capability absent | `experiments/2026-07-11-iccma2023-probe-7-cadical221-eager-arc.md`; red contract `a62b6c3` | Exact `rel-2.2.1` built and reported `2.2.1`; trivial SAT/UNSAT and independent DRAT validation passed. Capability failed closed before target access: `get_statistic_value("restarts")` returns unsupported sentinel `-1`, while the frozen raw `val(v)`/`val(-v)` opposite-answer condition contradicts the observed/documented IPASIR result (`val(1)=-1`, `val(-1)=-1`). No diagnostic engine, ICCMA row, metric, profile, production change, or holdout access. Probe not consumed; budget remains 6/8. |
| R1-P8 | Multiplicity-aware true-clone/module quotienting for ABA SE-PR | Gate A pass; Gate B fail-closed; probe consumed | `experiments/2026-07-11-iccma2023-probe-8-multiplicity-true-clone-quotient.md`; `experiments/artifacts/2026-07-11-probe-8-true-clone-shape.json` | Five focused shape contracts passed. First actual access consumed Probe 8; row `..._0.aba` emitted no telemetry before the frozen 5.0 s wall cap. No retry. Row `..._1.aba` was not opened after the gate became irreversibly red. No structural-survival claim, selected row, solver/profile work, production change, or holdout access. Usage 7/8; campaign goes to final synthesis. |
| H2 | Delete the complete/admissibility undefeated layer for SE-ST | invalid premise; superseded (no probe) | `reports/iccma-h2-stable-semantic-scout-20260711.md`; `experiments/2026-05-21-aba-se-st-direct-stable-encoding.md` (`4deb85d`) | The earlier "untouched territory" premise was wrong. The exact lean stable-only deletion was implemented at `4b6ee26`, passed semantic contracts, solved 0/5, and was abandoned after its real-worker profile remained in `clingo.Control.solve` (2,440 samples versus 2,450 for the complete-module path). The retained record names the exact profile at `data/iccma/2025/profiles/aba-se-st-direct-stable-encoding/small/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`. |
| H3-S1 | One-shot global maximum-cardinality complete set for SE-PR via `#maximize` | invalid premise; superseded (no probe) | `reports/iccma-maxcard-semantic-scout-20260711.md`; `reports/aba-preferred-salvage-inventory.md` (`5d7a5b6`); branch `experiment/aba-asp-saturation-preferred` (`fe1c317`, `aa56b7c`, `b6c9b1d`, failure record `408f4b0`) | The earlier candidate-selection premise was wrong. The exact one-shot Lehtonen `pi_com` construction with `#maximize { 1,X : in(X) }.`, proved-optimum waiting, and the existing single-witness result shape was already implemented and passed semantic gates. T1/T3/T5/T6/T8 then timed out on `auto`, `asp`, and `sat`. Retained diagnosis: global ASP optimization over complete extensions does not solve the dense preferred class. |
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

### Round 1 — Post-H3 invalidity correction: global max-cardinality preferred — 2026-07-11
The earlier candidate-selection premise was wrong. The proposed exact one-shot
global maximum-cardinality preferred witness was already implemented on
`experiment/aba-asp-saturation-preferred`: semantic properties landed at
`fe1c317`, the ASP maximality route at `aa56b7c`, proved-optimum witness return
at `b6c9b1d`, and the retained failure diagnosis at `408f4b0`. The construction
used Lehtonen `pi_com` with `#maximize { 1,X : in(X) }.`, waited for the proved
optimum, and returned the existing single-extension shape. Its semantic gates
passed, but T1/T3/T5/T6/T8 timed out on `auto`, `asp`, and `sat`. The retained
diagnosis is that global ASP optimization over complete extensions does not
solve the dense preferred class. This supersession spends no probe and creates
no experiment: usage remains **4 / 8 triage probes** and **0 / 3 full
experiments**.

### Round 1 — Candidate-history inventory freeze — 2026-07-11

`reports/iccma-history-sepr-inventory-20260711.md` and
`reports/iccma-history-sest-inventory-20260711.md` are together the authoritative
candidate-history boundary for this campaign. Known dead or superseded families
identified there must not reopen without new evidence that invalidates their
recorded cause of death or supersession. The single selected next target family
is **directed ABA SCC-recursive exact conditioning/decomposition**; this records
novelty and selection only and does not claim semantic composition or
operational usefulness.

The selected next task is to derive an executable semantic composition contract
before any shape measurement or source slice. Its exact question is:

> For every finite ordinary flat ABA framework in the bounded generated test
> domain, does a directed assumption-dependency/attack SCC recursion with
> explicit predecessor-boundary conditioning return, after lifting, exactly the
> same stable-extension set and exactly the same preferred-extension set as the
> direct semantic oracles, in both directions, including cross-SCC rule and
> contrary dependencies, empty and factual attackers, and branches with no
> extension?

This inventory freeze is not a probe and consumes no probe budget. Usage remains
exactly **4 / 8 triage probes** and **0 / 3 full experiments**. No shape
measurement, source slice, solver, benchmark, or holdout work is authorized by
this entry.

### Round 1 — Probe 5: collective-attack SCC semantic contract — 2026-07-11

The selected theorem is now executable as a bounded diagnostic/reference
contract. It materializes minimal-support collective attacks, normalizes factual
attackers, computes the collective-attack primal SCCs, and recursively carries
conditioned tails plus exact `D/P/U/UP` and preferred `C/M` state. Named fixtures
and bounded generated cases require complete stable and preferred extension-
family equality against both current direct native and support-model oracles;
the path contract also requires multiple SCCs, a cross-SCC collective tail,
partial activation, defeated-tail discard, nonempty mitigation, factual
normalization, and stable-branch annihilation.

No ICCMA hard row, benchmark, solver worker, production `src/` path, or holdout
was accessed. The separately committed operational shape measurement is
preregistered in
`experiments/2026-07-11-iccma2023-probe-5-scc-semantic-contract.md` and is
authorized only after this semantic gate passes. It must fail closed on the
frozen support, branch-state, and full-boundary caps and must prove more than one
useful SCC plus strict maximum-residual reduction on at least one hard
development framework. Probe budget used: **5 / 8**; full experiments used:
**0 / 3**.

### Round 1 — Probe 5 reconciliation: operational shape killed — 2026-07-11

After the six focused shape tests passed, the exact frozen development-only
command began. After about 13 minutes it had not completed the first exact
support extraction and had emitted no partial artifact. The real hot process
had accumulated about 800.42 CPU-seconds with a 2,318,831,616-byte working set.
`uv run --with py-spy py-spy dump --pid 362188` attached to that process and
reported `_add_minimal_support` -> `_minimal_set` -> `_combine_supports` ->
`_minimal_supports`, called by the diagnostic's `_measure_framework` and
`main`.

The diagnostic eagerly computes `_minimal_supports(framework)` before it can
count the collective attacks and call `require_cap`. The frozen 4,096 cap
therefore does not bound extraction itself. Frozen survival clause 2 did not
change and was not executable on the first hard row. The run was interrupted
only after this diagnosis. No per-row structural metric completed; no metric
is inferred. The profiler-backed operational record is
`experiments/2026-07-11-iccma2023-probe-5-scc-operational-measurement.md`, and
the fail-closed artifact is
`experiments/artifacts/2026-07-11-probe-5-scc-shape.json`.

Probe 5 is **operationally killed** with status
`promotion_no_go_diagnosed`; it is not an incomplete benchmark and consumed no
full experiment. Budget remains **5 / 8 triage probes** and **0 / 3 full
experiments**. No campaign kill criterion fires: the budget is not exhausted,
Round 1 is the only triage round, and this diagnostic-only probe did not create
a production source slice or advance the consecutive kept-production-
improvement criterion. Round 1 remains open.

The next candidate named by the committed history inventory is **small
backdoor/cutset conditioning into exact residual components**. It requires
bounded cutset/strict-residual telemetry and an exact lift/validation semantic
contract before any solver probe. This reconciliation does not start it.

### Round 1 — Probe 6 adjudication: strengthened cutset theorem survives — 2026-07-11

The constructive and adversarial backdoor reports were adjudicated without
averaging their conclusions. The strengthened candidate remains the inventory's
small assumption backdoor/cutset family, not bounded-incidence-width or tree-
decomposition DP: it deletes one bounded assumption set `K` from the compact
rule/contrary factor-incidence graph and proceeds only when that deletion
separates at least two assumption-bearing residual components. Exact per-
component attacked-`K` signatures, cut-defense obligations, admissible lifts,
deduplication, and global inclusion maximality are frozen boundary semantics,
not an `IN/OUT/UNDEC` product.

The adversarial fixed-`k=1` exponential-support family does not satisfy this
separator antecedent. With `K={x}` deleted, the factor for
`bar(c) <- x,t_1,...,t_m` connects every `t_i`; their rule factors connect all
`u_i,v_i`, and the contrary link connects `c`. There is one assumption-bearing
residual component, so `K={x}` is invalid. The family falsifies only the naive
`3^k` complete-state claim and reinforces the bans on eager minimal-support
extraction and post-extraction caps; it does not falsify the strengthened
theorem or fail-closed operational bounds.

The decisive record is
`experiments/2026-07-11-iccma2023-backdoor-cutset-adjudication.md`. Verdict:
**PROCEED TO PROBE 6 SEMANTIC CONTRACT.** This adjudication does not itself
spend the probe: usage remains **5 / 8 triage probes** and **0 / 3 full
experiments**. Exact next action is the bounded diagnostic/reference semantic
contract and ten named fixtures only. No shape measurement, source route,
solver call, benchmark, hard-row access, or holdout access is authorized.

### Round 1 — Probe 6 semantic contract: killed by frozen non-separator fixture — 2026-07-11

The bounded diagnostic/reference and its tests were implemented without any
production source, solver, benchmark, hard-row, holdout, profile, or operational
measurement. Nine composable named fixtures and all `300` deterministic
Hypothesis examples matched exhaustive admissibility plus both current direct
native and independent support preferred authorities for every qualifying
`K`, including empty and nonempty cutsets. Exact selected/rejected cut state,
attacked-`K` signatures, cut-defense obligations, collective-tail activation,
canonical lift/deduplication, and one global maximality filter are executable.

The tenth frozen fixture, `two_component_cut_attack_union`, requires both
`{a}->k` and `{b}->k` to contribute from distinct residual components after
deleting `K={k}`. Under the frozen compact rule/contrary factor-incidence graph,
both stored-rule factors share the literal `contrary(k)`, so `a` and `b` remain
connected in one assumption-bearing residual component. The diagnostic
explicitly returns `NonSeparatorError`; it does not silently compose or
substitute a different fixture. The fixed-`k` adversarial family is likewise
explicitly rejected as a non-separator.

The decisive record is
`experiments/2026-07-11-iccma2023-probe-6-backdoor-semantic-contract.md`.
Verdict: **SEMANTIC KILL.** Probe usage is now **6 / 8 triage probes** and
**0 / 3 full experiments**. The later support-free operational contract is not
preregistered and no operational telemetry, production route, solver probe,
benchmark, hard row, or holdout action is authorized. The next action is a
campaign-level correction/replacement of the inconsistent frozen package or
selection of the next inventory candidate.

### Round 1 — Probe 7 preregistration: CaDiCaL 2.2.1 eager-arc engine — 2026-07-11

Fresh read-only inventory and adversarial analyses agree that modern direct
CaDiCaL on the current eager-arc one-shot CNF is materially untried. Their
version disagreement is resolved by pinning the latest identified 2.x release,
`rel-2.2.1` at `4198d817d0dcde5b1240eefbff70b555b7df2af9`.

The exact capability, red operational contract, semantic authorities,
formula/variable/clause/phase identity hashes, sole SE-ST development row,
one-solve eager/no-fallback shape, process caps, interleaved repetition plan,
survival thresholds, and mandatory miss diagnosis are frozen in
`experiments/2026-07-11-iccma2023-probe-7-cadical221-eager-arc.md`. The
capability gate precedes probe consumption; absence is blocked-before-probe.
No CaDiCaL build, contract implementation, ICCMA row, production source,
holdout, or full development run is part of this records-only slice.

Usage remains exactly **6 / 8 triage probes** and **0 / 3 full experiments**.
Probe 7 is preregistered and **not consumed**. Because the current production
route excludes the 600-assumption row, even a positive diagnostic can authorize
only a separately preregistered routing experiment.

### Round 1 — Probe 7 capability outcome — 2026-07-11

The red-first deterministic contract was committed alone as `a62b6c3` before
the candidate build. A clean temporary checkout verified exact CaDiCaL source
identity `rel-2.2.1` / `4198d817d0dcde5b1240eefbff70b555b7df2af9` and runtime
version `2.2.1`. The direct C++ capability driver passed clause, assumption,
signed phase, termination-entrypoint, SAT, UNSAT, and proof-tracing calls. The
separate `drat-trim` checker at commit `2e3b2dc` independently verified the
trivial UNSAT proof.

The exact API nevertheless fails two frozen capabilities. Its direct statistic
query returns `-1` (unsupported) for `restarts`, and the real IPASIR values are
the same signed assigned variable for positive and negative queries—for example
`val(1)=-1` and `val(-1)=-1`—rather than the preregistered opposite raw answers.
The successful capabilities cannot substitute for either fail-closed
requirement. Status is **blocked before probe; dependency/API capability
absent**. The sole ICCMA row was not opened, so Probe 7 was not consumed and
usage remains **6 / 8 triage probes** and **0 / 3 full experiments**.

### Round 1 — Probe 8 preregistration: multiplicity-aware true-clone quotient — 2026-07-11

The last selected quotient family is frozen in
`experiments/2026-07-11-iccma2023-probe-8-multiplicity-true-clone-quotient.md`.
Gate A is a free bounded semantic contract committed before any development-row
access. It requires independently verified complete-framework, fix-outside
transpositions; rejection of entangled A/B attacker matching and near clones;
full-orbit family lifting distinct from later canonical witness selection; and
complete preferred-family equality with both native and support authorities on
12 named fixtures plus exactly 300 fixed-seed ordinary flat ABA frameworks.

Only a committed Gate A pass opens Gate B. First access to either of the two
authorized `aba_2000_0.3_10_10_{0,1}.aba` SE-PR rows consumes Probe 8 and moves
usage to 7/8. Gate B is normalized-incidence shape telemetry only: deterministic
color refinement followed by per-transposition verification as sole authority,
with no solver or support extraction. It fails closed at 5 seconds/512 MiB per
row and 15 seconds outer. Survival requires a nontrivial certified fix-outside
class and a strict quotient rule-template decrease on at least one row. Exact
raw state counts and unceiled decision reduction include size-2-class credit;
shape predicts no wall-clock speedup.

Only both committed gate passes can authorize the separately committed one-row
Clingo-vs-same-Clingo diagnostic with 9-second internal/10-second outer caps,
jobs 1, first-candidate falsification, then exactly `B1,Q1,B2,Q2,B3,Q3`, and
real-worker profiling on a miss. It remains triage evidence. No production
route/encoding is authorized before a later full-experiment preregistration.

Usage remains **6 / 8 triage probes** and **0 / 3 full experiments**. Probe 8
is preregistered and **not consumed**; campaign kill has not fired. Failure ends
this last quotient family and leads to final synthesis without redefining the
class/lift or widening to SCC, backdoor, support, portfolio, or another family.

### Round 1 — Probe 8 Gate A semantic contract: PASS — 2026-07-11

The Gate A diagnostic/reference was implemented test-first. The exact focused
command was first red because the independent reference module did not exist,
then passed all 15 tests in 22.16 seconds under the frozen 60-second timeout
and a hard 512 MiB process-memory cap. The contract contains exactly the 12
frozen named fixtures and exactly 300 deterministic seed-`2026071108`
Hypothesis examples with `deadline=None`.

The complete normalized serialization retains assumption/non-assumption
literal colors, distinct rule nodes, and contrary/head/body/factual
incidences. Every class pair is independently certified as a full
fix-outside transposition from that serialization. Near clones and the
attacker-matched entangled A/B classes are rejected. The bounded reference
constructs preferred quotient states without either comparison oracle, lifts
every multiplicity state to its complete concrete orbit, and matches the full
preferred family from both native and support authorities. Size-2 and size-3
classes and nontrivial `k=1`/`k=2` size-3 expansions are nonvacuous.

Existing ABA semantic/SCC gates passed 24 tests in 3.40 seconds; the unchanged
Probe 6 bounded gate passed 15 tests in 61.76 seconds with observed-runtime
slack. No semantic counterexample appeared. No ICCMA row/corpus file, solver,
benchmark, production source/routing/encoding, or holdout was accessed.

Verdict: **GATE A PASS**. Gate B is authorized from the committed Gate A slice
but has not started. Probe usage remains **6 / 8 triage probes** and **0 / 3
full experiments**; Probe 8 is still **not consumed**. First permitted-row
access in Gate B will consume it.

### Round 1 — Probe 8 Gate B structural shape: FAIL-CLOSED — 2026-07-11

The diagnostic-only Gate B script was developed against five synthetic tests
before corpus access. It uses deterministic color refinement only to propose
candidate buckets, calls the committed Gate A complete-framework fix-outside
verifier for every candidate transposition, revalidates every emitted
certificate, retains exact multiplicities in quotient rule templates, and
computes unceiled multiplicity-state reduction including size-2 credit.

A direct-file module-resolution error occurred before any corpus open and did
not consume the probe. After the entrypoint and focused tests passed, the first
actual permitted-row access consumed Probe 8. The
`aba_2000_0.3_10_10_0.aba` worker emitted no parseable telemetry before its
frozen 5.0-second wall timeout. The row was not retried. Since any timeout makes
Gate B irreversibly red, `aba_2000_0.3_10_10_1.aba` was not opened and is
explicitly recorded as not accessed. Unavailable hashes/counts/certificates are
`null` in the artifact rather than invented.

Verdict: **GATE B FAIL-CLOSED: ROW WALL TIMEOUT**. This is not a structural-kill
claim because the intended invariant was not observed either way. There is no
selected row, shape predicts no speedup, and no solver diagnostic or profile is
authorized. No solver/support enumeration, preferred computation, production
source/routing/encoding, other dev/SE-ST row, full population, or holdout was
opened. Usage is **7 / 8 triage probes** and **0 / 3 full experiments**. Probe 8
was the last selected quotient family; the campaign now goes to final synthesis
without retrying or widening the family.

---

## Related standalone measurement (not part of this campaign or its budget)

- **2026-07-17 realistic-budget census** — `experiments/2026-07-17-realistic-budget-census.md`.
  A separate truth-measurement (not a campaign hypothesis): reruns a frozen
  stratified sample of ICCMA-2025 timeout rows at 600 s to split budget
  artifacts from algorithmic hardness, and rechecks this campaign's 2026-07-11
  Probe 1–8 kills (which ran at a 5–10 s row wall on the 600-assumption
  `aba_2000_0.3_10_10_{0,1}.aba` dev shapes) at 600 s. See that record for the
  probe-recheck verdict bearing on Probes N1/R1-P3/8.
