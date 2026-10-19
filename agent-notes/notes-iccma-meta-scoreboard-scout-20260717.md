# ICCMA Meta-Scoreboard Scout — 2026-07-17 (FINAL)

## 1. HEADLINE / SCOREBOARD NUMBERS
- **Full-corpus truth run (2026-05-14)** `iccma-2025-full-uncapped-auto-t5`: **4243 solved / 1871 timeout**
  / 1280 skipped / 7394 total.
  `data/iccma/2025/runs/iccma-2025-full-uncapped-auto-t5-2026-05-14-summary.json`.
  This is still the newest full-corpus census. NO comparable full re-run has been done after the
  July landings — the 4243 number has NOT been re-measured, so cumulative solved gains are inferred
  from slice/frontier evidence, not a fresh census.
- **Frontier-v1 scoreboard: 18 solved / 12 timeout of 30** (was 9/30 at baseline 2026-07-07).
  Measured on label `frontier-v1-post-6a-parallel`, --jobs 8, t=120s.
  `experiments/2026-07-10-frontier-parallel.md:36-47`.
  Manifest `tests/manifests/iccma2025-frontier-v1.json` (30 rows; classes 21 hard / 4 boundary_melt / 5 melt).
  CAVEAT (`experiments/2026-07-07-frontier-v1-baseline.md:17-19`): 30 of the 1871 timeout rows, stratified
  probe not a census.
- Foreman ledger (`notes-iccma-campaign-log-2026-07-02.md:36`): DS-PR 229→235, SST 576→578, SE-ST 217→241, Frontier 9→18/30.

## 2. EXPERIMENTS SINCE 2026-07-01
| Experiment (record) | Hypothesis | Verdict | Landed? | Evidence |
|---|---|---|---|---|
| aba-sest-clingo-route (2026-07-07) | route sparse-narrow SE-ST to clingo | PROMOTE, +10 SE-ST solved | YES (exp/aba-sest-clingo-route merged) | `experiments/2026-07-07-aba-sest-clingo-route.md` |
| aba-simplify-stable-budget (2026-07-08) | fix simplify_aba exp blow-up | PROMOTE, +16 SE-ST solved, 2 frontier flips | YES (merged) | `experiments/2026-07-08-aba-simplify-stable-budget.md` |
| abcgen-arc-acyc (2026-07-09) | eager arc-acyclic foundedness, kill CEGAR | PROMOTE, c25 5x, SE-PR c25 frontier flip | YES (merged) | `experiments/2026-07-09-abcgen-arc-acyc.md` |
| af-scc-acceptance (2026-07-10) | SCC-cone acceptance routing DS-PR/DC-CO | GO, 5/7 frontier flips | YES (integrate/af-scc-acceptance merged; exp/ branch +7 docs only) | `experiments/2026-07-10-af-scc-acceptance.md` |
| frontier-parallel + runner --jobs (2026-07-10) | parallelize sweep | 50min→5.1min, byte-identical | YES (merged) | `experiments/2026-07-10-frontier-parallel.md` |
| aba-satve (2026-07-10) | SAT-VE acyclicity beats arc on c35 | **NO-GO for routing** (VE worse/equal; c35 wall is CDCL instance-scale hardness, encoding lever exhausted) | NO (exp/aba-satve +3, kept selectable, default unchanged) | `git show exp/aba-satve:experiments/2026-07-10-aba-satve.md`; summaries 245→247 solved |
| af-satcore-flat (2026-07-10) | sat-core vs smt on flat AF paths | **INCOMPLETE** — only probe/preregistration committed, Decision "TO BE FILLED" | NO (exp/af-satcore-flat +1) | `git show exp/af-satcore-flat:experiments/2026-07-10-af-satcore-flat.md` |
| aba-sest-clingo-route-v2 | follow-up routing | in-flight | NO (+2) | branch only |
| ICCMA 2023 ABA campaign Probes 1–8 (2026-07-11) | 8 triage hypotheses on 24-row dev frame | ALL NEGATIVE/KILLED (see §4) | n/a (triage, no source change) | `experiments/INDEX.md` |

