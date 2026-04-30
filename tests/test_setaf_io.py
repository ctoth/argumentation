from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.setaf import SETAF
from argumentation.setaf_io import (
    parse_aspartix_setaf,
    parse_compact_setaf,
    write_aspartix_setaf,
    write_compact_setaf,
)


SMALL_ARGUMENTS = ("a", "b", "c", "d")


def _all_subsets(arguments: frozenset[str]) -> tuple[frozenset[str], ...]:
    ordered = sorted(arguments)
    return tuple(
        frozenset(argument for index, argument in enumerate(ordered) if mask & (1 << index))
        for mask in range(1 << len(ordered))
    )


@st.composite
def setafs(draw: st.DrawFn) -> SETAF:
    arguments = frozenset(draw(st.sets(st.sampled_from(SMALL_ARGUMENTS), min_size=1)))
    possible_attacks = [
        (tail, target)
        for tail in _all_subsets(arguments)
        if tail
        for target in sorted(arguments)
    ]
    attacks = frozenset(
        draw(st.sets(st.sampled_from(possible_attacks), min_size=1, max_size=6))
    )
    return SETAF(arguments=arguments, attacks=attacks)


def test_parse_aspartix_setaf_official_fixture() -> None:
    text = """
    arg(a).
    arg(b).
    arg(c).
    att(r1,c).
    mem(r1,a).
    mem(r1,b).
    """

    assert parse_aspartix_setaf(text) == SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )


@given(setafs())
@settings(max_examples=100)
def test_aspartix_round_trip_preserves_setaf_relation(framework: SETAF) -> None:
    assert parse_aspartix_setaf(write_aspartix_setaf(framework)) == framework


@given(setafs())
@settings(max_examples=100)
def test_aspartix_writer_uses_only_official_fact_types(framework: SETAF) -> None:
    text = write_aspartix_setaf(framework)

    assert "p setaf" not in text
    for line in text.splitlines():
        assert line.startswith(("arg(", "att(", "mem("))
        assert line.endswith(").")


def test_parse_aspartix_setaf_rejects_compact_header() -> None:
    with pytest.raises(ValueError, match="invalid ASPARTIX SETAF line"):
        parse_aspartix_setaf("p setaf\narg a\n")


def test_parse_aspartix_setaf_rejects_missing_fact_dot() -> None:
    with pytest.raises(ValueError, match="invalid ASPARTIX SETAF line"):
        parse_aspartix_setaf("arg(a)\n")


def test_parse_aspartix_setaf_rejects_member_without_attack_target() -> None:
    with pytest.raises(ValueError, match="unknown attack"):
        parse_aspartix_setaf("arg(a).\nmem(r1,a).\n")


def test_parse_aspartix_setaf_rejects_attack_with_empty_support() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        parse_aspartix_setaf("arg(a).\natt(r1,a).\n")


def test_compact_setaf_format_is_package_local() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )
    text = write_compact_setaf(framework)

    assert text.startswith("p setaf\n")
    assert parse_compact_setaf(text) == framework
