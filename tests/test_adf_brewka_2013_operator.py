from __future__ import annotations

from argumentation.adf import (
    AbstractDialecticalFramework,
    Atom,
    Not,
    ThreeValued,
    True_,
    admissible_interpretations,
    complete_models,
    interpretation_from_mapping,
    is_admissible,
    is_complete,
    preferred_models,
    stable_models,
)


def test_operator_semantics_for_single_attack_adf() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b"}),
        links=frozenset({("a", "b")}),
        acceptance_conditions={
            "a": True_(),
            "b": Not(Atom("a")),
        },
    )
    model = interpretation_from_mapping({"a": ThreeValued.T, "b": ThreeValued.F})

    assert is_admissible(framework, model)
    assert is_complete(framework, model)
    assert model in admissible_interpretations(framework)
    assert complete_models(framework) == (model,)
    assert preferred_models(framework) == (model,)
    assert stable_models(framework) == (model,)


def test_preferred_models_keep_both_two_valued_models_of_mutual_attack() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b"}),
        links=frozenset({("a", "b"), ("b", "a")}),
        acceptance_conditions={
            "a": Not(Atom("b")),
            "b": Not(Atom("a")),
        },
    )

    assert preferred_models(framework) == (
        interpretation_from_mapping({"a": ThreeValued.F, "b": ThreeValued.T}),
        interpretation_from_mapping({"a": ThreeValued.T, "b": ThreeValued.F}),
    )
