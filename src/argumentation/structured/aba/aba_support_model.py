"""Brute-force minimal-support model for flat ABA enumeration.

Leaf module: depends only on the ABA/ASPIC data types, never on ``aba_sat``.
``aba_sat`` re-exports these symbols so existing ``aba_sat.<name>`` paths keep
resolving.
"""

from __future__ import annotations

from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aspic.aspic import Literal


class _SupportState:
    def __init__(
        self,
        framework: ABAFramework,
        assumptions: tuple[Literal, ...],
        supports: dict[Literal, frozenset[int]],
    ) -> None:
        self.framework = framework
        self.assumptions = assumptions
        self.index = {assumption: index for index, assumption in enumerate(assumptions)}
        self.supports = supports
        self.attack_supports = {
            assumption: supports.get(framework.contrary[assumption], frozenset())
            for assumption in assumptions
        }

    @classmethod
    def from_framework(cls, framework: ABAFramework) -> _SupportState:
        assumptions = tuple(sorted(framework.assumptions, key=repr))
        index = {assumption: offset for offset, assumption in enumerate(assumptions)}
        supports = {
            literal: frozenset(
                _support_mask(support, index)
                for support in values
            )
            for literal, values in _minimal_supports(framework).items()
        }
        return cls(framework, assumptions, supports)

    def extension(self, mask: int) -> AssumptionSet:
        return frozenset(
            assumption
            for index, assumption in enumerate(self.assumptions)
            if mask & (1 << index)
        )

    def derives_extension(self, extension: AssumptionSet, literal: Literal) -> bool:
        return self.derives(_support_mask(extension, self.index), literal)

    def derives(self, mask: int, literal: Literal) -> bool:
        return any((support & mask) == support for support in self.supports.get(literal, ()))

    def attacks(self, mask: int, assumption: Literal) -> bool:
        return any(
            (support & mask) == support
            for support in self.attack_supports.get(assumption, ())
        )

    def conflict_free(self, mask: int) -> bool:
        return not any(
            mask & (1 << index) and self.attacks(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )

    def defends(self, mask: int, assumption: Literal) -> bool:
        for attack_support in self.attack_supports.get(assumption, ()):
            if attack_support == 0:
                return False
            if not any(
                attack_support & (1 << index) and self.attacks(mask, target)
                for index, target in enumerate(self.assumptions)
            ):
                return False
        return True

    def admissible(self, mask: int) -> bool:
        return self.conflict_free(mask) and all(
            not (mask & (1 << index)) or self.defends(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )

    def complete(self, mask: int) -> bool:
        return self.admissible(mask) and all(
            bool(mask & (1 << index)) == self.defends(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )

    def stable(self, mask: int) -> bool:
        return self.conflict_free(mask) and all(
            bool(mask & (1 << index)) or self.attacks(mask, assumption)
            for index, assumption in enumerate(self.assumptions)
        )


def _support_mask(
    support: AssumptionSet,
    index: dict[Literal, int],
) -> int:
    mask = 0
    for assumption in support:
        mask |= 1 << index[assumption]
    return mask


def _minimal_supports(framework: ABAFramework) -> dict[Literal, frozenset[AssumptionSet]]:
    supports: dict[Literal, set[AssumptionSet]] = {
        literal: set() for literal in framework.language
    }
    for assumption in framework.assumptions:
        supports[assumption].add(frozenset({assumption}))

    changed = True
    while changed:
        changed = False
        for rule in sorted(framework.rules, key=repr):
            consequent_supports = _combine_supports(
                tuple(supports[antecedent] for antecedent in rule.antecedents)
            )
            for support in consequent_supports:
                if _add_minimal_support(supports[rule.consequent], support):
                    changed = True

    return {
        literal: frozenset(values)
        for literal, values in supports.items()
    }


def _combine_supports(
    support_sets: tuple[set[AssumptionSet], ...],
) -> set[AssumptionSet]:
    if not support_sets:
        return {frozenset()}
    combined: set[AssumptionSet] = {frozenset()}
    for choices in support_sets:
        if not choices:
            return set()
        combined = {
            frozenset(left | right)
            for left in combined
            for right in choices
        }
    return _minimal_set(combined)


def _add_minimal_support(
    supports: set[AssumptionSet],
    candidate: AssumptionSet,
) -> bool:
    if any(existing <= candidate for existing in supports):
        return False
    supersets = {existing for existing in supports if candidate < existing}
    supports.difference_update(supersets)
    supports.add(candidate)
    return True


def _minimal_set(supports: set[AssumptionSet]) -> set[AssumptionSet]:
    minimal: set[AssumptionSet] = set()
    for support in sorted(supports, key=lambda item: (len(item), tuple(sorted(map(repr, item))))):
        _add_minimal_support(minimal, support)
    return minimal
