# Codex Review Remediation Master Plan

Date: 2026-07-10

Status: Authorized for full execution on 2026-07-10.

Source review: [`reviews/2026-07-10/codex.md`](../reviews/2026-07-10/codex.md)

## Aim

Resolve every confirmed defect and repository-gate failure in the Codex review,
and force a paper-backed decision on the remaining `attacks`/`defeats`
semantic ambiguity. This document coordinates the focused plans; it does not
authorize implementation by itself.

## Control Rules

1. Planning is the current phase. Do not edit production code or tests until
   the user explicitly asks to execute these plans.
2. When execution begins, this master plan remains the control surface until
   every focused plan is complete or the user explicitly defers it.
3. Work on one issue family at a time. Before beginning the next family, the
   current slice must be either committed as a kept improvement or fully
   restored with Git.
4. Verify the branch and tracked-file state before every implementation slice.
   Preserve the pre-existing paper-note modifications and unrelated untracked
   files.
5. Each behavioral change starts with an executable failing contract. Commit
   that red contract separately before the implementation commit.
6. Do not add an interface, adapter, sender, wrapper, or compatibility layer
   merely to preserve a disproved implementation. Move callers to the real
   semantic owner and delete the false path.
7. Paper-dependent claims must be reread from the checked-in page images, not
   extracted PDF text. Record exact page-image paths in the corresponding test
   or plan checkpoint.
8. For any solver or performance-sensitive change, add a deterministic
   operational contract before optimization: bounded calls/evaluations, route
   selection, residual-size reduction, or calibrated opt-in wall time.
9. After every substantial targeted test pass and every full-suite pass,
   reread this plan, identify the next unchecked phase, and continue unless the
   user redirects.
10. Do not call the remediation complete while an old production path still
    coexists with its corrected replacement unless a focused plan explicitly
    requires both.

## Focused Plans

| Order | Plan | Review finding | Completion signal |
|---:|---|---|---|
| 0 | [Repository gate repair](2026-07-10-repository-gate-repair.md) | Two current full-suite failures | Clean baseline suite and documentation-path scan |
| 1 | [Ranking semantics correction](2026-07-10-ranking-semantics-correction.md) | Paper-named rankings implement heuristic substitutes | Paper examples, distinguishing counterexamples, and axioms pass |
| 2 | [ADF link classification correction](2026-07-10-adf-link-classification-correction.md) | Link classification follows syntax instead of semantics | Truth-table-equivalent formulas classify identically |
| 3 | [Solver error taxonomy](2026-07-10-solver-error-taxonomy.md) | Broad `RuntimeError` handling hides defects as missing dependencies | Dependency absence remains unavailable; invariants do not |
| 4 | [ABA duplicate contrary declarations](2026-07-10-aba-parser-duplicate-declarations.md) | Duplicate declarations silently overwrite earlier input | Both ABA syntaxes reject duplicates with source location |
| 5 | [Gradual convergence contract](2026-07-10-gradual-convergence-contract.md) | High-level explanations discard non-convergence | Non-converged values cannot be reported as settled strengths |
| 6 | [`attacks`/`defeats` semantic decision](2026-07-10-attacks-defeats-semantics-decision.md) | Naive semantics differs from stage/admissible and CF2 over structured projections | Paper-backed decision table and consistent executable behavior |

## Dependency and Execution Order

### Phase 0: Recover a trustworthy baseline

Execute the repository-gate repair first. The suite currently has two known
failures, so later red tests cannot be interpreted cleanly until those failures
are resolved in their own commits. This phase must not include semantic library
changes.

### Phase 1: Correct false paper-semantic claims

Execute ranking correction, then ADF link classification. These are the two
highest-severity semantic mismatches. Their paper checkpoints and
representation decisions must be complete before implementation begins.

### Phase 2: Restore honest failure reporting

Execute solver error taxonomy, ABA duplicate handling, and gradual convergence
handling. Each is independently releasable and must remain a separate Git
slice.

### Phase 3: Resolve relation ownership

Execute the `attacks`/`defeats` decision plan. This starts as a bounded semantic
adjudication, not a presumed code change. If current behavior is correct, the
phase ends with executable policy contracts and no speculative rewrite. If it
is inconsistent, implement exactly the relation policy established by those
contracts.

### Phase 4: Cross-cutting closure audit

After all focused plans are complete:

1. Search exported APIs, docs, examples, and tests for the disproved ranking
   formulas, structural ADF polarity, broad solver `RuntimeError` conversion,
   silent duplicate contrary overwrite, and ignored convergence flags.
2. Confirm no compatibility shim or second semantic path remains.
3. Confirm every public behavior change has release-note or migration coverage
   if the repository maintains such records.
4. Run the named full gates below.
5. Compare the final tree line-by-line against the source review and mark every
   finding complete, explicitly deferred, or invalidated by evidence.

## Required Gates

Run targeted commands named by each focused plan first, then:

```powershell
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
git status --short
```

If the import-linter entrypoint differs in the current project configuration,
use the repository's existing import-contract command and record its exact
shape rather than substituting a nearby check.

## Commit Ledger

Use a minimum of one red-contract commit and one implementation commit per
behavioral slice. Gate-only documentation fixes may use a single commit when no
behavior changes. Suggested slice boundaries are:

1. Timeout-budget expectation.
2. Documentation boundary paths.
3. Each individual ranking semantics correction.
4. ADF semantic classifier.
5. Solver dependency/invariant distinction.
6. ABA compact duplicate rejection.
7. ABA numeric duplicate rejection.
8. Gradual non-convergence propagation.
9. `attacks`/`defeats` policy contracts and, only if required, implementation.

Do not combine unresolved source slices in the worktree.

## Completion Definition

This workstream is complete only when:

- every focused plan is complete or explicitly deferred by the user;
- every confirmed review finding has a regression contract and a corrected or
  deliberately removed production path;
- the `attacks`/`defeats` risk has a paper-backed, executable verdict;
- the full tests, type checker, import contracts, and diff check pass;
- no stale paper-named heuristic or silent failure conversion remains; and
- Git records each kept slice independently and the final status contains only
  known pre-existing or intentionally created artifacts.

## First Executable Slice

When the user authorizes execution, begin only with
[`2026-07-10-repository-gate-repair.md`](2026-07-10-repository-gate-repair.md).
Do not begin ranking or other semantic work until the baseline is green and
that slice is committed.
