from __future__ import annotations

from gunray import DefeasibleTheory, Rule as GunrayRule

from argumentation.aspic import GroundAtom, Literal, build_arguments
from argumentation.datalog_grounding import (
    ground_defeasible_theory,
    grounding_inspection_to_aspic,
)


def test_ground_defeasible_theory_uses_gunray_simplification() -> None:
    theory = DefeasibleTheory(
        facts={"bird": {("tweety",)}},
        strict_rules=[
            GunrayRule(id="s1", head="animal(X)", body=["bird(X)"]),
        ],
        defeasible_rules=[
            GunrayRule(id="d1", head="flies(X)", body=["animal(X)"]),
        ],
    )

    grounded = ground_defeasible_theory(theory)

    assert grounded.non_approximated_predicates == frozenset({"animal", "bird"})
    assert Literal(GroundAtom("bird", ("tweety",))) in grounded.kb.axioms
    assert Literal(GroundAtom("animal", ("tweety",))) in grounded.kb.axioms
    assert not grounded.system.strict_rules
    assert {
        (rule.name, rule.consequent)
        for rule in grounded.system.defeasible_rules
    } == {
        (
            'd1#{"X":{"type":"str","value":"tweety"}}',
            Literal(GroundAtom("flies", ("tweety",))),
        )
    }


def test_ground_defeasible_theory_normalizes_strong_negation() -> None:
    theory = DefeasibleTheory(
        facts={"bird": {("tweety",)}},
        defeasible_rules=[
            GunrayRule(id="d1", head="~flies(X)", body=["bird(X)"]),
        ],
    )

    grounded = ground_defeasible_theory(theory)

    assert {
        rule.consequent
        for rule in grounded.system.defeasible_rules
    } == {
        Literal(GroundAtom("flies", ("tweety",)), negated=True),
    }
    assert all(
        rule.consequent.atom.predicate != "~flies"
        for rule in grounded.system.defeasible_rules
    )


def test_ground_defeasible_theory_projects_superiority_to_ground_rules() -> None:
    theory = DefeasibleTheory(
        facts={"bird": {("tweety",)}},
        defeasible_rules=[
            GunrayRule(id="weak", head="flies(X)", body=["bird(X)"]),
            GunrayRule(id="strong", head="~flies(X)", body=["bird(X)"]),
        ],
        superiority=(("strong", "weak"),),
    )

    grounded = ground_defeasible_theory(theory)

    assert len(grounded.pref.rule_order) == 1
    weaker, stronger = next(iter(grounded.pref.rule_order))
    assert weaker.name is not None
    assert stronger.name is not None
    assert weaker.name.startswith("weak#")
    assert stronger.name.startswith("strong#")


def test_ground_defeasible_theory_output_builds_aspic_arguments() -> None:
    theory = DefeasibleTheory(
        facts={"bird": {("tweety",)}},
        defeasible_rules=[
            GunrayRule(id="d1", head="flies(X)", body=["bird(X)"]),
        ],
    )

    grounded = ground_defeasible_theory(theory)
    arguments = build_arguments(grounded.system, grounded.kb)

    assert any(
        argument.rule.name is not None and argument.rule.name.startswith("d1#")
        for argument in arguments
        if hasattr(argument, "rule")
    )


def test_grounding_inspection_to_aspic_uses_existing_gunray_result() -> None:
    from gunray import inspect_grounding

    theory = DefeasibleTheory(
        facts={"bird": {("tweety",)}},
        defeasible_rules=[
            GunrayRule(id="d1", head="flies(X)", body=["bird(X)"]),
            GunrayRule(id="d2", head="~flies(X)", body=["bird(X)"]),
        ],
        superiority=(("d2", "d1"),),
    )

    grounded = grounding_inspection_to_aspic(
        inspect_grounding(theory),
        superiority=theory.superiority,
    )

    assert {
        rule.consequent
        for rule in grounded.system.defeasible_rules
    } == {
        Literal(GroundAtom("flies", ("tweety",))),
        Literal(GroundAtom("flies", ("tweety",)), negated=True),
    }
    weaker, stronger = next(iter(grounded.pref.rule_order))
    assert weaker.name is not None and weaker.name.startswith("d1#")
    assert stronger.name is not None and stronger.name.startswith("d2#")
