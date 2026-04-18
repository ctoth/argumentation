"""Tests for goal-directed backward chaining argument construction.

Verifies build_arguments_for() against build_arguments() and exercises
edge cases: depth limiting, unreachable goals, attacker inclusion.

References:
    Modgil & Prakken 2018, Def 5 (pp.9-10): argument structure.
    Toni (2014): ABA backward chaining from claims to assumptions.
    Besnard & Hunter (2001, Def 6.1, p.215): argument trees.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings, assume
from hypothesis import strategies as st

from argumentation.aspic import (
    Literal,
    GroundAtom,
    ContrarinessFn,
    Rule,
    PremiseArg,
    StrictArg,
    DefeasibleArg,
    Argument,
    KnowledgeBase,
    ArgumentationSystem,
    build_arguments,
    build_arguments_for,
    compute_attacks,
    conc,
    prem,
    sub,
    _contraries_of,
)


# ── Helpers ────────────────────────────────────────────────────────


def _make_system(
    atoms: list[str],
    strict_rules: list[Rule] | None = None,
    defeasible_rules: list[Rule] | None = None,
    extra_contraries: frozenset[tuple[Literal, Literal]] | None = None,
) -> tuple[ArgumentationSystem, frozenset[Literal]]:
    """Build an ArgumentationSystem from atom names and rules."""
    literals = frozenset(
        Literal(atom=GroundAtom(a), negated=n) for a in atoms for n in (False, True)
    )
    contradictory_pairs = frozenset(
        (Literal(atom=GroundAtom(a), negated=False), Literal(atom=GroundAtom(a), negated=True))
        for a in atoms
    )
    cfn = ContrarinessFn(
        contradictories=contradictory_pairs,
        contraries=extra_contraries or frozenset(),
    )
    system = ArgumentationSystem(
        language=literals,
        contrariness=cfn,
        strict_rules=frozenset(strict_rules or []),
        defeasible_rules=frozenset(defeasible_rules or []),
    )
    return system, literals


# ── Test: _contraries_of helper ────────────────────────────────────


class TestContrariesOf:
    def test_contradictory_pair(self):
        """~p is a contrary of p via contradiction."""
        p = Literal(GroundAtom("p"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        lang = frozenset({p, neg_p})
        cfn = ContrarinessFn(contradictories=frozenset({(p, neg_p)}))
        result = _contraries_of(p, cfn, lang)
        assert neg_p in result

    def test_asymmetric_contrary(self):
        """Directed contraries: a is contrary of b but b is not contrary of a."""
        a = Literal(GroundAtom("a"))
        b = Literal(GroundAtom("b"))
        lang = frozenset({a, b})
        cfn = ContrarinessFn(
            contradictories=frozenset(),
            contraries=frozenset({(a, b)}),  # a attacks b
        )
        # a is in bar(b), so contraries_of(b) should include a
        result = _contraries_of(b, cfn, lang)
        assert a in result
        # b is NOT in bar(a), so contraries_of(a) should not include b
        result_a = _contraries_of(a, cfn, lang)
        assert b not in result_a


# ── Test: basic backward chaining ──────────────────────────────────


class TestBasicBackwardChaining:
    def test_premise_only(self):
        """Goal that is a premise should return just PremiseArg."""
        p = Literal(GroundAtom("p"))
        system, _ = _make_system(["p"])
        kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))

        result = build_arguments_for(system, kb, p, include_attackers=False)
        assert len(result) >= 1
        premise_args = {a for a in result if isinstance(a, PremiseArg)}
        assert any(a.premise == p for a in premise_args)

    def test_axiom_only(self):
        """Goal that is an axiom should return PremiseArg with is_axiom=True."""
        p = Literal(GroundAtom("p"))
        system, _ = _make_system(["p"])
        kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset())

        result = build_arguments_for(system, kb, p, include_attackers=False)
        assert len(result) >= 1
        assert any(
            isinstance(a, PremiseArg) and a.is_axiom and a.premise == p
            for a in result
        )

    def test_single_strict_rule(self):
        """p -> q with p as premise, goal=q should produce StrictArg."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        rule = Rule(antecedents=(p,), consequent=q, kind="strict")
        system, _ = _make_system(["p", "q"], strict_rules=[rule])
        kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))

        result = build_arguments_for(system, kb, q, include_attackers=False)
        assert len(result) >= 1
        strict_args = {a for a in result if isinstance(a, StrictArg)}
        assert any(a.rule == rule for a in strict_args)

    def test_single_defeasible_rule(self):
        """p => q with p as premise, goal=q should produce DefeasibleArg."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        rule = Rule(
            antecedents=(p,), consequent=q, kind="defeasible", name="r1"
        )
        system, _ = _make_system(["p", "q"], defeasible_rules=[rule])
        kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))

        result = build_arguments_for(system, kb, q, include_attackers=False)
        assert len(result) >= 1
        def_args = {a for a in result if isinstance(a, DefeasibleArg)}
        assert any(a.rule == rule for a in def_args)

    def test_chain_of_rules(self):
        """p -> q, q -> r with p as premise, goal=r should chain through."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        r = Literal(GroundAtom("r"))
        r1 = Rule(antecedents=(p,), consequent=q, kind="strict")
        r2 = Rule(antecedents=(q,), consequent=r, kind="strict")
        system, _ = _make_system(["p", "q", "r"], strict_rules=[r1, r2])
        kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))

        result = build_arguments_for(system, kb, r, include_attackers=False)
        assert len(result) >= 1
        # Should have argument concluding r
        assert any(conc(a) == r for a in result)

    def test_unreachable_goal(self):
        """Goal with no rules and not in KB should return empty."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        system, _ = _make_system(["p", "q"])
        kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset())

        result = build_arguments_for(system, kb, q, include_attackers=False)
        assert len(result) == 0


# ── Test: attacker inclusion ───────────────────────────────────────


class TestAttackerInclusion:
    def test_contrary_argument_included(self):
        """With include_attackers=True, arguments for ~goal are included."""
        p = Literal(GroundAtom("p"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        system, _ = _make_system(["p"])
        kb = KnowledgeBase(
            axioms=frozenset(), premises=frozenset({p, neg_p})
        )

        result = build_arguments_for(system, kb, p, include_attackers=True)
        conclusions = {conc(a) for a in result}
        assert p in conclusions
        assert neg_p in conclusions

    def test_attackers_excluded_when_disabled(self):
        """With include_attackers=False, only goal arguments returned."""
        p = Literal(GroundAtom("p"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        system, _ = _make_system(["p"])
        kb = KnowledgeBase(
            axioms=frozenset(), premises=frozenset({p, neg_p})
        )

        result = build_arguments_for(system, kb, p, include_attackers=False)
        conclusions = {conc(a) for a in result}
        assert p in conclusions
        assert neg_p not in conclusions

    def test_rule_based_attacker(self):
        """Attacker via rule: s => ~p should be found when querying p."""
        p = Literal(GroundAtom("p"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        s = Literal(GroundAtom("s"))
        rule = Rule(
            antecedents=(s,), consequent=neg_p, kind="defeasible", name="r_attack"
        )
        system, _ = _make_system(["p", "s"], defeasible_rules=[rule])
        kb = KnowledgeBase(
            axioms=frozenset(), premises=frozenset({p, s})
        )

        result = build_arguments_for(system, kb, p, include_attackers=True)
        conclusions = {conc(a) for a in result}
        assert neg_p in conclusions  # attacker found

    def test_attacker_expansion_reaches_reinstatement_depth_three(self):
        """Attacker closure must continue until attack relevance is closed.

        Goal: ``p``.
        Attacker: ``q => ~p``.
        Counter-attacker: ``r => ~q``.
        Counter-counter-attacker: ``s => ~r``.

        The focused result must include ``~r``; a hardcoded two-pass
        expansion stops too early and misses it.
        """

        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        neg_q = Literal(GroundAtom("q"), negated=True)
        neg_r = Literal(GroundAtom("r"), negated=True)
        s = Literal(GroundAtom("s"))
        rules = [
            Rule(
                antecedents=(q,),
                consequent=neg_p,
                kind="defeasible",
                name="r_attack_p",
            ),
            Rule(
                antecedents=(Literal(GroundAtom("r")),),
                consequent=neg_q,
                kind="defeasible",
                name="r_attack_q",
            ),
            Rule(
                antecedents=(s,),
                consequent=neg_r,
                kind="defeasible",
                name="r_attack_r",
            ),
        ]
        system, _ = _make_system(["p", "q", "r", "s"], defeasible_rules=rules)
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p, q, Literal(GroundAtom("r")), s}),
        )

        result = build_arguments_for(system, kb, p, include_attackers=True)
        conclusions = {conc(a) for a in result}

        assert neg_p in conclusions
        assert neg_q in conclusions
        assert neg_r in conclusions


# ── Test: depth limiting ───────────────────────────────────────────


class TestDepthLimiting:
    def test_depth_limit_prevents_deep_chains(self):
        """Deep chain beyond max_depth should be truncated."""
        # Create chain: a0 -> a1 -> a2 -> ... -> a(N)
        N = 15
        atoms = [f"a{i}" for i in range(N + 1)]
        lits = [Literal(GroundAtom(a)) for a in atoms]
        rules = [
            Rule(antecedents=(lits[i],), consequent=lits[i + 1], kind="strict")
            for i in range(N)
        ]
        system, _ = _make_system(atoms, strict_rules=rules)
        kb = KnowledgeBase(axioms=frozenset({lits[0]}), premises=frozenset())

        # With max_depth=5, should NOT reach a15
        result_shallow = build_arguments_for(
            system, kb, lits[N], include_attackers=False, max_depth=5
        )
        assert len(result_shallow) == 0  # can't reach depth 15 with limit 5

        # With max_depth=20, should reach
        result_deep = build_arguments_for(
            system, kb, lits[N], include_attackers=False, max_depth=20
        )
        assert len(result_deep) >= 1

    def test_cyclic_rules_terminate(self):
        """Rules forming a cycle should not cause infinite recursion."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        r1 = Rule(antecedents=(p,), consequent=q, kind="strict")
        r2 = Rule(antecedents=(q,), consequent=p, kind="strict")
        system, _ = _make_system(["p", "q"], strict_rules=[r1, r2])
        kb = KnowledgeBase(axioms=frozenset(), premises=frozenset())

        # Should terminate without error, returning empty (no premises to seed)
        result = build_arguments_for(system, kb, p, include_attackers=False)
        assert isinstance(result, frozenset)


