"""Tests for exact merge operators over tiny argumentation frameworks."""

from __future__ import annotations

from itertools import product

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from argumentation.dung import ArgumentationFramework
from argumentation.partial_af import (
    EnumerationExceeded,
    consensual_expand,
    leximax_merge_frameworks,
    max_merge_frameworks,
    sum_merge_frameworks,
)


PAIR_SPACE = [("A", "A"), ("A", "B"), ("B", "A"), ("B", "B")]
st_attack_pairs = st.sets(st.sampled_from(PAIR_SPACE), max_size=len(PAIR_SPACE))
ALL_ATTACK_SETS = [
    set(pair for pair, enabled in zip(PAIR_SPACE, mask, strict=True) if enabled)
    for mask in product([False, True], repeat=len(PAIR_SPACE))
]


def _af(arguments: set[str], attacks: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(attacks),
        attacks=frozenset(attacks),
    )


def test_consensual_expand_preserves_in_scope_pairs_and_marks_out_of_scope_as_ignorance():
    af = _af({"A"}, {("A", "A")})

    expanded = consensual_expand(af, frozenset({"A", "B"}))

    assert ("A", "A") in expanded.attacks
    assert ("A", "B") in expanded.ignorance
    assert ("B", "A") in expanded.ignorance
    assert ("B", "B") in expanded.ignorance


def test_consensual_expand_on_shared_universe_introduces_no_ignorance():
    af = _af({"A", "B"}, {("A", "B")})

    expanded = consensual_expand(af, frozenset({"A", "B"}))

    assert expanded.ignorance == frozenset()
    assert expanded.attacks == frozenset({("A", "B")})
    assert expanded.non_attacks == frozenset(
        {("A", "A"), ("B", "A"), ("B", "B")}
    )


@settings(
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(attacks=st_attack_pairs)
def test_sum_merge_unanimity(attacks: set[tuple[str, str]]):
    framework = _af({"A", "B"}, attacks)

    result = sum_merge_frameworks({"left": framework, "right": framework})

    assert result == [framework]


def test_concordant_profiles_yield_unique_result_for_all_operators():
    framework = _af({"A", "B"}, {("A", "B"), ("B", "A")})
    profile = {"left": framework, "right": framework, "third": framework}

    assert sum_merge_frameworks(profile) == [framework]
    assert max_merge_frameworks(profile) == [framework]
    assert leximax_merge_frameworks(profile) == [framework]


@settings(
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(left_attacks=st_attack_pairs, right_attacks=st_attack_pairs)
def test_sum_merge_profile_order_invariant(
    left_attacks: set[tuple[str, str]],
    right_attacks: set[tuple[str, str]],
):
    left = _af({"A", "B"}, left_attacks)
    right = _af({"A", "B"}, right_attacks)

    forward = sum_merge_frameworks({"left": left, "right": right})
    reverse = sum_merge_frameworks({"right": right, "left": left})

    assert forward == reverse


def test_sum_merge_matches_majority_profile_on_shared_universe():
    left = _af({"A", "B"}, {("A", "B")})
    middle = _af({"A", "B"}, {("A", "B")})
    right = _af({"A", "B"}, set())

    result = sum_merge_frameworks({"left": left, "middle": middle, "right": right})

    assert result == [_af({"A", "B"}, {("A", "B")})]


def test_sum_merge_returns_enumeration_exceeded_past_candidate_ceiling():
    profile = {
        "left": _af({"A", "B"}, {("A", "B")}),
        "right": _af({"A", "B"}, {("B", "A")}),
    }

    result = sum_merge_frameworks(profile, max_candidates=1)

    assert isinstance(result, EnumerationExceeded)
    assert result.partial_count == 1
    assert result.max_candidates == 1
    assert result.remainder_provenance == "vacuous"


@settings(
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(left_attacks=st_attack_pairs, right_attacks=st_attack_pairs)
def test_max_merge_profile_order_invariant(
    left_attacks: set[tuple[str, str]],
    right_attacks: set[tuple[str, str]],
):
    left = _af({"A", "B"}, left_attacks)
    right = _af({"A", "B"}, right_attacks)

    forward = max_merge_frameworks({"left": left, "right": right})
    reverse = max_merge_frameworks({"right": right, "left": left})

    assert forward == reverse


def test_max_merge_returns_enumeration_exceeded_past_candidate_ceiling():
    profile = {
        "left": _af({"A", "B"}, {("A", "B")}),
        "right": _af({"A", "B"}, {("B", "A")}),
    }

    result = max_merge_frameworks(profile, max_candidates=1)

    assert isinstance(result, EnumerationExceeded)
    assert result.partial_count == 1
    assert result.max_candidates == 1
    assert result.remainder_provenance == "vacuous"


def test_leximax_refines_max_results():
    left = _af({"A", "B"}, {("A", "B")})
    middle = _af({"A", "B"}, {("B", "A")})
    right = _af({"A", "B"}, set())

    max_results = max_merge_frameworks({"left": left, "middle": middle, "right": right})
    leximax_results = leximax_merge_frameworks(
        {"left": left, "middle": middle, "right": right}
    )

    assert leximax_results
    assert set(leximax_results).issubset(set(max_results))


def test_leximax_merge_returns_enumeration_exceeded_past_candidate_ceiling():
    profile = {
        "left": _af({"A", "B"}, {("A", "B")}),
        "right": _af({"A", "B"}, {("B", "A")}),
    }

    result = leximax_merge_frameworks(profile, max_candidates=1)

    assert isinstance(result, EnumerationExceeded)
    assert result.partial_count == 1
    assert result.max_candidates == 1
    assert result.remainder_provenance == "vacuous"


def test_sum_and_max_diverge_on_tiny_exact_profile():
    found = None
    for left_attacks in ALL_ATTACK_SETS:
        for middle_attacks in ALL_ATTACK_SETS:
            for right_attacks in ALL_ATTACK_SETS:
                profile = {
                    "left": _af({"A", "B"}, left_attacks),
                    "middle": _af({"A", "B"}, middle_attacks),
                    "right": _af({"A", "B"}, right_attacks),
                }
                sum_results = sum_merge_frameworks(profile)
                max_results = max_merge_frameworks(profile)
                if set(sum_results) != set(max_results):
                    found = (profile, sum_results, max_results)
                    break
            if found is not None:
                break
        if found is not None:
            break

    assert found is not None
    _profile, sum_results, max_results = found
    assert set(sum_results) != set(max_results)


def test_leximax_strictly_refines_a_multi_result_max_profile():
    found = None
    for left_attacks in ALL_ATTACK_SETS:
        for middle_attacks in ALL_ATTACK_SETS:
            for right_attacks in ALL_ATTACK_SETS:
                profile = {
                    "left": _af({"A", "B"}, left_attacks),
                    "middle": _af({"A", "B"}, middle_attacks),
                    "right": _af({"A", "B"}, right_attacks),
                }
                max_results = max_merge_frameworks(profile)
                leximax_results = leximax_merge_frameworks(profile)
                if len(max_results) > 1 and set(leximax_results) < set(max_results):
                    found = (profile, max_results, leximax_results)
                    break
            if found is not None:
                break
        if found is not None:
            break

    assert found is not None
    _profile, max_results, leximax_results = found
    assert set(leximax_results) < set(max_results)
