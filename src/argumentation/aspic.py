"""ASPIC+ logical language and contrariness function.

Implements the foundational data structures for ASPIC+ structured
argumentation, following Modgil & Prakken (2018) Definitions 1-2.

This is a leaf module with no application-layer dependency.

References:
    Modgil, S. & Prakken, H. (2018). A general account of argumentation
    with preferences. Artificial Intelligence, 248, 51-104.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeAlias, TypeVar, Union

if TYPE_CHECKING:
    from argumentation.dung import ArgumentationFramework

Scalar: TypeAlias = str | int | float | bool


@dataclass(frozen=True)
class GroundAtom:
    """An atomic formula: a predicate applied to ground arguments.

    Matches standard logic terminology (Riveret 2017 Def 2.1,
    Diller et al. 2025 Def 7). Nullary atoms (no arguments)
    represent propositional symbols — existing claim IDs.

    Attributes:
        predicate: The predicate name (or claim ID for nullary atoms).
        arguments: Ground terms. Empty tuple for propositional atoms.
    """

    predicate: str
    arguments: tuple[Scalar, ...] = ()

    def __repr__(self) -> str:
        if not self.arguments:
            return self.predicate
        args = ", ".join(str(a) for a in self.arguments)
        return f"{self.predicate}({args})"


@dataclass(frozen=True)
class Literal:
    """A literal in the logical language L.

    A literal is an atom or its negation. The ``.contrary`` property
    returns the complementary literal (negation of this literal).

    Modgil & Prakken 2018, Def 1 (p.8): L is a logical language
    closed under the contrariness function — every formula's
    contraries/contradictories are also in L.

    Attributes:
        atom: The propositional atom name.
        negated: Whether this literal is the negation of the atom.
    """

    atom: GroundAtom
    negated: bool = False

    @property
    def contrary(self) -> Literal:
        """Return the complementary literal.

        For atom p: p.contrary = ~p, and ~p.contrary = p.
        This is an involution: a.contrary.contrary == a.

        Modgil & Prakken 2018, Def 1 (p.8).
        """
        return Literal(self.atom, not self.negated)

    def __repr__(self) -> str:
        if self.negated:
            return f"~{self.atom}"
        return repr(self.atom)


@dataclass(frozen=True)
class ContrarinessFn:
    """Contrariness function over a logical language.

    Maps pairs of literals to their conflict relationship:
    contradictories (symmetric) or contraries (asymmetric).

    Modgil & Prakken 2018, Def 1 (p.8):
        - If phi in bar(psi) AND psi in bar(phi): contradictories
        - If phi in bar(psi) AND psi NOT in bar(phi): phi is a contrary of psi

    Attributes:
        contradictories: Frozenset of (Literal, Literal) pairs that are
            contradictory. Only one direction need be stored; lookup
            checks both orderings.
        contraries: Frozenset of directed (Literal, Literal) pairs where
            the left literal is a contrary of the right literal but the
            reverse direction need not hold.
    """

    contradictories: frozenset[tuple[Literal, Literal]]
    contraries: frozenset[tuple[Literal, Literal]] = frozenset()

    def is_contradictory(self, a: Literal, b: Literal) -> bool:
        """True if a and b are contradictories (symmetric conflict).

        Modgil & Prakken 2018, Def 2 (p.8): phi and psi are
        contradictories iff phi in bar(psi) AND psi in bar(phi).
        """
        if a == b:
            return False
        return (a, b) in self.contradictories or (b, a) in self.contradictories

    def is_contrary(self, a: Literal, b: Literal) -> bool:
        """True if a is a contrary of b.

        Modgil & Prakken 2018, Def 2 (p.8): phi is a contrary of psi
        iff phi in bar(psi) and psi is not in bar(phi). Contraries are
        therefore directional and exclude contradictories.
        """
        if a == b or self.is_contradictory(a, b):
            return False
        return (a, b) in self.contraries

    def is_conflicting(self, a: Literal, b: Literal) -> bool:
        """True if the literals conflict in either contrary direction or by contradiction."""
        return (
            self.is_contradictory(a, b)
            or self.is_contrary(a, b)
            or self.is_contrary(b, a)
        )


@dataclass(frozen=True)
class Rule:
    """A strict or defeasible inference rule.

    Modgil & Prakken 2018, Def 2 (p.8).
    Strict rules: antecedents -> consequent (no exceptions).
    Defeasible rules: antecedents => consequent (presumptive).
    Defeasible rules have a name n(r) for undercutting attacks.

    Prakken 2010, Def 3.4 (p.47-48):
        - Strict rule: phi_1, ..., phi_n -> phi
        - Defeasible rule: phi_1, ..., phi_n => phi

    Attributes:
        antecedents: Tuple of literals forming the rule body.
        consequent: The literal concluded by the rule.
        kind: Either "strict" or "defeasible".
        name: n(r) for defeasible rules (Modgil & Prakken 2018, Def 2, p.8).
            Required for defeasible rules to enable undercutting attacks.
            None for strict rules.
    """

    antecedents: tuple[Literal, ...]
    consequent: Literal
    kind: str  # "strict" or "defeasible"
    name: str | None = None  # n(r) for defeasible rules


@dataclass(frozen=True)
class PremiseArg:
    """Argument from a premise. Modgil & Prakken 2018, Def 5 clause 1."""
    premise: Literal
    is_axiom: bool  # True if in K_n, False if in K_p
    _hash: int | None = field(default=None, init=False, repr=False, compare=False, hash=False)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, PremiseArg):
            return NotImplemented
        return (
            self.premise == other.premise
            and self.is_axiom == other.is_axiom
        )

    def __hash__(self) -> int:
        if self._hash is None:
            object.__setattr__(
                self,
                "_hash",
                hash((PremiseArg, self.premise, self.is_axiom)),
            )
        cached = self._hash
        if cached is None:
            raise RuntimeError("PremiseArg hash cache was not initialized")
        return cached


@dataclass(frozen=True)
class StrictArg:
    """Argument via strict rule. Modgil & Prakken 2018, Def 5 clause 2."""
    sub_args: tuple[Argument, ...]
    rule: Rule  # must have kind == "strict"
    _hash: int | None = field(default=None, init=False, repr=False, compare=False, hash=False)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, StrictArg):
            return NotImplemented
        if self.rule != other.rule:
            return False
        if hash(self) != hash(other):
            return False
        return self.sub_args == other.sub_args

    def __hash__(self) -> int:
        if self._hash is None:
            object.__setattr__(
                self,
                "_hash",
                hash((StrictArg, self.sub_args, self.rule)),
            )
        cached = self._hash
        if cached is None:
            raise RuntimeError("StrictArg hash cache was not initialized")
        return cached


@dataclass(frozen=True)
class DefeasibleArg:
    """Argument via defeasible rule. Modgil & Prakken 2018, Def 5 clause 3."""
    sub_args: tuple[Argument, ...]
    rule: Rule  # must have kind == "defeasible"
    _hash: int | None = field(default=None, init=False, repr=False, compare=False, hash=False)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, DefeasibleArg):
            return NotImplemented
        if self.rule != other.rule:
            return False
        if hash(self) != hash(other):
            return False
        return self.sub_args == other.sub_args

    def __hash__(self) -> int:
        if self._hash is None:
            object.__setattr__(
                self,
                "_hash",
                hash((DefeasibleArg, self.sub_args, self.rule)),
            )
        cached = self._hash
        if cached is None:
            raise RuntimeError("DefeasibleArg hash cache was not initialized")
        return cached


Argument: TypeAlias = Union[PremiseArg, StrictArg, DefeasibleArg]
PreferenceOrderedT = TypeVar("PreferenceOrderedT", Literal, Rule)


@dataclass(frozen=True)
class Attack:
    """An attack from argument A on sub-argument B' of B.

    Modgil & Prakken 2018, Def 8 (p.11): three types of attack:
    - Undermining (Def 8a): A attacks ordinary premise of B'
    - Rebutting (Def 8b): A attacks defeasible conclusion of B'
    - Undercutting (Def 8c): A attacks defeasible rule applicability of B'
    """
    attacker: Argument
    target: Argument       # B — the argument being attacked
    target_sub: Argument   # B' — the specific sub-argument targeted
    kind: str              # "undermining", "rebutting", or "undercutting"


@dataclass(frozen=True)
class KnowledgeBase:
    """KB = (K_n, K_p). Modgil & Prakken 2018, Def 4 (p.9)."""
    axioms: frozenset[Literal]    # K_n — not attackable
    premises: frozenset[Literal]  # K_p — attackable


@dataclass(frozen=True)
class PreferenceConfig:
    """Configuration for preference-based defeat filtering.

    Modgil & Prakken 2018, Defs 19-21 (p.21).

    Defeat filtering uses preference orderings to determine when attacks
    succeed as defeats. Undercutting always succeeds (Def 9, p.12).
    Rebutting and undermining succeed only when the attacker is not
    strictly weaker than the targeted sub-argument (Def 9, p.12).

    The preference ordering over arguments is derived from orderings
    over rules and premises via set comparison (Def 19) and either
    last-link (Def 20) or weakest-link (Def 21) principles.

    Attributes:
        rule_order: Pairs (weaker, stronger) of defeasible rules forming
            a strict partial order (irreflexive, transitive). Def 22 (p.22).
        premise_order: Pairs (weaker, stronger) of ordinary premises forming
            a strict partial order (irreflexive, transitive). Def 22 (p.22).
        comparison: Set comparison mode — "elitist" or "democratic" (Def 19, p.21).
        link: Preference principle — "last" or "weakest" (Defs 20-21, p.21).
    """
    rule_order: frozenset[tuple[Rule, Rule]]      # (weaker, stronger) pairs
    premise_order: frozenset[tuple[Literal, Literal]]  # (weaker, stronger) pairs
    comparison: str  # "elitist" or "democratic"
    link: str        # "last" or "weakest"


@dataclass(frozen=True)
class ArgumentationSystem:
    """AS = (L, contrariness, R_s, R_d, n). Modgil & Prakken 2018, Def 2."""
    language: frozenset[Literal]
    contrariness: ContrarinessFn
    strict_rules: frozenset[Rule]
    defeasible_rules: frozenset[Rule]


def _is_degenerate_rule(rule: Rule, contrariness: ContrarinessFn) -> bool:
    """Check if a strict rule is degenerate and should be excluded.

    A rule is degenerate if it has a contradictory pair among its
    antecedents (both φ and ~φ). Such rules can only fire when
    contradictory information is already present, and their
    transpositions produce ill-formed rules.

    Modgil & Prakken 2018, Def 12 (p.13): transposition closure requires
    well-formed rules. Rules with contradictory antecedent pairs cannot
    be properly closed under transposition.

    Note: rules where an antecedent is the contrary of the consequent
    (e.g., ~r, p -> ~p) are NOT degenerate — they are valid transpositions
    needed for the rationality postulates (Thm 14, p.18: direct consistency).
    """
    antes = rule.antecedents
    for i, left in enumerate(antes):
        for right in antes[i + 1:]:
            if contrariness.is_contradictory(left, right):
                return True
    return False


def _contradictories_of(
    literal: Literal,
    language: frozenset[Literal],
    contrariness: ContrarinessFn,
) -> tuple[Literal, ...]:
    """Return the explicit contradictories of ``literal`` in ``language``.

    Prakken 2010, Def. 5.1 (pp. 141-142) defines transposition with the
    argumentation system's ``-`` operator. In this implementation, that
    operator is represented by ``ContrarinessFn.is_contradictory`` rather than
    by the structural ``Literal.contrary`` accessor alone.
    """
    contradictories = tuple(
        sorted(
            (
                other
                for other in language
                if other != literal and contrariness.is_contradictory(literal, other)
            ),
            key=repr,
        )
    )
    if not contradictories:
        raise ValueError(
            "transposition_closure requires every strict-rule literal to have "
            f"an explicit contradictory in the contrariness relation: {literal!r}"
        )
    return contradictories


def transposition_closure(
    rules: frozenset[Rule],
    language: frozenset[Literal],
    contrariness: ContrarinessFn,
) -> frozenset[Rule]:
    """Compute the transposition closure of strict rules.

    Modgil & Prakken 2018, Def 12 (p.13); Prakken 2010, Def 5.1 (p.141).

    For each strict rule A1,...,An -> C and each i (1 <= i <= n):
    the transposed rule A1,...,~C,...,An -> ~Ai must also be in R_s.

    Iterates until fixpoint (no new rules produced).

    Only strict rules are transposed. Defeasible rules are never transposed
    (Def 12 applies to R_s only). The fixpoint always terminates because L
    is finite, bounding the number of possible rules.

    Rules with contradictory antecedent pairs (both φ and ~φ) are excluded:
    they are degenerate (ex falso quodlibet) and their transpositions
    produce rules where the consequent appears in the antecedents,
    violating well-formedness. Similarly, any generated transposition
    whose consequent appears in its own antecedents is excluded.

    Prakken 2010, Defs. 5.1-5.3 (pp. 141-142; local page image
    ``papers/Prakken_2010_AbstractFrameworkArgumentationStructured/pngs/page-012.png``)
    define this as the least fixpoint under adding transpositions. The
    fixpoint computation therefore belongs here; well-definedness checks that
    depend on a particular knowledge base belong to the caller.

    Args:
        rules: The initial set of strict rules.
        language: The logical language L (set of all valid literals).
        contrariness: The explicit contrariness relation providing the
            contradictories used as ``-phi`` during transposition.

    Returns:
        The smallest frozenset of well-formed Rules closed under
        transposition, containing all well-formed input rules.

    Raises:
        ValueError: if a strict-rule literal has no contradictory partner in
            the supplied contrariness relation.
    """
    # Filter out degenerate seed rules with contradictory antecedent pairs.
    closed: set[Rule] = {
        r for r in rules
        if not _is_degenerate_rule(r, contrariness)
    }
    changed = True
    while changed:
        changed = False
        new_rules: set[Rule] = set()
        for r in closed:
            if r.kind != "strict":
                continue
            for i, ante_i in enumerate(r.antecedents):
                for contrary_consequent in _contradictories_of(
                    r.consequent, language, contrariness
                ):
                    for contrary_antecedent in _contradictories_of(
                        ante_i, language, contrariness
                    ):
                        # Prakken 2010, Def. 5.1 (p. 141):
                        # φ1,...,φ(i-1), -ψ, φ(i+1),...,φn -> -φi
                        transposed_antes = list(r.antecedents)
                        transposed_antes[i] = contrary_consequent
                        transposed_consequent = contrary_antecedent
                        if transposed_consequent not in language:
                            continue
                        if any(a not in language for a in transposed_antes):
                            continue
                        if transposed_consequent in transposed_antes:
                            continue
                        new_rule = Rule(
                            antecedents=tuple(transposed_antes),
                            consequent=transposed_consequent,
                            kind="strict",
                            name=None,
                        )
                        if _is_degenerate_rule(new_rule, contrariness):
                            continue
                        if new_rule not in closed:
                            new_rules.add(new_rule)
                            changed = True
        closed.update(new_rules)
    return frozenset(closed)


def strict_closure(
    conclusions: frozenset[Literal],
    strict_rules: frozenset[Rule],
) -> frozenset[Literal]:
    """Closure of literal set under strict rules.

    Modgil & Prakken 2018, Def 3 (p.8).
    Cl_Rs(S) = smallest superset of S closed under R_s.

    If all antecedents of a strict rule are in the set, the consequent
    is added. Iterates until fixpoint (no new literals produced).

    Args:
        conclusions: The initial set of literals to close.
        strict_rules: The set of strict rules R_s.

    Returns:
        The smallest frozenset containing conclusions that is closed
        under strict_rules.
    """
    result = set(conclusions)
    changed = True
    while changed:
        changed = False
        for rule in strict_rules:
            if rule.kind == "strict" and all(a in result for a in rule.antecedents):
                if rule.consequent not in result:
                    result.add(rule.consequent)
                    changed = True
    return frozenset(result)


@functools.cache
def is_c_consistent(
    literals: frozenset[Literal],
    strict_rules: frozenset[Rule],
    contrariness: ContrarinessFn,
) -> bool:
    """Whether a set of literals is c-consistent.

    Modgil & Prakken 2018, Def 6 (p.10): a set S is c-consistent iff
    its strict closure does not derive conflicting literals.
    """
    closed = tuple(sorted(strict_closure(literals, strict_rules), key=repr))
    for i, left in enumerate(closed):
        for right in closed[i + 1:]:
            if contrariness.is_conflicting(left, right):
                return False
    return True


# ── Computed property functions ───────────────────────────────────
# All per Modgil & Prakken 2018, Def 5 (pp.9-10) unless noted.


@functools.cache
def conc(a: Argument) -> Literal:
    """Conclusion of argument. Modgil & Prakken 2018, Def 5."""
    if isinstance(a, PremiseArg):
        return a.premise
    return a.rule.consequent


@functools.cache
def prem(a: Argument) -> frozenset[Literal]:
    """All premises (recursive). Modgil & Prakken 2018, Def 5."""
    if isinstance(a, PremiseArg):
        return frozenset({a.premise})
    premises: set[Literal] = set()
    for sub_arg in a.sub_args:
        premises.update(prem(sub_arg))
    return frozenset(premises)


@functools.cache
def sub(a: Argument) -> frozenset[Argument]:
    """All sub-arguments including self. Modgil & Prakken 2018, Def 5."""
    if isinstance(a, PremiseArg):
        return frozenset({a})
    sub_arguments: set[Argument] = {a}
    for sub_arg in a.sub_args:
        sub_arguments.update(sub(sub_arg))
    return frozenset(sub_arguments)


@functools.cache
def all_concs(a: Argument) -> frozenset[Literal]:
    """All conclusions reachable in the sub-argument tree."""
    if isinstance(a, PremiseArg):
        return frozenset({a.premise})
    conclusions: set[Literal] = {a.rule.consequent}
    for sub_arg in a.sub_args:
        conclusions.update(all_concs(sub_arg))
    return frozenset(conclusions)


@functools.cache
def top_rule(a: Argument) -> Rule | None:
    """Top-level rule. None for PremiseArg. Modgil & Prakken 2018, Def 5."""
    if isinstance(a, PremiseArg):
        return None
    return a.rule


@functools.cache
def def_rules(a: Argument) -> frozenset[Rule]:
    """All defeasible rules used. Modgil & Prakken 2018, Def 5."""
    if isinstance(a, PremiseArg):
        return frozenset()
    rules: set[Rule] = set()
    for sub_arg in a.sub_args:
        rules.update(def_rules(sub_arg))
    if isinstance(a, DefeasibleArg):
        rules.add(a.rule)
    return frozenset(rules)


@functools.cache
def last_def_rules(a: Argument) -> frozenset[Rule]:
    """Last defeasible rules before strict-only chain.

    Modgil & Prakken 2018, p.10: LastDefRules returns the set of
    defeasible rules at the boundary between defeasible and strict
    inference in the argument tree.
    """
    if isinstance(a, PremiseArg):
        return frozenset()
    if isinstance(a, DefeasibleArg):
        return frozenset({a.rule})
    rules: set[Rule] = set()
    for sub_arg in a.sub_args:
        rules.update(last_def_rules(sub_arg))
    return frozenset(rules)


@functools.cache
def prem_p(a: Argument) -> frozenset[Literal]:
    """Ordinary premises only (K_p members). Modgil & Prakken 2018, p.10."""
    if isinstance(a, PremiseArg):
        return frozenset() if a.is_axiom else frozenset({a.premise})
    premises: set[Literal] = set()
    for sub_arg in a.sub_args:
        premises.update(prem_p(sub_arg))
    return frozenset(premises)


def _clear_argument_function_caches() -> None:
    """Clear process-global memo tables before a fresh argument job.

    These helpers cache results over immutable argument trees, which is useful
    within one build/attack/defeat pipeline. Keeping them alive across many
    unrelated Hypothesis-generated systems makes the process-wide caches grow
    without bound and can slow later runs in the same test session.
    """
    conc.cache_clear()
    prem.cache_clear()
    sub.cache_clear()
    all_concs.cache_clear()
    top_rule.cache_clear()
    def_rules.cache_clear()
    last_def_rules.cache_clear()
    prem_p.cache_clear()
    _set_strictly_less.cache_clear()
    _strictly_weaker.cache_clear()


def is_firm(a: Argument) -> bool:
    """True if all premises are axioms (K_n). Prakken 2010, Def 3.8."""
    return len(prem_p(a)) == 0


def is_strict(a: Argument) -> bool:
    """True if no defeasible rules used. Prakken 2010, Def 3.8."""
    return len(def_rules(a)) == 0


def _attack_target_literal(attack: Attack) -> Literal:
    """Return the literal targeted by an ASPIC+ attack."""
    if attack.kind == "undermining":
        assert isinstance(attack.target_sub, PremiseArg)
        return attack.target_sub.premise
    if attack.kind == "rebutting":
        return conc(attack.target_sub)
    if attack.kind == "undercutting":
        rule = top_rule(attack.target_sub)
        if rule is None or rule.name is None:
            raise ValueError("Undercutting attack must target a named defeasible rule")
        return Literal(GroundAtom(rule.name), False)
    raise ValueError(f"Unknown attack kind: {attack.kind}")


def _is_preference_independent_attack(attack: Attack, system: ArgumentationSystem) -> bool:
    """True if the attack succeeds regardless of the preference ordering.

    Modgil & Prakken 2018, Def 9 (p.12): undercutting and attacks based on
    directional contraries are preference-independent. Contradictory attacks
    remain preference-dependent unless they are undercuts.
    """
    if attack.kind == "undercutting":
        return True
    return system.contrariness.is_contrary(
        conc(attack.attacker),
        _attack_target_literal(attack),
    )


# ── Argument construction ─────────────────────────────────────────


def build_arguments(
    system: ArgumentationSystem, kb: KnowledgeBase
) -> frozenset[Argument]:
    """Bottom-up c-consistent argument construction.

    Modgil & Prakken 2018, Def 5 (pp.9-10), Def 7 (p.11);
    Prakken 2010, Def 3.6 (p.36).

    1. Seed: create PremiseArg for each literal in K_n (axiom) and K_p (ordinary).
    2. Index arguments by their conclusion literal.
    3. Iterate until fixpoint: for each rule, enumerate all combinations of
       existing arguments whose conclusions match the rule's antecedents,
       and create the corresponding StrictArg or DefeasibleArg.
    4. Keep only c-consistent arguments: A is included iff Prem(A) is
       c-consistent under the strict rules.

    Terminates because L is finite, bounding the number of distinct conclusions,
    and arguments are deduplicated (frozen dataclasses are hashable).
    """
    import itertools
    _clear_argument_function_caches()

    # Step 1: Seed with premise arguments
    all_args: set[Argument] = set()
    # Index: conclusion literal -> set of arguments with that conclusion
    conc_index: dict[Literal, set[Argument]] = {}

    def _add(arg: Argument) -> bool:
        """Add argument to set and index. Returns True if new."""
        if not is_c_consistent(
            prem(arg),
            system.strict_rules,
            system.contrariness,
        ):
            return False
        if arg in all_args:
            return False
        all_args.add(arg)
        c = conc(arg)
        if c not in conc_index:
            conc_index[c] = set()
        conc_index[c].add(arg)
        return True

    for lit in kb.axioms:
        _add(PremiseArg(premise=lit, is_axiom=True))
    for lit in kb.premises:
        _add(PremiseArg(premise=lit, is_axiom=False))

    # Step 2-3: Iterate until fixpoint
    all_rules = list(system.strict_rules | system.defeasible_rules)
    attempted_rule_combos: set[tuple[int, tuple[int, ...]]] = set()
    changed = True
    while changed:
        changed = False
        for rule in all_rules:
            # For each rule, get the sets of arguments matching each antecedent
            ante_arg_sets: list[tuple[Argument, ...]] = []
            skip = False
            for ante_lit in rule.antecedents:
                args_for_lit = conc_index.get(ante_lit)
                if not args_for_lit:
                    skip = True
                    break
                ante_arg_sets.append(tuple(args_for_lit))
            if skip:
                continue

            # Enumerate all combinations via Cartesian product
            for combo in itertools.product(*ante_arg_sets):
                combo_signature = (id(rule), tuple(id(sub_arg) for sub_arg in combo))
                if combo_signature in attempted_rule_combos:
                    continue
                attempted_rule_combos.add(combo_signature)

                # Acyclicity: the rule's consequent must not already
                # appear as a conclusion in any sub-argument tree.
                # This prevents infinite nesting from rule cycles
                # (e.g., p->q, q->p producing ever-deeper arguments).
                # ASPIC+ arguments are finite trees (Def 5); a conclusion
                # appearing in a sub-argument would create a cycle.
                combo_concs: set[Literal] = set()
                for sub_arg in combo:
                    combo_concs.update(all_concs(sub_arg))
                if rule.consequent in combo_concs:
                    continue

                if rule.kind == "strict":
                    new_arg = StrictArg(sub_args=combo, rule=rule)
                else:
                    new_arg = DefeasibleArg(sub_args=combo, rule=rule)
                if _add(new_arg):
                    changed = True

    return frozenset(all_args)


def _contraries_of(
    literal: Literal,
    contrariness: ContrarinessFn,
    language: frozenset[Literal],
) -> frozenset[Literal]:
    """Find all literals that conflict with the given literal.

    Returns every literal in L that is contradictory to or a contrary of
    the given literal — i.e., every phi such that phi in bar(literal).

    Modgil & Prakken 2018, Def 1 (p.8): bar maps each formula to its
    contraries and contradictories.
    """
    result: set[Literal] = set()
    for other in language:
        if contrariness.is_contradictory(other, literal) or contrariness.is_contrary(
            other, literal
        ):
            result.add(other)
    return frozenset(result)


def build_arguments_for(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    goal: Literal,
    *,
    include_attackers: bool = True,
    max_depth: int = 10,
) -> frozenset[Argument]:
    """Goal-directed argument construction for a specific conclusion.

    Backward chaining from goal through rules to premises.
    Constructs only arguments relevant to the queried conclusion,
    rather than enumerating all possible arguments.

    Modgil & Prakken 2018, Def 5 (pp.9-10): same argument structure
    as build_arguments(), but constructed top-down.

    The algorithm:
    1. Base case: if goal is in kb.axioms or kb.premises, create PremiseArg
    2. Recursive case: find all rules whose consequent matches goal,
       recursively build arguments for each antecedent, combine into
       StrictArg or DefeasibleArg
    3. If include_attackers: build arguments for contraries of goal
       to enable attack computation on the result
    4. Only c-consistent arguments are kept
    5. Depth-limited to prevent infinite recursion through rule cycles

    The existing compute_attacks() and compute_defeats() work unchanged
    on the resulting argument set.

    References:
        Toni (2014): ABA backward chaining from claims to assumptions.
        Besnard & Hunter (2001, Def 6.1, p.215): argument trees rooted
            at a specific conclusion.
        de Kleer (1986, p.214): ATMS applies to consequent reasoning.

    Args:
        system: The argumentation system (L, contrariness, R_s, R_d).
        kb: The knowledge base (K_n, K_p).
        goal: The literal to build arguments for.
        include_attackers: If True, also build arguments for contraries
            of goal and of intermediate conclusions, enabling attack
            computation on the result. Default True.
        max_depth: Maximum recursion depth to prevent infinite loops
            through rule cycles. Default 10.

    Returns:
        Frozenset of all c-consistent arguments relevant to the goal.
    """
    import itertools
    _clear_argument_function_caches()

    all_rules = list(system.strict_rules | system.defeasible_rules)

    # Memoization cache: literal -> frozenset of arguments concluding it
    memo: dict[Literal, frozenset[Argument]] = {}
    # Track literals currently being resolved to detect cycles
    in_progress: set[Literal] = set()
    cycle_tainted: set[Literal] = set()

    def _build_backward(
        target: Literal, depth: int
    ) -> frozenset[Argument]:
        """Recursively build arguments for a target literal."""
        if depth > max_depth:
            return frozenset()

        if target in memo:
            return memo[target]

        # Cycle detection: if we're already resolving this literal
        # higher in the call stack, return empty to break the cycle.
        # ASPIC+ arguments are finite trees (Def 5); cycles are not
        # valid arguments.
        if target in in_progress:
            cycle_tainted.update(in_progress)
            return frozenset()

        in_progress.add(target)
        args: set[Argument] = set()

        # Base case: target is a premise or axiom
        if target in kb.axioms:
            p = PremiseArg(premise=target, is_axiom=True)
            if is_c_consistent(
                prem(p), system.strict_rules, system.contrariness
            ):
                args.add(p)
        if target in kb.premises:
            p = PremiseArg(premise=target, is_axiom=False)
            if is_c_consistent(
                prem(p), system.strict_rules, system.contrariness
            ):
                args.add(p)

        # Recursive case: find rules whose consequent matches target
        for rule in all_rules:
            if rule.consequent != target:
                continue

            # Build arguments for each antecedent
            ante_arg_sets: list[tuple[Argument, ...]] = []
            skip = False
            for ante_lit in rule.antecedents:
                ante_args = _build_backward(ante_lit, depth + 1)
                if not ante_args:
                    skip = True
                    break
                ante_arg_sets.append(tuple(ante_args))
            if skip:
                continue

            # Enumerate combinations via Cartesian product
            for combo in itertools.product(*ante_arg_sets):
                # Acyclicity: the rule's consequent must not already
                # appear as a conclusion in any sub-argument tree.
                # Same check as build_arguments() line 596-604.
                combo_concs: set[Literal] = set()
                for sub_arg in combo:
                    combo_concs.update(all_concs(sub_arg))
                if rule.consequent in combo_concs:
                    continue

                if rule.kind == "strict":
                    new_arg = StrictArg(sub_args=combo, rule=rule)
                else:
                    new_arg = DefeasibleArg(sub_args=combo, rule=rule)

                # c-consistency check
                if is_c_consistent(
                    prem(new_arg),
                    system.strict_rules,
                    system.contrariness,
                ):
                    args.add(new_arg)

        result = frozenset(args)
        in_progress.discard(target)
        if target not in cycle_tainted:
            memo[target] = result
        return result

    # Build arguments for the goal
    goal_args = _build_backward(goal, 0)

    if not include_attackers:
        return goal_args

    # Build arguments for contraries of every attack-relevant literal
    # until the focused set reaches a fixed point. This keeps
    # reinstatement chains of arbitrary depth rather than stopping
    # after a hardcoded two passes.
    all_relevant: set[Argument] = set(goal_args)
    pending_literals: list[Literal] = []
    seen_target_literals: set[Literal] = set()

    def _enqueue_attack_targets(arguments: frozenset[Argument] | set[Argument]) -> None:
        for arg in arguments:
            for s in sub(arg):
                lit = conc(s)
                if lit not in seen_target_literals:
                    seen_target_literals.add(lit)
                    pending_literals.append(lit)
                tr = top_rule(s)
                if tr is not None and tr.kind == "defeasible" and tr.name is not None:
                    name_lit = Literal(GroundAtom(tr.name), False)
                    if name_lit not in seen_target_literals:
                        seen_target_literals.add(name_lit)
                        pending_literals.append(name_lit)

    _enqueue_attack_targets(goal_args)

    while pending_literals:
        lit = pending_literals.pop()
        for contrary_lit in _contraries_of(
            lit, system.contrariness, system.language
        ):
            attacker_args = _build_backward(contrary_lit, 0)
            new_args = attacker_args - all_relevant
            if not new_args:
                continue
            all_relevant.update(new_args)
            _enqueue_attack_targets(new_args)

    return frozenset(all_relevant)


# ── Attack determination ─────────────────────────────────────────


def compute_attacks(
    arguments: frozenset[Argument], system: ArgumentationSystem
) -> frozenset[Attack]:
    """Compute all attacks between arguments.

    Modgil & Prakken 2018, Def 8 (p.11): three attack types.

    For each ordered pair (A, B) in arguments, and each B' in sub(B):

    (a) Undermining: A undermines B on B' iff B' is a PremiseArg with
        is_axiom=False (ordinary premise) and conc(A) is contrary or
        contradictory to B'.premise. (Def 8a, p.11)

    (b) Rebutting: A rebuts B on B' iff top_rule(B') is defeasible and
        conc(A) is contrary or contradictory to conc(B'). (Def 8b, p.11;
        Pollock 1987, Def 2.4, p.485)

    (c) Undercutting: A undercuts B on B' iff top_rule(B') is a defeasible
        rule r with name n(r), and conc(A) is contrary or contradictory to
        Literal(n(r), False). (Def 8c, p.11; Pollock 1987, Def 2.5, p.485)

    Firm+strict sub-arguments are never targeted: they have no ordinary
    premises (so no undermining) and no defeasible rules (so no rebutting
    or undercutting). This is a consequence of Def 18 (p.16).

    Args:
        arguments: The set of all arguments built from the system and KB.
        system: The argumentation system providing the contrariness function.

    Returns:
        Frozenset of all Attack instances.
    """
    cfn = system.contrariness
    argument_list = tuple(arguments)
    argument_index = {arg: idx for idx, arg in enumerate(argument_list)}
    attack_keys: set[tuple[int, int, int, str]] = set()

    # Pre-compute sub-arguments and conclusion index so we can reason from
    # potentially attackable target literals to candidate attackers, instead
    # of scanning every argument against every target/sub-target pair.
    sub_cache: dict[Argument, frozenset[Argument]] = {
        b: sub(b) for b in arguments
    }
    conc_index: dict[Literal, set[Argument]] = {}
    for arg in arguments:
        conc_index.setdefault(conc(arg), set()).add(arg)

    attack_points: list[tuple[str, Argument, Argument, Literal]] = []
    target_literals: set[Literal] = set()

    for b in arguments:
        for b_prime in sub_cache[b]:
            # Skip firm+strict sub-arguments — unattackable
            # (Def 18, p.16: no ordinary premises, no defeasible rules)
            if is_firm(b_prime) and is_strict(b_prime):
                continue

            # (a) Undermining (Def 8a, p.11)
            if isinstance(b_prime, PremiseArg) and not b_prime.is_axiom:
                target_lit = b_prime.premise
                attack_points.append(("undermining", b, b_prime, target_lit))
                target_literals.add(target_lit)

            tr = top_rule(b_prime)
            if tr is None or tr.kind != "defeasible":
                continue

            # (b) Rebutting (Def 8b, p.11)
            rebut_target = conc(b_prime)
            attack_points.append(("rebutting", b, b_prime, rebut_target))
            target_literals.add(rebut_target)

            # (c) Undercutting (Def 8c, p.11)
            if tr.name is not None:
                name_lit = Literal(GroundAtom(tr.name), False)
                attack_points.append(("undercutting", b, b_prime, name_lit))
                target_literals.add(name_lit)

    candidate_attackers: dict[Literal, frozenset[Argument]] = {}
    for target_lit in target_literals:
        candidates: set[Argument] = set()
        for conc_lit, args_with_conc in conc_index.items():
            if (
                cfn.is_contrary(conc_lit, target_lit)
                or cfn.is_contradictory(conc_lit, target_lit)
            ):
                candidates.update(args_with_conc)
        candidate_attackers[target_lit] = frozenset(candidates)

    for kind, target, target_sub, target_lit in attack_points:
        for attacker in candidate_attackers.get(target_lit, frozenset()):
            attack_keys.add(
                (
                    argument_index[attacker],
                    argument_index[target],
                    argument_index[target_sub],
                    kind,
                )
            )

    return frozenset(
        Attack(
            attacker=argument_list[attacker_idx],
            target=argument_list[target_idx],
            target_sub=argument_list[target_sub_idx],
            kind=kind,
        )
        for attacker_idx, target_idx, target_sub_idx, kind in attack_keys
    )


# ── Defeat determination ──────────────────────────────────────────


@functools.cache
def _set_strictly_less(
    gamma: frozenset[PreferenceOrderedT],
    gamma_prime: frozenset[PreferenceOrderedT],
    base_order: frozenset[tuple[PreferenceOrderedT, PreferenceOrderedT]],
    comparison: str,
) -> bool:
    """Set comparison Gamma <_s Gamma' per Modgil & Prakken 2018, Def 19 (p.21).

    Determines if set ``gamma`` is strictly less than ``gamma_prime``
    under a base ordering, using either Elitist or Democratic comparison.

    Def 19 (p.21):
    - Empty Gamma is never strictly less than anything.
    - Elitist: exists X in Gamma s.t. forall Y in Gamma', (X, Y) in base_order.
    - Democratic: forall X in Gamma, exists Y in Gamma' s.t. (X, Y) in base_order.

    The base_order contains (weaker, stronger) pairs — i.e., (X, Y) means X < Y.

    Args:
        gamma: The candidate weaker set.
        gamma_prime: The candidate stronger set.
        base_order: Pairs (weaker, stronger) forming a strict partial order.
        comparison: "elitist" or "democratic" (Def 19, p.21).

    Returns:
        True if gamma <_s gamma_prime.
    """
    # Modgil & Prakken 2018, Def. 19 (p.21) gives two explicit edge cases:
    # empty Gamma is never strictly less than anything, while non-empty Gamma
    # is strictly less than empty Gamma'. Defs. 20-21 rely on that lifting when
    # comparing defeasible arguments against firm/strict target sub-arguments.
    if not gamma:
        return False
    if not gamma_prime:
        return True

    if comparison == "elitist":
        # Def 19 (p.21), Elitist: Gamma <_Eli Gamma' iff
        # exists X in Gamma s.t. forall Y in Gamma', X < Y.
        # Gamma is weaker if one of its own elements is below every
        # element of Gamma'.
        for x in gamma:
            if all((x, y) in base_order for y in gamma_prime):
                return True
        return False
    elif comparison == "democratic":
        # Def 19 (p.21), Democratic: Gamma <_Dem Gamma' iff
        # forall X in Gamma, exists Y in Gamma' s.t. X < Y.
        # Gamma is weaker if every element in Gamma is dominated by
        # something in Gamma'.
        for x in gamma:
            if not any((x, y) in base_order for y in gamma_prime):
                return False
        return True
    else:
        raise ValueError(f"Unknown comparison mode: {comparison}")


@functools.cache
def _strictly_weaker(
    a: Argument,
    b: Argument,
    pref: PreferenceConfig,
    kb: KnowledgeBase,
) -> bool:
    """Determine if argument ``a`` is strictly weaker than ``b``.

    Uses the configured preference principle to derive argument ordering
    from the base orderings over rules and premises.

    Modgil & Prakken 2018:
    - Def 20 (p.21): Last-link principle.
    - Def 21 (p.21): Weakest-link principle.
    - Def 22 (p.22): The inducing ordering is a strict partial order.

    Args:
        a: Candidate weaker argument.
        b: Candidate stronger argument.
        pref: Preference configuration with orderings and comparison mode.
        kb: Knowledge base (needed to determine firm/strict status).

    Returns:
        True if a is strictly weaker than b (a prec b).
    """
    if pref.link == "last":
        # Def 20 (p.21): Last-link principle
        # a prec b iff:
        #   LastDefRules(a) <_s LastDefRules(b)
        #   OR (both have empty LastDefRules AND Prem_p(a) <_s Prem_p(b))
        ldr_a = last_def_rules(a)
        ldr_b = last_def_rules(b)
        if ldr_a or ldr_b:
            # At least one has last defeasible rules — compare rules
            return _set_strictly_less(
                ldr_a, ldr_b, pref.rule_order, pref.comparison
            )
        else:
            # Both have empty LastDefRules — compare ordinary premises
            return _set_strictly_less(
                prem_p(a), prem_p(b), pref.premise_order, pref.comparison
            )
    elif pref.link == "weakest":
        # Def 21 (p.21): Weakest-link principle
        # a prec b iff:
        #   If both strict: Prem_p(a) <_s Prem_p(b)
        #   If both firm: DefRules(a) <_s DefRules(b)
        #   Otherwise: Prem_p(a) <_s Prem_p(b) AND DefRules(a) <_s DefRules(b)
        a_strict = is_strict(a)
        b_strict = is_strict(b)
        a_firm = is_firm(a)
        b_firm = is_firm(b)

        if a_strict and b_strict:
            # Both strict — compare ordinary premises only
            return _set_strictly_less(
                prem_p(a), prem_p(b), pref.premise_order, pref.comparison
            )
        elif a_firm and b_firm:
            # Both firm — compare defeasible rules only
            return _set_strictly_less(
                def_rules(a), def_rules(b), pref.rule_order, pref.comparison
            )
        else:
            # General case — both conditions must hold
            return (
                _set_strictly_less(
                    prem_p(a), prem_p(b), pref.premise_order, pref.comparison
                )
                and _set_strictly_less(
                    def_rules(a), def_rules(b), pref.rule_order, pref.comparison
                )
            )
    else:
        raise ValueError(f"Unknown link mode: {pref.link}")


def compute_defeats(
    attacks: frozenset[Attack],
    arguments: frozenset[Argument],
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    pref: PreferenceConfig,
) -> frozenset[Attack]:
    """Filter attacks into defeats using preference orderings.

    Modgil & Prakken 2018, Def 9 (p.12):
    - Undercutting: ALWAYS a defeat. No preference check.
      (Pollock 1987, Def 2.5, p.485)
    - Contrary rebutting / undermining: ALWAYS a defeat.
    - Contradictory rebutting / undermining: defeat iff A is NOT strictly
      weaker than B'.

    The preference comparison is between the attacker A and the targeted
    sub-argument B' (attack.target_sub), not the whole target B.

    Args:
        attacks: The set of all attacks from compute_attacks.
        arguments: The set of all arguments.
        system: The argumentation system.
        kb: The knowledge base.
        pref: Preference configuration (orderings, comparison, link).

    Returns:
        Frozenset of Attack instances that succeed as defeats.
    """
    argument_list = tuple(arguments)
    argument_index = {arg: idx for idx, arg in enumerate(argument_list)}
    defeat_keys: set[tuple[int, int, int, str]] = set()

    for atk in attacks:
        key = (
            argument_index[atk.attacker],
            argument_index[atk.target],
            argument_index[atk.target_sub],
            atk.kind,
        )
        if _is_preference_independent_attack(atk, system):
            # Undercutting and directional-contrary attacks always succeed
            # (Modgil & Prakken 2018, Def 9, p.12).
            defeat_keys.add(key)
        else:
            # Rebutting or undermining: defeat iff attacker is NOT strictly
            # weaker than the targeted sub-argument B' (Def. 9, p.12), even
            # when the attacker also happens to equal the whole target.
            if not _strictly_weaker(atk.attacker, atk.target_sub, pref, kb):
                defeat_keys.add(key)

    return frozenset(
        Attack(
            attacker=argument_list[attacker_idx],
            target=argument_list[target_idx],
            target_sub=argument_list[target_sub_idx],
            kind=kind,
        )
        for attacker_idx, target_idx, target_sub_idx, kind in defeat_keys
    )


# ── Complete Structured Argumentation Framework ──────────────────


@dataclass(frozen=True)
class CSAF:
    """Complete Structured Argumentation Framework.

    Bundles all components of a well-formed c-SAF for property testing:
    the argumentation system, knowledge base, preference configuration,
    computed arguments/attacks/defeats, and the derived Dung AF.

    Modgil & Prakken 2018, Def 12 (p.13): a c-SAF is well-defined iff
    it is axiom consistent, well-formed, and closed under transposition.

    Attributes:
        system: The argumentation system (L, contrariness, R_s, R_d).
        kb: The knowledge base (K_n, K_p).
        pref: The preference configuration (orderings, comparison, link).
        arguments: All arguments built from the system and KB.
        attacks: All attacks between arguments (Attack objects).
        defeats: Defeat pairs (attacker, target) after preference filtering.
        framework: The derived Dung AF for extension computation.
        arg_to_id: Mapping from Argument to string ID.
        id_to_arg: Mapping from string ID to Argument.
    """
    system: ArgumentationSystem
    kb: KnowledgeBase
    pref: PreferenceConfig
    arguments: frozenset[Argument]
    attacks: frozenset[Attack]
    defeats: frozenset[tuple[Argument, Argument]]
    framework: ArgumentationFramework  # from dung.py
    arg_to_id: dict[Argument, str]
    id_to_arg: dict[str, Argument]
