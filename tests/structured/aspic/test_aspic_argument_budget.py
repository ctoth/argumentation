"""Operational contract for ASPIC+ argument multiplication (issue #102).

Per this repository's AGENTS.md, a performance-shaped defect gets a
deterministic budget that fails fast instead of timing out. The attack count
is computed from per-conclusion argument counts (every argument concluding a
conflicting literal attacks each rebuttable or underminable sub-argument,
Modgil & Prakken 2018, Def 8, p.11) without calling ``compute_attacks``.
"""

from __future__ import annotations

from collections import Counter

from argumentation.structured.aspic.aspic import (
    Argument,
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PremiseArg,
    Rule,
    build_arguments,
    conc,
    is_firm,
    is_strict,
    sub,
    top_rule,
)

ARGUMENT_BUDGET = 200
ATTACK_PAIR_BUDGET = 20_000


def _attack_pair_count(
    system: ArgumentationSystem, arguments: frozenset[Argument]
) -> int:
    by_conclusion = Counter(conc(argument) for argument in arguments)
    contrariness = system.contrariness

    def attackers_of(target: Literal) -> int:
        return sum(
            count
            for literal, count in by_conclusion.items()
            if contrariness.is_contradictory(literal, target)
            or contrariness.is_contrary(literal, target)
        )

    pairs = 0
    for argument in arguments:
        for sub_argument in sub(argument):
            if is_firm(sub_argument) and is_strict(sub_argument):
                continue
            if isinstance(sub_argument, PremiseArg) and not sub_argument.is_axiom:
                pairs += attackers_of(sub_argument.premise)
            rule = top_rule(sub_argument)
            if rule is not None and rule.kind == "defeasible":
                pairs += attackers_of(conc(sub_argument))
    return pairs


def _issue_102_theory() -> tuple[ArgumentationSystem, KnowledgeBase]:
    """The Hypothesis-shrunk theory from #102: 4 ordinary premises, 11 strict
    rules (including ``~q, ~q -> p`` and permuted duplicates) and 3
    defeasible rules."""
    p, q, r, s = (Literal(GroundAtom(name)) for name in "pqrs")
    not_p, not_q, not_r, not_s = (atom.contrary for atom in (p, q, r, s))
    strict = frozenset(
        Rule(body, head, "strict")
        for body, head in [
            ((p,), not_s),
            ((q, not_r), s),
            ((q, not_s), r),
            ((s,), not_p),
            ((not_p, not_q), q),
            ((not_q, not_p), q),
            ((not_q, not_q), p),
            ((not_r, q), s),
            ((not_r, not_s), not_q),
            ((not_s, q), r),
            ((not_s, not_r), not_q),
        ]
    )
    defeasible = frozenset(
        {
            Rule((r, q), not_r, "defeasible", "d0"),
            Rule((s,), q, "defeasible", "d3"),
            Rule((not_p,), not_s, "defeasible", "d1"),
        }
    )
    system = ArgumentationSystem(
        frozenset({p, q, r, s, not_p, not_q, not_r, not_s}),
        ContrarinessFn(frozenset((atom, atom.contrary) for atom in (p, q, r, s))),
        strict,
        defeasible,
    )
    return system, KnowledgeBase(
        axioms=frozenset(), premises=frozenset({q, s, not_p, not_r})
    )


def test_issue_102_theory_stays_within_argument_and_attack_budget() -> None:
    """Issue #102: the theory must build at most 200 arguments and at most
    20,000 attack pairs. With strict antecedents read as sets it builds 98
    arguments and 7,226 attack pairs (it was 18,850 and ~306M)."""
    system, kb = _issue_102_theory()

    arguments = build_arguments(system, kb)

    assert len(arguments) <= ARGUMENT_BUDGET
    assert _attack_pair_count(system, arguments) <= ATTACK_PAIR_BUDGET


def test_small_theory_within_budget_control() -> None:
    """Control: a theory with distinct antecedents (q, ~r -> s; s => q) is
    well inside the budget."""
    q, r, s = (Literal(GroundAtom(name)) for name in "qrs")
    system = ArgumentationSystem(
        frozenset({q, r, s, q.contrary, r.contrary, s.contrary}),
        ContrarinessFn(frozenset((atom, atom.contrary) for atom in (q, r, s))),
        frozenset({Rule((q, r.contrary), s, "strict")}),
        frozenset({Rule((s,), q, "defeasible", "d3")}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({q, r.contrary}))

    arguments = build_arguments(system, kb)

    assert len(arguments) <= ARGUMENT_BUDGET
    assert _attack_pair_count(system, arguments) <= ATTACK_PAIR_BUDGET
