# Wave C2b — clingo multi-shot incremental CEGAR for ABA (ASPforABA reproduction)

You are a coding subagent. Working dir: `C:\Users\Q\code\argumentation`, branch `experiment/graph-speedup-wave-a-preprocessing` (HEAD after C2a is `bf3862d`). `git checkout` it; commit there; do NOT branch.

## Spec — read first

- `reports/aba-incremental-spec.md` — implement **§2.3b ONLY** (the clingo multi-shot loop = the ASPforABA reproduction). §1 and §2.3a are already done by Wave C2a — do not redo them. Item F in the spec's UNRESOLVED list is this work; settle it against the oracle.
- `reports/graph-speedup-wave-c2a-aba-preprocessing.md` — has a "what Wave C2b needs to know" section. Read it. The `simplify_aba` layer (`src/argumentation/aba_preprocessing.py`) already exists and is wired; compose under it (simplify → multi-shot solve on the residual → lift), exactly as C2a composed under it.
- `papers/Lehtonen_2021_IncrementalASP_ABA.pdf` (arXiv:2108.04192) — Algorithm 1, Listing 1. This is the algorithm. Read it.
- Source: `src/argumentation/aba_asp.py` (currently does one-shot subprocess clingo over `.lp` files — the spec §0/§2.3b says to replace the enumerate-then-filter with a multi-shot loop), `src/argumentation/solver_adapters/clingo.py` (the clingo glue — does it expose the Python `clingo` module or only subprocess? the spec/recon should say; if only subprocess, you'll need the `clingo` Python API directly — it's installed), `src/argumentation/aba.py`, `src/argumentation/aba_sat.py`, and whatever `.lp` files live alongside `aba_asp.py` (the existing ABA ASP encodings — your new incremental `.lp` derives from Listing 1 and should be consistent with them).

## What to build

A multi-shot `clingo.Control`-based incremental solver for ABA reasoning, per L21-TPLP Algorithm 1:
- One `clingo.Control`, ground `ABA(F) ∪ com` (the complete-assumption-set encoding) once.
- Iterate: `solve(assumptions=...)` for the transient check; on a counterexample, add a `constr(out(I))` refinement clause (a non-monotone-in-shots program part added via `Control.add` + re-ground of just that part, or via external atoms — whatever Listing 1 / the clingo multi-shot idiom uses); repeat.
- Apply this to the ABA tasks the spec identifies as the timeout cluster — at minimum DS-PR (skeptical preferred, the Π₂ᴾ task), and any others Algorithm 1 covers (the spec says complete/stable/admissible are the NP queries reusable across calls; preferred is the 2ᴾ one needing a fresh `Control` per query because refinement clauses are query-specific).
- New `.lp` resource file (e.g. `aba_com_incremental.lp`) transcribed from Listing 1, placed with the other ABA `.lp` files.

### Compose with C2a
`simplify_aba` runs first; the multi-shot loop runs on the residual; results lift back through `AbaSimplification.lift` / `.lift_all`. Default ON, `simplify=False` opt-out preserved. The multi-shot path itself should also be transparent — same results as the current `aba_asp.py` path, just faster on hard instances.

### Hard correctness directive
The multi-shot solver MUST produce results identical to the existing `aba_asp.py` / `aba_sat.py` ABA paths and the brute-force `aba.py` reference — same extensions, same DC/DS answers — on every ABA framework. No approximation. If clingo multi-shot grounding semantics make the refinement-clause mechanism tricky, get it right (test against the oracle) rather than approximating. Oracle disagreement ⇒ your code is wrong.

### If the Python `clingo` module's multi-shot API isn't usable here
The spec assumes the `clingo` Python package is available (it's in the test deps). If for some reason multi-shot can't be done cleanly (e.g. only the CLI is available and it doesn't support the needed incremental mode), STOP and report that — do not fake incrementality with repeated subprocess calls and call it done.

## Tests
Extend `tests/test_aba_preprocessing.py` or add `tests/test_aba_multishot.py`:
- Oracle equivalence: multi-shot ABA solve == existing `aba_asp.py`/`aba_sat.py` path == brute-force `aba.py`, for the tasks Algorithm 1 covers (esp. DS-PR), on a battery + random ABA instances, DC and DS, assumption and sentence queries.
- A test that the multi-shot loop actually iterates (refinement clauses get added) on an instance that needs ≥2 rounds — assert via telemetry/spy, not just timing.
- `simplify=False` regression for any existing ABA telemetry tests affected.
- Full suite. Baseline after C2a: `1 failed, 1620 passed, 2 skipped` (`--ignore=tests/test_datalog_grounding.py --tb=no`, z3+clingo installed). Do not regress beyond the documented pre-existing `test_kernel_ideal_extension_is_admissible`.

## Benchmark
- No ICCMA cap-100 corpus in-repo — generate ABA instances with a preferred-refinement-heavy structure (many spurious complete sets that get pruned) plus a no-help control (instance solved in one round). BEFORE = the current `aba_asp.py` enumerate-then-filter path; AFTER = the multi-shot loop. Record the delta on DS-PR especially.

## Definition of done
1. Multi-shot incremental ABA solver implemented per Algorithm 1, composed under `simplify_aba`, wired as the default ABA-ASP path (opt-out preserved), with the new `.lp` resource.
2. Oracle tests pass; full suite no worse than the post-C2a baseline.
3. Before/after benchmark recorded incl. no-help control.
4. `ruff` + `pyright` clean on touched files — paste pyright output for touched files into the report.
5. `git add` + `git commit` on the feature branch. **Commit hash in the report.**
6. Report → `reports/graph-speedup-wave-c2b-aba-multishot.md`: what you built, the `.lp` derivation, how the refinement-clause mechanism works in clingo multi-shot, which tasks use it, how it composes with C2a, test results, before/after benchmark + control, pyright output, commit hash.

## Hard stops
- Do NOT redo §1 (`simplify_aba`) or §2.3a (the Z3 refactor) — already done.
- Do NOT materialize the Dung AF, route ABA through the AF SCC layer, gate admissible, or touch ABA+ semantics.
- Do NOT touch `preprocessing.py` or `scc_recursive.py` except to read.
- If the spec is wrong/incomplete in a way you can't settle against the oracle, or the clingo Python multi-shot API isn't usable, STOP and report — do not invent or fake.
- If the suite is red beyond the documented baseline on a clean checkout before your changes, STOP and report.
