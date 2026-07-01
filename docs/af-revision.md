# AF Revision

`argumentation.af_revision` is the formal abstract-argumentation change
surface for WS-B. It is distinct from `propstore.support_revision.af_adapter`,
which only projects a support-incision state into argumentation-facing inputs.

## Implemented Surfaces

`baumann_2015_kernel_union_expand(base, new)` implements the Baumann-style
kernel-union expansion shape over Dung frameworks: arguments, defeats, and
attacks are unioned into the expanded framework.

`ExtensionRevisionState` represents Diller-style extension revision with a
faithful ranking over all extension candidates for a finite argument universe.
`diller_2015_revise_by_formula(state, formula)` selects the minimal ranked
extensions satisfying a formula. `diller_2015_revise_by_framework(state,
framework, semantics="stable")` revises toward the stable extensions of a
target framework, preserving overlap when possible and otherwise selecting
minimal faithful candidates.

`cayrol_2014_classify_grounded_argument_addition(framework, argument, attacks)`
classifies the effect of adding an argument under grounded semantics using the
WS-B taxonomy values in `AFChangeKind`: decisive, restrictive, questioning,
destructive, expansive, conservative, and altering.

## Gates

`tests/test_af_revision_postulates.py` property-tests the implemented Baumann,
Diller, and Cayrol-facing behavior over finite frameworks and extension
candidates. The Diller-facing checks exercise faithful ranking behavior; the
Baumann-facing checks exercise expansion by kernel union; the Cayrol-facing
checks exercise grounded-extension change classification.

## Boundaries

Do not cite `propstore.support_revision.af_adapter` as AF revision. It is a
projection adapter for current accepted support atoms. Formal AF revision lives
in `argumentation.af_revision`.

## Not Implemented

These AF-revision and AF-merge constructions are not implemented in propstore's
belief-set layer. They are owned by the upstream `argumentation` package and
tracked through WS-O-arg, with propstore consuming only public API surfaces:

- Baumann-Brewka 2015 full R1-R8 revision postulates. The current public
  surface covers kernel-union expansion and Diller-style extension revision;
  it is not a complete Baumann-Brewka revision implementation.
- Baumann 2019 AGM-style contraction for abstract argumentation frameworks,
  including the documented failure modes for recovery and Harper-style
  contraction.
- Coste-Marquis 2007 merging of Dung argumentation frameworks.
- Complete Diller 2015 P*1-P*6 and A*1-A*6 coverage beyond the currently
  implemented public revision/expansion adapters.
- A propstore-owned AF revision kernel. D-12 keeps the kernel in
  `argumentation`; propstore may add a thin public-API consumer adapter but must
  not recreate an embedded AF revision kernel.
