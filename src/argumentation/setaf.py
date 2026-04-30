"""Argumentation frameworks with collective attacks (SETAFs)."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable


CollectiveAttack = tuple[frozenset[str], str]


@dataclass(frozen=True)
class SETAF:
    """Finite SETAF with attacks from argument sets to single targets."""

    arguments: frozenset[str]
    attacks: frozenset[CollectiveAttack]

    def __post_init__(self) -> None:
        arguments = frozenset(str(argument) for argument in self.arguments)
        attacks = frozenset(
            (frozenset(str(attacker) for attacker in attackers), str(target))
            for attackers, target in self.attacks
        )
        unknown = sorted(
            (tuple(sorted(attackers)), target)
            for attackers, target in attacks
            if not attackers <= arguments or target not in arguments
        )
        if unknown:
            raise ValueError(f"attacks must reference declared arguments: {unknown!r}")
        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "attacks", attacks)


def conflict_free(framework: SETAF, candidate: frozenset[str]) -> bool:
    """Return whether no active collective attack targets ``candidate``."""
    _check_candidate(framework, candidate)
    return not any(
        attackers <= candidate and target in candidate
        for attackers, target in framework.attacks
    )


def attacks_argument(
    framework: SETAF,
    candidate: frozenset[str],
    target: str,
) -> bool:
    """Return whether ``candidate`` activates an attack against ``target``."""
    return any(
        attackers <= candidate and attacked == target
        for attackers, attacked in framework.attacks
    )


def defends(framework: SETAF, candidate: frozenset[str], argument: str) -> bool:
    """Return whether ``candidate`` defends ``argument`` from all attacks."""
    for attackers, target in framework.attacks:
        if target != argument:
            continue
        if not any(attacks_argument(framework, candidate, attacker) for attacker in attackers):
            return False
    return True


def admissible(framework: SETAF, candidate: frozenset[str]) -> bool:
    """Return SETAF admissibility."""
    _check_candidate(framework, candidate)
    return conflict_free(framework, candidate) and all(
        defends(framework, candidate, argument)
        for argument in candidate
    )


def characteristic_fn(framework: SETAF, candidate: frozenset[str]) -> frozenset[str]:
    return frozenset(
        argument
        for argument in framework.arguments
        if defends(framework, candidate, argument)
    )


def grounded_extension(framework: SETAF) -> frozenset[str]:
    current: frozenset[str] = frozenset()
    while True:
        updated = characteristic_fn(framework, current)
        if updated == current:
            return current
        current = updated


def complete_extensions(framework: SETAF) -> tuple[frozenset[str], ...]:
    return _sorted_extensions(
        candidate
        for candidate in _all_subsets(framework.arguments)
        if admissible(framework, candidate)
        and characteristic_fn(framework, candidate) == candidate
    )


def preferred_extensions(framework: SETAF) -> tuple[frozenset[str], ...]:
    admissibles = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if admissible(framework, candidate)
    ]
    return _sorted_extensions(
        candidate
        for candidate in admissibles
        if not any(candidate < other for other in admissibles)
    )


def range_of(framework: SETAF, candidate: frozenset[str]) -> frozenset[str]:
    defeated = frozenset(
        target
        for attackers, target in framework.attacks
        if attackers <= candidate
    )
    return candidate | defeated


def stable_extensions(framework: SETAF) -> tuple[frozenset[str], ...]:
    return _sorted_extensions(
        candidate
        for candidate in _all_subsets(framework.arguments)
        if conflict_free(framework, candidate)
        and range_of(framework, candidate) == framework.arguments
    )


def semi_stable_extensions(framework: SETAF) -> tuple[frozenset[str], ...]:
    return _range_maximal(complete_extensions(framework), framework)


def stage_extensions(framework: SETAF) -> tuple[frozenset[str], ...]:
    conflict_free_sets = [
        candidate
        for candidate in _all_subsets(framework.arguments)
        if conflict_free(framework, candidate)
    ]
    return _range_maximal(conflict_free_sets, framework)


def _range_maximal(
    candidates: tuple[frozenset[str], ...] | list[frozenset[str]],
    framework: SETAF,
) -> tuple[frozenset[str], ...]:
    ranges = {candidate: range_of(framework, candidate) for candidate in candidates}
    return _sorted_extensions(
        candidate
        for candidate in candidates
        if not any(ranges[candidate] < other_range for other_range in ranges.values())
    )


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = sorted(arguments)
    subsets: list[frozenset[str]] = []
    for size in range(len(ordered) + 1):
        for subset in combinations(ordered, size):
            subsets.append(frozenset(subset))
    return subsets


def _sorted_extensions(values: Iterable[frozenset[str]]) -> tuple[frozenset[str], ...]:
    return tuple(
        sorted(
            values,
            key=lambda extension: (len(extension), tuple(sorted(extension))),
        )
    )


def _check_candidate(framework: SETAF, candidate: frozenset[str]) -> None:
    unknown = sorted(candidate - framework.arguments)
    if unknown:
        raise ValueError(f"candidate contains unknown arguments: {unknown!r}")
