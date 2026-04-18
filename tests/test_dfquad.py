from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import ProbabilisticAF, compute_probabilistic_acceptance
from argumentation.probabilistic_dfquad import (
    compute_dfquad_baf_strengths,
    compute_dfquad_quad_strengths,
    dfquad_aggregate,
    dfquad_combine,
)


def test_dfquad_aggregate_bounds_attack_and_support_effects() -> None:
    assert dfquad_aggregate(0.4, 0.5) == pytest.approx(0.7)
    assert dfquad_aggregate(0.4, -0.5) == pytest.approx(0.2)


def test_dfquad_combine_uses_noisy_or_for_each_polarity() -> None:
    assert dfquad_combine([0.5, 0.5], []) == pytest.approx(0.75)
    assert dfquad_combine([], [0.5, 0.5]) == pytest.approx(-0.75)


def test_quad_strengths_are_support_sensitive() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            defeats=frozenset(),
        ),
        p_args={"a": 0.9, "b": 0.3},
        p_defeats={},
        supports=frozenset({("a", "b")}),
        p_supports={("a", "b"): 0.8},
    )

    strengths = compute_dfquad_quad_strengths(
        praf,
        {("a", "b"): 0.8},
        tau={"a": 0.9, "b": 0.3},
    )

    assert strengths["b"] > 0.3


def test_dfquad_dispatch_requires_explicit_tau_for_quad_mode() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(arguments=frozenset({"a"}), defeats=frozenset()),
        p_args={"a": 0.8},
        p_defeats={},
    )

    with pytest.raises(ValueError, match="tau"):
        compute_probabilistic_acceptance(praf, strategy="dfquad_quad")


def test_baf_strengths_use_neutral_base_score() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            defeats=frozenset({("a", "b")}),
        ),
        p_args={"a": 1.0, "b": 1.0},
        p_defeats={("a", "b"): 1.0},
    )

    strengths = compute_dfquad_baf_strengths(praf, {})

    assert strengths["a"] == pytest.approx(0.5)
    assert strengths["b"] < 0.5
