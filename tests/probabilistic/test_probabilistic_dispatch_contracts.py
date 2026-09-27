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
from argumentation.probabilistic import probabilistic
from argumentation.probabilistic.probabilistic import (
    PrAFResult,
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


def _isolated_plus_self_attacker(p_b: float) -> ProbabilisticAF:
    return ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("b", "b")})),
        {"a": 1.0, "b": p_b},
        {},
    )


@pytest.mark.parametrize("inference_mode", ["credulous", "skeptical"])
@pytest.mark.parametrize("p_b", [1.0, 0.5])
def test_mc_stable_accounts_for_extension_nonexistence_elsewhere(
    p_b: float,
    inference_mode: str,
) -> None:
    """Issue #3: a stable extension must attack every outside argument (Dung
    1995, Def 13, p.328), so a present self-attacker b leaves the whole AF
    without stable extensions and a is not accepted; stable semantics can fail
    to exist, which breaks per-component composition (Baroni et al. 2005,
    p.167-168). Exact P(a) = P(b absent) = 1 - p_b (Li 2011 Eq 2, p.4)."""
    praf = _isolated_plus_self_attacker(p_b)

    result = compute_probabilistic_acceptance(
        praf,
        semantics="stable",
        strategy="mc",
        query_kind="argument_acceptance",
        inference_mode=inference_mode,
        rng_seed=1,
        mc_epsilon=0.02,
    )

    assert result.acceptance_probs is not None
    assert result.confidence_interval_half is not None
    expected = 1.0 - p_b
    assert abs(result.acceptance_probs["a"] - expected) <= max(
        result.confidence_interval_half, 1e-12
    )
    if p_b == 1.0:
        assert result.acceptance_probs == {"a": 0.0, "b": 0.0}


@pytest.mark.parametrize("inference_mode", ["credulous", "skeptical"])
def test_mc_grounded_component_decomposition_control(inference_mode: str) -> None:
    """Issue #3 control: grounded extensions always exist (Dung 1995, p.329),
    so the isolated argument a is accepted in every world."""
    result = compute_probabilistic_acceptance(
        _isolated_plus_self_attacker(0.5),
        semantics="grounded",
        strategy="mc",
        query_kind="argument_acceptance",
        inference_mode=inference_mode,
        rng_seed=1,
        mc_epsilon=0.02,
    )

    assert result.acceptance_probs is not None
    assert result.acceptance_probs["a"] == 1.0
    assert result.acceptance_probs["b"] == 0.0


def _dense_praf(n_args: int, p_defeat: float) -> ProbabilisticAF:
    arguments = frozenset(f"a{i:02d}" for i in range(n_args))
    defeats = frozenset(
        (source, target)
        for source in arguments
        for target in arguments
        if source != target
    )
    return ProbabilisticAF(
        ArgumentationFramework(arguments, defeats),
        {argument: 0.9 for argument in arguments},
        {defeat: p_defeat for defeat in defeats},
    )


def _sentinel_result(strategy: str) -> PrAFResult:
    return PrAFResult(acceptance_probs={}, strategy_used=strategy)


