"""Regression contracts for PrAF dispatch, routing, and result honesty.

Semantics follow Li, Oren & Norman (2011), "Probabilistic Argumentation
Frameworks" (papers/Li_2011_ProbabilisticArgumentationFrameworks/notes.md):
a PrAF induces a distribution over sub-frameworks (Def 3, p.2) whose world
probability is the product over present/absent arguments and defeats
(p.3-4), and acceptance marginalizes over all inducible worlds (Eq 2, p.4).
"""

from __future__ import annotations

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.probabilistic.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
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
