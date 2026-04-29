from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.matt_toni import matt_toni_strengths


def test_unattacked_arguments_are_strongest_and_attacked_arguments_are_weaker() -> None:
    """Matt and Toni 2008, JELIA, p. 291, Table 1, frameworks F1-F3."""

    unattacked = ArgumentationFramework(arguments=frozenset({"a"}), defeats=frozenset())
    one_way_attack = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    mutual_attack = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    assert matt_toni_strengths(unattacked)["a"] == pytest.approx(1.0)
    assert matt_toni_strengths(one_way_attack) == pytest.approx({"a": 1.0, "b": 0.25})
    assert matt_toni_strengths(mutual_attack) == pytest.approx({"a": 0.5, "b": 0.5})
