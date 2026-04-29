"""Tests for Dung's abstract argumentation semantics.

Property-based tests verify formal theorems from:
    Dung, P.M. (1995). On the acceptability of arguments and its
    fundamental role in nonmonotonic reasoning, logic programming
    and n-person games. Artificial Intelligence, 77(2), 321-357.

Concrete regression tests use known examples from the paper.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from argumentation.dung import (
    ArgumentationFramework,
    attackers_of,
    characteristic_fn,
    admissible,
    cf2_extensions,
    conflict_free,
    complete_extensions,
    defends,
    grounded_extension,
    ideal_extension,
    preferred_extensions,
    range_of,
    semi_stable_extensions,
    stage_extensions,
    stable_extensions,
)
from argumentation.semantics import extensions
from argumentation.labelling import ExactEnumerationExceeded


# ── Hypothesis strategies ───────────────────────────────────────────


@st.composite
def argumentation_frameworks(draw, max_args=8):
    """Generate random argumentation frameworks for property testing."""
    args = draw(
        st.frozensets(
            st.text(alphabet="abcdefgh", min_size=1, max_size=2),
            min_size=1,
            max_size=max_args,
        )
    )
    arg_list = sorted(args)
    attacks = draw(
        st.frozensets(
            st.tuples(
                st.sampled_from(arg_list),
                st.sampled_from(arg_list),
            ),
            max_size=len(arg_list) ** 2,
        )
    )
    return ArgumentationFramework(arguments=args, defeats=attacks)


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = sorted(arguments)
    return [
        frozenset(arg for index, arg in enumerate(ordered) if mask & (1 << index))
        for mask in range(1 << len(ordered))
    ]


def _definition_range(
    extension: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    return extension | frozenset(
        target
        for attacker, target in defeats
        if attacker in extension
    )


def _draw_subset(data: st.DataObject, arguments: frozenset[str]) -> frozenset[str]:
    return frozenset(data.draw(st.sets(st.sampled_from(sorted(arguments)), max_size=len(arguments))))


# ── Concrete regression tests ───────────────────────────────────────


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    """Shorthand for building an AF from plain sets."""
    return ArgumentationFramework(
        arguments=frozenset(args),
        defeats=frozenset(defeats),
    )


class TestGroundedConcrete:
    """Concrete examples for grounded extension."""

    def test_empty_framework(self):
        """Empty AF has empty grounded extension."""
        assert grounded_extension(af(set(), set())) == frozenset()

    def test_unattacked_wins(self):
        """A attacks B, nothing attacks A. Grounded = {A}."""
        assert grounded_extension(af({"A", "B"}, {("A", "B")})) == frozenset({"A"})

    def test_nixon_diamond(self):
        """A attacks B, B attacks A. Grounded = {} (mutual defeat)."""
        assert grounded_extension(af({"A", "B"}, {("A", "B"), ("B", "A")})) == frozenset()

    def test_reinstatement(self):
        """A attacks B, B attacks C. A reinstates C. Grounded = {A, C}."""
        result = grounded_extension(af({"A", "B", "C"}, {("A", "B"), ("B", "C")}))
        assert result == frozenset({"A", "C"})

    def test_odd_cycle(self):
        """A->B->C->A. Grounded = {} (no unattacked argument)."""
        result = grounded_extension(
            af({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")})
        )
        assert result == frozenset()

    def test_self_attacker(self):
        """A attacks itself. Grounded = {}."""
        assert grounded_extension(af({"A"}, {("A", "A")})) == frozenset()

    def test_floating_defeat(self):
        """A attacks B and C, B and C attack each other. Grounded = {A}."""
        result = grounded_extension(
            af({"A", "B", "C"}, {("A", "B"), ("A", "C"), ("B", "C"), ("C", "B")})
        )
        assert result == frozenset({"A"})

    def test_no_attacks(self):
        """No attacks means all arguments are in grounded extension."""
        assert grounded_extension(af({"A", "B", "C"}, set())) == frozenset({"A", "B", "C"})

    def test_chain_of_four(self):
        """A->B->C->D. Grounded = {A, C}. A and C are defended."""
        result = grounded_extension(
            af({"A", "B", "C", "D"}, {("A", "B"), ("B", "C"), ("C", "D")})
        )
        assert result == frozenset({"A", "C"})

    def test_grounded_ignores_attack_metadata(self):
        """Grounded semantics always uses defeats, even when attacks are present."""
        fw = ArgumentationFramework(
            arguments=frozenset({"A", "B"}),
            defeats=frozenset(),
            attacks=frozenset({("A", "B")}),
        )
        assert grounded_extension(fw) == frozenset({"A", "B"})


class TestFrameworkValidation:
    def test_defeats_must_reference_declared_arguments(self) -> None:
        with pytest.raises(ValueError, match="defeats"):
            ArgumentationFramework(
                arguments=frozenset({"A"}),
                defeats=frozenset({("A", "B")}),
            )

    def test_attacks_must_reference_declared_arguments(self) -> None:
        with pytest.raises(ValueError, match="attacks"):
            ArgumentationFramework(
                arguments=frozenset({"A"}),
                defeats=frozenset(),
                attacks=frozenset({("B", "A")}),
            )


class TestPreferredConcrete:
    """Concrete examples for preferred extensions."""

    def test_nixon_diamond(self):
        """Nixon diamond has two preferred extensions: {A} and {B}."""
        exts = preferred_extensions(af({"A", "B"}, {("A", "B"), ("B", "A")}))
        assert len(exts) == 2
        assert frozenset({"A"}) in exts
        assert frozenset({"B"}) in exts

    def test_unattacked_wins(self):
        """A attacks B. Single preferred = {A}."""
        exts = preferred_extensions(af({"A", "B"}, {("A", "B")}))
        assert exts == [frozenset({"A"})]

    def test_reinstatement(self):
        """A->B->C. Single preferred = {A, C}."""
        exts = preferred_extensions(
            af({"A", "B", "C"}, {("A", "B"), ("B", "C")})
        )
        assert exts == [frozenset({"A", "C"})]

    def test_self_attacker(self):
        """Self-attacking A. Preferred = [{}] (empty set is maximal admissible)."""
        exts = preferred_extensions(af({"A"}, {("A", "A")}))
        assert exts == [frozenset()]

    def test_no_attacks(self):
        """No attacks. Single preferred = all arguments."""
        exts = preferred_extensions(af({"A", "B"}, set()))
        assert exts == [frozenset({"A", "B"})]


class TestStableConcrete:
    """Concrete examples for stable extensions."""

    def test_nixon_diamond(self):
        """Nixon diamond: two stable extensions {A} and {B}."""
        exts = stable_extensions(af({"A", "B"}, {("A", "B"), ("B", "A")}))
        assert len(exts) == 2
        assert frozenset({"A"}) in exts
        assert frozenset({"B"}) in exts

    def test_odd_cycle_no_stable(self):
        """A->B->C->A. No stable extension exists."""
        exts = stable_extensions(
            af({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")})
        )
        assert exts == []

    def test_self_attacker_no_stable(self):
        """Self-attacking A. No stable extension (can't defeat A from empty set)."""
        exts = stable_extensions(af({"A"}, {("A", "A")}))
        assert exts == []

    def test_unattacked_wins(self):
        """A attacks B. Stable = [{A}]."""
        exts = stable_extensions(af({"A", "B"}, {("A", "B")}))
        assert exts == [frozenset({"A"})]

    def test_no_attacks(self):
        """No attacks. Stable = [all args] (defeats all outsiders vacuously)."""
        exts = stable_extensions(af({"A", "B"}, set()))
        assert exts == [frozenset({"A", "B"})]

    def test_attack_metadata_blocks_preference_filtered_joint_stable_extension(self):
        """Stable sets are attack-conflict-free and defeat every outsider."""
        framework = ArgumentationFramework(
            arguments=frozenset({"A", "B"}),
            defeats=frozenset(),
            attacks=frozenset({("A", "B")}),
        )

        assert stable_extensions(framework) == []


class TestRangeSemanticsConcrete:
    """Concrete examples for range-based semantics."""

    def test_range_of_extension_is_extension_plus_defeated_arguments(self):
        """Grounded in Caminada 2011 page-image page 3, Definition 2.3."""
        assert range_of(
            frozenset({"A", "C"}),
            frozenset({("A", "B"), ("B", "C")}),
        ) == frozenset({"A", "B", "C"})

    def test_semi_stable_coincides_with_stable_when_stable_exists(self):
        """Semi-stable should agree with stable on stable-friendly AFs."""
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})

        assert set(semi_stable_extensions(framework)) == set(
            stable_extensions(framework)
        )

    def test_semi_stable_is_complete_with_maximal_range_when_no_stable_exists(self):
        """Odd cycles have no stable extension but still have semi-stable ones."""
        framework = af(
            {"A", "B", "C"},
            {("A", "B"), ("B", "C"), ("C", "A")},
        )

        assert stable_extensions(framework) == []
        assert semi_stable_extensions(framework) == [frozenset()]

    def test_stage_extensions_are_conflict_free_sets_with_maximal_range(self):
        """Stage does not require completeness, so an odd cycle has singleton stages."""
        framework = af(
            {"A", "B", "C"},
            {("A", "B"), ("B", "C"), ("C", "A")},
        )

        assert set(stage_extensions(framework)) == {
            frozenset({"A"}),
            frozenset({"B"}),
            frozenset({"C"}),
        }

    def test_dispatch_supports_semi_stable_and_stage(self):
        framework = af(
            {"A", "B", "C"},
            {("A", "B"), ("B", "C"), ("C", "A")},
        )

        assert extensions(framework, semantics="semi-stable") == (frozenset(),)
        assert extensions(framework, semantics="stage") == (
            frozenset({"A"}),
            frozenset({"B"}),
            frozenset({"C"}),
        )


