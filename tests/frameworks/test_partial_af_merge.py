"""Tests for exact merge operators over tiny argumentation frameworks."""

from __future__ import annotations

from itertools import product

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from argumentation.core.dung import ArgumentationFramework
from argumentation.frameworks.af_merging import (
    leximax_merge_frameworks,
    max_merge_frameworks,
    sum_merge_frameworks,
)
from argumentation.frameworks.partial_af import (
    EnumerationExceeded,
    consensual_expand,
    merge_framework_edit_distance,
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


def test_consensual_expand_matches_example_14_first_source():
    """Coste-Marquis et al. 2007, pp. 737–738: AF1 imports b->c and c->d."""
    profile = {
        "AF1": _af({"a", "b"}, {("a", "b"), ("b", "a")}),
        "AF2": _af({"b", "c", "d"}, {("b", "c"), ("c", "d")}),
        "AF3": _af({"a", "b", "d"}, {("a", "b"), ("a", "d")}),
        "AF4": _af({"a", "b", "d"}, {("b", "d"), ("b", "a")}),
    }

    expanded = consensual_expand(profile["AF1"], profile)

    assert expanded.arguments == frozenset({"a", "b", "c", "d"})
    assert expanded.attacks == frozenset(
        {("a", "b"), ("b", "a"), ("b", "c"), ("c", "d")}
    )
    assert expanded.ignorance == frozenset({("a", "d"), ("b", "d")})
    assert ("a", "c") in expanded.non_attacks  # No agent knows both endpoints.


def test_consensual_expand_retains_source_scope_outside_profile():
    """Definition 12 uses A union union(A_i), preserving a source outside P."""
    af = _af({"A", "B"}, {("A", "B")})
    profile = {"other": _af({"C"}, {("C", "C")})}

    expanded = consensual_expand(af, profile)

    assert expanded.arguments == frozenset({"A", "B", "C"})
    assert expanded.attacks == frozenset({("A", "B"), ("C", "C")})
    assert expanded.ignorance == frozenset()
    assert {("A", "A"), ("B", "A"), ("B", "B"), ("A", "C")} <= expanded.non_attacks


def test_consensual_expand_keeps_conflicting_outside_pairs_ignorant():
    """Example 14's AF2 retains b->c/c->d and is ignorant about a->b/b->a/a->d."""
    profile = {
        "AF1": _af({"a", "b"}, {("a", "b"), ("b", "a")}),
        "AF2": _af({"b", "c", "d"}, {("b", "c"), ("c", "d")}),
        "AF3": _af({"a", "b", "d"}, {("a", "b"), ("a", "d")}),
        "AF4": _af({"a", "b", "d"}, {("b", "d"), ("b", "a")}),
    }

    expanded = consensual_expand(profile["AF2"], profile)

    assert expanded.attacks == frozenset({("b", "c"), ("c", "d")})
    assert expanded.ignorance == frozenset({("a", "b"), ("b", "a"), ("a", "d")})
    assert ("b", "d") in expanded.non_attacks  # AF2's own non-attack is preserved.


def test_edit_distance_to_own_expansion_uses_pre_preference_attacks():
    """Coste-Marquis et al. 2007, Def. 15/18 (p.8-9): ``d(x, y) = 0`` iff
    ``x = y``. An AF whose attack ``A -> B`` was filtered from its defeats must
    read the same attack relation as its same-universe consensual expansion."""
    af = ArgumentationFramework(
        arguments=frozenset({"A", "B"}),
        defeats=frozenset(),
        attacks=frozenset({("A", "B")}),
    )

    expanded = consensual_expand(af, {"source": af})

    assert merge_framework_edit_distance(af, expanded) == 0


def test_edit_distance_counts_attack_versus_non_attack_pairs():
    """Control: Def. 18 counts one pair labelled attack vs non-attack."""
    left = _af({"A", "B"}, {("A", "B")})
    right = _af({"A", "B"}, set())

    assert merge_framework_edit_distance(left, right) == 1
    expanded = consensual_expand(left, {"source": left})
    assert merge_framework_edit_distance(left, expanded) == 0


def test_consensual_expand_on_shared_universe_introduces_no_ignorance():
    af = _af({"A", "B"}, {("A", "B")})

    expanded = consensual_expand(
        af, {"source": af, "contrary": _af({"A", "B"}, set())}
    )

    assert expanded.ignorance == frozenset()
    assert expanded.attacks == frozenset({("A", "B")})
    assert expanded.non_attacks == frozenset({("A", "A"), ("B", "A"), ("B", "B")})


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


def test_sum_merge_strict_bipartition_profile_bypasses_candidate_ceiling():
    arguments = {f"A{index}" for index in range(6)}
    majority_attacks = {("A0", "A1"), ("A2", "A3"), ("A4", "A5")}
    profile = {
        "left": _af(arguments, majority_attacks),
        "middle": _af(arguments, majority_attacks),
        "right": _af(arguments, set()),
    }

    result = sum_merge_frameworks(profile, max_candidates=1)

    assert result == [_af(arguments, majority_attacks)]


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
