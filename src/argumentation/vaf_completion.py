"""Bench-Capon 2003 chain, line, and fact-value VAF helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import permutations
from typing import Sequence

from argumentation.vaf import Audience, ValueBasedArgumentationFramework


FACT_VALUE = "fact"


class VAFArgumentStatus(Enum):
    """Bench-Capon 2003 p. 440 status classes from Theorem 6.6."""

    OBJECTIVE = "objective"
    SUBJECTIVE = "subjective"
    INDEFENSIBLE = "indefensible"


@dataclass(frozen=True)
class ArgumentChain:
    """A same-valued argument chain.

    Bench-Capon 2003 p. 438, Definition 6.3, numbers chain positions from 1.
    """

    arguments: tuple[str, ...]
    value: str

    def __post_init__(self) -> None:
        if not self.arguments:
            raise ValueError("chain must contain at least one argument")

    def odd_arguments(self) -> frozenset[str]:
        """Return one-based odd-positioned arguments."""

        return frozenset(argument for index, argument in enumerate(self.arguments, start=1) if index % 2)

    def even_arguments(self) -> frozenset[str]:
        """Return one-based even-positioned arguments."""

        return frozenset(
            argument for index, argument in enumerate(self.arguments, start=1) if index % 2 == 0
        )

    def accepted_arguments(self, *, start_accepted: bool) -> frozenset[str]:
        """Return accepted arguments under the p. 438 parity alternation."""

        return self.odd_arguments() if start_accepted else self.even_arguments()

    def is_odd_length(self) -> bool:
        """Return whether the chain length is odd."""

        return len(self.arguments) % 2 == 1


@dataclass(frozen=True)
class ArgumentLine:
    """A line of argument for a target argument.

    Bench-Capon 2003 p. 439, Definition 6.5, links each later chain's last
    argument to the first argument of the previous chain.
    """

    chains: tuple[ArgumentChain, ...]
    target: str
    terminated_by_repeated_value: bool = False

    def __post_init__(self) -> None:
        if not self.chains:
            raise ValueError("line must contain at least one chain")
        if self.chains[0].arguments[-1] != self.target:
            raise ValueError("target must be the last argument of the first chain")
        values = [chain.value for chain in self.chains]
        if len(values) != len(set(values)):
            raise ValueError("line chains must have distinct values")


def make_argument_chain(
    vaf: ValueBasedArgumentationFramework,
    arguments: Sequence[str],
) -> ArgumentChain:
    """Validate and return a Bench-Capon p. 438 argument chain."""

    chain_arguments = tuple(arguments)
    if not chain_arguments:
        raise ValueError("chain must contain at least one argument")
    unknown = [argument for argument in chain_arguments if argument not in vaf.arguments]
    if unknown:
        raise ValueError(f"chain contains unknown arguments: {unknown!r}")

    values = {vaf.valuation[argument] for argument in chain_arguments}
    if len(values) != 1:
        raise ValueError("chain arguments must all have the same value")
    value = values.pop()

    chain_set = set(chain_arguments)
    first_attackers = _attackers_of(vaf, chain_arguments[0]) & chain_set
    if first_attackers:
        raise ValueError("first chain argument must have no attacker in the chain")

    for previous, current in zip(chain_arguments, chain_arguments[1:]):
        chain_attackers = _attackers_of(vaf, current) & chain_set
        if chain_attackers != {previous}:
            raise ValueError(
                "each later chain argument must be attacked only by its predecessor"
            )

    return ArgumentChain(arguments=chain_arguments, value=value)


def build_lines_of_argument(
    vaf: ValueBasedArgumentationFramework,
    target: str,
) -> tuple[ArgumentLine, ...]:
    """Build deterministic p. 439 lines of argument for ``target``."""

    if target not in vaf.arguments:
        raise ValueError(f"unknown target argument: {target!r}")
    first_chains = _chains_ending_at(vaf, target)
    lines: list[ArgumentLine] = []
    for first_chain in first_chains:
        _extend_line(vaf, first_chain, (first_chain,), frozenset({first_chain.value}), lines)
    return tuple(lines)


def classify_line_of_argument(
    vaf: ValueBasedArgumentationFramework,
    line: ArgumentLine,
) -> VAFArgumentStatus:
    """Classify a p. 439 line under Theorem 6.6's p. 440 preconditions."""

    _validate_theorem_6_6_preconditions(vaf)
    _validate_line_links(vaf, line)

    first_chain = line.chains[0]
    target_position = first_chain.arguments.index(line.target) + 1
    has_later_odd_chain = any(chain.is_odd_length() for chain in line.chains[1:])

    if has_later_odd_chain:
        return VAFArgumentStatus.SUBJECTIVE
    if target_position % 2 == 1:
        return VAFArgumentStatus.OBJECTIVE
    return VAFArgumentStatus.INDEFENSIBLE


def two_value_cycle_extension(
    vaf: ValueBasedArgumentationFramework,
    chains: Sequence[ArgumentChain],
    audience: Sequence[str],
) -> frozenset[str]:
    """Return the Corollary 6.7 preferred extension for a two-value cycle."""

    cycle_chains = tuple(chains)
    if len(cycle_chains) < 2:
        raise ValueError("two-value cycle must contain at least two chains")
    values = {chain.value for chain in cycle_chains}
    if len(values) != 2:
        raise ValueError("cycle must contain exactly two values")
    ordering = vaf._validate_audience(audience)
    _validate_cycle_links(vaf, cycle_chains)

    preferred_value = ordering[0]
    if preferred_value not in values:
        raise ValueError("audience preferred value must be one of the cycle values")

    accepted: set[str] = set()
    for index, chain in enumerate(cycle_chains):
        previous_chain = cycle_chains[index - 1]
        if previous_chain.is_odd_length() is False:
            accepted.update(chain.odd_arguments())
        elif chain.value == preferred_value:
            accepted.update(chain.odd_arguments())
        else:
            accepted.update(chain.even_arguments())
    return frozenset(accepted)


