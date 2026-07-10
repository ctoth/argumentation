# Ranking Semantics Correction Plan

Date: 2026-07-10

Status: Active under the remediation master plan.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Make every exported paper-named ranking function implement the cited semantic
object exactly, or remove/rename it honestly if the current result contract
cannot represent that object. Do not preserve a heuristic implementation under
a paper-semantic name.

This plan supersedes the ranking acceptance claim in the older package-first
workstream for the specific functions disproved by the Codex review.

## Paper Checkpoint

Before writing tests, reread the checked-in page images that define the relevant
objects, including at minimum:

- `papers/Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks/pngs/page-009.png`
- `papers/Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks/pngs/page-010.png`
- the exact Bonzon et al. page images defining tuple valuation and comparison;
- the exact Besnard-Hunter page image defining the categoriser recurrence; and
- the exact page images for any retained iterated-graded implementation.

For each semantic, write a short contract note in its test module identifying
the page image and translating the definition into executable comparisons. Do
not use extracted PDF text as the authority.

## Phase 1: Representation and Caller Decision

The current `RankingResult.scores` shape is numeric, while discussion-based,
burden-based, and tuple semantics require lexicographic structured values.
Before production edits:

1. Inventory all callers of `discussion_based_ranking`, `burden_ranking`,
   `tuples_ranking`, `h_categoriser_ranking`, and the public `RankingResult`
   fields.
2. Write distinguishing tests that cannot pass through a scalar weighted sum.
3. Determine the smallest faithful public contract:
   - if the existing result can expose exact tiers while treating numeric
     scores as inapplicable, specify that behavior explicitly; or
   - if exact values must be public, propose the minimum result change and
     obtain user approval before introducing it; or
   - if compatibility cannot be made honest, rename/remove the heuristic API
     and migrate callers directly, without a wrapper.
4. Record the chosen contract in this plan before implementation begins.

A new generic ranking interface, adapter, or parallel result hierarchy is not
the default solution.

### Recorded decision — 2026-07-10

- `RankingResult.scores` will be broadened in place to hold either a numeric
  value or an exact finite lexicographic tuple. Discussion-based and
  burden-based rankings will expose their comparison tuples directly; they will
  not publish an invented scalar score.
- `burden_numbers` remains the explicit API for callers that want only the
  numeric value at a selected iteration. `burden_ranking` will use the complete
  prefix from step zero through the requested bound and report whether that
  prefix has stabilized.
- Bonzon 2016 page image `page-004.png` states that Tuple* can leave arguments
  incomparable and is defined there for acyclic frameworks. It therefore
  cannot use `RankingResult`, whose `ranking` is a total preorder and whose
  `equivalent` method would conflate incomparability with equality. The Tuple*
  slice will use one specific result that exposes exact tupled values and the
  paper comparison relation; the false scalar `tuples_ranking` contract will be
  removed rather than wrapped.
- Numeric semantics continue to return floats. No generic ranking adapter or
  compatibility hierarchy will be introduced.

## Phase 2: Discussion-Based Semantics

### Red contracts

- Count signed attack/defence paths with multiplicity; a merged frontier node
  reached by two paths contributes twice.
- Compare the signed path-count sequence lexicographically as defined by the
  paper, not through fixed weights.
- Include a framework where the current unique-frontier weighted sum produces
  a different ordering from the paper definition.
- Specify cyclic behavior. If a finite depth is only an approximation, the
  result must say it is truncated/non-converged rather than claim the exact
  semantics.

### Green implementation

Replace the set-frontier/weighted-sum path with the paper object. Delete the
disproved formula; do not retain it as a silent fast path.

## Phase 3: Burden-Based Semantics

### Red contracts

- Retain the full burden sequence required for lexicographic comparison.
- Include two arguments whose final scalar iteration has the same or reversed
  ordering relative to the full sequence.
- Prove the meaning of `converged`; a fixed iteration count cannot set it to
  `True` unconditionally.
- Cover unattacked arguments and the paper's worked examples.

### Green implementation

Compare the actual burden sequences. If a bounded prefix is exposed, mark it as
bounded/truncated and do not describe it as convergence without a proof.

## Phase 4: Tuple Valuation

### Red contracts

- Preserve the attack and defence tuples as tuples/multisets, including path
  multiplicity and the paper's comparison rule.
- Include a counterexample where subtracting weighted scalar sums changes the
  tuple ordering.
- Establish the supported graph class from the paper. Reject unsupported
  cyclic inputs explicitly if the semantics is only defined for acyclic graphs.

### Green implementation

Return/order by the exact tuple object chosen in Phase 1. Remove the scalar
surrogate from the paper-named function.

## Phase 5: H-Categoriser

### Red contracts

- Encode the exact recurrence without capping the summed attacker strength.
- Include at least one argument whose attacker sum exceeds one, distinguishing
  the current capped result.
- Check convergence using both a value tolerance and a deterministic iteration
  bound; report non-convergence honestly.
- Differentially test against the repository's other categoriser implementation
  if both claim the same recurrence.

### Green implementation

Remove `min(1.0, attacker_sum)` unless the reread paper image explicitly defines
that cap. Consolidate duplicate implementations only if they are genuinely the
same owner and direct caller migration can delete one path.

## Phase 6: Export-Wide Ranking Audit

Before closure, audit every exported function in
`src/argumentation/ranking/ranking.py`, including iterated graded defense, for:

- arbitrary weights, caps, or iteration counts not present in the cited paper;
- scalarization of lexicographic/multiset objects;
- lost path multiplicity;
- false `converged=True` claims; and
- graph classes silently outside the definition's domain.

Any newly confirmed mismatch becomes another isolated red/green slice under
this plan. Do not broaden into unrelated ranking feature work.

## Operational Contracts

Exactness must not produce an unbounded accidental search path:

- Record deterministic path/iteration counts in tests for representative small
  frameworks.
- For bounded approximations, assert the bound and the non-converged/truncated
  status.
- For cyclic exact algorithms, add a route or termination invariant before any
  performance tuning.
- If a benchmark misses, profile the real worker/solver path and record the
  dominant cost before selecting an optimization.

## Acceptance Gates

```powershell
uv run pytest -q tests/ranking
uv run pytest -q tests/axioms/test_ranking_axioms.py
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

Adjust only the targeted paths to the repository's exact current test layout;
do not substitute a narrower check for the full gate.

## Done When

- Every retained paper-named ranking matches its page-image definition on
  worked examples and distinguishing counterexamples.
- Structured lexicographic values are not silently scalarized.
- Path multiplicity is preserved where defined.
- Convergence and truncation claims are truthful.
- No disproved heuristic path remains in production or examples.
- Each semantic correction is separately committed before the next begins.
