from __future__ import annotations

import pytest

import argumentation
from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
)
from argumentation.value_based import (
    complementary_literals,
    subjective_argumentation_theory,
    subjective_defeasible_rules,
    subjective_knowledge_base,
)


def test_value_based_module_is_exported() -> None:
    assert argumentation.value_based.subjective_knowledge_base is subjective_knowledge_base
    assert "value_based" in argumentation.__all__


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def rule(name: str, antecedents: tuple[str, ...], consequent: str) -> Rule:
    return Rule(
        antecedents=tuple(lit(item) for item in antecedents),
        consequent=lit(consequent),
        kind="defeasible",
        name=name,
    )


def test_subjective_knowledge_base_adds_complements_for_rejected_props() -> None:
    kb = KnowledgeBase(
        axioms=frozenset({lit("a")}),
        premises=frozenset({lit("b"), lit("d"), lit("f")}),
    )
    propositions = frozenset({lit("a"), lit("b"), lit("c"), lit("d"), lit("e"), lit("f")})
    clean = frozenset({lit("a"), lit("b"), lit("c"), lit("e"), lit("f")})

    subjective = subjective_knowledge_base(kb, propositions=propositions, clean=clean)

    assert subjective.axioms == kb.axioms
    assert lit("d") not in subjective.premises
    assert lit("d").contrary in subjective.premises
    assert {lit("b"), lit("f")} <= subjective.premises


def test_complementary_literals_are_rejected_positive_props() -> None:
    propositions = frozenset({lit("a"), lit("b")})
    clean = frozenset({lit("a")})

    assert complementary_literals(propositions, clean) == frozenset({lit("b").contrary})


def test_subjective_defeasible_rules_filter_body_head_and_rule_name() -> None:
    d1 = rule("d1", ("a", "b"), "c")
    d2 = rule("d2", ("d",), "c")
    d3 = rule("d3", ("c",), "e")
    d4 = rule("d4", ("f",), "a")
    clean = frozenset({
        lit("a"),
        lit("b"),
        lit("c"),
        lit("e"),
        lit("f"),
        lit("d1"),
        lit("d3"),
        lit("d4"),
    })

    assert subjective_defeasible_rules(frozenset({d1, d2, d3, d4}), clean=clean) == frozenset({
        d1,
        d3,
        d4,
    })


def test_subjective_defeasible_rules_reject_unnamed_defeasible_rules() -> None:
    unnamed = Rule(
        antecedents=(lit("a"),),
        consequent=lit("b"),
        kind="defeasible",
        name=None,
    )

    with pytest.raises(ValueError, match="name"):
        subjective_defeasible_rules(frozenset({unnamed}), clean=frozenset({lit("a"), lit("b")}))


def test_subjective_argumentation_theory_returns_filtered_projection() -> None:
    d1 = rule("d1", ("a",), "b")
    d2 = rule("d2", ("b",), "c")
    system = ArgumentationSystem(
        language=frozenset({
            lit("a"),
            lit("b"),
            lit("c"),
            lit("d1"),
            lit("d2"),
            lit("b").contrary,
            lit("d2").contrary,
        }),
        contrariness=ContrarinessFn(contradictories=frozenset({(lit("b"), lit("b").contrary)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({d1, d2}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({lit("a"), lit("b")}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    subjective = subjective_argumentation_theory(
        system,
        kb,
        pref,
        propositions=frozenset({lit("a"), lit("b"), lit("c"), lit("d1"), lit("d2")}),
        clean=frozenset({lit("a"), lit("c"), lit("d1")}),
    )

    assert subjective.knowledge_base.premises == frozenset({
        lit("a"),
        lit("b").contrary,
        lit("d2").contrary,
    })
    assert subjective.system.defeasible_rules == frozenset({d1})
    assert subjective.projection.arguments
    assert subjective.projection.framework.arguments
