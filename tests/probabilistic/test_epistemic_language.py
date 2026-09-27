from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.probabilistic.epistemic import (
    ArgumentTerm,
    AtomFormula,
    EpistemicAtom,
    OperationalFormula,
    ProbabilityFunction,
    ProbabilityTerm,
    evaluate_epistemic_formula,
    parse_epistemic_formula,
    parse_term,
    term_probability,
    write_epistemic_formula,
    write_term,
)


def test_hunter_definition_3_1_term_round_trip_for_boolean_combinations() -> None:
    term = parse_term("(a & !b) | c")

    assert write_term(term) == "((a & !b) | c)"
    assert write_term(parse_term(write_term(term))) == write_term(term)


def test_hunter_definition_3_2_term_probability_sums_satisfying_worlds() -> None:
    distribution = ProbabilityFunction(
        arguments=frozenset({"a", "b"}),
        probabilities={
            frozenset(): 0.1,
            frozenset({"a"}): 0.2,
            frozenset({"b"}): 0.3,
            frozenset({"a", "b"}): 0.4,
        },
    )

    assert term_probability(parse_term("a"), distribution) == pytest.approx(0.6)
    assert term_probability(parse_term("a & b"), distribution) == pytest.approx(0.4)
    assert term_probability(parse_term("!a"), distribution) == pytest.approx(0.4)


def test_hunter_example_4_epistemic_formula_evaluation() -> None:
    distribution = ProbabilityFunction(
        arguments=frozenset({"a", "b", "c", "d"}),
        probabilities={
            frozenset(): 0.0,
            frozenset({"a"}): 0.0,
            frozenset({"b"}): 0.0,
            frozenset({"c"}): 0.1,
            frozenset({"d"}): 0.1,
            frozenset({"a", "b"}): 0.7,
            frozenset({"a", "c"}): 0.0,
            frozenset({"a", "d"}): 0.0,
            frozenset({"b", "c"}): 0.0,
            frozenset({"b", "d"}): 0.0,
            frozenset({"c", "d"}): 0.0,
            frozenset({"a", "b", "c"}): 0.0,
            frozenset({"a", "b", "d"}): 0.0,
            frozenset({"a", "c", "d"}): 0.0,
            frozenset({"b", "c", "d"}): 0.0,
            frozenset({"a", "b", "c", "d"}): 0.1,
        },
    )

    formula = parse_epistemic_formula("p(a & b) - p(c) - p(d) > 0")

    assert evaluate_epistemic_formula(formula, distribution) is True
    assert write_epistemic_formula(
        parse_epistemic_formula(write_epistemic_formula(formula))
    ) == (write_epistemic_formula(formula))


def test_hunter_definition_3_1_rejects_atom_thresholds_outside_unit_interval() -> None:
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        EpistemicAtom(
            OperationalFormula((ProbabilityTerm(parse_term("a")),), ()),
            ">",
            1.1,
        )


@pytest.mark.parametrize("suffix", [" ", "\n", " \t\r\n"])
def test_parsers_accept_trailing_whitespace(suffix: str) -> None:
    """Issue #13: whitespace separates tokens wherever it appears.

    The Hunter, Polberg, and Thimm term and formula grammar (Definition 3.1)
    is whitespace-insensitive; trailing whitespace must parse like leading
    whitespace does.
    """
    assert parse_term("a" + suffix) == ArgumentTerm("a")
    assert parse_epistemic_formula(
        "p(a) >= 0.5" + suffix
    ) == parse_epistemic_formula("p(a) >= 0.5")
    # Control: leading whitespace already parses.
    assert parse_term(suffix + "a") == ArgumentTerm("a")


def _threshold_atom(operator: str, threshold: float) -> AtomFormula:
    return AtomFormula(
        EpistemicAtom(
            OperationalFormula((ProbabilityTerm(ArgumentTerm("a")),), ()),
            operator,  # type: ignore[arg-type]
            threshold,
        )
    )


def test_formula_writer_round_trips_scientific_notation_threshold() -> None:
    """Issue #12: every threshold in [0, 1] survives write/parse.

    Hunter, Polberg, and Thimm's epistemic atoms p(alpha) # x allow any
    x in [0, 1] (Definition 3.1); the writer must not emit text for such an
    x that the parser rejects.
    """
    tiny = _threshold_atom(">", 1e-7)
    ordinary = _threshold_atom(">", 0.25)

    assert parse_epistemic_formula(write_epistemic_formula(tiny)) == tiny
    # Control: a plain decimal threshold already round-trips.
    assert parse_epistemic_formula(write_epistemic_formula(ordinary)) == ordinary


@given(
    threshold=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    )
)
@settings(max_examples=200)
def test_formula_writer_round_trips_every_unit_interval_threshold(
    threshold: float,
) -> None:
    formula = _threshold_atom("<=", threshold)

    assert parse_epistemic_formula(write_epistemic_formula(formula)) == formula


@given(
    p_empty=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
    p_a=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_hunter_definition_3_2_negated_term_probability_is_complement(
    p_empty: float,
    p_a: float,
) -> None:
    total = p_empty + p_a
    if total == 0:
        p_empty = 1.0
        p_a = 0.0
    else:
        p_empty /= total
        p_a /= total
    distribution = ProbabilityFunction(
        arguments=frozenset({"a"}),
        probabilities={frozenset(): p_empty, frozenset({"a"}): p_a},
    )

    assert term_probability(parse_term("!a"), distribution) == pytest.approx(
        1.0 - term_probability(parse_term("a"), distribution)
    )
