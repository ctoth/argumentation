from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

import argumentation
from argumentation.dung import ArgumentationFramework
from argumentation.ranking import (
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


def test_ranking_module_is_exported() -> None:
    assert argumentation.ranking.categoriser_scores is categoriser_scores
    assert argumentation.ranking.RankingResult is RankingResult
    assert "ranking" in argumentation.__all__


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

    assert burdens.converged is True
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
    assert ranking.ranking == (
        frozenset({"b"}),
        frozenset({"d"}),
        frozenset({"e"}),
        frozenset({"c"}),
        frozenset({"a"}),
    )
    assert ranking.strictly_prefers("d", "c")


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
