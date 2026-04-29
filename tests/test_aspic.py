"""Tests for ASPIC+ logical language, contrariness, rules, and transposition.

Property-based tests verify formal definitions from:
    Modgil, S. & Prakken, H. (2018). A general account of argumentation
    with preferences. Artificial Intelligence, 248, 51-104.
    - Def 1 (p.8): Logical language L
    - Def 2 (p.8): Contrariness function, contradictories vs contraries
    - Def 2 (p.8): Strict rules R_s, defeasible rules R_d, naming function n
    - Def 12 (p.13): Transposition closure for strict rules

    Prakken, H. (2010). An abstract framework for argumentation with
    structured arguments. Argument & Computation, 1(2), 93-124.
    - Def 3.1: Argumentation system tuple
    - Def 3.2: Contrariness — symmetric (contradictory) vs asymmetric (contrary)
    - Def 3.4 (p.47-48): Strict vs defeasible rules
    - Def 5.1 (p.141-142): Transposition of strict rules
    - Def 5.2: Closure under transposition

Concrete regression tests verify hand-constructed examples.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings, assume
from hypothesis import strategies as st

from argumentation.aspic import (
    Literal, GroundAtom, ContrarinessFn, Rule, transposition_closure,
    PremiseArg, StrictArg, DefeasibleArg, Argument, Attack,
    KnowledgeBase, ArgumentationSystem, PreferenceConfig,
    build_arguments, compute_attacks, compute_defeats,
    _set_strictly_less, _strictly_weaker, _is_preference_independent_attack,
    conc, prem, sub, top_rule,
    def_rules, last_def_rules, prem_p, is_firm, is_strict,
    CSAF, is_c_consistent, strict_closure,
)
from argumentation.dung import (
    ArgumentationFramework,
    complete_extensions,
    grounded_extension,
    conflict_free,
)


# ── Hypothesis strategies ───────────────────────────────────────────


@st.composite
def logical_language(draw, max_atoms=4):
    """Generate a logical language L with contrariness function.

    Modgil & Prakken 2018, Defs 1-2 (p.8).
    L consists of atoms and their negations.
    Contradictory pairs: (p, ~p) are symmetric — if φ ∈ ¯ψ then ψ ∈ ¯φ.
    """
    pool = ["p", "q", "r", "s", "t"]
    # Draw 2-4 distinct atoms
    atoms = draw(
        st.lists(
            st.sampled_from(pool),
            min_size=2,
            max_size=max_atoms,
            unique=True,
        )
    )
    # Build literals: each atom and its negation
    literals = frozenset(
        Literal(atom=GroundAtom(a), negated=n) for a in atoms for n in (False, True)
    )
    # Build contrariness function: each atom and its negation are contradictories
    contradictory_pairs = frozenset(
        (Literal(atom=GroundAtom(a), negated=False), Literal(atom=GroundAtom(a), negated=True))
        for a in atoms
    )
    cfn = ContrarinessFn(contradictories=contradictory_pairs)
    return literals, cfn


# ── Property tests ─────────────────────────────────────────────────


class TestLanguageProperties:
    """Property tests for logical language L.

    Every property cites the formal definition it verifies.
    """

    @given(logical_language())
    @settings(deadline=None)
    def test_every_literal_has_negation_in_L(self, lang_cfn):
        """For every literal in L, its .contrary is also in L.

        Modgil & Prakken 2018, Def 1 (p.8): L is closed —
        every formula's contraries/contradictories are in L.
        """
        L, _cfn = lang_cfn
        for lit in L:
            assert lit.contrary in L, (
                f"{lit}.contrary = {lit.contrary} not in L"
            )

    @given(logical_language())
    @settings(deadline=None)
    def test_contrary_is_involutory(self, lang_cfn):
        """For every literal a in L, a.contrary.contrary == a.

        Negation is an involution: applying it twice returns
        the original formula. Follows from the symmetric structure
        of contradictories (Modgil & Prakken 2018, Def 2, p.8).
        """
        L, _cfn = lang_cfn
        for lit in L:
            assert lit.contrary.contrary == lit, (
                f"{lit}.contrary.contrary = {lit.contrary.contrary} != {lit}"
            )

    @given(logical_language())
    @settings(deadline=None)
    def test_contradictories_are_symmetric(self, lang_cfn):
        """If (a, b) is a contradictory pair, then (b, a) is also.

        Modgil & Prakken 2018, Def 2 (p.8): φ and ψ are contradictories
        iff φ ∈ ¯ψ AND ψ ∈ ¯φ (symmetric relation).
        Prakken 2010, Def 3.2: same symmetry condition.
        """
        L, cfn = lang_cfn
        for a in L:
            for b in L:
                if cfn.is_contradictory(a, b):
                    assert cfn.is_contradictory(b, a), (
                        f"({a}, {b}) contradictory but ({b}, {a}) is not"
                    )

    @given(logical_language())
    @settings(deadline=None)
    def test_no_self_contrary(self, lang_cfn):
        """No literal is contrary or contradictory to itself.

        A formula cannot be its own contrary or contradictory —
        self-conflict is not permitted in a well-formed language.
        Modgil & Prakken 2018, Def 2 (p.8): contrariness maps
        formulas to *other* formulas.
        """
        L, cfn = lang_cfn
        for lit in L:
            assert not cfn.is_contrary(lit, lit), (
                f"{lit} is contrary to itself"
            )
            assert not cfn.is_contradictory(lit, lit), (
                f"{lit} is contradictory to itself"
            )

    @given(logical_language())
    @settings(deadline=None)
    def test_language_nonempty(self, lang_cfn):
        """L has at least 2 literals (an atom and its negation).

        A language must contain at least one atom and its negation
        to support any argumentation. Follows from the strategy
        drawing min_size=2 atoms, each producing 2 literals.
        """
        L, _cfn = lang_cfn
        assert len(L) >= 2

    @given(logical_language())
    @settings(deadline=None)
    def test_language_even_size(self, lang_cfn):
        """|L| is even: every atom has exactly one negation.

        Since L is built from atoms and their negations, each atom
        contributes exactly 2 literals. |L| = 2 * |atoms|.
        """
        L, _cfn = lang_cfn
        assert len(L) % 2 == 0, f"|L| = {len(L)} is odd"


# ── Concrete regression tests ──────────────────────────────────────


class TestLanguageConcrete:
    """Hand-constructed examples for verifying language properties."""

    def test_simple_two_atom_language(self):
        """Manually construct L = {p, ~p, q, ~q}.

        Contradictories: {(p, ~p), (~p, p), (q, ~q), (~q, q)}.
        Verifies all properties from TestLanguageProperties hold
        on a concrete, known-good instance.
        """
        p = Literal(atom=GroundAtom("p"), negated=False)
        not_p = Literal(atom=GroundAtom("p"), negated=True)
        q = Literal(atom=GroundAtom("q"), negated=False)
        not_q = Literal(atom=GroundAtom("q"), negated=True)

        L = frozenset({p, not_p, q, not_q})

        contradictory_pairs = frozenset({(p, not_p), (q, not_q)})
        cfn = ContrarinessFn(contradictories=contradictory_pairs)

        # Every literal's negation is in L
        for lit in L:
            assert lit.contrary in L

        # Involution
        for lit in L:
            assert lit.contrary.contrary == lit

        # Contradictories are symmetric
        assert cfn.is_contradictory(p, not_p)
        assert cfn.is_contradictory(not_p, p)
        assert cfn.is_contradictory(q, not_q)
        assert cfn.is_contradictory(not_q, q)

        # No self-contrary
        for lit in L:
            assert not cfn.is_contrary(lit, lit)
            assert not cfn.is_contradictory(lit, lit)

        # Non-empty and even
        assert len(L) == 4
        assert len(L) % 2 == 0

        # Cross-atom pairs are not contradictory
        assert not cfn.is_contradictory(p, q)
        assert not cfn.is_contradictory(p, not_q)
        assert not cfn.is_contradictory(not_p, q)
        assert not cfn.is_contradictory(not_p, not_q)

    def test_asymmetric_contrary_is_one_way(self):
        """A contrary is directional, while contradictories remain symmetric."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        cfn = ContrarinessFn(
            contradictories=frozenset(),
            contraries=frozenset({(p, q)}),
        )

        assert cfn.is_contrary(p, q) is True
        assert cfn.is_contrary(q, p) is False
        assert cfn.is_contradictory(p, q) is False

    def test_asymmetric_contrary_generates_one_way_attack(self):
        """Only the attacking direction licensed by the contrary should appear."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        system = ArgumentationSystem(
            language=frozenset({p, q}),
            contrariness=ContrarinessFn(
                contradictories=frozenset(),
                contraries=frozenset({(p, q)}),
            ),
            strict_rules=frozenset(),
            defeasible_rules=frozenset(),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p, q}),
        )

        arg_p = PremiseArg(premise=p, is_axiom=False)
        arg_q = PremiseArg(premise=q, is_axiom=False)

        attacks = compute_attacks(build_arguments(system, kb), system)
        attack_pairs = {(attack.attacker, attack.target) for attack in attacks}

        assert (arg_p, arg_q) in attack_pairs
        assert (arg_q, arg_p) not in attack_pairs


# ── Phase 2: Rule strategies ─────────────────────────────────────


@st.composite
def strict_rules(draw, language, contrariness, max_rules=4):
    """Generate strict rules over L with transposition closure.

    Modgil & Prakken 2018, Defs 2, 12 (pp.8, 13).
    Prakken 2010, Defs 3.4, 5.1-5.2 (pp.47-48, 141-142).

    1. Draw 0-max_rules seed rules with 1-2 antecedents from L, consequent from L.
    2. Filter: consequent not in antecedents.
    3. Compute transposition closure (calls transposition_closure which does not
       exist yet -- tests will fail with ImportError in red phase).
    4. Return the closed rule set.
    """
    L_list = sorted(language, key=repr)
    n_rules = draw(st.integers(min_value=0, max_value=max_rules))
    seed_rules: list[Rule] = []
    for _ in range(n_rules):
        n_ante = draw(st.integers(min_value=1, max_value=min(2, len(L_list))))
        antecedents = tuple(
            draw(st.sampled_from(L_list)) for _ in range(n_ante)
        )
        consequent = draw(st.sampled_from(L_list))
        # Filter: consequent must not appear in antecedents
        if consequent in antecedents:
            continue
        seed_rules.append(
            Rule(
                antecedents=antecedents,
                consequent=consequent,
                kind="strict",
                name=None,
            )
        )
    closed, _post_language = transposition_closure(
        frozenset(seed_rules),
        language,
        contrariness,
    )
    return closed


@st.composite
def strict_seed_rules(draw, language, contrariness, max_rules=4):
    """Generate well-formed strict seed rules before transposition closure."""
    L_list = sorted(language, key=repr)
    n_rules = draw(st.integers(min_value=0, max_value=max_rules))
    seed_rules: list[Rule] = []
    for _ in range(n_rules):
        n_ante = draw(st.integers(min_value=1, max_value=min(2, len(L_list))))
        antecedents = tuple(
            draw(st.sampled_from(L_list)) for _ in range(n_ante)
        )
        consequent = draw(st.sampled_from(L_list))
        if consequent in antecedents:
            continue
        if any(
            contrariness.is_contradictory(left, right)
            for index, left in enumerate(antecedents)
            for right in antecedents[index + 1:]
        ):
            continue
        seed_rules.append(
            Rule(
                antecedents=antecedents,
                consequent=consequent,
                kind="strict",
                name=None,
            )
        )
    return frozenset(seed_rules)


def _contradictories_in_language(
    literal: Literal,
    language: frozenset[Literal],
    contrariness: ContrarinessFn,
) -> tuple[Literal, ...]:
    return tuple(
        sorted(
            (
                other
                for other in language
                if other != literal and contrariness.is_contradictory(literal, other)
            ),
            key=repr,
        )
    )


def _schema_transpositions(
    rule: Rule,
    language: frozenset[Literal],
    contrariness: ContrarinessFn,
) -> frozenset[Rule]:
    transpositions: set[Rule] = set()
    if rule.kind != "strict":
        return frozenset()
    for index, antecedent in enumerate(rule.antecedents):
        for contrary_consequent in _contradictories_in_language(
            rule.consequent,
            language,
            contrariness,
        ):
            for contrary_antecedent in _contradictories_in_language(
                antecedent,
                language,
                contrariness,
            ):
                transposed_antecedents = list(rule.antecedents)
                transposed_antecedents[index] = contrary_consequent
                if contrary_antecedent in transposed_antecedents:
                    continue
                candidate = Rule(
                    antecedents=tuple(transposed_antecedents),
                    consequent=contrary_antecedent,
                    kind="strict",
                    name=None,
                )
                if any(
                    contrariness.is_contradictory(left, right)
                    for left_index, left in enumerate(candidate.antecedents)
                    for right in candidate.antecedents[left_index + 1:]
                ):
                    continue
                transpositions.add(candidate)
    return frozenset(transpositions)


@st.composite
def defeasible_rules(draw, language, max_rules=4):
    """Generate defeasible rules with naming function.

    Modgil & Prakken 2018, Def 2 (p.8): each defeasible rule r has a
    name n(r) in L, enabling undercutting attacks on the inference step.

    Prakken 2010, Def 3.4 (p.47-48): defeasible rules use => (presumptive).

    Names are strings "d0", "d1", etc. — these are rule identifiers, not
    Literals. The name-Literals are created during argument construction
    in Phase 3.
    """
    L_list = sorted(language, key=repr)
    n_rules = draw(st.integers(min_value=0, max_value=max_rules))
    rules: list[Rule] = []
    for i in range(n_rules):
        n_ante = draw(st.integers(min_value=1, max_value=min(2, len(L_list))))
        antecedents = tuple(
            draw(st.sampled_from(L_list)) for _ in range(n_ante)
        )
        consequent = draw(st.sampled_from(L_list))
        # Filter: consequent must not appear in antecedents
        if consequent in antecedents:
            continue
        rules.append(
            Rule(
                antecedents=antecedents,
                consequent=consequent,
                kind="defeasible",
                name=f"d{i}",
            )
        )
    return frozenset(rules)


# ── Phase 2: Rule property tests ─────────────────────────────────


class TestRuleProperties:
    """Property tests for strict and defeasible rules.

    Verifies structural invariants of rules generated by the strategies.
    Modgil & Prakken 2018, Def 2 (p.8); Prakken 2010, Def 3.4 (p.47-48).
    """

    pytestmark = pytest.mark.property

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_strict_rules_all_strict(self, lc_rules):
        """Every rule from strict_rules() has kind == 'strict'.

        Modgil & Prakken 2018, Def 2 (p.8): R_s contains only strict rules.
        """
        (_L, _cfn), rules = lc_rules
        for r in rules:
            assert r.kind == "strict", f"Rule {r} has kind={r.kind}, expected 'strict'"

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            defeasible_rules(language=lc[0]),
        )
    ))
    @settings(deadline=None)
    def test_defeasible_rules_all_defeasible(self, lc_rules):
        """Every rule from defeasible_rules() has kind == 'defeasible'.

        Modgil & Prakken 2018, Def 2 (p.8): R_d contains only defeasible rules.
        """
        (_L, _cfn), rules = lc_rules
        for r in rules:
            assert r.kind == "defeasible", (
                f"Rule {r} has kind={r.kind}, expected 'defeasible'"
            )

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            defeasible_rules(language=lc[0]),
        )
    ))
    @settings(deadline=None)
    def test_defeasible_rules_all_named(self, lc_rules):
        """Every defeasible rule has name is not None.

        Modgil & Prakken 2018, Def 2 (p.8): the naming function n maps
        each defeasible rule to a name n(r), enabling undercutting attacks.
        """
        (_L, _cfn), rules = lc_rules
        for r in rules:
            assert r.name is not None, f"Defeasible rule {r} has no name"

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_rules(language=lc[0], contrariness=lc[1]),
            defeasible_rules(language=lc[0]),
        )
    ))
    @settings(deadline=None)
    def test_rule_antecedents_in_language(self, lc_sr_dr):
        """All antecedents and consequents are in L.

        Modgil & Prakken 2018, Def 2 (p.8): rules are over the language L.
        Prakken 2010, Def 3.4 (p.47-48): antecedents and consequent in L.
        """
        (L, _cfn), s_rules, d_rules = lc_sr_dr
        for r in s_rules | d_rules:
            for ante in r.antecedents:
                assert ante in L, f"Antecedent {ante} of rule {r} not in L"
            assert r.consequent in L, f"Consequent {r.consequent} of rule {r} not in L"

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_rules(language=lc[0], contrariness=lc[1]),
            defeasible_rules(language=lc[0]),
        )
    ))
    @settings(deadline=None)
    def test_consequent_not_in_antecedents(self, lc_sr_dr):
        """No rule has its consequent appearing in its antecedents.

        A rule phi_1, ..., phi_n -> psi must have psi not in {phi_1, ..., phi_n}.
        This is a well-formedness constraint: a rule cannot trivially conclude
        one of its own premises.
        """
        (L, _cfn), s_rules, d_rules = lc_sr_dr
        for r in s_rules | d_rules:
            assert r.consequent not in r.antecedents, (
                f"Rule {r} has consequent {r.consequent} in antecedents"
            )


class TestTranspositionClosure:
    """Property tests for transposition closure of strict rules.

    Modgil & Prakken 2018, Def 12 (p.13): if A1,...,An -> C is a strict
    rule, then for each i, A1,...,~C,...,An -> ~Ai must also be in R_s.

    Prakken 2010, Defs 5.1-5.2 (pp.141-142): transposition and closure.

    Theorem 6.10 (Prakken 2010): closure under transposition is REQUIRED
    for the rationality postulates to hold.
    """

    pytestmark = pytest.mark.property

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_seed_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_transposition_closure_is_extensive_for_well_formed_seed_rules(self, lc_rules):
        """Seed strict rules are retained by closure.

        Grounded in
        `papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-012.png`:
        Prakken 2010 Defs. 5.1-5.2 define closure by adding transpositions.
        """
        (language, cfn), seed_rules = lc_rules

        closed, _post_language = transposition_closure(seed_rules, language, cfn)
        assert seed_rules <= closed

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_seed_rules(language=lc[0], contrariness=lc[1]),
            strict_seed_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_transposition_closure_is_monotone_over_added_seed_rules(self, lc_rules):
        """Adding strict rules cannot shrink the transposition closure.

        Grounded in
        `papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-012.png`.
        """
        (language, cfn), seed_rules, added_rules = lc_rules

        closed_seed, _seed_language = transposition_closure(seed_rules, language, cfn)
        closed_union, _union_language = transposition_closure(
            seed_rules | added_rules,
            language,
            cfn,
        )

        assert closed_seed <= closed_union

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_seed_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_every_added_rule_matches_prakken_2010_page_12_transposition_schema(self, lc_rules):
        """Every non-seed closure member is generated by the transposition schema.

        Grounded in
        `papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-012.png`:
        replacing one antecedent with a contradictory of the consequent yields
        a strict rule whose consequent is a contradictory of that antecedent.
        """
        (language, cfn), seed_rules = lc_rules
        closed, _post_language = transposition_closure(seed_rules, language, cfn)
        schema_rules = frozenset(
            transposed
            for rule in closed
            for transposed in _schema_transpositions(rule, language, cfn)
        )

        assert closed - seed_rules <= schema_rules

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_transposition_closure_complete(self, lc_rules):
        """For every strict rule A1,...,An -> C, for every i, the transposed
        rule A1,...,~C,...,An -> ~Ai exists in R_s.

        Modgil & Prakken 2018, Def 12 (p.13).
        Prakken 2010, Def 5.1 (p.141-142): a transposition of
        phi_1,...,phi_n -> psi is phi_1,...,-psi,...,phi_n -> -phi_i.
        """
        (L, _cfn), rules = lc_rules
        for r in rules:
            for i, ante_i in enumerate(r.antecedents):
                # Build the transposed rule: replace antecedent i with ~C,
                # consequent becomes ~ante_i
                transposed_antes = list(r.antecedents)
                transposed_antes[i] = r.consequent.contrary
                transposed = Rule(
                    antecedents=tuple(transposed_antes),
                    consequent=ante_i.contrary,
                    kind="strict",
                    name=None,
                )
                assert transposed in rules, (
                    f"Transposition of {r} at position {i} missing: {transposed}"
                )

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_transposition_closure_idempotent(self, lc_rules):
        """Applying transposition_closure again produces no new rules.

        Prakken 2010, Def 5.2: Cl_{R_s}(R_s) is the smallest set closed
        under transposition. Applying closure to an already-closed set
        must be a fixed point.
        """
        (L, cfn), rules = lc_rules
        closed_again, _post_language = transposition_closure(rules, L, cfn)
        assert closed_again == rules, (
            f"Closure not idempotent: {len(closed_again)} rules vs {len(rules)}"
        )

    @given(logical_language().flatmap(
        lambda lc: st.tuples(
            st.just(lc),
            strict_rules(language=lc[0], contrariness=lc[1]),
        )
    ))
    @settings(deadline=None)
    def test_transposition_closure_preserves_kind(self, lc_rules):
        """All transposed rules have kind == 'strict'.

        Transposition applies only to strict rules and produces strict rules.
        Modgil & Prakken 2018, Def 12 (p.13): transposition is defined
        only for strict rules in R_s.
        """
        (_L, _cfn), rules = lc_rules
        for r in rules:
            assert r.kind == "strict", (
                f"Transposed rule {r} has kind={r.kind}, expected 'strict'"
            )

    def test_empty_rules_closure_is_empty(self):
        """Transposition closure of the empty set is the empty set.

        Trivial base case: no rules means no transpositions to generate.
        """
        L = frozenset({Literal(GroundAtom("p")), Literal(GroundAtom("p"), negated=True)})
        cfn = ContrarinessFn(
            contradictories=frozenset({(Literal(GroundAtom("p")), Literal(GroundAtom("p"), negated=True))})
        )
        result, _post_language = transposition_closure(frozenset(), L, cfn)
        assert result == frozenset(), f"Expected empty set, got {result}"

    def test_transposition_closure_does_not_erase_unrelated_rules_on_singleton_inconsistency(self):
        """Transposition closure must not wipe out unrelated strict rules.

        Prakken 2010, Defs 5.1-5.3 (pp. 141-142; local page image
        ``papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-012.png``)
        defines closure under transposition purely as the least fixpoint under
        adding transpositions. It does not say to delete the whole strict theory
        when one singleton closure is inconsistent.
        """

        p = Literal(GroundAtom("p"))
        not_p = Literal(GroundAtom("p"), negated=True)
        q = Literal(GroundAtom("q"))
        not_q = Literal(GroundAtom("q"), negated=True)
        r = Literal(GroundAtom("r"))
        not_r = Literal(GroundAtom("r"), negated=True)
        s = Literal(GroundAtom("s"))
        not_s = Literal(GroundAtom("s"), negated=True)
        language = frozenset({p, not_p, q, not_q, r, not_r, s, not_s})
        cfn = ContrarinessFn(
            contradictories=frozenset({
                (p, not_p),
                (q, not_q),
                (r, not_r),
                (s, not_s),
            })
        )
        unrelated = Rule(antecedents=(r,), consequent=s, kind="strict")
        rules = frozenset(
            {
                Rule(antecedents=(not_p,), consequent=q, kind="strict"),
                Rule(antecedents=(q,), consequent=p, kind="strict"),
                unrelated,
            }
        )

        closed, _post_language = transposition_closure(rules, language, cfn)

        assert unrelated in closed
        assert closed != frozenset()

    def test_transposition_closure_uses_explicit_contradictories_from_contrariness(self):
        """Transposition must follow the supplied contradictory relation.

        Prakken 2010, Def. 5.1 (p. 141; local page image
        ``papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-012.png``)
        defines transposition with the argumentation system's ``-`` operator.
        If ``-`` is represented by ``ContrarinessFn``, the implementation must
        use that relation instead of hard-coding ``Literal.contrary``.
        """

        p = Literal(GroundAtom("p"))
        not_p = Literal(GroundAtom("p"), negated=True)
        q = Literal(GroundAtom("q"))
        not_q = Literal(GroundAtom("q"), negated=True)
        r = Literal(GroundAtom("r"))
        not_r = Literal(GroundAtom("r"), negated=True)
        s = Literal(GroundAtom("s"))
        not_s = Literal(GroundAtom("s"), negated=True)
        language = frozenset({p, not_p, q, not_q, r, not_r, s, not_s})
        cfn = ContrarinessFn(
            contradictories=frozenset({
                (p, q),
                (not_p, not_q),
                (r, s),
                (not_r, not_s),
            })
        )
        original = Rule(antecedents=(p,), consequent=r, kind="strict")

        closed, _post_language = transposition_closure(frozenset({original}), language, cfn)

        assert Rule(antecedents=(s,), consequent=q, kind="strict") in closed


class TestRuleConcrete:
    """Hand-constructed examples for verifying rule and transposition properties."""

    def test_married_bachelor_transposition(self):
        """Classic example: married -> ~bachelor transposes to bachelor -> ~married.

        Modgil & Prakken 2014, Example 4.4.
        Prakken 2010, Def 5.1 (p.141-142).

        Given strict rule: married -> ~bachelor
        Transposition must produce: bachelor -> ~married
        (Replace the single antecedent 'married' with ~(~bachelor) = bachelor,
         and the consequent becomes ~married.)
        """
        married = Literal(GroundAtom("married"))
        not_married = Literal(GroundAtom("married"), negated=True)
        bachelor = Literal(GroundAtom("bachelor"))
        not_bachelor = Literal(GroundAtom("bachelor"), negated=True)

        L = frozenset({married, not_married, bachelor, not_bachelor})
        cfn = ContrarinessFn(
            contradictories=frozenset({
                (married, not_married),
                (bachelor, not_bachelor),
            })
        )

        # Original rule: married -> ~bachelor
        original = Rule(
            antecedents=(married,),
            consequent=not_bachelor,
            kind="strict",
            name=None,
        )

        # Expected transposition: bachelor -> ~married
        # (ante[0]=married replaced by ~(~bachelor)=bachelor, consequent=~married)
        expected_transposition = Rule(
            antecedents=(bachelor,),
            consequent=not_married,
            kind="strict",
            name=None,
        )

        # Compute closure
        closed, _post_language = transposition_closure(frozenset({original}), L, cfn)

        # Original must be preserved
        assert original in closed, "Original rule missing from closure"

        # Transposition must be present
        assert expected_transposition in closed, (
            f"Expected transposition {expected_transposition} not in closure: {closed}"
        )


# ── Phase 3: Knowledge base strategy ─────────────────────────────


@st.composite
def knowledge_base(draw, language, strict_rules, defeasible_rules):
    """Generate a knowledge base with non-triviality guarantee.

    Modgil & Prakken 2018, Def 4 (p.9): K = K_n ∪ K_p where
    K_n (axioms) are not attackable, K_p (ordinary premises) are attackable.

    Non-triviality: forces at least one rule's antecedents into K_p,
    ensuring at least one non-premise argument can be constructed.
    See reports/hypothesis-aspic-feasibility.md Section 3, Level 4.
    """
    L_list = sorted(language, key=repr)
    all_rules = list(strict_rules) + list(defeasible_rules)

    # Force at least one rule's antecedents into K_p for non-triviality
    forced_premises: frozenset[Literal] = frozenset()
    if all_rules:
        target = draw(st.sampled_from(all_rules))
        forced_premises = frozenset(target.antecedents)

    # Draw additional K_p members from L (up to 4 total)
    extra_kp = draw(
        st.frozensets(st.sampled_from(L_list), max_size=4)
    )
    K_p = forced_premises | extra_kp

    # Draw K_n members from L (up to 2), ensuring consistency
    # (no literal and its contrary both in K_n)
    K_n_candidates = draw(
        st.frozensets(st.sampled_from(L_list), max_size=2)
    )
    # Filter: no contradictory pair in K_n
    K_n = frozenset()
    for lit in K_n_candidates:
        if lit.contrary not in K_n:
            K_n = K_n | {lit}

    # Ensure K_n and K_p are disjoint
    K_n = K_n - K_p

    return KnowledgeBase(axioms=K_n, premises=K_p)


@st.composite
def well_defined_knowledge_base(draw, language, strict_rules, defeasible_rules, contrariness):
    """Generate a KB whose axioms and full base are c-consistent."""
    L_list = sorted(language, key=repr)
    all_rules = list(strict_rules) + list(defeasible_rules)

    forced_premises: frozenset[Literal] = frozenset()
    candidate_rules = [
        rule for rule in all_rules
        if is_c_consistent(frozenset(rule.antecedents), strict_rules, contrariness)
    ]
    if candidate_rules:
        target = draw(st.sampled_from(candidate_rules))
        forced_premises = frozenset(target.antecedents)

    extra_kp = draw(
        st.frozensets(st.sampled_from(L_list), max_size=4)
    )
    K_p = frozenset(forced_premises)
    for lit in extra_kp:
        tentative = K_p | {lit}
        if is_c_consistent(tentative, strict_rules, contrariness):
            K_p = tentative

    K_n_candidates = draw(
        st.frozensets(st.sampled_from(L_list), max_size=2)
    )
    K_n = frozenset()
    for lit in K_n_candidates:
        if lit in K_p:
            continue
        tentative = K_n | {lit}
        if (
            is_c_consistent(tentative, strict_rules, contrariness)
            and is_c_consistent(tentative | K_p, strict_rules, contrariness)
        ):
            K_n = tentative

    # Guard the full knowledge base, not just the incremental construction path.
    # This keeps the rationality-postulate generators on genuinely well-defined
    # c-SAF inputs even when Hypothesis shrinks toward edge cases.
    assume(is_c_consistent(K_n | K_p, strict_rules, contrariness))
    return KnowledgeBase(axioms=K_n, premises=K_p)


# ── Phase 3: Argument construction property tests ─────────────────


class TestArgumentConstructionProperties:
    """Property tests for recursive argument construction.

    Modgil & Prakken 2018, Def 5 (pp.9-10): arguments are constructed
    recursively from premises and rules, with computed properties
    Prem(A), Conc(A), Sub(A), DefRules(A), TopRule(A), LastDefRules(A).

    Prakken 2010, Def 3.6 (p.36): argument construction.
    """

    @given(data=st.data())
    @settings(deadline=None)
    def test_premise_arg_conclusion_equals_premise(self, data):
        """For every PremiseArg A, conc(A) == A.premise.

        Modgil & Prakken 2018, Def 5 clause 1 (p.9): if phi in K
        then Conc(A) = phi.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            if isinstance(arg, PremiseArg):
                assert conc(arg) == arg.premise, (
                    f"PremiseArg conclusion {conc(arg)} != premise {arg.premise}"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_sub_contains_self(self, data):
        """For every argument A, A in sub(A).

        Modgil & Prakken 2018, Def 5 (p.9-10): Sub(A) always
        includes A itself.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            assert arg in sub(arg), (
                f"Argument {arg} not in its own sub-arguments"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_sub_transitively_closed(self, data):
        """For every A, for every B in sub(A), sub(B) ⊆ sub(A).

        Modgil & Prakken 2018, Def 5 (p.9-10): Sub is defined
        recursively as Sub(A1) ∪ ... ∪ Sub(An) ∪ {A}, which
        makes it transitively closed by construction.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            for b in sub(arg):
                assert sub(b) <= sub(arg), (
                    f"sub({b}) not subset of sub({arg})"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_prem_subset_of_kb(self, data):
        """For every argument A, prem(A) ⊆ K_n ∪ K_p.

        Modgil & Prakken 2018, Def 5 (p.9): premises come from K.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        all_kb = kb.axioms | kb.premises
        for arg in arguments:
            assert prem(arg) <= all_kb, (
                f"prem({arg}) = {prem(arg)} not subset of K = {all_kb}"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_every_built_argument_is_c_consistent(self, data):
        """Public build_arguments() should emit only c-consistent arguments."""
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            assert is_c_consistent(prem(arg), system.strict_rules, system.contrariness)

    @given(data=st.data())
    @settings(deadline=None)
    def test_conc_in_language(self, data):
        """For every argument A, conc(A) in L.

        Modgil & Prakken 2018, Def 5 (p.9-10): conclusions are
        formulas in the logical language L.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            assert conc(arg) in L, (
                f"conc({arg}) = {conc(arg)} not in L"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_rule_args_antecedents_match(self, data):
        """For every StrictArg/DefeasibleArg A, the conclusions of
        A.sub_args match the antecedents of A.rule.

        Modgil & Prakken 2018, Def 5 clauses 2-3 (p.9-10): if
        A1,...,An are arguments and their conclusions match a rule's
        antecedents, then the compound is an argument.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            if isinstance(arg, (StrictArg, DefeasibleArg)):
                sub_concs = tuple(conc(sa) for sa in arg.sub_args)
                assert sub_concs == arg.rule.antecedents, (
                    f"Sub-arg conclusions {sub_concs} != "
                    f"rule antecedents {arg.rule.antecedents}"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_def_rules_empty_for_premise(self, data):
        """For every PremiseArg A, def_rules(A) == frozenset().

        Modgil & Prakken 2018, Def 5 clause 1 (p.9):
        DefRules(A) = ∅ for premise arguments.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            if isinstance(arg, PremiseArg):
                assert def_rules(arg) == frozenset(), (
                    f"PremiseArg has non-empty def_rules: {def_rules(arg)}"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_def_rules_includes_top_for_defeasible(self, data):
        """For every DefeasibleArg A, A.rule in def_rules(A).

        Modgil & Prakken 2018, Def 5 clause 3 (p.9-10):
        DefRules(A) = DefRules(A1) ∪ ... ∪ DefRules(An) ∪ {TopRule(A)}.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            if isinstance(arg, DefeasibleArg):
                assert arg.rule in def_rules(arg), (
                    f"DefeasibleArg top rule {arg.rule} not in "
                    f"def_rules: {def_rules(arg)}"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_is_firm_iff_prem_subset_kn(self, data):
        """is_firm(A) iff prem(A) ⊆ kb.axioms.

        Modgil & Prakken 2018, Def 5 / Prakken 2010 Def 3.8:
        an argument is firm iff all its premises are axioms (K_n).
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            expected = prem(arg) <= kb.axioms
            assert is_firm(arg) == expected, (
                f"is_firm({arg}) = {is_firm(arg)}, "
                f"but prem(A) <= K_n is {expected}"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_is_strict_iff_no_def_rules(self, data):
        """is_strict(A) iff def_rules(A) == frozenset().

        Modgil & Prakken 2018, Def 5 / Prakken 2010 Def 3.8:
        an argument is strict iff it uses no defeasible rules.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        for arg in arguments:
            expected = def_rules(arg) == frozenset()
            assert is_strict(arg) == expected, (
                f"is_strict({arg}) = {is_strict(arg)}, "
                f"but def_rules empty is {expected}"
            )

    @given(data=st.data())
    @settings(deadline=None, suppress_health_check=[HealthCheck.filter_too_much])
    def test_firm_strict_exist_when_kn_nonempty(self, data):
        """When K_n is nonempty, at least one argument is both firm and strict.

        Modgil & Prakken 2018, Def 5 clause 1 (p.9): every phi in K
        is a PremiseArg. If phi in K_n, the argument is firm (prem ⊆ K_n)
        and strict (no defeasible rules). So K_n nonempty guarantees at
        least one firm+strict argument.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        assume(len(kb.axioms) > 0)
        # Prakken 2010, Thm. 6.10 (p. 145; local page image
        # ``papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-015.png``)
        # requires consistent Cl_Rs(K_n) for the rationality guarantees. Once
        # transposition_closure stops erasing inconsistent strict theories, this
        # property must restrict itself to that well-defined fragment.
        assume(is_c_consistent(kb.axioms, R_s, cfn))
        arguments = build_arguments(system, kb)
        assert any(
            is_firm(a) and is_strict(a) for a in arguments
        ), "K_n nonempty but no firm+strict argument found"

    @given(data=st.data())
    @settings(deadline=None)
    def test_nontriviality(self, data):
        """When rules exist whose antecedents are in K, at least one
        non-PremiseArg is constructed.

        This is the non-triviality guarantee from the knowledge_base
        strategy: it forces at least one rule's antecedents into K_p,
        ensuring build_arguments produces compound arguments when a
        c-consistent rule antecedent set is available.
        See reports/hypothesis-aspic-feasibility.md Section 3, Level 4.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        all_rules = R_s | R_d
        assume(len(all_rules) > 0)
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        assume(any(
            frozenset(rule.antecedents) <= (kb.axioms | kb.premises)
            and is_c_consistent(
                frozenset(rule.antecedents),
                system.strict_rules,
                system.contrariness,
            )
            for rule in all_rules
        ))
        non_premise = [
            a for a in arguments if not isinstance(a, PremiseArg)
        ]
        assert len(non_premise) > 0, (
            "Rules exist and antecedents are in K, "
            "but no non-PremiseArg was constructed"
        )


class TestArgumentConstructionConcrete:
    """Hand-constructed examples for argument construction."""

    def test_simple_modus_ponens(self):
        """K_p = {p, q}. Defeasible rule: p, q => r.

        Modgil & Prakken 2018, Def 5 (p.9-10): construct arguments
        bottom-up from premises through rule application.

        Expected arguments:
        - PremiseArg(p), PremiseArg(q)
        - DefeasibleArg(sub_args=(PremiseArg(p), PremiseArg(q)),
                        rule=(p, q => r))
        The compound argument's conclusion is r.
        """
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        r = Literal(GroundAtom("r"))
        not_p = p.contrary
        not_q = q.contrary
        not_r = r.contrary

        L = frozenset({p, q, r, not_p, not_q, not_r})
        cfn = ContrarinessFn(contradictories=frozenset({
            (p, not_p), (q, not_q), (r, not_r),
        }))

        rule_pq_r = Rule(
            antecedents=(p, q),
            consequent=r,
            kind="defeasible",
            name="d0",
        )

        system = ArgumentationSystem(
            language=L,
            contrariness=cfn,
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule_pq_r}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p, q}),
        )

        arguments = build_arguments(system, kb)

        # Find premise arguments
        prem_p = PremiseArg(premise=p, is_axiom=False)
        prem_q = PremiseArg(premise=q, is_axiom=False)
        assert prem_p in arguments, f"PremiseArg(p) not in arguments: {arguments}"
        assert prem_q in arguments, f"PremiseArg(q) not in arguments: {arguments}"

        # Find the compound defeasible argument
        compound = DefeasibleArg(
            sub_args=(prem_p, prem_q),
            rule=rule_pq_r,
        )
        assert compound in arguments, (
            f"DefeasibleArg(p,q => r) not in arguments: {arguments}"
        )

        # Conclusion of the compound is r
        assert conc(compound) == r, (
            f"Expected conc = r, got {conc(compound)}"
        )

    def test_c_inconsistent_argument_is_not_constructed(self):
        """An argument with c-inconsistent premises must be excluded."""
        p = Literal(GroundAtom("p"))
        not_p = p.contrary
        q = Literal(GroundAtom("q"))
        not_q = q.contrary
        r = Literal(GroundAtom("r"))
        not_r = r.contrary

        L = frozenset({p, not_p, q, not_q, r, not_r})
        cfn = ContrarinessFn(contradictories=frozenset({
            (p, not_p), (q, not_q), (r, not_r),
        }))
        strict_rules, _post_language = transposition_closure(
            frozenset({
                Rule((p,), q, "strict"),
                Rule((not_q,), not_p, "strict"),
                Rule((p, not_q), r, "strict"),
            }),
            L,
            cfn,
        )
        system = ArgumentationSystem(
            language=L,
            contrariness=cfn,
            strict_rules=strict_rules,
            defeasible_rules=frozenset(),
        )
        kb = KnowledgeBase(
            axioms=frozenset({not_q}),
            premises=frozenset({p}),
        )

        arguments = build_arguments(system, kb)
        inconsistent_arg = StrictArg(
            sub_args=(
                PremiseArg(premise=p, is_axiom=False),
                PremiseArg(premise=not_q, is_axiom=True),
            ),
            rule=Rule((p, not_q), r, "strict"),
        )
        assert inconsistent_arg not in arguments


# ── Phase 4: Attack determination property tests ─────────────────


class TestAttackProperties:
    """Property tests for three-type attack determination on sub-arguments.

    Modgil & Prakken 2018, Def 8 (p.11): undermining, rebutting, undercutting.
    Pollock 1987, Defs 2.4-2.5 (p.485): rebutting vs undercutting defeaters.

    All tests use compute_attacks() which DOES NOT EXIST YET — tests
    fail with ImportError.
    """

    @given(data=st.data())
    @settings(deadline=None)
    def test_undermining_targets_ordinary_premises(self, data):
        """Every undermining attack targets a PremiseArg with is_axiom == False.

        Modgil & Prakken 2018, Def 8a (p.11): A undermines B on B' iff
        B' is a PremiseArg with ordinary premise phi (phi in K_p).
        Axiom premises (K_n) cannot be undermined.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        for atk in attacks:
            if atk.kind == "undermining":
                assert isinstance(atk.target_sub, PremiseArg), (
                    f"Undermining target_sub is {type(atk.target_sub).__name__}, "
                    f"expected PremiseArg"
                )
                assert not atk.target_sub.is_axiom, (
                    f"Undermining attack targets axiom premise "
                    f"{atk.target_sub.premise} — axioms cannot be undermined"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_rebutting_targets_defeasible_conclusions(self, data):
        """Every rebutting attack targets a sub-argument whose top_rule() is defeasible.

        Modgil & Prakken 2018, Def 8b (p.11): A rebuts B on B' iff
        TopRule(B') is defeasible, and Conc(A) is in the contrariness of Conc(B').
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        for atk in attacks:
            if atk.kind == "rebutting":
                tr = top_rule(atk.target_sub)
                assert tr is not None, (
                    f"Rebutting target_sub has no top rule (PremiseArg)"
                )
                assert tr.kind == "defeasible", (
                    f"Rebutting target_sub top rule is {tr.kind}, "
                    f"expected 'defeasible'"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_undercutting_targets_defeasible_rules(self, data):
        """Every undercutting attack targets a sub-argument whose top_rule() is defeasible.

        Modgil & Prakken 2018, Def 8c (p.11): A undercuts B on B' iff
        TopRule(B') is a defeasible rule r, and Conc(A) is in the
        contrariness of n(r). Strict rules cannot be undercut.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        for atk in attacks:
            if atk.kind == "undercutting":
                tr = top_rule(atk.target_sub)
                assert tr is not None, (
                    f"Undercutting target_sub has no top rule (PremiseArg)"
                )
                assert tr.kind == "defeasible", (
                    f"Undercutting target_sub top rule is {tr.kind}, "
                    f"expected 'defeasible'"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_no_attack_on_firm_strict_subarg(self, data):
        """No attack targets a sub-argument B' where is_firm(B') and is_strict(B').

        Modgil & Prakken 2018, Def 18 (p.16): firm+strict sub-arguments
        are unattackable — they use only axiom premises and strict rules.
        Consequence of Def 8: undermining requires ordinary premises,
        rebutting requires defeasible top rule, undercutting requires
        defeasible top rule. Firm+strict satisfies none of these.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        for atk in attacks:
            assert not (is_firm(atk.target_sub) and is_strict(atk.target_sub)), (
                f"Attack {atk.kind} targets firm+strict sub-argument "
                f"{atk.target_sub}"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_attacker_and_target_in_arguments(self, data):
        """Every attack's attacker and target are both in the argument set.

        compute_attacks operates over the argument set; it should not
        introduce arguments from outside that set.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        for atk in attacks:
            assert atk.attacker in arguments, (
                f"Attacker {atk.attacker} not in argument set"
            )
            assert atk.target in arguments, (
                f"Target {atk.target} not in argument set"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_target_sub_in_sub_of_target(self, data):
        """Every attack's target_sub is in sub(attack.target).

        Modgil & Prakken 2018, Def 8 (p.11): all three attack types
        require B' in Sub(B) — the attacked sub-argument must be a
        sub-argument of the target argument.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        for atk in attacks:
            assert atk.target_sub in sub(atk.target), (
                f"target_sub {atk.target_sub} not in sub({atk.target})"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_rebutting_symmetry_for_contradictories(self, data):
        """Contradictory rebut is symmetric when both sides are defeasible.

        Modgil & Prakken 2018, Def 2 (p.8): contradictories are symmetric.
        Def 8b (p.11): rebutting requires Conc(A) in contrariness of Conc(B').

        The symmetry applies at the level of rebuttable defeasible conclusions.
        If A rebuts B' and both A and B' have defeasible top rules with
        contradictory conclusions, then B' must also rebut A.

        This does NOT hold when the attacker is only a premise or a strict
        conclusion: Def 8b constrains the target structure, not the attacker.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        reverse_rebut_targets = {
            (conc(atk2.attacker), id(atk2.target_sub))
            for atk2 in attacks
            if atk2.kind == "rebutting"
        }

        for atk in attacks:
            if atk.kind != "rebutting":
                continue
            tr_a = top_rule(atk.attacker)
            if tr_a is None or tr_a.kind != "defeasible":
                continue
            conc_a = conc(atk.attacker)
            conc_b_prime = conc(atk.target_sub)
            # Only check when they are contradictories (symmetric)
            if not cfn.is_contradictory(conc_a, conc_b_prime):
                continue
            tr_b = top_rule(atk.target_sub)
            if tr_b is None or tr_b.kind != "defeasible":
                continue
            # Index by target_sub identity to avoid quadratic deep-argument
            # equality checks across large Hypothesis-generated attack sets.
            reverse_exists = (conc_b_prime, id(atk.attacker)) in reverse_rebut_targets
            assert reverse_exists, (
                f"Rebutting attack from defeasible {conc_a} on defeasible "
                f"{conc_b_prime} is contradictory-symmetric, but no reverse "
                f"rebutting attack onto the attacker was found"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_attack_kind_is_valid(self, data):
        """Every attack has kind in {"undermining", "rebutting", "undercutting"}.

        Modgil & Prakken 2018, Def 8 (p.11): exactly three attack types.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        valid_kinds = {"undermining", "rebutting", "undercutting"}
        for atk in attacks:
            assert atk.kind in valid_kinds, (
                f"Attack kind '{atk.kind}' not in {valid_kinds}"
            )


class TestAttackConcrete:
    """Hand-constructed examples for attack determination.

    Modgil & Prakken 2018, Def 8 (p.11).
    Pollock 1987, Defs 2.4-2.5 (p.485).
    """

    def test_undermining_example(self):
        """K_p = {p, ~p}. Defeasible rule: p => q.
        The argument for ~p undermines the argument for q on sub-argument PremiseArg(p).

        Modgil & Prakken 2018, Def 8a (p.11): A undermines B on B' iff
        B' in Sub(B), B' is a PremiseArg with ordinary premise phi (phi in K_p),
        and Conc(A) is in the contrariness of phi.

        Here: Conc(A) = ~p, phi = p, ~p in bar(p) (contradictories). So A
        undermines B on PremiseArg(p).
        """
        p = Literal(GroundAtom("p"))
        not_p = p.contrary
        q = Literal(GroundAtom("q"))
        not_q = q.contrary

        L = frozenset({p, not_p, q, not_q})
        cfn = ContrarinessFn(contradictories=frozenset({
            (p, not_p), (q, not_q),
        }))

        rule_p_q = Rule(
            antecedents=(p,), consequent=q,
            kind="defeasible", name="d0",
        )

        system = ArgumentationSystem(
            language=L, contrariness=cfn,
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule_p_q}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p, not_p}),
        )

        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)

        prem_p_arg = PremiseArg(premise=p, is_axiom=False)
        prem_not_p_arg = PremiseArg(premise=not_p, is_axiom=False)
        compound_q = DefeasibleArg(
            sub_args=(prem_p_arg,), rule=rule_p_q,
        )

        # The argument for ~p undermines the argument for q on PremiseArg(p)
        expected = Attack(
            attacker=prem_not_p_arg,
            target=compound_q,
            target_sub=prem_p_arg,
            kind="undermining",
        )
        assert expected in attacks, (
            f"Expected undermining attack {expected} not found in {attacks}"
        )

    def test_undercutting_example(self):
        """K_p = {p, ~d0}. Defeasible rule d0: p => q (name="d0").
        The argument for ~d0 undercuts the argument for q.

        Modgil & Prakken 2018, Def 8c (p.11): A undercuts B on B' iff
        B' in Sub(B), TopRule(B') is a defeasible rule r, and Conc(A)
        is in the contrariness of n(r).

        Here: n(r) = d0 (as a Literal), Conc(A) = ~d0. ~d0 in bar(d0)
        (contradictories). So A undercuts B on B'.

        Pollock 1987, Def 2.5 (p.485): undercutting defeats the connection
        between premise and conclusion, not the conclusion itself.
        """
        p = Literal(GroundAtom("p"))
        not_p = p.contrary
        q = Literal(GroundAtom("q"))
        not_q = q.contrary
        d0 = Literal(GroundAtom("d0"))
        not_d0 = d0.contrary

        L = frozenset({p, not_p, q, not_q, d0, not_d0})
        cfn = ContrarinessFn(contradictories=frozenset({
            (p, not_p), (q, not_q), (d0, not_d0),
        }))

        rule_p_q = Rule(
            antecedents=(p,), consequent=q,
            kind="defeasible", name="d0",
        )

        system = ArgumentationSystem(
            language=L, contrariness=cfn,
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule_p_q}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p, not_d0}),
        )

        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)

        prem_p_arg = PremiseArg(premise=p, is_axiom=False)
        prem_not_d0_arg = PremiseArg(premise=not_d0, is_axiom=False)
        compound_q = DefeasibleArg(
            sub_args=(prem_p_arg,), rule=rule_p_q,
        )

        # The argument for ~d0 undercuts the argument for q
        expected = Attack(
            attacker=prem_not_d0_arg,
            target=compound_q,
            target_sub=compound_q,
            kind="undercutting",
        )
        assert expected in attacks, (
            f"Expected undercutting attack {expected} not found in {attacks}"
        )


# ── Phase 5: Preference ordering strategy ─────────────────────────


@st.composite
def preference_config(draw, defeasible_rules_set, premises):
    """Generate a preference ordering configuration.

    Modgil & Prakken 2018, Defs 19-21 (p.21).
    Def 22 (p.22): the inducing ordering must be a strict partial order
    (irreflexive and transitive).

    Generates random partial orderings over rules and premises by:
    1. Drawing a random subset of pairs.
    2. Ensuring irreflexivity (no self-pairs).
    3. Computing transitive closure.
    4. Checking for cycles; if cyclic, falling back to empty ordering.
    """
    # Build rule ordering: random subset of (weaker, stronger) pairs
    rules_list = sorted(defeasible_rules_set, key=repr)
    rule_pairs: set[tuple[Rule, Rule]] = set()
    if len(rules_list) >= 2:
        n_pairs = draw(st.integers(min_value=0, max_value=len(rules_list)))
        for _ in range(n_pairs):
            r1 = draw(st.sampled_from(rules_list))
            r2 = draw(st.sampled_from(rules_list))
            if r1 != r2:  # irreflexivity
                rule_pairs.add((r1, r2))
        # Transitive closure
        rule_pairs = _transitive_closure_pairs(rule_pairs)
        # Check for cycles (antisymmetry): if (a,b) and (b,a) both in set, discard all
        if _has_cycle(rule_pairs):
            rule_pairs = set()

    # Build premise ordering: random subset of (weaker, stronger) pairs
    prem_list = sorted(premises, key=repr)
    prem_pairs: set[tuple[Literal, Literal]] = set()
    if len(prem_list) >= 2:
        n_pairs = draw(st.integers(min_value=0, max_value=len(prem_list)))
        for _ in range(n_pairs):
            p1 = draw(st.sampled_from(prem_list))
            p2 = draw(st.sampled_from(prem_list))
            if p1 != p2:  # irreflexivity
                prem_pairs.add((p1, p2))
        # Transitive closure
        prem_pairs = _transitive_closure_pairs(prem_pairs)
        # Check for cycles
        if _has_cycle(prem_pairs):
            prem_pairs = set()

    comparison = draw(st.sampled_from(["elitist", "democratic"]))
    link = draw(st.sampled_from(["last", "weakest"]))

    return PreferenceConfig(
        rule_order=frozenset(rule_pairs),
        premise_order=frozenset(prem_pairs),
        comparison=comparison,
        link=link,
    )


def _transitive_closure_pairs(pairs):
    """Compute transitive closure of a set of (a, b) pairs."""
    closed = set(pairs)
    changed = True
    while changed:
        changed = False
        new = set()
        for a, b in closed:
            for c, d in closed:
                if b == c and (a, d) not in closed and a != d:
                    new.add((a, d))
        if new:
            closed.update(new)
            changed = True
    return closed


def _has_cycle(pairs):
    """Check if a set of (a, b) pairs contains a cycle (a,b) and (b,a)."""
    for a, b in pairs:
        if (b, a) in pairs:
            return True
    return False


# ── Phase 5: Defeat property tests ────────────────────────────────


class TestDefeatProperties:
    """Property tests for defeat filtering via preference orderings.

    Modgil & Prakken 2018:
    - Def 9 (p.12): when attacks succeed as defeats
    - Def 19 (p.21): Elitist and Democratic set comparison
    - Def 20 (p.21): Last-link principle
    - Def 21 (p.21): Weakest-link principle
    """

    @given(data=st.data())
    @settings(deadline=None)
    def test_undercutting_always_defeats(self, data):
        """Every undercutting attack is a defeat regardless of preference ordering.

        Modgil & Prakken 2018, Def 9 (p.12): undercutting attacks are
        preference-independent — they always succeed as defeats.
        Pollock 1987, Def 2.5 (p.485): undercutting defeats the
        connection between premise and conclusion.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = data.draw(preference_config(R_d, kb.premises))
        defeats = compute_defeats(attacks, arguments, system, kb, pref)

        # Every undercutting attack must appear in defeats
        undercutting_attacks = {
            (atk.attacker, atk.target)
            for atk in attacks if atk.kind == "undercutting"
        }
        defeat_pairs = {(d.attacker, d.target) for d in defeats}
        for pair in undercutting_attacks:
            assert pair in defeat_pairs, (
                f"Undercutting attack {pair} not in defeats — "
                f"undercutting must always succeed (Def 9, p.12)"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_defeats_subset_of_attacks(self, data):
        """Every defeat (a,b) corresponds to an attack from a on b.

        Modgil & Prakken 2018, Def 9 (p.12): defeats are a subset
        of attacks — an attack must exist for a defeat to occur.
        Defeats ⊆ Attacks.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = data.draw(preference_config(R_d, kb.premises))
        defeats = compute_defeats(attacks, arguments, system, kb, pref)

        attack_pairs = {
            (atk.attacker, atk.target, atk.target_sub)
            for atk in attacks
        }
        for d in defeats:
            assert (d.attacker, d.target, d.target_sub) in attack_pairs, (
                f"Defeat {d} has no corresponding attack"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_empty_ordering_still_respects_definition_19_edge_cases(self, data):
        """Empty base orders do not erase Definition 19's empty-set lifting.

        Modgil & Prakken 2018, Def 19 (p.21) still makes a non-empty defeasible
        set strictly less than an empty target set, even when the underlying
        order relations themselves are empty. So defeats with empty preferences
        are exactly the preference-independent attacks plus the attacks whose
        attacker is not strictly weaker than the targeted sub-argument.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        empty_pref = PreferenceConfig(
            rule_order=frozenset(),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )
        defeats = compute_defeats(attacks, arguments, system, kb, empty_pref)

        expected_defeats = {
            atk
            for atk in attacks
            if _is_preference_independent_attack(atk, system)
            or not _strictly_weaker(atk.attacker, atk.target_sub, empty_pref, kb)
        }
        assert defeats == expected_defeats, (
            f"With empty preferences, defeats should still follow Def 9/19. "
            f"Missing: {expected_defeats - defeats}; extra: {defeats - expected_defeats}"
        )

    @given(data=st.data())
    @settings(deadline=None)
    def test_defeat_is_directed(self, data):
        """If (a,b) is a defeat, it means a defeats b — directionality is preserved.

        Modgil & Prakken 2018, Def 9 (p.12): defeat is a directed relation.
        The attacker and target roles must be consistent with the attack.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = data.draw(preference_config(R_d, kb.premises))
        defeats = compute_defeats(attacks, arguments, system, kb, pref)

        for d in defeats:
            # The defeat must correspond to an attack in the same direction
            matching_attack = any(
                atk.attacker == d.attacker
                and atk.target == d.target
                and atk.target_sub == d.target_sub
                for atk in attacks
            )
            assert matching_attack, (
                f"Defeat from {d.attacker} to {d.target} has no matching "
                f"attack in the same direction"
            )

    @given(data=st.data())
    @settings(deadline=None)
    def test_last_link_irreflexive(self, data):
        """No argument is strictly weaker than itself under last-link.

        Modgil & Prakken 2018, Def 20 (p.21): the last-link principle
        derives argument orderings from rule/premise orderings. Since the
        inducing ordering is irreflexive (Def 22, p.22), no argument
        can be strictly weaker than itself.

        Def 9 (p.12) compares the attacker against the targeted
        sub-argument B', not automatically against itself. So even a
        self-attack only succeeds when A is not strictly weaker than B'.

        Page-image grounding for last-link/lifting:
        papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-015.png
        papers/Lehtonen_2024_PreferentialASPIC/pages/page_004.png
        papers/Lehtonen_2024_PreferentialASPIC/pages/page_005.png
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = data.draw(preference_config(R_d, kb.premises))
        # Force last-link
        pref_last = PreferenceConfig(
            rule_order=pref.rule_order,
            premise_order=pref.premise_order,
            comparison=pref.comparison,
            link="last",
        )
        defeats = compute_defeats(attacks, arguments, system, kb, pref_last)

        # Def 9 (p.12): self-attack does not bypass the A vs B' preference check.
        for atk in attacks:
            if atk.attacker == atk.target:
                expected = _is_preference_independent_attack(atk, system) or (
                    not _strictly_weaker(atk.attacker, atk.target_sub, pref_last, kb)
                )
                actual = atk in defeats
                assert actual == expected, (
                    f"Self-attack {atk} should follow Def 9 against target_sub "
                    f"{atk.target_sub}: expected defeat={expected}, got {actual}"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_weakest_link_irreflexive(self, data):
        """No argument is strictly weaker than itself under weakest-link.

        Modgil & Prakken 2018, Def 21 (p.21): same irreflexivity
        property as last-link, but under the weakest-link principle.
        Def 22 (p.22): inducing ordering is irreflexive.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = data.draw(preference_config(R_d, kb.premises))
        # Force weakest-link
        pref_weakest = PreferenceConfig(
            rule_order=pref.rule_order,
            premise_order=pref.premise_order,
            comparison=pref.comparison,
            link="weakest",
        )
        defeats = compute_defeats(attacks, arguments, system, kb, pref_weakest)

        # Def 9 (p.12): self-attack does not bypass the A vs B' preference check.
        for atk in attacks:
            if atk.attacker == atk.target:
                expected = _is_preference_independent_attack(atk, system) or (
                    not _strictly_weaker(
                        atk.attacker, atk.target_sub, pref_weakest, kb
                    )
                )
                actual = atk in defeats
                assert actual == expected, (
                    f"Self-attack {atk} should follow Def 9 against target_sub "
                    f"{atk.target_sub}: expected defeat={expected}, got {actual}"
                )

    @given(data=st.data())
    @settings(deadline=None)
    def test_firm_strict_never_defeated(self, data):
        """If A is firm+strict, no argument B can defeat A.

        Modgil & Prakken 2018, Def 18 (p.16): firm+strict arguments
        are never strictly weaker than any argument. Since they have
        no ordinary premises and no defeasible rules, they cannot be
        targets of undermining, rebutting, or undercutting attacks.

        Consequence of Def 18 conditions 1.i and 1.ii: strict+firm
        arguments dominate all plausible/defeasible arguments, and
        are never dominated.
        """
        L, cfn = data.draw(logical_language())
        R_s = data.draw(strict_rules(L, cfn))
        R_d = data.draw(defeasible_rules(L))
        system = ArgumentationSystem(L, cfn, R_s, R_d)
        kb = data.draw(knowledge_base(L, R_s, R_d))
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = data.draw(preference_config(R_d, kb.premises))
        defeats = compute_defeats(attacks, arguments, system, kb, pref)

        for d in defeats:
            assert not (is_firm(d.target) and is_strict(d.target)), (
                f"Firm+strict argument {d.target} appears as defeat target — "
                f"firm+strict arguments cannot be defeated (Def 18, p.16)"
            )


class TestSetComparisonProperties:
    """Property tests for Def. 19 over finite induced orders.

    Prakken (2010), page 16, gives the elitist set order used by
    last-link:
    papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-015.png

    Lehtonen (2024), pages 523-524, rephrases last-link defeat under
    elitist and democratic lifting:
    papers/Lehtonen_2024_PreferentialASPIC/pages/page_004.png
    papers/Lehtonen_2024_PreferentialASPIC/pages/page_005.png
    """

    pytestmark = pytest.mark.property

    @given(
        st.permutations((0, 1, 2, 3)),
        st.sets(st.integers(min_value=0, max_value=3), min_size=1, max_size=4),
        st.sets(st.integers(min_value=0, max_value=3), min_size=1, max_size=4),
    )
    @settings(deadline=None)
    def test_elitist_matches_definition_19(self, ranking, gamma, gamma_prime):
        order_index = {item: idx for idx, item in enumerate(ranking)}
        base_order = frozenset(
            (x, y)
            for x in ranking
            for y in ranking
            if order_index[x] < order_index[y]
        )
        expected = any(
            all((x, y) in base_order for y in gamma_prime)
            for x in gamma
        )
        actual = _set_strictly_less(
            frozenset(gamma),
            frozenset(gamma_prime),
            base_order,
            "elitist",
        )
        assert actual == expected

    @given(
        st.permutations((0, 1, 2, 3)),
        st.sets(st.integers(min_value=0, max_value=3), min_size=1, max_size=4),
        st.sets(st.integers(min_value=0, max_value=3), min_size=1, max_size=4),
    )
    @settings(deadline=None)
    def test_democratic_matches_definition_19(self, ranking, gamma, gamma_prime):
        order_index = {item: idx for idx, item in enumerate(ranking)}
        base_order = frozenset(
            (x, y)
            for x in ranking
            for y in ranking
            if order_index[x] < order_index[y]
        )
        expected = all(
            any((x, y) in base_order for y in gamma_prime)
            for x in gamma
        )
        actual = _set_strictly_less(
            frozenset(gamma),
            frozenset(gamma_prime),
            base_order,
            "democratic",
        )
        assert actual == expected


class TestDefeatConcrete:
    """Hand-constructed examples for defeat with preferences.

    Modgil & Prakken 2018, Def 9 (p.12), Defs 19-21 (p.21).
    """

    def test_elitist_set_comparison_matches_definition_19(self):
        """Elitist comparison quantifies over Gamma, not Gamma'."""
        assert _set_strictly_less(
            frozenset({1, 5}),
            frozenset({3, 4}),
            frozenset({(1, 3), (1, 4)}),
            "elitist",
        )

    def test_definition_19_treats_nonempty_set_as_below_empty_set(self):
        """Definition 19 (p.21) explicitly gives Gamma <_s empty when Gamma != empty."""
        base_order = frozenset({("weak", "strong")})

        assert _set_strictly_less(
            frozenset({"weak"}),
            frozenset(),
            base_order,
            "elitist",
        )
        assert _set_strictly_less(
            frozenset({"weak"}),
            frozenset(),
            base_order,
            "democratic",
        )

    def test_self_undermining_defeat_still_checks_target_sub_preference(self):
        """Self-undermining does not automatically become a defeat.

        Modgil & Prakken 2018, Def 9 (p.12), compares attacker A against the
        targeted sub-argument B'. Under Defs 19-20 (p.21), a defeasible
        argument can be strictly weaker than its own premise sub-argument when
        its last defeasible rule set is non-empty and the target sub-argument's
        last defeasible rule set is empty.
        """
        p = Literal(GroundAtom("p"))
        not_p = p.contrary

        L = frozenset({p, not_p})
        cfn = ContrarinessFn(contradictories=frozenset({(p, not_p)}))

        rule_self_attack = Rule(
            antecedents=(p,),
            consequent=not_p,
            kind="defeasible",
            name="d_self_attack",
        )

        system = ArgumentationSystem(
            language=L,
            contrariness=cfn,
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule_self_attack}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p}),
        )

        premise_arg = PremiseArg(premise=p, is_axiom=False)
        attacker = DefeasibleArg(sub_args=(premise_arg,), rule=rule_self_attack)
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        self_undermining = Attack(
            attacker=attacker,
            target=attacker,
            target_sub=premise_arg,
            kind="undermining",
        )
        assert self_undermining in attacks

        pref = PreferenceConfig(
            rule_order=frozenset({(rule_self_attack, p)}),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )

        assert _strictly_weaker(attacker, premise_arg, pref, kb)

        defeats = compute_defeats(attacks, arguments, system, kb, pref)
        assert self_undermining not in defeats

    def test_stronger_rebutter_defeats(self):
        """Two defeasible arguments for contradictory conclusions.
        Give one a stronger rule ordering. The stronger defeats the weaker,
        not vice versa.

        Modgil & Prakken 2018, Def 9 (p.12): rebutting succeeds as defeat
        iff the attacker is NOT strictly weaker than the targeted sub-argument.
        If B prec A (B is weaker), then B's rebutting attack on A fails,
        but A's rebutting attack on B succeeds.
        """
        p = Literal(GroundAtom("p"))
        not_p = p.contrary
        q = Literal(GroundAtom("q"))
        not_q = q.contrary

        L = frozenset({p, not_p, q, not_q})
        cfn = ContrarinessFn(contradictories=frozenset({
            (p, not_p), (q, not_q),
        }))

        # Two defeasible rules: both from p, one to q, one to ~q
        rule_strong = Rule(
            antecedents=(p,), consequent=q,
            kind="defeasible", name="d_strong",
        )
        rule_weak = Rule(
            antecedents=(p,), consequent=not_q,
            kind="defeasible", name="d_weak",
        )

        system = ArgumentationSystem(
            language=L, contrariness=cfn,
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule_strong, rule_weak}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p}),
        )

        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)

        # Preference: rule_weak < rule_strong (weak is strictly weaker)
        pref = PreferenceConfig(
            rule_order=frozenset({(rule_weak, rule_strong)}),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )
        defeats = compute_defeats(attacks, arguments, system, kb, pref)

        prem_p_arg = PremiseArg(premise=p, is_axiom=False)
        arg_q = DefeasibleArg(sub_args=(prem_p_arg,), rule=rule_strong)
        arg_not_q = DefeasibleArg(sub_args=(prem_p_arg,), rule=rule_weak)

        # Strong defeats weak (A's attack on B succeeds: A not < B)
        defeat_pairs = {(d.attacker, d.target) for d in defeats}
        assert (arg_q, arg_not_q) in defeat_pairs, (
            f"Stronger argument should defeat weaker. "
            f"Defeats: {defeat_pairs}"
        )
        # Weak does NOT defeat strong (B's attack on A fails: B < A)
        assert (arg_not_q, arg_q) not in defeat_pairs, (
            f"Weaker argument should not defeat stronger. "
            f"Defeats: {defeat_pairs}"
        )

    def test_equal_strength_mutual_defeat(self):
        """Two equally-ranked defeasible arguments with contradictory conclusions.
        Both attacks succeed as defeats (neither is strictly weaker).

        Modgil & Prakken 2018, Def 9 (p.12): rebutting succeeds iff
        A is NOT strictly weaker. If neither is weaker (equal or
        incomparable), both attacks succeed as mutual defeats.
        """
        p = Literal(GroundAtom("p"))
        not_p = p.contrary
        q = Literal(GroundAtom("q"))
        not_q = q.contrary

        L = frozenset({p, not_p, q, not_q})
        cfn = ContrarinessFn(contradictories=frozenset({
            (p, not_p), (q, not_q),
        }))

        rule_a = Rule(
            antecedents=(p,), consequent=q,
            kind="defeasible", name="d_a",
        )
        rule_b = Rule(
            antecedents=(p,), consequent=not_q,
            kind="defeasible", name="d_b",
        )

        system = ArgumentationSystem(
            language=L, contrariness=cfn,
            strict_rules=frozenset(),
            defeasible_rules=frozenset({rule_a, rule_b}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p}),
        )

        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)

        # Empty preference: neither rule is weaker
        pref = PreferenceConfig(
            rule_order=frozenset(),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )
        defeats = compute_defeats(attacks, arguments, system, kb, pref)

        prem_p_arg = PremiseArg(premise=p, is_axiom=False)
        arg_q = DefeasibleArg(sub_args=(prem_p_arg,), rule=rule_a)
        arg_not_q = DefeasibleArg(sub_args=(prem_p_arg,), rule=rule_b)

        defeat_pairs = {(d.attacker, d.target) for d in defeats}
        # Both directions should be defeats (mutual defeat)
        assert (arg_q, arg_not_q) in defeat_pairs, (
            f"Equal-strength: arg_q should defeat arg_not_q. "
            f"Defeats: {defeat_pairs}"
        )
        assert (arg_not_q, arg_q) in defeat_pairs, (
            f"Equal-strength: arg_not_q should defeat arg_q. "
            f"Defeats: {defeat_pairs}"
        )

    def test_elitist_last_link_blocks_rebut_when_attacker_is_strictly_weaker(self):
        """A rebut must fail when one attacker rule is below every target rule.

        Last-link and elitist-lifting grounding:
        papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-015.png
        papers/Lehtonen_2024_PreferentialASPIC/pages/page_005.png
        """
        a = Literal(GroundAtom("a"))
        b = Literal(GroundAtom("b"))
        c = Literal(GroundAtom("c"))
        x = Literal(GroundAtom("x"))
        y = Literal(GroundAtom("y"))
        q = Literal(GroundAtom("q"))
        not_q = q.contrary

        d1 = Rule((a,), x, "defeasible", "d1")
        d2 = Rule((b,), y, "defeasible", "d2")
        t1 = Rule((c,), q, "defeasible", "t1")
        s1 = Rule((x, y), not_q, "strict")

        system = ArgumentationSystem(
            language=frozenset({a, b, c, x, y, q, not_q}),
            contrariness=ContrarinessFn(frozenset({(q, not_q)})),
            strict_rules=frozenset({s1}),
            defeasible_rules=frozenset({d1, d2, t1}),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({a, b, c}),
        )

        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        pref = PreferenceConfig(
            rule_order=frozenset({(d1, t1)}),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )

        defeats = compute_defeats(attacks, arguments, system, kb, pref)
        assert defeats == frozenset()

    def test_contrary_undermining_ignores_preference_ordering(self):
        """Contrary undermining is preference-independent and always defeats."""
        p = Literal(GroundAtom("p"))
        q = Literal(GroundAtom("q"))
        system = ArgumentationSystem(
            language=frozenset({p, q}),
            contrariness=ContrarinessFn(
                contradictories=frozenset(),
                contraries=frozenset({(p, q)}),
            ),
            strict_rules=frozenset(),
            defeasible_rules=frozenset(),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({p, q}),
        )
        pref = PreferenceConfig(
            rule_order=frozenset(),
            premise_order=frozenset({(p, q)}),
            comparison="elitist",
            link="last",
        )

        arg_p = PremiseArg(premise=p, is_axiom=False)
        arg_q = PremiseArg(premise=q, is_axiom=False)

        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)
        defeats = compute_defeats(attacks, arguments, system, kb, pref)
        defeat_pairs = {(defeat.attacker, defeat.target) for defeat in defeats}

        assert (arg_p, arg_q) in defeat_pairs
        assert (arg_q, arg_p) not in defeat_pairs

    def test_last_and_weakest_link_can_diverge(self):
        """A weak earlier rule can matter under weakest-link but not last-link."""
        a = Literal(GroundAtom("a"))
        b = Literal(GroundAtom("b"))
        x = Literal(GroundAtom("x"))
        q = Literal(GroundAtom("q"))
        not_q = q.contrary

        d_weak = Rule((a,), x, "defeasible", "d_weak")
        d_strong = Rule((x,), not_q, "defeasible", "d_strong")
        t_mid = Rule((b,), q, "defeasible", "t_mid")

        system = ArgumentationSystem(
            language=frozenset({a, b, x, q, not_q}),
            contrariness=ContrarinessFn(
                contradictories=frozenset({(q, not_q)}),
            ),
            strict_rules=frozenset(),
            defeasible_rules=frozenset({d_weak, d_strong, t_mid}),
        )
        kb = KnowledgeBase(
            axioms=frozenset({a, b}),
            premises=frozenset(),
        )
        arguments = build_arguments(system, kb)
        attacks = compute_attacks(arguments, system)

        pref_last = PreferenceConfig(
            rule_order=frozenset({
                (d_weak, t_mid),
                (t_mid, d_strong),
                (d_weak, d_strong),
            }),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )
        pref_weakest = PreferenceConfig(
            rule_order=pref_last.rule_order,
            premise_order=frozenset(),
            comparison="elitist",
            link="weakest",
        )

        arg_a = PremiseArg(premise=a, is_axiom=True)
        arg_b = PremiseArg(premise=b, is_axiom=True)
        arg_not_q = DefeasibleArg(
            sub_args=(DefeasibleArg(sub_args=(arg_a,), rule=d_weak),),
            rule=d_strong,
        )
        arg_q = DefeasibleArg(sub_args=(arg_b,), rule=t_mid)

        last_pairs = {
            (defeat.attacker, defeat.target)
            for defeat in compute_defeats(attacks, arguments, system, kb, pref_last)
        }
        weakest_pairs = {
            (defeat.attacker, defeat.target)
            for defeat in compute_defeats(attacks, arguments, system, kb, pref_weakest)
        }

        assert (arg_not_q, arg_q) in last_pairs
        assert (arg_q, arg_not_q) not in last_pairs
        assert (arg_not_q, arg_q) not in weakest_pairs
        assert (arg_q, arg_not_q) in weakest_pairs


# ── Phase 6: Rationality postulate strategies and tests ──────────


ASPIC_RATIONALITY_MAX_ARGUMENTS = 10
ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES = 1 << ASPIC_RATIONALITY_MAX_ARGUMENTS


@st.composite
def well_formed_csaf(draw, max_atoms=4, max_strict=3, max_defeasible=4):
    """Generate a well-formed c-SAF per Modgil & Prakken 2018, Def 12.

    Chains: logical_language -> strict_rules -> defeasible_rules -> well_defined_knowledge_base
    Then runs: build_arguments -> compute_attacks -> compute_defeats
    Finally emits: dung.ArgumentationFramework for extension computation.

    Guarantees:
    - Axiom consistency (Cl_Rs(K_n) is c-consistent)
    - Well-formed contrariness (contradictories symmetric)
    - Transposition closure (R_s = Cl(R_s))
    - At least one non-premise argument (non-triviality)

    Modgil & Prakken 2018, Def 12 (p.13): a c-SAF is well-defined iff
    it is axiom consistent, well-formed, and closed under transposition.
    """
    L, cfn = draw(logical_language(max_atoms=max_atoms))
    R_s = draw(strict_rules(L, cfn, max_rules=max_strict))
    R_d = draw(defeasible_rules(L, max_rules=max_defeasible))
    system = ArgumentationSystem(L, cfn, R_s, R_d)
    kb = draw(well_defined_knowledge_base(L, R_s, R_d, cfn))
    pref = draw(preference_config(R_d, kb.premises))

    # Computed (not drawn)
    arguments = build_arguments(system, kb)
    attacks = compute_attacks(arguments, system)
    defeat_attacks = compute_defeats(attacks, arguments, system, kb, pref)

    # Extract defeat pairs (Argument, Argument) from Attack objects
    defeats = frozenset(
        (atk.attacker, atk.target) for atk in defeat_attacks
    )

    # Build Dung AF
    # Assign string IDs to arguments for the Dung layer
    arg_list = sorted(arguments, key=lambda a: repr(a))  # deterministic ordering
    arg_to_id = {a: f"arg_{i}" for i, a in enumerate(arg_list)}
    id_to_arg = {v: k for k, v in arg_to_id.items()}

    af = ArgumentationFramework(
        arguments=frozenset(arg_to_id.values()),
        defeats=frozenset(
            (arg_to_id[a], arg_to_id[b])
            for a, b in defeats
            if a in arg_to_id and b in arg_to_id
        ),
        attacks=frozenset(
            (arg_to_id[atk.attacker], arg_to_id[atk.target])
            for atk in attacks
            if atk.attacker in arg_to_id and atk.target in arg_to_id
        ),
    )

    return CSAF(
        system=system, kb=kb, pref=pref, arguments=arguments,
        attacks=attacks, defeats=defeats, framework=af,
        arg_to_id=arg_to_id, id_to_arg=id_to_arg,
    )


@st.composite
def exact_complete_extension_csaf(draw):
    """Generate c-SAFs small enough for exhaustive complete-extension checks."""
    csaf = draw(well_formed_csaf(max_atoms=3, max_strict=2, max_defeasible=2))
    assume(len(csaf.framework.arguments) <= ASPIC_RATIONALITY_MAX_ARGUMENTS)
    return csaf


# ── Phase 6: The 8 Rationality Postulate Tests ──────────────────


class TestRationalityPostulates:
    """Property tests for the 8 rationality postulates of ASPIC+.

    These are the crown jewel: if all 8 hold on 200 random well-formed
    c-SAFs, the implementation is correct per Modgil & Prakken 2018.

    Complete-extension postulates use bounded generated c-SAFs because exact
    Dung complete-extension enumeration is exponential in the projected AF size.
    """

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_sub_argument_closure(self, csaf):
        """Postulate 1 — Sub-argument closure (Thm 12, p.18).

        If A is in a complete extension E and A' is in Sub(A),
        then A' is also in E. Extensions are closed under sub-arguments.

        Modgil & Prakken 2018, Theorem 12 (p.18): for every attack-
        conflict-free complete extension E of a well-defined c-SAF
        with reasonable ordering, Sub(E) = E.
        """
        for ext_ids in complete_extensions(
            csaf.framework,
            max_candidates=ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES,
        ):
            for aid in ext_ids:
                arg = csaf.id_to_arg[aid]
                for sub_arg in sub(arg):
                    assert csaf.arg_to_id[sub_arg] in ext_ids, (
                        f"Sub-argument {sub_arg} of {arg} not in extension"
                    )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_strict_closure(self, csaf):
        """Postulate 2 — Closure under strict rules (Thm 13, p.18).

        Cl_Rs(Conc(E)) = Conc(E): the set of conclusions of arguments
        in a complete extension is already closed under strict rules.

        Modgil & Prakken 2018, Theorem 13 (p.18): for every attack-
        conflict-free complete extension E of a well-defined c-SAF
        with reasonable ordering, Cl_Rs(Conc(E)) = Conc(E).
        """
        for ext_ids in complete_extensions(
            csaf.framework,
            max_candidates=ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES,
        ):
            conclusions = frozenset(
                conc(csaf.id_to_arg[aid]) for aid in ext_ids
            )
            closed = strict_closure(conclusions, csaf.system.strict_rules)
            assert closed == conclusions, (
                f"Strict closure added: {closed - conclusions}"
            )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_direct_consistency(self, csaf):
        """Postulate 3 — Direct consistency (Thm 14, p.18).

        No two conclusions in a complete extension are contraries or
        contradictories. The extension conclusions are directly consistent.

        Modgil & Prakken 2018, Theorem 14 (p.18): for every attack-
        conflict-free complete extension E of a well-defined c-SAF
        with reasonable ordering, Conc(E) is consistent.
        """
        for ext_ids in complete_extensions(
            csaf.framework,
            max_candidates=ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES,
        ):
            conclusions = [conc(csaf.id_to_arg[aid]) for aid in ext_ids]
            for i, c1 in enumerate(conclusions):
                for c2 in conclusions[i + 1:]:
                    assert not csaf.system.contrariness.is_contradictory(c1, c2), (
                        f"Direct inconsistency: {c1} and {c2} are contradictories"
                    )
                    assert not csaf.system.contrariness.is_contrary(c1, c2), (
                        f"Direct inconsistency: {c1} is a contrary of {c2}"
                    )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_indirect_consistency(self, csaf):
        """Postulate 4 — Indirect consistency (Thm 15, p.19).

        Cl_Rs(Conc(E)) is consistent: the strict closure of conclusions
        contains no contradictory pair.

        Modgil & Prakken 2018, Theorem 15 (p.19): for every attack-
        conflict-free complete extension E of a well-defined c-SAF
        with reasonable ordering, Cl_Rs(Conc(E)) is consistent.
        """
        for ext_ids in complete_extensions(
            csaf.framework,
            max_candidates=ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES,
        ):
            conclusions = frozenset(
                conc(csaf.id_to_arg[aid]) for aid in ext_ids
            )
            closed = strict_closure(conclusions, csaf.system.strict_rules)
            closed_list = list(closed)
            for i, c1 in enumerate(closed_list):
                for c2 in closed_list[i + 1:]:
                    assert not csaf.system.contrariness.is_contradictory(c1, c2), (
                        f"Indirect inconsistency: {c1} and {c2} are "
                        f"contradictories in Cl_Rs(Conc(E))"
                    )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_firm_strict_in_every_complete(self, csaf):
        """Postulate 5 — Firm+strict in every complete extension (Def 18).

        Every argument that is both firm (all premises are axioms) and
        strict (no defeasible rules) must be in every complete extension.

        Modgil & Prakken 2018, Def 18 (p.16): reasonable orderings
        require that firm+strict arguments are never strictly weaker
        than any argument. Combined with the fundamental lemma (Props
        9-11, p.17), this means they are in every complete extension.
        """
        firm_strict_ids = {
            csaf.arg_to_id[a] for a in csaf.arguments
            if is_firm(a) and is_strict(a)
        }
        for ext_ids in complete_extensions(
            csaf.framework,
            max_candidates=ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES,
        ):
            assert firm_strict_ids <= ext_ids, (
                f"Firm+strict args {firm_strict_ids - ext_ids} "
                f"not in complete extension"
            )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_undercutting_always_defeats(self, csaf):
        """Postulate 6 — Undercutting always defeats (Def 9).

        Every undercutting attack succeeds as a defeat regardless of
        the preference ordering. Undercutting is preference-independent.

        Modgil & Prakken 2018, Def 9 (p.12): undercutting attacks
        always succeed as defeats.
        Pollock 1987, Def 2.5 (p.485): undercutting defeaters.
        """
        for atk in csaf.attacks:
            if atk.kind == "undercutting":
                pair = (csaf.arg_to_id[atk.attacker], csaf.arg_to_id[atk.target])
                assert pair in csaf.framework.defeats, (
                    f"Undercutting attack {atk} not in framework defeats"
                )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_attack_based_conflict_free(self, csaf):
        """Postulate 7 — Attack-based conflict-free (Def 14).

        Every complete extension is conflict-free with respect to the
        attack relation (not just the defeat relation).

        Modgil & Prakken 2018, Def 14 (p.14): a set S is attack-based
        conflict-free iff no argument in S attacks another argument in S.
        This is strictly stronger than defeat-based conflict-free.
        """
        for ext_ids in complete_extensions(
            csaf.framework,
            max_candidates=ASPIC_RATIONALITY_MAX_COMPLETE_CANDIDATES,
        ):
            assert conflict_free(ext_ids, csaf.framework.attacks), (
                f"Complete extension {ext_ids} is not attack-based "
                f"conflict-free"
            )

    @given(exact_complete_extension_csaf())
    @settings(deadline=None)
    def test_transposition_closure_maintained(self, csaf):
        """Postulate 8 — Transposition closure (Def 12).

        The strict rules in the argumentation system are already closed
        under transposition. Applying transposition_closure again
        produces the same set.

        Modgil & Prakken 2018, Def 12 (p.13): well-definedness requires
        closure under transposition.
        Prakken 2010, Theorem 6.10: transposition closure is REQUIRED
        for the rationality postulates to hold.
        """
        closed, _post_language = transposition_closure(
            csaf.system.strict_rules,
            csaf.system.language,
            csaf.system.contrariness,
        )
        assert closed == csaf.system.strict_rules, (
            f"Strict rules not closed under transposition: "
            f"{len(closed)} rules after closure vs {len(csaf.system.strict_rules)}"
        )


# ── Phase 6: Concrete regression test ───────────────────────────


class TestRationalityPostulatesConcrete:
    """Hand-crafted regression tests for rationality postulates.

    These complement the property tests with known examples from the
    literature, providing deterministic coverage of specific scenarios.
    """

    def test_married_bachelor_consistency(self):
        """The married/bachelor example from Modgil 2014, Example 4.4.

        L = {married, ~married, bachelor, ~bachelor}
        Strict rule: married -> ~bachelor (with transposition: bachelor -> ~married)
        K_p = {married, bachelor}

        Build CSAF. Compute grounded extension.
        Assert: the extension does NOT contain both bachelor and ~bachelor
        (direct consistency holds).

        This is a classic example of how transposition closure ensures
        consistency: the strict rule generates a counter-argument that
        prevents contradictory conclusions from coexisting in any extension.
        """
        married = Literal(GroundAtom("married"))
        not_married = Literal(GroundAtom("married"), negated=True)
        bachelor = Literal(GroundAtom("bachelor"))
        not_bachelor = Literal(GroundAtom("bachelor"), negated=True)

        L = frozenset({married, not_married, bachelor, not_bachelor})
        cfn = ContrarinessFn(contradictories=frozenset({
            (married, not_married),
            (bachelor, not_bachelor),
        }))

        # Strict rule: married -> ~bachelor
        rule_m_nb = Rule(
            antecedents=(married,),
            consequent=not_bachelor,
            kind="strict",
            name=None,
        )

        # Compute transposition closure: adds bachelor -> ~married
        R_s, _post_language = transposition_closure(frozenset({rule_m_nb}), L, cfn)

        system = ArgumentationSystem(
            language=L, contrariness=cfn,
            strict_rules=R_s,
            defeasible_rules=frozenset(),
        )
        kb = KnowledgeBase(
            axioms=frozenset(),
            premises=frozenset({married, bachelor}),
        )
        pref = PreferenceConfig(
            rule_order=frozenset(),
            premise_order=frozenset(),
            comparison="elitist",
            link="last",
        )

        # Build CSAF manually
        arguments = build_arguments(system, kb)
        attacks_set = compute_attacks(arguments, system)
        defeat_attacks = compute_defeats(attacks_set, arguments, system, kb, pref)
        defeats = frozenset(
            (atk.attacker, atk.target) for atk in defeat_attacks
        )

        arg_list = sorted(arguments, key=lambda a: repr(a))
        arg_to_id = {a: f"arg_{i}" for i, a in enumerate(arg_list)}
        id_to_arg = {v: k for k, v in arg_to_id.items()}

        af = ArgumentationFramework(
            arguments=frozenset(arg_to_id.values()),
            defeats=frozenset(
                (arg_to_id[a], arg_to_id[b])
                for a, b in defeats
                if a in arg_to_id and b in arg_to_id
            ),
            attacks=frozenset(
                (arg_to_id[atk.attacker], arg_to_id[atk.target])
                for atk in attacks_set
                if atk.attacker in arg_to_id and atk.target in arg_to_id
            ),
        )

        csaf = CSAF(
            system=system, kb=kb, pref=pref, arguments=arguments,
            attacks=attacks_set, defeats=defeats, framework=af,
            arg_to_id=arg_to_id, id_to_arg=id_to_arg,
        )

        # Compute grounded extension
        ext = grounded_extension(csaf.framework)

        # Direct consistency: extension should NOT contain both
        # bachelor and ~bachelor conclusions
        ext_conclusions = {conc(csaf.id_to_arg[aid]) for aid in ext}
        assert not (bachelor in ext_conclusions and not_bachelor in ext_conclusions), (
            f"Grounded extension contains both bachelor and ~bachelor — "
            f"direct consistency violated. Conclusions: {ext_conclusions}"
        )
