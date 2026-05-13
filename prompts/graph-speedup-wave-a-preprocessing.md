# Wave A — AF preprocessing layer: grounded reduct + cheap structural reductions

You are a coding subagent. Execute this task end to end, commit your work, and write a report.
Working dir: `C:\Users\Q\code\argumentation`.

## Required reading first (do not skip, do not paraphrase back to me — just absorb)

1. `notes/graph-theory-recon-codebase-2026-05-12.md` — codebase recon of the current solving paths. This is your ground truth for what exists and where. Trust file:line references in it.
2. `reports/graph-theory-speedups-2026-05-12.md` — literature framing. Items **#1 (grounded-reduct preprocessing)** and **#2 (cheap structural reductions)** are what you implement. Ignore items #3–#6.
3. The actual source files the recon names: `src/argumentation/af_sat.py`, `src/argumentation/dung.py`, `src/argumentation/af_revision.py`, `src/argumentation/sat_encoding.py`, `src/argumentation/solver_adapters/clingo.py` (and whatever the ASP/ICCMA path entry point is — `iccma.py` / `solver.py`). Read them before writing anything.

## What to build

A **preprocessing layer** for Dung abstract argumentation frameworks that shrinks an AF before it is handed to the SAT (Z3) or ASP encoder, then lifts the answer back. Concretely:

### 1. Grounded reduct
Compute the grounded extension (the recon says `dung.grounded_extension` already exists and is O(V+E)). The arguments in it are forced **IN**; everything they attack is forced **OUT**. Remove all forced arguments from the AF and re-solve only the residual. This is the standard µ-toksia / pyglaf / ASPARTIX-V preprocessing — see `reports/graph-theory-speedups-2026-05-12.md` item #1.

### 2. Cheap structural reductions (apply after / alongside the grounded reduct)
- **Self-attacker removal**: any `a` with `(a,a)` in the attack relation cannot be in any conflict-free set → forced OUT.
- **Isolated-argument elimination**: any `a` with no incoming and no outgoing attacks is in every extension of the semantics we support → forced IN, removed from the encoded instance.
- **Acyclic shortcut**: if the residual AF's attack graph is acyclic, the unique complete = preferred = stable = grounded extension is just the grounded labelling — return it directly, no SAT/ASP call. (The recon notes `_is_acyclic` already exists in `af_sat.py`.)
- **Symmetric-AF shortcut**: if the attack relation is symmetric and irreflexive, the AF is coherent and several tasks become polynomial (Coste-Marquis et al. ECSQARU 2005, cited in the report item #2). Implement at minimum the cheap consequences you can do safely; if a full symmetric special-case is more than ~30 LOC, do the detection + a TODO and say so in your report rather than getting it subtly wrong.
- **Kernel pruning** (optional, do it only if low-risk): the recon says `af_revision.py` has `stable_kernel` / `baumann_2015_kernel` that shrink the attack relation while preserving the relevant extensions. If — and only if — there's an existing kernel whose preservation guarantee exactly matches the semantics being solved, apply it to thin the attack relation before encoding. If you're not certain the guarantee matches, **do not apply it** — leave a TODO and explain in the report. Soundness beats speed here.

### Hard correctness directive
The preprocessing MUST be semantics-preserving: for every supported semantics, `solve(simplify(af))` lifted back to the full argument set must equal `solve(af)` exactly — same set of extensions, same accept/reject answers. There is no acceptable "approximate" mode. If a reduction is only valid for some semantics, gate it by semantics.

### Wiring directive
The layer must actually take effect on the default solve paths — both the Z3 AF SAT path (`af_sat.py` / the `AfSatKernel`) and the ASP/clingo AF path. A preprocessing module that exists but isn't called is worthless. Find the choke point where an AF + a task goes into an encoder and insert the simplify there, with the lift-back on the way out. It must be transparent: callers see identical results, just faster. If there's a natural place for an opt-out flag (e.g. `simplify=True` default), add one, but default ON.

Module placement: your call — put it where it fits the codebase (a new `src/argumentation/preprocessing.py`, or extend an existing module). State where and why in your report.

## Tests

- Add unit tests that, for a battery of small AFs (acyclic, symmetric, with self-attackers, with isolated args, with non-trivial grounded extension, and a few random ones), assert that the brute-force / existing oracle results equal the results through the preprocessed path, for grounded, complete, preferred, stable, semi-stable, stage, ideal. The recon mentions brute-force enumeration exists — use it as the oracle.
- Run the full existing test suite. It must stay green. Tests live under `tests/`.

## Benchmark (before/after)

- Find the benchmark harness: the recon names `bench/asp_vs_sat.py`, `bench/instance_gen.py`, and an ICCMA cap-100 corpus / runner. Read `bench/README.md`.
- BEFORE making changes: run the relevant benchmark (at minimum the ICCMA cap-100 AF tasks, or if that's too slow, a representative subset including the DS-PR rows the recon says time out) and record wall-clock + timeout counts.
- AFTER: run the same thing. Record the delta.
- If you genuinely cannot run the ICCMA corpus in reasonable time, run `bench/asp_vs_sat.py` on generated instances and say explicitly in your report that you did not run the ICCMA corpus and why.

## Definition of done

1. Preprocessing layer implemented and wired into the Z3 AF path AND the ASP AF path.
2. New oracle-equivalence tests pass; full existing suite green.
3. Before/after benchmark numbers recorded.
4. Precommit / lint checks pass (check `pyproject.toml` / repo conventions for the command — likely `ruff` + `pyright`; the modernize notes may mention it).
5. `git add` the files you changed, `git commit` with a descriptive message. **Include the commit hash in your report.**
6. Write your report to `reports/graph-speedup-wave-a-preprocessing.md` containing: what you built, where it's wired, which reductions you implemented vs deferred (and why), test results, before/after benchmark numbers, the commit hash, and anything the next wave (SCC-recursive core semantics) needs to know about the new layer's API.

## Constraints / hard stops

- Do NOT touch the ABA or ASPIC code paths — separate waves.
- Do NOT implement SCC-recursive evaluation or treewidth DP — separate waves.
- If a reduction's soundness is uncertain, omit it and document — never ship an unsound shortcut.
- If the test suite is red on a clean checkout *before* your changes, stop and report that — don't build on a broken baseline.
