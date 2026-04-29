from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework, complete_extensions
from argumentation.equational import equational_fixpoint
from argumentation.gradual import WeightedBipolarGraph


def test_eq_min_crisp_attack_chain_recovers_complete_extension_acceptance() -> None:
    """Gabbay 2012, Argument & Computation, pp. 104-108, Dung relation."""

    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    graph = WeightedBipolarGraph(
        arguments=framework.arguments,
        initial_weights={"a": 1.0, "b": 1.0},
        attacks=framework.defeats,
    )

    result = equational_fixpoint(graph, scheme="min")

    assert result.converged
    assert complete_extensions(framework) == [frozenset({"a"})]
    assert result.strengths == pytest.approx({"a": 1.0, "b": 0.0})
