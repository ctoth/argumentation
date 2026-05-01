from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
)
from argumentation.aspic_encoding import solve_aspic_with_backend


def mutually_attacking_premises():
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    system = ArgumentationSystem(
        language=frozenset({p, q}),
        contrariness=ContrarinessFn(frozenset({(p, q)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p, q}))
    pref = PreferenceConfig(frozenset(), frozenset(), "elitist", "last")
    return system, kb, pref


@pytest.mark.parametrize("semantics", ["grounded", "admissible", "complete", "stable", "preferred"])
def test_aspic_asp_matches_materialized_reference_on_mutual_attack(semantics) -> None:
    system, kb, pref = mutually_attacking_premises()

    expected = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="materialized_reference",
        semantics=semantics,
    )
    result = solve_aspic_with_backend(system, kb, pref, backend="asp", semantics=semantics)

    assert result.status == "success"
    assert set(result.extensions) == set(expected.extensions)
    assert result.metadata["projection"] == "aspic_abstract_framework"


def test_aspic_asp_supports_last_link_preferences() -> None:
    a = Literal(GroundAtom("a"))
    b = Literal(GroundAtom("b"))
    p = Literal(GroundAtom("p"))
    not_p = p.contrary
    d_p = Rule((a,), p, "defeasible", "d_p")
    d_not_p = Rule((b,), not_p, "defeasible", "d_not_p")
    system = ArgumentationSystem(
        language=frozenset({a, b, p, not_p}),
        contrariness=ContrarinessFn(frozenset({(p, not_p)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({d_p, d_not_p}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({a, b}))
    pref = PreferenceConfig(
        rule_order=frozenset({(d_not_p, d_p)}),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    expected = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="materialized_reference",
        semantics="preferred",
    )
    result = solve_aspic_with_backend(system, kb, pref, backend="asp", semantics="preferred")

    assert result.status == "success"
    assert set(result.extensions) == set(expected.extensions)


def test_aspic_asp_rejects_weakest_link_preferences() -> None:
    system, kb, _pref = mutually_attacking_premises()
    pref = PreferenceConfig(frozenset(), frozenset(), "elitist", "weakest")

    result = solve_aspic_with_backend(system, kb, pref, backend="asp", semantics="grounded")

    assert result.status == "unavailable_backend"
    assert result.metadata["reason"] == (
        "ASP backend covers last-link only; weakest-link grounded is NP-hard "
        "per Lehtonen 2024 Prop 17"
    )


@st.composite
def acyclic_aspic_theories(draw):
    size = draw(st.integers(min_value=1, max_value=4))
    literals = tuple(Literal(GroundAtom(f"p{index}")) for index in range(size))
    rules = frozenset(
        Rule((literals[index],), literals[index + 1], "defeasible", f"d_{index}")
        for index in range(size - 1)
        if draw(st.booleans())
    )
    system = ArgumentationSystem(
        language=frozenset(literals),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=rules,
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({literals[0]}))
    pref = PreferenceConfig(frozenset(), frozenset(), "elitist", "last")
    return system, kb, pref


@given(acyclic_aspic_theories(), st.sampled_from(("grounded", "complete", "stable", "preferred")))
@settings(deadline=10000, max_examples=25)
def test_aspic_asp_matches_reference_on_generated_acyclic_theories(theory, semantics) -> None:
    system, kb, pref = theory
    expected = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="materialized_reference",
        semantics=semantics,
    )
    result = solve_aspic_with_backend(system, kb, pref, backend="asp", semantics=semantics)

    assert result.status == "success"
    assert set(result.extensions) == set(expected.extensions)
