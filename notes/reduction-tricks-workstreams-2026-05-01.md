# Reduction-tricks workstream research — checkpoint 2026-05-01

## State

Master report and four supporting reports complete and in `reports/`:
- `reduction-tricks-2026-05-01.md` (synthesis, ~10-trick catalog)
- `reduction-targets-catalog.md`
- `encoding-preconditions.md`
- `argumentation-reductions-anchor.md`
- `why-bounded-catalog.md`

§7 of the master flagged three unused-but-ripe tricks for this codebase:
1. DG-style treewidth-aware encoding (Fichte 2021, Mahmood 2025)
2. ASP backend for ABA+ / preferential ABA (Lehtonen 2020/2024)
3. Datalog-style grounding for first-order ABA (Diller 2025)

## Current task

Q asked for a research agent per item, producing workstream-design reports
in `reports/`. For the Datalog one, target `../gunray` as the Datalog
engine (gunray = pure-Python defeasible logic engine with stratified
Datalog `SemiNaiveEvaluator` in `src/gunray/evaluator.py`).

## Observed about codebase

`src/argumentation/` has aba.py, aba_sat.py, aspic.py, aspic_encoding.py,
plus 25+ other modules (dung, adf, bipolar, caf, gradual, equational,
probabilistic, dynamic, enforcement, etc.). The SAT machinery for ABA
lives in `aba_sat.py`. ASPIC support exists in `aspic.py` /
`aspic_encoding.py`.

Gunray confirmed as: defeasible-logic engine, MIT, Python 3.11+, DeLP
pipeline + stratified Datalog (semi-naive) + KLM closure. Strict-only
fast path routes degenerate defeasible theories to the Datalog engine.

## Next

Dispatch three researchers in parallel. Each produces a workstream report
in `reports/workstream-{name}.md`. After all return, present to Q for
selection of which workstream to prosecute.

## Blocker

None.

## Update — all three workstream reports complete

Files in `reports/`:
- `workstream-dg-treewidth.md` — 3526 words, 6 phases (0–5). Existing
  `probabilistic_treedecomp.py` dataclasses lift in. Phase 3 (ABA-DG) is
  novel research — no literature, may fail if assumption-attack primal
  graphs are inherently wide.
- `workstream-asp-backend.md` — 3516 words, 6 phases, ~11.5 eng-days.
  Half built already: `solver_adapters/clingo.py` driver exists,
  `solve_aspic_with_backend(backend="clingo", semantics="grounded")`
  wired up but emits facts only, no `.lp` rules bundled, tests
  monkeypatch subprocess. Reference `.dl` files sit in
  `scratch/sources/aspforaba/aspforaba/encodings/`.
- `workstream-datalog-grounding.md` — 4795 words, 6 phases. `argumentation`
  is propositional only (verified via grep). Author already cites Diller
  2025 in `aspic.py:GroundAtom` docstring. gunray already has
  conservative T2 (Diller Def 9 / Algo 2) but NOT non-approximated-
  predicate detection (Def 12 — the engineering payoff). Architecture A
  (loose coupling via `Program` + `SemiNaiveEvaluator`) recommended over
  routing through DeLP `DefeasibleTheory`.

Q's response: doing all three. Asked me to "hit me with questions" —
extract the §5/§6 decision points from each report into a single
consolidated decision sheet for Q to answer in one pass before any
workstream begins.

Decision points extracted (15 total: 5 DG + 5 ASP + 5 Datalog).
Consolidating into the response now.

## Update — Q answered all 15 decisions; updating workstream reports

Decisions (full set in `reports/workstream-decisions-2026-05-01.md`):
Q1 yes / Q2 symmetric / Q3 keyword dispatch / Q4 Architecture A
(needs more research) / Q5 upstream in gunray / Q6 model counting yes
/ Q7 ABA-DG keep / Q8 success bar (c) / Q9 hard fail / Q10 post-hoc
build_arguments_for / Q11 Phase 1 / Q12 include external / Q13 add
pysat / Q14 add htd / Q15 serial ASP→Datalog→DG.

## Editing progress

ASP report (`workstream-asp-backend.md`) — DONE:
- Phase 0 backend abstraction → keyword dispatch (Q3)
- Phase 0 add clingo to dev group (Q2 symmetric CI)
- Phase 0 includes real-clingo smoke test as gating step
- Phase 2 Q10 risk → flipped to option A (post-hoc build_arguments_for)
- Phase 4 expanded for external systems (ASPforABA, ASPforASPIC,
  TOAST, ANGRY, ICCMA 2023 instances)
- Phase totals updated: 13.5-15.5 days
- §6 Open questions → §6 Decisions (resolved 2026-05-01)
- Noted runs first per Q15

Datalog report (`workstream-datalog-grounding.md`) — IN PROGRESS:
- §4 architectural posture preamble added (Q4, Q5, Q11, Q15)
- Phase 0 expanded with Q4 research subagent dispatch + CI symmetry
- Phase 1 elevated preference plumbing to deliverable (Q11)
- Phase 3 split into Phase 3a (upstream gunray NAP) + Phase 3b
  (consume in argumentation) per Q5
- STILL TO DO: Phase 5 external benchmarks promote from stretch to
  required (Q12); update phase totals; replace §6 with Decisions

DG report (`workstream-dg-treewidth.md`) — NOT YET STARTED:
- Need to: bake Q3 keyword dispatch, Q6 keep counting, Q7 keep ABA-DG,
  Q8 success bar (c), Q12 external benchmarks, Q13 pysat optional,
  Q14 htd optional. Replace §5 Open questions with Decisions section.

## Blocker

None. Continuing edits.

## Update — Q said "look at the log silly"

Found `logs/` dir (NOT `out/` — `out` is a file). Contains:
- `baseline-pre-ws-o-arg-vaf-ranking.log` (Apr 28 17:34, 9384 bytes)
- `post-ws-o-arg-vaf-ranking.log` (Apr 28 18:05, 9384 bytes)
- `post-ws-o-arg-vaf-ranking-axioms.log` (Apr 28 18:26, 4639 bytes)

So Q has prior workstream practice: `baseline-pre-ws-{X}` and
`post-ws-{X}` test logs captured around each workstream. Naming
suggests "ws-o" = workstream O (15th letter — they've done at least
14 prior workstreams). Q was telling me there's established practice
I should adopt for the upcoming ws (likely "ws-p" for ASP backend?).

Also baseline log shows **the test suite is timing out today** (line
24: pytest hits timeout during `test_aspic.py`). 410 tests collected.
This means baseline-on-clean-master is NOT clean. Per CLAUDE.md
"Before starting work on any project with tests, run the full suite
on clean master and establish a baseline. `DID NOT RUN` → cannot
mark complete." We have a broken baseline in the repo and I haven't
acknowledged it.

## Implications for the current claim that "we're well-positioned"

I claimed zero code edits and ready-to-build. But:
1. There's existing workstream-tracking practice (logs/) I ignored
2. The test baseline is timing out — needs investigation before any
   workstream begins
3. Q is gently pointing out I should be reading the log discipline
   that already exists, not inventing new structure