class TestIdealConcrete:
    """Concrete examples for ideal semantics."""

    def test_ideal_can_be_less_skeptical_than_grounded(self):
        """Grounded in Dung, Mancarella, Toni 2007 page-image page 4."""
        framework = af(
            {"a", "b", "c", "d"},
            {
                ("a", "a"),
                ("a", "b"),
                ("b", "a"),
                ("c", "d"),
                ("d", "c"),
            },
        )

        assert grounded_extension(framework) == frozenset()
        assert set(preferred_extensions(framework)) == {
            frozenset({"b", "c"}),
            frozenset({"b", "d"}),
        }
        assert ideal_extension(framework) == frozenset({"b"})

    def test_ideal_can_be_proper_subset_of_preferred_intersection(self):
        """Grounded in Dung, Mancarella, Toni 2007 page-image pages 4-5."""
        framework = af(
            {"a", "b", "c", "d", "e", "f"},
            {
                ("a", "a"),
                ("a", "b"),
                ("b", "a"),
                ("c", "d"),
                ("d", "c"),
                ("c", "e"),
                ("d", "e"),
                ("e", "f"),
            },
        )

        assert set(preferred_extensions(framework)) == {
            frozenset({"b", "c", "f"}),
            frozenset({"b", "d", "f"}),
        }
        assert ideal_extension(framework) == frozenset({"b"})

    def test_dispatch_supports_ideal(self):
        framework = af(
            {"a", "b", "c", "d"},
            {
                ("a", "a"),
                ("a", "b"),
                ("b", "a"),
                ("c", "d"),
                ("d", "c"),
            },
        )

        assert extensions(framework, semantics="ideal") == (frozenset({"b"}),)


