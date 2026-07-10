# ADF Link Classification Correction Plan

Date: 2026-07-10

Status: Active under the remediation master plan.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Replace syntax-occurrence link classification with the behavioral definition
of supporting and attacking ADF links. Logically equivalent acceptance
conditions must classify a parent identically.

## Paper Checkpoint

Reread directly:

- `papers/Strass_2013_ApproximatingOperatorsSemanticsAbstract/pngs/page-008.png`

Translate the page-image definition into a truth-table contract before editing
`src/argumentation/frameworks/adf.py`. Record the exact quantification used by
the implementation in the test comments.

## Semantic Contract

For parent `p` and every interpretation `R` of the other parents:

- supporting: making `p` true never changes an accepted condition to rejected;
- attacking: making `p` true never changes a rejected condition to accepted;
- both: both monotonicity conditions hold;
- neither: neither monotonicity condition holds.

The plan must also settle the behavior for a symbol that is not a semantic
parent. Reuse the existing `LinkType` vocabulary according to its documented
meaning; do not invent a fifth category without explicit need.

## Red Contracts

1. The review counterexample `a OR (a AND NOT a)` is classified exactly like
   `a`, not as both supporting and attacking merely because `a` occurs under a
   negation node.
2. Pairs of logically equivalent formulas with different syntax receive the
   same link classification.
3. Include canonical supporting-only, attacking-only, both/independent, and
   neither/non-monotone formulas.
4. Exhaustively enumerate small Boolean acceptance conditions and compare
   `classify_link` with a test-local truth-table oracle.
5. Cover multiple other parents so classification quantifies over all their
   assignments rather than one favored interpretation.

Commit these failing contracts before production edits.

## Green Implementation

1. Make `classify_link` evaluate the acceptance condition behavior under paired
   interpretations that differ only in the target parent.
2. Use the framework's existing condition evaluator and parent inventory. Do
   not introduce a parallel formula interpreter.
3. Delete `_structural_polarity` if it has no remaining valid owner or caller.
   Do not leave it as a fallback or fast path.
4. Preserve syntax inspection only where it answers a syntax question; it must
   not determine semantic link type.
5. Ensure condition evaluation failures remain distinguishable from a valid
   `NEITHER`/`UNDEFINED` result.

## Operational Contract

Behavioral classification is exponential in the number of other parents under
direct enumeration. Before optimization:

- add a deterministic evaluation-count assertion for small parent sets;
- confirm a parent assignment pair is evaluated at most once per classification;
- document the supported size expectation; and
- if a faster route is introduced later, require differential equivalence to
  the exhaustive oracle before benchmarking.

No timing-only benchmark may replace the semantic oracle.

## Acceptance Gates

```powershell
uv run pytest -q tests/frameworks/test_adf.py
uv run pytest -q tests -k "adf and link"
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

Use the exact current test paths discovered during execution if names differ.

## Done When

- Classification is invariant under Boolean equivalence.
- The review counterexample passes.
- All four behavioral classes have direct tests.
- The structural occurrence classifier is deleted from the semantic path.
- Evaluation work has a deterministic bound contract.
- The focused and full gates pass in a clean, separately committed slice.
