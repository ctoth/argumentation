from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.dynamics.approximate import (
    approximate_grounded,
    approximate_semi_stable,
    k_stable_extensions,
)
from argumentation.core.dung import (
    ArgumentationFramework,
    range_of,
    semi_stable_extensions,
    stable_extensions,
)


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_maximum_k_stable_extensions_match_stable_semantics() -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})

    assert set(k_stable_extensions(framework, k=2)) == set(stable_extensions(framework))


def test_k_stable_uses_minimum_range_size() -> None:
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "c"), ("c", "a")})

    assert set(k_stable_extensions(framework, k=2)) == {
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"c"}),
    }
    assert set(k_stable_extensions(framework, k=0)) == {
        frozenset(),
        frozenset({"a"}),
        frozenset({"b"}),
        frozenset({"c"}),
    }


def test_bounded_grounded_iterations_are_monotone_prefixes() -> None:
    framework = af({"a", "b", "c", "d"}, {("a", "b"), ("b", "c"), ("c", "d")})

    one = approximate_grounded(framework, k_iterations=1)
    two = approximate_grounded(framework, k_iterations=2)

    assert one.extension == frozenset({"a"})
    assert two.extension == frozenset({"a", "c"})
    assert one.extension <= two.extension
    assert two.exact is True


def test_approximate_semi_stable_exact_budget_matches_reference() -> None:
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "c"), ("c", "a")})

    result = approximate_semi_stable(framework, max_candidates=None)

    assert result.exact is True
    assert set(result.extensions) == set(semi_stable_extensions(framework))


def test_approximate_semi_stable_limited_budget_reports_inexact_witnesses() -> None:
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "c"), ("c", "a")})

    result = approximate_semi_stable(framework, max_candidates=2)

    assert result.exact is False
    assert result.examined_candidates == 2
    assert result.extensions


ARGUMENTS = ("a", "b", "c")
PAIRS = tuple((left, right) for left in ARGUMENTS for right in ARGUMENTS)


@st.composite
def st_mixed_framework(draw) -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset(ARGUMENTS),
        defeats=frozenset(draw(st.sets(st.sampled_from(PAIRS), max_size=5))),
        attacks=frozenset(draw(st.sets(st.sampled_from(PAIRS), max_size=5))),
    )


def test_exhaustive_bounded_semi_stable_respects_attacks() -> None:
    """Issue #19: an exhausted budget must return the exact answer.

    Conflict-freeness is checked against the pre-preference attacks
    (Modgil & Prakken 2018, Definition 14), exactly as the reference
    ``semi_stable_extensions`` does (Caminada 2011, Definition 2.3), so the
    conflicting set {a, b} is not a semi-stable extension.
    """
    framework = ArgumentationFramework(
        frozenset({"a", "b"}), frozenset(), frozenset({("a", "b")})
    )

    bounded = approximate_semi_stable(framework, max_candidates=4)
    unbounded = approximate_semi_stable(framework, max_candidates=None)

    assert bounded.exact is True
    assert frozenset({"a", "b"}) not in bounded.extensions
    assert set(bounded.extensions) == set(unbounded.extensions)


def test_exhaustive_bounded_semi_stable_matches_reference_without_attacks() -> None:
    """Issue #19 control: the same framework with no separate attack layer."""
    framework = af({"a", "b"}, set())

    bounded = approximate_semi_stable(framework, max_candidates=4)

    assert bounded.exact is True
    assert set(bounded.extensions) == set(semi_stable_extensions(framework))


def test_k_stable_uses_one_conflict_policy_for_every_k() -> None:
    """Issue #19: k-stable must not switch relation policy at k = |A|.

    Stable semantics checks conflict-freeness against attacks (Modgil &
    Prakken 2018, Definition 14), so the k < |A| candidates must too.
    """
    framework = ArgumentationFramework(
        frozenset({"a", "b"}), frozenset(), frozenset({("a", "b")})
    )

    assert set(k_stable_extensions(framework, k=1)) == {
        frozenset({"a"}),
        frozenset({"b"}),
    }


@given(st_mixed_framework())
@settings(deadline=None)
def test_exhaustive_bounded_semi_stable_matches_reference(
    framework: ArgumentationFramework,
) -> None:
    """Issue #19: exact=True means the reference semi-stable extensions."""
    bounded = approximate_semi_stable(framework, max_candidates=2 ** len(ARGUMENTS))

    assert bounded.exact is True
    assert set(bounded.extensions) == set(semi_stable_extensions(framework))


@given(st_mixed_framework())
@settings(deadline=None)
def test_k_stable_is_a_range_filter_of_zero_stable(
    framework: ArgumentationFramework,
) -> None:
    """Issue #19: every k filters the same conflict-free candidates by range."""
    zero_stable = k_stable_extensions(framework, k=0)
    for k in range(len(ARGUMENTS) + 1):
        assert set(k_stable_extensions(framework, k=k)) == {
            candidate
            for candidate in zero_stable
            if len(range_of(candidate, framework.defeats)) >= k
        }
    assert set(k_stable_extensions(framework, k=len(ARGUMENTS))) == set(
        stable_extensions(framework)
    )
