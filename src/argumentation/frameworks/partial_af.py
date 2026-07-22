"""Partial argumentation frameworks and completion-based queries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations, product
from typing import TypeAlias, cast

from argumentation.core.dung import (
    ArgumentationFramework,
    SemanticsName,
    extensions_for,
)

AttackPair = tuple[str, str]


class PairState(StrEnum):
    ATTACK = "attack"
    IGNORANCE = "ignorance"
    NON_ATTACK = "non_attack"


def _normalize_pairs(
    pairs: frozenset[AttackPair] | set[AttackPair],
) -> frozenset[AttackPair]:
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
            (attacks & ignorance) | (attacks & non_attacks) | (ignorance & non_attacks)
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
                f"attacks, ignorance, and non_attacks must partition A x A{suffix}"
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


def _coerce_partial_framework(
    framework: FrameworkLike,
) -> PartialArgumentationFramework:
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


_COMPLETION_SEMANTICS: frozenset[str] = frozenset({"grounded", "preferred", "stable"})


def _extensions_for_completion(
    completion: ArgumentationFramework,
    *,
    semantics: str,
) -> list[frozenset[str]]:
    if semantics not in _COMPLETION_SEMANTICS:
        raise ValueError(f"Unknown semantics: {semantics}")
    return list(extensions_for(completion, cast(SemanticsName, semantics)))


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


__all__ = [
    "EnumerationExceeded",
    "PairState",
    "PartialArgumentationFramework",
    "enumerate_completions",
    "merge_framework_edit_distance",
    "skeptically_accepted_arguments",
    "credulously_accepted_arguments",
    "consensual_expand",
]
