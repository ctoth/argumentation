# Reduction Tricks Report — 2026-05-01

## Task
Write `reports/why-bounded-catalog.md` arguing the catalog of useful solver-target reductions is small (~5-12 entries), structured around three orthogonal axes (complexity cell, theory, structure).

## State
- Done. Report at `C:/Users/Q/code/argumentation/reports/why-bounded-catalog.md`, 2,453 words.
- Sibling reports referenced in prompt do not exist; reports/ was empty.
- Web research: confirmed competition tracks (SAT, MaxSAT Evaluation, QBFEval 2QBF/PCNF/QCIR, ASP, Model Counting Competition) match the complexity-cell axis. Confirmed knowledge-compilation hierarchy (Darwiche map, OBDD/d-DNNF/SDD).

## Verdict committed
N = 10 canonical reduction tricks, 12 with honorable mentions. List in section 9 of the report:
SAT, MaxSAT, MIP/ILP, SMT, CP, ASP/Datalog, QBF, CEGAR, #SAT, knowledge compilation, plus FOL theorem proving and FPT/treewidth DP as the boundary entries.

## Key argumentative moves
1. Three axes: complexity cell (~6-8), theory (~5-7), structure (~5-7).
2. Cube is sparse — collapses: theory→Boolean via bit-blasting, structure→solver internals via CDCL, higher PH→QBF/CEGAR.
3. Solver communities form at fixed points (sinks of reduction graph); new sinks rare.
4. Engaged counterargument: planning/MC/probabilistic-inference dissolve into named cells; LLMs are encoders not solvers; approximate solvers a separate small catalog.

## Blocker
None. Done.
