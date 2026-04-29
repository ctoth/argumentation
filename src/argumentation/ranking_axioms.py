"""Executable checks for common ranking-semantics postulates.

The predicates in this module materialize the ranking-postulate vocabulary from
Amgoud and Ben-Naim 2013 pp. 3-8 and Bonzon et al. 2016 pp. 1-2.  They check a
single finite framework/result pair; callers that need universal claims should
run them across generated or enumerated framework families.
"""

from __future__ import annotations

from collections.abc import Callable

from argumentation.dung import ArgumentationFramework
from argumentation.ranking import RankingResult

RankingSemantics = Callable[[ArgumentationFramework], RankingResult]


def strict_preference_transitive(result: RankingResult) -> bool:
    """Return whether strict preference induced by the ranking is transitive."""

    arguments = frozenset(result.scores)
    return all(
        not (result.strictly_prefers(left, middle) and result.strictly_prefers(middle, right))
        or result.strictly_prefers(left, right)
        for left in arguments
        for middle in arguments
        for right in arguments
    )


def abstraction(
    semantics: RankingSemantics,
    framework: ArgumentationFramework,
) -> bool:
    """Check one canonical isomorphism witness for abstraction.

    Amgoud and Ben-Naim 2013 p. 3: rankings must be invariant under argument
    renaming.  The predicate renames every argument deterministically and checks
    that every pairwise comparison is preserved.
    """

    renaming = {
        argument: f"iso_{index}"
        for index, argument in enumerate(sorted(framework.arguments))
    }
    renamed = ArgumentationFramework(
        arguments=frozenset(renaming.values()),
        defeats=frozenset((renaming[left], renaming[right]) for left, right in framework.defeats),
        attacks=(
            None
            if framework.attacks is None
            else frozenset((renaming[left], renaming[right]) for left, right in framework.attacks)
        ),
    )
    original_result = semantics(framework)
    renamed_result = semantics(renamed)

    return all(
        _same_pair_order(
            original_result,
            left,
            right,
            renamed_result,
            renaming[left],
            renaming[right],
        )
        for left in framework.arguments
        for right in framework.arguments
    )


def independence(
    semantics: RankingSemantics,
    framework: ArgumentationFramework,
) -> bool:
    """Check weak-component independence for the supplied framework.

    Amgoud and Ben-Naim 2013 p. 4: rankings inside one disconnected component
    must not change because another component is present.
    """

    full_result = semantics(framework)
    for component in _weak_components(framework):
        if len(component) < 2:
            continue
        component_framework = _induced_framework(framework, component)
        component_result = semantics(component_framework)
        for left in component:
            for right in component:
                if not _same_pair_order(full_result, left, right, component_result, left, right):
                    return False
    return True


def void_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check that unattacked arguments outrank attacked arguments.

    Amgoud and Ben-Naim 2013 pp. 4-5 and Bonzon et al. 2016 p. 1: every
    unattacked argument must be strictly above every attacked argument.
    """

    attackers = _attackers(framework)
    unattacked = {argument for argument, values in attackers.items() if not values}
    attacked = set(framework.arguments) - unattacked
    return all(
        result.strictly_prefers(left, right)
        for left in unattacked
        for right in attacked
    )


def self_contradiction(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check Bonzon et al. 2016 p. 1 self-contradiction precedence."""

    self_attacking = {argument for argument in framework.arguments if (argument, argument) in _attack_relation(framework)}
    clean = set(framework.arguments) - self_attacking
    return all(
        not result.strictly_prefers(self_attacker, other)
        for self_attacker in self_attacking
        for other in clean
    )


