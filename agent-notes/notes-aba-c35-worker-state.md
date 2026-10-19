# ABA c35 lane worker — state

Branch: `exp/aba-c35-lane` (base f4b8eac = main). Isolated worktree at
`C:\Users\Q\code\aba-c35-lane-wt` (shared checkout is on another worker's
branch; do NOT switch branches in the shared checkout). Ward: experiment.

## STEP 0 — ADJUDICATION: DONE (commit 154ef61)
Record: `experiments/2026-07-17-aba-c35-lane-adjudication.md`.
Verdict: **CaDiCaL-2.x direct engine SURVIVES**; SAT-VE static encoding DEAD;
SCC-decomposition/cutset DEAD.
- SAT-VE: opportunity scout WRONG ("untried") — 6844d0d derived + 39feffe
  implemented the paper's Sec 3.2 VE; 777c5ea measured NO-GO (arc≈VE within 10%
  on c35). Encoding lever exhausted. Ineligible (nothing changed).
- Probe 5 (SCC): support-enum blowup structural kill. Probe 6 (cutset): semantic
  separator kill (ABA shared-contrary incidence). Both apply to c35. Ineligible.
- CaDiCaL survives: paper ran ALL SAT variants incl eager SAT-VE on CaDiCaL
  2.1.3 (p.713); SAT-VE/SAT-UFS beat ASPforABA on c25/30/35 CLUSTERED (p.714).
  Repo NO-GO changed the ENCODING but held ENGINE at glucose4. Probe 7 block =
  preregistration artifact (restarts stat + wrong val assertion), not merit;
  never ran on c35.

## STEP 1 — CaDiCaL 2.x vs glucose4 on identical c35 eager-arc DIMACS
Plan:
1. Preregister contracts (corrected telemetry: 3 native stats, IPASIR val).
2. Triage: export c35 SE-ST eager-arc CNF to DIMACS; run glucose4 vs cadical.exe
   on byte-identical DIMACS at a cap; py-spy on real child. Gate = flip at t120
   OR strictly-later stage / profiled dominant-cost shift.
3. If survives triage: dev-slice (c35 rows + no-regress c25 + ABA property
   suite + full pytest) -> GO/NO-GO record + INDEX.md.
Reuse Probe 7 CaDiCaL 2.2.1 build (rel-2.2.1 / 4198d817) + drat-trim if still on
disk under %TEMP%\argumentation-probe7-cadical221-*.

OPEN RISK: c35 SE-ST may be SAT (extension exists), paper's biggest CaDiCaL
margin is on UNSAT. Triage must not assume UNSAT-shaped win.

## DIMACS export mechanism (confirmed)
- CaDiCaL 2.2.1 build SURVIVES: %TEMP%\argumentation-probe7-cadical221-20260711-a62b6c3
  \cadical\build\cadical.exe (+ drat-trim\drat-trim.exe). Reuse directly.
- `_NativeSparseNarrowStableSolver.__init__` (aba_sat.py:844) builds ALL clauses
  eagerly: `_add_completion_clauses` + `_add_arc_acyclic_clauses`, each via
  `_add_clause` -> `self.solver.add_clause(list[int])`. nvars = self._next_var-1.
- `stable_extension()` (line 1042) does `self.solver.solve(assumptions=...)`.
  NEED: confirm assumptions for the flat c35 SE-ST solve (expect [] or a small
  set) to fold into unit clauses for the DIMACS file.
- EXPORT PLAN: subclass/monkeypatch `_add_clause` to also append clause to a
  list; build solver on c35 instance; write DIMACS header `p cnf <nvars>
  <nclauses>` + clauses; append assumption literals as units. Run cadical.exe on
  it AND glucose4 (pysat) on the byte-identical file. Diagnostic script only,
  under scripts/ or scratchpad; no production edit.
- c35 instance: data/iccma/2025/extracted/instances/ABAs/
  abcgen_c35_atoms25_asms30_mra3_mbs2_cp0.8_ins2.aba (1050 asms).

## RESULTS (triage)
- Export: nvars=35098 nclauses=129983 build=0.54s
  dimacs_sha256=3f10968dfcdb0f678b51da85ecee85f90577112c12615d2dd5ee5b36c00aa6f4
- Fidelity (small aba_100_0.3_5_5_7): in-memory SAT == glucose SAT == cadical
  SAT. Export faithful.
- **CaDiCaL 2.2.1 on c35 DIMACS: SAT in 25.28s** (exit 10). conflicts=666525
  decisions=975395 props=89.0M restarts=19570. Model emitted (v lines).
