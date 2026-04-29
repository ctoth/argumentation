from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from argumentation.dfquad import dfquad_strengths
from argumentation.gradual import WeightedBipolarGraph


@given(
    base=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    influence=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
)
def test_dfquad_equal_attack_and_support_is_continuous_at_zero(
    base: float,
    influence: float,
) -> None:
    """Rago et al. 2016, KR, pp. 65-66, Defs. 1-3 and Lemma 3."""

    graph = WeightedBipolarGraph(
        arguments=frozenset({"supporter", "attacker", "target"}),
        initial_weights={
            "supporter": influence,
            "attacker": influence,
            "target": base,
        },
        supports=frozenset({("supporter", "target")}),
        attacks=frozenset({("attacker", "target")}),
    )

    result = dfquad_strengths(graph, base_scores={"target": base})

    assert result.converged
    assert result.strengths["target"] == pytest.approx(base)
