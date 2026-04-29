from __future__ import annotations

import pytest

from argumentation.equational import equational_fixpoint
from argumentation.gradual import WeightedBipolarGraph


def test_eq_inverse_and_eq_max_on_simple_attack_chain() -> None:
    """Gabbay 2012, Argument & Computation, pp. 104-108, Eq-inverse/Eq-max."""

    graph = WeightedBipolarGraph(
        arguments=frozenset({"a", "b", "c"}),
        initial_weights={"a": 1.0, "b": 1.0, "c": 1.0},
        attacks=frozenset({("a", "b"), ("b", "c")}),
    )

    inverse = equational_fixpoint(graph, scheme="inverse")
    maximum = equational_fixpoint(graph, scheme="max")

    assert inverse.converged
    assert maximum.converged
    assert inverse.strengths == pytest.approx({"a": 1.0, "b": 0.0, "c": 1.0})
    assert maximum.strengths == pytest.approx({"a": 1.0, "b": 0.0, "c": 1.0})
