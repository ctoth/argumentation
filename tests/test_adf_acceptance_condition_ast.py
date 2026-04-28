from __future__ import annotations

import argumentation

from argumentation.adf import (
    AbstractDialecticalFramework,
    And,
    Atom,
    False_,
    LinkType,
    Not,
    Or,
    ThreeValued,
    True_,
    classify_link,
    from_json,
    parse_iccma_formula,
    to_json,
    write_iccma_formula,
)


def test_adf_module_is_exported() -> None:
    assert "adf" in argumentation.__all__


def test_acceptance_condition_ast_json_and_iccma_round_trip() -> None:
    condition = And((Atom("a"), Not(Atom("b")), Or((Atom("c"), False_()))))

    assert from_json(to_json(condition)) == condition
    assert parse_iccma_formula(write_iccma_formula(condition)) == condition


def test_acceptance_condition_ast_canonicalizes_without_callable_path() -> None:
    assert And(()) == True_()
    assert Or(()) == False_()
    assert Not(Not(Atom("a"))) == Atom("a")
    assert And((Atom("b"), Atom("a"))) == And((Atom("a"), Atom("b")))
    assert not hasattr(Atom, "from_callable")
    assert "__call__" not in Atom.__dict__


def test_adf_dataclass_validates_parents_and_conditions() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b", "c"}),
        links=frozenset({("a", "c"), ("b", "c")}),
        acceptance_conditions={
            "a": True_(),
            "b": False_(),
            "c": And((Atom("a"), Not(Atom("b")))),
        },
    )

    assert framework.parents("c") == frozenset({"a", "b"})


def test_structural_link_classifier_uses_ast_shape() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b", "c"}),
        links=frozenset({("a", "c"), ("b", "c")}),
        acceptance_conditions={
            "a": True_(),
            "b": True_(),
            "c": And((Atom("a"), Not(Atom("b")))),
        },
    )

    assert classify_link(framework, "a", "c") is LinkType.SUPPORTING
    assert classify_link(framework, "b", "c") is LinkType.ATTACKING
    assert classify_link(framework, "a", "b") is LinkType.NEITHER


def test_three_valued_interpretation_values_are_exported() -> None:
    assert {ThreeValued.T.value, ThreeValued.F.value, ThreeValued.U.value} == {"t", "f", "u"}
