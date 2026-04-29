"""Labelling utilities for Dung-style abstract argumentation frameworks."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from argumentation.dung import (
    ArgumentationFramework,
    admissible,
    attackers_of,
    characteristic_fn,
)


class Label(Enum):
    """The three standard argument labelling statuses."""

    IN = "in"
    OUT = "out"
    UNDEC = "undec"


DEFAULT_COMPLETE_LABELLING_CANDIDATE_BUDGET = 65_536


class ExactEnumerationExceeded(RuntimeError):
    """Raised when exact complete-labelling enumeration exceeds its budget."""


def _normalize_label(value: Label | str) -> Label:
    if isinstance(value, Label):
        return value
    try:
        return Label(value)
    except ValueError as exc:
        raise ValueError(f"Unknown labelling status: {value!r}") from exc


@dataclass(frozen=True)
class Labelling:
    """Immutable three-valued labelling over a finite argument set."""

    statuses: Mapping[str, Label]

    def __post_init__(self) -> None:
        normalized = {
            argument: _normalize_label(status)
            for argument, status in self.statuses.items()
        }
        object.__setattr__(self, "statuses", MappingProxyType(normalized))

    @classmethod
    def from_statuses(
        cls,
        *,
        arguments: frozenset[str],
        statuses: Mapping[str, Label | str],
    ) -> Labelling:
        """Build a labelling whose status map exactly covers ``arguments``."""
        status_arguments = frozenset(statuses)
        if status_arguments != arguments:
            missing = sorted(arguments - status_arguments)
            extra = sorted(status_arguments - arguments)
            raise ValueError(
                "statuses must cover exactly the argument set; "
                f"missing={missing!r}, extra={extra!r}"
            )
        normalized = {
            argument: _normalize_label(status)
            for argument, status in statuses.items()
        }
        return cls(normalized)

    @classmethod
    def from_extension(
        cls,
        framework: ArgumentationFramework,
        extension: frozenset[str],
    ) -> Labelling:
        """Convert an extension into its induced in/out/undec labelling.

        Arguments in the extension are labelled ``in``. Arguments outside the
        extension defeated by an ``in`` argument are labelled ``out``. All other
        outsiders are labelled ``undec``.
        """
        unknown = sorted(extension - framework.arguments)
        if unknown:
            raise ValueError(f"extension contains unknown arguments: {unknown!r}")

        statuses: dict[str, Label] = {}
        for argument in framework.arguments:
            if argument in extension:
                statuses[argument] = Label.IN
            elif any(
                attacker in extension
                for attacker, target in framework.defeats
                if target == argument
            ):
                statuses[argument] = Label.OUT
            else:
                statuses[argument] = Label.UNDEC
        return cls.from_statuses(arguments=framework.arguments, statuses=statuses)

    @property
    def arguments(self) -> frozenset[str]:
        return frozenset(self.statuses)

    @property
    def in_arguments(self) -> frozenset[str]:
        return self._arguments_with_label(Label.IN)

    @property
    def out_arguments(self) -> frozenset[str]:
        return self._arguments_with_label(Label.OUT)

    @property
    def undecided_arguments(self) -> frozenset[str]:
        return self._arguments_with_label(Label.UNDEC)

    @property
    def range(self) -> frozenset[str]:
        return self.in_arguments | self.out_arguments

    @property
    def extension(self) -> frozenset[str]:
        return self.in_arguments

    def _arguments_with_label(self, label: Label) -> frozenset[str]:
        return frozenset(
            argument
            for argument, status in self.statuses.items()
            if status == label
        )


def legally_in(
    labelling: Labelling,
    framework: ArgumentationFramework,
    argument: str,
) -> bool:
    """Return Caminada-legal IN status for one argument.

    Caminada 2006, p. 3: an argument is labelled in iff every defeater is out.
    """
    _require_known_argument(framework, argument)
    return all(
        labelling.statuses[attacker] is Label.OUT
        for attacker in attackers_of(argument, framework.defeats)
    )


def legally_out(
    labelling: Labelling,
    framework: ArgumentationFramework,
    argument: str,
) -> bool:
    """Return Caminada-legal OUT status for one argument.

    Caminada 2006, p. 3: an argument is labelled out iff it has an in defeater.
    """
    _require_known_argument(framework, argument)
    return any(
        labelling.statuses[attacker] is Label.IN
        for attacker in attackers_of(argument, framework.defeats)
    )


def is_reinstatement_labelling(
    labelling: Labelling,
    framework: ArgumentationFramework,
) -> bool:
    """Return whether ``labelling`` satisfies Caminada reinstatement."""
    if labelling.arguments != framework.arguments:
        return False
    for argument, status in labelling.statuses.items():
        if status is Label.IN and not legally_in(labelling, framework, argument):
            return False
        if status is not Label.IN and legally_in(labelling, framework, argument):
            return False
        if status is Label.OUT and not legally_out(labelling, framework, argument):
            return False
        if status is not Label.OUT and legally_out(labelling, framework, argument):
            return False
    return True


def complete_labellings(
    framework: ArgumentationFramework,
    *,
    max_candidates: int | None = DEFAULT_COMPLETE_LABELLING_CANDIDATE_BUDGET,
) -> list[Labelling]:
    """Compute all complete labellings by Caminada 2006 reinstatement."""
    if _is_acyclic(framework):
        return [grounded_labelling(framework)]

    results: list[Labelling] = []
    for candidate_count, extension in enumerate(_all_subsets(framework.arguments), start=1):
        if max_candidates is not None and candidate_count > max_candidates:
            raise ExactEnumerationExceeded(
                "complete labellings exact enumeration exceeded "
                f"{max_candidates} candidate subsets for "
                f"{len(framework.arguments)} arguments"
            )
        if characteristic_fn(
            extension,
            framework.arguments,
            framework.defeats,
        ) != extension:
            continue
        if not admissible(extension, framework.arguments, framework.defeats):
            continue
        labelling = Labelling.from_extension(framework, extension)
        if is_reinstatement_labelling(labelling, framework):
            results.append(labelling)
    return _sort_labellings(results)


def grounded_labelling(framework: ArgumentationFramework) -> Labelling:
    """Return the unique grounded labelling.

    Caminada 2006, p. 5: grounded is the reinstatement labelling with maximal
    undecided set, equivalently minimal in-set.
    """
    current: frozenset[str] = frozenset()
    while True:
        next_current = characteristic_fn(
            current,
            framework.arguments,
            framework.defeats,
        )
        if next_current == current:
            return Labelling.from_extension(framework, current)
        current = next_current


def preferred_labellings(framework: ArgumentationFramework) -> list[Labelling]:
    """Return complete labellings whose IN sets are inclusion-maximal."""
    labellings = complete_labellings(framework)
    return _sort_labellings(
        [
            labelling
            for labelling in labellings
            if not any(
                labelling.in_arguments < other.in_arguments
                for other in labellings
            )
        ]
    )


def stable_labellings(framework: ArgumentationFramework) -> list[Labelling]:
    """Return complete labellings with no undecided arguments."""
    return _sort_labellings(
        [
            labelling
            for labelling in complete_labellings(framework)
            if not labelling.undecided_arguments
        ]
    )


def semi_stable_labellings(framework: ArgumentationFramework) -> list[Labelling]:
    """Return complete labellings with inclusion-minimal undecided sets.

    Caminada 2006, pp. 6-7: semi-stable semantics is minimal undecidedness.
    """
    labellings = complete_labellings(framework)
    return _sort_labellings(
        [
            labelling
            for labelling in labellings
            if not any(
                other.undecided_arguments < labelling.undecided_arguments
                for other in labellings
            )
        ]
    )


def eager_labelling(framework: ArgumentationFramework) -> Labelling:
    """Return the unique eager labelling."""
    from argumentation.dung import eager_extension

    return Labelling.from_extension(framework, eager_extension(framework))


def stage2_labellings(framework: ArgumentationFramework) -> list[Labelling]:
    """Return stage2 extensions projected into labellings."""
    from argumentation.dung import stage2_extensions

    return _sort_labellings(
        [
            Labelling.from_extension(framework, extension)
            for extension in stage2_extensions(framework)
        ]
    )


def _sort_labellings(labellings: list[Labelling]) -> list[Labelling]:
    return sorted(
        labellings,
        key=lambda labelling: (
            len(labelling.in_arguments),
            tuple(sorted(labelling.in_arguments)),
            tuple(sorted(labelling.out_arguments)),
        ),
    )


def _all_subsets(arguments: frozenset[str]) -> Iterator[frozenset[str]]:
    ordered = sorted(arguments)
    for mask in range(1 << len(ordered)):
        yield frozenset(
            ordered[index]
            for index in range(len(ordered))
            if mask & (1 << index)
        )


def _is_acyclic(framework: ArgumentationFramework) -> bool:
    outgoing: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in framework.defeats:
        outgoing.setdefault(attacker, set()).add(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(argument: str) -> bool:
        if argument in visiting:
            return False
        if argument in visited:
            return True
        visiting.add(argument)
        for target in outgoing.get(argument, set()):
            if not visit(target):
                return False
        visiting.remove(argument)
        visited.add(argument)
        return True

    return all(visit(argument) for argument in sorted(framework.arguments))


def _require_known_argument(framework: ArgumentationFramework, argument: str) -> None:
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument!r}")


__all__ = [
    "Label",
    "Labelling",
    "ExactEnumerationExceeded",
    "complete_labellings",
    "eager_labelling",
    "grounded_labelling",
    "is_reinstatement_labelling",
    "legally_in",
    "legally_out",
    "preferred_labellings",
    "semi_stable_labellings",
    "stable_labellings",
    "stage2_labellings",
]
