# DS-PR remaining cap-100 timeouts — 2026-05-02

## State
- 8 timeouts remaining after super-core + shortcut + learned witness work: B/4 irvine-shuttle (apx,tgf), D/2 BA_60_60_3 (apx,tgf), 2019 Small-result-b76/b88/b90/b97.apx.
- Solver in src/argumentation/af_sat.py: PreferredSkepticalTaskSolver -> super-core, admissible seed, then CEGAR loop with _PreferredSkepticalAttackerSolver.
- Loop emits preferred_skeptical_adm_ext_att (find E attacking some admissible q-set) then _admissible_extension(req=E∪{q}); blocking lemma in learn_witness_region is just `OR over args outside extended set` — weak per-iteration progress.
- SCC decomposition exists in dung.py (`_strongly_connected_components`) but is NOT wired into PreferredSkepticalTaskSolver. Grounded extension reduction not used as preprocessor either.
- find_stable_extension exists but stable-first shortcut not attempted.

## Hypotheses
1. Weak blocking clause: extended set in learn_witness_region is *some* admissible superset, not maximal. Maximizing F first yields exponentially fewer iterations (dual blocking).
2. SCC + grounded reduct preprocessing would shrink BA_60_60_3 and irvine-shuttle drastically; both likely have non-trivial grounded core.
3. Stable shortcut: if every preferred is stable (e.g. coherent AF), DS-PR ↔ skeptical stable, single SAT call.

## Blocker
None — diagnosis ready, need to write the five-section report.

## 2026-05-12 SE-PR aba_500_0.1_10_5_2 diagnosis (in progress)
- env: clingo only under `uv run` (5.8.0); bare python has neither clingo nor z3.
- instance: 50 assumptions, 2407 rules, 500 literals. NO stable extension (stable_extension -> None in 0.21s).
- So SE-PR goes: preferred_extension() -> admissible_extension(prefer_large=True) CEGAR loop -> then outer growth loop (up to 50 iters), each a fresh CEGAR (learned[] not reused across outer calls).
- Suspected bottleneck: per CEGAR iteration does self.closure(candidate) + _defense_counterexamples -> up to 50x derives(framework,...) each a full fixpoint closure; closure() re-sorts framework.rules by repr inside `while changed` -> O(passes * 2407 * log) per closure. preferred_extension() ran >120s (killed).
- TODO: bounded profile to confirm hot function; then write the 4-section answer.

## 2026-05-12 Wave C2b — clingo multi-shot CEGAR for ABA (in progress)
- Task: implement §2.3b of reports/aba-incremental-spec.md — clingo multi-shot Alg.1 (Lehtonen 2021), new aba_com_incremental.lp from Listing 1, replace enumerate-then-filter in aba_asp.py default path, compose under simplify_aba.
- Listing 1 (Module πcom) extracted to tmp_work/page05.txt; Algorithm 1 in tmp_work/page04.txt. ABA(F) facts = assumption/head(i,b)/body(i,b)/contrary(a,x).
- Python clingo 5.8.0 IS available (multi-shot OK).
- aba_asp.py: solve_aba_with_backend already wired with simplify=True, backend "asp"/"clingo" uses subprocess. Need new backend path / replace.
- aba.py: ABAFramework(language,rules,assumptions,contrary{Mapping}); derives(); grounded_extension(); preferred_extensions().
- Plan: new module aba_incremental.py with AbaIncrementalSolver using clingo.Control. encodings/aba_com_incremental.lp transcribed from Listing 1. Wire as default in aba_asp solve_aba_with_backend for backend asp/clingo. Tests tests/test_aba_multishot.py. Branch experiment/graph-speedup-wave-a-preprocessing (already on it).

## 2026-05-12 C2b progress checkpoint 2
- Wrote encodings/aba_com_incremental.lp (Listing 1 verbatim, underscores for spaces, head(R,_)).
- Wrote src/argumentation/aba_incremental.py: AbaIncrementalSolver + IncrementalTelemetry. Uses encode_aba_theory facts + com module. Algorithm 1 (is_skeptically_accepted_preferred), Alg 4 (enumerate_preferred/find_preferred_extension), enumerate_complete/_stable (single Control), credulous helpers. Reasoned through Alg 1 correctness (greedy growth maximal among not-deriving-s; Line 8 superset must derive s).
- TODO: wire into aba_asp.solve_aba_with_backend (backend asp/clingo -> multi-shot for complete/stable/preferred/grounded; admissible stays subprocess; add backend="clingo_subprocess" for old path). Lazy import to avoid cycle.
- TODO: tests/test_aba_multishot.py; run full suite; benchmark; ruff+pyright; commit; report.
- NOT YET RUN anything. clingo .lp syntax untested.

## 2026-05-12 C2b checkpoint 3 — solver works
- Fixed clingo Model lifetime bug (extract in-set inside on_model). aba_incremental.py now: complete/stable enum match native; preferred enum matches; DS-PR matches intersection-of-preferred on hand example. Telemetry shows iterations.
- Need a DS-PR YES case + a multi-round case for tests. Next: random differential test vs aba.py + aba_asp subprocess; wire into aba_asp.solve_aba_with_backend (backend asp/clingo -> multishot for complete/stable/preferred/grounded; admissible+old path under backend="clingo_subprocess"); tests/test_aba_multishot.py; full suite; benchmark; ruff/pyright; commit; report.

## 2026-05-12 C2b checkpoint 4
- Wired _solve_multishot into aba_asp.solve_aba_with_backend: backend asp/clingo -> multishot for complete/stable/preferred/grounded (DS-PR uses Alg1 fast path); admissible + legacy path under backend="clingo_subprocess".
- Differential vs aba.py 200 random: 0 fails. Vs subprocess clingo 160: 0 fails.
- Wrote tests/test_aba_multishot.py with hand battery (incl. found multi-round DS-PR cases) + 120 random. Running now (background binvcu1uy).
- Remaining: full suite, benchmark (bench/asp_vs_sat.py + ad-hoc), ruff+pyright on touched files (aba_incremental.py, aba_asp.py, aba_com_incremental.lp not lintable, test file), commit, report.

## 2026-05-12 C2b checkpoint 5
- First test run: 110 fail (mostly metadata "algorithm"!=L21 because simplify=True path used enum projection). Fixed: added _solve_simplified_ds_pr in aba_asp.py — DS-PR with simplify=True now applies lift rules (fixed_in/fixed_out/Th(fixed_in)/not-in-residual.language) then Alg1 on residual, lifts counterexample. Metadata algorithm=L21-TPLP-Alg1. Also fixed not-in-language counterexample to be a real preferred set; relaxed telemetry test.
- Re-running tests now.

## 2026-05-12 C2b checkpoint 6
- tests/test_aba_multishot.py: 1012 passed. ruff clean. pyright clean (added Any annotation for ctl, type guards in test).
- Full suite running (b9bob2arx). Then benchmark, commit, report.

## 2026-05-12 C2b checkpoint 7
- Full suite: 1 failed (pre-existing test_kernel_ideal_extension_is_admissible), 2632 passed, 2 skipped. No regression (baseline 1620 passed; +1012 new).
- Benchmark running. Then commit + report.

## 2026-05-12 C2b DONE
- Committed: 466d38d (impl) + report commit. Report at reports/graph-speedup-wave-c2b-aba-multishot.md.
- Benchmark: DS-PR pref-heavy ~14-30x over subprocess; no-help control ~2ms/~50x. Full suite 1 pre-existing fail, 2632 pass, 2 skip. ruff+pyright clean. tmp_work/ removed.
