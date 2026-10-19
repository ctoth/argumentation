# Cleanliness review — refactor/dedup branch (2026-06-27)

Five parallel scouts read the actual code (not old notes) across all 11 subpackages.
Verdict: **architecture clean, connective tissue copy-pasted.** Headline dedup
consolidations landed (z3 loader → optional_deps, semantics dispatch → dung.extensions_for,
enforcement 8-key contract). Remaining work = pervasive small duplication with no shared home.

## Top theme: one missing primitive, re-rolled per layer
- Inclusion-maximal filter `not any(x < other …)` — ~15× (dung, bipolar, scc_recursive, setaf, caf) → `finite.maximal_sets()`
- Attacker-fixpoint loop — ~7× (ranking.py ×3, gradual.py, dfquad, equational) → `finite.iterate_fixpoint(update_fn)`
- Horn forward-closure — 5–6× (aba.py, aba_sat.py, aba_telemetry.py)
- Grow-to-maximal-preferred loop — 4× in aba_sat.py (L624/779/1427/1819)
- Credulous/skeptical acceptance — 4× (enforcement, semantics, dynamic)
- predecessors_index wrappers (_attackers/_predecessors/_attack_relation) — ~6 files; bipolar dups dung._attackers_index byte-for-byte
- Range-maximal selection — 3× (dung/setaf/caf); cf2 vs stage2 SCC recursion near-identical copy

## Big-file split targets
- aba_sat.py (2427 LOC) = SIX solvers in one file (z3+pysat+clingo+brute-force+2 CEGAR+API). Split by backend.
- probabilistic_treedecomp.py (1663) = two parallel TD DPs (paper I/O/U + grounded edge-tracking) + TD construction. Split construction/paper_dp/grounded_dp.
- solver.py (1275) & af_sat.py (1631) = repetitive per-semantics dispatch; table-driven collapses #4/#5.
- dung.py (710) bolts on prudent family + cf2/stage2 recursion. adf.py inlines I/O (setaf split it into setaf_io). partial_af.py fuses partial-AFs + AF-merging.

## Dead / test-only code to delete-or-wire
- sat_encoding.py CNFEncoding/encode_stable_extensions path — no src caller, docstring lies
- solving/backends.py — tested policy the real selector never consults
- aba_sat._native_sparse_narrow_fixedpoint_extension (L1233) dead; _AdmissibleCegarSolver trio (~130 LOC) tests-only
- probabilistic_treedecomp._compute_grounded_dp_component (L1317) dead
- probabilistic: compute_probabilistic_acceptance *args shim, _compute_dfquad vestigial `supports` param, alias trail

## Latent-correctness inconsistencies (not just aesthetics)
- Opposed semantics-string normalizers: preprocessing.py:207 "-"→"_" vs scc_recursive.py:272 "_"→"-"; convention split "semi-stable" vs "semi_stable". Unify convention, delete one.
- semantics.py:_dung_extensions still has parallel 11-key Dung dispatch overlapping dung.extensions_for on 8 keys — the exact path enforcement refactor removed, left here.
- enforcement._SUPPORTED_SEMANTICS hand-dups SemanticsName Literal; SemanticsName defined twice (dung 9-val w/ naive vs enforcement 8-val).

## Recommended order
1. Dead-code sweep (pure subtraction, cheapest) — the 4 items above.
2. Build out core/finite.py: maximal_sets, iterate_fixpoint, public graph helpers; collapse call sites layer by layer (highest leverage, mechanical, test-guarded).
3. Decisions needed (not mechanical): semantics-string convention; aba_sat.py backend split.

## State
Review only — NO code changed. Awaiting Q's pick: start finite.py primitives + dead-code sweep, or scope aba_sat.py split first.
Scout agent IDs (resumable): core/frameworks a146d2c3142b2fe67, solving a1bd4ced6ea365cbf, structured a82b8e7def60b6ea1, prob/gradual/ranking ae9850156e48959b8, dynamics/seams a059d63bd139c6c79.
