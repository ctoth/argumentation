"""Core tests for tiny partial argumentation frameworks."""

from __future__ import annotations

from itertools import combinations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.partial_af import (
    PartialArgumentationFramework,
    enumerate_completions,
    merge_framework_edit_distance,
)


def _powerset(items: frozenset[tuple[str, str]]) -> set[frozenset[tuple[str, str]]]:
    ordered = sorted(items)
    return {
        frozenset(choice)
        for size in range(len(ordered) + 1)
        for choice in combinations(ordered, size)
    }


def _tiny_paf() -> PartialArgumentationFramework:
    return PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks={("A", "B")},
        ignorance={("A", "A"), ("B", "A")},
        non_attacks={("B", "B")},
    )


def test_partial_argumentation_framework_tracks_total_partition():
    paf = _tiny_paf()

    assert paf.ordered_pairs == frozenset(
        {("A", "A"), ("A", "B"), ("B", "A"), ("B", "B")}
    )
    assert paf.attacks | paf.ignorance | paf.non_attacks == paf.ordered_pairs
    assert paf.attacks.isdisjoint(paf.ignorance)
    assert paf.attacks.isdisjoint(paf.non_attacks)
    assert paf.ignorance.isdisjoint(paf.non_attacks)


@pytest.mark.parametrize(
    ("attacks", "ignorance", "non_attacks"),
    [
        (
            {("A", "B")},
            {("A", "B")},
            {("A", "A"), ("B", "A"), ("B", "B")},
        ),
        (
            {("A", "B")},
            set(),
            {("A", "A"), ("B", "B")},
        ),
    ],
)
def test_partial_argumentation_framework_rejects_non_partitions(
    attacks: set[tuple[str, str]],
    ignorance: set[tuple[str, str]],
    non_attacks: set[tuple[str, str]],
):
    with pytest.raises(ValueError):
        PartialArgumentationFramework(
            arguments={"A", "B"},
            attacks=attacks,
            ignorance=ignorance,
            non_attacks=non_attacks,
        )


def test_paf_completions_are_sound_dung_frameworks():
    paf = _tiny_paf()

    completions = enumerate_completions(paf)

    assert completions
    for completion in completions:
        assert isinstance(completion, ArgumentationFramework)
        assert completion.arguments == paf.arguments
        assert paf.attacks <= completion.defeats
        assert completion.defeats <= paf.attacks | paf.ignorance
        assert completion.defeats.isdisjoint(paf.non_attacks)


def test_paf_completions_are_exact_and_counted_by_ignorance_choices():
    paf = _tiny_paf()

    expected = {
        frozenset(paf.attacks | choice)
        for choice in _powerset(paf.ignorance)
    }
    actual = {completion.defeats for completion in enumerate_completions(paf)}

    assert actual == expected
    assert len(actual) == 2 ** len(paf.ignorance)


def test_merge_framework_edit_distance_is_identity_and_symmetric():
    left = _tiny_paf()
    right = PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks={("A", "B"), ("B", "A")},
        ignorance={("A", "A")},
        non_attacks={("B", "B")},
    )

    assert merge_framework_edit_distance(left, left) == 0
    assert merge_framework_edit_distance(left, right) == 1
    assert merge_framework_edit_distance(right, left) == 1


def test_merge_framework_edit_distance_satisfies_triangle_inequality():
    left = _tiny_paf()
    middle = PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks={("A", "B"), ("B", "A")},
        ignorance={("A", "A")},
        non_attacks={("B", "B")},
    )
    right = PartialArgumentationFramework(
        arguments={"A", "B"},
        attacks=set(),
        ignorance={("A", "A"), ("B", "A")},
        non_attacks={("A", "B"), ("B", "B")},
    )

    direct = merge_framework_edit_distance(left, right)
    via_middle = (
        merge_framework_edit_distance(left, middle)
        + merge_framework_edit_distance(middle, right)
    )

    assert direct <= via_middle
