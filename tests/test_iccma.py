from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.iccma import parse_af, write_af


def test_parse_af_reads_iccma_2025_numeric_format() -> None:
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
        defeats=frozenset({
            ("1", "2"),
            ("2", "4"),
            ("4", "5"),
            ("5", "4"),
            ("5", "5"),
        }),
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
