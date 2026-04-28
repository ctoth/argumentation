"""Executable checks for common ranking-semantics postulates."""

from __future__ import annotations

from argumentation.dung import ArgumentationFramework
from argumentation.ranking import RankingResult


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


def void_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check that unattacked arguments outrank attacked arguments."""

    attackers = _attackers(framework)
    unattacked = {argument for argument, values in attackers.items() if not values}
    attacked = set(framework.arguments) - unattacked
    return all(
        result.strictly_prefers(left, right)
        for left in unattacked
        for right in attacked
    )


def cardinality_precedence(
    framework: ArgumentationFramework,
    result: RankingResult,
) -> bool:
    """Check the fewer-unattacked-attackers postulate where applicable."""

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


def _attack_relation(
    framework: ArgumentationFramework,
) -> frozenset[tuple[str, str]]:
    return framework.attacks if framework.attacks is not None else framework.defeats


def _attackers(framework: ArgumentationFramework) -> dict[str, frozenset[str]]:
    attackers: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in _attack_relation(framework):
        attackers[target].add(attacker)
    return {argument: frozenset(values) for argument, values in attackers.items()}