def defense_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check Amgoud and Ben-Naim 2013 p. 5 defense precedence."""

    attackers = _attackers(framework)
    for defended in framework.arguments:
        defended_attackers = attackers[defended]
        if not defended_attackers or not _every_attacker_is_attacked(defended_attackers, framework):
            continue
        for undefended in framework.arguments:
            undefended_attackers = attackers[undefended]
            if (
                len(defended_attackers) == len(undefended_attackers)
                and undefended_attackers
                and not _any_attacker_is_attacked(undefended_attackers, framework)
                and not result.strictly_prefers(defended, undefended)
            ):
                return False
    return True


def counter_transitivity(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check Amgoud and Ben-Naim 2013 p. 6 counter-transitivity."""

    attackers = _attackers(framework)
    for left in framework.arguments:
        for right in framework.arguments:
            if _group_at_least_as_acceptable(
                attackers[right],
                attackers[left],
                result,
                strict=False,
            ) and not _at_least_as_acceptable(left, right, result):
                return False
    return True


def strict_counter_transitivity(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check Amgoud and Ben-Naim 2013 p. 6 strict counter-transitivity."""

    attackers = _attackers(framework)
    for left in framework.arguments:
        for right in framework.arguments:
            if _group_at_least_as_acceptable(
                attackers[right],
                attackers[left],
                result,
                strict=True,
            ) and not result.strictly_prefers(left, right):
                return False
    return True


def cardinality_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check the fewer-unattacked-attackers postulate where applicable.

    Amgoud and Ben-Naim 2013 p. 8 and Bonzon et al. 2016 p. 1: when direct
    attackers are all unattacked, fewer attackers strictly improves rank.
    """

    attackers = _attackers(framework)
    unattacked = {argument for argument, values in attackers.items() if not values}
    for left in framework.arguments:
        left_attackers = attackers[left]
        if not left_attackers or not left_attackers <= unattacked:
            continue
        for right in framework.arguments:
            right_attackers = attackers[right]
            if (
                len(left_attackers) < len(right_attackers)
                and right_attackers
                and right_attackers <= unattacked
                and not result.strictly_prefers(left, right)
            ):
                return False
    return True


def quality_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check Bonzon et al. 2016 p. 1 quality precedence for singleton attacks."""

    attackers = _attackers(framework)
    for left in framework.arguments:
        if len(attackers[left]) != 1:
            continue
        left_attacker = next(iter(attackers[left]))
        for right in framework.arguments:
            if len(attackers[right]) != 1:
                continue
            right_attacker = next(iter(attackers[right]))
            if (
                result.strictly_prefers(right_attacker, left_attacker)
                and not result.strictly_prefers(left, right)
            ):
                return False
    return True


def distributed_defense_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check Amgoud and Ben-Naim 2013 p. 8 distributed defense precedence."""

    for left in framework.arguments:
        left_profile = _defense_profile(framework, left)
        if not left_profile["simple"] or not left_profile["distributed"]:
            continue
        for right in framework.arguments:
            right_profile = _defense_profile(framework, right)
            if (
                right_profile["simple"]
                and not right_profile["distributed"]
                and left_profile["attacker_count"] == right_profile["attacker_count"]
                and left_profile["defender_count"] == right_profile["defender_count"]
                and not result.strictly_prefers(left, right)
            ):
                return False
    return True


def strict_addition_of_defense_branch(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check the strict addition-of-defense-branch pattern.

    Bonzon et al. 2016 p. 5 lists ``+AB`` among ranking properties.  On one
    framework/result pair, the checkable local shape is: with equal direct
    attacker count, an argument whose attackers receive at least one defender is
    strictly above the corresponding no-defense shape.
    """

    attackers = _attackers(framework)
    for left in framework.arguments:
        left_attackers = attackers[left]
        if not left_attackers or not _any_attacker_is_attacked(left_attackers, framework):
            continue
        for right in framework.arguments:
            right_attackers = attackers[right]
            if (
                len(left_attackers) == len(right_attackers)
                and right_attackers
                and not _any_attacker_is_attacked(right_attackers, framework)
                and not result.strictly_prefers(left, right)
            ):
                return False
    return True


def _attack_relation(
    framework: ArgumentationFramework,
) -> frozenset[tuple[str, str]]:
    return framework.attacks if framework.attacks is not None else framework.defeats


def _attackers(framework: ArgumentationFramework) -> dict[str, frozenset[str]]:
    attackers: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in _attack_relation(framework):
        attackers[target].add(attacker)
    return {argument: frozenset(values) for argument, values in attackers.items()}


def _same_pair_order(
    left_result: RankingResult,
    left_a: str,
    left_b: str,
    right_result: RankingResult,
    right_a: str,
    right_b: str,
) -> bool:
    return (
        left_result.strictly_prefers(left_a, left_b)
        == right_result.strictly_prefers(right_a, right_b)
        and left_result.equivalent(left_a, left_b)
        == right_result.equivalent(right_a, right_b)
    )


def _weak_components(framework: ArgumentationFramework) -> list[frozenset[str]]:
    neighbors: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in _attack_relation(framework):
        neighbors[attacker].add(target)
        neighbors[target].add(attacker)

    unseen = set(framework.arguments)
    components: list[frozenset[str]] = []
    while unseen:
        seed = unseen.pop()
        component = {seed}
        stack = [seed]
        while stack:
            current = stack.pop()
            for neighbor in neighbors[current] & unseen:
                unseen.remove(neighbor)
                component.add(neighbor)
                stack.append(neighbor)
        components.append(frozenset(component))
    return components


def _induced_framework(
    framework: ArgumentationFramework,
    arguments: frozenset[str],
) -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=arguments,
        defeats=frozenset(
            (left, right)
            for left, right in framework.defeats
            if left in arguments and right in arguments
        ),
        attacks=(
            None
            if framework.attacks is None
            else frozenset(
                (left, right)
                for left, right in framework.attacks
                if left in arguments and right in arguments
            )
        ),
    )


def _at_least_as_acceptable(left: str, right: str, result: RankingResult) -> bool:
    return result.strictly_prefers(left, right) or result.equivalent(left, right)


def _group_at_least_as_acceptable(
    better_group: frozenset[str],
    worse_group: frozenset[str],
    result: RankingResult,
    *,
    strict: bool,
) -> bool:
    if len(better_group) < len(worse_group):
        return False
    if not worse_group:
        return bool(better_group) if strict else True

    better = tuple(sorted(better_group))
    worse = tuple(sorted(worse_group))
    used: set[str] = set()
    saw_strict = len(better_group) > len(worse_group)

    for weaker in worse:
        match = next(
            (
                candidate
                for candidate in better
                if candidate not in used and _at_least_as_acceptable(candidate, weaker, result)
            ),
            None,
        )
        if match is None:
            return False
        used.add(match)
        saw_strict = saw_strict or result.strictly_prefers(match, weaker)
    return saw_strict if strict else True


def _every_attacker_is_attacked(
    attackers: frozenset[str],
    framework: ArgumentationFramework,
) -> bool:
    relation = _attack_relation(framework)
    return all(any(target == attacker for _, target in relation) for attacker in attackers)


def _any_attacker_is_attacked(
    attackers: frozenset[str],
    framework: ArgumentationFramework,
) -> bool:
    relation = _attack_relation(framework)
    return any(target in attackers for _, target in relation)


def _defense_profile(
    framework: ArgumentationFramework,
    argument: str,
) -> dict[str, bool | int]:
    attackers = _attackers(framework)[argument]
    relation = _attack_relation(framework)
    defender_targets: dict[str, set[str]] = {}
    target_defenders: dict[str, set[str]] = {attacker: set() for attacker in attackers}
    for defender, target in relation:
        if target in attackers:
            defender_targets.setdefault(defender, set()).add(target)
            target_defenders[target].add(defender)

    defenders = set(defender_targets)
    simple = bool(defenders) and all(len(targets) == 1 for targets in defender_targets.values())
    distributed = simple and all(len(values) <= 1 for values in target_defenders.values())
    return {
        "attacker_count": len(attackers),
        "defender_count": len(defenders),
        "simple": simple,
        "distributed": distributed,
    }
