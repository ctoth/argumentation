from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.probabilistic.epistemic import (
    ProbabilityFunction,
    induced_probability_labelling,
    possible_worlds,
)


SMALL_ARGUMENTS = ("a", "b", "c")


def test_potyka_basics_possible_worlds_are_all_argument_subsets() -> None:
    assert possible_worlds(frozenset({"a", "b"})) == (
        frozenset(),
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"a", "b"}),
    )


def test_potyka_basics_induced_argument_probabilities_sum_worlds_containing_argument() -> (
    None
):
    distribution = ProbabilityFunction(
        arguments=frozenset({"a", "b"}),
        probabilities={
            frozenset(): 0.1,
            frozenset({"a"}): 0.2,
            frozenset({"b"}): 0.3,
            frozenset({"a", "b"}): 0.4,
        },
    )

    assert induced_probability_labelling(distribution) == pytest.approx(
        {"a": 0.6, "b": 0.7}
    )


def test_probability_function_rejects_missing_worlds_or_non_normalized_mass() -> None:
    with pytest.raises(ValueError, match="possible worlds"):
        ProbabilityFunction(
            arguments=frozenset({"a"}),
            probabilities={frozenset(): 1.0},
        )
    with pytest.raises(ValueError, match="sum to 1"):
        ProbabilityFunction(
            arguments=frozenset({"a"}),
            probabilities={frozenset(): 0.8, frozenset({"a"}): 0.8},
        )


@pytest.mark.parametrize("bad_mass", [float("nan"), float("inf"), float("-inf")])
def test_probability_function_rejects_nonfinite_world_mass(bad_mass: float) -> None:
    """Issue #11: world masses must be real numbers in [0, 1].

    Hunter and Thimm (2017), p.7: a probability function maps 2^Arg to [0, 1]
    with total mass 1, so NaN or infinite masses are not probabilities.
    """
    with pytest.raises(ValueError, match="finite"):
        ProbabilityFunction(
            arguments=frozenset({"a"}),
            probabilities={frozenset(): bad_mass, frozenset({"a"}): bad_mass},
        )
    # Control: a finite neighbouring distribution is accepted.
    control = ProbabilityFunction(
        arguments=frozenset({"a"}),
        probabilities={frozenset(): 0.5, frozenset({"a"}): 0.5},
    )
    assert induced_probability_labelling(control) == pytest.approx({"a": 0.5})


@st.composite
def normalized_distributions(draw: st.DrawFn) -> ProbabilityFunction:
    arguments = frozenset(draw(st.sets(st.sampled_from(SMALL_ARGUMENTS), max_size=3)))
    worlds = possible_worlds(arguments)
    raw_weights = draw(
        st.lists(
            st.floats(
                min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
            ),
            min_size=len(worlds),
            max_size=len(worlds),
        )
    )
    total = sum(raw_weights)
    if total == 0.0:
        weights = [1.0 / len(worlds) for _ in worlds]
    else:
        weights = [weight / total for weight in raw_weights]
    return ProbabilityFunction(
        arguments=arguments, probabilities=dict(zip(worlds, weights, strict=True))
    )


@given(normalized_distributions())
@settings(max_examples=100)
def test_any_probability_function_induces_valid_probability_labelling(
    distribution: ProbabilityFunction,
) -> None:
    labelling = induced_probability_labelling(distribution)

    assert set(labelling) == set(distribution.arguments)
    assert all(0.0 <= value <= 1.0 for value in labelling.values())
    for argument in distribution.arguments:
        expected = sum(
            probability
            for world, probability in distribution.probabilities.items()
            if argument in world
        )
        assert labelling[argument] == pytest.approx(expected)
