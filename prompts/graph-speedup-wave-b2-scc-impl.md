# Wave B2 — Implement SCC-recursive solving for complete / preferred / stable

You are a coding subagent. Working dir: `C:\Users\Q\code\argumentation`. Work on branch `experiment/graph-speedup-wave-a-preprocessing` (the feature branch; Wave A committed `f827ff1`/`50f9204` there). `git checkout` it if you're not on it. Commit your work there. Do NOT create a new branch.

## Spec — read these first, in order

1. `reports/scc-recursive-algorithm.md` — **this is your specification.** Implement exactly what it says. It is based on Baroni-Giacomin-Guida AIJ 2005 (`papers/Baroni_2005_SCC_recursiveness.pdf`). Do not deviate from it. Where it flags something "UNRESOLVED", treat the oracle tests as the arbiter and document your choice.
2. `reports/graph-speedup-wave-a-preprocessing.md` + `notes/graph-speedup-wave-a-preprocessing.md` — the Wave A preprocessing layer you build on.
3. Source: `src/argumentation/preprocessing.py` (`simplify_af` → `AfSimplification` with `.residual`, `.lift`, `.lift_all`), `src/argumentation/dung.py` (`_strongly_connected_components` ~L410, `_subframework`, `_component_defeated` ~L491, the cf2/stage2 SCC loop ~L516-579 — note: shape reuse only, the base function differs), `src/argumentation/af_sat.py` (the flat Z3 solve path — `AfSatKernel`, the `find_*_extension` finders, `is_preferred_skeptically_accepted`).

## What to build

SCC-recursive decomposition for the three semantics the spec says are genuinely SCC-recursive: **complete, preferred, stable**. (Semi-stable, stage, grounded, ideal, admissible: leave on their existing paths — do NOT touch them.) Per the spec:

- Input is the **residual AF after `preprocessing.simplify_af`** (compose: simplify → SCC-decompose the residual → solve per SCC → lift through the SCC layer → lift through the preprocessing layer).
- Compute the condensation, process SCCs in topological order. For each SCC `S`, compute the `D`/`P`/`U` sets from already-decided upstream arguments per the spec's definitions, restrict `S` accordingly, solve the **base semantics on that single SCC** by calling the existing flat Z3 path (`af_sat.py`) — do not reimplement the flat solver. Combine per-SCC partial results by cross-product over the topological order, exactly as the spec describes (including the preferred per-SCC maximality subtlety).
- **Single-SCC detection**: if the residual is one SCC (or trivially small), skip the decomposition machinery entirely and call the flat path directly — no overhead. Same for empty residual.
- This must support: enumeration (all extensions), and the credulous/skeptical decision tasks (DC/DS) for these semantics — at minimum, route DC/DS through enumeration if a smarter query-driven pruning is in the "UNRESOLVED" bucket; a correct-but-not-maximally-clever DC/DS is fine for this wave.

### Hard correctness directive
For complete, preferred, stable: `scc_solve(af)` (with preprocessing + SCC decomposition) lifted back to the full argument set MUST equal the existing flat-path result EXACTLY — same set of extensions, same DC/DS answers — on every AF. No approximation. If the spec's algorithm and the oracle disagree, the algorithm as you implemented it is wrong; fix it, don't fudge the test.

### Wiring directive
Make it the default path for complete/preferred/stable solving (with a `scc=False` / `decompose=False` opt-out flag, default ON), composed under the Wave A `simplify` (so the order is: simplify → SCC → flat). It must be transparent — callers (`solver.py`, `iccma*`) get identical results, faster. If composing cleanly with the existing `AfSatKernel` incremental-solver design is awkward, put the SCC layer *outside* the kernel (decompose first, then create kernels per SCC) rather than threading it through — but say what you did in the report.

Module placement: your call. A new `src/argumentation/scc_recursive.py`, or extend `preprocessing.py` / `af_sat.py`. State where and why.

## Tests

New `tests/test_scc_recursive.py`:
- Oracle equivalence: for complete/preferred/stable, on (a) a hand-built battery of multi-SCC AFs — long grounding chains feeding cycles, diamond condensations, SCCs of size 1/2/3+, self-loops inside SCCs, an SCC attacked by an UNDEC upstream argument (the `D`-set case), parallel independent SCCs — and (b) ≥150 random AFs of varied size/density, assert `scc-path result == flat-path result == brute-force-reference result` (sets of extensions, and DC/DS for a sampled argument). Use the existing brute-force enumerator as the third oracle.
- A test that single-SCC and empty-residual inputs take the flat path (assert via telemetry / a spy / behavior, not just timing).
- Run the full suite. Baseline per Wave A report: `1 failed, 909 passed, 2 skipped` (`--ignore=tests/test_datalog_grounding.py`); the 1 failure (`test_kernel_ideal_extension_is_admissible`) is pre-existing — do not regress beyond that. Requires `z3-solver` + `clingo` installed (`pip install z3-solver clingo`; `pip install -e .`).

## Benchmark (before/after)

- BEFORE: on a battery of layered / many-small-SCC AFs (and a couple of single-giant-SCC AFs as the no-help control), time complete/preferred/stable enumeration + a DS-PR query on the flat path (`scc=False`).
- AFTER: same, `scc=True` (default). Record the speedup, and confirm the single-giant-SCC control shows ≈1.0× (no regression).
- Note that the ICCMA cap-100 corpus is not in the repo (Wave A established this) — use generated instances; `bench/instance_gen.py` exists.

## Definition of done

1. SCC-recursive layer implemented per `reports/scc-recursive-algorithm.md`, wired as default for complete/preferred/stable, composed under Wave A's simplify, with opt-out.
2. New oracle tests pass; full suite no worse than the Wave A baseline.
3. Before/after benchmark recorded, including the no-help control.
4. Precommit/lint (`ruff`, `pyright`) clean on every file you touched — run pyright on the touched files and paste the output into your report. (Repo has pre-existing findings elsewhere; don't touch those.)
5. `git add` + `git commit` on the feature branch. **Commit hash in the report.**
6. Report → `reports/graph-speedup-wave-b2-scc-impl.md`: what you built, where wired, how it composes with the kernel, which spec "UNRESOLVED" items you resolved and how, test results, before/after benchmark (incl. control), pyright output on touched files, commit hash, and anything Wave C (ABA) or a reviewer needs to know.

## Hard stops

- Do NOT implement SCC decomposition for semi-stable, stage, ideal, grounded, admissible — the spec says those aren't (cleanly) SCC-recursive. Leave them.
- Do NOT touch ABA / ASPIC code paths.
- Do NOT modify the Wave A preprocessing logic — only compose with it.
- If the spec turns out to be wrong or incomplete in a way you can't resolve against the oracle, STOP and report — do not invent algorithm.
- If the suite is red beyond the documented baseline on a clean checkout before your changes, STOP and report.
