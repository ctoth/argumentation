"""Tests for argumentation-framework sensitivity / importance analysis.

The hand-constructed cases use a small framework whose expected
sensitivity value is checked by hand in the accompanying comments.
The property-based cases generate random small frameworks and base-score
maps with ``hypothesis`` and assert invariants that hold by construction.
"""

from __future__ import annotations

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

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


# ── Property-based tests ────────────────────────────────────────────
#
# Generators produce VALID inputs only: defeats range over declared
# arguments, base_scores covers exactly the arguments, support weights
# lie in [0, 1], and supports never overlap attacks. A property test
# that crashed on its own malformed input would prove nothing.

_PROP_SETTINGS = settings(deadline=None)


@st.composite
def frameworks(draw, max_args: int = 6):
    """Draw a small ArgumentationFramework over a..f with defeats on declared args."""
    args = draw(
        st.frozensets(
            st.text(alphabet="abcdef", min_size=1, max_size=2),
            min_size=1,
            max_size=max_args,
        )
    )
    arg_list = sorted(args)
    defeats = draw(
        st.frozensets(
            st.tuples(st.sampled_from(arg_list), st.sampled_from(arg_list)),
            max_size=len(arg_list) ** 2,
        )
    )
    return ArgumentationFramework(arguments=args, defeats=defeats)


@st.composite
def framework_with_scored_attacks(draw, max_args: int = 6):
    """Draw a framework, a base-score map covering exactly its arguments,
    in-range support weights over support edges disjoint from the defeats,
    and a candidate attack to remove.

    Returns ``(framework, supports, base_scores, attack)``. The candidate
    attack is a real defeat about half the time and a non-defeat the other
    half, so absent-attack and present-attack behaviour are both exercised.
    """
    framework = draw(frameworks(max_args=max_args))
    arg_list = sorted(framework.arguments)

    base_scores = {
        arg: draw(
            st.floats(
                min_value=0.0,
                max_value=1.0,
                allow_nan=False,
                allow_infinity=False,
            )
        )
        for arg in arg_list
    }

    all_pairs = [(s, t) for s in arg_list for t in arg_list]
    support_candidates = [p for p in all_pairs if p not in framework.defeats]
    support_edges = (
        draw(
            st.frozensets(
                st.sampled_from(support_candidates),
                max_size=len(support_candidates),
            )
        )
        if support_candidates
        else frozenset()
    )
    supports = {
        edge: draw(
            st.floats(
                min_value=0.0,
                max_value=1.0,
                allow_nan=False,
                allow_infinity=False,
            )
        )
        for edge in support_edges
    }

    defeat_list = sorted(framework.defeats)
    if defeat_list and draw(st.booleans()):
        attack = draw(st.sampled_from(defeat_list))
    else:
        attack = draw(st.sampled_from(all_pairs))

    return framework, supports, base_scores, attack


# ── score_conflict ──────────────────────────────────────────────────


class TestScoreConflictProperties:
    """Invariants of ``score_conflict`` that hold by construction."""

    pytestmark = pytest.mark.property

    @given(framework=frameworks(), data=st.data())
    @_PROP_SETTINGS
    def test_result_is_within_unit_interval(self, framework, data) -> None:
        """The returned swing score is always clamped into ``[0.0, 1.0]``."""
        arg_list = sorted(framework.arguments)
        claim_a = data.draw(st.sampled_from(arg_list))
        claim_b = data.draw(st.sampled_from(arg_list))
        score = score_conflict(framework, claim_a, claim_b)
        assert 0.0 <= score <= 1.0

    @given(framework=frameworks(), data=st.data())
    @_PROP_SETTINGS
    def test_symmetric_in_the_two_claim_arguments(self, framework, data) -> None:
        """``score_conflict(f, a, b) == score_conflict(f, b, a)``."""
        arg_list = sorted(framework.arguments)
        claim_a = data.draw(st.sampled_from(arg_list))
        claim_b = data.draw(st.sampled_from(arg_list))
        assert score_conflict(framework, claim_a, claim_b) == score_conflict(
            framework, claim_b, claim_a
        )

    @given(framework=frameworks(), data=st.data())
    @_PROP_SETTINGS
    def test_deterministic(self, framework, data) -> None:
        """Same inputs yield the same output on repeated calls."""
        arg_list = sorted(framework.arguments)
        claim_a = data.draw(st.sampled_from(arg_list))
        claim_b = data.draw(st.sampled_from(arg_list))
        first = score_conflict(framework, claim_a, claim_b)
        second = score_conflict(framework, claim_a, claim_b)
        assert first == second


