from __future__ import annotations

import pytest

import argumentation
from argumentation.dung import grounded_extension
from argumentation.weighted import (
    WeightedArgumentationFramework,
    minimum_budget_for_grounded_acceptance,
    weighted_grounded_extensions,
)


def test_weighted_module_is_exported() -> None:
    assert argumentation.weighted.WeightedArgumentationFramework is WeightedArgumentationFramework
    assert "weighted" in argumentation.__all__


def _mutual_weighted_framework() -> WeightedArgumentationFramework:
    return WeightedArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        attacks=frozenset({("a", "b"), ("b", "a")}),
        weights={("a", "b"): 1.0, ("b", "a"): 2.0},
    )


def test_weighted_framework_requires_positive_attack_weights() -> None:
    with pytest.raises(ValueError, match="positive"):
        WeightedArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            attacks=frozenset({("a", "b")}),
            weights={("a", "b"): 0.0},
        )

    with pytest.raises(ValueError, match="exactly"):
        WeightedArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            attacks=frozenset({("a", "b")}),
            weights={},
        )


def test_zero_budget_recovers_unweighted_grounded_extension() -> None:
    framework = _mutual_weighted_framework()

    weighted = weighted_grounded_extensions(framework, budget=0.0)

    assert [result.extension for result in weighted] == [
        grounded_extension(framework.as_dung_framework())
    ]
    assert weighted[0].deleted_attacks == frozenset()
    assert weighted[0].deleted_weight == pytest.approx(0.0)


def test_increasing_budget_adds_grounded_extensions_with_witnesses() -> None:
    framework = _mutual_weighted_framework()

    beta_one = weighted_grounded_extensions(framework, budget=1.0)
    beta_two = weighted_grounded_extensions(framework, budget=2.0)

    assert {result.extension for result in beta_one} == {
        frozenset(),
        frozenset({"b"}),
    }
    b_witness = next(result for result in beta_one if result.extension == frozenset({"b"}))
    assert b_witness.deleted_attacks == frozenset({("a", "b")})
    assert b_witness.deleted_weight == pytest.approx(1.0)

    assert {result.extension for result in beta_two} == {
        frozenset(),
        frozenset({"a"}),
        frozenset({"b"}),
    }
    a_witness = next(result for result in beta_two if result.extension == frozenset({"a"}))
    assert a_witness.deleted_attacks == frozenset({("b", "a")})
    assert a_witness.deleted_weight == pytest.approx(2.0)


def test_minimum_budget_for_grounded_acceptance() -> None:
    framework = _mutual_weighted_framework()

    assert minimum_budget_for_grounded_acceptance(framework, "a") == pytest.approx(2.0)
    assert minimum_budget_for_grounded_acceptance(framework, "b") == pytest.approx(1.0)
