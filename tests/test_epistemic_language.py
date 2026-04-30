from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.epistemic import (
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
    assert write_epistemic_formula(parse_epistemic_formula(write_epistemic_formula(formula))) == (
        write_epistemic_formula(formula)
    )


def test_hunter_definition_3_1_rejects_atom_thresholds_outside_unit_interval() -> None:
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        EpistemicAtom(
            OperationalFormula((ProbabilityTerm(parse_term("a")),), ()),
            ">",
            1.1,
        )


@given(
    p_empty=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
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
