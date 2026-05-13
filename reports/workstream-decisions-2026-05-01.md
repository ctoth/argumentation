# Workstream decisions — 2026-05-01

Q's answers to the consolidated 15-question decision sheet for the three
reduction-trick workstreams (ASP backend, Datalog grounding via gunray,
DG/treewidth encoding). Source questions live in conversation history and
in the §5/§6 sections of each workstream report.

## A. Dependency policy

- **Q1.** Three new optional extras OK, including `[grounding]` as `git+`
  install for gunray. → **Yes.**
- **Q2.** CI policy. → **Symmetric** — install `clingo`, `gunray`, and
  `htd` binary in CI alongside `z3-solver`.

## B. Architecture

- **Q3.** Backend abstraction depth. → **B** — widened keyword-string
  dispatch, no `Backend` Protocol. Smaller diff. Refactor to a Protocol
  later if a third backend forces it.
- **Q4.** gunray coupling shape. → **A** (loose: `gunray.Program` +
  `SemiNaiveEvaluator` only). **Caveat: Q wants more research before
  Datalog Phase 0 begins.** Does not block ASP. Action: research
  subagent on gunray's `Program` API surface area, breaking-change
  history, and whether DeLP-flavoured pieces leak through.
- **Q5.** Where Diller-Def-12 NAP analysis lives. → **Upstream in
  gunray.** Q controls both packages. Action: when Datalog workstream
  starts, spawn a parallel gunray-side workstream for the NAP
  implementation. Cross-repo PR cadence needs a plan.

## C. Scope cuts

- **Q6.** DG model counting (Phase 5). → **Yes.**
- **Q7.** ABA-DG (DG Phase 3, the novel-research phase). → **Keep.**
- **Q8.** DG success bar. → **(c)** — full Phases 0–5. DG encoding +
  benchmark win on at least one realistic instance class + model
  counting works.
- **Q9.** ASP weakest-link policy. → **Hard fail** with
  `unavailable_backend` when `pref.link == "weakest"` is requested.
- **Q10.** ASP `accepted_argument_ids` population. → **A** — populate
  via post-hoc `build_arguments_for`. Pay the materialisation cost to
  match the SAT backend's surface.
- **Q11.** Datalog Phase 1 plumbing for preferences and rule names. →
  **Phase 1** (built in from the start, not a follow-up).
- **Q12.** Benchmark scope. → **Include external** systems (ANGRY,
  ASPforASPIC, TOAST, ICCMA solvers). Triples per-workstream benchmark
  scope. Treat as a sub-phase per workstream, not scope creep.

## D. Solver / library choices

- **Q13.** DG SAT backend. → **Add pysat** for CaDiCaL / CryptoMiniSat
  alongside Z3. Required for Phase 5 (DIMACS for model counters).
- **Q14.** TD solver. → **Add htd as optional dep** alongside NetworkX.
  Subprocess via `$PATH`.

## E. Sequencing

- **Q15.** Order of execution. → **(a) Strictly serial, ASP → Datalog →
  DG.** No parallel tracks. Each workstream completes before the next
  begins.

## Implications and follow-ups

1. **Immediate next phase:** ASP backend Phase 0 (per workstream-asp-
   backend.md §4). Phase 0 = backend abstraction (now answered: keyword
   dispatch only) + add `[asp]` optional extra + clingo to dev group.
2. **Before Datalog Phase 0:** Q4 deeper research on gunray coupling.
   Subagent task to dispatch when ASP workstream hits Phase 4 or 5.
3. **When Datalog Phase 0 starts:** Spawn parallel gunray-side
   workstream for upstream Diller-Def-12 NAP analysis (Q5). Cross-repo
   PR cadence: TBD when we get there.
4. **Per-workstream benchmark sub-phase:** Each workstream now carries
   an external-systems benchmark sub-phase (ANGRY, ASPforASPIC,
   TOAST, ICCMA solvers). Estimated +2–4 days per workstream.

## Phase counts after decisions land

- **ASP backend:** 6 phases unchanged + benchmark sub-phase (Phase 4
  expands to include external systems).
- **Datalog grounding:** 6 phases + parallel gunray-side workstream
  (Q5) + Phase 1 carries preferences and rule-name plumbing (Q11).
- **DG/treewidth:** 6 phases unchanged (success bar (c) means all six
  must ship; Phase 3 ABA-DG kept; Phase 5 model counting kept).
