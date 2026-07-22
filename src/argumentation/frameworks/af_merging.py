"""Coste-Marquis et al. 2007 exact AF-merging operators.

Given a profile of Dung AFs over (possibly differing) argument scopes, the merge
operators expand every source to the shared universe and return the AFs that
minimise an aggregation of per-pair edit distance: Sum, Max, and the Leximax
refinement of Max. Enumeration is bounded by an optional candidate ceiling.
"""

from __future__ import annotations

from itertools import combinations, product

from argumentation.core.dung import ArgumentationFramework
from argumentation.frameworks.partial_af import (
    AttackPair,
    EnumerationExceeded,
    PartialArgumentationFramework,
    _attack_relation,
    consensual_expand,
    merge_framework_edit_distance,
)


def _candidate_frameworks(
    arguments: frozenset[str],
    *,
    max_candidates: int | None = None,
) -> list[ArgumentationFramework] | EnumerationExceeded:
    ordered_pairs = sorted(product(arguments, arguments))
    candidates: list[ArgumentationFramework] = []
    for size in range(len(ordered_pairs) + 1):
        for selected in combinations(ordered_pairs, size):
            if max_candidates is not None and len(candidates) >= max_candidates:
                return EnumerationExceeded(
                    partial_count=len(candidates),
                    max_candidates=max_candidates,
                )
            attacks = frozenset(selected)
            candidates.append(
                ArgumentationFramework(
                    arguments=arguments,
                    defeats=attacks,
                    attacks=attacks,
                )
            )
    return candidates


def _expanded_profile(
    profile: dict[str, ArgumentationFramework],
    universe: frozenset[str],
) -> dict[str, PartialArgumentationFramework]:
    return {
        source: consensual_expand(framework, universe)
        for source, framework in profile.items()
    }


def _framework_key(framework: ArgumentationFramework) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(_attack_relation(framework)))


def _shared_universe(profile: dict[str, ArgumentationFramework]) -> frozenset[str]:
    if not profile:
        raise ValueError("merge profile must not be empty")
    return frozenset().union(*(framework.arguments for framework in profile.values()))


def _strict_bipartition_sum_merge(
    universe: frozenset[str],
    expanded: dict[str, PartialArgumentationFramework],
) -> list[ArgumentationFramework] | None:
    """Return the unique pairwise Sum median for a strict bipartition profile.

    Coste-Marquis et al. 2007 define AF merge distances over attack statuses.
    For complete shared-universe profiles with no ignorance and a strict
    attack/non-attack majority on every ordered pair, the Sum objective
    decomposes per pair, so the unique winner is obtained without enumerating
    the 2^(|A|^2) candidate AF space.
    """

    if any(framework.ignorance for framework in expanded.values()):
        return None

    attacks: set[AttackPair] = set()
    for pair in product(universe, universe):
        attack_votes = sum(
            1 for framework in expanded.values() if pair in framework.attacks
        )
        non_attack_votes = sum(
            1 for framework in expanded.values() if pair in framework.non_attacks
        )
        if attack_votes == non_attack_votes:
            return None
        if attack_votes > non_attack_votes:
            attacks.add(pair)

    attack_relation = frozenset(attacks)
    return [
        ArgumentationFramework(
            arguments=universe,
            defeats=attack_relation,
            attacks=attack_relation,
        )
    ]


def sum_merge_frameworks(
    profile: dict[str, ArgumentationFramework],
    *,
    max_candidates: int | None = None,
) -> list[ArgumentationFramework] | EnumerationExceeded:
    """Return exact Sum-minimizing AFs over the shared argument universe."""
    universe = _shared_universe(profile)
    expanded = _expanded_profile(profile, universe)
    strict_bipartition_winners = _strict_bipartition_sum_merge(universe, expanded)
    if strict_bipartition_winners is not None:
        return strict_bipartition_winners

    candidates = _candidate_frameworks(universe, max_candidates=max_candidates)
    if isinstance(candidates, EnumerationExceeded):
        return candidates

    best_score: int | None = None
    winners: list[ArgumentationFramework] = []
    for candidate in candidates:
        score = sum(
            merge_framework_edit_distance(candidate, source_framework)
            for source_framework in expanded.values()
        )
        if best_score is None or score < best_score:
            best_score = score
            winners = [candidate]
        elif score == best_score:
            winners.append(candidate)
    return sorted(winners, key=_framework_key)


def max_merge_frameworks(
    profile: dict[str, ArgumentationFramework],
    *,
    max_candidates: int | None = None,
) -> list[ArgumentationFramework] | EnumerationExceeded:
    """Return exact Max-minimizing AFs over the shared argument universe."""
    universe = _shared_universe(profile)
    expanded = _expanded_profile(profile, universe)
    candidates = _candidate_frameworks(universe, max_candidates=max_candidates)
    if isinstance(candidates, EnumerationExceeded):
        return candidates

    best_score: int | None = None
    winners: list[ArgumentationFramework] = []
    for candidate in candidates:
        score = max(
            merge_framework_edit_distance(candidate, source_framework)
            for source_framework in expanded.values()
        )
        if best_score is None or score < best_score:
            best_score = score
            winners = [candidate]
        elif score == best_score:
            winners.append(candidate)
    return sorted(winners, key=_framework_key)


def leximax_merge_frameworks(
    profile: dict[str, ArgumentationFramework],
    *,
    max_candidates: int | None = None,
) -> list[ArgumentationFramework] | EnumerationExceeded:
    """Return exact Leximax-minimizing AFs over the shared argument universe."""
    universe = _shared_universe(profile)
    expanded = _expanded_profile(profile, universe)
    max_winners = max_merge_frameworks(profile, max_candidates=max_candidates)
    if isinstance(max_winners, EnumerationExceeded):
        return max_winners

    best_vector: tuple[int, ...] | None = None
    winners: list[ArgumentationFramework] = []
    for candidate in max_winners:
        vector = tuple(
            sorted(
                (
                    merge_framework_edit_distance(candidate, source_framework)
                    for source_framework in expanded.values()
                ),
                reverse=True,
            )
        )
        if best_vector is None or vector < best_vector:
            best_vector = vector
            winners = [candidate]
        elif vector == best_vector:
            winners.append(candidate)
    return sorted(winners, key=_framework_key)


__all__ = [
    "leximax_merge_frameworks",
    "max_merge_frameworks",
    "sum_merge_frameworks",
]
