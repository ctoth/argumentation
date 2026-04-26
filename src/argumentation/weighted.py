"""Weighted argument systems with inconsistency budgets."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import inf
from typing import Mapping

from argumentation.dung import ArgumentationFramework, grounded_extension


@dataclass(frozen=True)
class WeightedArgumentationFramework:
    """A Dung AF with positive weights on attacks.

    Dunne et al. 2011, Definitions 4-6: a weighted argument system assigns a
    positive real-valued weight to each attack and uses a non-negative budget to
    bound which attacks may be disregarded.
    """

    arguments: frozenset[str]
    attacks: frozenset[tuple[str, str]]
    weights: Mapping[tuple[str, str], float]

    def __post_init__(self) -> None:
        arguments = frozenset(str(argument) for argument in self.arguments)
        attacks = frozenset((str(source), str(target)) for source, target in self.attacks)

        unknown = sorted(
            (source, target)
            for source, target in attacks
            if source not in arguments or target not in arguments
        )
        if unknown:
            raise ValueError(f"attacks must only reference declared arguments: {unknown!r}")

        normalized_weights = {
            (str(source), str(target)): float(weight)
            for (source, target), weight in self.weights.items()
        }
        if set(normalized_weights) != set(attacks):
            raise ValueError("weights must cover exactly the attack relation")
        non_positive = sorted(
            attack for attack, weight in normalized_weights.items()
            if weight <= 0.0
        )
        if non_positive:
            raise ValueError(f"attack weights must be positive: {non_positive!r}")

        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "attacks", attacks)
        object.__setattr__(self, "weights", normalized_weights)

    def as_dung_framework(
        self,
        *,
        deleted_attacks: frozenset[tuple[str, str]] = frozenset(),
    ) -> ArgumentationFramework:
        return ArgumentationFramework(
            arguments=self.arguments,
            defeats=self.attacks - deleted_attacks,
        )

    def deleted_weight(self, deleted_attacks: frozenset[tuple[str, str]]) -> float:
        unknown = deleted_attacks - self.attacks
        if unknown:
            raise ValueError(f"deleted_attacks contains undeclared attacks: {sorted(unknown)!r}")
        return sum(self.weights[attack] for attack in deleted_attacks)


@dataclass(frozen=True)
class WeightedGroundedExtension:
    """A grounded extension plus the deleted-attack witness that realizes it."""

    extension: frozenset[str]
    deleted_attacks: frozenset[tuple[str, str]]
    deleted_weight: float


def weighted_grounded_extensions(
    framework: WeightedArgumentationFramework,
    *,
    budget: float,
) -> list[WeightedGroundedExtension]:
    """Return beta-grounded extensions with minimum-cost witnesses.

    This is the direct executable definition: enumerate ``R`` such that
    ``wt(R,w) <= beta`` and compute ordinary grounded semantics over
    ``A \\ R``. If several deleted-attack sets realize the same extension, the
    cheapest deterministic witness is retained.
    """
    if budget < 0.0:
        raise ValueError("budget must be non-negative")

    best_by_extension: dict[frozenset[str], WeightedGroundedExtension] = {}
    for deleted_attacks in _attack_subsets(framework.attacks):
        cost = framework.deleted_weight(deleted_attacks)
        if cost > budget:
            continue
        extension = grounded_extension(
            framework.as_dung_framework(deleted_attacks=deleted_attacks)
        )
        candidate = WeightedGroundedExtension(
            extension=extension,
            deleted_attacks=deleted_attacks,
            deleted_weight=cost,
        )
        previous = best_by_extension.get(extension)
        if previous is None or _witness_sort_key(candidate) < _witness_sort_key(previous):
            best_by_extension[extension] = candidate

    return sorted(best_by_extension.values(), key=_witness_sort_key)


def minimum_budget_for_grounded_acceptance(
    framework: WeightedArgumentationFramework,
    argument: str,
) -> float:
    """Return the cheapest budget that makes ``argument`` grounded-accepted."""
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument!r}")

    best = inf
    for deleted_attacks in _attack_subsets(framework.attacks):
        cost = framework.deleted_weight(deleted_attacks)
        if cost >= best:
            continue
        extension = grounded_extension(
            framework.as_dung_framework(deleted_attacks=deleted_attacks)
        )
        if argument in extension:
            best = cost

    return best


def _attack_subsets(
    attacks: frozenset[tuple[str, str]],
) -> list[frozenset[tuple[str, str]]]:
    ordered = sorted(attacks)
    subsets: list[frozenset[tuple[str, str]]] = []
    for size in range(len(ordered) + 1):
        for subset in combinations(ordered, size):
            subsets.append(frozenset(subset))
    return subsets


def _witness_sort_key(
    result: WeightedGroundedExtension,
) -> tuple[float, int, tuple[str, ...], tuple[tuple[str, str], ...]]:
    return (
        result.deleted_weight,
        len(result.extension),
        tuple(sorted(result.extension)),
        tuple(sorted(result.deleted_attacks)),
    )
