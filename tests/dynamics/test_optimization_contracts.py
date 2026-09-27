"""Regression contracts for OMT-backed argumentation optimization.

Selected sets are Dung conflict-free or admissible sets (Dung 1995, Def 5-6,
p.326; papers/Dung_1995_AcceptabilityArguments/notes.md); objectives are
combined lexicographically (Bjorner & Phan 2014, p.7).
"""

from __future__ import annotations

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.dynamics.optimization import (
    OptimizationFeature,
    OptimizationObjective,
    OptimizationPolicy,
    _z3_safe_name,
    optimize_framework,
)

pytest.importorskip("z3")


def test_z3_symbol_names_are_injective_over_distinct_arguments() -> None:
    """Issue #40: each argument is its own membership variable; distinct
    arguments a-b and a_b must not share a solver symbol."""
    arguments = ("a-b", "a_b", "a b", "a.b", "a__b", "a_2d_b", "ab")

    symbols = [_z3_safe_name(argument) for argument in arguments]

    assert len(set(symbols)) == len(arguments)
    assert all(symbol.replace("_", "").isalnum() for symbol in symbols)


def test_optimization_distinguishes_arguments_with_colliding_sanitized_names() -> None:
    """Issue #40: in the conflict-free framework {a-b, a_b} with no attacks,
    choosing exactly one candidate is satisfiable (Dung 1995, p.326)."""
    framework = ArgumentationFramework(frozenset({"a-b", "a_b"}), frozenset())
    policy = OptimizationPolicy(
        candidates=framework.arguments,
        objectives=(OptimizationObjective("score", "maximize"),),
    )

    result = optimize_framework(
        framework,
        policy,
        [
            OptimizationFeature("a-b", "score", 1),
            OptimizationFeature("a_b", "score", 5),
        ],
    )

    assert result.status == "optimal"
    assert result.selected_candidate == "a_b"
    assert result.objective_values["score"] == 5


def test_optimization_plain_argument_names_control() -> None:
    """Issue #40 control: ordinary identifier arguments optimize as before."""
    framework = ArgumentationFramework(frozenset({"a", "b"}), frozenset())
    policy = OptimizationPolicy(
        candidates=framework.arguments,
        objectives=(OptimizationObjective("score", "maximize"),),
    )

    result = optimize_framework(
        framework,
        policy,
        [OptimizationFeature("a", "score", 3), OptimizationFeature("b", "score", 2)],
    )

    assert result.status == "optimal"
    assert result.selected_candidate == "a"
