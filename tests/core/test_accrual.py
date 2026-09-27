from __future__ import annotations

import pytest

from argumentation.core.accrual import (
    AccrualArgument,
    accrual_envelope,
    accrual_grounded_labelling,
    strongly_applicable,
    weakly_applicable,
)
from argumentation.core.labelling import Label, Labelling


def _labelling(statuses: dict[str, Label]) -> Labelling:
    return Labelling.from_statuses(arguments=frozenset(statuses), statuses=statuses)


def test_weak_and_strong_applicability_follow_labelling_statuses() -> None:
    argument = AccrualArgument(
        identifier="a",
        conclusion="p",
        undercutters=frozenset({"u"}),
        immediate_subarguments=frozenset({"s"}),
    )

    weak_only = _labelling({"a": Label.UNDEC, "u": Label.UNDEC, "s": Label.IN})
    strong = _labelling({"a": Label.UNDEC, "u": Label.OUT, "s": Label.IN})
    blocked_by_undercutter = _labelling(
        {"a": Label.UNDEC, "u": Label.IN, "s": Label.IN}
    )
    blocked_by_subargument = _labelling(
        {"a": Label.UNDEC, "u": Label.OUT, "s": Label.OUT}
    )

    assert weakly_applicable(argument, weak_only)
    assert not strongly_applicable(argument, weak_only)
    assert strongly_applicable(argument, strong)
    assert not weakly_applicable(argument, blocked_by_undercutter)
    assert not weakly_applicable(argument, blocked_by_subargument)


def test_accrual_envelope_groups_same_conclusion_arguments_without_subset_blowup() -> (
    None
):
    a = AccrualArgument("a", "p")
    b = AccrualArgument("b", "p", undercutters=frozenset({"u"}))
    c = AccrualArgument("c", "q")
    labelling = _labelling(
        {
            "a": Label.UNDEC,
            "b": Label.UNDEC,
            "c": Label.UNDEC,
            "u": Label.UNDEC,
        }
    )

    envelope = accrual_envelope(
        frozenset({a, b, c}), conclusion="p", labelling=labelling
    )

    assert envelope.conclusion == "p"
    assert envelope.strongly_applicable == frozenset({"a"})
    assert envelope.weakly_applicable == frozenset({"a", "b"})
    assert envelope.minimal_required == frozenset({"a"})
    assert envelope.maximal_available == frozenset({"a", "b"})


def test_accrual_grounded_labelling_reaches_fixed_point() -> None:
    arguments = frozenset(
        {
            AccrualArgument("a", "p"),
            AccrualArgument("b", "p", immediate_subarguments=frozenset({"a"})),
            AccrualArgument("u", "not-p"),
            AccrualArgument("c", "p", undercutters=frozenset({"u"})),
        }
    )

    labelling = accrual_grounded_labelling(arguments)

    assert labelling.statuses["a"] is Label.IN
    assert labelling.statuses["b"] is Label.IN
    assert labelling.statuses["u"] is Label.IN
    assert labelling.statuses["c"] is Label.OUT


def test_grounded_labelling_rejects_conflicting_duplicate_identifiers() -> None:
    """Issue #37: one identifier cannot name two different arguments.

    Prakken 2019 (pp.2-3, 5-6) labels each argument of ``AF = (A, D)`` once;
    the characteristic function decides an argument from its own undercutters
    and immediate subarguments. Two different dependency sets under one label
    have no well-defined status, so the input is rejected rather than labelled
    by whichever object iteration order visits last.
    """
    arguments = frozenset(
        {
            AccrualArgument("a", "p"),
            AccrualArgument("a", "p", undercutters=frozenset({"a"})),
        }
    )

    with pytest.raises(ValueError, match="duplicate accrual argument identifier"):
        accrual_grounded_labelling(arguments)


def test_grounded_labelling_accepts_distinct_identifiers_with_same_shape() -> None:
    """Issue #37 control: the same two dependency shapes under distinct ids."""
    arguments = frozenset(
        {
            AccrualArgument("a", "p"),
            AccrualArgument("b", "p", undercutters=frozenset({"b"})),
        }
    )

    labelling = accrual_grounded_labelling(arguments)

    assert labelling.statuses["a"] is Label.IN
    assert labelling.statuses["b"] is Label.UNDEC
