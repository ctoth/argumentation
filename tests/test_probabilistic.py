from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
    summarize_defeat_relations,
)


def test_deterministic_probabilistic_af_matches_grounded_extension() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c")}),
    )
    praf = ProbabilisticAF(
        framework=framework,
        p_args={"a": 1.0, "b": 1.0, "c": 1.0},
        p_defeats={("a", "b"): 1.0, ("b", "c"): 1.0},
    )

    result = compute_probabilistic_acceptance(
        praf,
        semantics="grounded",
        strategy="deterministic",
    )

    assert result.acceptance_probs == {"a": 1.0, "b": 0.0, "c": 1.0}
    assert result.strategy_used == "deterministic"


def test_exact_enum_extension_probability_query() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    praf = ProbabilisticAF(
        framework=framework,
        p_args={"a": 1.0, "b": 1.0},
        p_defeats={("a", "b"): 0.5},
    )

    result = compute_probabilistic_acceptance(
        praf,
        semantics="grounded",
        strategy="exact_enum",
        query_kind="extension_probability",
        queried_set={"a"},
    )

    assert result.extension_probability == pytest.approx(0.5)


def test_probabilities_are_plain_bounded_floats() -> None:
    framework = ArgumentationFramework(arguments=frozenset({"a"}), defeats=frozenset())

    with pytest.raises(ValueError, match="p_args"):
        ProbabilisticAF(framework=framework, p_args={"a": 1.2}, p_defeats={})


def test_summarize_defeat_relations_returns_exact_marginals() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    praf = ProbabilisticAF(
        framework=framework,
        p_args={"a": 1.0, "b": 1.0},
        p_defeats={("a", "b"): 0.25},
    )

    assert summarize_defeat_relations(praf) == {("a", "b"): pytest.approx(0.25)}
