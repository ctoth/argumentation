"""Value-based argumentation frameworks.

Bench-Capon 2003 extends Dung AFs with values and audience-specific value
orders. An attack succeeds for an audience exactly when the attacked argument's
value is not strictly preferred to the attacker's value.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Mapping, Sequence

from argumentation.dung import ArgumentationFramework, preferred_extensions


Audience = tuple[str, ...]


@dataclass(frozen=True)
class ValueBasedArgumentationFramework:
    """A finite value-based argumentation framework.

    Bench-Capon 2003 p. 435, Definition 5.1: ``VAF=(AR, attacks, V, val, P)``.
    If ``audiences`` is omitted, all total value orderings are considered for
    objective and subjective acceptance. ``audience`` is the active ordering
    used by ``successful_attacks``.
    """

    arguments: frozenset[str]
    attacks: frozenset[tuple[str, str]]
    values: frozenset[str]
    valuation: Mapping[str, str]
    audience: Audience | None = None
    audiences: tuple[Audience, ...] | None = None

    def __post_init__(self) -> None:
        arguments = frozenset(self.arguments)
        values = frozenset(self.values)
        attacks = frozenset((attacker, target) for attacker, target in self.attacks)
        valuation = dict(self.valuation)

        if not values:
            raise ValueError("values must be non-empty")

        unknown_attack_arguments = sorted(
            (attacker, target)
            for attacker, target in attacks
            if attacker not in arguments or target not in arguments
        )
        if unknown_attack_arguments:
            raise ValueError(
                "attacks must only contain framework arguments: "
                f"{unknown_attack_arguments!r}"
            )

        missing_valuations = sorted(arguments - valuation.keys())
        extra_valuations = sorted(set(valuation) - arguments)
        if missing_valuations or extra_valuations:
            raise ValueError(
                "valuation must map exactly the framework arguments: "
                f"missing={missing_valuations!r}, extra={extra_valuations!r}"
            )

        unknown_values = sorted(value for value in valuation.values() if value not in values)
        if unknown_values:
            raise ValueError(f"valuation uses unknown values: {unknown_values!r}")

        normalized_audiences = (
            tuple(self._validate_audience(audience) for audience in self.audiences)
            if self.audiences is not None
            else None
        )
        active_audience = self._validate_audience(self.audience) if self.audience else None

        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "attacks", attacks)
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "valuation", valuation)
        object.__setattr__(self, "audience", active_audience)
        object.__setattr__(self, "audiences", normalized_audiences)

    def with_audience(self, audience: Sequence[str]) -> ValueBasedArgumentationFramework:
        """Return the same VAF with a different active audience ordering."""

        return ValueBasedArgumentationFramework(
            arguments=self.arguments,
            attacks=self.attacks,
            values=self.values,
            valuation=self.valuation,
            audience=tuple(audience),
            audiences=self.audiences,
        )

    def value_preferred(self, left: str, right: str, audience: Sequence[str] | None = None) -> bool:
        """Return whether ``left`` is strictly preferred to ``right``."""

        ordering = self._active_or_supplied_audience(audience)
        ranking = {value: index for index, value in enumerate(ordering)}
        return ranking[left] < ranking[right]

    def successful_attacks(
        self,
        audience: Sequence[str] | None = None,
    ) -> frozenset[tuple[str, str]]:
        """Return attacks that defeat under Bench-Capon's audience condition.

        Bench-Capon 2003 p. 436, Definition 5.3: ``A`` defeats ``B`` iff
        ``A`` attacks ``B`` and ``val(B)`` is not preferred to ``val(A)``.
        """

        ordering = self._active_or_supplied_audience(audience)
        ranking = {value: index for index, value in enumerate(ordering)}
        defeats: set[tuple[str, str]] = set()
        for attacker, target in self.attacks:
            attacker_value = self.valuation[attacker]
            target_value = self.valuation[target]
            if ranking[target_value] >= ranking[attacker_value]:
                defeats.add((attacker, target))
        return frozenset(defeats)

    def induced_framework(self, audience: Sequence[str] | None = None) -> ArgumentationFramework:
        """Return the Dung AF induced by removing failing attacks."""

        defeats = self.successful_attacks(audience)
        return ArgumentationFramework(
            arguments=self.arguments,
            defeats=defeats,
        )

    def preferred_extensions_for_audience(
        self,
        audience: Sequence[str],
    ) -> list[frozenset[str]]:
        """Return preferred extensions for the audience-specific VAF."""

        return preferred_extensions(self.induced_framework(audience))

    def possible_audiences(self) -> tuple[Audience, ...]:
        """Return explicit audiences or all total orders over the value set."""

        if self.audiences is not None:
            return self.audiences
        return tuple(tuple(ordering) for ordering in permutations(sorted(self.values)))

    def objectively_acceptable(self) -> frozenset[str]:
        """Arguments in every preferred extension for every audience.

        Bench-Capon 2003 p. 437, Definition 6.1.
        """

        objective = set(self.arguments)
        for audience in self.possible_audiences():
            extensions = self.preferred_extensions_for_audience(audience)
            if not extensions:
                objective.clear()
                break
            accepted_by_audience = set.intersection(*(set(extension) for extension in extensions))
            objective &= accepted_by_audience
        return frozenset(objective)

    def subjectively_acceptable(self) -> frozenset[str]:
        """Arguments in at least one preferred extension for some audience.

        Bench-Capon 2003 p. 437, Definition 6.2.
        """

        subjective: set[str] = set()
        for audience in self.possible_audiences():
            for extension in self.preferred_extensions_for_audience(audience):
                subjective.update(extension)
        return frozenset(subjective)

    def indefensible(self) -> frozenset[str]:
        """Return arguments that are not subjectively acceptable."""

        return self.arguments - self.subjectively_acceptable()

    def _active_or_supplied_audience(self, audience: Sequence[str] | None) -> Audience:
        if audience is not None:
            return self._validate_audience(audience)
        if self.audience is None:
            raise ValueError("an audience is required for audience-specific defeat")
        return self.audience

    def _validate_audience(self, audience: Sequence[str]) -> Audience:
        ordering = tuple(audience)
        if frozenset(ordering) != self.values or len(ordering) != len(self.values):
            raise ValueError("audience must be a total ordering of the VAF values")
        return ordering
