"""Regression contracts for epistemic belief updates and term round trips.

Grounding: Hunter & Thimm (2017), "Probabilistic reasoning with abstract
argumentation frameworks" (papers/Hunter_2017_ProbabilisticReasoningAbstract
Argumentation/notes.md): assessments are repaired toward the constraint set by
the Euclidean distance d_2 (Def 10, p.24-25).
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import argumentation.probabilistic.epistemic as epistemic
from argumentation.probabilistic.epistemic import (
    LinearAtomicConstraint,
    LinearRelation,
    least_squares_update_labelling,
)


def _squared_distance(left: dict[str, float], right: dict[str, float]) -> float:
    return sum((left[key] - right[key]) ** 2 for key in left)


def test_least_squares_update_returns_nearest_feasible_point(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Issue #39: the update is the d_2-nearest feasible labelling (Hunter &
    Thimm 2017, Def 10, p.24-25). From (0, 0) under x >= 0.8 and
    x + y >= 1.5 the nearest point is (0.8, 0.7), squared distance 1.13;
    the feasibility check runs once and the projection itself calls no solver."""
    calls = 0
    original = epistemic.constraints_satisfiable

    def counted(*args: object) -> bool:
        nonlocal calls
        calls += 1
        assert calls <= 1
        return original(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(epistemic, "constraints_satisfiable", counted)
    current = {"x": 0.0, "y": 0.0}
    constraints = [
        LinearAtomicConstraint({"x": 1.0}, LinearRelation.GE, 0.8),
        LinearAtomicConstraint({"x": 1.0, "y": 1.0}, LinearRelation.GE, 1.5),
    ]

    updated = least_squares_update_labelling(
        frozenset({"x", "y"}), current, constraints
    )

    assert updated is not None
    assert all(constraint.satisfied_by(updated) for constraint in constraints)
    assert updated == pytest.approx({"x": 0.8, "y": 0.7}, abs=1e-9)
    assert _squared_distance(updated, current) <= 0.8**2 + 0.7**2 + 1e-10


def test_least_squares_update_single_halfspace_control() -> None:
    """Issue #39 control: projecting (0.6, 0.7) onto a + b <= 1 gives the
    orthogonal projection (0.45, 0.55)."""
    updated = least_squares_update_labelling(
        frozenset({"a", "b"}),
        {"a": 0.6, "b": 0.7},
        (LinearAtomicConstraint({"a": 1.0, "b": 1.0}, LinearRelation.LE, 1.0),),
    )

    assert updated == pytest.approx({"a": 0.45, "b": 0.55})


def test_least_squares_update_respects_unit_box_nearest_point() -> None:
    """Issue #39: the unit box bounds are part of the feasible set; from
    (0.9, 0.9) under a - b >= 0.5 the nearest point is (1.0, 0.5), not the
    unconstrained halfspace projection (1.15, 0.65)."""
    current = {"a": 0.9, "b": 0.9}

    updated = least_squares_update_labelling(
        frozenset({"a", "b"}),
        current,
        (LinearAtomicConstraint({"a": 1.0, "b": -1.0}, LinearRelation.GE, 0.5),),
    )

    assert updated == pytest.approx({"a": 1.0, "b": 0.5}, abs=1e-9)


@given(
    x0=st.integers(0, 10),
    y0=st.integers(0, 10),
    first=st.tuples(st.integers(-2, 2), st.integers(-2, 2), st.integers(-10, 10)),
    second=st.tuples(st.integers(-2, 2), st.integers(-2, 2), st.integers(-10, 10)),
)
@settings(max_examples=60, deadline=None)
def test_least_squares_update_is_no_farther_than_any_feasible_grid_point(
    x0: int,
    y0: int,
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> None:
    """Issue #39: no feasible point on a 0.05 grid of the unit box is nearer
    to the current labelling than the returned update (Def 10, p.24-25)."""
    current = {"x": x0 / 10, "y": y0 / 10}
    constraints = [
        LinearAtomicConstraint({"x": a, "y": b}, LinearRelation.GE, c / 10)
        for a, b, c in (first, second)
    ]

    updated = least_squares_update_labelling(
        frozenset({"x", "y"}), current, constraints
    )

    grid = [i / 20 for i in range(21)]
    feasible_grid = [
        {"x": x, "y": y}
        for x in grid
        for y in grid
        if all(constraint.satisfied_by({"x": x, "y": y}) for constraint in constraints)
    ]
    if updated is None:
        assert not feasible_grid
        return
    assert all(constraint.satisfied_by(updated) for constraint in constraints)
    best_grid = min(
        (_squared_distance(point, current) for point in feasible_grid),
        default=float("inf"),
    )
    assert _squared_distance(updated, current) <= best_grid + 1e-9
