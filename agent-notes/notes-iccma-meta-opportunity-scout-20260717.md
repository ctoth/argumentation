# ICCMA meta-opportunity scout — unexecuted improvement inventory — 2026-07-17

Read-only survey. Every claim cites a file/line or commit. Prior-art gate
(AGENTS.md) respected: each proposed candidate is checked against the
failed-candidate records and the killing record is named for each dead one.

## 1. 2026-07-01 ranked strategy items 1–8 — executed? outcome? open?

Verdict source per item is cited. "ON MAIN" verified by
`git merge-base --is-ancestor`/`git log main`.

| # | Item (2026-07-01) | Status | Outcome | Evidence |
|---|---|---|---|---|
| 1 | AF DS-PR via CDAS (Thimm 2021); wire grounded-reduct+SCC preproc | **EXECUTED, GO, ON MAIN** (`934d998`) | Variant B (remove `_grow_preferred` maximisation) = +6 solved / −6 timeout on the 964-row DS-PR slice, −1.66% time, 0 losses, 0 answer changes. Variant A (stronger blocking) proven **vacuous** — paper clause already implemented. | `experiments/2026-07-02-af-dspr-cdas-blocking.md` |
| 2 | Z3 per-check timeout + failover (also fixes silent-wrong-answer) | **EXECUTED, GO, ON MAIN** (`4d2278f`) | Robustness, not speed. Closes the `unknown→negative` correctness hazard on the whole AF SAT path; default `budget=None` bit-identical (235=235 solved, +0.96% noise). | `experiments/2026-07-02-af-z3-check-budget.md` |
| 3 | AF SST/STG: Pu range-vector + CEGARTIX loops | **EXECUTED, GO, ON MAIN** (`39f6acc`) | Range encoding was *already* Pu 2017's `r=x+R⁺(x)`; added two Dvořák-2014 fragment shortcuts (stable-first + acyclic). +2 SST solved, −3.89% time, 0 losses. | `experiments/2026-07-02-af-sststg-shortcuts.md` |
| 4 | ABA mid-size: lower/lazy support-completion gate | **EXECUTED, GO, ON MAIN** (`23c6856`) | Not a "gate" — fixed the exponential `_minimal_supports` enumeration (`aba_support_model.py`) to a polynomial closure fixpoint at *two* call sites. +16 SE-ST solved (incl. the named `aba_2000_0.1_5_5_{1,6}` frontier cells: 15s TO → 0.7s), 0 losses, −10.29% time. | `experiments/2026-07-08-aba-simplify-stable-budget.md` |
| 5 | ABA DC-CO acyc: promote external 100ba-acyc or port propagator | **OPEN / UNPROMOTED** | (a) External `exp/iccma-aba-dcco-100ba-acyc` = +47 commits, **never merged**; DC-CO stocktake says "do not tune DC-CO yet" (`experiments/2026-06-29-iccma-uncapped-aba-dcco-profile.md`, diagnosis-incomplete). (b) Native lazy-CNF port = recorded **NO-GO** (IPASIR-UP correct but ~4× too slow, Python callback). (c) A related eager arc-acyclic STABLE port was done (`exp/abcgen-arc-acyc`): SE-PR c25 flipped 280.7s→56s, **recommend-promotion but NOT on main**; c35 giant-SCC single-solve wall (522s) unsolved. | `experiments/2026-07-09-abcgen-arc-acyc.md`; INDEX ledger row D1 |
| 6 | EE query-driven SCC pruning (`scc_recursive.py:41`) | **PARTIAL** | AF **acceptance** DC/DS *was* routed through the query's SCC ancestor cone (`11629eb` ON MAIN, `src/argumentation/solving/af_scc_cone.py`): 5/7 frontier cells flipped. But **EE enumeration** SCC pruning is still deferred — `scc_recursive.py` DC/DS still routes through full enumeration ("query-driven pruning deferred", UNRESOLVED item #2). The two biggest DS-PR crusti cones still TO on Python clause-construction. | `experiments/2026-07-10-af-scc-acceptance.md`; `src/argumentation/core/scc_recursive.py:41` |
| 7 | SETAF: candidate cap now; SAT encoding later | **NOT EXECUTED** | No SETAF experiment record exists (`ls experiments | grep setaf` empty). Uncapped 2^n brute force + unused symmetric/kernel preprocessing still stand (per 2026-07-01 arch-scout). | (absence of record) |
| 8 | Fetch mu-toksia + ICCMA system-description papers | **DONE** | `papers/Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner` (pdf+notes, no pngs), `papers/Mailly_2023_CrustabriRustArgumentationReasoner` (ICCMA23), `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT` (pngs present). | `papers/` listing |
| — | 2015/2021 tracks never executed (coverage gap) | **OPEN** | No evidence of wiring since 2026-07-01. | (per runs-analyst 2026-07-01) |

