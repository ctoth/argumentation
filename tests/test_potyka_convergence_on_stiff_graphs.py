from __future__ import annotations

from argumentation.gradual import (
    WeightedBipolarGraph,
    quadratic_energy_strengths_continuous,
    quadratic_energy_strengths_discrete,
)


def test_continuous_integrator_converges_when_short_discrete_run_has_not() -> None:
    """Potyka 2018, KR, p. 150, Def. 2 and convergence discussion."""

    graph = WeightedBipolarGraph(
        arguments=frozenset({"a", "b", "c", "d"}),
        initial_weights={"a": 0.95, "b": 0.05, "c": 0.9, "d": 0.1},
        supports=frozenset({("a", "c"), ("c", "a")}),
        attacks=frozenset({("b", "a"), ("c", "d"), ("d", "b")}),
    )

    discrete = quadratic_energy_strengths_discrete(
        graph,
        tolerance=1e-12,
        max_iterations=1,
    )
    continuous = quadratic_energy_strengths_continuous(
        graph,
        tolerance=1e-10,
        max_iterations=10_000,
    )

    assert not discrete.converged
    assert continuous.converged
    assert continuous.integration_method == "rk4_adaptive"
    assert all(0.0 <= strength <= 1.0 for strength in continuous.strengths.values())
