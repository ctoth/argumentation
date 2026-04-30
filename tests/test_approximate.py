from __future__ import annotations

from argumentation.approximate import (
    approximate_grounded,
    approximate_semi_stable,
    k_stable_extensions,
)
from argumentation.dung import ArgumentationFramework, semi_stable_extensions, stable_extensions


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_k_zero_stable_extensions_match_stable_semantics() -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})

    assert set(k_stable_extensions(framework, k=0)) == set(stable_extensions(framework))


def test_k_stable_allows_bounded_uncovered_outsiders() -> None:
    framework = af({"a", "b", "c"}, {("a", "b"), ("b", "c"), ("c", "a")})

    assert set(k_stable_extensions(framework, k=1)) == {
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
