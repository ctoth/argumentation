"""Immutable snapshots for mapping fields of frozen framework types."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def freeze_mapping(mapping: Mapping[K, V]) -> Mapping[K, V]:
    """Return a read-only snapshot of ``mapping``.

    The snapshot copies the entries, so later changes to the caller's mapping
    do not reach it, and wraps them in ``MappingProxyType``, so item
    assignment on the stored field raises ``TypeError``.
    """
    return MappingProxyType(dict(mapping))
