# Graph-theory recon: argumentation codebase (2026-05-12)

Recon for "can graph theory speed up the solver". All claims cite file:line.

## (a) Per-module structural-optimization inventory

### `src/argumentation/af_sat.py` (1299 lines) — Z3 incremental SAT kernel for Dung AFs
- Backend: **Z3 only** (`_load_z3` line 1278). No external CDCL, no DIMACS path here.
- Incrementality: one `AfSatKernel` per AF; base-semantics clauses added once and deduped via `self._added` (lines 71, 77-162). Query constraints scoped with `solver.push()/pop()` (e.g. `_complete_extension` lines 666-695). So clause reuse within a kernel = yes; fresh `z3.Solver()` per top-level query = yes.
- Grounded reduct preprocessing into the SAT instance: **NO.** Grounded is used only as a *decision shortcut* in `PreferredSkepticalTaskSolver._shortcut` (lines 493-512): q in grounded -> accept; q attacked-by-grounded -> reject; `_is_acyclic` -> grounded == answer. It never fixes grounded-in/out variables to shrink the encoding.
- SCC decomposition / SCC-recursive evaluation: **NONE** in af_sat.py.
- `_is_acyclic` (line 1254): DFS cycle detection, used only in that preferred-skeptical shortcut.
- Self-attacker handling: only `(query,query) in framework.defeats` short-circuit at line 494; not a general AF-wide preprocessing.
- `PreferredSuperCoreSolver` (lines 537-576): SAT-backed iterative fixpoint computing a conservative subset of every preferred extension (admissibility-attacker pruning + undefended-attacker fixpoint) — used to shortcut DS-PR.
- `PreferredSkepticalTaskSolver` (line 418): CDAS-style — admissible-set SAT utilities + learned "must-hit-outside" blocking clauses (`_PreferredSkepticalAttackerSolver.learn_witness_region` line 814).
- Range-maximal (semi-stable, stage) = `RangeMaximalTaskSolver` (line 924): binary search on range size (`_max_range_size` line 1069) + "high-range shortcut" probing bounded missing-sets (`_high_range_shortcut` line 1009), disabled on dense instances (`>=160` args & `defeats >= 8*args`, lines 1042-1048). Blocks exhausted ranges via `exclude_range_subset` (line 246).
- No symmetric-AF / bipartite / even-odd-cycle special-casing.

### `src/argumentation/dung.py` (720) — reference enumeration semantics
- `grounded_extension` (line 207): efficient BFS least-fixpoint with live-attacker counters (O(V+E)). This is the only fast path; result of `reports/perf-fixes-grounded-report.md`.
- `complete_extensions`/`preferred`/`stable`/`semi_stable`/`stage`/`naive`/`cf2`/`stage2`/`eager`/`ideal`/`prudent_*`: all brute force over `_all_subsets` = 2^n (lines 330-335 and callers; stable/complete via `labelling` module candidate budget).
- `_strongly_connected_components` (line 410): Tarjan. **Used ONLY** by `_is_cf2_extension` (line 516) and `_is_stage2_extension` (line 568). Confirmed: nothing else uses SCC. `_subframework` (line 456) and `_component_defeated` (line 491) likewise only feed cf2/stage2 recursion.
- `indirect_attacks` (line 584): odd-length attack-path detection for prudent semantics only.

### `src/argumentation/aba_sat.py` (1111) — ABA SAT/ASP
- `support_extensions` (line 13): brute force over `2^|assumptions|` masks via `_SupportState` with bitmask-precomputed minimal supports (`_minimal_supports` line 862; `_SupportState.from_framework` line 784).
- `AssumptionKernel` (line 52): **clingo-backed** (`_solve_selected` line 255, `_load_clingo` line 1097) — emits ASP for stable / admissible / preferred over assumption-selection vars.
- SAT path for ABA complete/preferred: **Z3** (`_load_z3` line 1089). `sat_support_extension` line 347: admissible/complete constraints over assumption vars + minimal-support disjunctions (`_any_support_selected` line 922). Preferred via strict-superset growth loop (lines 412-428) or CEGAR (`_sat_preferred_cegar_extension` line 481, `_add_ranked_closure_constraints` line 634 — Int ranks; a BitVec variant `_add_bitvec_ranked_closure_constraints` line 695 exists but appears unused).
- No SCC / grounded-reduct / treewidth preprocessing. `closure` (line 143) is an efficient worklist closure (consequence of `f932446`/`68a5dc1` "Speed up ABA closure" commits).

