from __future__ import annotations

from itertools import product
from typing import Mapping

from hypothesis import given
from hypothesis import strategies as st

from argumentation.frameworks.adf import (
    AcceptanceCondition,
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
)
from argumentation.frameworks.adf_io import (
    from_json,
    parse_iccma_formula,
    to_json,
    write_iccma_formula,
)


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


def test_semantic_link_classifier_uses_acceptance_behavior() -> None:
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
    assert classify_link(framework, "a", "b") is LinkType.UNDEFINED


def test_semantic_link_classifier_ignores_cancelled_syntax_occurrences() -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "c"}),
        links=frozenset({("a", "c")}),
        acceptance_conditions={
            "a": True_(),
            "c": Or((Atom("a"), And((Atom("a"), Not(Atom("a")))))),
        },
    )

    assert classify_link(framework, "a", "c") is LinkType.SUPPORTING


def test_semantic_link_classifier_covers_all_four_behavioral_classes() -> None:
    conditions = {
        "support": Atom("p"),
        "attack": Not(Atom("p")),
        "both": Atom("q"),
        "neither": Or(
            (
                And((Atom("p"), Atom("q"))),
                And((Not(Atom("p")), Atom("r"))),
            )
        ),
    }

    for child, condition in conditions.items():
        framework = AbstractDialecticalFramework(
            statements=frozenset({"p", "q", "r", child}),
            links=frozenset({("p", child), ("q", child), ("r", child)}),
            acceptance_conditions={
                "p": True_(),
                "q": True_(),
                "r": True_(),
                child: condition,
            },
        )
        expected = {
            "support": LinkType.SUPPORTING,
            "attack": LinkType.ATTACKING,
            "both": LinkType.BOTH,
            "neither": LinkType.NEITHER,
        }[child]
        assert classify_link(framework, "p", child) is expected


class _CountingCondition(AcceptanceCondition):
    def __init__(self, condition: AcceptanceCondition) -> None:
        self.condition = condition
        self.calls = 0

    def atoms(self) -> frozenset[str]:
        return self.condition.atoms()

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        self.calls += 1
        return self.condition.evaluate(assignment)


def test_semantic_link_classifier_evaluates_each_assignment_pair_once() -> None:
    condition = _CountingCondition(Or((And((Atom("p"), Atom("q"))), Not(Atom("r")))))
    framework = AbstractDialecticalFramework(
        statements=frozenset({"p", "q", "r", "c"}),
        links=frozenset({("p", "c"), ("q", "c"), ("r", "c")}),
        acceptance_conditions={
            "p": True_(),
            "q": True_(),
            "r": True_(),
            "c": condition,
        },
    )

    classify_link(framework, "p", "c")

    assert condition.calls == 2 * 2 ** (len(framework.parents("c")) - 1)


def _conditions() -> st.SearchStrategy[AcceptanceCondition]:
    atoms = st.sampled_from(("p", "q", "r")).map(Atom)
    leaves = st.one_of(atoms, st.just(True_()), st.just(False_()))
    return st.recursive(
        leaves,
        lambda children: st.one_of(
            children.map(Not),
            st.lists(children, max_size=3).map(lambda values: And(tuple(values))),
            st.lists(children, max_size=3).map(lambda values: Or(tuple(values))),
        ),
        max_leaves=8,
    )


def _semantic_link_oracle(
    framework: AbstractDialecticalFramework,
    parent: str,
    child: str,
) -> LinkType:
    if (parent, child) not in framework.links:
        return LinkType.UNDEFINED
    condition = framework.acceptance_conditions[child]
    other_parents = sorted(framework.parents(child) - {parent})
    supporting = True
    attacking = True
    for values in product((False, True), repeat=len(other_parents)):
        assignment = dict(zip(other_parents, values, strict=True))
        false_value = condition.evaluate(assignment | {parent: False})
        true_value = condition.evaluate(assignment | {parent: True})
        supporting &= not false_value or true_value
        attacking &= not true_value or false_value
    if supporting and attacking:
        return LinkType.BOTH
    if supporting:
        return LinkType.SUPPORTING
    if attacking:
        return LinkType.ATTACKING
    return LinkType.NEITHER


@given(_conditions())
def test_semantic_link_classifier_matches_truth_table_oracle(
    condition: AcceptanceCondition,
) -> None:
    framework = AbstractDialecticalFramework(
        statements=frozenset({"p", "q", "r", "c"}),
        links=frozenset({("p", "c"), ("q", "c"), ("r", "c")}),
        acceptance_conditions={
            "p": True_(),
            "q": True_(),
            "r": True_(),
            "c": condition,
        },
    )

    assert classify_link(framework, "p", "c") is _semantic_link_oracle(
        framework, "p", "c"
    )


def test_three_valued_interpretation_values_are_exported() -> None:
    assert {ThreeValued.T.value, ThreeValued.F.value, ThreeValued.U.value} == {
        "t",
        "f",
        "u",
    }
