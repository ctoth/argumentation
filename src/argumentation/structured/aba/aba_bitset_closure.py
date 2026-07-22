"""Bitset Horn-closure helper shared by the ABA SAT solver engines."""

from __future__ import annotations

from collections import defaultdict

from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aspic.aspic import Literal


class _BitsetHornClosure:
    def __init__(
        self,
        literal_bits: dict[Literal, int],
        assumption_bits: dict[Literal, int],
        waiting: dict[int, tuple[int, ...]],
        remaining_counts: tuple[int, ...],
        consequents: tuple[int, ...],
        zero_consequents: tuple[int, ...],
        telemetry: dict[str, int],
    ) -> None:
        self.literal_bits = literal_bits
        self.assumption_bits = assumption_bits
        self.waiting = waiting
        self.remaining_counts = remaining_counts
        self.consequents = consequents
        self.zero_consequents = zero_consequents
        self.telemetry = telemetry
        self._closure_cache: dict[int, int] = {}

    @classmethod
    def from_framework(
        cls,
        framework: ABAFramework,
        telemetry: dict[str, int],
    ) -> _BitsetHornClosure:
        literals = sorted(
            set(framework.language)
            | set(framework.assumptions)
            | set(framework.contrary.values())
            | {rule.consequent for rule in framework.rules}
            | {
                antecedent
                for rule in framework.rules
                for antecedent in rule.antecedents
            },
            key=repr,
        )
        literal_bits = {literal: 1 << index for index, literal in enumerate(literals)}
        assumption_bits = {
            assumption: literal_bits[assumption]
            for assumption in sorted(framework.assumptions, key=repr)
        }
        waiting_lists: dict[int, list[int]] = defaultdict(list)
        remaining_counts: list[int] = []
        consequents: list[int] = []
        zero_consequents: list[int] = []
        for rule in sorted(framework.rules, key=repr):
            antecedent_bits = tuple(
                literal_bits[antecedent] for antecedent in frozenset(rule.antecedents)
            )
            consequent = literal_bits[rule.consequent]
            if antecedent_bits:
                rule_index = len(remaining_counts)
                remaining_counts.append(len(antecedent_bits))
                consequents.append(consequent)
                for bit in antecedent_bits:
                    waiting_lists[bit].append(rule_index)
            else:
                zero_consequents.append(consequent)
        waiting = {bit: tuple(indices) for bit, indices in waiting_lists.items()}
        return cls(
            literal_bits,
            assumption_bits,
            waiting,
            tuple(remaining_counts),
            tuple(consequents),
            tuple(zero_consequents),
            telemetry,
        )

    def closure_mask(self, assumptions: AssumptionSet) -> int:
        return self._closure_from_seed(self._assumption_mask(assumptions))

    def contains(self, closure: int, literal: Literal) -> bool:
        return bool(closure & self.literal_bits[literal])

    def shrink_support(
        self,
        support: AssumptionSet,
        conclusion: Literal,
    ) -> AssumptionSet:
        self.telemetry["prefsat_attacker_bitset_shrink_checks"] += 1
        current = self._assumption_mask(support)
        conclusion_bit = self.literal_bits[conclusion]
        for assumption in sorted(support, key=repr):
            reduced = current & ~self.assumption_bits[assumption]
            if self._closure_from_seed(reduced) & conclusion_bit:
                current = reduced
        return frozenset(
            assumption
            for assumption, bit in self.assumption_bits.items()
            if current & bit
        )

    def _assumption_mask(self, assumptions: AssumptionSet) -> int:
        mask = 0
        for assumption in assumptions:
            mask |= self.assumption_bits[assumption]
        return mask

    def _closure_from_seed(self, seed: int) -> int:
        cached = self._closure_cache.get(seed)
        if cached is not None:
            return cached
        self.telemetry["prefsat_attacker_bitset_closure_checks"] += 1
        closure = seed
        remaining = list(self.remaining_counts)
        queue = self._bits(seed)
        for consequent in self.zero_consequents:
            if not closure & consequent:
                closure |= consequent
                queue.append(consequent)
        while queue:
            bit = queue.pop()
            for rule_index in self.waiting.get(bit, ()):
                remaining[rule_index] -= 1
                self.telemetry["prefsat_attacker_bitset_rule_firings"] += 1
                if remaining[rule_index] == 0:
                    consequent = self.consequents[rule_index]
                    if not closure & consequent:
                        closure |= consequent
                        queue.append(consequent)
        self._closure_cache[seed] = closure
        return closure

    def _bits(self, mask: int) -> list[int]:
        bits: list[int] = []
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            bits.append(bit)
            remaining ^= bit
        return bits
