# Wave B3 — Adversarial correctness review of the SCC-recursive implementation

You are an analyst subagent. Read-only on source; you may run tests/benchmarks. You do NOT fix anything — you find problems and report them. Working dir: `C:\Users\Q\code\argumentation`, branch `experiment/graph-speedup-wave-a-preprocessing` (HEAD should be `b882a25`, atop `cebb9a9`).

## What you're reviewing

Wave B2 added `src/argumentation/scc_recursive.py` implementing the SCC-recursive schema for complete/preferred/stable, composed under the Wave A preprocessing layer (`src/argumentation/preprocessing.py`). Context:
- `reports/scc-recursive-algorithm.md` — the spec it was supposed to implement (based on Baroni-Giacomin-Guida AIJ 2005, `papers/Baroni_2005_SCC_recursiveness.pdf`).
- `reports/graph-speedup-wave-b2-scc-impl.md` + `notes/graph-speedup-wave-b2-scc-impl.md` — what the coder says it did.
- `reports/graph-speedup-wave-a-preprocessing.md` — the layer underneath.

## Your job — verify, don't trust

1. **Spec conformance.** Read `scc_recursive.py` against `reports/scc-recursive-algorithm.md`. Does the recursion match BG&G Def 20? Are the `D` / `U` / `UP` (provisionally-defeated / undefined-attacked) sets computed correctly? Is the per-SCC preferred maximality handled where the spec says it must be? Is the condensation processed in a valid topological order? Are the spec's edge cases (empty AF, single SCC → flat solve, self-loops inside an SCC, size-1 SCC) actually handled? Quote file:line for anything suspicious.
2. **Soundness gating.** Confirm semi-stable, stage, ideal, grounded, admissible are NOT routed through the SCC path (the spec says only complete/preferred/stable are SCC-recursive). Confirm the SCC path is applied to the *post-`simplify_af` residual*, and the double-lift (SCC layer then preprocessing layer) is correct. Is `decompose=False` a real opt-out that reproduces the flat result?
3. **Break it.** Construct adversarial AFs and check `scc_extensions(af, sem) == dung.<sem>_extensions(af)` (the brute-force oracle) for complete/preferred/stable. Targets: AFs where an SCC is attacked only by an UNDEC upstream argument; nested condensations (chain of SCCs each feeding the next); an SCC that becomes empty after the `D` restriction; AFs with multiple parallel source SCCs; AFs with even and odd cycles inside one SCC; AFs that are a single big SCC (must equal flat); the empty AF; an AF with one self-attacking argument as a whole SCC; AFs where preprocessing already solves everything (empty residual). Also random AFs at sizes ~6–14 with varied density, a few hundred, all three semantics, comparing scc-path vs flat (`decompose=False`) vs brute-force. If you find ANY disagreement, that's a P0 — report the exact AF, the three results, and your best read of which step is wrong.
4. **Suite + lint reality check.** Run `python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no` (the report notes a 32-bit-Python traceback-renderer MemoryError artifact, hence `--tb=no`). Confirm: only the documented pre-existing failure (`test_kernel_ideal_extension_is_admissible`), nothing else. Run `pyright` on `src/argumentation/scc_recursive.py`, `src/argumentation/solver.py`, `src/argumentation/sat_encoding.py`, `tests/test_scc_recursive.py` — confirm 0 errors (the new-diagnostics noise during the coder's run should be gone in the committed state; if it isn't, that's a finding). Check whether `bench_scc_b2.py` was committed to the repo root — if so, note it (root-level bench script clutter — a cleanup item, not a blocker).
5. **Performance sanity.** Spot-check the benchmark claims: layered AFs should be much faster with the SCC path; a single-giant-SCC AF should be ≈1.0× (no regression). You don't need to reproduce exact numbers — just confirm the direction and that there's no pathological slowdown.

## Deliverable

`reports/graph-speedup-wave-b3-analyst.md`:
- Verdict: **SOUND** (ship it, proceed to Wave C) / **FIXES NEEDED** (list them, severity-ranked, with file:line and repro) / **BROKEN** (oracle disagreement found — P0).
- Spec-conformance findings.
- Any oracle disagreements (exact AFs + results).
- Suite + pyright results as you observed them.
- Minor cleanup items (e.g. `bench_scc_b2.py` in repo root) called out separately from correctness issues.

Be adversarial. The point of this pass is to catch a subtle SCC-decomposition bug *before* it's built upon. "Looks fine" without having actually run the oracle comparison is not acceptable.
