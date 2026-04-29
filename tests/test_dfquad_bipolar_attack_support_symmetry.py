from __future__ import annotations

import pytest

from argumentation.dfquad import dfquad_bipolar_strengths
from argumentation.gradual import WeightedBipolarGraph


def test_bipolar_single_support_and_attack_are_symmetric_around_neutral() -> None:
    """Rago, Cyras, and Toni 2016, SAFA, p. 35, Defs. 1-3."""

    supported = WeightedBipolarGraph(
        arguments=frozenset({"source", "target"}),
        initial_weights={"source": 0.7, "target": 0.5},
        supports=frozenset({("source", "target")}),
    )
    attacked = WeightedBipolarGraph(
        arguments=frozenset({"source", "target"}),
        initial_weights={"source": 0.7, "target": 0.5},
        attacks=frozenset({("source", "target")}),
    )

    support_result = dfquad_bipolar_strengths(supported)
    attack_result = dfquad_bipolar_strengths(attacked)

    assert support_result.strengths["target"] - 0.5 == pytest.approx(
        0.5 - attack_result.strengths["target"]
    )
