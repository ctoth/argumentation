# Codex deep review — 2026-07-10

Status: Accepted as the remediation basis on 2026-07-10.

I found five concrete correctness/API defects and one broken repository gate. The most serious problem is that several exported ranking functions do not implement the semantics whose names they expose.

## Findings

### 1. High — Several ranking semantics are heuristic substitutes

In [`ranking.py`](../../src/argumentation/ranking/ranking.py):

- `discussion_based_ranking` (line 141) should lexicographically compare signed counts of linear discussions at each depth. The implementation instead deduplicates paths into sets of nodes, weights depths by `1/(level+1)`, then sums everything into one float.
- `burden_ranking` (line 132) should lexicographically compare the sequence of burden numbers. It ranks only the final requested iteration and labels the result `converged=True`.
- `tuples_ranking` (line 212) returns a decimal-weighted scalar, not the paper's tuple representation and ordering.
- `h_categoriser_ranking` (line 244) caps the attacker sum at `1.0`; the cited equation uses the full sum.

This is directly contradicted by [Amgoud–Ben-Naim page 10](../../papers/Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks/pngs/page-009.png) and [page 11](../../papers/Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks/pngs/page-010.png). Tests for most of these functions merely verify that they return a total preorder, so semantically incorrect algorithms pass.

### 2. High — ADF links are classified syntactically, not semantically

[`classify_link`](../../src/argumentation/frameworks/adf.py) at line 291 delegates to occurrence-polarity analysis at line 457.

Counterexample: `a ∨ (a ∧ ¬a)` is semantically just `a`, so its `a` link is supporting only. The implementation sees both positive and negative occurrences and returns `BOTH`.

The source definition quantifies over parent assignments rather than AST polarity; see [Strass 2013, p.47](../../papers/Strass_2013_ApproximatingOperatorsSemanticsAbstract/pngs/page-008.png). The classifier must evaluate monotonicity of the Boolean acceptance function.

### 3. High — Solver invariant failures are reported as missing dependencies

Broad `except RuntimeError` handlers in [`solver.py`](../../src/argumentation/solving/solver.py), including lines 375 and 421–485, convert every runtime failure through `_sat_runtime_unavailable` at line 613 into `SolverBackendUnavailable` with an "Install z3" hint.

But [`af_sat.py`](../../src/argumentation/solving/af_sat.py) line 1290 raises `RuntimeError` when preferred-extension growth violates an internal strict-superset invariant. That is a solver correctness failure, not missing z3. The public result therefore conceals real bugs and gives users a false remediation.

### 4. Medium — ABA parsers silently overwrite duplicate contraries

Both compact and numeric parsers use last-write-wins dictionary assignment in [`iccma.py`](../../src/argumentation/interop/iccma.py), at lines 223–224 and 273–276.

Thus this malformed framework is accepted:

```text
p aba
a x
c x y
c x z
```

The first contrary disappears silently. ABA defines a contrary function `A → L`, and the model constructor explicitly requires exactly one contrary per assumption. Duplicate declarations should be rejected at their second line.

### 5. Medium — LLM-facing gradual reasoning treats non-converged values as final

[`explain_acceptance`](../../src/argumentation/gradual/llm_surface.py) at line 81 extracts only `.strengths` from `GradualStrengthResult`, discarding `converged`, `iterations`, and residual error. `max_iterations=1` can therefore produce an explanation presented as final even when convergence failed.

`contest` at line 107 similarly emits accepted/rejected booleans from potentially non-converged before/after scores without exposing that fact.

### 6. Repository gate is currently red

Full result: **2 failed, 2,932 passed, 3 skipped, 1 xfailed** in 4m50s.

- [`test_iccma_runner.py`](../../tests/interop/test_iccma_runner.py) line 528 expects a 39-second child budget, but production intentionally reserves five seconds in [`iccma2025_run_native.py`](../../tools/iccma2025_run_native.py) lines 1008 and 1054. This is a stale test.
- [`argumentation-package-boundary.md`](../../docs/argumentation-package-boundary.md) lines 49–63 contains five pre-reorganization source paths, failing the documentation surface gate.

## Additional risk

[`naive_extensions`](../../src/argumentation/core/dung.py) at line 391 checks conflict-freedom against `defeats`, while stage and admissibility paths consult `attacks` when present. I would not call this definitively wrong because the framework documentation also says pure Dung semantics use defeats, but applying naive/CF2 semantics to an ASPIC projection with distinct attacks and defeats is currently ambiguous and inconsistent.

## Verification

Static verification was otherwise clean:

- Pyright reported zero errors.
- Both import contracts held.
- The focused ranking/ADF/interop/LLM/solver suite passed 65 tests.
- Full suite: 2 failed, 2,932 passed, 3 skipped, 1 xfailed in 290.25 seconds.

The focused pass demonstrates why these defects survive: the relevant semantic counterexamples are not encoded.

## Recommended repair order

1. Correct or honestly rename the ranking semantics.
2. Replace structural ADF link classification with semantic monotonicity checks.
3. Introduce exception types that distinguish missing dependencies from solver invariant failures.
4. Reject duplicate ABA contrary declarations.
5. Propagate or enforce gradual-semantics convergence at the LLM-facing boundary.
6. Repair the two repository gate failures.

No source or test files were modified during the review. The pre-existing paper edits and noisy untracked worktree were left untouched.
