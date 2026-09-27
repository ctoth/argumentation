from __future__ import annotations

import pytest

from argumentation.frameworks.adf import (
    AbstractDialecticalFramework,
    And,
    Atom,
    False_,
    Not,
    ThreeValued,
    True_,
    grounded_interpretation,
)
from argumentation.interop.iccma import parse_adf, write_adf


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


@pytest.mark.parametrize("reserved", ["true", "false", "not", "and", "or"])
def test_adf_iccma_writer_rejects_atoms_named_like_formula_keywords(
    reserved: str,
) -> None:
    """Issue #4: an atom spelled like a formula keyword has no ICCMA escape.

    Brewka 2013 (notes.md, p.1) represents each acceptance condition as a
    formula whose atoms are statements, distinct from the truth constants.
    The compact ``c`` line reads ``true``/``false`` as constants and
    ``not``/``and``/``or`` as connectives, so writing ``Atom("true")``
    verbatim reads back as ``True_()`` and flips the grounded value of b.
    """
    framework = AbstractDialecticalFramework(
        statements=frozenset({reserved, "b"}),
        links=frozenset({(reserved, "b")}),
        acceptance_conditions={reserved: False_(), "b": Atom(reserved)},
    )
    assert dict(grounded_interpretation(framework))["b"] == ThreeValued.F

    with pytest.raises(ValueError, match=f"atom {reserved!r}"):
        write_adf(framework)


def test_adf_iccma_round_trips_reserved_statement_used_only_as_constant() -> None:
    """Control: a statement named ``true`` is representable when no formula
    references it as an atom, and the round trip preserves grounded values."""
    framework = AbstractDialecticalFramework(
        statements=frozenset({"true", "b"}),
        links=frozenset(),
        acceptance_conditions={"true": False_(), "b": True_()},
    )

    restored = parse_adf(write_adf(framework))

    assert restored == framework
    assert dict(grounded_interpretation(restored)) == dict(
        grounded_interpretation(framework)
    )


def test_adf_iccma_rejects_missing_header() -> None:
    with pytest.raises(ValueError, match="p adf"):
        parse_adf("s a\n")
