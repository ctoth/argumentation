"""Tests for argumentation-framework sensitivity / importance analysis.

Each case uses a small hand-constructed framework whose expected
sensitivity value is checked by hand in the accompanying comments.
"""

from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.sensitivity import attack_removal_sensitivity, score_conflict


# ── score_conflict ──────────────────────────────────────────────────


def test_score_conflict_pivotal_argument_is_one() -> None:
    # a defeats b.  grounded = {a}.
    # remove a -> args {b}, grounded {b}; symdiff {a,b} = 2.
    # remove b -> args {a}, grounded {a}; symdiff {} = 0.
    # total = 2 -> min(1, 2/2) = 1.0.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    assert score_conflict(framework, "a", "b") == pytest.approx(1.0)


def test_score_conflict_isolated_arguments_only_drop_themselves() -> None:
    # three arguments, no defeats. grounded = {a,b,c}.
    # removing a leaves {b,c}; symdiff = {a} = 1. likewise for b.
    # total = 3 -> min(1, 1/3) = 1/3.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset(),
    )
    assert score_conflict(framework, "a", "b") == pytest.approx(1.0 / 3.0)


def test_score_conflict_empty_framework_is_zero() -> None:
    framework = ArgumentationFramework(arguments=frozenset(), defeats=frozenset())
    assert score_conflict(framework, "a", "b") == 0.0


def test_score_conflict_rejects_unsupported_semantics() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a"}),
        defeats=frozenset(),
    )
    with pytest.raises(ValueError, match="Unsupported semantics"):
        score_conflict(framework, "a", "a", semantics="preferred")


# ── attack_removal_sensitivity ──────────────────────────────────────


def test_attack_removal_sensitivity_recovers_suppressed_strength() -> None:
    # a -> b, base scores 0.5 / 0.5, no supports.
    # with attack: b influence = -(1 - (1-0.5)) = -0.5;
    #   dfquad_aggregate(0.5, -0.5) = 0.5 + (-0.5)*0.5 = 0.25.
    # without attack: b strength = base 0.5.
    # delta = 0.5 - 0.25 = 0.25.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    base_scores = {"a": 0.5, "b": 0.5}
    delta = attack_removal_sensitivity(framework, {}, base_scores, ("a", "b"))
    assert delta == pytest.approx(0.25)


def test_attack_removal_sensitivity_absent_attack_is_zero() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    base_scores = {"a": 0.5, "b": 0.5}
    # ("b", "a") is not a defeat of the framework.
    assert attack_removal_sensitivity(framework, {}, base_scores, ("b", "a")) == 0.0


def test_attack_removal_sensitivity_targets_only_the_attacked_argument() -> None:
    # a -> b with an unrelated c. base 0.4 / 0.6 / 0.7.
    # with attack: b influence = -(1 - (1-0.4)) = -0.4;
    #   dfquad_aggregate(0.6, -0.4) = 0.6 + (-0.4)*0.6 = 0.36.
    # without attack: b strength = base 0.6.
    # delta for target b = 0.6 - 0.36 = 0.24; c never enters.
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b")}),
    )
    base_scores = {"a": 0.4, "b": 0.6, "c": 0.7}
    delta = attack_removal_sensitivity(framework, {}, base_scores, ("a", "b"))
    assert delta == pytest.approx(0.24)
