# Claim-Augmented Argumentation Frameworks

`argumentation.caf` implements finite claim-augmented argumentation frameworks
as a semantic surface, not a complexity-theorem surface.

## Implemented model

A `ClaimAugmentedAF` consists of:

- a Dung `ArgumentationFramework`;
- a total claim map assigning exactly one claim identifier (coerced to `str`)
  to every argument. The constructor raises `ValueError` if the claim-map
  domain does not equal the argument set.

The module exposes two CAF views, dispatched through a single entry point:

```python
from argumentation.caf import ClaimAugmentedAF, extensions

caf = ClaimAugmentedAF(framework=af, claims={"a1": "x", "a2": "x", "a3": "y"})

extensions(caf, semantics="preferred", view="inherited")
extensions(caf, semantics="preferred", view="claim_level")
```

`view: CAFView` is a `Literal["inherited", "claim_level"]`. Note the
underscore in `"claim_level"` (not hyphen) and the hyphens in the semantics
names (`"semi-stable"`, `"stable-admissible"`).

- **Inherited semantics** — compute ordinary Dung extensions, then project
  each extension to its set of claims.
- **Claim-level semantics** — evaluate the claim-centric variants from the
  CAF papers.

## Implemented semantics

Inherited semantics accept the following eight literals (others raise
`ValueError`):

`grounded`, `complete`, `preferred`, `stable`, `semi-stable`, `stage`,
`naive`, `cf2`.

Claim-level semantics accept:

- `preferred`;
- `naive`;
- `stable`, meaning cl-stable with a conflict-free realization;
- `stable-admissible`, meaning the admissible cl-stable variant;
- `semi-stable`;
- `stage`.

Claim-level semi-stable and stage select claim sets whose claim-range —
`claim ∪ defeated_claims` — is non-dominated. An argument set defeats a
claim only when it attacks every argument carrying that claim.

## Implemented predicates

- `is_well_formed(caf)` — matches the CAF condition that arguments with the
  same claim have the same outgoing attack targets.
- `concurrence_holds(caf, *, semantics)` — the paper's concurrence test
  comparing inherited and claim-level extensions for a given semantics.
- `defeated_claims(caf, extension)`.
- `claim_range(caf, extension)`.
- `is_i_maximal(claim_sets)`.

These helpers exist because the paper statements use them directly in
definitions, lemmas, and propositions.

## Complexity scope

Dvořák, Greßler, Rapberger & Woltran (2023) give a complexity landscape for
CAF reasoning problems such as verification, credulous acceptance, skeptical
acceptance, non-empty existence, and concurrence.

This package does not expose those complexity classes or problem labels as
runtime APIs. It implements the finite semantic computations above. No
theorem or complexity class should be read as an implemented decision
procedure unless a corresponding function and tests exist in
`argumentation.caf`.

## Test standard

CAF behavior is tested from paper-derived statements:

- Dvořák, Rapberger & Woltran (KR 2020) and Dvořák, Greßler, Rapberger &
  Woltran (AIJ 2023) definitions for CAFs, inherited semantics, defeated
  claims, and claim-level semantics.
- KR 2020 propositions for cl-preferred, cl-naive, stable-variant
  concurrence, I-maximality, and unique-claim coincidence.
- Generated Hypothesis tests over finite CAFs for those paper claims.

When extending this module, add a failing paper-derived test or property
before changing production code.
