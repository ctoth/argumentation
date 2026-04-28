from __future__ import annotations

import pytest

from argumentation.aba import ABAFramework, NotFlatABAError
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.iccma import parse_aba, write_aba


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_aba_iccma_round_trip_preserves_flat_framework() -> None:
    alpha = lit("alpha")
    beta = lit("beta")
    leave = lit("leave")
    stay = lit("stay")
    framework = ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset({Rule((alpha,), leave, "strict"), Rule((beta,), stay, "strict")}),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )

    assert parse_aba(write_aba(framework)) == framework


def test_aba_iccma_rejects_non_flat_input() -> None:
    text = """p aba
a alpha
a beta
c alpha beta
c beta alpha
r beta alpha
"""

    with pytest.raises(NotFlatABAError):
        parse_aba(text)


def test_aba_iccma_rejects_missing_header() -> None:
    with pytest.raises(ValueError, match="p aba"):
        parse_aba("a alpha\n")
