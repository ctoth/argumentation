from __future__ import annotations

import pytest

from argumentation.aba import ABAFramework, NotFlatABAError
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.iccma import parse_aba, parse_apx, parse_tgf, write_aba, write_numeric_aba


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


def test_parse_official_iccma_2025_numeric_aba_example() -> None:
    framework = parse_aba(
        """
        p aba 8
        # this is a comment
        a 1
        a 2
        a 3
        c 1 6
        c 2 7
        c 3 8
        r 4 5 1
        r 5
        r 6 2 3
        """
    )

    assert framework.language == frozenset(lit(str(index)) for index in range(1, 9))
    assert framework.assumptions == frozenset({lit("1"), lit("2"), lit("3")})
    assert framework.contrary == {
        lit("1"): lit("6"),
        lit("2"): lit("7"),
        lit("3"): lit("8"),
    }
    assert framework.rules == frozenset({
        Rule((lit("5"), lit("1")), lit("4"), "strict"),
        Rule((), lit("5"), "strict"),
        Rule((lit("2"), lit("3")), lit("6"), "strict"),
    })


def test_write_numeric_aba_emits_official_iccma_2025_header() -> None:
    alpha = lit("1")
    beta = lit("2")
    leave = lit("3")
    stay = lit("4")
    framework = ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset({Rule((alpha,), leave, "strict"), Rule((), stay, "strict")}),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )

    text = write_numeric_aba(framework)

    assert text.startswith("p aba 4\n")
    assert parse_aba(text) == framework


def test_parse_apx_reads_aspartix_argumentation_framework() -> None:
    framework = parse_apx(
        """
        arg(a1).
        arg(a2).
        att(a1,a2).
        att(a2,a1).
        """
    )

    assert framework.arguments == frozenset({"a1", "a2"})
    assert framework.defeats == frozenset({("a1", "a2"), ("a2", "a1")})


def test_parse_tgf_reads_trivial_graph_format_framework() -> None:
    framework = parse_tgf(
        """
        1 first argument
        2 second argument
        #
        1 2
        2 1
        """
    )

    assert framework.arguments == frozenset({"1", "2"})
    assert framework.defeats == frozenset({("1", "2"), ("2", "1")})


def test_parse_official_numeric_aba_rejects_out_of_range_atom() -> None:
    with pytest.raises(ValueError, match="outside 1..2"):
        parse_aba("p aba 2\na 3\n")


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
