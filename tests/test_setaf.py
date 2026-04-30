from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.dung import (
    ArgumentationFramework,
    admissible as dung_admissible,
    complete_extensions as dung_complete_extensions,
    conflict_free as dung_conflict_free,
    grounded_extension,
    preferred_extensions,
    stable_extensions as dung_stable_extensions,
)
from argumentation.setaf import (
    SETAF,
    admissible,
    attacks_argument,
    characteristic_fn,
    complete_extensions,
    conflict_free,
    defends,
    grounded_extension as setaf_grounded_extension,
    preferred_extensions as setaf_preferred_extensions,
    range_of,
    stable_extensions,
)


ARGUMENTS = frozenset({"a", "b", "c", "d"})
SMALL_ARGUMENTS = ("a", "b", "c", "d")


def _all_subsets(arguments: frozenset[str]) -> tuple[frozenset[str], ...]:
    ordered = sorted(arguments)
    return tuple(
        frozenset(argument for index, argument in enumerate(ordered) if mask & (1 << index))
        for mask in range(1 << len(ordered))
    )


@st.composite
def setafs(draw: st.DrawFn) -> SETAF:
    arguments = frozenset(draw(st.sets(st.sampled_from(SMALL_ARGUMENTS), max_size=4)))
    possible_attacks = [
        (tail, target)
        for tail in _all_subsets(arguments)
        if tail
        for target in sorted(arguments)
    ]
    attack_strategy = (
        st.just(set())
        if not possible_attacks
        else st.sets(st.sampled_from(possible_attacks), max_size=8)
    )
    attacks = frozenset(draw(attack_strategy))
    return SETAF(arguments=arguments, attacks=attacks)


@st.composite
def singleton_tail_frameworks(draw: st.DrawFn) -> tuple[SETAF, ArgumentationFramework]:
    arguments = frozenset(draw(st.sets(st.sampled_from(SMALL_ARGUMENTS), max_size=4)))
    possible_defeats = [
        (attacker, target)
        for attacker in sorted(arguments)
        for target in sorted(arguments)
    ]
    defeat_strategy = (
        st.just(set())
        if not possible_defeats
        else st.sets(st.sampled_from(possible_defeats), max_size=8)
    )
    defeats = frozenset(draw(defeat_strategy))
    setaf = SETAF(
        arguments=arguments,
        attacks=frozenset((frozenset({attacker}), target) for attacker, target in defeats),
    )
    dung = ArgumentationFramework(arguments=arguments, defeats=defeats)
    return setaf, dung


def test_collective_attack_requires_all_attackers() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )

    assert conflict_free(framework, frozenset({"a", "c"})) is True
    assert conflict_free(framework, frozenset({"a", "b", "c"})) is False


def test_admissibility_defends_against_collective_attackers() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c", "x", "y"}),
        attacks=frozenset(
            {
                (frozenset({"a", "b"}), "c"),
                (frozenset({"x"}), "a"),
                (frozenset({"y"}), "b"),
            }
        ),
    )

    assert admissible(framework, frozenset({"c"})) is False
    assert admissible(framework, frozenset({"c", "x"})) is True
    assert admissible(framework, frozenset({"c", "x", "y"})) is True


def test_setaf_rejects_empty_attack_tails_from_definition_1() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        SETAF(
            arguments=frozenset({"a"}),
            attacks=frozenset({(frozenset(), "a")}),
        )


def test_defense_attacks_at_least_one_member_of_collective_tail() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c", "x"}),
        attacks=frozenset(
            {
                (frozenset({"a", "b"}), "c"),
                (frozenset({"x"}), "a"),
            }
        ),
    )

    assert defends(framework, frozenset({"x"}), "c") is True


def test_singleton_setaf_reduces_to_dung_for_grounded_and_preferred() -> None:
    attacks = frozenset({(frozenset({"a"}), "b"), (frozenset({"b"}), "a")})
    setaf = SETAF(arguments=frozenset({"a", "b"}), attacks=attacks)
    dung = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    assert setaf_grounded_extension(setaf) == grounded_extension(dung)
    assert set(setaf_preferred_extensions(setaf)) == set(preferred_extensions(dung))


def test_stable_extensions_cover_outsiders_with_collective_attacks() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )

    assert stable_extensions(framework) == (frozenset({"a", "b"}),)


def test_grounded_extension_is_subset_minimal_complete_extension() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c", "d"}),
        attacks=frozenset(
            {
                (frozenset({"a", "b"}), "c"),
                (frozenset({"c"}), "d"),
            }
        ),
    )

    grounded = setaf_grounded_extension(framework)
    completes = complete_extensions(framework)

    assert grounded in completes
    assert not any(candidate < grounded for candidate in completes)


@given(setafs())
@settings(max_examples=100)
def test_definition_1_attack_activation_iff_tail_is_contained(framework: SETAF) -> None:
    for candidate in _all_subsets(framework.arguments):
        for target in framework.arguments:
            assert attacks_argument(framework, candidate, target) is any(
                tail <= candidate and attacked == target
                for tail, attacked in framework.attacks
            )


@given(setafs())
@settings(max_examples=100)
def test_definition_2_conflict_free_iff_no_active_attack_hits_candidate(
    framework: SETAF,
) -> None:
    for candidate in _all_subsets(framework.arguments):
        assert conflict_free(framework, candidate) is not any(
            tail <= candidate and target in candidate
            for tail, target in framework.attacks
        )


@given(setafs())
@settings(max_examples=100)
def test_definition_3_stable_iff_conflict_free_and_full_range(framework: SETAF) -> None:
    expected = {
        candidate
        for candidate in _all_subsets(framework.arguments)
        if conflict_free(framework, candidate)
        and range_of(framework, candidate) == framework.arguments
    }

    assert set(stable_extensions(framework)) == expected


@given(setafs())
@settings(max_examples=100)
def test_grounded_is_subset_minimal_complete_extension(framework: SETAF) -> None:
    grounded = setaf_grounded_extension(framework)
    completes = complete_extensions(framework)

    assert grounded in completes
    assert not any(candidate < grounded for candidate in completes)


@given(setafs())
@settings(max_examples=100)
def test_characteristic_function_is_monotone(framework: SETAF) -> None:
    subsets = _all_subsets(framework.arguments)
    for left in subsets:
        for right in subsets:
            if left <= right:
                assert characteristic_fn(framework, left) <= characteristic_fn(framework, right)


@given(setafs())
@settings(max_examples=100)
def test_complete_extensions_are_exactly_admissible_fixed_points(
    framework: SETAF,
) -> None:
    expected = {
        candidate
        for candidate in _all_subsets(framework.arguments)
        if admissible(framework, candidate)
        and characteristic_fn(framework, candidate) == candidate
    }

    assert set(complete_extensions(framework)) == expected


@given(singleton_tail_frameworks())
@settings(max_examples=100)
def test_singleton_tail_setafs_reduce_to_dung_semantics(
    pair: tuple[SETAF, ArgumentationFramework],
) -> None:
    setaf, dung = pair

    for candidate in _all_subsets(setaf.arguments):
        assert conflict_free(setaf, candidate) is dung_conflict_free(candidate, dung.defeats)
        assert admissible(setaf, candidate) is dung_admissible(
            candidate,
            dung.arguments,
            dung.defeats,
        )

    assert set(complete_extensions(setaf)) == set(dung_complete_extensions(dung))
    assert setaf_grounded_extension(setaf) == grounded_extension(dung)
    assert set(setaf_preferred_extensions(setaf)) == set(preferred_extensions(dung))
    assert set(stable_extensions(setaf)) == set(dung_stable_extensions(dung))
