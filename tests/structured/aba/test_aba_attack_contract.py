"""Operational and semantic contracts for the plain flat-ABA attack predicate.

Bondarenko et al. 1997, Def 3.1 (p.76): ``Delta attacks alpha`` iff
``T u Delta |- contrary(alpha)``, and ``Delta attacks Delta'`` iff Delta
attacks some ``alpha`` in ``Delta'``. The relation is defined on the whole
attacker set, and Horn deduction is monotone, so deciding it needs one
closure of the attacker set rather than an enumeration of its subsets.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.structured.aba import aba
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal
from tests.aba_hypothesis_generators import flat_aba_frameworks


def _independent_assumptions(
    size: int,
) -> tuple[ABAFramework, dict[Literal, Literal]]:
    assumptions = frozenset(Literal(GroundAtom(f"a{index}")) for index in range(size))
    contrary = {
        assumption: Literal(GroundAtom(f"c{assumption.atom.predicate}"))
        for assumption in assumptions
    }
    framework = ABAFramework(
        assumptions | frozenset(contrary.values()),
        frozenset(),
        assumptions,
        contrary,
    )
    return framework, contrary


def _count_closures(monkeypatch) -> list[int]:
    original = aba._closure
    calls = [0]

    def measured(framework, premises):
        calls[0] += 1
        return original(framework, premises)

    monkeypatch.setattr(aba, "_closure", measured)
    return calls


def test_boolean_attack_query_uses_one_attacker_closure(monkeypatch) -> None:
    """Issue #54: the Boolean attack query shares one full-attacker closure.

    Operational contract: five independent assumptions with no rules used
    to trigger 160 identical-shape closures through support enumeration.
    """
    framework, _contrary = _independent_assumptions(5)
    calls = _count_closures(monkeypatch)

    assert aba.attacks(framework, framework.assumptions, framework.assumptions) is False
    assert calls[0] <= 1


def test_boolean_attack_query_still_detects_an_attack() -> None:
    """Issue #54 control: a contrary derivable from the attackers is an attack."""
    framework, contrary = _independent_assumptions(3)
    target = Literal(GroundAtom("a0"))
    attacker = Literal(GroundAtom("x"))
    framework = ABAFramework(
        framework.language | frozenset({attacker, Literal(GroundAtom("cx"))}),
        frozenset(),
        framework.assumptions | frozenset({attacker}),
        {**contrary, attacker: Literal(GroundAtom("cx")), target: attacker},
    )

    assert aba.attacks(framework, frozenset({attacker}), frozenset({target})) is True
    assert aba.attacks(framework, frozenset(), frozenset({target})) is False


@given(flat_aba_frameworks(max_assumptions=4, max_rules=6), st.data())
@settings(max_examples=60, deadline=None)
def test_boolean_attack_matches_support_enumeration(
    framework: ABAFramework,
    data: st.DataObject,
) -> None:
    """Issue #54: the one-closure predicate equals the exhaustive witness search."""
    ordered = sorted(framework.assumptions, key=repr)
    attacker = frozenset(
        data.draw(st.sets(st.sampled_from(ordered))) if ordered else ()
    )
    target = frozenset(data.draw(st.sets(st.sampled_from(ordered))) if ordered else ())

    assert aba.attacks(framework, attacker, target) == bool(
        aba._attack_supports(framework, attacker, target)
    )
