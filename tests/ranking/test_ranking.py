from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

import argumentation.ranking.ranking as ranking_module
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


def test_h_categoriser_does_not_cap_the_attacker_sum() -> None:
    # Besnard--Hunter 2001, page-019.png (printed p.222), Definition 8.10:
    # h(N) = 1 / (1 + h(N1) + ... + h(Nl)). Two leaf attackers therefore
    # give 1/3, not the capped value 1/2.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("b", "a"), ("c", "a")}),
    )

    result = h_categoriser_ranking(framework)

    assert result.scores["a"] == pytest.approx(1.0 / 3.0)
    assert result.scores["b"] == pytest.approx(1.0)
    assert result.scores["c"] == pytest.approx(1.0)


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


def test_counting_ranking_uses_normalized_alternating_path_counts() -> None:
    # Delobelle--Villata 2019 page-004.png, Definition 5. With two leaf
    # attackers, the matrix infinity norm is two and the attacked argument's
    # limit is 1 - alpha * (1 + 1) / 2 = 1 - alpha.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("b", "a"), ("c", "a")}),
    )

    result = counting_ranking(framework, damping=0.9)

    assert result.scores["a"] == pytest.approx(0.1)
    assert result.scores["b"] == pytest.approx(1.0)
    assert result.scores["c"] == pytest.approx(1.0)
    assert result.converged is True


@pytest.mark.parametrize(
    "semantic",
    [
        discussion_based_ranking,
        counting_ranking,
        h_categoriser_ranking,
    ],
)
def test_additional_ranking_semantics_return_total_preorders(semantic) -> None:
    result = semantic(_bonzon_example())

    assert isinstance(result, RankingResult)
    assert set(result.scores) == _bonzon_example().arguments
    assert set().union(*result.ranking) == _bonzon_example().arguments
    assert all(result.equivalent(argument, argument) for argument in _bonzon_example().arguments)


def test_false_scalar_iterated_graded_paper_export_is_absent() -> None:
    # Grossi--Modgil 2015 defines argument rankings through graded defense,
    # neutrality, and extension semantics. A local weighted attacker/defender
    # count is not that semantic and must not retain its paper name.
    assert not hasattr(ranking_module, "iterated_graded_ranking")


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
def test_h_categoriser_is_the_besnard_hunter_categoriser(
    framework: ArgumentationFramework,
) -> None:
    expected = categoriser_scores(framework, max_iterations=100)
    actual = h_categoriser_ranking(framework, max_iterations=100)

    assert actual.scores == pytest.approx(expected.scores)
    assert actual.ranking == expected.ranking
    assert actual.converged is expected.converged
    assert actual.iterations == expected.iterations


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


def _branch_lengths(framework: ArgumentationFramework, argument: str) -> tuple[int, ...]:
    attackers = tuple(
        attacker for attacker, target in framework.defeats if target == argument
    )
    if not attackers:
        return (0,)
    return tuple(
        sorted(
            length + 1
            for attacker in attackers
            for length in _branch_lengths(framework, attacker)
        )
    )


@given(_small_acyclic_frameworks(), st.floats(min_value=0.05, max_value=0.95))
def test_counting_ranking_matches_finite_matrix_series_on_dags(
    framework: ArgumentationFramework,
    damping: float,
) -> None:
    # In a four-node DAG, M^4 is zero. Definition 5's infinite series is
    # therefore exactly the first four signed walk-count terms.
    normalization = max(
        (
            sum(1 for _attacker, target in framework.defeats if target == argument)
            for argument in framework.arguments
        ),
        default=0,
    )
    normalization = max(normalization, 1)
    expected = {
        argument: sum(
            ((-1.0) ** (length - 1))
            * (damping ** (length - 1))
            * abs(count)
            / (normalization ** (length - 1))
            for length, count in enumerate(
                _discussion_sequence(framework, argument, max_length=4),
                start=1,
            )
        )
        for argument in framework.arguments
    }

    result = counting_ranking(
        framework,
        damping=damping,
        tolerance=1e-12,
        max_iterations=5,
    )

    assert result.scores == pytest.approx(expected)
    assert result.converged is True


def test_tuples_ranking_preserves_exact_branch_tuples_and_incomparability() -> None:
    # Bonzon 2016 page-004.png, Definition 17 and Algorithm 1. ``a`` has
    # [(2),(1)]; ``x`` has [(2,2),(1,1)]. More defenses and more attacks are
    # conflicting criteria, so neither argument outranks the other.
    framework = ArgumentationFramework(
        arguments=frozenset({
            "a",
            "a_direct",
            "a_mid",
            "a_deep",
            "x",
            "x_direct_1",
            "x_direct_2",
            "x_mid_1",
            "x_mid_2",
            "x_deep_1",
            "x_deep_2",
        }),
        defeats=frozenset({
            ("a_direct", "a"),
            ("a_mid", "a"),
            ("a_deep", "a_mid"),
            ("x_direct_1", "x"),
            ("x_direct_2", "x"),
            ("x_mid_1", "x"),
            ("x_mid_2", "x"),
            ("x_deep_1", "x_mid_1"),
            ("x_deep_2", "x_mid_2"),
        }),
    )

    result = tuples_ranking(framework)

    assert result.values["a"].defense_lengths == (2,)
    assert result.values["a"].attack_lengths == (1,)
    assert result.values["x"].defense_lengths == (2, 2)
    assert result.values["x"].attack_lengths == (1, 1)
    assert result.incomparable("a", "x")
    assert not result.equivalent("a", "x")
    assert result.values["a_direct"].infinite_defense_zeros is True


def test_tuples_ranking_rejects_cyclic_frameworks() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    with pytest.raises(ValueError, match="acyclic"):
        tuples_ranking(framework)


@given(_small_acyclic_frameworks())
def test_tuples_ranking_matches_branch_multisets_and_is_a_partial_preorder(
    framework: ArgumentationFramework,
) -> None:
    result = tuples_ranking(framework)

    for argument in framework.arguments:
        lengths = _branch_lengths(framework, argument)
        value = result.values[argument]
        if lengths == (0,):
            assert value.infinite_defense_zeros is True
            assert value.defense_lengths == ()
            assert value.attack_lengths == ()
        else:
            assert value.infinite_defense_zeros is False
            assert value.defense_lengths == tuple(length for length in lengths if length % 2 == 0)
            assert value.attack_lengths == tuple(length for length in lengths if length % 2 == 1)

    for left in framework.arguments:
        assert result.at_least_as_acceptable(left, left)
        for middle in framework.arguments:
            for right in framework.arguments:
                if result.at_least_as_acceptable(
                    left, middle
                ) and result.at_least_as_acceptable(middle, right):
                    assert result.at_least_as_acceptable(left, right)


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
