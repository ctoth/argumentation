# Gradual Convergence Contract Plan

Date: 2026-07-10

Status: Active under the remediation master plan.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Prevent high-level acceptance explanations, contestation results, and derived
impact values from presenting a bounded non-converged gradual computation as a
settled strength.

## Contract Decision

The default high-level behavior will be fail-closed: if the underlying gradual
solver reports `converged=False`, no explanation or contestation object may
describe its numeric value as final.

Before adding a public field, exception, or parameter:

1. Inventory the existing gradual result, error, explanation, and contestation
   contracts plus all callers in `src/argumentation/gradual/llm_surface.py`.
2. Reuse an existing non-convergence signal if available.
3. If none exists, choose the minimum honest API change and record it here for
   user approval. Prefer one direct failure/result contract over a wrapper or
   parallel interface.
4. Keep direct lower-level solver access available for callers that explicitly
   want bounded intermediate values; do not relabel those values as converged.

### Recorded API Decision

The inventory found one existing convergence owner,
`GradualStrengthResult`, which already carries `converged`, `iterations`,
`max_delta`, `tolerance`, and the integration method. It found no existing
non-convergence exception or non-converged variant for the final explanation,
contestation, revised-impact, Shapley-impact, or sensitivity results.

The minimum fail-closed API change is one direct
`GradualConvergenceError` beside `GradualStrengthResult`. The error carries the
unchanged lower-level result and names the operation that required convergence.
High-level and derived-value boundaries raise it immediately on the first
non-converged required solve. The low-level strength functions continue to
return `GradualStrengthResult`, including bounded intermediate values, without
raising. No wrapper result, retry path, or compatibility interface is added.

## Red Contracts

1. Configure `explain_acceptance` with an iteration limit that cannot converge
   and assert it does not return a settled explanation.
2. Force each gradual solve used by `contest` into non-convergence and assert
   the high-level result remains visibly non-converged or fails explicitly.
3. Audit Shapley/attack-impact calculations and add a test proving a
   non-converged coalition solve cannot be silently combined into a final
   attribution.
4. Cover the mixed case where one of several internal solves fails to converge.
5. Preserve the existing output for a converged computation.
6. Assert the diagnostic includes iteration count, tolerance, and last residual
   when those are already available from the lower-level result.

Commit these contracts before production edits.

## Green Implementation

1. Check the lower-level convergence result at every high-level boundary before
   building explanatory prose or final impact values.
2. Propagate the chosen existing signal directly. Do not manufacture a numeric
   fallback, silently increase the iteration cap, or rerun through a second
   semantic path.
3. Thread existing convergence controls through high-level calls only where
   callers need to reproduce or test the behavior. Avoid adding knobs that do
   not change a supported decision.
4. Ensure multi-solve algorithms stop or mark the whole result non-converged as
   soon as one required solve is non-converged.
5. Delete any branch that discards `converged` after consuming the score.

## Operational Contracts

Add deterministic checks for:

- maximum solver calls per explanation/contestation request;
- early termination after the first required non-converged solve;
- propagation of iteration count/residual; and
- no hidden retry with a larger iteration budget.

If later work aims to improve convergence performance, that is a separate
experiment requiring a calibrated contract and profiling of the real solver
path. It is not part of this correctness slice.

## Acceptance Gates

```powershell
uv run pytest -q tests/gradual
uv run pytest -q tests -k "gradual and (converg or explain or contest or shapley)"
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

Use the exact current test paths during execution.

## Done When

- No high-level surface reports a non-converged value as settled.
- Single- and multi-solve paths obey the same fail-closed contract.
- Converged outputs remain compatible.
- The convergence signal is not discarded anywhere in the audited call graph.
- The operational route contracts and full gates pass in an isolated commit.
