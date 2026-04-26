"""Accrual applicability helpers for ASPIC-style arguments."""

from __future__ import annotations

from dataclasses import dataclass

from argumentation.labelling import Label, Labelling


@dataclass(frozen=True)
class AccrualArgument:
    """Argument metadata needed for labelling-relative accrual checks."""

    identifier: str
    conclusion: str
    undercutters: frozenset[str] = frozenset()
    immediate_subarguments: frozenset[str] = frozenset()


@dataclass(frozen=True)
class AccrualEnvelope:
    """Same-conclusion accrual candidates without enumerating every subset."""

    conclusion: str
    strongly_applicable: frozenset[str]
    weakly_applicable: frozenset[str]

    @property
    def minimal_required(self) -> frozenset[str]:
        return self.strongly_applicable

    @property
    def maximal_available(self) -> frozenset[str]:
        return self.weakly_applicable


def weakly_applicable(argument: AccrualArgument, labelling: Labelling) -> bool:
    """Return whether an argument is weakly applicable in ``labelling``.

    Prakken 2019: weak applicability excludes undercutters labelled in and
    immediate subarguments labelled out.
    """
    _validate_known(argument, labelling)
    return (
        not (argument.undercutters & labelling.in_arguments)
        and not (argument.immediate_subarguments & labelling.out_arguments)
    )


def strongly_applicable(argument: AccrualArgument, labelling: Labelling) -> bool:
    """Return whether an argument is strongly applicable in ``labelling``.

    Strong applicability additionally requires all undercutters to be out and
    all immediate subarguments to be in.
    """
    if not weakly_applicable(argument, labelling):
        return False
    return all(
        labelling.statuses[undercutter] == Label.OUT
        for undercutter in argument.undercutters
    ) and all(
        labelling.statuses[subargument] == Label.IN
        for subargument in argument.immediate_subarguments
    )


def accrual_envelope(
    arguments: frozenset[AccrualArgument],
    *,
    conclusion: str,
    labelling: Labelling,
) -> AccrualEnvelope:
    """Return strong and weak same-conclusion accrual candidates."""
    same_conclusion = frozenset(
        argument for argument in arguments
        if argument.conclusion == conclusion
    )
    strong = frozenset(
        argument.identifier
        for argument in same_conclusion
        if strongly_applicable(argument, labelling)
    )
    weak = frozenset(
        argument.identifier
        for argument in same_conclusion
        if weakly_applicable(argument, labelling)
    )
    return AccrualEnvelope(
        conclusion=conclusion,
        strongly_applicable=strong,
        weakly_applicable=weak,
    )


def accrual_grounded_labelling(
    arguments: frozenset[AccrualArgument],
    *,
    max_iterations: int = 1_000,
) -> Labelling:
    """Compute the least fixed point of the accrual labelling operator.

    Prakken 2019 studies the Dung-style relation between ordinary labellings
    and accrual-aware labellings. This operator keeps the existing package
    applicability definitions explicit: strongly applicable arguments become
    in, arguments that are not weakly applicable become out, and the remainder
    stay undecided until the least fixed point is reached.
    """
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    identifiers = frozenset(argument.identifier for argument in arguments)
    by_identifier = {argument.identifier: argument for argument in arguments}
    labelling = Labelling.from_statuses(
        arguments=identifiers,
        statuses={identifier: Label.UNDEC for identifier in identifiers},
    )

    for _ in range(max_iterations):
        statuses: dict[str, Label] = {}
        for identifier, argument in by_identifier.items():
            if strongly_applicable(argument, labelling):
                statuses[identifier] = Label.IN
            elif not weakly_applicable(argument, labelling):
                statuses[identifier] = Label.OUT
            else:
                statuses[identifier] = Label.UNDEC
        next_labelling = Labelling.from_statuses(
            arguments=identifiers,
            statuses=statuses,
        )
        if next_labelling.statuses == labelling.statuses:
            return next_labelling
        labelling = next_labelling

    raise RuntimeError("accrual labelling did not converge")


def _validate_known(argument: AccrualArgument, labelling: Labelling) -> None:
    required = {argument.identifier} | set(argument.undercutters) | set(argument.immediate_subarguments)
    unknown = sorted(required - labelling.arguments)
    if unknown:
        raise ValueError(f"labelling is missing accrual arguments: {unknown!r}")
