from __future__ import annotations

import pytest

from argumentation.dfquad import dfquad_bipolar_strengths
from argumentation.gradual import WeightedBipolarGraph


@pytest.mark.parametrize("pairs", [1, 5, 20, 100])
@pytest.mark.parametrize("base", [0.1, 0.5, 0.9])
def test_equal_attack_support_pairs_leave_neutral_base_fixed(
    pairs: int,
    base: float,
) -> None:
    """Rago, Cyras, and Toni 2016, SAFA, pp. 35-36, Defs. 2-3."""

    supporters = {f"s{i}" for i in range(pairs)}
    attackers = {f"a{i}" for i in range(pairs)}
    arguments = supporters | attackers | {"target"}
    graph = WeightedBipolarGraph(
        arguments=frozenset(arguments),
        initial_weights={
            **{argument: 0.5 for argument in supporters | attackers},
            "target": base,
        },
        supports=frozenset((argument, "target") for argument in supporters),
        attacks=frozenset((argument, "target") for argument in attackers),
    )

    result = dfquad_bipolar_strengths(graph, base_score=base)

    assert result.converged
    assert result.strengths["target"] == pytest.approx(base)
