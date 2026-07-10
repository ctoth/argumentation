from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from argumentation.core.dung import ArgumentationFramework
from argumentation.ranking.ranking import (
    RankingResult,
    burden_numbers,
    burden_ranking,
    categoriser_ranking,
    categoriser_scores,
    counting_ranking,
    discussion_based_ranking,
    h_categoriser_ranking,
    iterated_graded_ranking,
    tuples_ranking,
)


def _bonzon_example() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d", "e"}),
        defeats=frozenset({
            ("a", "e"),
            ("b", "a"),
            ("b", "c"),
            ("c", "e"),
            ("d", "a"),
            ("e", "d"),
        }),
    )


def test_categoriser_scores_match_bonzon_running_example() -> None:
    result = categoriser_scores(_bonzon_example(), tolerance=1e-10)

    assert result.converged is True
    assert result.semantics == "categoriser"
    assert result.scores["a"] == pytest.approx(0.38, abs=0.01)
    assert result.scores["b"] == pytest.approx(1.00, abs=0.01)
    assert result.scores["c"] == pytest.approx(0.50, abs=0.01)
    assert result.scores["d"] == pytest.approx(0.65, abs=0.01)
    assert result.scores["e"] == pytest.approx(0.53, abs=0.01)

    ranking = categoriser_ranking(_bonzon_example(), tolerance=1e-10)
    assert ranking.ranking == (
        frozenset({"b"}),
        frozenset({"d"}),
        frozenset({"e"}),
        frozenset({"c"}),
        frozenset({"a"}),
    )
    assert ranking.strictly_prefers("b", "a")


def test_burden_numbers_match_bonzon_running_example_steps() -> None:
    burdens = burden_numbers(_bonzon_example(), iterations=2)

    assert burdens.converged is False
    assert burdens.semantics == "burden"
    assert burdens.iterations == 2
    assert burdens.scores == pytest.approx({
        "a": 2.5,
        "b": 1.0,
        "c": 2.0,
        "d": 1.3333333333,
        "e": 1.8333333333,
    })

    ranking = burden_ranking(_bonzon_example(), iterations=2)
    assert ranking.scores == {
        "a": (1.0, 3.0, 2.5),
        "b": (1.0, 1.0, 1.0),
        "c": (1.0, 2.0, 2.0),
        "d": (1.0, 2.0, pytest.approx(1.3333333333)),
        "e": (1.0, 3.0, pytest.approx(1.8333333333)),
    }
    assert ranking.ranking == (
        frozenset({"b"}),
        frozenset({"d"}),
        frozenset({"c"}),
        frozenset({"e"}),
        frozenset({"a"}),
    )
    assert ranking.strictly_prefers("d", "c")
    assert ranking.strictly_prefers("c", "e")
    assert ranking.converged is False


def _burden_sequences(
    framework: ArgumentationFramework,
    *,
    iterations: int,
) -> dict[str, tuple[float, ...]]:
    """Test oracle for Amgoud--Ben-Naim 2013, page-010.png, Defs. 12-13."""

    current = {argument: 1.0 for argument in framework.arguments}
    sequences = {argument: [1.0] for argument in framework.arguments}
    for _ in range(iterations):
        current = {
            argument: 1.0
            + sum(
                1.0 / current[attacker]
                for attacker, target in framework.defeats
                if target == argument
            )
            for argument in framework.arguments
        }
        for argument, value in current.items():
            sequences[argument].append(value)
    return {argument: tuple(values) for argument, values in sequences.items()}


def test_ranking_keeps_unattacked_arguments_above_attacked_arguments() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("a", "c")}),
    )

    ranking = categoriser_ranking(framework)

    assert ranking.strictly_prefers("a", "b")
    assert ranking.strictly_prefers("a", "c")
    assert ranking.equivalent("b", "c")


def test_categoriser_non_convergence_is_result_data() -> None:
    result = categoriser_scores(_bonzon_example(), tolerance=1e-30, max_iterations=1)

    assert result.converged is False
    assert result.iterations == 1
    assert set(result.scores) == _bonzon_example().arguments


def _discussion_sequence(
    framework: ArgumentationFramework,
    argument: str,
    *,
    max_length: int,
) -> tuple[int, ...]:
    """Test oracle for Amgoud--Ben-Naim 2013, page-009.png, Defs. 10-11."""

    multiplicities = {argument: 1}
    sequence: list[int] = []
    for length in range(1, max_length + 1):
        count = sum(multiplicities.values())
        sequence.append(-count if length % 2 == 1 else count)
        next_multiplicities: dict[str, int] = {}
        for target, multiplicity in multiplicities.items():
            for attacker, attacked in framework.defeats:
                if attacked == target:
                    next_multiplicities[attacker] = (
                        next_multiplicities.get(attacker, 0) + multiplicity
                    )
        multiplicities = next_multiplicities
    return tuple(sequence)


