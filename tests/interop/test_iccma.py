from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.interop.iccma import parse_aba, parse_af, write_af
from argumentation.structured.aspic.aspic import GroundAtom, Literal


def test_parse_af_reads_iccma_2023_numeric_format() -> None:
    framework = parse_af(
        """
        # comments are ignored
        p af 5
        1 2
        2 4
        4 5
        5 4
        5 5
        """
    )

    assert framework == ArgumentationFramework(
        arguments=frozenset({"1", "2", "3", "4", "5"}),
        defeats=frozenset(
            {
                ("1", "2"),
                ("2", "4"),
                ("4", "5"),
                ("5", "4"),
                ("5", "5"),
            }
        ),
    )


@st.composite
def numeric_afs(draw: st.DrawFn) -> ArgumentationFramework:
    size = draw(st.integers(min_value=0, max_value=5))
    arguments = frozenset(str(index) for index in range(1, size + 1))
    possible_attacks = [
        (attacker, target)
        for attacker in sorted(arguments, key=int)
        for target in sorted(arguments, key=int)
    ]
    attack_strategy = (
        st.just(set())
        if not possible_attacks
        else st.sets(st.sampled_from(possible_attacks), max_size=10)
    )
    return ArgumentationFramework(
        arguments=arguments, defeats=frozenset(draw(attack_strategy))
    )


def test_write_af_emits_deterministic_iccma_format() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2", "3"}),
        defeats=frozenset({("2", "3"), ("1", "2")}),
    )

    assert write_af(framework) == "p af 3\n1 2\n2 3\n"


def test_parse_then_write_round_trip() -> None:
    text = "p af 3\n1 2\n2 3\n"

    assert write_af(parse_af(text)) == text


@given(numeric_afs())
@settings(max_examples=100)
def test_iccma_numeric_af_round_trip_preserves_contiguous_ids(
    framework: ArgumentationFramework,
) -> None:
    assert parse_af(write_af(framework)) == framework


def test_parse_af_allows_comments_only_around_official_lines() -> None:
    framework = parse_af("# first\np af 2\n# attack follows\n1 2\n")

    assert framework == ArgumentationFramework(
        arguments=frozenset({"1", "2"}),
        defeats=frozenset({("1", "2")}),
    )


def test_parse_af_rejects_non_numeric_or_out_of_range_attacks() -> None:
    with pytest.raises(ValueError, match="p af"):
        parse_af("1 2\n")
    with pytest.raises(ValueError, match="attack"):
        parse_af("p af 1\n1 2\n")
    with pytest.raises(ValueError, match="numeric"):
        parse_af("p af 2\na b\n")


def test_write_af_rejects_non_iccma_argument_ids() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a"}),
        defeats=frozenset(),
    )

    with pytest.raises(ValueError, match="numeric"):
        write_af(framework)


@pytest.mark.parametrize("noncanonical", ["01", "١"])
def test_write_af_rejects_noncanonical_numeric_ids(noncanonical: str) -> None:
    """Issue #24: ``p af n`` names arguments by the decimal ids 1..n and the
    reader constructs exactly those spellings, so an argument spelled "01"
    (or with a non-ASCII digit) cannot round-trip and must be rejected."""
    framework = ArgumentationFramework(
        arguments=frozenset({noncanonical, "2"}),
        defeats=frozenset({(noncanonical, "2")}),
    )

    with pytest.raises(ValueError, match="canonical"):
        write_af(framework)


def test_write_af_accepts_canonical_neighbour_of_noncanonical_id() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2"}),
        defeats=frozenset({("1", "2")}),
    )

    assert parse_af(write_af(framework)) == framework


def test_parse_af_rejects_noncanonical_attack_ids() -> None:
    with pytest.raises(ValueError, match="canonical"):
        parse_af("p af 2\n01 2\n")


def test_parse_numeric_aba_rejects_noncanonical_atom_ids() -> None:
    """Issue #24: the numeric ABA reader validated int("01") and then looked
    up the raw "01", raising KeyError instead of a format error."""
    with pytest.raises(ValueError, match="canonical"):
        parse_aba("p aba 2\na 01\nc 1 2\n")


def test_parse_numeric_aba_accepts_canonical_atom_ids_control() -> None:
    framework = parse_aba("p aba 2\na 1\nc 1 2\n")

    assert framework.contrary == {
        Literal(GroundAtom("1")): Literal(GroundAtom("2")),
    }


def test_write_af_rejects_non_contiguous_numeric_ids() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "3"}),
        defeats=frozenset(),
    )

    with pytest.raises(ValueError, match="1..n"):
        write_af(framework)