class TestCF2Concrete:
    """Concrete examples for CF2 semantics."""

    def test_cf2_uses_naive_sets_inside_a_single_scc(self):
        """Grounded in Gaggl and Woltran 2013 page-image pages 3 and 5."""
        framework = af(
            {"a", "b", "c"},
            {("a", "b"), ("b", "c"), ("c", "a")},
        )

        assert set(cf2_extensions(framework)) == {
            frozenset({"a"}),
            frozenset({"b"}),
            frozenset({"c"}),
        }

    def test_cf2_respects_component_defeat_across_sccs(self):
        """A selected upstream argument removes downstream arguments it defeats."""
        framework = af({"a", "b"}, {("a", "b")})

        assert cf2_extensions(framework) == [frozenset({"a"})]

    def test_cf2_matches_gaggl_woltran_2013_example_2_8(self):
        """Grounded in Gaggl and Woltran 2013 page-image page 5."""
        framework = af(
            {"a", "b", "c", "d", "e", "f", "g", "h", "i"},
            {
                ("a", "b"),
                ("b", "c"),
                ("c", "a"),
                ("b", "d"),
                ("b", "e"),
                ("d", "f"),
                ("e", "f"),
                ("f", "e"),
                ("f", "g"),
                ("g", "h"),
                ("h", "i"),
                ("i", "f"),
            },
        )

        assert set(cf2_extensions(framework)) == {
            frozenset({"a", "d", "e", "g", "i"}),
            frozenset({"b", "f", "h"}),
            frozenset({"b", "g", "i"}),
            frozenset({"c", "d", "e", "g", "i"}),
        }

    def test_dispatch_supports_cf2(self):
        framework = af(
            {"a", "b", "c"},
            {("a", "b"), ("b", "c"), ("c", "a")},
        )

        assert extensions(framework, semantics="cf2") == (
            frozenset({"a"}),
            frozenset({"b"}),
            frozenset({"c"}),
        )