### `src/argumentation/aba_asp.py` (355) — ASP-fact ABA backend
- `encode_aba_theory` (line 38): emits ASP facts incl. precomputed minimal supports; dispatches to `solver_adapters/clingo.py` with `.lp` encoding modules. No structural reduction; clingo does the work.

### `src/argumentation/solver.py` (1074) — dispatch
- `auto` backend rules: `_auto_dung_extension_backend` line 479 (sat for complete/stable, else native); `_auto_dung_single_backend` line 485 (sat for complete/ideal/preferred/semi-stable/stable/stage); `_auto_dung_acceptance_backend` line 495; `_auto_aba_backend` line 505 (sat for complete/preferred/stable). `grounded` always native (fast). cf2/stage2 always native (brute force).

### `src/argumentation/backends.py` (50) — `default_backend` line 17: grounded->asp, theory_size>30 & has_clingo->asp, else has_z3->sat, else materialized_reference. (This is a *separate* heuristic surface, used by ASPIC/ABA "structured" facade, not by `solver.py`'s `auto`.)

### `src/argumentation/sat_encoding.py` (203) — pure-Python CNF (no solver)
- `encode_stable_extensions` (line 66): the exact flat "conflict-free + in-or-attacked" CNF (one var per argument). `stable_extensions_from_encoding` (line 97) and `sat_extensions` (line 120) brute-force over 2^n satisfying assignments. `CNFEncoding` dataclass exists for DIMACS-style consumers but nothing emits DIMACS.

### `src/argumentation/approximate.py` (162) — k-stable + bounded grounded iteration, all brute force / pure-python; calibration surface only.

### `src/argumentation/solver_adapters/`: `clingo.py` (subprocess + python-module clingo runner), `iccma_af.py`, `iccma_aba.py` (subprocess ICCMA binary wrappers). `encodings/`: `aba_{admissible,complete,stable}.lp`, `aspic_{admissible,complete,stable}.lp`, `dung_{admissible,complete,stable}.lp`. `iccma.py`/`iccma_cli.py`: ICCMA file-format parsing + CLI; no solving logic itself (delegates).

## (b) Structural tricks NOT present
- No grounded-reduct preprocessing fed into SAT/ASP (only used as boolean shortcut for DS-PR).
- No SCC decomposition for the core semantics (complete/preferred/stable/semi-stable/stage) — SCC exists only for cf2/stage2 brute-force checks.
- No unattacked-argument fixpoint simplification of the framework before encoding (beyond grounded shortcut).
- No removal of self-attackers as preprocessing.
- No isolated/dominated-argument elimination.
- No symmetric-AF special case (symmetric AFs: stable=preferred=naive).
- No bipartite / even-cycle / acyclic special-case beyond `_is_acyclic` -> grounded in DS-PR only.
- No treewidth / tree-decomposition / clique-width structure-aware encoding (DG/DDG reductions). `probabilistic_treedecomp.py` has `TreeDecomposition`/`NiceTreeDecomposition` dataclasses but only for a grounded-DP backend that its own header says has zero asymptotic benefit (per `reports/workstream-dg-treewidth.md` §3.1).
- No model counting backend.
- No DIMACS export / external CDCL solver path (Z3 + clingo only).