## 3. REMAINING HARD FAMILIES + diagnosis on record
- **crusti DS-PR x2** (crusti_g2io_175_0.2_511_18, crusti_g2io_225_0.2_127_42) — needs shared-kernel/direct-CNF
  CDAS substrate (`2026-07-10-af-scc-acceptance.md` follow-up (a)).
- **DS-ST crusti x2** — "new idea needed" (foreman ledger).
- **ER x2** (ER DS-SST / ER DS-PR family, e.g. ER_400_60_3, ER_300_50_8) — direct-CNF CDAS candidate; was 7A target.
- **abcgen c35 x2** (SE-ST + SE-PR) — single-solve CDCL instance-scale hardness; giant-SCC 522s clingo solve.
  Diagnosis: NOT the acyclicity encoding (arc≈VE within 10%). Needs SCC-decomposition / cutset preprocessing
  (queue items 5 & 9) or CaDiCaL 2.x direct engine (`aba-satve` record rec 3).
- **abcgen c25 SE-ST** — routing gate misfires: abcgen-shaped (sparse-narrow, density≤25, cycle-heavy) rows route
  to clingo which also times out; needs a native-stable routing gate (`2026-07-09-abcgen-arc-acyc.md` follow-up (a)).
- **scc family** — "none left" (foreman); marginal scc_3605 cone shrink is a minor follow-up.
- Frontier still has 12/30 timeouts: 9 remaining hard cells + boundary rows not yet flipped.

## 4. ABA 2023 24-row campaign — DEAD-ENDED (experiments/INDEX.md)
Baseline 21/24 dev solved @ 5f75a7c. Budget 7/8 triage probes, 0/3 full experiments. Kill criteria met → final synthesis.
All eight probes failed: P1 stable-first (no witness); P2 Clingo config (no arm <8s); P3 support-free (already prod path);
P4 CEGAR churn (not bottleneck, 928 samples in clingo.solve); P5 SCC conditioning (operational no-go, eager
_minimal_supports hang ~13min); P6 backdoor/cutset (semantic kill, frozen fixture is non-separator);
P7 CaDiCaL 2.2.1 (blocked, API capability absent: restarts=-1, val() same sign — probe NOT consumed);
P8 true-clone quotient (Gate A pass, Gate B fail-closed at 5s row wall). Earlier N1 SAT route neg, N2 base-UNSAT 46s precheck neg.

## 5. IN-FLIGHT / HALF-DONE
- **Uncommitted working tree**: AGENTS.md modified (unstaged); `tests/structured/aba/test_aba_cadical2_eager_arc_contract.py`
  DELETED and staged (Probe 7 red-contract cleanup). Dozens of untracked notes-*.md / logs/*.log agent-state files (not code).
- **Unmerged solver branches**: exp/aba-satve (+3, NO-GO but keeps selectable encoding), exp/af-satcore-flat (+1, probe only,
  verdict unfilled), exp/aba-sest-clingo-route-v2 (+2), exp/af-scc-acceptance (+7, docs past merged integrate/).
- **D1 exp/iccma-aba-dcco-100ba-acyc (+47, base 7bc7fb7)**: DC-CO route + acyc SAT propagator/lazy-CNF + 100ba-acyc backend.
  Never landed. Lazy-CNF port is a recorded NO-GO (IPASIR-UP correct but ~4x too slow). Different task/slice.
- **Capstone branches** unmerged: capstone/iccma-conformance, experiment/iccma-capstone-deterministic-route{,-v2}.

## KEY JUDGMENT
Recent solver work landed a real cluster of ABA SE-ST/SE-PR + AF DS-PR/DC-CO gains (frontier 9→18/30) via
preprocessing fixes + routing gates + eager encodings. Both remaining live solver levers (SAT-VE, sat-core) stalled:
VE is a clean NO-GO, satcore is unfinished. The 24-row ABA-2023 side-campaign is fully dead-ended. The next real gains
require NEW mechanisms on the named hard families (direct-CNF CDAS for crusti/ER; SCC-decomposition/cutset or CaDiCaL-2.x
direct engine for abcgen c35), and a fresh full-corpus census to convert frontier flips into a real 4243→? number.