Net: items 1–4 landed and stuck (all four are pure wins on main). Item 8 done.
Items 5, 6, 7 and the 2015/2021 coverage gap remain open; item 6 is half-done
(acceptance yes, enumeration no).

## 2. Ranked UNTRIED technique candidates

Each: paper anchor + open bottleneck it targets + why the prior records do NOT
kill it. Ranked by expected value.

### A. Incremental persistent-SAT substrate for AF CDAS DS-PR (single CaDiCaL, solve-under-assumptions)
- **Anchor:** Niskanen 2020 mu-toksia (`papers/Niskanen_2020_MuToksia…`) — one
  SAT solver instantiated once, every task driven by incremental
  solve-under-assumptions against one persistent clause DB; Mailly 2023
  Crustabri (same persistent-state pattern); aba-next queue items #3/#4.
- **Bottleneck:** the two biggest DS-PR crusti cones (`crusti_g2io_175/225`)
  still time out *after* the SCC-cone win — the profile is now **Python-API
  clause construction, not SAT search**: CDAS rebuilds three Z3 kernels
  (~62 s) on the 92k-attack cone before the loop starts
  (`experiments/2026-07-10-af-scc-acceptance.md`, "next wall" §Interpretation).
- **Why not killed:** the AF SAT path has *never* had a persistent/incremental
  substrate; today it rebuilds kernels per solver object. The one CaDiCaL probe
  (Probe 7) was blocked on an unrelated IPASIR `val()`/statistic **API
  capability** quirk on the *ABA eager-arc* CNF, not on the incremental-SAT idea
  for AF (`experiments/2026-07-11-iccma2023-probe-7-cadical221-eager-arc.md`).
  Named explicitly as follow-up (a) by both the SCC-cone and af-dspr records.
  **Highest value: attacks the top open AF bottleneck with a precise cost model
  already in hand.**

### B. Z3 `Tactic('sat')` CDCL core on the FLAT AF acceptance paths
- **Anchor:** empirical finding inside `experiments/2026-07-10-af-scc-acceptance.md`
  — default Z3 SMT core was 165× slower than the CDCL sat core on the crusti_175
  cone (`require_in` complete-labelling: 265 s → 1.6 s).
- **Bottleneck:** single-SCC ER family (ER_300 DS-PR/DS-SST) where the cone =
  whole graph so the cone routing never fires; these were explicitly out of
  scope of the cone experiment.
- **Why not killed:** the sat-core engine is currently wired **only** on the
  cone path; extending it to the flat finders is untried and is named follow-up
  (b) in that record. Cheap, answer-preserving (same formula, different decision
  procedure). Risk noted: non-incremental sat-core hurt tiny CDAS loops
  (`BA_160_80_2`), so gate it on size — a solved constraint, not a blocker.

### C. Niskanen 2025 SAT-VE (vertex-elimination) acyclicity encoding for ABA stable/preferred
- **Anchor:** `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT`
  (pngs present) — SAT-VE and SAT-UFS "match or beat ASPforABA on ICCMA23,
  including ~50% more solved on the ideal task."
- **Bottleneck:** the abcgen c35 giant-SCC **single hard CDCL solve** (522 s)
  that the eager arc-acyclic port could not break
  (`experiments/2026-07-09-abcgen-arc-acyc.md`); the abcgen SE-ST/SE-PR family
  is the largest remaining ABA timeout mass.
