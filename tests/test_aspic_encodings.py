from __future__ import annotations

import importlib
import re

import argumentation
import pytest

from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
    conc,
)
from argumentation.aspic_encoding import encode_aspic_theory
from argumentation.aspic_encoding import solve_aspic_grounded
from argumentation.aspic_encoding import solve_aspic_with_backend
from argumentation.dung import grounded_extension


ASP_CONSTANT_RE = re.compile(r"^[a-z][A-Za-z0-9_]*$")


def test_aspic_encoding_module_is_exported_from_package() -> None:
    package = importlib.reload(argumentation)

    assert "aspic_encoding" in package.__all__


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


def test_solve_aspic_grounded_returns_accepted_conclusions() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    rule = Rule((p,), q, "defeasible", "d_q")
    system = ArgumentationSystem(
        language=frozenset({p, q}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({rule}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    result = solve_aspic_grounded(system, kb, pref)

    assert result.status == "success"
    assert result.semantics == "grounded"
    assert result.accepted_conclusions == frozenset({p, q})
    assert result.backend == "materialized_reference"


def test_solve_aspic_grounded_matches_materialized_pipeline() -> None:
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
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p, not_q}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    projection = build_abstract_framework(system, kb, pref)
    grounded_ids = grounded_extension(projection.framework)
    expected = frozenset(conc(projection.id_to_argument[arg_id]) for arg_id in grounded_ids)

    result = solve_aspic_grounded(system, kb, pref)

    assert result.accepted_conclusions == expected
    assert result.accepted_argument_ids == grounded_ids


def test_optional_aspic_backend_absence_is_typed() -> None:
    p = Literal(GroundAtom("p"))
    system = ArgumentationSystem(
        language=frozenset({p}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    result = solve_aspic_with_backend(system, kb, pref, backend="missing-test-backend")

    assert result.status == "unavailable_backend"
    assert result.backend == "missing-test-backend"
    assert result.accepted_argument_ids == frozenset()
    assert result.metadata["reason"] == "backend is not installed or registered"


def test_ws_o_arg_aspic_encoding_sanitises_literal_ids_for_asp() -> None:
    """Bug 2: encoded literal identifiers must be valid ASP constants."""
    p = Literal(GroundAtom("P", (1, 2)))
    not_p = p.contrary
    system = ArgumentationSystem(
        language=frozenset({p, not_p}),
        contrariness=ContrarinessFn(contradictories=frozenset({(p, not_p)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset({not_p}), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    encoding = encode_aspic_theory(system, kb, pref)
    ids = {
        fact.removesuffix(").").split("(", 1)[1]
        for fact in encoding.facts
        if fact.startswith(("axiom(", "premise("))
    }

    assert ids
    assert all(ASP_CONSTANT_RE.fullmatch(identifier) for identifier in ids)
    assert encoding.literal_by_id
    assert set(encoding.literal_by_id) >= ids
    assert not any("~" in fact or "(" in fact.split("(", 1)[1] for fact in encoding.facts)


def test_ws_o_arg_aspic_encoding_rejects_duplicate_defeasible_rule_names() -> None:
    """Bug 3: duplicate defeasible rule names must fail at encode time."""
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    r = Literal(GroundAtom("r"))
    first = Rule((p,), q, "defeasible", "dup")
    second = Rule((p,), r, "defeasible", "dup")
    system = ArgumentationSystem(
        language=frozenset({p, q, r}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({first, second}),
    )
    kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset())
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    with pytest.raises(ValueError, match="duplicate defeasible rule name: 'dup'"):
        encode_aspic_theory(system, kb, pref)