def test_auto_route_skips_exact_enumeration_for_relation_world_explosion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Issue #2: exact enumeration costs O(2^(|A|+|D|)) (Li 2011, p.3-4), and
    the ~13-argument crossover (p.8) was measured with deterministic defeats.
    13 arguments with all 156 directed defeats uncertain is a 2^169 world
    space, so auto must not enter exact enumeration. Backends are sentinels:
    this contract never runs the exponential search."""
    praf = _dense_praf(13, 0.5)
    assert probabilistic._exact_enumeration_world_exponent(praf) == 13 + 156

    def exact_enumeration_forbidden(*args: object, **kwargs: object) -> PrAFResult:
        raise AssertionError("auto routed a 2^169 world space to exact enumeration")

    monkeypatch.setattr(
        probabilistic, "_compute_exact_enumeration", exact_enumeration_forbidden
    )
    monkeypatch.setattr(
        probabilistic,
        "_compute_exact_dp",
        lambda *args, **kwargs: _sentinel_result("exact_dp"),
    )
    monkeypatch.setattr(
        probabilistic,
        "_compute_mc",
        lambda *args, **kwargs: _sentinel_result("mc"),
    )

    for semantics in ("grounded", "preferred", "stable", "complete"):
        result = compute_probabilistic_acceptance(praf, semantics=semantics)
        assert result.strategy_used in {"exact_dp", "mc"}


def test_auto_route_keeps_exact_enumeration_for_small_world_space() -> None:
    """Issue #2 control: 3 arguments and 6 uncertain defeats is a 2^9 world
    space, which stays on exact enumeration (Li 2011, p.8)."""
    praf = _dense_praf(3, 0.5)
    assert probabilistic._exact_enumeration_world_exponent(praf) == 9

    auto = compute_probabilistic_acceptance(praf)
    exact = compute_probabilistic_acceptance(praf, strategy="exact_enum")

    assert auto.strategy_used == "exact_enum"
    assert auto.acceptance_probs == exact.acceptance_probs


def test_world_exponent_ignores_deterministic_relations() -> None:
    """Issue #2 control: relations without a probability are fixed in every
    enumerated world, so only arguments contribute to the exponent."""
    praf = ProbabilisticAF(
        ArgumentationFramework(
            frozenset({"a", "b", "c"}), frozenset({("a", "b"), ("b", "c")})
        ),
        {"a": 0.5, "b": 0.5, "c": 0.5},
        {},
    )

    assert probabilistic._exact_enumeration_world_exponent(praf) == 3


def _exact_methods_agree(praf: ProbabilisticAF) -> dict[str, float]:
    enumerated = compute_probabilistic_acceptance(praf, strategy="exact_enum")
    dynamic = compute_probabilistic_acceptance(praf, strategy="exact_dp")
    assert enumerated.acceptance_probs is not None
    assert dynamic.acceptance_probs is not None
    assert dynamic.acceptance_probs == pytest.approx(enumerated.acceptance_probs)
    return dynamic.acceptance_probs


def test_exact_dp_treats_missing_defeat_probability_as_certain() -> None:
    """Issue #50: a defeat without a P_D entry is present in every induced
    world, as in exact enumeration; both exact methods compute Li 2011
    Eq 2 (p.4), so with P(a) = 0.5, b is grounded-accepted iff a is absent."""
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")})),
        {"a": 0.5, "b": 1.0},
        {},
    )

    assert _exact_methods_agree(praf) == pytest.approx({"a": 0.5, "b": 0.5})


def test_exact_dp_explicit_defeat_probability_control() -> None:
    """Issue #50 control: an explicit P_D((a,b)) = 0.5 (Li 2011 Def 2, p.2)."""
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")})),
        {"a": 1.0, "b": 1.0},
        {("a", "b"): 0.5},
    )

    assert _exact_methods_agree(praf) == pytest.approx({"a": 1.0, "b": 0.5})


@pytest.mark.parametrize(
    ("p_attack", "expected_b"),
    [(0.0, 1.0), (0.25, 0.75)],
)
def test_exact_dp_honors_explicit_attack_probability(
    p_attack: float,
    expected_b: float,
) -> None:
    """Issue #51: an explicit primitive attack probability takes precedence
    over the direct-defeat probability in the induced-world distribution
    (Li 2011 p.3-4), so both exact methods must use it."""
    edge = ("a", "b")
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({edge})),
        {"a": 1.0, "b": 1.0},
        {edge: 1.0},
        p_attacks={edge: p_attack},
    )

    assert _exact_methods_agree(praf) == pytest.approx({"a": 1.0, "b": expected_b})


def test_exact_dp_rejects_defeats_outside_base_defeats() -> None:
    """Issue #51: when base_defeats narrows the direct defeats, world
    enumeration realizes only those defeats (Li 2011 Def 3, p.2), which the
    DP does not model; the route guard must reject that representation."""
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")})),
        {"a": 1.0, "b": 1.0},
        {},
        base_defeats=frozenset(),
    )

    with pytest.raises(ValueError, match="exact_dp only supports"):
        compute_probabilistic_acceptance(praf, strategy="exact_dp")
