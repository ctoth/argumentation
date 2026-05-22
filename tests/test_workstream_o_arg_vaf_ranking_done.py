from __future__ import annotations

import importlib

import pytest

import argumentation
from argumentation.core.dung import ArgumentationFramework
from argumentation.ranking.ranking import RankingResult, categoriser_scores
from argumentation.ranking.ranking_axioms import (
    abstraction,
    cardinality_precedence,
    counter_transitivity,
    defense_precedence,
    distributed_defense_precedence,
    independence,
    quality_precedence,
    self_contradiction,
    strict_addition_of_defense_branch,
    strict_counter_transitivity,
    strict_preference_transitive,
    void_precedence,
)


def test_workstream_o_arg_vaf_ranking_public_surface_is_closed() -> None:
    assert argumentation.frameworks.vaf is importlib.import_module("argumentation.frameworks.vaf")
    assert argumentation.frameworks.practical_reasoning is importlib.import_module(
        "argumentation.frameworks.practical_reasoning"
    )
    assert argumentation.structured.aspic.subjective_aspic is importlib.import_module(
        "argumentation.structured.aspic.subjective_aspic"
    )
    assert argumentation.ranking.ranking_axioms is importlib.import_module(
        "argumentation.ranking.ranking_axioms"
    )

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("argumentation.value_based")


def test_workstream_o_arg_vaf_ranking_contracts_are_closed() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    result = categoriser_scores(framework, max_iterations=1, tolerance=1e-30)

    assert isinstance(result, RankingResult)
    assert result.converged is False
    assert {
        abstraction,
        cardinality_precedence,
        counter_transitivity,
        defense_precedence,
        distributed_defense_precedence,
        independence,
        quality_precedence,
        self_contradiction,
        strict_addition_of_defense_branch,
        strict_counter_transitivity,
        strict_preference_transitive,
        void_precedence,
    } == {
        argumentation.ranking.ranking_axioms.abstraction,
        argumentation.ranking.ranking_axioms.cardinality_precedence,
        argumentation.ranking.ranking_axioms.counter_transitivity,
        argumentation.ranking.ranking_axioms.defense_precedence,
        argumentation.ranking.ranking_axioms.distributed_defense_precedence,
        argumentation.ranking.ranking_axioms.independence,
        argumentation.ranking.ranking_axioms.quality_precedence,
        argumentation.ranking.ranking_axioms.self_contradiction,
        argumentation.ranking.ranking_axioms.strict_addition_of_defense_branch,
        argumentation.ranking.ranking_axioms.strict_counter_transitivity,
        argumentation.ranking.ranking_axioms.strict_preference_transitive,
        argumentation.ranking.ranking_axioms.void_precedence,
    }