- Recorded glucose4 in-memory baseline (WITH set_phases): 591.55s (arc). 
- glucose4-on-file (no phases) control: RUNNING (task blfw7kkgl, 650s cap).
- Prelim: cadical ~25s vs glucose ~592s = ~23x. Gate #1 (flip <=120s while
  glucose >120s) looks GO pending glucose-on-file control.
- NOTE: cadical ran WITHOUT set_phases (file has no phase directives); fair
  single-variable comparison needs glucose-on-file (also no phases) as control.
  A production routing expt would re-add phases for both.

Prohibitions honored: holdout sealed/untouched; heavy runs jobs 1-2; no main.

## FINAL (2026-07-17) — DONE
glucose control: GLUCOSE_EXIT=124 = TIMEOUT >651s on byte-identical no-phase CNF.
CaDiCaL (rel-2.2.1) --jobs 1: c35_asms30 SAT 25.28s, c35_asms35 SAT 9.19s,
c25 SAT 24.44s. All models independently VALID. ABA suites 1409 passed (lone
fail = untracked paper png not in worktree, not a regression).
TRIAGE = GO (directional). Commits on exp/aba-c35-lane:
154ef61 adjudication, 4fd7a17 prereg, 97532fc GO record.
NOT promotion: needs structural safety predicate + no-loss fallback + real
incremental-CaDiCaL dependency. Recommend-only. Background/Monitor mechanism
DEAD (12h stall) — ran everything synchronously.

## WAVE 2 (2026-07-18) — productionize on flat stable path — IN PROGRESS
Branch exp/aba-cadical-engine-prod, worktree C:\Users\Q\code\aba-cadical-prod-wt off main.
TIMING DEFERRED ~90min (census priority). SYNCHRONOUS only (bg wakeups dead).
Dependency: no CaDiCaL 2.x wheel; pysat has cadical195(1.9.5, correctness OK) +
kissat404(SEGFAULTS=disqualified). Gate D0 (deferred) decides cadical195 vs
vendored 2.2.1 by whether 1.9.5 reproduces c35 win.
Prereg committed bcafe2e. Tests test_aba_stable_engine_routing.py = 7 RED, about
to commit RED then implement seam: _STABLE_ENGINE_STRONG, _stable_engine_for(),
engine= param, self.phase_vector, native_sparse_narrow_engine telemetry,
_stable_extension_with_fallback (glucose4 on strong-engine exception).
Seam: aba_sat.py line 868 (name=glucose4), move after 914; wire lines 140+159.
OUT OF SCOPE: prefsat CEGAR (456), SE-PR/DS-PR.
Feature data: c35_asms30 rec373/edg407/asm1050/rul30293 (glucose TO);
c35_asms35 rec281/edg290/asm1225/rul39164 (TO); c25 rec187/edg194/asm875/rul18132 (63s).

## WAVE 2 impl progress (checkpoint)
RED committed 5e28406. Solver edits DONE in aba_sat.py:
- __init__(framework,*,engine=None); removed early glucose4 instantiation;
- after edges telemetry: self.engine via _stable_engine_for (or override),
  telemetry native_sparse_narrow_engine, self.solver=solver_class(name=engine);
- self.phase_vector exposed + passed to set_phases.
STILL TODO: add module-level _STABLE_ENGINE_STRONG + _stable_engine_for +
_stable_extension_with_fallback (before line 133); wire call sites 140 + 159 to
the fallback wrapper. Then run tests green, then full ABA suite + pyright/ruff.
Timing still deferred.

## WAVE 2 — ruff-format hazard (avoided)
`ruff format` reformats the ENTIRE aba_sat.py (261/94) even on pristine main —
worktree venv's ruff version differs from what formatted main. DO NOT run
`ruff format` on the whole file (spurious global churn). ruff CHECK passes,
pyright 0 errors. Restored aba_sat.py to HEAD; re-applying only the 6 functional
edits by hand, matching existing style. Then run tests green (was 23 passed
before the format mishap) + full ABA suite. Timing still deferred.

## WAVE 2 — IMPL COMPLETE (holding for timing window)
Commits on exp/aba-cadical-engine-prod: bcafe2e prereg, 5e28406 RED, 21fe29f impl.
GREEN: 7 routing contracts + full ABA suite 1416 passed (1 pre-existing untracked
Cerutti png artifact, not a regression). ruff check + pyright clean. Diff 82/13.
Predicate verified on REAL frameworks (build-only, no timing): c35_asms30 ->
cadical195, c35_asms35 -> cadical195, c25 -> glucose4. Correct.
DEFERRED (await census-done from team-lead): D0 (cadical195 solves c35 CNF
<=120s & <=~76s) + dev slice (c35 flip, c25 no-regress, safety gate) + finalize
dependency (cadical195 vs vendored 2.2.1) + GO/NO-GO record + INDEX.
NOTHING running. All synchronous.
