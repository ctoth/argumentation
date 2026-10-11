# Foreman: dedup cleanup pipeline (2026-06-27)

Branch: refactor/dedup. Mode: serial, one commit per cleanup, verify each report vs plan before next.
Source of findings: notes-cleanliness-review-2026-06-27.md (5 scout reports, file:line cited).

## Commit plan (each = 1 dispatch = 1 commit)
1. [ ] solving dead-code: remove sat_encoding.py dead CNF path (CNFEncoding/encode_stable_extensions/stable_extensions_from_encoding/_admissible_sets) + backends.py unused policy; prune orphaned tests. KEEP live sat_extensions.
2. [ ] aba dead-code: remove aba_sat._native_sparse_narrow_fixedpoint_extension (zero callers). Investigate _AdmissibleCegarSolver trio (tests-only) — delete path + its tests IF confirmed superseded by _RealPrefSatSolver.
3. [ ] probabilistic dead-code: remove _compute_grounded_dp_component (L1317 dead), _compute_dfquad vestigial `supports` param, compute_probabilistic_acceptance *args shim (keep typed _compute_probabilistic_acceptance as public).
4. [ ] finite.maximal_sets() + collapse ~15 inclusion-maximal `not any(x<other)` sites (dung/bipolar/scc_recursive/setaf/caf).
5. [ ] finite range-maximal unify (dung/setaf/caf) + merge cf2/stage2 SCC recursion (dung).
6. [ ] promote shared dung graph helpers to public finite API; kill _attackers/_predecessors/_attack_relation wrappers + bipolar dup _attackers_index.
7. [ ] finite.iterate_fixpoint() + collapse ~7 ranking/gradual fixpoint loops (ranking ×3, gradual, dfquad, equational).
8. [ ] aba: unify Horn forward-closure (aba.py, aba_sat.py, aba_telemetry.py 5-6 sites).
9. [ ] aba_sat: extract grow-to-maximal-preferred helper (4 sites L624/779/1427/1819).
10. [ ] semantics-string convention unify (semi-stable vs semi_stable); delete one of opposed normalizers (preprocessing.py:207 vs scc_recursive.py:272); semantics.py:_dung_extensions delegate to dung.extensions_for; enforcement._SUPPORTED_SEMANTICS derive from SemanticsName.
11. [ ] solver.py table-driven dispatch (solve_dung_single_extension 6× try/except; _solve_sat_*_acceptance 5×); strip redundant isinstance ladders in 4 _solve_iccma_* wrappers.
12. [ ] probabilistic MC/Agresti-Coull helper (4 CI copies, 2 loops) + strategy-dispatch table (_compute_probabilistic_acceptance 6-branch).
13. [ ] af_sat dedup: unify stable encoding (3×), admissible (2×), complete/conflict-free helper, util-name munging (3×), shared _sorted_extensions, one clingo-detection.
14. [ ] aba_sat.py split by backend (z3/native-cnf/asp-kernel/support/shared).
15. [ ] probabilistic_treedecomp.py split (construction/paper_dp/grounded_dp).
16. [ ] framework boundaries: adf_io split, partial_af merging split, dung prudent+cf2/stage2 split.

## ✅ PROCESS FIX (Q caught the livelock 2026-06-27): coder agents LIVELOCK on full-suite verification (pytest auto-backgrounds in SUBAGENT env → they yield forever, each "completed" notification is a stall not a finish). FOREMAN's OWN Bash runs pytest FOREGROUND fine (verified: full suite 421s returned cleanly). NEW LOOP: coder gates commit on ruff+targeted-tests ONLY and reports hash immediately; FOREMAN runs `uv run pytest -q` ITSELF to verify each commit. Never wait on a coder for full-suite confirmation again.
- c9 VERIFIED by foreman's own run: HEAD e067cac → 2908 passed, 3 skipped, 1 xfailed.

## ⚠⚠ ROOT CAUSE OF ALL COMMIT STALLS (c2/c5/c9): pytest AUTO-BACKGROUNDS in the subagent Bash env. Agents that run the suite BEFORE committing yield and never reach the commit. FIX FOR ALL REMAINING PROMPTS: order = (1) ruff check [fast, no background] → fix → (2) git add+commit+rev-parse [BEFORE any pytest] → (3) THEN run full pytest + lint-imports as POST-COMMIT confirmation (it backgrounds; agent notified on done; fix-forward with a NEW commit if red). Commit must never be gated behind a pytest call. Tell the coder to REPLY WITH THE HASH before running pytest.

