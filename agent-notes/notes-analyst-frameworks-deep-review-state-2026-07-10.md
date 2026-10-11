# Analyst checkpoint — frameworks deep review (2026-07-10)

Role: read-only analyst subagent (gauntlet). Scope: adf.py, adf_io.py, setaf(.py/_io), vaf(.py/_completion), caf.py, partial_af.py, af_merging.py, practical_reasoning.py, core/bipolar.py. This file is worker-state only (hook checkpoint), not the report; findings go back as final message text.

## CONFIRMED (executed counterexamples, uv run python)

1. **classify_link is syntactic, not semantic** — adf.py:291-307 delegates to `_structural_polarity` (adf.py:457). Executed:
   - `or(not(a), and(a,b))` (== not-a or b, semantically ATTACKING) -> code says BOTH.
   - `or(a, not(a))` (tautology, semantically REDUNDANT=both) -> BOTH.
   - XOR (semantically DEPENDENT=neither) -> BOTH (same label as opposite category).
   - declared link, parent absent from formula (semantically REDUNDANT/both) -> NEITHER.
   gamma() itself IS semantic (tautology evaluates T from U), so classify_link disagrees with the operator. Test test_structural_link_classifier_uses_ast_shape (tests/frameworks/test_adf_acceptance_condition_ast.py:53) only covers pure-polarity formulas.

2. **bipolar self set-defeat excluded** — core/bipolar.py cayrol_derived_defeats filters `source != target` (lines 126, 134, 137). Cayrol 2005 Def.3/6 (papers notes p.383-384) does not exclude A1=An. Executed: a S b, b D a -> conflict_free({a}) True (should be False), safe({a}) True. With extra a D b: stable_extensions returns {a} wrongly.
   Tests ENSHRINE the bug: tests/core/test_bipolar_semantics.py:266 test_derived_defeats_no_self_defeats.

3. **bipolar fixpoint over-generates mixed chains** — cayrol_derived_defeats iterates supported/indirect derivation to a fixpoint over derived defeats. a S b, b D c, c S d yields (a,d), but a S b D c S d fits neither Def.3 pattern (defeat must be first or last edge, not middle). Executed: derived = {(a,c),(a,d),(b,d)}; conflict_free({a,d}) False (paper: True).
   Enshrined in tests/core/test_bipolar_argumentation.py:61 test_cayrol_derived_defeats_chain_transitively (asserts ("A","D") in derived).

4. **merging edit distance wrong per Coste-Marquis Def.18** — partial_af.py merge_framework_edit_distance is plain Hamming over 3 states; Def.18 (papers notes lines 106-110) counts only attack-vs-non-attack clashes; ignorance costs 0. Executed: d(empty AF over {a,b}, expand(AF({a}))) = 3, paper 0. Sum winners unaffected (constant per source); Max/Leximax winners WRONG: profile {AF({a},{}), AF({a,b}, all 4 attacks)} -> code max winners = 7 non-empty subsets of {(a,b),(b,a),(b,b)}; paper winners = all-4 plus the four 3-subsets. af_merging.py claims the paper in its docstring.

5. **parse_adf duplicate c lines silently overwrite** — interop/iccma.py:154. "c a true\nc a false" -> False_ (last wins), no error.

6. **keyword statement names corrupt ADF round-trip** — statement named "true": write_adf emits `c x true` for condition Atom("true"); parse_adf reads True_(). Executed: round-trip != original, silent semantic change ("and"/"or"/"not" names fail loudly instead).

## Cleared as NOT bugs (checked)
- gamma/grounded/complete/preferred/model/stable ADF semantics match Brewka 2013 (consensus over two-valued completions of parents; reduct-based stable check correct; verified test for self-supporting a excluded from stable).
- _two_valued_completions bit mapping correct; `or [fixed]` branch dead but harmless.
- VAF successful_attacks matches Bench-Capon Def 5.3 (defeat iff target value not strictly preferred); objective/subjective Def 6.1/6.2 ok (total-order audiences documented).
- vaf_completion Theorem 6.6 / Corollary 6.7 logic matches paper notes.
- SETAF semantics (defends/CF/admissible/grounded/complete/preferred/stable/semi-stable/stage) standard and correct; setaf_io parsers validate (empty tails, unknown ids, dup targets rejected).
- caf.py claim-level semantics match KR2020 definitions as far as notes allow.
- partial_af enumerate_completions/skeptical/credulous OK; consensual_expand matches paper expansion.
- practical_reasoning validation and CQ5/6/11 fine.
- bipolar _supported_targets/set_supports (n>=2 path) correct incl. cycles.
- Cayrol supported/indirect single-direction derivations themselves correct (first/second loops map to Def.3 correctly, naming confusing).

## Minor / notes
- adf.py:491-550 dead duplicate _FormulaParser (same class lives in adf_io.py) — drift hazard.
- is_admissible with partial-domain interpretation returns False silently (domain mismatch in _information_leq) instead of raising.
- classify_link returns NEITHER for non-links instead of raising (conflates with dependent).
- skeptically_accepted_arguments returns {} when no completion has any stable extension; ICCMA DS convention would be "all accepted" — convention-dependent, flag PLAUSIBLE.
- value_preferred raises KeyError (not ValueError) for unknown values.

## Remaining before final report
- Skim tests/frameworks/test_vaf.py, test_caf.py, test_setaf.py, test_partial_af*.py for failure-mode coverage gaps (mostly done via grep).
- Compose final findings message (no report file).
