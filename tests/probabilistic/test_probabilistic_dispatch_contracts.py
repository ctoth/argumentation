"""Regression contracts for PrAF dispatch, routing, and result honesty.

Semantics follow Li, Oren & Norman (2011), "Probabilistic Argumentation
Frameworks" (papers/Li_2011_ProbabilisticArgumentationFrameworks/notes.md):
a PrAF induces a distribution over sub-frameworks (Def 3, p.2) whose world
probability is the product over present/absent arguments and defeats
(p.3-4), and acceptance marginalizes over all inducible worlds (Eq 2, p.4).
"""

from __future__ import annotations

import math

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.gradual.gradual import GradualConvergenceError
from argumentation.probabilistic.probabilistic import (
    ProbabilisticAF,
    _z_for_confidence,
    compute_probabilistic_acceptance,
    summarize_defeat_relations,
)


def _single_argument_praf(p_a: float) -> ProbabilisticAF:
    return ProbabilisticAF(
        ArgumentationFramework(frozenset({"a"}), frozenset()),
        {"a": p_a},
        {},
    )


def test_queried_set_without_query_kind_is_rejected() -> None:
    """Issue #29: an exact-set target (Li 2011 Eq 2, p.4, query set X) must
    not be silently replaced by the default argument-acceptance query."""
    praf = _single_argument_praf(1.0)

    with pytest.raises(ValueError, match="queried_set requires an explicit query_kind"):
        compute_probabilistic_acceptance(
            praf,
            strategy="exact_enum",
            queried_set={"a"},
        )


def test_queried_set_with_explicit_extension_query_is_answered() -> None:
    """Issue #29 control: the explicit extension-probability query still works."""
    praf = _single_argument_praf(1.0)

    result = compute_probabilistic_acceptance(
        praf,
        strategy="exact_enum",
        query_kind="extension_probability",
        queried_set={"a"},
    )

    assert result.query_kind == "extension_probability"
    assert result.queried_set == ("a",)
    assert result.extension_probability == 1.0


@pytest.mark.parametrize(
    "selectors",
    [
        {"query_kind": "extension_probability", "queried_set": {"a"}},
        {"query_kind": "argument_acceptance", "inference_mode": "credulous"},
        {"inference_mode": "skeptical"},
        {"queried_set": {"a"}},
    ],
)
def test_dfquad_rejects_explicit_probability_query_selectors(
    selectors: dict[str, object],
) -> None:
    """Issue #30: DF-QuAD (Rago et al. 2016) computes gradual strengths, not
    Li 2011 extension/acceptance probabilities (Eq 2, p.4); an explicitly
    requested probability query must not be answered with strengths."""
    praf = _single_argument_praf(1.0)

    with pytest.raises(ValueError, match="DF-QuAD"):
        compute_probabilistic_acceptance(
            praf,
            strategy="dfquad_quad",
            tau={"a": 0.5},
            **selectors,
        )


@pytest.mark.parametrize("selectors", [{}, {"query_kind": "gradual_strength"}])
def test_dfquad_answers_gradual_strength_query(selectors: dict[str, object]) -> None:
    """Issue #30 control: the implicit or explicit gradual-strength query is answered."""
    praf = _single_argument_praf(1.0)

    result = compute_probabilistic_acceptance(
        praf,
        strategy="dfquad_quad",
        tau={"a": 0.5},
        **selectors,
    )

    assert result.query_kind == "gradual_strength"
    assert result.acceptance_probs == {"a": 0.5}


def _self_attack_praf() -> ProbabilisticAF:
    return ProbabilisticAF(
        ArgumentationFramework(frozenset({"a"}), frozenset({("a", "a")})),
        {"a": 1.0},
        {},
    )


def test_dfquad_nonconvergent_strengths_raise() -> None:
    """Issue #31: DF-QuAD strengths are the fixed point of the Rago et al.
    (2016) update; a unit-weight self-attack oscillates 0 <-> 1, so there is
    no converged final strength to report."""
    with pytest.raises(GradualConvergenceError):
        compute_probabilistic_acceptance(
            _self_attack_praf(),
            strategy="dfquad_quad",
            tau={"a": 1.0},
        )


def test_dfquad_convergent_self_attack_strength_is_returned() -> None:
    """Issue #31 control: with base score 0.5 the self-attack has the fixed
    point s = 0.5 * (1 - s), i.e. s = 1/3, which the adapter returns."""
    result = compute_probabilistic_acceptance(
        _self_attack_praf(),
        strategy="dfquad_quad",
        tau={"a": 0.5},
    )

    assert result.acceptance_probs is not None
    assert result.acceptance_probs["a"] == pytest.approx(1.0 / 3.0)


