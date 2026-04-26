"""Labelling utilities for Dung-style abstract argumentation frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from argumentation.dung import ArgumentationFramework


class Label(Enum):
    """The three standard argument labelling statuses."""

    IN = "in"
    OUT = "out"
    UNDEC = "undec"


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


__all__ = ["Label", "Labelling"]
