"""Tests for generic preference helpers."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.preference import (
    defeat_holds,
    strict_partial_order_closure,
    strictly_weaker,
)


_strengths = st.floats(
    min_value=0.0,
    max_value=10.0,
    allow_nan=False,
    allow_infinity=False,
)
_strength_sets = st.lists(_strengths, min_size=1, max_size=5)
_comparisons = st.sampled_from(["elitist", "democratic"])
_PROP_SETTINGS = settings(deadline=None)


def test_strict_partial_order_closure_adds_transitive_pairs() -> None:
    assert strict_partial_order_closure({("r1", "r2"), ("r2", "r3")}) == frozenset(
        {
            ("r1", "r2"),
            ("r2", "r3"),
            ("r1", "r3"),
        }
    )


def test_strict_partial_order_closure_rejects_cycles() -> None:
    with pytest.raises(ValueError, match="cycle"):
        strict_partial_order_closure({("r1", "r2"), ("r2", "r1")})


class TestStrictlyWeakerConcrete:
    def test_elitist_weaker(self) -> None:
        assert strictly_weaker([1, 5], [3, 4], "elitist") is True

    def test_elitist_not_weaker(self) -> None:
        assert strictly_weaker([3, 5], [3, 4], "elitist") is False

    def test_democratic_weaker(self) -> None:
        assert strictly_weaker([1, 2], [3, 4], "democratic") is True

    def test_democratic_not_weaker(self) -> None:
        assert strictly_weaker([1, 5], [3, 4], "democratic") is False

    def test_empty_left_set_is_not_strictly_weaker(self) -> None:
        assert strictly_weaker([], [3, 4], "elitist") is False
        assert strictly_weaker([], [3, 4], "democratic") is False

    def test_ws_o_arg_non_empty_set_is_strictly_weaker_than_empty_boundary(self) -> None:
        """Bug 6: Modgil-Prakken Def 19 makes non-empty gamma < empty gamma'."""
        assert strictly_weaker([1, 2], [], "elitist") is True
        assert strictly_weaker([1, 2], [], "democratic") is True


class TestDefeatHoldsConcrete:
    def test_undercut_always_defeats(self) -> None:
        assert defeat_holds("undercuts", [0.1], [0.9], "elitist") is True
        assert defeat_holds("undercuts", [0.1], [0.9], "democratic") is True

    def test_supersedes_always_defeats(self) -> None:
        assert defeat_holds("supersedes", [0.1], [0.9], "elitist") is True

    def test_rebut_blocked_when_weaker(self) -> None:
        assert defeat_holds("rebuts", [1], [5], "elitist") is False

    def test_rebut_succeeds_when_equal(self) -> None:
        assert defeat_holds("rebuts", [3], [3], "elitist") is True


@given(_strength_sets, _comparisons)
@_PROP_SETTINGS
def test_strictly_weaker_irreflexive(strengths: list[float], mode: str) -> None:
    assert strictly_weaker(strengths, strengths, mode) is False


@given(_strength_sets, _strength_sets, _comparisons)
@_PROP_SETTINGS
def test_strictly_weaker_asymmetric(
    left: list[float],
    right: list[float],
    mode: str,
) -> None:
    if strictly_weaker(left, right, mode):
        assert strictly_weaker(right, left, mode) is False


@given(_strength_sets, _strength_sets, _comparisons)
@_PROP_SETTINGS
def test_undercuts_always_defeat(
    left: list[float],
    right: list[float],
    mode: str,
) -> None:
    assert defeat_holds("undercuts", left, right, mode) is True
