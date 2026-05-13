# Encoding Preconditions Report — Research Notes

## 2026-05-01 — Initial state

**Task**: Write `reports/encoding-preconditions.md` (~2000-3000 words) on structural preconditions that make a reduction to SAT/MaxSAT/ASP/QBF/SMT/etc. *practical*, not just possible (Cook-Levin).

**Audience**: Q, research engineer in computational argumentation.

**Structure**: One section per *structural property* (10 listed in prompt), then synthesis (decision tree + wasted-reduction failure modes).

**Constraints**:
- Don't enumerate targets themselves (sibling researcher does that).
- Don't cite specific argumentation encodings (sibling does that).
- Web research permitted; propstore papers permitted.

## Observations so far

- Confirmed `reports/` directory location (creating the file there).
- Confirmed propstore papers exist at `C:/Users/Q/code/propstore/papers/` — could read Mahmood 2025, Fichte 2021, Dunne 2009 if needed for treewidth/structure-aware sections.
- Have not yet fetched any web sources.

## Plan

1. Skip deep paper reads for now — the topic is general enough that I can write from established knowledge of:
   - Tseitin encoding and CNF blowup
   - MaxSAT vs ILP linear-objective tradeoff
   - Stratified Datalog vs ASP nonmonotonicity
   - QBF complexity hierarchy
   - Knowledge compilation / d-DNNF for #SAT
   - SMT theory propagators (Simplex for LRA)
   - Treewidth / Courcelle / FPT
   - CP global constraints (alldifferent's matching propagator)
   - BDD symbolic state representation
2. Optionally fetch one or two web sources to verify any specific claims (e.g., MaxSAT vs ILP performance, Tseitin polarity optimization).
3. Write the report directly.

## Blockers

None. Proceeding to draft.