def test_explicit_deterministic_strategy_rejects_uncertain_argument() -> None:
    """Issue #32: Li 2011 (p.2) equates a PrAF with its Dung AF only when
    P_A = 1 and P_D = 1; with P_A(a) = 0.5 the unique-world evaluation does
    not apply and a must not be silently deleted."""
    with pytest.raises(ValueError, match="deterministic"):
        compute_probabilistic_acceptance(
            _single_argument_praf(0.5),
            strategy="deterministic",
        )


def test_explicit_deterministic_strategy_rejects_uncertain_defeat() -> None:
    """Issue #32: an uncertain defeat (P_D < 1, Li 2011 Def 2, p.2) is not a
    deterministic structure either."""
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")})),
        {"a": 1.0, "b": 1.0},
        {("a", "b"): 0.5},
    )

    with pytest.raises(ValueError, match="deterministic"):
        compute_probabilistic_acceptance(praf, strategy="deterministic")


@pytest.mark.parametrize(("p_a", "expected"), [(1.0, 1.0), (0.0, 0.0)])
def test_explicit_deterministic_strategy_accepts_certain_inputs(
    p_a: float,
    expected: float,
) -> None:
    """Issue #32 control: P_A in {0, 1} is deterministic (Li 2011, p.2)."""
    result = compute_probabilistic_acceptance(
        _single_argument_praf(p_a),
        strategy="deterministic",
    )

    assert result.strategy_used == "deterministic"
    assert result.acceptance_probs == {"a": expected}


def test_z_for_confidence_handles_largest_representable_confidence() -> None:
    """Issue #33: the Agresti-Coull stopping rule (Li 2011, Eq 5, p.7) needs
    z = z_{1-alpha/2}; confidence 1 - 2**-53 lies in (0, 1) and must yield a
    finite quantile beyond the 0.999 one instead of log(0)."""
    confidence = 1.0 - 2.0**-53
    assert 0.0 < confidence < 1.0

    z = _z_for_confidence(confidence)

    assert math.isfinite(z)
    assert z > _z_for_confidence(0.999)


def test_mc_accepts_largest_representable_confidence() -> None:
    """Issue #33: MC dispatch with that confidence completes (Li 2011 Alg 1, p.5)."""
    result = compute_probabilistic_acceptance(
        _single_argument_praf(0.5),
        strategy="mc",
        mc_confidence=1.0 - 2.0**-53,
        mc_epsilon=0.2,
        rng_seed=1,
    )

    assert result.acceptance_probs is not None
    assert 0.0 < result.acceptance_probs["a"] < 1.0


@pytest.mark.parametrize(
    ("confidence", "expected"),
    [(0.5, 0.6744897502), (0.975, 2.2414027276), (0.999, 3.2905267315)],
)
def test_z_for_confidence_matches_normal_quantiles(
    confidence: float,
    expected: float,
) -> None:
    """Issue #33 control: ordinary confidences keep their two-tailed quantiles."""
    assert _z_for_confidence(confidence) == pytest.approx(expected, rel=1e-8)


def test_exact_enum_keeps_tiny_positive_probability_worlds() -> None:
    """Issue #34: exact acceptance sums P(AF) over every inducible world
    (Li 2011 Eq 2, p.4); the world {a} has probability 1e-16 and must count."""
    praf = _single_argument_praf(1e-16)

    acceptance = compute_probabilistic_acceptance(praf, strategy="exact_enum")
    extension = compute_probabilistic_acceptance(
        praf,
        strategy="exact_enum",
        query_kind="extension_probability",
        queried_set={"a"},
    )

    assert acceptance.acceptance_probs == {"a": 1e-16}
    assert extension.extension_probability == 1e-16


def test_defeat_marginal_keeps_tiny_positive_probability_worlds() -> None:
    """Issue #34: the exact defeat marginal is P(a)P(b)P_D((a,b)) (Li 2011, p.3-4)."""
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")})),
        {"a": 1e-8, "b": 1e-8},
        {("a", "b"): 1.0},
    )

    assert summarize_defeat_relations(praf) == {
        ("a", "b"): pytest.approx(1e-16, rel=1e-12)
    }


def test_exact_enum_ordinary_world_probabilities_control() -> None:
    """Issue #34 control: ordinary probabilities are unchanged."""
    result = compute_probabilistic_acceptance(
        _single_argument_praf(0.25),
        strategy="exact_enum",
    )

    assert result.acceptance_probs == {"a": 0.25}
