# Wave A — AF preprocessing layer (2026-05-12)

## State
Building `src/argumentation/preprocessing.py` — `simplify_af(framework, semantics)` -> (residual, fixed_in, lift_fn).

## Findings
- Z3 AF path choke point: `af_sat.py` 7 `find_*` functions + `PreferredSkepticalTaskSolver` + `PreferredSuperCoreSolver`. All take a full `ArgumentationFramework`, build `AfSatKernel`.
- `solver.py` dispatches to those `find_*` for SE/DC/DS Dung tasks (lines ~286-460).
- ASP Dung path: only via ASPIC+ projection in `aspic_encoding.py` ~266-324 (`dung_{complete,stable,admissible}.lp`). No standalone "AF -> ASP" entry. Will wire simplify into that projection branch.
- `dung.grounded_extension` O(V+E) BFS exists. `_is_acyclic` in af_sat.py. `af_revision.stable_kernel`/`baumann_2015_kernel` exist.
- Brute-force oracle: `dung.{complete,preferred,stable,semi_stable,stage,grounded}_extensions`, `ideal_extension`.

## Plan
1. preprocessing.py: grounded reduct + self-attacker removal + isolated-arg elim. Acyclic shortcut handled by callers (already partially). Symmetric: detect + TODO. Kernel: skip (TODO, soundness uncertainty).
2. Wire into af_sat.py find_* with `simplify=True` default.
3. Wire into aspic_encoding.py dung projection.
4. Oracle tests in tests/.
5. Run suite, bench, lint, commit.

## Env / baseline (2026-05-12)
- `pip install -e .` needed. `gunray` missing => test_datalog_grounding.py is pre-existing collection error, exclude it.
- Baseline full suite running in background bs4oayut9 (809 tests minus datalog).
- ruff: not configured in pyproject (no [tool.ruff]); installed ruff 0.15.12, default config; `ruff check src/...` passes. pyright 1.1.407 installed.
- bench/asp_vs_sat.py only does ABA-chain + ASPIC-chain, NOT Dung AF SAT. No ICCMA corpus in repo. -> will write ad-hoc Dung AF bench script, note ICCMA not run.

## BASELINE RESOLVED
- z3-solver was NOT installed -> 108 spurious fails. Installed z3-solver 4.16.0. Clean master now green.
- Also installed: ruff 0.15.12 (no [tool.ruff] in pyproject), pip install -e .

## Wiring progress
- preprocessing.py written (grounded reduct + pure-self-loop-sink removal; symmetric detected+TODO; kernels TODO).
- af_sat.py: added `_prepare` helper + `simplify=True` param on find_stable/find_complete/find_preferred/find_semi_stable + is_preferred_skeptically_accepted. Still TODO: find_stage, find_ideal. Then run tests.

## Bug found & fixed
- Pure self-loop sink removal UNSOUND for stable (sink is the obstruction to stable existing). Gated off for stable.
- 7 tests in test_solver_encoding.py fail: 1 was the real stable bug (now fixed by gating); 6 are internal-telemetry tests (trace counts / "uses direct ideal utilities" / range-shortcut-internals) that legitimately change because the SAT call now runs on the residual. Plan: add `simplify=False` to those 6 telemetry tests — they exercise kernel mechanics, not the public contract; public result is unchanged.

## Soundness gating finalized
- GROUNDED_REDUCT_SEMANTICS = {complete, preferred, stable, semi_stable, grounded, ideal}.
- NOT stage (conflict-free, not complete; counterexample {a,b,c},{(a,a),(b,c),(c,a)}: stage {c}, grounded {b}).
- NOT admissible ({} is admissible, need not contain G).
- self-loop-sink removal: all semantics EXCEPT stable.
- test_solver_encoding.py: all 55 pass. Added simplify=False to 4 internal-telemetry tests.
- Still TODO: wire ASP path (aspic_encoding.py dung projection branch), oracle tests, full suite, bench, lint, commit.

## ASP wiring
- Wired into aspic_encoding.py dung-projection branch: simplify_af(projection.framework, semantics), lift extensions back, empty-residual short-circuit.
- clingo was NOT installed -> ASPIC ASP tests fail at baseline too. Installed clingo 5.8.0. Need to re-baseline ASPIC then re-test.
- Env deps installed for this task: z3-solver 4.16.0, clingo 5.8.0, ruff 0.15.12, pip install -e .

## Full-suite state (after wiring + oracle tests)
- 4 fails: 1 = test_kernel_ideal_extension_is_admissible (PRE-EXISTING bug in find_ideal_extension itself, reproduces on clean master with simplify=False; Hypothesis example a→aa,a→b,aa→a,aa→b,b→c returns {c} which is not admissible). Out of scope; note in report.
- 3 = test_iccma_runner DS-PR streaming tests: my preprocessing bypasses SAT for tiny DS-PR instances so no sat_check events emitted. FIX: emit a trace event from is_preferred_skeptically_accepted when the simplify shortcut decides. In progress.
- test_preprocessing.py: 103 pass. ASPIC ASP: 111 pass.

## DONE state
- Full suite: 909 pass, 2 skip, 1 fail = test_kernel_ideal_extension_is_admissible (PRE-EXISTING, reproduces on clean master, bug in find_ideal_extension itself, not preprocessing).
- ruff: my files clean. 18 pre-existing ruff errors elsewhere (project has no [tool.ruff], doesn't gate). pyright: my files 0 errors.
- ICCMA runner telemetry: fixed by emitting SATCheck from preprocessing shortcut + adjusting one self-loop-sink test instance.
- Next: ad-hoc Dung AF benchmark before/after, then commit, then report.

## Correctness notes
- Grounded reduct valid for complete/preferred/stable/semi-stable/stage/ideal/grounded: every extension of these contains grounded ext and excludes grounded-attacked. Residual = AF minus (G ∪ G+). Lift = union fixed_in back.
  - WAIT: stage/naive are NOT admissibility-based — stage need not contain grounded. CHECK before applying grounded reduct to stage. Actually stage extensions: conflict-free + max range. Grounded args are unattacked => in every max-range cf set? Unattacked arg a: any cf set not containing a — can add a (still cf, range grows or stays) => not range-maximal unless a already in range, but a unattacked so a in range only if a in S. So every stage ext contains all unattacked args. Then args attacked by those are OUT (cf). Iterate => stage DOES respect grounded reduct. OK but be careful: the reduct removes G∪G+; residual stage extensions then unioned with G. Need: stage(AF) = { G ∪ E : E ∈ stage(residual) }. Plausible but VERIFY via oracle tests — that's what tests are for.
- Self-attacker: a with (a,a): never in any cf set => OUT for all semantics we support (all are cf-based). Safe. Remove a and all its attacks. But a being OUT doesn't force anything else IN. Just drop from encoded instance, never in any extension.
- Isolated arg (no in, no out edges): in every cf-maximal-ish ext. For complete/preferred/stable/semi-stable/stage/grounded/ideal: isolated arg is unattacked => in grounded => already handled by grounded reduct. So isolated-elim is subsumed; implement anyway as it's same mechanism.
