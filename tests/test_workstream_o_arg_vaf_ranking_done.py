from __future__ import annotations

import importlib

import pytest

import argumentation
from argumentation.dung import ArgumentationFramework
from argumentation.ranking import RankingResult, categoriser_scores
from argumentation.ranking_axioms import (
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
    assert argumentation.vaf is importlib.import_module("argumentation.vaf")
    assert argumentation.practical_reasoning is importlib.import_module(
        "argumentation.practical_reasoning"
    )
    assert argumentation.subjective_aspic is importlib.import_module(
        "argumentation.subjective_aspic"
    )
    assert argumentation.ranking_axioms is importlib.import_module(
        "argumentation.ranking_axioms"
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
        argumentation.ranking_axioms.abstraction,
        argumentation.ranking_axioms.cardinality_precedence,
        argumentation.ranking_axioms.counter_transitivity,
        argumentation.ranking_axioms.defense_precedence,
        argumentation.ranking_axioms.distributed_defense_precedence,
        argumentation.ranking_axioms.independence,
        argumentation.ranking_axioms.quality_precedence,
        argumentation.ranking_axioms.self_contradiction,
        argumentation.ranking_axioms.strict_addition_of_defense_branch,
        argumentation.ranking_axioms.strict_counter_transitivity,
        argumentation.ranking_axioms.strict_preference_transitive,
        argumentation.ranking_axioms.void_precedence,
    }
