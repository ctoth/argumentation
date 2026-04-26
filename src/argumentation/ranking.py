"""Ranking-based semantics for abstract argumentation frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from argumentation.dung import ArgumentationFramework


@dataclass(frozen=True)
class ArgumentRanking:
    """A total preorder over arguments, represented as best-to-worst tiers."""

    scores: dict[str, float]
    ordered_tiers: tuple[frozenset[str], ...]
    higher_is_better: bool
    tolerance: float

    def rank_index(self, argument: str) -> int:
        for index, tier in enumerate(self.ordered_tiers):
            if argument in tier:
                return index
        raise KeyError(argument)

    def strictly_prefers(self, left: str, right: str) -> bool:
        return self.rank_index(left) < self.rank_index(right)

    def equivalent(self, left: str, right: str) -> bool:
        return self.rank_index(left) == self.rank_index(right)


def categoriser_scores(
    framework: ArgumentationFramework,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> dict[str, float]:
    """Compute Besnard-Hunter Categoriser scores by fixed-point iteration.

    Bonzon et al. 2016, Definition 9: unattacked arguments receive 1; otherwise
    an argument receives ``1 / (1 + sum(Cat(attacker)))``.
    """
    _validate_iteration_parameters(tolerance, max_iterations)
    attackers = _attackers(framework)
    scores = {argument: 1.0 for argument in framework.arguments}

    for _ in range(max_iterations):
        updated = {
            argument: (
                1.0
                if not attackers[argument]
                else 1.0 / (1.0 + sum(scores[attacker] for attacker in attackers[argument]))
            )
            for argument in framework.arguments
        }
        delta = max(
            (abs(updated[argument] - scores[argument]) for argument in framework.arguments),
            default=0.0,
        )
        scores = updated
        if delta <= tolerance:
            return dict(sorted(scores.items()))

    raise RuntimeError("categoriser_scores did not converge")


def categoriser_ranking(
    framework: ArgumentationFramework,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> ArgumentRanking:
    scores = categoriser_scores(
        framework,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )
    return _ranking_from_scores(scores, higher_is_better=True, tolerance=tolerance)


def burden_numbers(
    framework: ArgumentationFramework,
    *,
    iterations: int,
) -> dict[int, dict[str, float]]:
    """Return Burden numbers for steps ``0..iterations``.

    Bonzon et al. 2016, Definitions 15-16 use ``Bur_0(a)=1`` and
    ``Bur_i(a)=1+sum(1/Bur_{i-1}(attacker))`` for later steps. Lower burden is
    more acceptable.
    """
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    attackers = _attackers(framework)
    burdens: dict[int, dict[str, float]] = {
        0: {argument: 1.0 for argument in framework.arguments}
    }

    for step in range(1, iterations + 1):
        previous = burdens[step - 1]
        burdens[step] = {
            argument: 1.0 + sum(1.0 / previous[attacker] for attacker in attackers[argument])
            for argument in framework.arguments
        }

    return {
        step: dict(sorted(values.items()))
        for step, values in sorted(burdens.items())
    }


def burden_ranking(
    framework: ArgumentationFramework,
    *,
    iterations: int,
    tolerance: float = 1e-9,
) -> ArgumentRanking:
    _validate_iteration_parameters(tolerance, max(iterations, 1))
    scores = burden_numbers(framework, iterations=iterations)[iterations]
    return _ranking_from_scores(scores, higher_is_better=False, tolerance=tolerance)


def _attack_relation(
    framework: ArgumentationFramework,
) -> frozenset[tuple[str, str]]:
    return framework.attacks if framework.attacks is not None else framework.defeats


def _attackers(framework: ArgumentationFramework) -> dict[str, frozenset[str]]:
    attackers: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in _attack_relation(framework):
        attackers[target].add(attacker)
    return {
        argument: frozenset(values)
        for argument, values in attackers.items()
    }


def _ranking_from_scores(
    scores: dict[str, float],
    *,
    higher_is_better: bool,
    tolerance: float,
) -> ArgumentRanking:
    direction: Literal[-1, 1] = -1 if higher_is_better else 1
    ordered = sorted(scores, key=lambda argument: (direction * scores[argument], argument))
    tiers: list[frozenset[str]] = []
    tier_values: list[float] = []

    for argument in ordered:
        value = scores[argument]
        if tier_values and abs(value - tier_values[-1]) <= tolerance:
            tiers[-1] = frozenset(set(tiers[-1]) | {argument})
            continue
        tiers.append(frozenset({argument}))
        tier_values.append(value)

    return ArgumentRanking(
        scores=dict(sorted(scores.items())),
        ordered_tiers=tuple(tiers),
        higher_is_better=higher_is_better,
        tolerance=tolerance,
    )


def _validate_iteration_parameters(tolerance: float, max_iterations: int) -> None:
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
