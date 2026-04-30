# Claim-Augmented Argumentation Frameworks

`argumentation.caf` implements finite claim-augmented argumentation frameworks
as a semantic surface, not a complexity-theorem surface.

## Implemented Model

A `ClaimAugmentedAF` consists of:

- a Dung `ArgumentationFramework`;
- a total claim map assigning exactly one claim identifier to every argument.

The module exposes two CAF views:

- inherited semantics: compute ordinary Dung extensions first, then project
  each extension to its set of claims;
- claim-level semantics: evaluate the claim-centric variants from the CAF
  papers.

## Implemented Semantics

Inherited semantics are available for the Dung semantics supported by the
underlying package dispatcher.

Claim-level semantics are implemented for:

- `preferred`;
- `naive`;
- `stable`, meaning cl-stable with a conflict-free realization;
- `stable-admissible`, meaning the admissible cl-stable variant;
- `semi-stable`;
- `stage`.

Claim-level semi-stable and stage semantics use the CAF defeated-claim range:
an argument set defeats a claim only when it attacks every argument carrying
that claim.

## Implemented Predicates

The module also exposes:

- `is_well_formed(caf)`, matching the CAF condition that arguments with the
  same claim have the same outgoing attack targets;
- `defeated_claims(caf, extension)`;
- `claim_range(caf, extension)`;
- `is_i_maximal(claim_sets)`.

These helpers exist because the paper statements use them directly in
definitions, lemmas, and propositions.

## Complexity Scope

The 2023 Artificial Intelligence paper gives a complexity landscape for CAF
reasoning problems such as verification, credulous acceptance, skeptical
acceptance, non-empty existence, and concurrence.

This package currently does not expose those complexity classes or problem
labels as runtime APIs. It implements the finite semantic computations above.
No theorem or complexity class should be read as an implemented decision
procedure unless a corresponding function and tests exist in `argumentation.caf`.

## Test Standard

CAF behavior is tested from paper-derived statements:

- KR 2020 / AIJ definitions for CAFs, inherited semantics, defeated claims, and
  claim-level semantics;
- KR 2020 propositions for cl-preferred, cl-naive, stable-variant concurrence,
  I-maximality, and unique-claim coincidence;
- generated Hypothesis tests over finite CAFs for those paper claims.

When extending this module, add a failing paper-derived test or property before
changing production code.
