from __future__ import annotations

import pytest

from argumentation.core.finite import (
    iter_subsets_bitmask,
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
