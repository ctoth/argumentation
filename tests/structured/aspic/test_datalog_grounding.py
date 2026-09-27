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

    assert {rule.consequent for rule in grounded.system.defeasible_rules} == {
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

    assert {rule.consequent for rule in grounded.system.defeasible_rules} == {
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


def _flies(constant: str) -> Literal:
    return Literal(GroundAtom("flies", (constant,)))


def _birds_fly_theory(defeater_head: str, exception_facts) -> DefeasibleTheory:
    return DefeasibleTheory(
        facts={"bird": {("a",), ("b",)}, "exception": exception_facts},
        defeasible_rules=[
            GunrayRule(id="birds_fly", head="flies(X)", body=["bird(X)"]),
        ],
        defeaters=[
            GunrayRule(id="except", head=defeater_head, body=["exception(X)"]),
        ],
    )


def test_named_defeater_undercuts_only_its_matching_rule_instance() -> None:
    """Issue #66: ``~birds_fly(a)`` undercuts only the ``X = a`` instance.

    Diller et al. 2025 ground each rule instance ``r theta`` separately, and
    an undercut targets the name ``n(r)`` of one defeasible rule (Def 3), so
    a named defeater for ``birds_fly(a)`` must not undercut ``birds_fly(b)``.
    """
    from argumentation.structured.aspic.aspic_encoding import solve_aspic_grounded

    grounded = ground_defeasible_theory(
        _birds_fly_theory("~birds_fly(X)", {("a",)})
    )

    targets = [
        grounded.rule_origins[origin.target_rule].substitution
        for origin in grounded.rule_origins.values()
        if origin.role == "undercut" and origin.target_rule is not None
    ]
    accepted = solve_aspic_grounded(
        grounded.system, grounded.kb, grounded.pref
    ).accepted_conclusions

    assert targets == [(("X", "a"),)]
    assert _flies("b") in accepted
    assert _flies("a") not in accepted


def test_named_defeater_without_exception_undercuts_nothing() -> None:
    """Issue #66 control: with no exception fact both birds fly."""
    from argumentation.structured.aspic.aspic_encoding import solve_aspic_grounded

    grounded = ground_defeasible_theory(_birds_fly_theory("~birds_fly(X)", set()))
    accepted = solve_aspic_grounded(
        grounded.system, grounded.kb, grounded.pref
    ).accepted_conclusions

    assert {_flies("a"), _flies("b")} <= accepted


def _animal_theory(heads: tuple[str, str]) -> DefeasibleTheory:
    return DefeasibleTheory(
        facts={"bird": {("a",)}},
        strict_rules=[
            GunrayRule(id=rule_id, head=head, body=["bird(X)"])
            for rule_id, head in zip(("s1", "s2"), heads, strict=True)
        ],
    )


def test_identically_grounded_strict_rules_keep_every_source_id() -> None:
    """Issue #67: two authored rules grounding to one ASPIC+ rule keep both ids.

    Diller et al. 2025 (Def 9) ground each authored rule separately, so the
    source-to-ground relation is many-to-one and must not drop ``s1``.
    """
    grounded = ground_defeasible_theory(
        _animal_theory(("animal(X)", "animal(X)")), simplify=False
    )
    animal = Literal(GroundAtom("animal", ("a",)))

    assert set(grounded.source_to_ground_rules) == {"s1", "s2"}
    assert grounded.source_to_ground_rules["s1"] == grounded.source_to_ground_rules[
        "s2"
    ]
    assert {rule.consequent for rule in grounded.source_to_ground_rules["s1"]} == {
        animal
    }


def test_distinctly_grounded_strict_rules_keep_every_source_id() -> None:
    """Issue #67 control: distinct heads give distinct ground rules."""
    grounded = ground_defeasible_theory(
        _animal_theory(("animal(X)", "creature(X)")), simplify=False
    )

    assert set(grounded.source_to_ground_rules) == {"s1", "s2"}
    assert grounded.source_to_ground_rules["s1"].isdisjoint(
        grounded.source_to_ground_rules["s2"]
    )


def _flying_with_unrelated_fact(fact_predicate: str) -> frozenset[Literal]:
    from argumentation.structured.aspic.aspic_encoding import solve_aspic_grounded

    grounded = ground_defeasible_theory(
        DefeasibleTheory(
            facts={"bird": {("a",)}, fact_predicate: {()}},
            defeasible_rules=[
                GunrayRule(id="birds_fly", head="flies(X)", body=["bird(X)"]),
            ],
        )
    )
    authored = {
        Literal(GroundAtom(fact_predicate.removeprefix("~")), negated=True),
        Literal(GroundAtom("bird", ("a",))),
    }
    names = {
        rule.name
        for rule in grounded.system.defeasible_rules
        if rule.name is not None
    }
    assert not names & {literal.atom.predicate for literal in authored}
    return solve_aspic_grounded(
        grounded.system, grounded.kb, grounded.pref
    ).accepted_conclusions


def test_generated_rule_names_avoid_authored_predicates() -> None:
    """Issue #68: generated names n(r) must be fresh in the language.

    An undercut targets ``n(r)`` (Diller et al. 2025, Def 3), so a generated
    name equal to an authored predicate turns the unrelated fact ``~gr0``
    into an undercutter of ``birds_fly``.
    """
    assert _flies("a") in _flying_with_unrelated_fact("~gr0")


def test_generated_rule_names_with_unrelated_fact_control() -> None:
    """Issue #68 control: a non-colliding unrelated fact changes nothing."""
    assert _flies("a") in _flying_with_unrelated_fact("~unrelated")
