from __future__ import annotations

from argumentation.adf import (
    AbstractDialecticalFramework,
    And,
    Atom,
    Not,
    ThreeValued,
    True_,
    grounded_interpretation,
    interpretation_from_mapping,
    is_complete,
)


def test_adf_grounded_matches_dung_style_attack_condition() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b"}),
        links=frozenset({("a", "b")}),
        acceptance_conditions={
            "a": True_(),
            "b": Not(Atom("a")),
        },
    )

    assert grounded_interpretation(framework) == interpretation_from_mapping(
        {"a": ThreeValued.T, "b": ThreeValued.F}
    )


def test_adf_grounded_keeps_unresolved_cycle_undefined() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b"}),
        links=frozenset({("a", "b"), ("b", "a")}),
        acceptance_conditions={
            "a": Not(Atom("b")),
            "b": Not(Atom("a")),
        },
    )

    grounded = grounded_interpretation(framework)

    assert grounded == interpretation_from_mapping(
        {"a": ThreeValued.U, "b": ThreeValued.U}
    )
    assert is_complete(framework, grounded)


def test_adf_gamma_respects_conjunctive_acceptance() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b", "c"}),
        links=frozenset({("a", "c"), ("b", "c")}),
        acceptance_conditions={
            "a": True_(),
            "b": True_(),
            "c": And((Atom("a"), Atom("b"))),
        },
    )

    assert grounded_interpretation(framework) == interpretation_from_mapping(
        {"a": ThreeValued.T, "b": ThreeValued.T, "c": ThreeValued.T}
    )
