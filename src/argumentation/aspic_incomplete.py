"""ASPIC+ reasoning under incomplete information by exact completion."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from argumentation.aspic import (
    ArgumentationSystem,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    build_arguments,
    conc,
)
from argumentation.aspic_encoding import solve_aspic_grounded


@dataclass(frozen=True)
class PartialASPICTheory:
    """ASPIC+ theory with optional ordinary premises left unknown."""

    system: ArgumentationSystem
    kb: KnowledgeBase
    pref: PreferenceConfig
    unknown_premises: frozenset[Literal]


@dataclass(frozen=True)
class IncompleteASPICResult:
    """Grounded incomplete-information status for one queried literal."""

    query: Literal
    status: str
    accepting_completions: tuple[frozenset[Literal], ...]
    rejecting_completions: tuple[frozenset[Literal], ...]
    completion_count: int


def evaluate_incomplete_grounded(
    theory: PartialASPICTheory,
    query: Literal,
) -> IncompleteASPICResult:
    """Classify a query by exhaustive enumeration of tiny completions.

    The status vocabulary follows the package workstream's implementation
    contract for Odekerken, Diller, and Borg style incomplete-information
    reasoning: stable, relevant, unknown, and unsupported.
    """
    accepting: list[frozenset[Literal]] = []
    rejecting: list[frozenset[Literal]] = []
    has_possible_argument = False
    completions = tuple(_completion_subsets(theory.unknown_premises))

    for completion in completions:
        kb = KnowledgeBase(
            axioms=theory.kb.axioms,
            premises=theory.kb.premises | completion,
        )
        arguments = build_arguments(theory.system, kb)
        if any(conc(argument) == query for argument in arguments):
            has_possible_argument = True
        result = solve_aspic_grounded(theory.system, kb, theory.pref)
        if query in result.accepted_conclusions:
            accepting.append(completion)
        else:
            rejecting.append(completion)

    ordered_accepting = _sort_completions(accepting)
    ordered_rejecting = _sort_completions(rejecting)
    if not has_possible_argument:
        status = "unsupported"
    elif len(ordered_accepting) == len(completions):
        status = "stable"
    elif ordered_accepting:
        status = "relevant"
    else:
        status = "unknown"

    return IncompleteASPICResult(
        query=query,
        status=status,
        accepting_completions=ordered_accepting,
        rejecting_completions=ordered_rejecting,
        completion_count=len(completions),
    )


def _completion_subsets(
    unknown_premises: frozenset[Literal],
) -> tuple[frozenset[Literal], ...]:
    ordered = tuple(sorted(unknown_premises, key=repr))
    completions: list[frozenset[Literal]] = []
    for size in range(len(ordered) + 1):
        for subset in combinations(ordered, size):
            completions.append(frozenset(subset))
    return tuple(completions)


def _sort_completions(
    completions: list[frozenset[Literal]],
) -> tuple[frozenset[Literal], ...]:
    return tuple(sorted(completions, key=lambda completion: tuple(map(repr, sorted(completion, key=repr)))))


__all__ = [
    "IncompleteASPICResult",
    "PartialASPICTheory",
    "evaluate_incomplete_grounded",
]
