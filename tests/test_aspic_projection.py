from __future__ import annotations

from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
    build_arguments,
    compute_attacks,
    compute_defeats,
)
from argumentation.dung import ArgumentationFramework


def test_build_abstract_framework_matches_manual_aspic_pipeline() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    not_q = q.contrary
    rule_q = Rule((p,), q, "defeasible", "d_q")

    system = ArgumentationSystem(
        language=frozenset({p, q, not_q}),
        contrariness=ContrarinessFn(contradictories=frozenset({(q, not_q)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({rule_q}),
    )
    kb = KnowledgeBase(
        axioms=frozenset(),
        premises=frozenset({p, not_q}),
    )
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    projection = build_abstract_framework(system, kb, pref)
    arguments = build_arguments(system, kb)
    attacks = compute_attacks(arguments, system)
    defeats = compute_defeats(attacks, arguments, system, kb, pref)

    assert projection.arguments == arguments
    assert projection.attacks == attacks
    assert projection.defeats == defeats
    assert projection.framework == ArgumentationFramework(
        arguments=frozenset(projection.argument_to_id.values()),
        attacks=frozenset(
            (projection.argument_to_id[attack.attacker], projection.argument_to_id[attack.target])
            for attack in attacks
        ),
        defeats=frozenset(
            (projection.argument_to_id[attack.attacker], projection.argument_to_id[attack.target])
            for attack in defeats
        ),
    )


def test_build_abstract_framework_assigns_deterministic_external_ids() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    system = ArgumentationSystem(
        language=frozenset({p, q}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({q, p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    first = build_abstract_framework(system, kb, pref)
    second = build_abstract_framework(system, kb, pref)

    assert first.argument_to_id == second.argument_to_id
    assert set(first.id_to_argument) == set(first.argument_to_id.values())
