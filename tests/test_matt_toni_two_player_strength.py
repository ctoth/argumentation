from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.matt_toni import matt_toni_strengths


def test_matt_toni_table_one_f8_strengths() -> None:
    """Matt and Toni 2008, JELIA, p. 291, Def. 6 and Table 1."""

    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d", "e", "f"}),
        defeats=frozenset(
            {
                ("a", "b"),
                ("b", "a"),
                ("b", "c"),
                ("c", "d"),
                ("e", "c"),
                ("f", "e"),
            }
        ),
    )

    strengths = matt_toni_strengths(framework)

    assert strengths == pytest.approx(
        {
            "a": 0.5,
            "b": 0.5,
            "c": 0.417,
            "d": 0.5,
            "e": 0.25,
            "f": 1.0,
        },
        abs=0.001,
    )