# ── Test: correctness property (subset of exhaustive) ──────────────


class TestCorrectnessProperty:
    """Goal-directed arguments for a conclusion should be exactly
    the subset of exhaustive arguments that conclude that literal
    (when include_attackers=False)."""

    def _check_subset(
        self,
        system: ArgumentationSystem,
        kb: KnowledgeBase,
        goal: Literal,
    ):
        """Verify backward result is subset of forward result."""
        exhaustive = build_arguments(system, kb)
        goal_directed = build_arguments_for(
            system, kb, goal, include_attackers=False
        )
        # Every goal-directed argument must also appear in exhaustive
        assert goal_directed <= exhaustive, (
            f"Goal-directed produced arguments not in exhaustive: "
            f"{goal_directed - exhaustive}"
        )

    def test_simple_system(self):
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        r = Literal(GroundAtom("r"))
        rule1 = Rule(antecedents=(p,), consequent=q, kind="strict")
        rule2 = Rule(antecedents=(q,), consequent=r, kind="defeasible", name="d1")
        system, _ = _make_system(
            ["p", "q", "r"], strict_rules=[rule1], defeasible_rules=[rule2]
        )
        kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset())

        self._check_subset(system, kb, r)
        self._check_subset(system, kb, q)
        self._check_subset(system, kb, p)

    def test_multi_path_system(self):
        """Multiple rules concluding the same literal."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        r = Literal(GroundAtom("r"))
        rule1 = Rule(antecedents=(p,), consequent=r, kind="strict")
        rule2 = Rule(antecedents=(q,), consequent=r, kind="strict")
        system, _ = _make_system(["p", "q", "r"], strict_rules=[rule1, rule2])
        kb = KnowledgeBase(
            axioms=frozenset(), premises=frozenset({p, q})
        )

        self._check_subset(system, kb, r)

    def test_with_attackers_subset(self):
        """With include_attackers=True, result should still be subset of exhaustive."""
        p = Literal(GroundAtom("p"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        q = Literal(GroundAtom("q"))
        rule = Rule(
            antecedents=(q,), consequent=neg_p, kind="defeasible", name="r1"
        )
        system, _ = _make_system(["p", "q"], defeasible_rules=[rule])
        kb = KnowledgeBase(
            axioms=frozenset(), premises=frozenset({p, q})
        )

        exhaustive = build_arguments(system, kb)
        goal_directed = build_arguments_for(
            system, kb, p, include_attackers=True
        )
        assert goal_directed <= exhaustive

    def test_attacks_work_on_goal_directed(self):
        """compute_attacks should work identically on goal-directed results."""
        p = Literal(GroundAtom("p"))
        neg_p = Literal(GroundAtom("p"), negated=True)
        q = Literal(GroundAtom("q"))
        rule = Rule(
            antecedents=(q,), consequent=neg_p, kind="defeasible", name="r1"
        )
        system, _ = _make_system(["p", "q"], defeasible_rules=[rule])
        kb = KnowledgeBase(
            axioms=frozenset(), premises=frozenset({p, q})
        )

        goal_args = build_arguments_for(system, kb, p, include_attackers=True)
        attacks = compute_attacks(goal_args, system)
        # Should find at least one attack (neg_p attacks p)
        assert len(attacks) >= 1


# ── Hypothesis property test ───────────────────────────────────────


@st.composite
def small_aspic_system(draw):
    """Generate a small ASPIC+ system with KB for property testing."""
    pool = ["p", "q", "r", "s"]
    atoms = draw(
        st.lists(st.sampled_from(pool), min_size=2, max_size=4, unique=True)
    )
    literals = [Literal(GroundAtom(a), n) for a in atoms for n in (False, True)]
    language = frozenset(literals)

    contradictory_pairs = frozenset(
        (Literal(GroundAtom(a), False), Literal(GroundAtom(a), True)) for a in atoms
    )
    cfn = ContrarinessFn(contradictories=contradictory_pairs)

    # Generate 0-3 defeasible rules
    num_rules = draw(st.integers(min_value=0, max_value=3))
    rules = []
    for i in range(num_rules):
        num_antes = draw(st.integers(min_value=1, max_value=2))
        antes = draw(
            st.lists(
                st.sampled_from(literals),
                min_size=num_antes,
                max_size=num_antes,
            )
        )
        consequent = draw(st.sampled_from(literals))
        # Skip if consequent is in antecedents
        if consequent in antes:
            continue
        rules.append(
            Rule(
                antecedents=tuple(antes),
                consequent=consequent,
                kind="defeasible",
                name=f"d{i}",
            )
        )

    system = ArgumentationSystem(
        language=language,
        contrariness=cfn,
        strict_rules=frozenset(),
        defeasible_rules=frozenset(rules),
    )

    # KB: draw some literals as axioms or premises
    kb_lits = draw(
        st.lists(st.sampled_from(literals), min_size=1, max_size=4, unique=True)
    )
    # Split into axioms and premises
    axioms = []
    premises = []
    for lit in kb_lits:
        if draw(st.booleans()):
            axioms.append(lit)
        else:
            premises.append(lit)

    kb = KnowledgeBase(
        axioms=frozenset(axioms), premises=frozenset(premises)
    )

    # Pick a goal from the language
    goal = draw(st.sampled_from(literals))

    return system, kb, goal


@given(data=small_aspic_system())
@settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None,
)
def test_backward_subset_of_forward(data):
    """Property: build_arguments_for(goal) ⊆ build_arguments() for any goal.

    Every argument produced by goal-directed backward chaining must also
    be produced by exhaustive forward construction. This is the fundamental
    correctness invariant.
    """
    system, kb, goal = data
    exhaustive = build_arguments(system, kb)
    goal_directed = build_arguments_for(
        system, kb, goal, include_attackers=False
    )
    assert goal_directed <= exhaustive, (
        f"Goal-directed produced arguments not in exhaustive.\n"
        f"Goal: {goal}\n"
        f"Extra: {goal_directed - exhaustive}"
    )


@given(data=small_aspic_system())
@settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None,
)
def test_backward_with_attackers_subset_of_forward(data):
    """Property: build_arguments_for(goal, include_attackers=True) ⊆ build_arguments().

    Even with attacker inclusion, every argument must appear in the
    exhaustive forward result.
    """
    system, kb, goal = data
    exhaustive = build_arguments(system, kb)
    goal_directed = build_arguments_for(
        system, kb, goal, include_attackers=True
    )
    assert goal_directed <= exhaustive, (
        f"Goal-directed+attackers produced arguments not in exhaustive.\n"
        f"Goal: {goal}\n"
        f"Extra: {goal_directed - exhaustive}"
    )


@given(data=small_aspic_system())
@settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None,
)
def test_backward_finds_all_goal_conclusions(data):
    """Property: every exhaustive argument concluding goal should appear
    in the goal-directed result (completeness for the goal literal).

    build_arguments_for(goal, include_attackers=False) should contain
    every argument from build_arguments() whose conclusion is the goal.
    """
    system, kb, goal = data
    exhaustive = build_arguments(system, kb)
    goal_directed = build_arguments_for(
        system, kb, goal, include_attackers=False
    )
    # All exhaustive arguments concluding goal should be in goal_directed
    exhaustive_for_goal = frozenset(a for a in exhaustive if conc(a) == goal)
    assert exhaustive_for_goal <= goal_directed, (
        f"Goal-directed missed arguments concluding {goal}.\n"
        f"Missing: {exhaustive_for_goal - goal_directed}"
    )
