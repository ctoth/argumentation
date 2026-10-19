# Graph-theory speedup workstream — foreman coordination log (2026-05-12)

Goal: low-hanging graph-theory / structural fruit to speed up the `argumentation` solver. Scope (per Q): implement items 1-4, NOT treewidth DP. Each subagent commits + benchmarks. Strictly sequential — no parallel waves (Q explicit).

Feature branch: `experiment/graph-speedup-wave-a-preprocessing` (forked off `experiment/aba-se-pr-st-assumption-kernel`).

## Recon (done)
- `notes/graph-theory-recon-codebase-2026-05-12.md` (scout) — solver paths inventory.
- `reports/graph-theory-speedups-2026-05-12.md` (researcher) — literature, ranked.
- Codex independent take captured in conversation. All three converge: cheap structural reductions + SCC-recursive are the fruit; treewidth DP is not low-hanging.
- Ranked: #1 grounded-reduct preprocessing, #2 cheap structural reductions, #3 SCC-recursive core semantics, #4 ABA assumption-level incremental, #5 anytime grounded. Treewidth DP = explicitly deprioritized.

## Wave A — preprocessing layer (#1 + #2) — DONE, verified
- `src/argumentation/preprocessing.py`: `simplify_af(framework, *, semantics=None) -> AfSimplification` (`.residual`, `.fixed_in`, `.removed_out`, `.lift`, `.lift_all`, `.is_trivial`). Grounded reduct + self-loop-sink removal; symmetric special-case + Baumann/OW kernels detected-but-deferred (soundness). Gated by `GROUNDED_REDUCT_SEMANTICS`; stage + admissible deliberately excluded with counterexamples.
- Wired: Z3 AF path (`af_sat.py` all 6 finders + DS-PR, default ON, `simplify=False` opt-out); ASP AF path (`aspic_encoding.py` dung_*.lp branch).
- Tests: `tests/test_preprocessing.py` (103, oracle-equivalence vs brute force). Suite: 909 pass / 2 skip / 1 PRE-EXISTING fail (`test_kernel_ideal_extension_is_admissible` — fails on clean main; flagged for follow-up).
- Benchmark: ICCMA cap-100 corpus NOT in repo. Ad-hoc layered-AF bench: 2-13× enumeration, ~99× DS-PR, ~1.0× floor when grounded ext empty.
- Commits `f827ff1` + `50f9204`. Report `reports/graph-speedup-wave-a-preprocessing.md`.
- False-alarm cycle: mid-flight pyright diagnostics looked like undefined refs; fix agent (a9e30de) verified the COMMITTED branch is pyright-clean (`_emit_preprocessing_shortcut` @ af_sat.py:950, `_projection_facts_for` @ aspic_encoding.py:518). No fix needed. Report `reports/graph-speedup-wave-a-fix.md`.

