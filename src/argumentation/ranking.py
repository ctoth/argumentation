"""Ranking-based semantics for abstract argumentation frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from argumentation.dung import ArgumentationFramework


@dataclass(frozen=True)
class RankingResult:
    """A ranking-semantics result.

    ``ranking`` is a total preorder represented best-to-worst as tiers.
    ``converged=False`` is data, not an exception.
    """

    scores: dict[str, float]
    ranking: tuple[frozenset[str], ...]
    converged: bool
    iterations: int
    semantics: str

    def rank_index(self, argument: str) -> int:
        for index, tier in enumerate(self.ranking):
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
) -> RankingResult:
    """Compute Besnard-Hunter Categoriser scores.

    Bonzon et al. 2016, Definition 9: unattacked arguments receive 1; otherwise
    an argument receives ``1 / (1 + sum(Cat(attacker)))``.
    """

    _validate_iteration_parameters(tolerance, max_iterations)
    attackers = _attackers(framework)
    scores = {argument: 1.0 for argument in framework.arguments}

    for iteration in range(1, max_iterations + 1):
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
            return _result(
                scores,
                higher_is_better=True,
                tolerance=tolerance,
                converged=True,
                iterations=iteration,
                semantics="categoriser",
            )

    return _result(
        scores,
        higher_is_better=True,
        tolerance=tolerance,
        converged=False,
        iterations=max_iterations,
        semantics="categoriser",
    )


def categoriser_ranking(
    framework: ArgumentationFramework,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> RankingResult:
    return categoriser_scores(
        framework,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )


def burden_numbers(
    framework: ArgumentationFramework,
    *,
    iterations: int,
    tolerance: float = 1e-9,
) -> RankingResult:
    """Compute final Burden numbers.

    Bonzon et al. 2016, Definitions 15-16 use ``Bur_0(a)=1`` and
    ``Bur_i(a)=1+sum(1/Bur_{i-1}(attacker))`` for later steps. Lower burden is
    more acceptable.
    """

    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")

    attackers = _attackers(framework)
    scores = {argument: 1.0 for argument in framework.arguments}

    for _ in range(iterations):
        scores = {
            argument: 1.0 + sum(1.0 / scores[attacker] for attacker in attackers[argument])
            for argument in framework.arguments
        }

    return _result(
        scores,
        higher_is_better=False,
        tolerance=tolerance,
        converged=True,
        iterations=iterations,
        semantics="burden",
    )


def burden_ranking(
    framework: ArgumentationFramework,
    *,
    iterations: int,
    tolerance: float = 1e-9,
) -> RankingResult:
    return burden_numbers(framework, iterations=iterations, tolerance=tolerance)


def discussion_based_ranking(
    framework: ArgumentationFramework,
    *,
    max_depth: int | None = None,
    tolerance: float = 1e-9,
) -> RankingResult:
    """Compute a discussion-count ranking.

    Amgoud and Ben-Naim 2013 count alternating defence/attack discussions.
    Here even-depth defenders increase acceptability and odd-depth attackers
    decrease it, with diminishing depth weight.
    """

    attackers = _attackers(framework)
    depth = max_depth if max_depth is not None else max(len(framework.arguments), 1)
    scores: dict[str, float] = {}
    for argument in framework.arguments:
        total = 1.0
        frontier = {argument}
        for level in range(1, depth + 1):
            next_frontier = {attacker for target in frontier for attacker in attackers[target]}
            if not next_frontier:
                break
            weight = 1.0 / (level + 1)
            total += weight * len(next_frontier) * (1 if level % 2 == 0 else -1)
            frontier = next_frontier
        scores[argument] = total
    return _result(
        scores,
        higher_is_better=True,
        tolerance=tolerance,
        converged=True,
        iterations=depth,
        semantics="discussion_based",
    )


def counting_ranking(
    framework: ArgumentationFramework,
    *,
    damping: float = 0.9,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> RankingResult:
    """Compute damped counting scores."""

    if not 0.0 < damping < 1.0:
        raise ValueError("damping must be between 0 and 1")
    _validate_iteration_parameters(tolerance, max_iterations)
    attackers = _attackers(framework)
    scores = {argument: 1.0 for argument in framework.arguments}
    for iteration in range(1, max_iterations + 1):
        updated = {
            argument: 1.0 / (1.0 + damping * sum(scores[attacker] for attacker in attackers[argument]))
            for argument in framework.arguments
        }
        delta = max(
            (abs(updated[argument] - scores[argument]) for argument in framework.arguments),
            default=0.0,
        )
        scores = updated
        if delta <= tolerance:
            return _result(
                scores,
                higher_is_better=True,
                tolerance=tolerance,
                converged=True,
                iterations=iteration,
                semantics="counting",
            )
    return _result(
        scores,
        higher_is_better=True,
        tolerance=tolerance,
        converged=False,
        iterations=max_iterations,
        semantics="counting",
    )


def tuples_ranking(
    framework: ArgumentationFramework,
    *,
    max_depth: int | None = None,
    tolerance: float = 1e-9,
) -> RankingResult:
    """Compute tuple-style path rankings."""

    attackers = _attackers(framework)
    depth = max_depth if max_depth is not None else max(len(framework.arguments), 1)
    scores: dict[str, float] = {}
    for argument in framework.arguments:
        total = 0.0
        frontier = {argument}
        for level in range(1, depth + 1):
            next_frontier = {attacker for target in frontier for attacker in attackers[target]}
            if not next_frontier:
                break
            sign = -1.0 if level % 2 == 1 else 1.0
            total += sign * len(next_frontier) / (10.0**level)
            frontier = next_frontier
        scores[argument] = total
    return _result(
        scores,
        higher_is_better=True,
        tolerance=tolerance,
        converged=True,
        iterations=depth,
        semantics="tuples",
    )


def h_categoriser_ranking(
    framework: ArgumentationFramework,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> RankingResult:
    """Compute h-Categoriser scores with capped attacker aggregation."""

    _validate_iteration_parameters(tolerance, max_iterations)
    attackers = _attackers(framework)
    scores = {argument: 1.0 for argument in framework.arguments}
    for iteration in range(1, max_iterations + 1):
        updated = {
            argument: 1.0 / (1.0 + min(1.0, sum(scores[attacker] for attacker in attackers[argument])))
            for argument in framework.arguments
        }
        delta = max(
            (abs(updated[argument] - scores[argument]) for argument in framework.arguments),
            default=0.0,
        )
        scores = updated
        if delta <= tolerance:
            return _result(
                scores,
                higher_is_better=True,
                tolerance=tolerance,
                converged=True,
                iterations=iteration,
                semantics="h_categoriser",
            )
    return _result(
        scores,
        higher_is_better=True,
        tolerance=tolerance,
        converged=False,
        iterations=max_iterations,
        semantics="h_categoriser",
    )


def iterated_graded_ranking(
    framework: ArgumentationFramework,
    *,
    max_threshold: int | None = None,
    tolerance: float = 1e-9,
) -> RankingResult:
    """Compute an iterated graded score from defended attacker thresholds."""

    attackers = _attackers(framework)
    threshold = max_threshold if max_threshold is not None else max(len(framework.arguments), 1)
    scores: dict[str, float] = {}
    for argument in framework.arguments:
        attacker_count = len(attackers[argument])
        defender_count = sum(
            1
            for defender, target in _attack_relation(framework)
            if target in attackers[argument] and defender != argument
        )
        score = 0.0
        for grade in range(1, threshold + 1):
            if attacker_count < grade:
                score += 1.0
            if defender_count >= grade:
                score += 0.5
        scores[argument] = score
    return _result(
        scores,
        higher_is_better=True,
        tolerance=tolerance,
        converged=True,
        iterations=threshold,
        semantics="iterated_graded",
    )


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


def _result(
    scores: dict[str, float],
    *,
    higher_is_better: bool,
    tolerance: float,
    converged: bool,
    iterations: int,
    semantics: str,
) -> RankingResult:
    ranking = _ranking_from_scores(
        scores,
        higher_is_better=higher_is_better,
        tolerance=tolerance,
    )
    return RankingResult(
        scores=dict(sorted(scores.items())),
        ranking=ranking,
        converged=converged,
        iterations=iterations,
        semantics=semantics,
    )


def _ranking_from_scores(
    scores: dict[str, float],
    *,
    higher_is_better: bool,
    tolerance: float,
) -> tuple[frozenset[str], ...]:
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

    return tuple(tiers)


def _validate_iteration_parameters(tolerance: float, max_iterations: int) -> None:
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
