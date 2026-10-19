# Deep correctness review — session state (2026-07-10)

Role: coordinator for read-only correctness review of src/argumentation. No source files modified (this notes file is the only write, per checkpoint hook).

## Task
≤12 findings, ranked by severity, exact file:line, violated invariant, counterexample, why tests miss it. Adversarial leads: ADF classify_link syntax-vs-function; duplicate ABA contrary lines; attacks-vs-defeats in naive/CF2; broad RuntimeError catches in solver dispatch; convergence metadata discarded by gradual LLM wrappers.

## State
- Surveyed repo: ~19k LOC under src/argumentation (core, solving, structured/aba, structured/aspic, frameworks, gradual, ranking, probabilistic, dynamics, interop, solver_adapters).
- Dispatched 7 background analyst agents (all running):
  1. core-sem — core Dung semantics + naive/CF2 lead
  2. sat-solve — af_sat/solver dispatch + RuntimeError-catch lead
  3. aba-rev — ABA subsystem + duplicate-contrary lead
  4. adf-fw — ADF/frameworks + classify_link lead
  5. grad-rank — gradual/ranking + LLM-wrapper convergence lead
  6. prob-dyn — probabilistic + dynamics
  7. aspic-io — ASPIC + ICCMA interop parsers
- Next: as each completes, verify load-bearing findings myself (read cited lines, rerun counterexamples), then rank and report ≤12, separating cleared-not-bugs and architecture notes.

## Findings so far
(none yet — awaiting agent reports)