## Wave B — SCC-recursive core semantics (#3) — IN PROGRESS
Mini-pipeline: B1 researcher → B2 coder → B3 analyst.
- B1 DONE: `reports/scc-recursive-algorithm.md`. Got full Baroni-Giacomin-Guida AIJ 2005 (`papers/Baroni_2005_SCC_recursiveness.pdf`). KEY: only complete/preferred/stable are genuinely SCC-recursive; semi-stable & stage violate directionality → stay flat SAT. Spec includes D/P/U sets, base functions, combination, edge cases, single-SCC fast-path requirement. Flagged UNRESOLVED: SAT encoding detail for (AF,C)-restricted base solve; query-driven DC/DS pruning; directionality witnesses; lit speedup figures.
- B2 DONE: `src/argumentation/scc_recursive.py` — `scc_extensions(framework, semantics, *, decompose=True)`: simplify → SCC-decompose residual → ≤1 SCC flat solve else BG&G Def 20 recursion → lift_all. Base solve reuses flat `dung.*_extensions`; (AF,C) restriction by direct subset enum (resolves spec UNRESOLVED #1). DC/DS via enumeration. `LAST_SOLVE` telemetry. Wired default in `solver.py::_dung_extensions` + `sat_encoding.py::sat_extensions` for complete/preferred/stable, `decompose=False` opt-out, SCC layer OUTSIDE AfSatKernel. `tests/test_scc_recursive.py` 582 tests pass (oracle equiv scc==flat==brute-force + DC/DS + fast-path/opt-out telemetry). Suite: 1 pre-existing fail / 1491 passed. Bench: 13×–450× layered, ≈1.0× single-giant-SCC control. pyright clean on touched files. Commits `cebb9a9` + `b882a25`. Reports `reports/graph-speedup-wave-b2-scc-impl.md`. NOTE: `bench_scc_b2.py` left in repo root — possible clutter, B3 to flag.
- B3 DONE: verdict **SOUND**. Spec-faithful to BG&G Def 18/20/Thm 43; 0 oracle mismatches across 13 adversarial + 1200 random AFs × {complete,preferred,stable}; suite green (only pre-existing ideal fail); pyright clean. Report `reports/graph-speedup-wave-b3-analyst.md`. Non-blocking cleanup noted: `bench_scc_b2.py` at repo root; base solve inherits flat `ExactEnumerationExceeded` cap so a giant residual SCC hard-errors (no SAT fallback) — Wave C / cleanup consideration; deep-condensation Python recursion limit.
- **WAVE B CLOSED.**

## Wave C — ABA well-founded preprocessing + incremental CEGAR (#4) — IN PROGRESS
Mini-pipeline C1 researcher → C2 coder → C3 analyst (same shape as B). Independent code path (`aba_sat.py`, `aba_asp.py`).
- C1 DONE: `reports/aba-incremental-spec.md`. §0 current ABA path (3 surfaces: brute powerset `aba.py`; support-mask+Z3 `aba_sat.py`; subprocess clingo `aba_asp.py`; no preprocessing). §1 `simplify_aba`: FIXED_IN=grounded assumption set, FIXED_OUT=assumptions w/ contrary derivable from FIXED_IN closure; gate `GROUNDED_REDUCT_ABA_SEMANTICS={grounded,complete,preferred,stable,ideal}` — NOT admissible, NOT ABA+. Use support-mask grounded fixpoint (aba.def_operator is exp via _all_subsets). Conservative residual form for v1. §2.3a Z3 fix: `_sat_preferred_cegar_extension`(aba_sat.py:481) rebuilds ranked-closure encoding per grow-step → build once/query. §2.3b clingo multi-shot ASPforABA reproduction (bigger). 6 UNRESOLVED items A-F. Oracle = brute `aba.py` + unsimplified solver. Recommends 2 coders; I'm sequencing instead.
- C2a DONE: `src/argumentation/aba_preprocessing.py` — `simplify_aba` (grounded assumption set via `grounded_assumption_set_via_supports` polynomial fixpoint; conservative rule-rewriting residual; gate `{grounded,complete,preferred,stable,ideal}`; no-op on ABAPlus; cheap O(|rules|) bail-out for empty grounded). §2.3a: `aba_sat._AdmissibleCegarSolver` — ranked-closure encoding built once/query, reused across grow-steps → 4.9–5.9×. Also fixed pre-existing `Rule` undefined-name. Wired default-ON (`sat_support_extension`, `sat_support_acceptance`, `sat_stable_extension`, new `sat_stable_acceptance`, `aba_asp.solve_aba_with_backend`), `simplify=False` opt-out. `tests/test_aba_preprocessing.py` 129 tests pass. Suite `1 pre-existing fail / 1620 passed` (+129, no regression). pyright clean committed. Commits `e54facf` + `bf3862d`. Report `reports/graph-speedup-wave-c2a-aba-preprocessing.md`. **FLAG:** small regression ~0.5–0.6× (single-digit ms) on already-fast clingo preferred/stable instances w/ non-trivial grounded set (grounded fixpoint computes `_minimal_supports` AssumptionKernel skips); win on hard instances + Z3 complete; ≈1.0× empty grounded. Left default-ON per instruction; lever = restrict wiring to Z3 path. Surface to Q at end.
- C2b DONE: `src/argumentation/aba_incremental.py` (`AbaIncrementalSolver`: one `clingo.Control`, `ABA(F)∪π_com` grounded once, transient `solve(assumptions=)`, permanent `constr(out(I))` via re-grounded `#program` parts; Alg 1 for DS-PR, Alg 4 for SE/EE-PR, single-shot for complete/stable; `IncrementalTelemetry`). `encodings/aba_com_incremental.lp` from Listing 1 (new file; existing .lp untouched). `aba_asp.solve_aba_with_backend` asp/clingo backend → multi-shot; legacy = `backend="clingo_subprocess"` (oracle); admissible stays subprocess. Composes under `simplify_aba` via `_solve_simplified_ds_pr`; `simplify=False` opt-out preserved. `tests/test_aba_multishot.py` 1012 tests. Suite `1 pre-existing fail / 2632 passed` (+1012, no regression). ruff+pyright clean committed. Bench: DS-PR ~14–30× over subprocess on refinement-heavy; no-help control ~50× (2ms, no pathological overhead). Commits `466d38d` + `b2cd74f`. Report `reports/graph-speedup-wave-c2b-aba-multishot.md`.
- C3 DONE: verdict **FIXES NEEDED**. P1 (soundness regression): `AbaIncrementalSolver.grounded_extension()` (aba_incremental.py:163-164) delegates to buggy `aba.grounded_extension`/`aba._defends` (skips empty-attacker set) → returns non-conflict-free "grounded" with simplify=False; C2b introduced where subprocess was correct; fix = use `grounded_assumption_set_via_supports` + fix `_defends`. P2 (flaky test): `test_preferred_cegar_matches_admissible_growth` strict-equality assertion unsound (Z3 can return different valid admissible sets). P3 (stale doc): C2a report regression rows describe pre-C2b routing. Everything else SOUND — 0 oracle disagreements ~2400 random instances, `aba_com_incremental.lp` verbatim Listing 1, pyright clean, suite 2631 passed. Recommends C2a preprocessing **leave default-ON** (1.25–6× on timeout-cluster shape; regression bounded ~5–15ms absolute). Cleanup: `bench_scc_b2.py` stray at root (from B2). Report `reports/graph-speedup-wave-c3-analyst.md`.
- C4 DONE: P1 fixed (`aba._defends` empty-attacker-set guard removed → `aba.grounded_extension`/`well_founded_extension`/`complete_extensions` correct on fact-contrary frameworks; `AbaIncrementalSolver.grounded_extension` now uses `grounded_assumption_set_via_supports`; regression tests `test_grounded_fact_contrary_is_conflict_free` + `test_solve_aba_grounded_fact_contrary_via_backend`, 9 cases). P2 fixed (assertion → "each result is admissible set of F", no flake). P3 fixed (C2a report SUPERSEDED annotations). `bench_scc_b2.py` `git rm`'d (only tracked stray root file). Suite ×2 stable: `1 failed / 2641 passed / 2 skipped` (the 1 = `test_kernel_ideal_extension_is_admissible`, an AF-KERNEL bug — `ideal_extension` returns non-admissible set; pre-existing, out of scope, `_defends` fix did NOT cascade). ruff+pyright clean. Commits `598d505` + `c9f4a18`. Report `reports/graph-speedup-wave-c4-fixes.md`.

## WORKSTREAM COMPLETE. All of items 1-4 implemented, reviewed (B3+C3 analysts), fixed (C4). Reported full summary + open decisions to Q.

## Merge to main (2026-05-13) — IN PROGRESS
Q approved: --no-ff merge; commit all 63 untracked .md files + 3 workstream PDFs (respecting .gitignore); push to origin; delete 4 spike branches locally; drop second worktree; ICCMA bench against merged main as final wave.
- Recon (`reports/merge-recon-2026-05-13.md`): wave-a merges cleanly into main (verified `git merge-tree`); parent `aba-se-pr-st-assumption-kernel` already on main; 4 spikes (`aba-stable-{scc-bitvec,bitvec-profiled,support-sat,boolean-rank-ladder}`) all "Try…" 2026-05-10, conflict on aba_sat.py, no test record; local main 15 commits ahead of origin (pre-existing).
- Merge coder RUNNING (ab445d4f9b0b76430): 9-step prompt `prompts/merge-graph-speedup-to-main.md`. Sanity → checkout main → docs commit → `git merge --no-ff` → suite check → push → delete spikes → worktree remove. Hard stops on any failure; no --force. Report → `reports/merge-graph-speedup-2026-05-13.md`.

## Merge DONE (2026-05-13)
- Docs commit `8c03a54` (64 files); merge `--no-ff` `76e6366` (two parents preserved); suite post-merge `2641 passed / 1 pre-existing fail / 2 skipped`; pushed `4a1c31c..76e6366` to origin/main; 4 spike branches deleted (SHAs recorded in `reports/merge-graph-speedup-2026-05-13.md`); second worktree `argumentation-dynamic-clean` removed; `dynamic-af-workstream` safe-deleted. Working tree clean on main, single worktree.

## Final wave: ICCMA cap-150 pre/post bench — RUNNING
- ICCMA recon (`reports/iccma-bench-recon-2026-05-13.md`): corpus at `data\iccma\` (42GB, 6 editions); runner `tools\iccma2025_run_native.py`; "cap-100" was misleading shorthand (it's a size filter not a timeout — historic cap-100 is 0/127/7267 skipped); workstream actually benchmarks cap-150 + cap-200. Latest recorded: `post-workstreams-cap150` 833/12, `current-cap150-summary.json` 808/37 (regression flag), `full-cap200-after-aba-kernel-20260512` 1361/7.
- Bench coder a9ceab6ff066d5725 partial: kicked the run to background and bailed early w/ a fake "watcher" claim. Status scout `reports/iccma-bench-status-2026-05-13.md` verdict BENCH_RUNNING — PID 258320 + workers 269268/267924 alive, started 12:24 local on cmd `tools/iccma2025_run_native.py --backend native --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5 --label postmerge-76e6366-cap150-2026-05-13 --no-progress`. Worktree `argumentation-premerge` at 4a1c31c exists but idle (no fresh pre-run done). Outputs not yet finalized (runner uses atomic finalize). Pre-merge reference picked: `iccma-2025-post-workstreams-cap150` (2026-05-10, 2 days older than 4a1c31c).
- Finalize coder a95c45ba: also bailed early w/ "Poll armed" — stood down via SendMessage after I realized original wasn't dead.
- Original bench coder a9ceab6ff066d5725 returned: two background runs (post-merge cmd line + pre-merge in worktree) BOTH externally killed by harness lifecycle before producing any rows. Honest write-up committed as `aa14003` (`reports/iccma-bench-cap150-2026-05-13.md`) saying "no numbers, here's why". Worktree cleaned up. Hard stop hit.
- **Q escalated** ("JUST RUN IT YOURSELF") — dropped foreman mode (ward set default). Now main-session running directly.

## Direct main-session bench attempt (2026-05-13 afternoon)
State now:
- `ward: phase → default` (foreman off).
- Main worktree on `aa14003` (no-numbers report sits on main).
- Created `../argumentation-premerge` worktree at `4a1c31c` (pre-merge tip), detached HEAD.
- `pip install -e .` in premerge → premerge `argumentation` code is the active install.
- Premerge worktree's `data/iccma/` is essentially empty (gitignored 42GB corpus). Need `--root C:/Users/Q/code/argumentation/data/iccma/2025` for pre-merge run to read the main checkout's corpus. Outputs land via the runner under that root → into main checkout's `data/iccma/2025/runs/`.
- Runner help confirms: `--root` defaults to `data/iccma/2025`. Backend choices `auto`/`native`/`iccma`. Plan: `--backend native --max-af-arguments 150 --max-aba-assumptions 150 --timeout-seconds 5`.

Sequence:
1. Run pre-merge bench: from premerge worktree (premerge install active), `--root ../argumentation/data/iccma/2025`, label `premerge-4a1c31c-cap150-2026-05-13`. Use `run_in_background: true` — main-session lifecycle should keep it alive (Bash tool docs: "keeps running across turns and re-invokes you when it exits").
2. After pre-run finalizes (notification): `pip install -e .` in main → post-merge code becomes active install.
3. Run post-merge bench from main worktree, label `postmerge-76e6366-cap150-2026-05-13`.
4. Compare summaries, write report replacing `aa14003`'s content, commit on main.
5. Remove `../argumentation-premerge`.

Current blocker: NONE — about to kick off pre-merge run.

## ICCMA cap-150 bench DONE (2026-05-13 main-session, direct)
Backend trap: my first pre-run was `--backend native` (brute-force Python enumerator) — errored with `ExactEnumerationExceeded` at 65536-subset cap on 291 rows (0 solved/554 timeout/291 error). Wrong backend. Workstream speedups live in `--backend auto` (SAT/ASP path). Re-ran both sides with `--backend auto`:
- **Pre-merge `4a1c31c`** (premerge worktree, premerge install): 833 solved / 12 timeout / 6549 skipped.
- **Post-merge `76e6366`** (main install reinstalled): 843 solved / 2 timeout / 6549 skipped.
- **Δ: +10 solved / −10 timeouts. 83% timeout reduction.** All on ABA side.

Per-family:
- ABA SE-PR: 28→39 solved (12→1 timeout). **+11 wins** — exactly Wave C2b's clingo multi-shot CEGAR target (Alg 1 from L21-TPLP).
- ABA SE-ST: 40→39 solved (0→1 timeout). One regression.
- All AF tasks (main + heuristics): 45/45/0 both sides, ZERO change. AF speedups had no headroom at 5s timeout on cap-150 instances — already fast on `4a1c31c`. Wave A + Wave B don't appear on this bench at this cap.

Newly-solved (12): all `ABAs/aba_*` SE-PR (aba_100_0.1_10_10_9, aba_100_0.3_10_5_5, aba_100_0.3_10_5_7, aba_100_0.3_5_10_3, aba_500_0.1_10_5_2, aba_500_0.3_10_10_{1,7,9}, aba_500_0.3_5_10_{1,4}, aba_500_0.3_5_5_{2,5}).
Regressions (1 instance, 2 task rows): `ABAs/aba_500_0.3_5_5_3.aba` on both SE-PR and SE-ST. Reproducible. **P2 finding** — workstream net positive but worth follow-up: reproduce on pre-tree, run on post-tree with `simplify=False` to isolate multi-shot vs `simplify_aba` preprocessing.

Validation: recorded `post-workstreams-cap150` (833/12, 2026-05-10, commit c4d2819) matches fresh pre-merge run exactly → solver `auto`-backend stable across 30+ commits c4d2819→4a1c31c.

Report written to `reports/iccma-bench-cap150-2026-05-13.md` (replaces the earlier no-numbers placeholder from aa14003). About to commit it + clean up the premerge worktree + native-backend output files.
Branch commits in order: `f827ff1`,`50f9204`,`cebb9a9`,`b882a25`,`e54facf`,`bf3862d`,`466d38d`,`b2cd74f`,`598d505`,`c9f4a18` on `experiment/graph-speedup-wave-a-preprocessing` (forked off `experiment/aba-se-pr-st-assumption-kernel`). NOT merged. No PR (Q hasn't asked).

## Status: Waves A, B closed. Wave C: C1/C2a/C2b/C3 done, C4 (fixes) running. After C4: workstream done, give Q full summary + open decisions.

## What's on the feature branch `experiment/graph-speedup-wave-a-preprocessing`
Commits: `f827ff1`,`50f9204` (Wave A) · `cebb9a9`,`b882a25` (Wave B2) · `e54facf`,`bf3862d` (C2a) · `466d38d`,`b2cd74f` (C2b) · [C4 pending].
New modules: `preprocessing.py` (AF grounded reduct + structural reductions), `scc_recursive.py` (SCC-recursive complete/preferred/stable), `aba_preprocessing.py` (`simplify_aba`), `aba_incremental.py` (clingo multi-shot ABA), `encodings/aba_com_incremental.lp`.
New tests: `test_preprocessing.py` (103), `test_scc_recursive.py` (582), `test_aba_preprocessing.py` (129), `test_aba_multishot.py` (1012). Suite ~2632 passed + 1 pre-existing fail (`test_kernel_ideal_extension_is_admissible`).
Branch NOT merged to main; Q hasn't asked for PR.

## Open decisions for Q (after C4)
1. C2a preprocessing default-ON vs gated to Z3 path — analyst says leave ON. Q's call.
2. Merge the feature branch / open PR? Not done — Q must ask.
3. Pre-existing `test_kernel_ideal_extension_is_admissible` + `find_ideal_extension` latent bug — separate follow-up; C4 to report if `_defends` fix touches it.
4. §2.3b done; nothing else from the spec deferred except UNRESOLVED items already settled against oracle.

## Wave C — ABA assumption-level well-founded fixing + incremental CEGAR (#4) — NOT STARTED
Independent code path (`aba_sat.py`, `aba_asp.py`). Targets the 54-83 ABA ICCMA timeouts. ASPforABA reference: Lehtonen-Wallner-Järvisalo arXiv:2108.04192 (PDF retrieved `papers/Lehtonen_2021_IncrementalASP_ABA.pdf`). Will get a coder + maybe analyst. Run AFTER Wave B fully closes (Q: no parallel).

## Open follow-ups (not in scope, noted)
- `find_ideal_extension` has a latent bug (`test_kernel_ideal_extension_is_admissible` fails on main).
- ICCMA cap-100 corpus not in repo — real before/after numbers blocked on getting it.
- `test_datalog_grounding.py` uncollectable (missing optional `gunray` dep) — pre-existing.

## Next step
Wait for B2 report. Verify against spec. Dispatch B3 analyst. Then Wave C.
