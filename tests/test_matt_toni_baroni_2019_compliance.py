from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from argumentation.dung import ArgumentationFramework
from argumentation.gradual_principles import PRINCIPLE_COMPLIANCE, ComplianceLabel
from argumentation.matt_toni import matt_toni_strengths


@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_matt_toni_declares_conditional_baroni_principle_compliance(
    _unused_weight: float,
) -> None:
    """Matt-Toni 2008, JELIA, p. 291; Baroni-Rago-Toni 2019, IJAR 105, pp. 258-259."""

    one_way_attack = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    mutual_attack = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    assert matt_toni_strengths(one_way_attack) == pytest.approx({"a": 1.0, "b": 0.25})
    assert matt_toni_strengths(mutual_attack) == pytest.approx({"a": 0.5, "b": 0.5})
    assert PRINCIPLE_COMPLIANCE["matt_toni"]["directionality"] is ComplianceLabel.HOLDS
    assert PRINCIPLE_COMPLIANCE["matt_toni"]["balance"] is ComplianceLabel.CONDITIONAL
    assert PRINCIPLE_COMPLIANCE["matt_toni"]["monotonicity"] is ComplianceLabel.CONDITIONAL