class TestCitationDocumentation:
    """Documentation pins semantics choices that combine literature definitions."""

    def test_stable_extension_attack_defeat_choice_is_cited(self):
        text = Path("CITATIONS.md").read_text(encoding="utf-8")

        assert "stable_extensions" in text
        assert "Dung 1995" in text
        assert "Modgil" in text
        assert "Prakken" in text
        assert "attack-conflict-free" in text
        assert "defeat every argument outside" in text


class TestCompleteConcrete:
    """Concrete examples for complete extensions."""

    def test_nixon_diamond(self):
        """Nixon diamond: three complete extensions: {}, {A}, {B}."""
        exts = complete_extensions(af({"A", "B"}, {("A", "B"), ("B", "A")}))
        assert len(exts) == 3
        assert frozenset() in exts
        assert frozenset({"A"}) in exts
        assert frozenset({"B"}) in exts

    def test_no_attacks(self):
        """No attacks. Single complete = all arguments."""
        exts = complete_extensions(af({"A", "B"}, set()))
        assert exts == [frozenset({"A", "B"})]

    def test_complete_extensions_exposes_exact_enumeration_budget(self):
        framework = af(
            {"A", "B", "C", "D"},
            {("A", "B"), ("B", "A"), ("C", "D"), ("D", "C")},
        )

        with pytest.raises(ExactEnumerationExceeded, match="complete labellings"):
            complete_extensions(framework, max_candidates=3)


class TestHelpers:
    """Tests for helper functions."""

    def test_attackers_of(self):
        defeats = frozenset({("A", "B"), ("C", "B"), ("A", "C")})
        assert attackers_of("B", defeats) == frozenset({"A", "C"})
        assert attackers_of("C", defeats) == frozenset({"A"})
        assert attackers_of("A", defeats) == frozenset()

    def test_conflict_free_yes(self):
        defeats = frozenset({("A", "B")})
        assert conflict_free(frozenset({"A"}), defeats) is True
        assert conflict_free(frozenset({"B"}), defeats) is True

    def test_conflict_free_no(self):
        defeats = frozenset({("A", "B")})
        assert conflict_free(frozenset({"A", "B"}), defeats) is False

    def test_conflict_free_self_attack(self):
        defeats = frozenset({("A", "A")})
        assert conflict_free(frozenset({"A"}), defeats) is False

    def test_defends(self):
        all_args = frozenset({"A", "B", "C"})
        defeats = frozenset({("A", "B"), ("B", "C")})
        # A defends C because A attacks B (C's only attacker)
        assert defends(frozenset({"A"}), "C", all_args, defeats) is True
        # Empty set doesn't defend C (B attacks C, nothing counter-attacks B)
        assert defends(frozenset(), "C", all_args, defeats) is False

    def test_characteristic_fn(self):
        all_args = frozenset({"A", "B", "C"})
        defeats = frozenset({("A", "B"), ("B", "C")})
        # F({}) = {A} (A has no attackers, so defended by any set)
        assert characteristic_fn(frozenset(), all_args, defeats) == frozenset({"A"})
        # F({A}) = {A, C} (A defends itself + C)
        assert characteristic_fn(frozenset({"A"}), all_args, defeats) == frozenset({"A", "C"})

    def test_admissible(self):
        all_args = frozenset({"A", "B", "C"})
        defeats = frozenset({("A", "B"), ("B", "C")})
        assert admissible(frozenset({"A", "C"}), all_args, defeats) is True
        assert admissible(frozenset({"B"}), all_args, defeats) is False  # B attacked by A, can't defend


