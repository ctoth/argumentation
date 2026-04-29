from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from argumentation.dfquad import dfquad_strengths
from argumentation.gradual import WeightedBipolarGraph
from argumentation.gradual_principles import (
    PRINCIPLE_COMPLIANCE,
    ComplianceLabel,
    principle_balance,
    principle_directionality,
    principle_monotonicity,
)


@given(
    target_base=st.floats(min_value=0.05, max_value=0.95, allow_nan=False, allow_infinity=False),
    supporter_strength=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    attacker_strength=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_dfquad_satisfies_baroni_balance_directionality_and_monotonicity(
    target_base: float,
    supporter_strength: float,
    attacker_strength: float,
) -> None:
    """Baroni, Rago, and Toni 2019, IJAR 105, pp. 258-259, GPs 1-11."""

    graph = WeightedBipolarGraph(
        arguments=frozenset({"supporter", "attacker", "target", "isolated"}),
        initial_weights={
            "supporter": supporter_strength,
            "attacker": attacker_strength,
            "target": target_base,
            "isolated": 0.37,
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
    assert PRINCIPLE_COMPLIANCE["dfquad"]["directionality"] is ComplianceLabel.HOLDS
    assert PRINCIPLE_COMPLIANCE["dfquad"]["monotonicity"] is ComplianceLabel.HOLDS
