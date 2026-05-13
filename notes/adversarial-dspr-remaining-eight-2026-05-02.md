# Adversarial review — workstream-dspr-remaining-eight — 2026-05-02

## What I read
- `reports/workstream-dspr-remaining-eight.md` (full).
- `src/argumentation/af_sat.py` lines 85-220, 370-499, 718-815, 1180-1196.
- `notes/ds-pr-timeouts-2026-05-02.md`.
- `reports/workstream-dspr-strong-learning.md` (precursor).
- `tests/test_iccma_run_timeout_rows.py` opening.

## Verified facts about current code
- `PreferredSkepticalTaskSolver.decide` (af_sat.py:429) loop: find_attacker → `_admissible_extension(required_in=attacker | {query}, utility="preferred_skeptical_extend_attacker")` → `attacker_problem.learn_witness_region(extended)`.
- `learn_witness_region` (af_sat.py:790) emits `Or(attacker_vars[a] for a in framework.arguments - extension)` — a "must hit outside" clause. Soundness depends on extension being a CDAS-valid witness for any attacker A' ⊆ extension.
- `_grow_preferred` (af_sat.py:849) calls `_complete_extension` repeatedly, each iteration is a SAT call growing the set; result is a maximal complete = preferred extension. Per-loop SAT-call cost scales with growth depth.
- `_PreferredSkepticalAttackerSolver` (af_sat.py:718) encodes BOTH attacker and candidate as admissible, requires query in candidate, requires some defeat from attacker to candidate. Find_attacker therefore returns admissible A that attacks some admissible C ⊇ {q}. Same `learn_witness_region` shape.
- `_optional_argument(framework, query)` returns `frozenset({query})`, so `required_query` is non-empty and `attacker | required_query` always includes query.
- `_shortcut` (af_sat.py:480) currently fires self-attacking, unattacked, acyclic-grounded, and (via super_core in `decide`) preferred-super-core. Order: trivial checks first, then super-core after.

## Soundness analysis of the workstream's proposals
- **Phase 1 grounded-in shortcut**: G ⊆ every preferred ⇒ q ∈ G ⇒ q ∈ every preferred ⇒ DS-PR true. Sound.
- **Phase 1 grounded-attacked shortcut**: ∃g ∈ G with (g,q) defeat ⇒ g in every preferred ⇒ q conflict-free with no preferred ⇒ DS-PR false. Sound.
- **Phase 2 complete witness ⇒ admissible witness**: every admissible has a complete super-set, so ∃ complete E ⊇ A ∪ {q} ⇔ ∃ admissible E ⊇ A ∪ {q}. Replacing admissible-extend with complete-extend preserves the decision semantics.
- **Phase 2 maximal preferred witness blocking clause**: larger E ⇒ smaller "outside" ⇒ stronger blocking clause. Soundness preserved because preferred ⊆ admissible ⇒ A' ⊆ E with E preferred is still witnessed by E in the admissible-extend semantics.

## Adversarial concerns
1. **"Grounded reduct shortcut" is a misnomer**: phase title promises a reduct (recurse on AF \ G \ G-attacked); proposal only checks G itself. Either rename or actually implement reduct-and-recurse.
2. **Per-loop cost increases**: `_grow_preferred` is O(growth-depth) SAT calls; Phase 2 also instantiates a second complete-labelling kernel (doubles var count vs the admissible kernel). 3x loop reduction may not produce 3x wall-clock reduction. Plan only measures loop count, not wall-clock.
3. **Stop-condition threshold (3x) is unjustified**: should be derived from per-loop cost ratio of new vs old learning, or stated as an explicit hypothesis to falsify.
4. **Witness non-uniqueness**: `_grow_preferred` returns one preferred. Different attackers can get different preferred witnesses; blocking clauses may not compose well. No test asserts that two consecutive attackers landing in the same preferred share the witness.
5. **Phase 1 missed sharper alternative**: q has any unattacked attacker (already in G) is already caught; but the slightly stronger "q is attacked by an argument in every preferred" is missed by grounded-only check. A grounded REDUCT iterating until fixpoint catches strictly more.
6. **Differential test gap**: Phase 1 says "differential-test against native preferred enumeration on small generated AFs" but does not prescribe coverage of: (a) cyclic AFs with non-trivial G, (b) AFs where G neither contains nor attacks q, (c) interaction with super_core ordering, (d) acyclic vs cyclic priority.
7. **No wall-clock or per-row resource budget for Phase 2**: solving "at least one of eight" is not a strong enough win condition to justify a complete-labelling kernel; could be lucky.
8. **Phase 0 selector tests under-specified**: "manifest for the eight rows OR deterministic selector over latest full-run outputs" — these are not equivalent. A drifting selector yields drift; a manifest pins behavior. Plan should pick one.
9. **No guard against changing super-core or seed semantics**: Phase 2 only changes extend; need explicit assertion that admissible seed (line 449) is unchanged (otherwise short-circuit return False on `seed is None` may regress).
10. **"Same cap shows a kept 3x reduction in attacker-loop count with no selected-row regression"**: a 3x loop reduction with 5x per-loop cost is a regression; the metric is wrong.

## Verdict (draft)
Plan is roughly sound but the success metric is the wrong dimension and the title "grounded reduct" overpromises. Sharpen with: (a) measure wall-clock alongside loops, (b) implement actual reduct or rename, (c) pin Phase 0 to a checked-in manifest, (d) prove blocking-clause soundness in a unit test, (e) add a per-loop cost ceiling so a complete-labelling kernel does not silently double SAT cost.

## Blocker
None — ready to write the four-section reply.
