"""Regression tests for BUG-3: recursive ``_is_acyclic`` DFS overflowing the stack.

Both ``argumentation.solving.af_sat._is_acyclic`` and
``argumentation.core.labelling._is_acyclic`` used a recursive ``visit()`` closure
that recursed one Python stack frame per graph edge along a path. A long acyclic
chain (a0 -> a1 -> ... -> a_{N-1}) therefore raised ``RecursionError`` once N
exceeded Python's recursion limit. These tests pin the iterative behaviour and the
preserved semantics for both copies.
"""

from __future__ import annotations

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.core.labelling import _is_acyclic as labelling_is_acyclic
from argumentation.solving.af_sat import _is_acyclic as af_sat_is_acyclic

_IS_ACYCLIC = pytest.mark.parametrize(
    "is_acyclic",
    [af_sat_is_acyclic, labelling_is_acyclic],
    ids=["af_sat", "labelling"],
)


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def _chain(length: int) -> ArgumentationFramework:
    """a0 -> a1 -> ... -> a_{length-1}, no back-edges (acyclic)."""
    args = {f"a{index}" for index in range(length)}
    defeats = {(f"a{index}", f"a{index + 1}") for index in range(length - 1)}
    return af(args, defeats)


@_IS_ACYCLIC
def test_long_acyclic_chain_does_not_overflow(is_acyclic) -> None:
    # N well above CPython's default recursion limit (~1000): recursive DFS
    # raises RecursionError here today.
    framework = _chain(3000)
    assert is_acyclic(framework) is True


# --- Semantics preservation -------------------------------------------------


@_IS_ACYCLIC
def test_small_cycle_is_not_acyclic(is_acyclic) -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})
    assert is_acyclic(framework) is False


@_IS_ACYCLIC
def test_long_chain_looping_back_is_not_acyclic(is_acyclic) -> None:
    framework = _chain(3000)
    looped = af(
        set(framework.arguments),
        set(framework.defeats) | {("a2999", "a0")},
    )
    assert is_acyclic(looped) is False


@_IS_ACYCLIC
def test_small_dag_is_acyclic(is_acyclic) -> None:
    framework = af(
        {"a", "b", "c", "d"},
        {("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")},
    )
    assert is_acyclic(framework) is True


@_IS_ACYCLIC
def test_empty_framework_is_acyclic(is_acyclic) -> None:
    assert is_acyclic(af(set(), set())) is True


@_IS_ACYCLIC
def test_single_argument_without_defeats_is_acyclic(is_acyclic) -> None:
    assert is_acyclic(af({"a"}, set())) is True


@_IS_ACYCLIC
def test_self_loop_is_not_acyclic(is_acyclic) -> None:
    assert is_acyclic(af({"a"}, {("a", "a")})) is False