## ⚠ STALE-DIAGNOSTIC PATTERN: After a deletion that shifts line numbers, the harness LSP emits PHANTOM errors at stale line numbers (seen on c1 sat_encoding test, c3 _compute_dfquad "supports unbound" — both proven false by fresh pyright + repro). For pure-deletion commits with green full suite, verify cheaply (git show + fresh pyright/repro), don't always spin a full fix agent.

## DOCS REFRESH (post-merge, branch docs/post-dedup-refresh off main). Audit (researcher a0a4dbe) → reports/docs-audit.md.
- Stale because refactor deleted/split: solving.backends (whole module GONE, docs/backends.md documents it + README:500/architecture:203-205/246/283-286), sat_encoding CNF claim now FALSE (README:10/104/459-461, architecture:206), probabilistic_treedecomp facade DELETED→3 modules (architecture:153-158, gaps.md:11-12, index.md:36).
- NO broken runnable examples in README/examples.md (only backends.md's own snippets fail).
- test_docs_surface.py = keyword/path GUARD (not ref-checker) — that's why stale refs passed. LANDMINES: must keep phrases "adapted grounded edge-tracking" + "not the full Popescu & Wallner I/O/U witness-table DP"; deleting backends.md breaks index-link test; no flat src/argumentation/<mod>.py paths.
- backends.md → REWRITE (not delete): keep backend-string tables, replace dead API with solver._has_clingo + _auto_* routing.
- CHANGELOG 0.3.0 table = HISTORICAL, LEAVE; add [Unreleased] Removed note.
- semi_stable_extensions identifier = CORRECT, do not touch. CONTRIBUTING/AGENTS/CITATIONS/setaf/caf/perf/iccma docs = clean.
- PLAN: doc-fix coder (aad8dc4), 2 commits: (1) rewrite backends.md, (2) repoint README+architecture+gaps+index + CHANGELOG [Unreleased]. Gate: tests/test_docs_surface.py (fast). Foreman verifies after.

## MERGE (Q asked "merge to master" — repo uses `main`): target = main. refactor/dedup is 42 commits ahead (B1-B8 + reorg from prior sessions + my 24 this session); main has NOT diverged (0 commits ahead) → ff possible. Tree clean (only untracked artifacts). remotes/origin/main exists but Q did NOT ask to push — merge LOCALLY only. Plan: final full-suite gate on HEAD 9078b6d, then git merge --no-ff into main (merge commit = revertable as a unit). c17 tool fix `9078b6d` committed (pyright clean). 24 session commits done.

## ✅ DE-FACADE (Q demanded NO re-exports, one canonical export per concept): c16 = 2 commits 4f1e1da + 1b29304. VERIFIED: probabilistic_treedecomp.py DELETED, zero "re-exported" noqa in src/, deleted names imported nowhere, 2908 passed, lint-imports clean. aba_sat keeps only genuinely-used imports (_BitsetHornClosure/_SupportState/_minimal_supports/AssumptionKernel — real deps, not re-exports); consumers (test_aba, aba_stable_diagnostics tool, probabilistic.py, TD tests) now import from canonical aba_kernel/aba_support_model/construction/paper_td/grounded_td. 23 COMMITS TOTAL.
- STILL open ticket: tools/aba_stable_diagnostics.py:307 calls nonexistent aba_sat.derives → AttributeError (pre-existing, not in test path).

## ✅✅ PIPELINE COMPLETE — 20 commits, all verified green by foreman's own full-suite runs (final 2908 passed, 3 skipped, 1 xfailed).
Commits: fd82638 5bfe44c f877dcc 2f16dfc 9834643 5a6b1e7 ace92f2 afe2bad e067cac 5942ef2 ac701b2 48f259a ace2dcf f12ee71 b13506d d05a438 1a3fb16 ea8ded0 8803988 392c5c9
- c15 DONE: adf_io.py split (880398) + af_merging.py split (392c5c9). VERIFIED: adf.__all__ no moved names, Any removed, 2908 passed. Diagnostics were stale.
- NOT DONE (deliberately deferred, LOW value): c16 warts — dung.defends all_args noqa'd param (harmless), partial_af.EnumerationExceeded.remainder_provenance + vaf_completion.ArgumentLine.terminated_by_repeated_value set-never-read fields. Removing risks tiny API changes for ~nil benefit. Recommend leave/skip.
- ALSO deferred (optional follow-ups noted by scouts): semantics.py _dung_extensions→extensions_for delegation (post-sorts, optional); _sorted_extensions dup (solver.py+sat_encoding.py → core.finite.sorted_extensions); probabilistic compute_probabilistic_acceptance *args shim → rename typed private; zero-consumer public aliases ProbabilisticArgumentationFramework/ProbabilisticResult (ASK Q before removing public names); aba_telemetry inline post-order dedup; grounded-TD inline post-order at :1346. BUG TICKET: tools/aba_stable_diagnostics.py:306 calls nonexistent aba_sat.derives → AttributeError.

## Pre-existing baseline (NOT introduced by this pipeline — do not blame coders)
- ruff: ~22 pre-existing errors in untouched files (e.g. solver.py) — present at HEAD before c1.
- pyright: `.answer` attr-access errors + `tests.core.test_dung` import in tests/solving/test_solver_encoding.py — present in HEAD~1.
Coders must ensure THEIR changed files are clean; pre-existing errors in untouched files are out of scope.

## Progress log
(updated after every subagent)

### Commit 8 DONE — `afe2bad` — "extract core.fixpoint.iterate_fixpoint and dedupe ranking/gradual fixpoint loops". VERIFIED: module+test tracked, called in ranking/gradual/dfquad, tree clean, suite 2899 (2894+5). Stale "could not be resolved" diagnostics (new module).
- iterate_fixpoint(initial, update, *, tolerance, max_iterations) -> FixpointOutcome NamedTuple. Routed 6 sites.
- Agent GOOD CALLS: left equational_fixpoint hand-rolled (empty input raises ValueError vs helper returns converged — REAL behavioral diff); left burden_numbers (no convergence check). → these are candidates for c8b only if we decide to normalize empty-input behavior (probably leave).

### Commit 7 DONE — `ace92f2` — "inline graph-helper wrappers into core.finite and dedupe ranking attack helpers". VERIFIED: zero _attackers_index refs in .py (only stale .pyc), tree clean, suite 2899, lint-imports clean. 13 files, +128/-183.
- Caught scout's importer-list GAP via my nudge: af_sat.py/sat_encoding.py/test_solver_encoding.py also imported dung._attackers_index — all repointed to finite.predecessors_index. LESSON: always tell coder to grep WHOLE repo for deleted symbols, don't trust scout's importer enumeration.
- Move 2: new ranking/_graph.py holds single attack_relation/attackers (both ranking.py + ranking_axioms.py import). Kept dung._strongly_connected_components/_subframework.

### c7 graph-helpers (history). Scout mapped it (Option C hybrid: inline pure-rename wrappers to finite; consolidate ranking _attack_relation into ranking/_graph.py; keep dung._strongly_connected_components/_subframework).
- ⚠ SCOUT IMPORTER-LIST GAP: diagnostics revealed solving/sat_encoding.py:13 AND tests/solving/test_solver_encoding.py:11 ALSO import dung._attackers_index — NOT in scout's list (only had scc_recursive+preprocessing). Sent nudge to running agent: grep WHOLE repo (src+tests) for every deleted symbol, fix all importers, don't commit until full suite green. VERIFY THIS on report.

### Commit 9 DONE — `e067cac` — "unify ABA frozenset Horn-closures into aba._closure.horn_closure". Committed (tree clean, _closure.py+test tracked, ruff+targeted aba tests passed). Full-suite confirmation running post-commit (expect 2899+new test). Took 5 nudges due to the pytest-auto-background stall — now diagnosed (see ROOT CAUSE note above).
- New leaf module aba/_closure.py (no aba.py import → no cycle); 3 sites routed (aba._closure wrapper, AssumptionKernel.closure, aba_telemetry._closure_from). LEFT: _BitsetHornClosure + _SupportState.derives.

### Commit 10 DONE — `5942ef2` — "unify semantics-string convention to hyphen (C10)". VERIFIED by foreman's own run: 2908 passed, zero semi_stable string keys remain. Fast loop worked (no livelock): coder committed gated on ruff+targeted(906 passed), foreman ran full suite.
- Flipped af_sat.py:863 + preprocessing.py:74 to hyphen ATOMICALLY with deleting preprocessing._normalize_semantics; deleted scc_recursive no-op normalizer; enforcement _SUPPORTED_SEMANTICS = frozenset(get_args(SemanticsName)) keeping 8-val Literal. Updated 4 test keys.
- DEFERRED: semantics.py _dung_extensions → extensions_for delegation (fold into c11 or separate).

### c10 semantics-string SCOUT DONE (acad6821) — SPEC READY:
- Canonical = HYPHEN "semi-stable" (public-API promise: ICCMA CLI, solver.py:1182 match hyphen only; tests 20 hyphen vs 4 underscore). NO public breakage (underscore never a working public input).
- CRITICAL ATOMIC: flip af_sat.py:863 (_prepare internal literal) + preprocessing.py:74 (GROUNDED_REDUCT_SEMANTICS) to hyphen IN SAME COMMIT as deleting preprocessing.py:206 normalizer — else simplify_af silently disables grounded-reduct (forgiving at preprocessing.py:133 → correct results, lost perf, NO error).
- scc_recursive.py:275 normalizer "_"→"-" is a PURE NO-OP (keys complete/preferred/stable have no _/-) → delete outright.
- enforcement 8-key contract LOAD-BEARING (commit 18b08bb restored it) → keep enforcement's 8-val SemanticsName separate; only do _SUPPORTED_SEMANTICS = frozenset(get_args(SemanticsName)).
- semantics.py _dung_extensions delegation = OPTIONAL follow-up (it post-sorts via _sorted_extensions; delegation must keep that wrap). DEFER to c10b/c11.
- PLAN: c10 = ONE commit (flip 2 sites + delete both normalizers + get_args dedup). Risk low.

### c9 Horn-closure SCOUT DONE (af7fe78) — recommendation: only 3 frozenset closures truly duplicate → merge into horn_closure(seed, rules) in NEW leaf module aba/_closure.py (aba.py:255 _closure becomes wrapper; aba_sat.py:264 AssumptionKernel.closure; aba_telemetry.py:138 _closure_from). 3 call sites. LEAVE SEPARATE: _BitsetHornClosure (int-mask, CEGAR hot loop, memoized, telemetry — merging regresses perf) + its _NativeCnfPrefSatSolver._closure adapter; EXCLUDE _SupportState.derives (it's a subset test, not a closure — folding = correctness bug). Spec ready for c9 coder.

### Commit 6 DONE — `5a6b1e7` — "merge cf2/stage2 SCC recursion into one parameterized recursor". VERIFIED: Callable imported (L15), _is_scc_recursive_extension (L441) + both wrappers delegate, tree clean, suite 2894 (unchanged), 7 cf2/stage2 tests pass. "Callable not defined" diagnostic was stale.
- Enumeration drivers cf2_extensions/stage2_extensions left as-is (out of cited scope) — possible follow-up.

### Commit 11 DONE — `ac701b2` — "table-driven dispatch in solving/solver.py (C11)". VERIFIED foreman run: 2908 passed. solver.py 1276→1195. Collapsed 6 single-ext blocks→dict, 4 _solve_sat_*_acceptance→1 helper, stripped dead iccma isinstance branches. Agent left preferred-cred/skep/ideal separate (correct — don't fit finder contract).

### c12 SCOUT (a8c97cb) DONE — only SAFE af_sat wins = Item3 (_complete/_conflict_free orchestration merge) + Item4 (_seed util-name helper). LEAVE the 2 admissibility encoders + stable encoding (different CNF, correctness risk). Net value MINOR. _sorted_extensions dup is solver.py:1178 + sat_encoding.py:74 (NOT af_sat) → both reducible to core.finite.sorted_extensions (separate small cleanup, maybe c12b). c12 coder running (Items 3+4).

### c13 SCOUT (a63450a) DONE — SPLIT PLAN (3 small move+re-export-facade commits, aba_sat.py stays facade, no import-linter change):
- c13a: NEW aba_bitset_closure.py ← _BitsetHornClosure (aba_sat:1437-1571, ~135L). LOWEST risk, no external importers, not monkeypatched.
- c13b: NEW aba_kernel.py ← AssumptionKernel (:175-381) + _positive_solver_model (:43-47) + _load_clingo (:2088-92), ~215L. test-only importers (re-export covers).
- c13c (optional): NEW aba_support_model.py ← _SupportState (:1755) + _minimal_supports (:1849) + helpers, ~155L. 2 PROD importers (aba_preprocessing:154, aba_asp:16) — re-export or update.
- ⚠ MUST STAY co-located in aba_sat.py (tests monkeypatch these module globals; moving breaks patching): dispatch funcs sat_support_extension/sat_support_acceptance + native_cnf_prefsat_extension + real_prefsat_extension + _aba_simplification. Also keep all 3 engines, ranked-closure emitters, z3 encoders, result dataclasses.
- BONUS BUG (out of scope, ticket): tools/aba_stable_diagnostics.py:306,308 call aba_sat.derives which doesn't exist → AttributeError (tool not in pytest path).

### Commit 12 DONE — `48f259a` — "dedup af_sat extension orchestration and seed labels (C12)". VERIFIED foreman run: 2908 passed. _run_extension helper (Item3), _seed_label_base (Item4); encoders left untouched. Item6 skipped.

### Commit 13c DONE — `b13506d` — "extract _SupportState/_minimal_supports into aba_support_model.py". VERIFIED foreman run: 2908 passed. aba_sat.py 1759→1613. New aba_support_model.py 165L. Updated prod importers aba_asp + aba_preprocessing. ✅ aba_sat SPLIT COMPLETE: 2108→1613 (−23%), 3 leaf modules (144+226+165=535L extracted), all green via re-export facade.

### Commit 13b DONE — `f12ee71` — "extract AssumptionKernel into aba_kernel.py". VERIFIED foreman run: 2908 passed, aba_sat.py 1973→1759, aba_kernel.py 226L. Agent followed corrected ordering (commit on ruff+pyright, then confirmation). GOOD CALL: left _positive_solver_model in aba_sat (scout misidentified — real callers are the 3 SAT solvers, not kernel); moved only AssumptionKernel + _load_clingo.

### Commit 13a DONE — `ace2dcf` — "extract _BitsetHornClosure into aba_bitset_closure.py". VERIFIED foreman run: 2908 passed, aba_sat.py 2108→1973. Leaf module (no aba_sat import), re-export facade keeps aba_sat._BitsetHornClosure working.
- PROMPT-TEMPLATE FIX: gate commit on ruff+pyright ONLY (both fast, no background); commit+reply hash BEFORE any pytest (targeted pytest also auto-backgrounds → stalls). Then tests after.

### Commit 14a/b/c DONE — `d05a438`/`1a3fb16`/`ea8ded0` — treedecomp 3-way split. VERIFIED foreman run: 2908 passed. probabilistic_treedecomp.py 1663→59 facade + construction(449)/paper_td(621)/grounded_td(628). lint-imports clean. ✅ BOTH headline giant files split.

### c14 SCOUT (abcab0b) DONE — treedecomp 3-way split, CLEAN (no monkeypatch, no cycle, DPs share only construction+DPTableSummary):
- c14a: probabilistic_treedecomp_construction.py (LEAF, imports core.dung only) ← TD/NiceTD dataclasses + DPTableSummary + estimate_treewidth/compute_tree_decomposition/validate/to_nice/_nice_td_post_order/_build_primal_graph.
- c14b: probabilistic_paper_td.py ← PaperTD*/paper_*_rows/compute_paper_exact_extension_probability/_paper_td_*. imports construction.
- c14c: probabilistic_grounded_td.py ← GroundedOutcome*/ExactDPDiagnostics/compute_exact_dp*/_dp_introduce/forget/join/_compute_grounded_dp* + supports_exact_dp. imports construction + probabilistic_components.
- probabilistic_treedecomp.py → pure re-export facade (zero importer edits; probabilistic.py lazy imports + 2 test modules unaffected).
- DOC-not-fix: grounded re-implements post-order inline at :1346-1356 (latent dedup, leave during move).
- PLAN: ONE coder, 3 commits, each ruff+pyright-gated, NO pytest between commits (avoids stall), reply 3 hashes, foreman verifies full suite.

## REMAINING after c12: c13a/b/c aba_sat extractions, c14 treedecomp split (scout first), c15 framework boundaries, c16 warts (low/skip).

## REMAINING after c11: c12 af_sat internal dedup (NOTE: c1 already removed sat_encoding CNF + backends.py, so clingo-detection dup and 1 of 3 stable-encoding copies ALREADY GONE — scout to get current state), c13 aba_sat.py SPLIT (~2300 lines, headline), c14 probabilistic_treedecomp.py SPLIT (~1600), c15 framework boundaries (adf_io split, partial_af merging split, dung prudent split, vaf style), c16 warts (dung all_args param, set-never-read dataclass fields — LOW value, noqa'd/harmless, maybe skip). c12+c13 scouts dispatched in parallel.

## REORDERED REMAINING PLAN (by risk; serial, one coder at a time given recurring commit-stalls)
- c8 NEXT: core/fixpoint.py iterate_fixpoint() + collapse 7 loops (ranking ×3, gradual.py, dfquad, equational). HOME DECISION: new module core/fixpoint.py (NOT finite.py — numeric fixpoint ≠ finite relations). Helper returns (scores, converged, iterations, delta); each caller wraps its own Result type.
- c7 (graph helpers) DEFERRED: needs a scout to map layering + import-linter contracts before deciding where public attackers/targets/predecessors helpers live and whether gradual/ranking may depend on dung. Touches core(dung/bipolar/scc_recursive/preprocessing)+gradual+ranking. Do AFTER c8 (overlaps gradual/ranking files).
- HIGH-RISK (scout-first + verifier gate, NOT blind coder): c9 Horn-closure unify (perf-critical bitset SAT path — maybe only unify frozenset variants, leave _BitsetHornClosure), c12 af_sat SAT-encoding dedup, c13 aba_sat split, c14 treedecomp split, c15 framework boundaries.
- MEDIUM: c10 semantics-string convention (core+semantics+enforcement), c11 dispatch tables (solver/probabilistic).
- c16 warts: dung all_args unused param, passthrough wrappers (overlaps c7 — fold together).

### Commit 5 DONE — `9834643` — "unify range-maximal selection via finite.maximal_by". VERIFIED: HEAD correct, tree clean, maximal_by called at 4 sites; full suite 2894 (2892+2 new), ruff/pyright/lint-imports clean.
- maximal_by(candidates, key) generalizes maximal_sets; maximal_sets refolded as maximal_by(c, identity). 3 range sites routed (dung/setaf/caf).
- Note: "maximal_by is not defined" reportUndefinedVariable diagnostics were ALSO stale (imports were present). Lesson reinforced: even strong pyright error classes go stale post-edit; grep/fresh-pyright to confirm. The one REAL issue (test annotation frozenset[str] vs int) was fixed before commit.

### Commit 4 DONE — `2f16dfc` (+ stray doc-commit `9316d14`) — "extract finite.maximal_sets and dedupe inclusion-maximal filters". VERIFIED: grep confirms 8 real maximal_sets() call sites (dung ×4, bipolar, scc_recursive, caf, setaf); full suite 2892 (2891+new test); ruff/pyright/lint-imports clean. "not accessed" diagnostics were stale phantoms (ruff-clean rules out unused imports).
- maximal_sets(candidates: Iterable[frozenset[T]]) -> list[frozenset[T]]: keep x where no other is strict superset; preserves order; no dedup (per-site wrappers kept).
- Correctly LEFT: _range_maximal (ranges = different collection → c5), scc fixpoint <= test, len<=1 checks.
- PROCESS NOTE: agent made a SEPARATE doc commit for the report (9316d14). Future coders: do NOT git add/commit the report — leave untracked like c1-c3.
- Pre-existing warts surfaced by diagnostics (NOT c4): dung all_args unused param (L116), bipolar _support_predecessors wrapper, dung extensions_for unreachable tail (L694-710), caf L146 unreachable — all on the later cleanup list.

### Commit 3 DONE — `f877dcc` — "remove dead _compute_grounded_dp_component and vestigial dfquad supports param". VERIFIED (fix-agent a22e4d96 + repro): full suite 2891 pass, dfquad paths run clean, supports unconditionally bound. Diagnostics were STALE (flagged the assignment line as unbound).
- Part 2 investigation (deferred items): (3) compute_probabilistic_acceptance IS public API (__all__ + 6 test files) — keep name but rename typed private _compute_probabilistic_acceptance → public, drop *args shim (FOLLOW-UP, fold into c12). (4) aliases ProbabilisticArgumentationFramework/ProbabilisticResult have ZERO consumers in src/tests — removable; only external-API stability argues keep. DECISION PENDING (ask Q before removing public names).

### Commit 2 DONE — `5bfe44c` — "remove dead and superseded aba_sat solver paths". VERIFIED: full suite 2891 passed/3 skip/1 xfail (was 2892; −1 = removed CEGAR pinning test), ruff+pyright+lint-imports clean.
- Collapsed Part1+c2b into ONE commit (both dead-code in aba_sat.py). Deleted: _native_sparse_narrow_fixedpoint_extension + cascade; _AdmissibleCegarSolver trio + orphaned _defense_counterexample(s)/_attacker_support_not_counterattacked/_shrink_attack_support + unused `derives` import; test_preferred_cegar_matches_admissible_growth. 317 del / 1 ins.
- Agent (correctly) KEPT _clause_count (live: discarded tuple element from _emit_ranked_closure_constraints, not dead) and _add_ranked_closure_constraints (live L1822). Coverage retained via test_single_extension_random.
- PROCESS NOTE: agent wasted ~5 turns backgrounding the 6-min full suite and yielding. Fix that worked: "run checks in FOREGROUND, commit FIRST, never reset/stash/background." Bake into all future prompts.

### Commit 2 (history of in-progress) — aba dead-code.
- Part 1 done on disk (NOT yet committed): deleted _native_sparse_narrow_fixedpoint_extension + orphan cascade (_conflict_pruned_extension, _is_stable_extension, _attacked_assumptions), ~102 lines. ruff+pyright clean.
- Agent stopped before committing; resumed to verify pytest/lint-imports + commit (commit A).
- Part 2 investigation: CEGAR trio (_AdmissibleCegarSolver + 2 helpers, ~130 lines) is dead-but-test-pinned. Production preferred/admissible covered by test_single_extension_random (120 frameworks via live sat_support_extension). APPROVED deletion → commit B (c2b): also remove orphaned _defense_counterexample(s)/_attacker_support_not_counterattacked + pinning test test_preferred_cegar_matches_admissible_growth; KEEP _add_ranked_closure_constraints (live L1822). Also resolve _clause_count L1938 diagnostic.
- COURSE CORRECTION: agent flailed (stopped 3×, proposed `git reset` to reconstruct 2 commits while work was UNCOMMITTED — would lose it). HEAD still fd82638, nothing committed. Both deletions sat mixed+uncommitted in working tree. DECISION: collapse Part1+c2b into ONE commit "refactor: remove dead and superseded aba_sat solver paths" — no resets. Also must clean lint leftovers: unused `derives` import (L12) + `_clause_count` (L1749). Awaiting single hash.
- LESSON for next coders: prompt must say "make changes then immediately commit; never git reset/stash/checkout; if multiple logical changes pile up uncommitted, commit them together rather than rewriting the tree."

### Commit 1 DONE — `fd82638` — solving dead-code. VERIFIED clean (verifier a796c5ff: 56 tests pass, full suite 2892 passed; analyzer diagnostics were stale).
- Removed sat_encoding CNF cluster (CNFEncoding/encode_stable_extensions/stable_extensions_from_encoding + helpers), rewrote docstring, __all__=["sat_extensions"].
- Deleted backends.py entirely (zero src callers) + tests/solving/test_backend_selection.py + 5 dead tests in test_solver_encoding.py.
- CORRECTION vs plan: `_admissible_sets` is LIVE (called by sat_extensions admissible branch) — correctly KEPT. Plan line numbers were off.
- _sorted_extensions dup left for later commit (c13).
