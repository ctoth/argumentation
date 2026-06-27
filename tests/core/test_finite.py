from __future__ import annotations

import pytest

from argumentation.core.finite import (
    iter_subsets_bitmask,
    maximal_by,
    maximal_sets,
    normalize_binary_relation,
    predecessors_index,
    sorted_extensions,
    strongly_connected_components,
    subsets_by_size,
    successors_index,
)


class ReprOnly:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


def test_normalize_binary_relation_validates_universe() -> None:
    assert normalize_binary_relation(
        "edges",
        frozenset({("a", "b")}),
        frozenset({"a", "b"}),
    ) == frozenset({("a", "b")})

    with pytest.raises(ValueError, match="edges"):
        normalize_binary_relation(
            "edges",
            frozenset({("a", "missing")}),
            frozenset({"a"}),
        )


def test_relation_indexes_can_include_empty_nodes() -> None:
    relation = frozenset({("a", "b"), ("c", "b")})

    assert predecessors_index(relation, nodes=frozenset({"a", "b", "c"})) == {
        "a": frozenset(),
        "b": frozenset({"a", "c"}),
        "c": frozenset(),
    }
    assert successors_index(relation, nodes=frozenset({"a", "b", "c"})) == {
        "a": frozenset({"b"}),
        "b": frozenset(),
        "c": frozenset({"b"}),
    }


def test_subset_orders_are_explicit() -> None:
    arguments = frozenset({"a", "b", "c"})

    assert list(iter_subsets_bitmask(arguments))[:4] == [
        frozenset(),
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"a", "b"}),
    ]
    assert subsets_by_size(arguments)[:5] == [
        frozenset(),
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"c"}),
        frozenset({"a", "b"}),
    ]


def test_sorted_extensions_support_repr_only_members() -> None:
    a = ReprOnly("a")
    b = ReprOnly("b")

    assert sorted_extensions(
        [frozenset({b}), frozenset({a, b}), frozenset({a})],
        key=repr,
    ) == (
        frozenset({a}),
        frozenset({b}),
        frozenset({a, b}),
    )


def test_maximal_sets_keeps_inclusion_maximal_members() -> None:
    # Nested chain: only the largest survives.
    assert maximal_sets(
        [frozenset({"a"}), frozenset({"a", "b"}), frozenset({"a", "b", "c"})]
    ) == [frozenset({"a", "b", "c"})]

    # Incomparable sets are all maximal; input order is preserved.
    assert maximal_sets([frozenset({"a"}), frozenset({"b"})]) == [
        frozenset({"a"}),
        frozenset({"b"}),
    ]

    # Mixed: the strict subset is dropped, incomparable ones kept in order.
    assert maximal_sets(
        [frozenset({"a"}), frozenset({"a", "b"}), frozenset({"c"})]
    ) == [frozenset({"a", "b"}), frozenset({"c"})]

    # Duplicates are NOT removed: equal sets are not strict subsets.
    assert maximal_sets([frozenset({"a"}), frozenset({"a"})]) == [
        frozenset({"a"}),
        frozenset({"a"}),
    ]

    # Singletons and the empty family.
    assert maximal_sets([frozenset({"a"})]) == [frozenset({"a"})]
    assert maximal_sets([]) == []

    # An empty set is a strict subset of any non-empty member, so it drops out
    # unless it is the only member.
    assert maximal_sets([frozenset(), frozenset({"a"})]) == [frozenset({"a"})]
    assert maximal_sets([frozenset()]) == [frozenset()]


def test_maximal_by_ranks_members_by_key() -> None:
    # The key, not the member, decides maximality. Members carry a tag plus the
    # frozenset used as the ranking key.
    def key(member: tuple[str, frozenset[int]]) -> frozenset[int]:
        return member[1]

    # Chain by key: only the member with the largest key survives, even though
    # the surviving member's own tag is unrelated to the key.
    a = ("a", frozenset({1}))
    b = ("b", frozenset({1, 2}))
    c = ("c", frozenset({1, 2, 3}))
    assert maximal_by([a, b, c], key) == [c]

    # Incomparable keys: every member survives and input order is preserved.
    x = ("x", frozenset({1}))
    y = ("y", frozenset({2}))
    assert maximal_by([x, y], key) == [x, y]

    # Ties: members with equal keys are not strict subsets of one another, so
    # every one survives (no deduplication), even with distinct tags.
    t1 = ("t1", frozenset({1, 2}))
    t2 = ("t2", frozenset({1, 2}))
    assert maximal_by([t1, t2], key) == [t1, t2]

    # Mixed: the strictly contained member drops; incomparable ones stay in
    # order. ``a``'s key {1} is contained in ``b``'s key {1, 2}; ``z``'s key {3}
    # is incomparable to both.
    z = ("z", frozenset({3}))
    assert maximal_by([a, b, z], key) == [b, z]

    # Empty family.
    assert maximal_by([], key) == []


def test_maximal_by_with_identity_matches_maximal_sets() -> None:
    candidates = [
        frozenset({"a"}),
        frozenset({"a", "b"}),
        frozenset({"c"}),
        frozenset({"a", "b"}),
    ]
    assert maximal_by(candidates, lambda member: member) == maximal_sets(candidates)


def test_strongly_connected_components_are_deterministic() -> None:
    graph = {
        "a": {"b"},
        "b": {"a", "c"},
        "c": set(),
    }

    assert strongly_connected_components(graph) == [
        frozenset({"a", "b"}),
        frozenset({"c"}),
    ]
