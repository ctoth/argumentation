"""AF-level revision operators over finite argumentation frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations
from typing import Protocol

from argumentation.dung import ArgumentationFramework, grounded_extension, stable_extensions


class ExtensionConstraint(Protocol):
    """Boolean constraint over extension candidates."""

    def atoms(self) -> frozenset[str]: ...

    def evaluate(self, extension: frozenset[str]) -> bool: ...


class AFChangeKind(StrEnum):
    DECISIVE = "decisive"
    RESTRICTIVE = "restrictive"
    QUESTIONING = "questioning"
    DESTRUCTIVE = "destructive"
    EXPANSIVE = "expansive"
    CONSERVATIVE = "conservative"
    ALTERING = "altering"


class AFKernelSemantics(StrEnum):
    STABLE = "stable"
    ADMISSIBLE = "admissible"
    GROUNDED = "grounded"
    COMPLETE = "complete"


class UnknownArgumentRank(Exception):
    """Raised when an extension revision state lacks a required old rank."""

    def __init__(
        self,
        extension: frozenset[str],
        *,
        candidate: frozenset[str],
        added_arguments: frozenset[str],
    ) -> None:
        self.extension = extension
        self.candidate = candidate
        self.added_arguments = added_arguments
        added = ", ".join(sorted(added_arguments)) or "<none>"
        super().__init__(
            "unknown rank for projected extension "
            f"{sorted(extension)!r} while extending with {added}; "
            f"new candidate was {sorted(candidate)!r}"
        )


@dataclass(frozen=True, slots=True)
class ExtensionRevisionState:
    arguments: frozenset[str]
    extensions: tuple[frozenset[str], ...]
    ranking: dict[frozenset[str], int]

    def __post_init__(self) -> None:
        all_extensions = self.all_extensions(self.arguments)
        normalized = tuple(frozenset(extension) for extension in self.extensions)
        if not set(normalized) <= set(all_extensions):
            raise ValueError("extensions must be subsets of the argument universe")
        if set(self.ranking) != set(all_extensions):
            raise ValueError("ranking must cover every extension candidate")
        extension_set = set(normalized)
        non_extension_floor = min(
            (self.ranking[extension] for extension in extension_set),
            default=0,
        ) + 1
        faithful_ranking = {
            candidate: 0
            if candidate in extension_set
            else max(non_extension_floor, int(rank))
            for candidate, rank in self.ranking.items()
        }
        min_rank = min(faithful_ranking.values(), default=0)
        object.__setattr__(self, "extensions", normalized)
        object.__setattr__(
            self,
            "ranking",
            {
                frozenset(extension): int(rank) - min_rank
                for extension, rank in faithful_ranking.items()
            },
        )

    @classmethod
    def from_extensions(
        cls,
        arguments: frozenset[str],
        extensions: tuple[frozenset[str], ...],
        *,
        ranking: dict[frozenset[str], int] | None = None,
    ) -> ExtensionRevisionState:
        candidates = cls.all_extensions(arguments)
        if ranking is None:
            ranking = {
                candidate: 0 if candidate in set(extensions) else 1
                for candidate in candidates
            }
        return cls(arguments=arguments, extensions=extensions, ranking=ranking)

    @staticmethod
    def all_extensions(arguments: frozenset[str]) -> tuple[frozenset[str], ...]:
        ordered = tuple(sorted(arguments))
        result: list[frozenset[str]] = []
        for size in range(len(ordered) + 1):
            for subset in combinations(ordered, size):
                result.append(frozenset(subset))
        return tuple(result)

    def minimal_extensions(
        self,
        candidates: tuple[frozenset[str], ...],
    ) -> tuple[frozenset[str], ...]:
        if not candidates:
            return ()
        best = min(self.ranking.get(candidate, len(self.ranking) + 1) for candidate in candidates)
        return tuple(sorted(
            (candidate for candidate in candidates if self.ranking.get(candidate, len(self.ranking) + 1) == best),
            key=lambda item: (len(item), tuple(sorted(item))),
        ))

    def with_argument(self, argument: str) -> ExtensionRevisionState:
        if argument in self.arguments:
            return self
        arguments = self.arguments | frozenset((argument,))
        ranking = {
            candidate: self.ranking.get(frozenset(item for item in candidate if item != argument), 0)
            for candidate in self.all_extensions(arguments)
        }
        extensions = tuple(frozenset(set(extension) | {argument}) for extension in self.extensions)
        return ExtensionRevisionState.from_extensions(arguments, extensions, ranking=ranking)


@dataclass(frozen=True, slots=True)
class ExtensionRevisionResult:
    extensions: tuple[frozenset[str], ...]
    state: ExtensionRevisionState


def baumann_2015_kernel_union_expand(
    base: ArgumentationFramework,
    new: ArgumentationFramework,
) -> ArgumentationFramework:
    """Union-expand two AFs through Baumann's stable kernel.

    Baumann 2014, ECAI pp. 63-68, characterizes update/deletion
    equivalence by kernels. For stable semantics, non-self attacks from
    a self-attacking source are kernel-redundant and are removed before
    the expanded AF is exposed.
    """
    arguments = base.arguments | new.arguments
    union = ArgumentationFramework(
        arguments=arguments,
        defeats=frozenset(base.defeats | new.defeats),
        attacks=frozenset((base.attacks or base.defeats) | (new.attacks or new.defeats)),
    )
    return stable_kernel(union)


def stable_kernel(framework: ArgumentationFramework) -> ArgumentationFramework:
    """Return Baumann's stable-semantics kernel for an AF.

    Baumann 2014, ECAI pp. 63-68: for stable semantics, attacks
    ``(a, b)`` with ``a != b`` are redundant when ``(a, a)`` is present.
    The self-attack itself is retained because it records that ``a`` is
    conflicting.
    """
    return baumann_2015_kernel(framework, semantics=AFKernelSemantics.STABLE)


def baumann_2015_kernel(
    framework: ArgumentationFramework,
    *,
    semantics: AFKernelSemantics | str = AFKernelSemantics.STABLE,
) -> ArgumentationFramework:
    """Return Baumann's classical kernel for the selected semantics.

    Baumann 2015, Definition 5.10, gives context-free kernels for
    stable, admissible, grounded, and complete semantics. All variants
    preserve arguments and self-loops while removing the semantics-specific
    non-self attacks that cannot affect the corresponding extensions.
    """
    normalized_semantics = AFKernelSemantics(semantics)
    return ArgumentationFramework(
        arguments=framework.arguments,
        defeats=_baumann_kernel_relation(framework.defeats, normalized_semantics),
        attacks=(
            None
            if framework.attacks is None
            else _baumann_kernel_relation(framework.attacks, normalized_semantics)
        ),
    )


def _baumann_kernel_relation(
    relation: frozenset[tuple[str, str]],
    semantics: AFKernelSemantics,
) -> frozenset[tuple[str, str]]:
    self_attackers = frozenset(
        attacker for attacker, target in relation if attacker == target
    )
    return frozenset(
        (attacker, target)
        for attacker, target in relation
        if not _is_baumann_kernel_redundant(
            attacker,
            target,
            relation,
            self_attackers,
            semantics,
        )
    )


def _is_baumann_kernel_redundant(
    attacker: str,
    target: str,
    relation: frozenset[tuple[str, str]],
    self_attackers: frozenset[str],
    semantics: AFKernelSemantics,
) -> bool:
    if attacker == target:
        return False
    if semantics is AFKernelSemantics.STABLE:
        return attacker in self_attackers
    if semantics is AFKernelSemantics.ADMISSIBLE:
        return attacker in self_attackers and (
            (target, attacker) in relation or target in self_attackers
        )
    if semantics is AFKernelSemantics.GROUNDED:
        return target in self_attackers and (
            attacker in self_attackers or (target, attacker) in relation
        )
    if semantics is AFKernelSemantics.COMPLETE:
        return attacker in self_attackers and target in self_attackers
    raise AssertionError(f"Unhandled Baumann kernel semantics: {semantics}")


def diller_2015_revise_by_formula(
    state: ExtensionRevisionState,
    formula: ExtensionConstraint,
) -> ExtensionRevisionResult:
    arguments = state.arguments | formula.atoms()
    working = state if arguments == state.arguments else _extend_state(state, arguments)
    satisfying = tuple(
        extension
        for extension in working.all_extensions(arguments)
        if formula.evaluate(extension)
    )
    revised = working.minimal_extensions(satisfying)
    return ExtensionRevisionResult(
        extensions=revised,
        state=ExtensionRevisionState.from_extensions(arguments, revised, ranking=working.ranking),
    )


def diller_2015_revise_by_framework(
    state: ExtensionRevisionState,
    framework: ArgumentationFramework,
    *,
    semantics: str = "stable",
) -> ExtensionRevisionResult:
    if semantics != "stable":
        raise ValueError("Only stable extension revision is implemented")
    target = tuple(stable_extensions(framework)) or (frozenset(),)
    arguments = state.arguments | framework.arguments
    working = state if arguments == state.arguments else _extend_state(state, arguments)
    lifted_target = tuple(frozenset(extension) for extension in target)
    overlap = tuple(extension for extension in working.extensions if extension in set(lifted_target))
    revised = overlap or working.minimal_extensions(lifted_target)
    return ExtensionRevisionResult(
        extensions=revised,
        state=ExtensionRevisionState.from_extensions(arguments, revised, ranking=working.ranking),
    )


def cayrol_2014_classify_grounded_argument_addition(
    framework: ArgumentationFramework,
    argument: str,
    attacks: frozenset[tuple[str, str]],
) -> AFChangeKind:
    before = (grounded_extension(framework),)
    changed = ArgumentationFramework(
        arguments=framework.arguments | frozenset((argument,)),
        defeats=framework.defeats | attacks,
        attacks=frozenset((framework.attacks or framework.defeats) | attacks),
    )
    after = (grounded_extension(changed),)
    return _classify_extension_change(before, after)


def _classify_extension_change(
    before: tuple[frozenset[str], ...],
    after: tuple[frozenset[str], ...],
) -> AFChangeKind:
    """Classify structural extension change after an AF update.

    Cayrol, de Saint-Cyr, and Lagasquie-Schiex 2010, JAIR 38, Table 3
    distinguish seven extension-family changes: conservative, decisive,
    destructive, expansive, restrictive, questioning, and altering.
    """
    if before == after:
        return AFChangeKind.CONSERVATIVE
    if not after or after == (frozenset(),):
        return AFChangeKind.DESTRUCTIVE
    if len(after) == 1 and (not before or before == (frozenset(),) or len(before) > 2):
        return AFChangeKind.DECISIVE
    if len(before) > len(after) >= 2:
        # Cayrol et al.'s restrictive case is a strict cardinality shrink
        # that does not collapse to the decisive or destructive cases above.
        return AFChangeKind.RESTRICTIVE
    if len(before) < len(after):
        return AFChangeKind.QUESTIONING
    if len(after) == len(before) and all(any(old < new for new in after) for old in before):
        return AFChangeKind.EXPANSIVE
    return AFChangeKind.ALTERING


def _extend_state(
    state: ExtensionRevisionState,
    arguments: frozenset[str],
) -> ExtensionRevisionState:
    extras = arguments - state.arguments
    ranking: dict[frozenset[str], int] = {}
    for candidate in ExtensionRevisionState.all_extensions(arguments):
        projected = frozenset(item for item in candidate if item not in extras)
        try:
            ranking[candidate] = state.ranking[projected]
        except KeyError:
            raise UnknownArgumentRank(
                projected,
                candidate=candidate,
                added_arguments=extras,
            ) from None
    extensions = tuple(frozenset(extension) for extension in state.extensions)
    return ExtensionRevisionState.from_extensions(arguments, extensions, ranking=ranking)


__all__ = [
    "ExtensionConstraint",
    "AFChangeKind",
    "AFKernelSemantics",
    "ExtensionRevisionState",
    "ExtensionRevisionResult",
    "UnknownArgumentRank",
    "baumann_2015_kernel",
    "baumann_2015_kernel_union_expand",
    "stable_kernel",
    "diller_2015_revise_by_formula",
    "diller_2015_revise_by_framework",
    "cayrol_2014_classify_grounded_argument_addition",
]
