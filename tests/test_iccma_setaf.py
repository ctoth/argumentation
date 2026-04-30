from __future__ import annotations

from argumentation.iccma_setaf import parse_setaf, write_setaf
from argumentation.setaf import SETAF


def test_setaf_iccma_round_trip_preserves_collective_attacks() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )

    assert parse_setaf(write_setaf(framework)) == framework


def test_parse_setaf_rejects_missing_header() -> None:
    try:
        parse_setaf("arg a\n")
    except ValueError as exc:
        assert "header" in str(exc)
    else:
        raise AssertionError("parse_setaf accepted input without a header")