def fact_first_audiences(
    values: frozenset[str],
    *,
    fact_value: str = FACT_VALUE,
) -> tuple[Audience, ...]:
    """Return all reasonable p. 444 audiences with fact ranked highest."""

    if fact_value not in values:
        raise ValueError("fact value must be present in values")
    ordinary_values = sorted(values - {fact_value})
    return tuple((fact_value, *ordering) for ordering in permutations(ordinary_values))


def is_skeptically_objective_under_fact_uncertainty(
    vaf: ValueBasedArgumentationFramework,
    argument: str,
    *,
    fact_value: str = FACT_VALUE,
) -> bool:
    """Return p. 447 skeptical objective status under fact-first audiences."""

    if argument not in vaf.arguments:
        raise ValueError(f"unknown argument: {argument!r}")

    audiences = (
        tuple(audience for audience in vaf.audiences if audience[0] == fact_value)
        if vaf.audiences is not None
        else fact_first_audiences(vaf.values, fact_value=fact_value)
    )
    if not audiences:
        raise ValueError("no fact-first audiences are available")

    for audience in audiences:
        for extension in vaf.preferred_extensions_for_audience(audience):
            if argument not in extension:
                return False
    return True


def _attackers_of(vaf: ValueBasedArgumentationFramework, target: str) -> set[str]:
    return {attacker for attacker, attacked in vaf.attacks if attacked == target}


def _chains_ending_at(
    vaf: ValueBasedArgumentationFramework,
    target: str,
) -> tuple[ArgumentChain, ...]:
    value = vaf.valuation[target]
    chains: list[ArgumentChain] = []

    def walk(current: str, suffix: tuple[str, ...]) -> None:
        same_value_attackers = sorted(
            attacker
            for attacker in _attackers_of(vaf, current)
            if vaf.valuation[attacker] == value and attacker not in suffix
        )
        if not same_value_attackers:
            chains.append(make_argument_chain(vaf, suffix))
            return
        for attacker in same_value_attackers:
            walk(attacker, (attacker, *suffix))

    walk(target, (target,))
    return tuple(chains)


def _extend_line(
    vaf: ValueBasedArgumentationFramework,
    current_chain: ArgumentChain,
    line_chains: tuple[ArgumentChain, ...],
    seen_values: frozenset[str],
    lines: list[ArgumentLine],
) -> None:
    cross_attackers = sorted(
        attacker
        for attacker in _attackers_of(vaf, current_chain.arguments[0])
        if vaf.valuation[attacker] != current_chain.value
    )
    if not cross_attackers:
        lines.append(ArgumentLine(chains=line_chains, target=line_chains[0].arguments[-1]))
        return

    extended = False
    terminated_by_repeat = False
    for attacker in cross_attackers:
        attacker_value = vaf.valuation[attacker]
        if attacker_value in seen_values:
            terminated_by_repeat = True
            continue
        for next_chain in _chains_ending_at(vaf, attacker):
            if next_chain.arguments[-1] != attacker:
                raise AssertionError("internal chain builder returned the wrong target")
            extended = True
            _extend_line(
                vaf,
                next_chain,
                (*line_chains, next_chain),
                seen_values | {next_chain.value},
                lines,
            )

    if not extended:
        lines.append(
            ArgumentLine(
                chains=line_chains,
                target=line_chains[0].arguments[-1],
                terminated_by_repeated_value=terminated_by_repeat,
            )
        )


def _validate_line_links(vaf: ValueBasedArgumentationFramework, line: ArgumentLine) -> None:
    for previous, current in zip(line.chains, line.chains[1:]):
        link = (current.arguments[-1], previous.arguments[0])
        if link not in vaf.attacks:
            raise ValueError("each later chain must attack the previous chain start")


def _validate_cycle_links(
    vaf: ValueBasedArgumentationFramework,
    chains: tuple[ArgumentChain, ...],
) -> None:
    for index, chain in enumerate(chains):
        previous = chains[index - 1]
        link = (previous.arguments[-1], chain.arguments[0])
        if link not in vaf.attacks:
            raise ValueError("chains must form a closed two-value cycle")


def _validate_theorem_6_6_preconditions(vaf: ValueBasedArgumentationFramework) -> None:
    for argument in sorted(vaf.arguments):
        attackers = _attackers_of(vaf, argument)
        if len(attackers) > 1:
            raise ValueError("Theorem 6.6 requires at most one attacker per argument")
    if _has_single_valued_cycle(vaf):
        raise ValueError("Theorem 6.6 requires no single-valued cycles")


def _has_single_valued_cycle(vaf: ValueBasedArgumentationFramework) -> bool:
    for start in vaf.arguments:
        value = vaf.valuation[start]
        stack: list[tuple[str, tuple[str, ...]]] = [(start, (start,))]
        while stack:
            current, path = stack.pop()
            for attacker, target in vaf.attacks:
                if attacker != current or vaf.valuation[target] != value:
                    continue
                if target == start:
                    return True
                if target not in path:
                    stack.append((target, (*path, target)))
    return False
