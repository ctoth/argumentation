from __future__ import annotations

from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
)
from argumentation.aspic_encoding import encode_aspic_theory


def test_aspic_encoding_assigns_deterministic_facts_and_signature() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    not_q = q.contrary
    strict = Rule((p,), q, "strict")
    defeasible = Rule((q,), not_q, "defeasible", "d_not_q")
    system = ArgumentationSystem(
        language=frozenset({not_q, q, p}),
        contrariness=ContrarinessFn(contradictories=frozenset({(q, not_q)})),
        strict_rules=frozenset({strict}),
        defeasible_rules=frozenset({defeasible}),
    )
    kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset({q}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    first = encode_aspic_theory(system, kb, pref)
    second = encode_aspic_theory(system, kb, pref)

    assert first.facts == second.facts
    assert first.signature == second.signature
    assert first.facts == tuple(sorted(first.facts))
    assert "axiom(p)." in first.facts
    assert "premise(q)." in first.facts
    assert "s_head(s_0,q)." in first.facts
    assert "s_body(s_0,p)." in first.facts
    assert "d_head(d_not_q,~q)." in first.facts
    assert "d_body(d_not_q,q)." in first.facts
    assert "contrary(q,~q)." in first.facts


def test_aspic_encoding_signature_is_stable_under_input_set_ordering() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    r = Literal(GroundAtom("r"))
    d1 = Rule((p,), q, "defeasible", "d1")
    d2 = Rule((q,), r, "defeasible", "d2")
    first_system = ArgumentationSystem(
        language=frozenset({p, q, r}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({d1, d2}),
    )
    second_system = ArgumentationSystem(
        language=frozenset({r, q, p}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({d2, d1}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({q, p}))
    pref = PreferenceConfig(
        rule_order=frozenset({(d1, d2)}),
        premise_order=frozenset(),
        comparison="democratic",
        link="last",
    )

    first = encode_aspic_theory(first_system, kb, pref)
    second = encode_aspic_theory(second_system, kb, pref)

    assert first.signature == second.signature
    assert first.facts == second.facts
    assert "preferred(d2,d1)." in first.facts
    assert first.metadata["comparison"] == "democratic"
    assert first.metadata["link"] == "last"
