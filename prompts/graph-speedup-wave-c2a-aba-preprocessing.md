# Wave C2a — ABA well-founded preprocessing + Z3 preferred-growth incremental fix

You are a coding subagent. Working dir: `C:\Users\Q\code\argumentation`, branch `experiment/graph-speedup-wave-a-preprocessing` (the feature branch; HEAD `b882a25`). `git checkout` it if needed; commit there; do NOT branch.

## Spec — your specification, read first

`reports/aba-incremental-spec.md` — implement **§1 (well-founded ABA preprocessing)** and **§2.3a (the Z3 preferred-growth incremental fix)** ONLY. Do NOT do §2.3b (clingo multi-shot) — that's a separate wave. Where the spec flags an item UNRESOLVED (items A–F at the end), treat the differential oracle as the arbiter and document your choice in your report.

Also read: `reports/graph-speedup-wave-a-preprocessing.md` + `notes/graph-speedup-wave-a-preprocessing.md` (the AF precedent — mirror its API shape exactly), and the source files the spec cites: `src/argumentation/aba.py`, `src/argumentation/aba_sat.py`, `src/argumentation/aba_asp.py`, `src/argumentation/solver_differential.py`, `src/argumentation/preprocessing.py` (the AF version, for the shape).

## What to build

### Part 1 — `simplify_aba`
A preprocessing layer for ABA frameworks mirroring the AF `simplify_af`:
- `simplify_aba(framework, *, semantics=None) -> AbaSimplification` with `.residual`, `.fixed_in`, `.fixed_out`, `.lift(...)`, `.lift_all(...)`, `.is_trivial`.
- `FIXED_IN` = the grounded/well-founded assumption set; `FIXED_OUT` = assumptions whose contrary is derivable from `FIXED_IN`'s closure. Per the spec §1. **Compute the grounded assumption set with a support-mask fixpoint** (the spec warns `aba.def_operator`/`grounded_extension` as written is exponential via `_all_subsets`; reuse the `_SupportState`/`_supports`/mask machinery in `aba_sat.py`). 
- Residual: the **conservative form** the spec recommends for v1 ("pin the search space, don't rewrite rules") — i.e. fix the assumptions, don't restructure the rule set. Lift: re-union `fixed_in`.
- **Soundness gate**: `GROUNDED_REDUCT_ABA_SEMANTICS = {grounded, complete, preferred, stable, ideal}`. Do NOT apply to admissible (∅ is admissible) or to ABA+ frameworks (reverse attacks break the `fixed_out` formula — detect ABA+ and skip). Gate by semantics exactly like Wave A gated stage/admissible.
- Module placement: your call — new `src/argumentation/aba_preprocessing.py`, or extend `aba.py` / `preprocessing.py`. State where & why.

### Part 2 — §2.3a Z3 preferred-growth fix
Per the spec: `_sat_preferred_cegar_extension` (`aba_sat.py:481`) currently rebuilds the entire ranked-closure encoding on every "grow to a strict superset" step. Refactor so the encoding is built once per query and only the superset-forcing constraint changes between grow-steps (Z3 `push`/`pop`, or additive constraints — whatever matches the existing `AssumptionKernel` design). `_sat_admissible_cegar_extension` (`aba_sat.py:508`) already reuses its solver — don't break that; just bring the preferred path up to the same standard. This is a contained refactor — do not change what the algorithm computes, only how many times it rebuilds.

### Wiring
- `simplify_aba` wired into the default ABA solve paths (Z3 path in `aba_sat.py`, and the `auto`-backend routing — wherever an ABA framework + task enters a solver). Default ON, `simplify=False` opt-out, transparent (callers get identical results).
- The §2.3a fix is just in `aba_sat.py`, no API change.

### Hard correctness directive
For every gated semantics, `solve(simplify_aba(F))` lifted back must equal `solve(F)` exactly — same extensions / same accept-reject answers — on every ABA framework, including ABA+ ones (where the preprocessing must be a no-op). The §2.3a refactor must produce byte-identical results to before. No approximation. Oracle disagreement ⇒ your code is wrong; fix it.

## Tests
New `tests/test_aba_preprocessing.py` (mirror Wave A's discipline):
- `simplify_aba` structural invariants on a battery of ABA frameworks (trivial, with non-trivial well-founded set, ABA+ → no-op, with derivable contraries, flat) + random ABA instances.
- Oracle equivalence: `solve via simplify_aba == brute-force `aba.py` reference == unsimplified solver` for grounded/complete/preferred/stable/ideal, on the battery + random instances, for both assumption-acceptance and sentence-acceptance queries (DC and DS).
- A `simplify=False` regression for any existing ABA telemetry tests that would change.
- A test that the §2.3a-refactored `_sat_preferred_cegar_extension` matches the pre-refactor behavior (the existing ABA-preferred tests cover this; ensure they still pass and add one targeted growth-step test if coverage is thin).
- Full suite. Baseline (per Wave B2 report): `1 failed, 1491 passed, 2 skipped` with `--ignore=tests/test_datalog_grounding.py --tb=no`. Do not regress beyond the documented pre-existing `test_kernel_ideal_extension_is_admissible`. Requires `z3-solver` + `clingo` (`pip install z3-solver clingo`; `pip install -e .`).

## Benchmark
- ICCMA cap-100 corpus is not in the repo — use `bench/asp_vs_sat.py` / `bench/instance_gen.py` and/or generate ABA instances with non-trivial well-founded sets and a "preferred-growth-heavy" structure. BEFORE (`simplify=False`, pre-refactor or with the §2.3a path disabled if you can) vs AFTER. Record the deltas for: ABA solve with preprocessing, and ABA-preferred with the §2.3a fix. Note a no-help control (trivial well-founded set ⇒ ≈1.0×).

## Definition of done
1. `simplify_aba` implemented + wired (default ON, opt-out); §2.3a refactor applied.
2. New oracle tests pass; full suite no worse than the documented baseline.
3. Before/after benchmark recorded incl. no-help control.
4. `ruff` + `pyright` clean on every file you touched — paste pyright output for touched files into your report. (Pre-existing findings elsewhere: leave them.)
5. `git add` + `git commit` on the feature branch. **Commit hash in the report.**
6. Report → `reports/graph-speedup-wave-c2a-aba-preprocessing.md`: what you built, where wired, which UNRESOLVED items (A–F) you settled and how, test results, before/after benchmark + control, pyright output, commit hash, and what Wave C2b (clingo multi-shot) needs to know.

## Hard stops
- Do NOT implement §2.3b (clingo multi-shot) — separate wave.
- Do NOT materialize the Dung AF, route ABA through the AF SCC layer, gate admissible, or touch ABA+ semantics.
- Do NOT touch the AF preprocessing or SCC code (`preprocessing.py`, `scc_recursive.py`) except to read them.
- If the spec is wrong/incomplete in a way you can't settle against the oracle, STOP and report — do not invent.
- If the suite is red beyond the documented baseline on a clean checkout before your changes, STOP and report.
