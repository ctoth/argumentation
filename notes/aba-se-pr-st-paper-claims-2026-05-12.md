---
title: "ABA SE-PR/SE-ST implementation claims"
date: "2026-05-12"
source_pages_checked:
  - "papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-000.png"
  - "papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-007.png"
  - "papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-013.png"
  - "papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-014.png"
  - "papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-020.png"
  - "papers/Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/pngs/page-021.png"
  - "papers/Toni_2014_TutorialAssumption-basedArgumentation/pngs/page-000.png"
  - "papers/Toni_2014_TutorialAssumption-basedArgumentation/pngs/page-007.png"
  - "papers/Toni_2014_TutorialAssumption-basedArgumentation/pngs/page-009.png"
  - "papers/Toni_2014_TutorialAssumption-basedArgumentation/pngs/page-010.png"
  - "papers/Toni_2014_TutorialAssumption-basedArgumentation/pngs/page-011.png"
---

# ABA SE-PR/SE-ST implementation claims

This is the paper-pass gate for the ABA cap-200 timeout workstream. I inspected the page images listed above directly. I did not reread every page image of either paper in this pass; I used the existing paper-reader notes to navigate to the implementation-relevant pages, then checked the formal claims against the page images.

## Claims to implement

1. Flat ABA lets the hot path work at the assumption-set level.
   - Toni 2014 defines flat ABA as the case where no assumption is the head of any rule. The repository enforces this at `ABAFramework` construction.
   - Bondarenko 1997 states that flat frameworks are the simpler case where all assumption sets are closed. Therefore the solver does not need to add a separate closedness search for ICCMA flat ABA inputs.

2. Attack is contrary derivability from assumptions.
   - Bondarenko 1997 defines a set of assumptions `Delta` as attacking an assumption `alpha` when `T union Delta` derives the contrary of `alpha`.
   - Toni 2014 gives the same operational shape: attacks are directed at assumptions in supports, and a set attacks another set if some supported argument derives a contrary of an assumption in the target set.
   - Implementation consequence: precompute or incrementally constrain which contraries are derivable from the selected assumptions, then express attacks in terms of contrary-derived bits.

3. Stable single-extension is a direct coverage problem.
   - Bondarenko 1997 Definition 3.4: stable iff the set is closed, does not attack itself, and attacks every assumption outside it.
   - Toni 2014 assumption-level view gives the same condition: stable iff it does not attack itself and attacks all assumptions it does not contain.
   - Implementation consequence: `SE-ST` should not enumerate all stable extensions. It needs one selected-assumption model with no selected contrary derivable and all non-selected assumptions covered by derived contraries.

4. Preferred single-extension is maximal admissibility.
   - Bondarenko 1997 Definition 4.4: preferred iff maximal, under set inclusion, among admissible sets.
   - Toni 2014 assumption-level view repeats preferred as maximal admissible.
   - Implementation consequence: `SE-PR` can be implemented as admissible seed plus incremental strict-superset growth until no larger admissible model exists.

5. Stable witnesses are also preferred witnesses, but preferred is broader.
   - Bondarenko 1997 Theorem 4.6 states every stable set is preferred, while not every preferred set is stable.
   - Implementation consequence: a found stable witness is valid for preferred, but failure to find stable is not failure of preferred.

## Test fixtures

Use the baseline timeout groups:

- Quick `SE-PR`: `ABAs/aba_100_0.3_10_5_5.aba`
- Medium `SE-PR`: `ABAs/aba_500_0.1_10_5_2.aba`
- Large shared `SE-PR`/`SE-ST`: `ABAs/aba_2000_0.1_10_5_0.aba`

The promotion gate remains real-row improvement under the 15-second timeout fixture, not just cleaner internals.
