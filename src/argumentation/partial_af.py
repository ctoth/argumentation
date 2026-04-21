"""Partial argumentation frameworks and completion-based queries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations, product
from typing import TypeAlias

from argumentation.dung import (
    ArgumentationFramework,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)

AttackPair = tuple[str, str]


class PairState(StrEnum):
    ATTACK = "attack"
    IGNORANCE = "ignorance"
    NON_ATTACK = "non_attack"


def _normalize_pairs(pairs: frozenset[AttackPair] | set[AttackPair]) -> frozenset[AttackPair]:
    normalized: set[AttackPair] = set()
    for attacker, target in pairs:
        normalized.add((attacker, target))
    return frozenset(normalized)


@dataclass(frozen=True)
class PartialArgumentationFramework:
    """Partial AF over ordered pairs with an explicit three-way partition."""

    arguments: frozenset[str]
    attacks: frozenset[AttackPair]
    ignorance: frozenset[AttackPair]
    non_attacks: frozenset[AttackPair]

    def __post_init__(self) -> None:
        arguments = frozenset(self.arguments)
        attacks = _normalize_pairs(self.attacks)
        ignorance = _normalize_pairs(self.ignorance)
        non_attacks = _normalize_pairs(self.non_attacks)
        ordered_pairs = frozenset(product(arguments, arguments))

        overlap = (
            (attacks & ignorance)
            | (attacks & non_attacks)
            | (ignorance & non_attacks)
        )
        if overlap:
            raise ValueError(
                "attacks, ignorance, and non_attacks must be pairwise disjoint"
            )

        union = attacks | ignorance | non_attacks
        if union != ordered_pairs:
            missing = ordered_pairs - union
            extra = union - ordered_pairs
            details: list[str] = []
            if missing:
                details.append(f"missing={sorted(missing)!r}")
            if extra:
                details.append(f"extra={sorted(extra)!r}")
            suffix = f": {', '.join(details)}" if details else ""
            raise ValueError(
                "attacks, ignorance, and non_attacks must partition A x A"
                f"{suffix}"
            )

        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "attacks", attacks)
        object.__setattr__(self, "ignorance", ignorance)
        object.__setattr__(self, "non_attacks", non_attacks)

    @property
    def ordered_pairs(self) -> frozenset[AttackPair]:
        return frozenset(product(self.arguments, self.arguments))

    def state_of(self, pair: AttackPair) -> PairState:
        if pair in self.attacks:
            return PairState.ATTACK
        if pair in self.ignorance:
            return PairState.IGNORANCE
        if pair in self.non_attacks:
            return PairState.NON_ATTACK
        raise ValueError(f"Pair {pair!r} is not in {sorted(self.ordered_pairs)!r}")

    def completions(self) -> list[ArgumentationFramework]:
        return enumerate_completions(self)


@dataclass(frozen=True)
class EnumerationExceeded:
    """Anytime result for exact AF enumerators stopped by a candidate ceiling."""

    partial_count: int
    max_candidates: int
    remainder_provenance: str = "vacuous"


FrameworkLike: TypeAlias = PartialArgumentationFramework | ArgumentationFramework


def enumerate_completions(
    framework: PartialArgumentationFramework,
) -> list[ArgumentationFramework]:
    """Enumerate every Dung AF obtained by resolving ignorance exactly."""

    ignorance_pairs = sorted(framework.ignorance)
    completions: list[ArgumentationFramework] = []
    for size in range(len(ignorance_pairs) + 1):
        for selected in combinations(ignorance_pairs, size):
            defeats = frozenset(framework.attacks | frozenset(selected))
            completions.append(
                ArgumentationFramework(
                    arguments=framework.arguments,
                    defeats=defeats,
                )
            )
    return completions


def _coerce_partial_framework(framework: FrameworkLike) -> PartialArgumentationFramework:
    if isinstance(framework, PartialArgumentationFramework):
        return framework
    if isinstance(framework, ArgumentationFramework):
        arguments = frozenset(framework.arguments)
        attacks = frozenset(framework.defeats)
        ordered_pairs = frozenset(product(arguments, arguments))
        return PartialArgumentationFramework(
            arguments=arguments,
            attacks=attacks,
            ignorance=frozenset(),
            non_attacks=ordered_pairs - attacks,
        )
    raise TypeError(f"Unsupported framework type: {type(framework)!r}")


def merge_framework_edit_distance(
    left: FrameworkLike,
    right: FrameworkLike,
) -> int:
    """Hamming distance over pair labels on a shared argument universe."""

    left_framework = _coerce_partial_framework(left)
    right_framework = _coerce_partial_framework(right)
    if left_framework.arguments != right_framework.arguments:
        raise ValueError("merge_framework_edit_distance requires identical arguments")

    return sum(
        1
        for pair in left_framework.ordered_pairs
        if left_framework.state_of(pair) != right_framework.state_of(pair)
    )


def _extensions_for_completion(
    completion: ArgumentationFramework,
    *,
    semantics: str,
) -> list[frozenset[str]]:
    if semantics == "grounded":
        return [grounded_extension(completion)]
    if semantics == "preferred":
        return [frozenset(extension) for extension in preferred_extensions(completion)]
    if semantics == "stable":
        return [frozenset(extension) for extension in stable_extensions(completion)]
    raise ValueError(f"Unknown semantics: {semantics}")


def skeptically_accepted_arguments(
    framework: PartialArgumentationFramework,
    *,
    semantics: str = "grounded",
) -> frozenset[str]:
    """Arguments accepted in every extension of every completion."""
    extensions = [
        extension
        for completion in enumerate_completions(framework)
        for extension in _extensions_for_completion(completion, semantics=semantics)
    ]
    if not extensions:
        return frozenset()
    skeptical = set(framework.arguments)
    for extension in extensions:
        skeptical.intersection_update(extension)
    return frozenset(skeptical)


def credulously_accepted_arguments(
    framework: PartialArgumentationFramework,
    *,
    semantics: str = "grounded",
) -> frozenset[str]:
    """Arguments accepted in some extension of some completion."""
    credulous: set[str] = set()
    for completion in enumerate_completions(framework):
        for extension in _extensions_for_completion(completion, semantics=semantics):
            credulous.update(extension)
    return frozenset(credulous)


def _attack_relation(framework: ArgumentationFramework) -> frozenset[AttackPair]:
    return framework.attacks if framework.attacks is not None else framework.defeats


def consensual_expand(
    framework: ArgumentationFramework,
    universe: frozenset[str],
) -> PartialArgumentationFramework:
    """Expand an AF to a shared universe using ignorance outside source scope."""
    source_arguments = frozenset(framework.arguments)
    attack_relation = _attack_relation(framework)
    attacks: set[AttackPair] = set()
    ignorance: set[AttackPair] = set()
    non_attacks: set[AttackPair] = set()

    for pair in product(universe, universe):
        attacker, target = pair
        if attacker in source_arguments and target in source_arguments:
            if pair in attack_relation:
                attacks.add(pair)
            else:
                non_attacks.add(pair)
        else:
            ignorance.add(pair)

    return PartialArgumentationFramework(
        arguments=universe,
        attacks=frozenset(attacks),
        ignorance=frozenset(ignorance),
        non_attacks=frozenset(non_attacks),
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


def sum_merge_frameworks(
    profile: dict[str, ArgumentationFramework],
    *,
    max_candidates: int | None = None,
) -> list[ArgumentationFramework] | EnumerationExceeded:
    """Return exact Sum-minimizing AFs over the shared argument universe."""
    universe = _shared_universe(profile)
    expanded = _expanded_profile(profile, universe)
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
) -> list[ArgumentationFramework]:
    """Return exact Leximax-minimizing AFs over the shared argument universe."""
    universe = _shared_universe(profile)
    expanded = _expanded_profile(profile, universe)
    max_winners = max_merge_frameworks(profile)
    if isinstance(max_winners, EnumerationExceeded):
        raise AssertionError("unbounded max merge cannot exceed a ceiling")

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
    "EnumerationExceeded",
    "PairState",
    "PartialArgumentationFramework",
    "enumerate_completions",
    "merge_framework_edit_distance",
    "skeptically_accepted_arguments",
    "credulously_accepted_arguments",
    "consensual_expand",
    "sum_merge_frameworks",
    "max_merge_frameworks",
    "leximax_merge_frameworks",
]
