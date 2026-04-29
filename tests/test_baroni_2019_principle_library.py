from __future__ import annotations

from argumentation.dfquad import dfquad_strengths
from argumentation.gradual import WeightedBipolarGraph
from argumentation.gradual_principles import (
    PRINCIPLE_COMPLIANCE,
    ComplianceLabel,
    principle_balance,
    principle_directionality,
    principle_monotonicity,
)


def test_baroni_principle_predicates_accept_gradual_strength_functions() -> None:
    """Baroni, Rago, and Toni 2019, IJAR 105, pp. 252-286, GPs 1-11."""

    graph = WeightedBipolarGraph(
        arguments=frozenset({"supporter", "attacker", "target", "isolated"}),
        initial_weights={
            "supporter": 0.8,
            "attacker": 0.3,
            "target": 0.5,
            "isolated": 0.4,
        },
        supports=frozenset({("supporter", "target")}),
        attacks=frozenset({("attacker", "target")}),
    )

    def strength_fn(candidate: WeightedBipolarGraph) -> dict[str, float]:
        return dfquad_strengths(candidate).strengths

    assert principle_balance(strength_fn, graph)
    assert principle_directionality(strength_fn, graph)
    assert principle_monotonicity(strength_fn, graph)
    assert PRINCIPLE_COMPLIANCE["dfquad"]["balance"] is ComplianceLabel.HOLDS
