from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

import pytest

import argumentation
from argumentation.practical_reasoning import (
    ActionBasedAlternatingTransitionSystem,
    PracticalArgument,
    critical_question_objections,
)


def test_practical_reasoning_module_is_exported() -> None:
    assert argumentation.practical_reasoning.PracticalArgument is PracticalArgument
    assert "practical_reasoning" in argumentation.__all__


def _toy_aats() -> ActionBasedAlternatingTransitionSystem:
    return ActionBasedAlternatingTransitionSystem(
        states=frozenset({"q0", "q1", "q2", "q3"}),
        initial_state="q0",
        agents=frozenset({"farmer"}),
        actions=frozenset({"row_seeds", "row_chicken", "row_dog", "row_alone"}),
        preconditions={
            "row_seeds": frozenset({"q0"}),
            "row_chicken": frozenset({"q0"}),
            "row_dog": frozenset({"q0"}),
            "row_alone": frozenset({"q0"}),
        },
        transitions={
            ("q0", "row_seeds"): "q1",
            ("q0", "row_chicken"): "q1",
            ("q0", "row_dog"): "q2",
            ("q0", "row_alone"): "q3",
        },
        propositions=frozenset({"seeds_right", "chicken_right", "dog_right"}),
        interpretation={
            "q0": frozenset(),
            "q1": frozenset({"seeds_right"}),
            "q2": frozenset({"dog_right"}),
            "q3": frozenset(),
        },
        values=frozenset({"progress", "friendship"}),
        valuation={
            ("q0", "q1", "progress"): "+",
            ("q0", "q2", "friendship"): "+",
            ("q0", "q3", "progress"): "=",
        },
    )


def test_cq5_finds_alternative_action_with_same_consequences() -> None:
    # Atkinson & Bench-Capon 2007 p. 862, CQ5: another joint action reaches qy.
    arg = PracticalArgument(
        agent="farmer",
        current_state="q0",
        action="row_seeds",
        resulting_state="q1",
        goal="seeds_right",
        promoted_value="progress",
    )

    objections = critical_question_objections(_toy_aats(), arg, "CQ5")

    assert {objection.alternative_action for objection in objections} == {"row_chicken"}


def test_cq6_finds_alternative_action_realising_same_goal() -> None:
    # Atkinson & Bench-Capon 2007 p. 862, CQ6: another joint action realises
    # the same goal proposition change.
    aats = ActionBasedAlternatingTransitionSystem(
        states=frozenset({"q0", "q1", "q2"}),
        initial_state="q0",
        agents=frozenset({"farmer"}),
        actions=frozenset({"row_seeds", "throw_seeds"}),
        preconditions={"row_seeds": frozenset({"q0"}), "throw_seeds": frozenset({"q0"})},
        transitions={("q0", "row_seeds"): "q1", ("q0", "throw_seeds"): "q2"},
        propositions=frozenset({"seeds_right"}),
        interpretation={
            "q0": frozenset(),
            "q1": frozenset({"seeds_right"}),
            "q2": frozenset({"seeds_right"}),
        },
        values=frozenset({"progress"}),
        valuation={
            ("q0", "q1", "progress"): "+",
            ("q0", "q2", "progress"): "+",
        },
    )
    arg = PracticalArgument("farmer", "q0", "row_seeds", "q1", "seeds_right", "progress")

    objections = critical_question_objections(aats, arg, "CQ6")

    assert {objection.alternative_action for objection in objections} == {"throw_seeds"}


def test_cq11_finds_precluded_action_that_promotes_different_value() -> None:
    # Atkinson & Bench-Capon 2007 p. 862, CQ11: proposed action promotes one
    # value while a different available action promotes another value.
    arg = PracticalArgument(
        agent="farmer",
        current_state="q0",
        action="row_seeds",
        resulting_state="q1",
        goal="seeds_right",
        promoted_value="progress",
    )

    objections = critical_question_objections(_toy_aats(), arg, "CQ11")

    assert [(obj.alternative_action, obj.promoted_value) for obj in objections] == [
        ("row_dog", "friendship")
    ]


def test_unsupported_critical_question_is_rejected() -> None:
    arg = PracticalArgument("farmer", "q0", "row_seeds", "q1", "seeds_right", "progress")

    with pytest.raises(NotImplementedError, match="CQ4"):
        critical_question_objections(_toy_aats(), arg, "CQ4")


@given(
    proposed_value=st.sampled_from(("v0", "v1")),
    alternative_value=st.sampled_from(("v0", "v1")),
)
def test_generated_cq11_only_reports_different_promoted_values(
    proposed_value: str,
    alternative_value: str,
) -> None:
    aats = ActionBasedAlternatingTransitionSystem(
        states=frozenset({"q0", "q1", "q2"}),
        initial_state="q0",
        agents=frozenset({"agent"}),
        actions=frozenset({"proposed", "alternative"}),
        preconditions={"proposed": frozenset({"q0"}), "alternative": frozenset({"q0"})},
        transitions={("q0", "proposed"): "q1", ("q0", "alternative"): "q2"},
        propositions=frozenset({"goal"}),
        interpretation={"q0": frozenset(), "q1": frozenset({"goal"}), "q2": frozenset()},
        values=frozenset({"v0", "v1"}),
        valuation={
            ("q0", "q1", proposed_value): "+",
            ("q0", "q2", alternative_value): "+",
        },
    )
    arg = PracticalArgument("agent", "q0", "proposed", "q1", "goal", proposed_value)

    objections = critical_question_objections(aats, arg, "CQ11")

    assert bool(objections) is (proposed_value != alternative_value)