## (c) Known pain points from reports
- `reports/perf-fixes-grounded-report.md`: grounded was slow (iterative char-fn); fixed to labelling algorithm + reverse/forward adjacency indexes built once. Also `bipolar.py` grounded delegated to dung. Already done.
- `reports/research-nonstable-af-solver-backend.md` & `reports/workstream-incremental-af-sat-kernel.md`: complete/preferred/semi-stable/stage/ideal originally fell back to native 2^n enumeration -> timeouts. Fix: task-directed Z3 SAT (complete labellings + iterative maximality/range checks + CDAS for DS-PR). Largely implemented (that's what `af_sat.py` is now). Recommendations cite ArgSemSAT, PrefSat, Dvořák/Järvisalo/Wallner/Woltran CEGAR, Fudge, argmat-sat, Thimm/Cerutti/Vallati CDAS/CDIS.
- `reports/workstream-zero-timeouts-dspr-aba.md`: cap-100 ICCMA timeout profile — 2017: 16 AF DS-PR; 2019: 7 AF DS-PR; 2023: 83 ABA (SE-PR/SE-ST clusters); 2025: 54 ABA (DC/DS/SE on selected ABA files). DS-PR and ABA are the blockers; stage/semi-stable no longer dominant.
- `reports/workstream-dspr-remaining-eight.md` + `notes/adversarial-dspr-remaining-eight-2026-05-02.md`: after "strong learning" workstream, 8 AF DS-PR rows still time out (irvine-shuttle...80, BA_60_60_3, Small-result-b76/b88/b90/b97). Classified as "unique attacker/witness churn" — e.g. 5946 unique attacker checks / 5945 learned witness regions on one row. Caching/exact-duplicate suppression exhausted; need each learned clause to cover a *larger semantic region* (maximal preferred witness learning instead of arbitrary admissible witness). Claude's review explicitly noted: "The solver runs on the whole AF before any grounded/SCC-local simplification" — and warned full SCC-recursive preferred is easy to get wrong, do not approximate it. Phase 1 = grounded accept/reject shortcuts (a "reduct" misnomer — only checks G, doesn't recurse on AF\G\G-attacked).
- `reports/bench-asp-vs-sat-2026-05-01.md`: bench harness `bench/asp_vs_sat.py` compares `support_reference` vs `asp` (ABA chains) and `materialized_reference` vs `asp` (ASPIC+ chains); external systems (mu-toksia etc.) not installed. `bench/` = README.md, asp_vs_sat.py, instance_gen.py only.
- `reports/workstream-dg-treewidth.md` + `notes/dg-treewidth-workstream-2026-05-01.md`: a full *design-only* (unimplemented) workstream for Fichte 2021 decomposition-guided (treewidth-aware) SAT encodings and Mahmood 2025 clique-width (DDG). Key honest risks recorded: no published DG implementation for AFs; ICCMA winners use flat encodings + CEGAR; real ICCMA AFs may have treewidth 50-200 so the 2^O(tw) win may not land; honest expected outcome is "wins only on synthetic low-tw families." 6-phase plan (TD backend / DG-stable / DG-adm-complete-preferred-iterative / ABA-DG novel / benchmark vs mu-toksia / model counting). Reusable scaffolding noted: `probabilistic_treedecomp.py` dataclasses; `_attackers_index`. Not started (it's gated behind ASP + Datalog workstreams).

## (d) Where the AF is constructed from ABA / ASPIC
- ABA -> Dung: `aba.py:aba_to_dung` (line 232): enumerates `_all_arguments(framework)`, builds labels for each, then `defeats = {(label[a],label[t]) for a in args for t in args if _argument_attacks(...)}` — **O(|arguments|^2)** pair scan. ABA "arguments" = deduction trees, so the argument set itself can be large.
- ASPIC+ -> Dung: `aspic.py:build_abstract_framework` (line 1320): `build_arguments` (line 682, bottom-up fixpoint over rules, c-consistency-filtered, deduplicated) -> `compute_attacks` -> `compute_defeats` (preference filter). Argument construction is itself a fixpoint loop (line 735) with Cartesian products over antecedent-matching sub-arguments (`itertools.product`, line 751) — can blow up on rule-rich systems.
- Neither construction is profiled in the reports; the reports/workstreams treat ABA via the assumption-level SAT/ASP path (`aba_sat.py`, `aba_asp.py`) precisely to avoid materializing the Dung AF. `reports/workstream-zero-timeouts-dspr-aba.md` Phase 4 and Toni 2014 citation: "generating full Dung AFs unnecessarily" is called out as the thing to avoid.

## State
Recon complete. Report delivered to parent.