# ── Property tests ──────────────────────────────────────────────────


_PROP_SETTINGS = settings(deadline=None)


class TestDungDefinitionProperties:
    """Property tests for Dung 1995 definitions."""

    pytestmark = pytest.mark.property

    @given(framework=argumentation_frameworks(), data=st.data())
    @_PROP_SETTINGS
    def test_conflict_free_matches_dung_1995_page_326_definition(self, framework, data):
        """Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png`.

        Dung's conflict-free definition excludes every set that contains both
        sides of an attack relation.
        """
        candidate = _draw_subset(data, framework.arguments)

        expected = not any(
            attacker in candidate and target in candidate
            for attacker, target in framework.defeats
        )

        assert conflict_free(candidate, framework.defeats) is expected

    @given(framework=argumentation_frameworks(), data=st.data())
    @_PROP_SETTINGS
    def test_admissible_matches_dung_1995_page_326_definition(self, framework, data):
        """Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png`.

        An admissible set is conflict-free and every member is acceptable with
        respect to that set.
        """
        candidate = _draw_subset(data, framework.arguments)

        expected = conflict_free(candidate, framework.defeats) and all(
            defends(candidate, argument, framework.arguments, framework.defeats)
            for argument in candidate
        )

        assert admissible(candidate, framework.arguments, framework.defeats) is expected

    @given(argumentation_frameworks(max_args=6))
    @_PROP_SETTINGS
    def test_fundamental_lemma_dung_1995_page_327(self, framework):
        """Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-006.png`.

        If an admissible set S defends A and B, then S plus A remains
        admissible and still defends B.
        """
        for candidate in _all_subsets(framework.arguments):
            if not admissible(candidate, framework.arguments, framework.defeats):
                continue
            acceptable = characteristic_fn(candidate, framework.arguments, framework.defeats)
            for accepted_argument in acceptable:
                enlarged = candidate | {accepted_argument}
                assert admissible(enlarged, framework.arguments, framework.defeats)
                for still_accepted in acceptable:
                    assert defends(
                        enlarged,
                        still_accepted,
                        framework.arguments,
                        framework.defeats,
                    )


class TestGroundedProperties:
    """Property tests for grounded extension (Dung 1995 theorems)."""

    pytestmark = pytest.mark.property

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_conflict_free(self, framework):
        """P1: Grounded extension is conflict-free.

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png`.
        """
        ext = grounded_extension(framework)
        assert conflict_free(ext, framework.defeats)

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_admissible(self, framework):
        """P2: Grounded extension is admissible.

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png`.
        """
        ext = grounded_extension(framework)
        assert admissible(ext, framework.arguments, framework.defeats)

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_fixed_point(self, framework):
        """P7: Grounded is fixed point of F.

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-008.png`.
        """
        ext = grounded_extension(framework)
        assert characteristic_fn(ext, framework.arguments, framework.defeats) == ext

    @given(argumentation_frameworks(max_args=6))
    @_PROP_SETTINGS
    def test_grounded_is_least_fixed_point_dung_1995_page_329(self, framework):
        """Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-008.png`."""
        grounded = grounded_extension(framework)
        fixed_points = [
            candidate
            for candidate in _all_subsets(framework.arguments)
            if characteristic_fn(candidate, framework.arguments, framework.defeats) == candidate
        ]

        assert fixed_points
        assert all(grounded <= fixed_point for fixed_point in fixed_points)

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_subset_of_every_preferred(self, framework):
        """P3: Grounded is contained in every preferred extension.

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-008.png`.
        """
        grounded = grounded_extension(framework)
        for pref in preferred_extensions(framework):
            assert grounded <= pref

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_no_attacks_means_all_in(self, framework):
        """P10: Empty defeat set → grounded = all arguments."""
        assume(len(framework.defeats) == 0)
        assert grounded_extension(framework) == framework.arguments