# ── attack_removal_sensitivity ──────────────────────────────────────


class TestAttackRemovalSensitivityProperties:
    """Invariants of ``attack_removal_sensitivity``."""

    pytestmark = pytest.mark.property

    @given(framework_with_scored_attacks())
    @_PROP_SETTINGS
    def test_absent_attack_returns_exactly_zero(self, scenario) -> None:
        """An attack not in ``framework.defeats`` returns exactly ``0.0``."""
        framework, supports, base_scores, attack = scenario
        if attack not in framework.defeats:
            assert (
                attack_removal_sensitivity(framework, supports, base_scores, attack)
                == 0.0
            )

    @given(framework_with_scored_attacks())
    @_PROP_SETTINGS
    def test_delta_is_finite_and_bounded(self, scenario) -> None:
        """DF-QuAD strengths lie in ``[0, 1]``, so the delta lies in ``[-1, 1]``."""
        framework, supports, base_scores, attack = scenario
        delta = attack_removal_sensitivity(framework, supports, base_scores, attack)
        assert delta == delta  # not NaN
        assert -1.0 <= delta <= 1.0

    @given(framework_with_scored_attacks())
    @_PROP_SETTINGS
    def test_deterministic(self, scenario) -> None:
        """Same inputs yield the same delta on repeated calls."""
        framework, supports, base_scores, attack = scenario
        first = attack_removal_sensitivity(framework, supports, base_scores, attack)
        second = attack_removal_sensitivity(framework, supports, base_scores, attack)
        assert first == second

    @pytest.mark.xfail(
        reason=(
            "Plausible-but-unproven, and FALSIFIED by hypothesis: removing an "
            "attack should not DECREASE the target's DF-QuAD strength. The minimal "
            "counterexample is a SELF-ATTACK -- args {a, b}, defeats all four "
            "directed pairs, base {a: 0.5, b: 0.9375}, remove (a, a). The target "
            "of the removed attack is 'a' itself; 'a' is also attacked by 'b', so "
            "the DF-QuAD fixed point couples the two incoming attacks. Removing "
            "(a, a) shifts the joint fixed point and 'a' ends ~0.068 LOWER, not "
            "higher. The docstring's 'removing an attack normally raises the "
            "target' holds only in isolation; cyclic/coupled attacks flip the "
            "sign. See reports/argumentation-sensitivity-proptests.md."
        ),
        strict=True,
    )
    @given(framework_with_scored_attacks())
    @example(
        # The minimal counterexample hypothesis found, pinned so the xfail
        # is deterministic rather than dependent on the random search budget.
        scenario=(
            ArgumentationFramework(
                arguments=frozenset({"a", "b"}),
                defeats=frozenset({("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")}),
            ),
            {},
            {"a": 0.5, "b": 0.9375},
            ("a", "a"),
        ),
    )
    @_PROP_SETTINGS
    def test_removing_attack_does_not_decrease_target_strength(self, scenario) -> None:
        """Removing an attack should raise (not lower) the target's strength.

        This is the documented ``xfail``: the docstring of
        ``attack_removal_sensitivity`` says removing an attack "normally
        raises the target's strength", and the delta is
        ``strength_reduced - strength_full``. The conjecture under test is
        that the delta is therefore ``>= 0`` for every valid input.
        hypothesis falsifies it -- a self-attack on the target couples the
        target's incoming attacks through the DF-QuAD fixed point, and
        removing one can lower the target's strength.
        """
        framework, supports, base_scores, attack = scenario
        delta = attack_removal_sensitivity(framework, supports, base_scores, attack)
        assert delta >= -1e-9
