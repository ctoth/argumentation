"""Synthetic ABA and ASPIC+ benchmark instance generators."""

from __future__ import annotations

from argumentation.aba import ABAFramework
from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
)


def aba_chain(size: int, *, body_size: int = 1) -> ABAFramework:
    assumptions = tuple(Literal(GroundAtom(f"a{index}")) for index in range(size))
    contraries = tuple(Literal(GroundAtom(f"c{index}")) for index in range(size))
    rules: set[Rule] = set()
    for index, contrary in enumerate(contraries):
        body = tuple(assumptions[(index + offset + 1) % size] for offset in range(body_size))
        rules.add(Rule(body, contrary, "strict", f"r_{index}"))
    return ABAFramework(
        language=frozenset((*assumptions, *contraries)),
        rules=frozenset(rules),
        assumptions=frozenset(assumptions),
        contrary=dict(zip(assumptions, contraries, strict=True)),
    )


def aspic_chain(size: int, *, defeasible_ratio: float = 1.0):
    literals = tuple(Literal(GroundAtom(f"p{index}")) for index in range(size))
    negated = tuple(literal.contrary for literal in literals)
    strict_rules: set[Rule] = set()
    defeasible_rules: set[Rule] = set()
    defeasible_cutoff = int(max(0, min(1, defeasible_ratio)) * max(0, size - 1))
    for index in range(size - 1):
        if index < defeasible_cutoff:
            defeasible_rules.add(Rule((literals[index],), literals[index + 1], "defeasible", f"d_{index}"))
        else:
            strict_rules.add(Rule((literals[index],), literals[index + 1], "strict"))
    system = ArgumentationSystem(
        language=frozenset((*literals, *negated)),
        contrariness=ContrarinessFn(frozenset(zip(literals, negated, strict=True))),
        strict_rules=frozenset(strict_rules),
        defeasible_rules=frozenset(defeasible_rules),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({literals[0]}))
    pref = PreferenceConfig(frozenset(), frozenset(), "elitist", "last")
    return system, kb, pref
