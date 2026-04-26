from __future__ import annotations

import importlib

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
from argumentation.aspic_incomplete import (
    PartialASPICTheory,
    evaluate_incomplete_grounded,
)


def _empty_pref() -> PreferenceConfig:
    return PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )


def test_aspic_incomplete_module_is_exported_from_package() -> None:
    package = importlib.reload(argumentation)

    assert "aspic_incomplete" in package.__all__


def test_unknown_premise_makes_conclusion_relevant_across_completions() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    rule = Rule((p,), q, "defeasible", "d_q")
    theory = PartialASPICTheory(
        system=ArgumentationSystem(
            language=frozenset({p, q}),
            contrariness=ContrarinessFn(frozenset()),
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule}),
        ),
        kb=KnowledgeBase(axioms=frozenset(), premises=frozenset()),
        pref=_empty_pref(),
        unknown_premises=frozenset({p}),
    )

    result = evaluate_incomplete_grounded(theory, q)

    assert result.status == "relevant"
    assert result.accepting_completions == (frozenset({p}),)
    assert result.rejecting_completions == (frozenset(),)


def test_known_premise_makes_conclusion_stable() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    rule = Rule((p,), q, "defeasible", "d_q")
    theory = PartialASPICTheory(
        system=ArgumentationSystem(
            language=frozenset({p, q}),
            contrariness=ContrarinessFn(frozenset()),
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule}),
        ),
        kb=KnowledgeBase(axioms=frozenset(), premises=frozenset({p})),
        pref=_empty_pref(),
        unknown_premises=frozenset(),
    )

    result = evaluate_incomplete_grounded(theory, q)

    assert result.status == "stable"
    assert result.accepting_completions == (frozenset(),)
    assert result.rejecting_completions == ()


def test_query_with_arguments_but_no_acceptance_is_unknown() -> None:
    p = Literal(GroundAtom("p"))
    not_p = p.contrary
    theory = PartialASPICTheory(
        system=ArgumentationSystem(
            language=frozenset({p, not_p}),
            contrariness=ContrarinessFn(contradictories=frozenset({(p, not_p)})),
            strict_rules=frozenset(),
            defeasible_rules=frozenset(),
        ),
        kb=KnowledgeBase(axioms=frozenset(), premises=frozenset({p, not_p})),
        pref=_empty_pref(),
        unknown_premises=frozenset(),
    )

    result = evaluate_incomplete_grounded(theory, p)

    assert result.status == "unknown"
    assert result.accepting_completions == ()
    assert result.rejecting_completions == (frozenset(),)


def test_query_with_no_possible_argument_is_unsupported() -> None:
    p = Literal(GroundAtom("p"))
    r = Literal(GroundAtom("r"))
    theory = PartialASPICTheory(
        system=ArgumentationSystem(
            language=frozenset({p, r}),
            contrariness=ContrarinessFn(frozenset()),
            strict_rules=frozenset(),
            defeasible_rules=frozenset(),
        ),
        kb=KnowledgeBase(axioms=frozenset(), premises=frozenset({p})),
        pref=_empty_pref(),
        unknown_premises=frozenset(),
    )

    result = evaluate_incomplete_grounded(theory, r)

    assert result.status == "unsupported"
    assert result.accepting_completions == ()
    assert result.rejecting_completions == (frozenset(),)
