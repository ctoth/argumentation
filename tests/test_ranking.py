from __future__ import annotations

import pytest

import argumentation
from argumentation.dung import ArgumentationFramework
from argumentation.ranking import (
    burden_numbers,
    burden_ranking,
    categoriser_ranking,
    categoriser_scores,
)


def test_ranking_module_is_exported() -> None:
    assert argumentation.ranking.categoriser_scores is categoriser_scores
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
    scores = categoriser_scores(_bonzon_example(), tolerance=1e-10)

    assert scores["a"] == pytest.approx(0.38, abs=0.01)
    assert scores["b"] == pytest.approx(1.00, abs=0.01)
    assert scores["c"] == pytest.approx(0.50, abs=0.01)
    assert scores["d"] == pytest.approx(0.65, abs=0.01)
    assert scores["e"] == pytest.approx(0.53, abs=0.01)

    ranking = categoriser_ranking(_bonzon_example(), tolerance=1e-10)
    assert ranking.ordered_tiers == (
        frozenset({"b"}),
        frozenset({"d"}),
        frozenset({"e"}),
        frozenset({"c"}),
        frozenset({"a"}),
    )
    assert ranking.strictly_prefers("b", "a")


def test_burden_numbers_match_bonzon_running_example_steps() -> None:
    burdens = burden_numbers(_bonzon_example(), iterations=2)

    assert burdens[1] == pytest.approx({
        "a": 3.0,
        "b": 1.0,
        "c": 2.0,
        "d": 2.0,
        "e": 3.0,
    })
    assert burdens[2] == pytest.approx({
        "a": 2.5,
        "b": 1.0,
        "c": 2.0,
        "d": 1.3333333333,
        "e": 1.8333333333,
    })

    ranking = burden_ranking(_bonzon_example(), iterations=2)
    assert ranking.ordered_tiers == (
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
