from __future__ import annotations

import pytest

from argumentation.gradual import (
    WeightedBipolarGraph,
    quadratic_energy_strengths,
)


def test_quadratic_energy_keeps_isolated_argument_at_initial_weight() -> None:
    graph = WeightedBipolarGraph(
        arguments=frozenset({"a"}),
        initial_weights={"a": 0.37},
    )

    result = quadratic_energy_strengths(graph)

    assert result.converged
    assert result.strengths == pytest.approx({"a": 0.37})


def test_quadratic_energy_single_support_and_attack_match_equilibrium_formula() -> None:
    supported = WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 0.5, "b": 0.5},
        supports=frozenset({("a", "b")}),
    )
    attacked = WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 0.5, "b": 0.5},
        attacks=frozenset({("a", "b")}),
    )

    support_result = quadratic_energy_strengths(supported)
    attack_result = quadratic_energy_strengths(attacked)

    assert support_result.converged
    assert attack_result.converged
    assert support_result.strengths["a"] == pytest.approx(0.5)
    assert support_result.strengths["b"] == pytest.approx(0.6)
    assert attack_result.strengths["a"] == pytest.approx(0.5)
    assert attack_result.strengths["b"] == pytest.approx(0.4)


def test_quadratic_energy_is_monotone_for_direct_supporters_and_attackers() -> None:
    weak_supporter = WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 0.3, "b": 0.5},
        supports=frozenset({("a", "b")}),
    )
    strong_supporter = WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 0.8, "b": 0.5},
        supports=frozenset({("a", "b")}),
    )
    weak_attacker = WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 0.3, "b": 0.5},
        attacks=frozenset({("a", "b")}),
    )
    strong_attacker = WeightedBipolarGraph(
        arguments=frozenset({"a", "b"}),
        initial_weights={"a": 0.8, "b": 0.5},
        attacks=frozenset({("a", "b")}),
    )

    assert (
        quadratic_energy_strengths(strong_supporter).strengths["b"]
        > quadratic_energy_strengths(weak_supporter).strengths["b"]
    )
    assert (
        quadratic_energy_strengths(strong_attacker).strengths["b"]
        < quadratic_energy_strengths(weak_attacker).strengths["b"]
    )


def test_weighted_bipolar_graph_rejects_overlapping_edges() -> None:
    with pytest.raises(ValueError, match="overlap"):
        WeightedBipolarGraph(
            arguments=frozenset({"a", "b"}),
            initial_weights={"a": 0.5, "b": 0.5},
            attacks=frozenset({("a", "b")}),
            supports=frozenset({("a", "b")}),
        )