class TestPreferredProperties:
    """Property tests for preferred extensions."""

    pytestmark = pytest.mark.property

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_all_admissible(self, framework):
        """P4: Every preferred extension is admissible.

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-006.png`.
        """
        for ext in preferred_extensions(framework):
            assert admissible(ext, framework.arguments, framework.defeats)

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_maximal_admissible(self, framework):
        """P12: Preferred extensions are maximal admissible sets."""
        prefs = preferred_extensions(framework)
        for ext in prefs:
            # No proper superset of ext should be admissible
            for arg in framework.arguments - ext:
                candidate = ext | {arg}
                if admissible(candidate, framework.arguments, framework.defeats):
                    # candidate is admissible and strictly larger — ext is not maximal
                    # But it must be a subset of some other preferred extension
                    assert any(candidate <= other for other in prefs)

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_at_least_one(self, framework):
        """Every AF has at least one preferred extension.

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-006.png`.
        """
        assert len(preferred_extensions(framework)) >= 1

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_are_complete(self, framework):
        """P5/P9: Every preferred extension is a complete extension."""
        prefs = set(preferred_extensions(framework))
        comps = set(complete_extensions(framework))
        for p in prefs:
            assert p in comps


class TestStableProperties:
    """Property tests for stable extensions."""

    pytestmark = pytest.mark.property

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_implies_preferred(self, framework):
        """P5: Every stable extension is a preferred extension (Thm 13)."""
        stables = set(stable_extensions(framework))
        prefs = set(preferred_extensions(framework))
        for s in stables:
            assert s in prefs

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_conflict_free_and_defeats_all_outsiders(self, framework):
        """P6: Stable = conflict-free + defeats all outsiders (Def 12)."""
        for ext in stable_extensions(framework):
            assert conflict_free(ext, framework.defeats)
            outsiders = framework.arguments - ext
            for out in outsiders:
                assert any((a, out) in framework.defeats for a in ext)


class TestCompleteProperties:
    """Property tests for complete extensions."""

    pytestmark = pytest.mark.property

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_are_fixed_points(self, framework):
        """P8: Complete extensions are fixed points of F (Def 10)."""
        for ext in complete_extensions(framework):
            assert characteristic_fn(ext, framework.arguments, framework.defeats) == ext

    @given(argumentation_frameworks())
    @_PROP_SETTINGS
    def test_grounded_is_least_complete(self, framework):
        """Grounded is the least (smallest) complete extension."""
        grounded = grounded_extension(framework)
        for ext in complete_extensions(framework):
            assert grounded <= ext


class TestNewSemanticsProperties:
    """Property coverage for non-Dung-1995 semantics added in this workstream."""

    pytestmark = pytest.mark.property

    @given(argumentation_frameworks(max_args=5))
    @_PROP_SETTINGS
    def test_semi_stable_extensions_are_complete_with_maximal_range(self, framework):
        completes = complete_extensions(framework)
        complete_ranges = {
            complete: _definition_range(complete, framework.defeats)
            for complete in completes
        }

        for extension in semi_stable_extensions(framework):
            assert extension in completes
            extension_range = complete_ranges[extension]
            assert not any(
                extension_range < other_range
                for other_range in complete_ranges.values()
            )

    @given(argumentation_frameworks(max_args=5))
    @_PROP_SETTINGS
    def test_stage_extensions_are_conflict_free_with_maximal_range(self, framework):
        conflict_free_sets = [
            candidate
            for candidate in _all_subsets(framework.arguments)
            if conflict_free(candidate, framework.defeats)
        ]
        ranges = {
            candidate: _definition_range(candidate, framework.defeats)
            for candidate in conflict_free_sets
        }

        for extension in stage_extensions(framework):
            assert extension in conflict_free_sets
            extension_range = ranges[extension]
            assert not any(
                extension_range < other_range
                for other_range in ranges.values()
            )

    @given(argumentation_frameworks(max_args=5))
    @_PROP_SETTINGS
    def test_ideal_is_maximal_admissible_subset_of_every_preferred(self, framework):
        ideal = ideal_extension(framework)
        preferred = preferred_extensions(framework)

        assert admissible(ideal, framework.arguments, framework.defeats)
        assert all(ideal <= extension for extension in preferred)

        for candidate in _all_subsets(framework.arguments):
            if not admissible(candidate, framework.arguments, framework.defeats):
                continue
            if all(candidate <= extension for extension in preferred):
                assert candidate <= ideal

    @given(argumentation_frameworks(max_args=5))
    @_PROP_SETTINGS
    def test_cf2_extensions_are_conflict_free(self, framework):
        for extension in cf2_extensions(framework):
            assert conflict_free(extension, framework.defeats)


