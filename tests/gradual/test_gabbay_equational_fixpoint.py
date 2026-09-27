from __future__ import annotations

import pytest

from argumentation.gradual.equational import EquationScheme, equational_fixpoint
from argumentation.gradual.gradual import WeightedBipolarGraph


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


@pytest.mark.parametrize("scheme", ["inverse", "max", "min"])
def test_empty_graph_has_empty_fixpoint(scheme: EquationScheme) -> None:
    """Gabbay 2012, Theorem 2.2: a finite equational network has a solution.

    With no nodes there are no equations, so the empty assignment is the
    (unique) solution and it is already a fixed point.
    """

    graph = WeightedBipolarGraph(arguments=frozenset(), initial_weights={})

    result = equational_fixpoint(graph, scheme=scheme)

    assert result.converged
    assert result.strengths == {}
    assert result.max_delta == 0.0


def test_single_unattacked_argument_is_fully_in() -> None:
    """Control: an unattacked node has the empty product, so ``f(a) = 1``."""

    graph = WeightedBipolarGraph(arguments=frozenset({"a"}), initial_weights={"a": 1.0})

    result = equational_fixpoint(graph)

    assert result.converged
    assert result.strengths == {"a": 1.0}
