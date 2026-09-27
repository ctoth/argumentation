from __future__ import annotations

import pytest

from argumentation.structured.aba.aba import ABAFramework, NotFlatABAError
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from argumentation.interop.iccma import (
    parse_aba,
    parse_apx,
    parse_tgf,
    write_aba,
    write_numeric_aba,
)


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_aba_iccma_round_trip_preserves_flat_framework() -> None:
    alpha = lit("alpha")
    beta = lit("beta")
    leave = lit("leave")
    stay = lit("stay")
    framework = ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset(
            {Rule((alpha,), leave, "strict"), Rule((beta,), stay, "strict")}
        ),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )

    assert parse_aba(write_aba(framework)) == framework


def test_write_aba_rejects_language_literals_it_cannot_represent() -> None:
    """Issue #21: the compact format has no vocabulary declaration line.

    Bondarenko 1997 (notes.md, p.69) makes the language L a component of the
    deductive system independent of the rules, so a literal may belong to L
    without occurring in any assumption, contrary, or rule.  The compact
    reader rebuilds L only from those lines, so the writer must refuse
    rather than silently drop the literal.
    """
    framework = ABAFramework(
        language=frozenset({lit("unused")}),
        rules=frozenset(),
        assumptions=frozenset(),
        contrary={},
    )

    with pytest.raises(ValueError, match="unused"):
        write_aba(framework)


def test_write_aba_round_trips_when_every_literal_occurs() -> None:
    """Control: the same literal round-trips once a rule mentions it."""
    unused = lit("unused")
    framework = ABAFramework(
        language=frozenset({unused}),
        rules=frozenset({Rule((), unused, "strict")}),
        assumptions=frozenset(),
        contrary={},
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
    assert framework.rules == frozenset(
        {
            Rule((lit("5"), lit("1")), lit("4"), "strict"),
            Rule((), lit("5"), "strict"),
            Rule((lit("2"), lit("3")), lit("6"), "strict"),
        }
    )


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


@pytest.mark.parametrize(
    "text",
    [
        "arg(a).\narg(b).\natt(a, b).\n",
        "arg( a ).\narg(b ).\natt( a ,b ).\n",
    ],
)
def test_parse_apx_ignores_whitespace_around_fact_terms(text: str) -> None:
    """Issue #23: APX facts are ASP facts (Egly 2010, notes.md: the AF is the
    database {arg(a)} and binary attack facts), and ASP allows whitespace
    between the terms of an atom, so ``att(a, b).`` names the argument b,
    not a new argument " b"."""
    framework = parse_apx(text)

    assert framework.arguments == frozenset({"a", "b"})
    assert framework.defeats == frozenset({("a", "b")})


def test_parse_apx_reads_compact_attack_fact_control() -> None:
    framework = parse_apx("arg(a).\narg(b).\natt(a,b).\n")

    assert framework.arguments == frozenset({"a", "b"})
    assert framework.defeats == frozenset({("a", "b")})


@pytest.mark.parametrize("line", ["arg( ).", "att( ,b).", "att(a, )."])
def test_parse_apx_rejects_blank_fact_terms(line: str) -> None:
    with pytest.raises(ValueError, match="invalid APX line 1"):
        parse_apx(line + "\n")


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


@pytest.mark.parametrize(
    ("text", "assumption", "line_number"),
    [
        (
            "p aba\na alpha\nc alpha not_alpha\nc alpha other\n",
            "alpha",
            4,
        ),
        (
            "p aba\na alpha\nc alpha not_alpha\nc alpha not_alpha\n",
            "alpha",
            4,
        ),
        (
            "p aba 3\na 1\nc 1 2\nc 1 3\n",
            "1",
            4,
        ),
        (
            "p aba 2\na 1\nc 1 2\nc 1 2\n",
            "1",
            4,
        ),
    ],
    ids=(
        "compact-different",
        "compact-identical",
        "numeric-different",
        "numeric-identical",
    ),
)
def test_parse_aba_rejects_duplicate_contrary_declarations(
    text: str,
    assumption: str,
    line_number: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=rf"duplicate contrary.*{assumption}.*line {line_number}",
    ):
        parse_aba(text)


@pytest.mark.parametrize(
    "text",
    [
        "p aba\na alpha\na beta\nc alpha contrary\nc beta contrary\n",
        "p aba 3\na 1\na 2\nc 1 3\nc 2 3\n",
    ],
    ids=("compact", "numeric"),
)
def test_parse_aba_allows_different_assumptions_to_share_a_contrary(
    text: str,
) -> None:
    framework = parse_aba(text)

    assert len(framework.contrary) == 2
    assert len(set(framework.contrary.values())) == 1


def test_aba_serializers_emit_one_contrary_per_assumption_and_round_trip() -> None:
    alpha = lit("1")
    beta = lit("2")
    contrary = lit("3")
    framework = ABAFramework(
        language=frozenset({alpha, beta, contrary}),
        rules=frozenset(),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: contrary, beta: contrary},
    )

    compact = write_aba(framework)
    numeric = write_numeric_aba(framework)

    assert sum(line.startswith("c ") for line in compact.splitlines()) == 2
    assert sum(line.startswith("c ") for line in numeric.splitlines()) == 2
    assert parse_aba(compact) == framework
    assert parse_aba(numeric) == framework


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
