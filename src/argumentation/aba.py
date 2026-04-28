"""Flat assumption-based argumentation and ABA+ preferences.

Bondarenko, Dung, Kowalski, and Toni 1997 define ABA frameworks through a
deductive system, assumptions, and contraries; flatness means assumption sets
are closed under deduction. Toni 2014 gives the forward-deduction operational
view used here. Cyras and Toni 2016 define ABA+ by adding preferences over
assumptions and reversing attacks supported by weaker assumptions.

This module intentionally accepts flat ABA only. Non-flat ABA is rejected at
construction time rather than deferred to a partial runtime path.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain, combinations
from typing import Mapping, TypeAlias

from argumentation.aspic import Literal, Rule
from argumentation.dung import ArgumentationFramework


AssumptionSet: TypeAlias = frozenset[Literal]
ABAInput: TypeAlias = "ABAFramework | ABAPlusFramework"


class NotFlatABAError(ValueError):
    """Raised when a framework violates the flat-ABA boundary."""


@dataclass(frozen=True)
class ABAArgument:
    assumptions: AssumptionSet
    conclusion: Literal


@dataclass(frozen=True)
class ABAFramework:
    language: frozenset[Literal]
    rules: frozenset[Rule]
    assumptions: AssumptionSet
    contrary: Mapping[Literal, Literal]

    def __post_init__(self) -> None:
        language = frozenset(self.language)
        rules = frozenset(self.rules)
        assumptions = frozenset(self.assumptions)
        contrary = dict(self.contrary)
        if not assumptions <= language:
            raise ValueError("ABA assumptions must be contained in the language")
        if set(contrary) != set(assumptions):
            raise ValueError("ABA contrary map must define exactly one contrary per assumption")
        rule_literals = frozenset(
            chain.from_iterable(rule.antecedents for rule in rules)
        ) | frozenset(rule.consequent for rule in rules)
        if not rule_literals <= language:
            raise ValueError("ABA rules must reference only language literals")
        if not frozenset(contrary.values()) <= language:
            raise ValueError("ABA contraries must be language literals")
        assumption_heads = assumptions & frozenset(rule.consequent for rule in rules)
        if assumption_heads:
            raise NotFlatABAError(
                "flat ABA requires no assumption to be the head of a rule "
                f"(Bondarenko et al. 1997 Def 4.10): {sorted(map(repr, assumption_heads))}"
            )
        object.__setattr__(self, "language", language)
        object.__setattr__(self, "rules", rules)
        object.__setattr__(self, "assumptions", assumptions)
        object.__setattr__(self, "contrary", contrary)


@dataclass(frozen=True)
class ABAPlusFramework:
    framework: ABAFramework
    preference_order: frozenset[tuple[Literal, Literal]]

    def __post_init__(self) -> None:
        assumptions = self.framework.assumptions
        if any(left not in assumptions or right not in assumptions for left, right in self.preference_order):
            raise ValueError("ABA+ preferences must range over assumptions")
        object.__setattr__(self, "preference_order", _transitive_closure(self.preference_order))


def derives(framework: ABAFramework, premises: AssumptionSet, conclusion: Literal) -> bool:
    return conclusion in _closure(framework, premises)


def argument_for(framework: ABAFramework, conclusion: Literal) -> ABAArgument:
    for support in sorted(_all_subsets(framework.assumptions), key=lambda item: (len(item), sorted(map(repr, item)))):
        if derives(framework, support, conclusion):
            return ABAArgument(support, conclusion)
    raise ValueError(f"no ABA argument derives {conclusion!r}")


def attacks(
    framework: ABAFramework,
    attacker_assumptions: AssumptionSet,
    target_assumptions: AssumptionSet,
) -> bool:
    return bool(_attack_supports(framework, attacker_assumptions, target_assumptions))


def attacks_with_preferences(
    framework: ABAPlusFramework,
    attacker_assumptions: AssumptionSet,
    target_assumptions: AssumptionSet,
) -> bool:
    base = framework.framework
    for target in target_assumptions:
        for support in _supports_deriving(base, attacker_assumptions, base.contrary[target]):
            if not any(_strictly_less(framework, assumption, target) for assumption in support):
                return True
    for attacker in attacker_assumptions:
        for support in _supports_deriving(base, target_assumptions, base.contrary[attacker]):
            if any(_strictly_less(framework, assumption, attacker) for assumption in support):
                return True
    return False


def closed(framework: ABAInput, assumptions: AssumptionSet) -> bool:
    base = _base(framework)
    return assumptions <= base.assumptions and (_closure(base, assumptions) & base.assumptions) == assumptions


def conflict_free(framework: ABAInput, assumptions: AssumptionSet) -> bool:
    return not _attacks(framework, assumptions, assumptions)


def admissible(framework: ABAInput, assumptions: AssumptionSet) -> bool:
    return closed(framework, assumptions) and conflict_free(framework, assumptions) and _defends(
        framework,
        assumptions,
        assumptions,
    )


def def_operator(framework: ABAInput, assumptions: AssumptionSet) -> AssumptionSet:
    base = _base(framework)
    return frozenset(
        assumption
        for assumption in base.assumptions
        if _defends(framework, assumptions, frozenset({assumption}))
    )


def complete_extensions(framework: ABAInput) -> tuple[AssumptionSet, ...]:
    extensions = [
        candidate
        for candidate in _all_subsets(_base(framework).assumptions)
        if admissible(framework, candidate) and def_operator(framework, candidate) <= candidate
    ]
    return _sort_extensions(extensions)


def preferred_extensions(framework: ABAInput) -> tuple[AssumptionSet, ...]:
    admissible_sets = [
        candidate
        for candidate in _all_subsets(_base(framework).assumptions)
        if admissible(framework, candidate)
    ]
    return _sort_extensions(
        candidate
        for candidate in admissible_sets
        if not any(candidate < other for other in admissible_sets)
    )


def stable_extensions(framework: ABAInput) -> tuple[AssumptionSet, ...]:
    base = _base(framework)
    return _sort_extensions(
        candidate
        for candidate in _all_subsets(base.assumptions)
        if closed(framework, candidate)
        and conflict_free(framework, candidate)
        and all(
            _attacks(framework, candidate, frozenset({assumption}))
            for assumption in base.assumptions - candidate
        )
    )


def naive_extensions(framework: ABAInput) -> tuple[AssumptionSet, ...]:
    conflict_free_sets = [
        candidate
        for candidate in _all_subsets(_base(framework).assumptions)
        if conflict_free(framework, candidate)
    ]
    return _sort_extensions(
        candidate
        for candidate in conflict_free_sets
        if not any(candidate < other for other in conflict_free_sets)
    )


def grounded_extension(framework: ABAInput) -> AssumptionSet:
    current = frozenset()
    while True:
        next_extension = def_operator(framework, current)
        if next_extension == current:
            return current
        current = next_extension


def well_founded_extension(framework: ABAInput) -> AssumptionSet:
    complete = complete_extensions(framework)
    if not complete:
        return frozenset()
    return frozenset.intersection(*complete)


def ideal_extension(framework: ABAInput) -> AssumptionSet:
    preferred = preferred_extensions(framework)
    if not preferred:
        return frozenset()
    common = frozenset.intersection(*preferred)
    candidates = [
        candidate
        for candidate in _all_subsets(common)
        if admissible(framework, candidate)
    ]
    maximal = [
        candidate
        for candidate in candidates
        if not any(candidate < other for other in candidates)
    ]
    if len(maximal) != 1:
        raise AssertionError("flat ABA ideal extension must be unique")
    return maximal[0]


def aba_to_dung(framework: ABAFramework) -> ArgumentationFramework:
    arguments = frozenset(repr(assumption) for assumption in framework.assumptions)
    defeats = frozenset(
        (repr(attacker), repr(target))
        for attacker in framework.assumptions
        for target in framework.assumptions
        if attacks(framework, frozenset({attacker}), frozenset({target}))
    )
    return ArgumentationFramework(arguments=arguments, defeats=defeats)


def _base(framework: ABAInput) -> ABAFramework:
    return framework.framework if isinstance(framework, ABAPlusFramework) else framework


def _attacks(framework: ABAInput, attacker: AssumptionSet, target: AssumptionSet) -> bool:
    if isinstance(framework, ABAPlusFramework):
        return attacks_with_preferences(framework, attacker, target)
    return attacks(framework, attacker, target)


def _closure(framework: ABAFramework, premises: AssumptionSet) -> frozenset[Literal]:
    closure = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if set(rule.antecedents) <= closure and rule.consequent not in closure:
                closure.add(rule.consequent)
                changed = True
    return frozenset(closure)


def _supports_deriving(
    framework: ABAFramework,
    available: AssumptionSet,
    conclusion: Literal,
) -> tuple[AssumptionSet, ...]:
    return tuple(
        support
        for support in _all_subsets(available)
        if derives(framework, support, conclusion)
    )


def _attack_supports(
    framework: ABAFramework,
    attacker_assumptions: AssumptionSet,
    target_assumptions: AssumptionSet,
) -> tuple[AssumptionSet, ...]:
    supports: list[AssumptionSet] = []
    for target in target_assumptions:
        supports.extend(
            _supports_deriving(
                framework,
                attacker_assumptions,
                framework.contrary[target],
            )
        )
    return tuple(supports)


def _defends(framework: ABAInput, defender: AssumptionSet, target: AssumptionSet) -> bool:
    base = _base(framework)
    for attacker in _all_subsets(base.assumptions):
        if attacker and closed(framework, attacker) and _attacks(framework, attacker, target):
            if not _attacks(framework, defender, attacker):
                return False
    return True


def _all_subsets(items: frozenset[Literal]) -> tuple[AssumptionSet, ...]:
    ordered = sorted(items, key=repr)
    return tuple(
        frozenset(combination)
        for size in range(len(ordered) + 1)
        for combination in combinations(ordered, size)
    )


def _sort_extensions(extensions) -> tuple[AssumptionSet, ...]:
    return tuple(sorted(extensions, key=lambda ext: (len(ext), tuple(sorted(map(repr, ext))))))


def _transitive_closure(
    relation: frozenset[tuple[Literal, Literal]],
) -> frozenset[tuple[Literal, Literal]]:
    closure = set(relation)
    changed = True
    while changed:
        changed = False
        for left, middle in tuple(closure):
            for maybe_middle, right in tuple(closure):
                if middle == maybe_middle and (left, right) not in closure:
                    closure.add((left, right))
                    changed = True
    return frozenset(closure)


def _strictly_less(framework: ABAPlusFramework, left: Literal, right: Literal) -> bool:
    return (left, right) in framework.preference_order and (right, left) not in framework.preference_order


__all__ = [
    "ABAArgument",
    "ABAFramework",
    "ABAPlusFramework",
    "AssumptionSet",
    "NotFlatABAError",
    "aba_to_dung",
    "admissible",
    "argument_for",
    "attacks",
    "attacks_with_preferences",
    "closed",
    "complete_extensions",
    "conflict_free",
    "def_operator",
    "derives",
    "grounded_extension",
    "ideal_extension",
    "naive_extensions",
    "preferred_extensions",
    "stable_extensions",
    "well_founded_extension",
]
