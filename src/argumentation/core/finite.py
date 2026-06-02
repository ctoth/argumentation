"""Shared helpers for finite sets and binary relations."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Any, TypeVar, cast


T = TypeVar("T")


def _ordered_items(
    items: Iterable[T],
    key: Callable[[T], Any] | None,
) -> tuple[T, ...]:
    if key is None:
        return cast(tuple[T, ...], tuple(sorted(cast(Iterable[Any], items))))
    return tuple(sorted(items, key=key))


def _ordered_key_values(
    items: Iterable[T],
    key: Callable[[T], Any] | None,
) -> tuple[object, ...]:
    ordered = _ordered_items(items, key)
    if key is None:
        return cast(tuple[object, ...], ordered)
    return tuple(key(item) for item in ordered)


def normalize_binary_relation(
    name: str,
    relation: Iterable[tuple[T, T]],
    universe: frozenset[T],
    *,
    value: Callable[[T], T] | None = None,
    error_template: str = "{name} must only contain pairs over arguments: {unknown!r}",
) -> frozenset[tuple[T, T]]:
    """Coerce a binary relation and validate that both endpoints are declared."""
    if value is None:
        normalized = frozenset((source, target) for source, target in relation)
    else:
        normalized = frozenset((value(source), value(target)) for source, target in relation)
    unknown = sorted(
        (source, target)
        for source, target in normalized
        if source not in universe or target not in universe
    )
    if unknown:
        raise ValueError(error_template.format(name=name, unknown=unknown))
    return normalized


def predecessors_index(
    relation: Iterable[tuple[T, T]],
    *,
    nodes: Iterable[T] | None = None,
) -> dict[T, frozenset[T]]:
    """Build target -> sources adjacency for a binary relation."""
    predecessors: dict[T, set[T]] = {}
    if nodes is not None:
        predecessors = {node: set() for node in nodes}
    for source, target in relation:
        predecessors.setdefault(target, set()).add(source)
    return {
        target: frozenset(sources)
        for target, sources in predecessors.items()
    }


def successors_index(
    relation: Iterable[tuple[T, T]],
    *,
    nodes: Iterable[T] | None = None,
) -> dict[T, frozenset[T]]:
    """Build source -> targets adjacency for a binary relation."""
    successors: dict[T, set[T]] = {}
    if nodes is not None:
        successors = {node: set() for node in nodes}
    for source, target in relation:
        successors.setdefault(source, set()).add(target)
    return {
        source: frozenset(targets)
        for source, targets in successors.items()
    }


def iter_subsets_bitmask(
    items: Iterable[T],
    *,
    key: Callable[[T], Any] | None = None,
) -> Iterator[frozenset[T]]:
    """Yield all subsets in sorted bit-mask order."""
    ordered = _ordered_items(items, key)
    for mask in range(1 << len(ordered)):
        yield frozenset(
            ordered[index]
            for index in range(len(ordered))
            if mask & (1 << index)
        )


def subsets_bitmask(
    items: Iterable[T],
    *,
    key: Callable[[T], Any] | None = None,
) -> list[frozenset[T]]:
    """Return all subsets in sorted bit-mask order."""
    return list(iter_subsets_bitmask(items, key=key))


def subsets_by_size(
    items: Iterable[T],
    *,
    key: Callable[[T], Any] | None = None,
) -> list[frozenset[T]]:
    """Return all subsets ordered by size, then sorted item order."""
    ordered = _ordered_items(items, key)
    return [
        frozenset(ordered[index] for index in range(len(ordered)) if mask & (1 << index))
        for size in range(len(ordered) + 1)
        for mask in range(1 << len(ordered))
        if mask.bit_count() == size
    ]


def extension_sort_key(
    extension: frozenset[T],
    *,
    key: Callable[[T], Any] | None = None,
) -> tuple[int, tuple[object, ...]]:
    """Canonical extension ordering: smaller sets first, then lexical members."""
    return (len(extension), _ordered_key_values(extension, key))


def sorted_extensions(
    extensions: Iterable[frozenset[T]],
    *,
    key: Callable[[T], Any] | None = None,
    unique: bool = False,
) -> tuple[frozenset[T], ...]:
    """Sort extension families by size and member order."""
    values: Iterable[frozenset[T]]
    if unique:
        values = {frozenset(extension) for extension in extensions}
    else:
        values = extensions
    return tuple(sorted(values, key=lambda extension: extension_sort_key(extension, key=key)))


def strongly_connected_components(
    graph: Mapping[T, Iterable[T]],
    *,
    key: Callable[[T], Any] | None = None,
) -> list[frozenset[T]]:
    """Return strongly connected components of a finite directed graph."""
    nodes = set(graph)
    for successors in graph.values():
        nodes.update(successors)

    index = 0
    stack: list[T] = []
    on_stack: set[T] = set()
    indices: dict[T, int] = {}
    lowlinks: dict[T, int] = {}
    components: list[frozenset[T]] = []

    def connect(node: T) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for successor in _ordered_items(graph.get(node, ()), key):
            if successor not in indices:
                connect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[successor])

        if lowlinks[node] == indices[node]:
            component: set[T] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(frozenset(component))

    for node in _ordered_items(nodes, key):
        if node not in indices:
            connect(node)

    return sorted(
        components,
        key=lambda component: _ordered_key_values(component, key),
    )