def test_discussion_ranking_counts_linear_discussions_with_multiplicity() -> None:
    # Both roots have two direct attackers. The two length-three discussions
    # for ``a`` merge at d, while ``x`` has only one. A set frontier loses that
    # multiplicity and incorrectly ties the arguments.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d", "x", "y", "z", "w"}),
        defeats=frozenset({
            ("b", "a"),
            ("c", "a"),
            ("d", "b"),
            ("d", "c"),
            ("y", "x"),
            ("z", "x"),
            ("w", "y"),
        }),
    )

    result = discussion_based_ranking(framework, max_depth=3)

    assert result.scores["a"] == (-1, 2, -2)
    assert result.scores["x"] == (-1, 2, -1)
    assert result.strictly_prefers("a", "x")
    assert result.converged is True
    assert result.iterations == 3


def test_discussion_ranking_marks_a_bounded_cycle_as_truncated() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    result = discussion_based_ranking(framework, max_depth=4)

    assert result.scores["a"] == (-1, 1, -1, 1)
    assert result.scores["b"] == (-1, 1, -1, 1)
    assert result.converged is False
    assert result.iterations == 4


@pytest.mark.parametrize(
    "semantic",
    [
        discussion_based_ranking,
        counting_ranking,
        tuples_ranking,
        h_categoriser_ranking,
        iterated_graded_ranking,
    ],
)
def test_additional_ranking_semantics_return_total_preorders(semantic) -> None:
    result = semantic(_bonzon_example())

    assert isinstance(result, RankingResult)
    assert set(result.scores) == _bonzon_example().arguments
    assert set().union(*result.ranking) == _bonzon_example().arguments
    assert all(result.equivalent(argument, argument) for argument in _bonzon_example().arguments)


def _small_frameworks() -> st.SearchStrategy[ArgumentationFramework]:
    arguments = ("a", "b", "c", "d")
    possible_attacks = [(attacker, target) for attacker in arguments for target in arguments]
    return st.builds(
        lambda attacks: ArgumentationFramework(
            arguments=frozenset(arguments),
            defeats=frozenset(attacks),
        ),
        st.sets(st.sampled_from(possible_attacks), max_size=8),
    )


def _small_acyclic_frameworks() -> st.SearchStrategy[ArgumentationFramework]:
    arguments = ("a", "b", "c", "d")
    possible_attacks = [
        (arguments[left], arguments[right])
        for left in range(len(arguments))
        for right in range(left + 1, len(arguments))
    ]
    return st.builds(
        lambda attacks: ArgumentationFramework(
            arguments=frozenset(arguments),
            defeats=frozenset(attacks),
        ),
        st.sets(st.sampled_from(possible_attacks)),
    )


@given(_small_acyclic_frameworks())
def test_burden_ranking_matches_lexicographic_sequence_property(
    framework: ArgumentationFramework,
) -> None:
    # Four iterations are sufficient to propagate through and then stabilize
    # every attack chain in a four-node DAG.
    result = burden_ranking(framework, iterations=4)
    expected = _burden_sequences(framework, iterations=4)

    for argument in framework.arguments:
        assert result.scores[argument] == pytest.approx(expected[argument])
    assert result.converged is True
    for left in framework.arguments:
        for right in framework.arguments:
            if expected[left] < expected[right]:
                assert result.strictly_prefers(left, right)
            elif expected[left] == expected[right]:
                assert result.equivalent(left, right)


@given(_small_acyclic_frameworks())
def test_discussion_ranking_matches_linear_discussion_count_property(
    framework: ArgumentationFramework,
) -> None:
    # In a four-node DAG every linear discussion has length at most four.
    # The exact signed sequence, including path multiplicity, is the semantic
    # object compared by Definition 11 on Amgoud--Ben-Naim page-009.png.
    result = discussion_based_ranking(framework, max_depth=4)
    expected = {
        argument: _discussion_sequence(framework, argument, max_length=4)
        for argument in framework.arguments
    }

    assert result.scores == expected
    assert result.converged is True
    for left in framework.arguments:
        for right in framework.arguments:
            if expected[left] < expected[right]:
                assert result.strictly_prefers(left, right)
            elif expected[left] == expected[right]:
                assert result.equivalent(left, right)


@given(_small_frameworks())
def test_generated_ranking_results_are_reflexive_and_transitive(
    framework: ArgumentationFramework,
) -> None:
    # Ranking semantics are total preorders over arguments; every result should
    # therefore induce reflexive equivalence and transitive strict preference.
    result = categoriser_ranking(framework, max_iterations=100)

    for argument in framework.arguments:
        assert result.equivalent(argument, argument)

    for left in framework.arguments:
        for middle in framework.arguments:
            for right in framework.arguments:
                if result.strictly_prefers(left, middle) and result.strictly_prefers(middle, right):
                    assert result.strictly_prefers(left, right)