- **Why not killed:** the repo implemented the *arc/level-based* acyclicity
  variant (aba_sat.py eager-arc) — **not** SAT-VE. Critically, SAT-VE is a
  **static clause encoding**, so the recorded cause of death for the propagator
  routes — IPASIR-UP Python-callback overhead ~3.36–4× too slow
  (`notes/aba-completion-sat-bottleneck-2026-05-20.md`; D1 lazy-CNF NO-GO) —
  **does not apply to SAT-VE**. SAT-UFS *does* use a propagator and would hit
  that wall, so SAT-VE is the surviving variant.

### D. CDIS ideal-extension algorithm for SE-ID / DC-ID (Thimm 2021)
- **Anchor:** `papers/Thimm_2021_SkepticalReasoningPreferredSemantics` — same
  paper as item 1; CDIS derives ideal from preferred-super-core pruning.
- **Bottleneck:** SE-ID/DC-ID had 35% timeout rate (runs-analyst 2026-07-01),
  untouched.
- **Why not killed:** item 1 executed **only CDAS (DS-PR)**; the ideal path was
  never given the CDIS treatment. No record attempts it. The super-core
  machinery CDIS needs already exists in `af_sat.py`
  (`PreferredSuperCoreSolver`).

### E. AF EE (enumeration) query-driven SCC pruning / condensation ordering
- **Anchor:** Baroni 2005 SCC-recursiveness
  (`papers/Baroni_2005_SCC-recursiveness…`); aba-next queue item #6.
- **Bottleneck:** EE-CO/PR/ST brute 2^n per SCC with a 65,536 budget →
  `ExactEnumerationExceeded` for SCC>16 args (arch-scout 2026-07-01;
  `scc_recursive._base_solve`).
- **Why not killed:** the 2026-07-10 cone work covers **acceptance (DC/DS)**
  only; enumeration tasks still route through full enumeration
  (`scc_recursive.py:41` "query-driven pruning deferred"). The 2^16 subset cliff
  is real and unaddressed for EE. Lower rank because EE is a smaller slice of the
  timeout mass than A/B.

### F. SETAF SAT encoding + symmetric/kernel preprocessing
- **Anchor:** aba-next portfolio; SETAF track. `setaf.py` uncapped 2^n brute
  force; symmetric-AF poly case + kernels detected but unused
  (`preprocessing.py`, arch-scout 2026-07-01).
- **Why not killed:** no SETAF experiment ever run (§1 item 7). Genuinely
  greenfield. Lower rank: SETAF is a small ICCMA track.

### G. (Speculative) Tree-decomposition DP for ABA — Popescu 2023
- **Anchor:** `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions`;
  aba-next items #7/#8.
- **Bottleneck:** dense ABA preferred class (T1/T3/T5/T6).
- **Why weak, not dead:** never executed, but hard rows have giant derivation
  SCCs (`scc_max_size=157`, `p_acyclic=False`;
  `notes/aba-completion-sat-bottleneck-2026-05-20.md`), so measured width is
  likely too high to pay off. Requires a **shape-telemetry pass first** (queue's
  own suggested order step 4) before any DP implementation — do not code blind.

## 3. DEAD candidates — do NOT retry (killing record named)

