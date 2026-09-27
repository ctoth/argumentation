from __future__ import annotations

import math

import pytest

import argumentation.gradual.gradual as gradual_module
from argumentation.gradual.gradual import (
    WeightedBipolarGraph,
    _quadratic_derivative,
    quadratic_energy_strengths,
    quadratic_energy_strengths_continuous,
)


@pytest.fixture
def bounded_rk4(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail instead of hanging if the adaptive loop never exits."""
    original = gradual_module._rk4_step
    calls = 0

    def bounded(*args: object) -> dict[str, float]:
        nonlocal calls
        calls += 1
        assert calls <= 30, "adaptive RK4 loop exceeded 30 calls"
        return original(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(gradual_module, "_rk4_step", bounded)


@pytest.mark.usefixtures("bounded_rk4")
@pytest.mark.parametrize(
    ("initial_step", "tolerance"),
    [(math.nan, 1e-9), (math.inf, 1e-9), (0.25, math.nan)],
)
def test_continuous_rejects_non_finite_controls(
    initial_step: float, tolerance: float
) -> None:
    """Potyka 2018, KR, p. 150: RK4 integrates with a real step size; NaN or
    infinite controls cannot drive the step-halving loop to termination."""

    with pytest.raises(ValueError):
        quadratic_energy_strengths_continuous(
            _single_attack_graph(),
            initial_step=initial_step,
            tolerance=tolerance,
            max_iterations=1,
        )


@pytest.mark.usefixtures("bounded_rk4")
def test_continuous_accepts_finite_controls() -> None:
    """Control: a finite positive step with one iteration returns a result."""

    result = quadratic_energy_strengths_continuous(
        _single_attack_graph(), initial_step=0.5, max_iterations=1
    )

    assert result.iterations == 1


def _single_attack_graph() -> WeightedBipolarGraph:
    return WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 1.0, "b": 0.5},
        attacks=frozenset({("a", "b")}),
    )


def _residual(graph: WeightedBipolarGraph, strengths: dict[str, float]) -> float:
    return max(abs(value) for value in _quadratic_derivative(graph, strengths).values())


def test_exhausted_budget_reports_residual_of_returned_state() -> None:
    """Potyka 2018, KR, p. 150, Def. 2: the residual is ``|d sigma / dt|``.

    ``max_delta`` must describe the returned strengths, not the state before
    the final RK4 update.
    """

    graph = _single_attack_graph()

    result = quadratic_energy_strengths_continuous(graph, max_iterations=1)

    assert not result.converged
    assert result.max_delta == pytest.approx(
        _residual(graph, result.strengths), abs=1e-12
    )


def test_exhausted_budget_converges_when_final_state_is_within_tolerance() -> None:
    """Def. 2 residual at the returned state (0.2349) is below 0.24 after one
    step even though the initial state's residual (0.25) was not."""

    graph = _single_attack_graph()

    result = quadratic_energy_strengths_continuous(
        graph, tolerance=0.24, max_iterations=1
    )

    assert result.converged
    assert result.max_delta == pytest.approx(
        _residual(graph, result.strengths), abs=1e-12
    )


def test_converged_result_reports_residual_of_returned_state() -> None:
    """Control: the converged path already measures the returned state."""

    graph = _single_attack_graph()

    result = quadratic_energy_strengths_continuous(graph)

    assert result.converged
    assert result.max_delta == pytest.approx(
        _residual(graph, result.strengths), abs=1e-12
    )


def test_continuous_quadratic_energy_matches_fixed_point_on_acyclic_graph() -> None:
    """Potyka 2018, KR, p. 150, Def. 2."""

    graph = WeightedBipolarGraph(
        arguments=frozenset({"a", "b", "c"}),
        initial_weights={"a": 0.5, "b": 0.4, "c": 0.5},
        supports=frozenset({("a", "c")}),
        attacks=frozenset({("b", "c")}),
    )

    continuous = quadratic_energy_strengths_continuous(graph, tolerance=1e-12)
    default = quadratic_energy_strengths(graph, tolerance=1e-12)

    assert continuous.converged
    assert continuous.integration_method == "rk4_adaptive"
    assert default.integration_method == "rk4_adaptive"
    assert continuous.strengths == pytest.approx(default.strengths, abs=1e-9)
