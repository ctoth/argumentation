"""Regression tests for BUG-4: silent non-convergence in epistemic projection.

``_project_labelling`` runs a fixed Kaczmarz-style iteration loop.  Before the
fix, when the maximum constraint violation never dropped below tolerance within
the iteration cap, it silently ``break``ed and returned the last (still
infeasible) point with no flag or exception, and ``least_squares_update_labelling``
rounded and returned it as if it were a valid labelling.  These tests pin the
fail-loud behavior: non-convergence must raise ``EpistemicProjectionError``.
"""

from __future__ import annotations

import pytest

from argumentation.probabilistic.epistemic import (
    EpistemicProjectionError,
    LinearAtomicConstraint,
    LinearRelation,
    _constraint_violation,
    _project_labelling,
    least_squares_update_labelling,
)


# An over-constrained system: a >= 0.8, b >= 0.8, a + b <= 1.  The two GE
# half-spaces and the LE half-space have no common feasible point inside the
# unit box, so the alternating Kaczmarz projections oscillate forever and the
# maximum violation never drops below tolerance, even at the full iteration cap.
_OSCILLATING_CONSTRAINTS = (
    LinearAtomicConstraint({"a": 1.0}, LinearRelation.GE, 0.8),
    LinearAtomicConstraint({"a": 1.0, "b": 1.0}, LinearRelation.LE, 1.0),
    LinearAtomicConstraint({"b": 1.0}, LinearRelation.GE, 0.8),
)


def test_project_labelling_raises_when_it_cannot_converge() -> None:
    with pytest.raises(EpistemicProjectionError) as excinfo:
        _project_labelling({"a": 0.0, "b": 0.0}, list(_OSCILLATING_CONSTRAINTS))

    # The exception must carry the achieved violation and iteration count so the
    # failure is diagnosable rather than silent.
    assert excinfo.value.violation > 1e-10
    assert excinfo.value.iterations >= 1


def test_project_labelling_raises_when_cap_is_too_small_for_a_feasible_system() -> None:
    # A feasible system that simply needs more than one iteration to satisfy.
    constraints = [
        LinearAtomicConstraint({"a": 1.0}, LinearRelation.GE, 0.6),
        LinearAtomicConstraint({"a": 1.0, "b": 1.0}, LinearRelation.LE, 1.0),
        LinearAtomicConstraint({"b": 1.0}, LinearRelation.GE, 0.6),
    ]

    with pytest.raises(EpistemicProjectionError):
        _project_labelling({"a": 0.0, "b": 0.0}, constraints, max_iterations=1)


def test_non_converged_point_was_actually_infeasible_documents_the_bug() -> None:
    # Reproduce the OLD silent path by running the same projection logic without
    # the convergence guard, and show the returned point violated a constraint
    # well beyond tolerance -- i.e. silently returning it was a real wrong answer.
    point = {"a": 0.0, "b": 0.0}
    for _ in range(10_000):
        max_violation = 0.0
        for constraint in _OSCILLATING_CONSTRAINTS:
            violation = _constraint_violation(point, constraint)
            max_violation = max(max_violation, abs(violation))
            if abs(violation) <= 1e-12:
                continue
            norm = sum(c * c for c in constraint.coefficients.values())
            if norm == 0.0:
                continue
            for argument, coefficient in constraint.coefficients.items():
                point[argument] = point[argument] - (violation / norm) * coefficient
        if max_violation <= 1e-10:
            break

    worst = max(
        abs(_constraint_violation(point, c)) for c in _OSCILLATING_CONSTRAINTS
    )
    assert worst > 1e-10  # the silently-returned point did NOT satisfy the system


def test_feasible_update_still_returns_correct_labelling_without_raising() -> None:
    # Negative control: a normal, feasible update must still succeed silently.
    updated = least_squares_update_labelling(
        frozenset({"a", "b"}),
        {"a": 0.6, "b": 0.7},
        (LinearAtomicConstraint({"a": 1.0, "b": 1.0}, LinearRelation.LE, 1.0),),
    )

    assert updated is not None
    assert updated["a"] == pytest.approx(0.45)
    assert updated["b"] == pytest.approx(0.55)
