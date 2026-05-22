from __future__ import annotations

from gunray import DefeasibleTheory, Rule as GunrayRule

from argumentation.structured.aspic.aspic import GroundAtom, Literal, build_arguments
from argumentation.structured.aspic.datalog_grounding import (
    ground_defeasible_theory,
    grounding_inspection_to_aspic,
)


def _single_defeasible_rule(grounded):
    (rule,) = tuple(grounded.system.defeasible_rules)
    return rule


def _ground_rules(grounded):
    return tuple(
        rule
        for rule, origin in grounded.rule_origins.items()
        if origin.role == "ground"
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

    rule = _single_defeasible_rule(grounded)
    assert rule.name == "gr0"
    assert "#" not in rule.name
    assert "d1" not in rule.name
    assert rule.consequent == Literal(GroundAtom("flies", ("tweety",)))

    origin = grounded.rule_origins[rule]
    assert origin.source_rule_id == "d1"
    assert origin.substitution == (("X", "tweety"),)
    assert origin.role == "ground"
    assert origin.target_rule is None


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
    assert "#" not in weaker.name
    assert "#" not in stronger.name
    assert grounded.rule_origins[weaker].source_rule_id == "weak"
    assert grounded.rule_origins[stronger].source_rule_id == "strong"


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
        argument.rule in _ground_rules(grounded)
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
    assert weaker.name is not None and "#" not in weaker.name
    assert stronger.name is not None and "#" not in stronger.name
    assert grounded.rule_origins[weaker].source_rule_id == "d1"
    assert grounded.rule_origins[stronger].source_rule_id == "d2"


def test_defeater_projection_records_structured_undercut_origin() -> None:
    theory = DefeasibleTheory(
        facts={"bird": {("tweety",)}, "exception": {("tweety",)}},
        defeasible_rules=[
            GunrayRule(id="birds_fly", head="flies(X)", body=["bird(X)"]),
        ],
        defeaters=[
            GunrayRule(
                id="named_defeater",
                head="~birds_fly(X)",
                body=["exception(X)"],
            ),
        ],
    )

    grounded = ground_defeasible_theory(theory)
    ground_rules = {
        origin.source_rule_id: rule
        for rule, origin in grounded.rule_origins.items()
        if origin.role == "ground"
    }
    undercut_rules = {
        rule: origin
        for rule, origin in grounded.rule_origins.items()
        if origin.role == "undercut"
    }

    target_rule = ground_rules["birds_fly"]
    assert target_rule.name is not None

    ((undercut_rule, undercut_origin),) = tuple(undercut_rules.items())
    assert undercut_rule.name == "uc0"
    assert "#" not in undercut_rule.name
    assert undercut_rule.consequent == Literal(
        GroundAtom(target_rule.name),
        negated=True,
    )
    assert undercut_origin.source_rule_id == "named_defeater"
    assert undercut_origin.substitution == (("X", "tweety"),)
    assert undercut_origin.role == "undercut"
    assert undercut_origin.target_rule == target_rule
