"""Unit tests for the shared fixed-point driver."""

from __future__ import annotations

import pytest

from argumentation.core.fixpoint import FixpointOutcome, iterate_fixpoint


def test_immediate_convergence_reports_iteration_one() -> None:
    # An identity update never changes the scores, so the first delta is 0.0.
    outcome = iterate_fixpoint(
        {"a": 0.5, "b": 1.0},
        lambda scores: dict(scores),
        tolerance=1e-9,
        max_iterations=100,
    )
    assert isinstance(outcome, FixpointOutcome)
    assert outcome.converged is True
    assert outcome.iterations == 1
    assert outcome.last_delta == 0.0
    assert outcome.scores == {"a": 0.5, "b": 1.0}


def test_converges_after_several_iterations() -> None:
    # Each step halves the distance to 0; with tolerance 0.1 it should take a
    # predictable number of 1-based iterations to cross the threshold.
    def update(scores: dict[str, float]) -> dict[str, float]:
        return {key: value / 2.0 for key, value in scores.items()}

    outcome = iterate_fixpoint(
        {"a": 1.0},
        update,
        tolerance=0.1,
        max_iterations=100,
    )
    # Deltas: 0.5, 0.25, 0.125, 0.0625 (<= 0.1) -> converges on iteration 4.
    assert outcome.converged is True
    assert outcome.iterations == 4
    assert outcome.last_delta == pytest.approx(0.0625)
    assert outcome.scores["a"] == pytest.approx(0.0625)


def test_never_converges_hits_max_iterations() -> None:
    # A constant +1 shift keeps delta at 1.0 forever, so the loop exhausts.
    outcome = iterate_fixpoint(
        {"a": 0.0},
        lambda scores: {key: value + 1.0 for key, value in scores.items()},
        tolerance=1e-9,
        max_iterations=5,
    )
    assert outcome.converged is False
    assert outcome.iterations == 5
    assert outcome.last_delta == pytest.approx(1.0)
    assert outcome.scores["a"] == pytest.approx(5.0)


def test_delta_is_max_absolute_change_over_keys() -> None:
    # One key jumps by 0.4 and another by 0.1; the reported delta is the max,
    # and convergence is decided against that maximum.
    seen: list[float] = []

    def update(scores: dict[str, float]) -> dict[str, float]:
        if not seen:
            seen.append(1.0)
            return {"a": scores["a"] + 0.4, "b": scores["b"] + 0.1}
        return dict(scores)

    outcome = iterate_fixpoint(
        {"a": 0.0, "b": 0.0},
        update,
        tolerance=0.2,
        max_iterations=10,
    )
    # First iteration delta is max(0.4, 0.1) = 0.4 > 0.2, so it does not stop;
    # second iteration is the identity, delta 0.0 -> converged on iteration 2.
    assert outcome.converged is True
    assert outcome.iterations == 2
    assert outcome.last_delta == 0.0


def test_empty_scores_converge_immediately() -> None:
    # With no keys the delta defaults to 0.0, matching the ranking/discrete
    # loops that pass ``default=0.0`` for empty frameworks.
    outcome = iterate_fixpoint(
        {},
        lambda scores: dict(scores),
        tolerance=1e-9,
        max_iterations=10,
    )
    assert outcome.converged is True
    assert outcome.iterations == 1
    assert outcome.last_delta == 0.0
    assert outcome.scores == {}