class TestCharacteristicFnProperties:
    """Property tests for the characteristic function."""

    pytestmark = pytest.mark.property

    @given(framework=argumentation_frameworks(), data=st.data())
    @_PROP_SETTINGS
    def test_monotone(self, framework, data):
        """F is monotone: if S1 is a subset of S2, then F(S1) is a subset of F(S2).

        Grounded in `papers/Dung_1995_AcceptabilityArguments/pngs/page-008.png`.
        """
        args = framework.arguments
        defeats = framework.defeats
        lower = _draw_subset(data, args)
        remaining = args - lower
        extra = (
            frozenset(data.draw(st.sets(st.sampled_from(sorted(remaining)), max_size=len(remaining))))
            if remaining
            else frozenset()
        )
        upper = lower | extra

        assert characteristic_fn(lower, args, defeats) <= characteristic_fn(upper, args, defeats)


class TestSingleDungPath:
    def test_complete_labelling_path_handles_small_framework(self):
        framework = af({"A", "B"}, {("A", "B")})

        assert set(complete_extensions(framework)) == {
            frozenset({"A"}),
        }

    def test_complete_labelling_path_handles_larger_framework(self):
        args = {f"a{i}" for i in range(7)}
        framework = af(args, {(f"a{i}", f"a{(i + 1) % 7}") for i in range(7)})

        assert complete_extensions(framework) == [frozenset()]

    def test_preferred_labelling_path_handles_reinstatement(self):
        framework = af({"A", "B", "C"}, {("A", "B"), ("B", "C")})

        assert preferred_extensions(framework) == [frozenset({"A", "C"})]

    def test_stable_labelling_path_handles_odd_cycle(self):
        framework = af(
            {f"a{i}" for i in range(7)},
            {(f"a{i}", f"a{(i + 1) % 7}") for i in range(7)},
        )

        assert stable_extensions(framework) == []


# ── Attacks ≠ Defeats property tests (F27) ─────────────────────────


@st.composite
def af_with_attacks_superset(draw, max_args=6):
    """Generate AFs where attacks is a superset of defeats.

    Some attacks are filtered by preference, producing a strict
    subset as defeats.  This exercises the post-hoc attack-CF
    pruning path in grounded_extension (dung.py lines 126-150).
    """
    args = draw(
        st.frozensets(
            st.text(alphabet="abcdef", min_size=1, max_size=2),
            min_size=1,
            max_size=max_args,
        )
    )
    arg_list = sorted(args)
    # Generate all attacks first
    all_attacks = draw(
        st.frozensets(
            st.tuples(
                st.sampled_from(arg_list),
                st.sampled_from(arg_list),
            ),
            max_size=len(arg_list) ** 2,
        )
    )
    # Defeats is a subset of attacks (some attacks filtered by preference)
    defeats = draw(
        st.frozensets(
            st.sampled_from(sorted(all_attacks)) if all_attacks else st.nothing(),
            max_size=len(all_attacks),
        )
    )
    return ArgumentationFramework(
        arguments=args,
        defeats=defeats,
        attacks=all_attacks,
    )
