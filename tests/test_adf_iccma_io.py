from __future__ import annotations

import pytest

from argumentation.adf import (
    AbstractDialecticalFramework,
    And,
    Atom,
    Not,
    True_,
)
from argumentation.iccma import parse_adf, write_adf


def test_adf_iccma_round_trip_preserves_ast_shape() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b", "c"}),
        links=frozenset({("a", "c"), ("b", "c")}),
        acceptance_conditions={
            "a": True_(),
            "b": True_(),
            "c": And((Atom("a"), Not(Atom("b")))),
        },
    )

    assert parse_adf(write_adf(framework)) == framework


def test_adf_iccma_rejects_missing_header() -> None:
    with pytest.raises(ValueError, match="p adf"):
        parse_adf("s a\n")
