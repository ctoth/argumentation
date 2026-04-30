# CAF Semantics Workstream

## Goal

Bring claim-augmented argumentation framework support into explicit conformance
with the claim-centric semantics papers, while preserving the distinction
between inherited semantics and claim-level semantics.

## Primary Papers

- Dvorak, Rapberger, and Woltran (2020), "Argumentation Semantics under a
  Claim-Centric View".
- Dvorak, Gressler, Rapberger, and Woltran (2023), "The Complexity Landscape
  of Claim-Augmented Argumentation Frameworks".

For each implementation slice, reread the relevant page images directly before
changing code. Do not rely on extracted PDF text for definitions, examples, or
notation.

## Current State

- `argumentation.caf` has a `ClaimAugmentedAF` type.
- Inherited semantics project ordinary Dung extensions to claim sets.
- Claim-level preferred, naive, stable, semi-stable, and stage semantics are
  implemented as a first pass.
- `stable-admissible` is exposed for the admissible cl-stable variant.

## Execution Mode

Use TDD for every behavior change:

1. Add a failing test from a reread paper definition, paper example, or stated
   invariant.
2. Implement the smallest production change that makes it pass.
3. Add or extend Hypothesis coverage for the general property behind the
   example.
4. Run the targeted test file before moving to the next slice.

Hypothesis properties must be taken from paper statements, not invented from
local intuition. For each property test, cite the definition, lemma,
proposition, or theorem in the test name or an adjacent comment, assert that it
holds over generated finite CAFs satisfying the paper's preconditions, and only
then implement the production code.

Paper-derived property candidates:

- Definition 4: inherited CAF extensions equal projected Dung extensions for
  every generated finite AF and total claim map.
- Lemma 1: in well-formed CAFs, if two argument sets have the same claim set,
  they have the same defeated-claim set.
- Proposition 1: every cl-preferred claim set is also i-preferred.
- Proposition 2: every cl-preferred output is I-maximal.
- Proposition 3: for well-formed CAFs, cl-preferred and i-preferred coincide.
- Proposition 5: every cl-naive claim set is also i-naive.
- Proposition 6: every cl-naive output is I-maximal.
- Proposition 8: for well-formed CAFs, the stable variants coincide.
- Proposition 10: for well-formed CAFs, cl-semi-stable and i-semi-stable
  outputs are I-maximal.
- Proposition 11: for well-formed CAFs, cl-stage and i-stage outputs are
  I-maximal.
- Lemma 3: with unique claims, inherited, claim-level, and ordinary AF semantics
  coincide for the listed semantics.

## Phases

### Phase 1: Paper Example Fixtures

- Convert every small CAF example used in the KR 2020 definitions into a test
  fixture.
- Cover Examples 1-6 where the paper separates inherited and claim-level
  behavior.
- Keep tests named after the exact semantic distinction they protect, not just
  the example number.

Acceptance criteria:
- Each implemented claim-level semantic has at least one paper-backed positive
  example and one separation example where the paper provides one.
- Tests include expected claim sets, not only cardinalities.

### Phase 2: Well-Formed CAF Surface

- Add `is_well_formed(caf)` using the paper condition: arguments with the same
  claim have the same attack behavior against every other claim-equivalent
  argument.
- Add tests for well-formed and non-well-formed examples from the paper.
- Expose helper errors/messages only if they support debugging test failures.

Acceptance criteria:
- Well-formedness examples from the paper are executable tests.
- The implementation does not infer well-formedness from unique claims alone.

### Phase 3: Relation and I-Maximality Checks

- Add reusable predicates for I-maximality of claim-set outputs.
- Add tests for the paper's relation table: inherited vs claim-level preferred,
  naive, stable, semi-stable, and stage.
- Separate general CAF results from well-formed CAF results.

Acceptance criteria:
- Every relation row exposed in tests cites the corresponding paper section in
  the test name or comment.
- Failing relation checks show the two claim-set collections involved.

### Phase 4: 2023 Complexity Surface

- Decide whether the package should expose only semantics or also reasoning
  problem labels from the 2023 complexity landscape.
- If exposing problem labels, add typed enums for verification, credulous
  acceptance, skeptical acceptance, and existence variants.
- Do not implement complexity claims as runtime behavior unless the code
  actually decides the corresponding problem.

Acceptance criteria:
- Public API documentation states exactly which CAF reasoning problems are
  implemented.
- No theorem or complexity class appears in docs as if it were an algorithm.

## Tests

Targeted command:

```powershell
uv run pytest tests\test_caf.py -q
```

Full verification before completion:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- `ClaimAugmentedAF` semantics match the definitions exposed in the papers.
- Every exposed CAF semantic has paper-backed regression coverage.
- Docs distinguish inherited semantics, cl-semantics, and admissible cl-stable.
- No old projection-only shortcut remains in the claim-level production path.

## Known Traps

- Claim-level semantics are not "project then maximize" for range-based
  semantics; they use claim-level defeated-claim ranges.
- Stable has multiple claim-level variants; do not collapse cl-stable and
  admissible cl-stable.
- Well-formed CAF coincidences must not be assumed for arbitrary CAFs.
