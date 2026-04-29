from __future__ import annotations

import pytest

from argumentation.gradual import (
    WeightedBipolarGraph,
    quadratic_energy_strengths,
    quadratic_energy_strengths_continuous,
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