| Candidate | Cause of death | Killing record |
|---|---|---|
| ABA global ASP max-cardinality over complete extensions (SE-PR, queue #12) | T1/T3/T5/T6/T8 timed out on auto/asp/sat after `#maximize` proved-optimum | branch `experiment/aba-asp-saturation-preferred` `408f4b0`; INDEX row H3-S1 |
| ABA stable-only deletion (delete complete/undefeated layer, SE-ST, queue #10-ish) | 0/5 solved; real-worker profile unchanged, still `clingo.Control.solve`-bound | `experiments/2026-05-21-aba-se-st-direct-stable-encoding.md` (`4b6ee26` abandoned) |
| ABA collective-attack SCC conditioning (queue #6) | Operationally killed — eager `_minimal_supports` blow-up runs *before* the 4,096 cap can bind; 13 min, no first extraction | Probe 5, `experiments/2026-07-11-iccma2023-probe-5-scc-operational-measurement.md` |
| ABA backdoor/cutset conditioning (queue #5) | Semantic kill — frozen `two_component_cut_attack_union` fixture is **not a separator** (a,b stay joined via shared `contrary(k)` literal) | Probe 6, `experiments/2026-07-11-iccma2023-probe-6-backdoor-semantic-contract.md` |
| ABA true-clone/module quotient (queue #9) | Gate A passed; Gate B fail-closed (row wall timeout, no telemetry). Family closed, but **not a clean structural kill** — invariant never observed | Probe 8, `experiments/2026-07-11-iccma2023-probe-8-multiplicity-true-clone-quotient.md` |
| Native lazy-CNF acyc port for ABA DC-CO | NO-GO: IPASIR-UP propagator correct but ~4× too slow (Python callback) | D1 branch note; 2026-07-01 notes-scout |
| ABA level-mapping / SCC-local founded levels / static SCC preload / projection / greedy seeds / IPASIR-UP observe-all / support-core reduction / inprocessing | All tried and reverted (regressed the focused gate) | `notes/aba-completion-sat-bottleneck-2026-05-20.md` (28-experiment sweep) |
| Clingo built-in config sweep (handy/crafty/trendy) for SE-PR | No arm cleared ≤8s median / <9s every-run; fastest `trendy` 9.759s | Probe 2, `experiments/2026-07-11-iccma2023-clingo-config-triage.md` |
| Stable-first shortcut for ABA SE-PR | Capped stable query returns no witness → cannot produce a preferred witness | Probe 1, INDEX row R1-P1 |
| ABA-600 direct-SAT stable route beats Clingo (N1) | Bottleneck *moved* (Clingo-solve → `_add_ranked_closure_constraints`), did not shrink | `experiments/2026-07-11-iccma2023-aba-600-stable-sat-route.md` |
| ABA stable base-UNSAT precheck (N2) | Base is UNSAT but the proof took 46.12s — cannot front a 5s worker | `experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md` |
| ABA support-free/core-fact preprocessing (SE-ST/SE-PR) | Already the production path; grounded reduct fixes 0/600 assumptions on hard rows | Probe 3, `experiments/2026-07-11-iccma2023-support-free-core-fact-preprocessing.md` |
| ABA SE-PR CEGAR re-grounding churn | Only 3 refinement samples vs 928 solve samples — churn is not the bottleneck | Probe 4, `experiments/2026-07-11-iccma2023-cegar-regrounding-churn-triage.md` |
| Direct CaDiCaL 2.2.1 on eager-arc CNF (queue #4, partial) | Blocked before probe on IPASIR `val()`/statistic API capability — **NOT a kill of the incremental-SAT idea** (see candidate A) | Probe 7, `experiments/2026-07-11-iccma2023-probe-7-cadical221-eager-arc.md` |

## 4. Load-bearing caveat for whoever picks a candidate (prior-art gate)

The entire 2026-07-11 iccma2023 campaign (Probes 1–8, dead rows above) ran at a
**5–10s per-row budget** on the `aba_2000_0.3` 600-assumption SE-PR/SE-ST shape.
`notes/aba-completion-sat-bottleneck-2026-05-20.md` proves that shape family
solves in **84s (clingo) / 104–152s (native)** and the real ICCMA budget is
**1200s** — so several of those "kills" are **budget artifacts**, not true dead
ends. A candidate targeting that exact shape at a realistic (≥120s) budget is
**not** killed by the 5s-cap probes; re-check the budget before citing a Probe
1–8 record as the cause of death. This is the streetlight/phantom-trap pattern
the 2026-05-20 correction documents (the "never terminates" conclusion was a
truncated-profile artifact).

## Selection recommendation (not authorization)

If one candidate is to be run next, **A (incremental persistent-SAT substrate
for AF CDAS DS-PR)** has the best evidence: it targets the single largest
*confirmed-open* AF bottleneck (crusti DS-PR), the cost model is already
measured (~62s in kernel rebuilds), the paper substrate is in-repo (mu-toksia,
Crustabri), and no record kills it. **B (sat-core on flat AF paths)** is the
cheapest and is a near-free companion. Per AGENTS.md, candidate selection
requires a written prior-art search record first and `protocols:campaign` (more
than one plausible hypothesis competes).
