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

    successors_by_node = {
        node: _ordered_items(graph.get(node, ()), key)
        for node in nodes
    }
    predecessors_by_node: dict[T, set[T]] = {node: set() for node in nodes}
    for source, successors in successors_by_node.items():
        for target in successors:
            predecessors_by_node.setdefault(target, set()).add(source)

    visited: set[T] = set()
    finish_order: list[T] = []
    components: list[frozenset[T]] = []

    for node in _ordered_items(nodes, key):
        if node in visited:
            continue
        visited.add(node)
        stack: list[tuple[T, Iterator[T]]] = [
            (node, iter(successors_by_node.get(node, ())))
        ]
        while stack:
            current, successors = stack[-1]
            for successor in successors:
                if successor in visited:
                    continue
                visited.add(successor)
                stack.append((successor, iter(successors_by_node.get(successor, ()))))
                break
            else:
                finish_order.append(current)
                stack.pop()

    assigned: set[T] = set()
    for node in reversed(finish_order):
        if node in assigned:
            continue
        component: set[T] = set()
        component_stack = [node]
        assigned.add(node)
        while component_stack:
            current = component_stack.pop()
            component.add(current)
            for predecessor in _ordered_items(predecessors_by_node.get(current, ()), key):
                if predecessor in assigned:
                    continue
                assigned.add(predecessor)
                component_stack.append(predecessor)
        components.append(frozenset(component))

    return sorted(
        components,
        key=lambda component: _ordered_key_values(component, key),
    )


def is_acyclic(
    graph: Mapping[T, Iterable[T]],
    *,
    key: Callable[[T], Any] | None = None,
) -> bool:
    """Return ``True`` iff a finite directed graph contains no cycle.

    Uses an iterative post-order DFS (explicit stack) so a long chain of nodes
    does not recurse one Python frame per edge and raise ``RecursionError``.
    Each stack entry is ``(node, entered)``: the first pop with ``entered=False``
    marks the node grey and re-pushes it as ``entered=True`` beneath its
    children; the second pop (``entered=True``) marks it black. A grey node
    reached again is a cycle. Roots and successors are iterated in sorted order
    so the result does not depend on the graph's insertion order.
    """
    nodes = set(graph)
    for successors in graph.values():
        nodes.update(successors)

    successors_by_node = {
        node: _ordered_items(graph.get(node, ()), key)
        for node in nodes
    }

    visiting: set[T] = set()
    visited: set[T] = set()

    for root in _ordered_items(nodes, key):
        if root in visited:
            continue
        stack: list[tuple[T, bool]] = [(root, False)]
        while stack:
            node, entered = stack.pop()
            if entered:
                visiting.discard(node)
                visited.add(node)
                continue
            if node in visited:
                continue
            if node in visiting:
                return False
            visiting.add(node)
            stack.append((node, True))
            for target in successors_by_node.get(node, ()):
                if target in visiting:
                    return False
                if target not in visited:
                    stack.append((target, False))

    return True
