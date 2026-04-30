"""Minimal-change enforcement for abstract argumentation frameworks.

The module provides a brute-force reference oracle for small Dung AFs.  It is
intended as the executable specification for later SAT/MaxSAT-backed
enforcement: enumerate bounded add/remove edits, apply each edit, and keep the
least-cost witness that makes the requested acceptance condition true.

References:
    Baumann, R. (2012). What does it take to enforce an argument?
    Wallner, Niskanen, and Jarvisalo (2017). Complexity results and
    algorithms for extension enforcement in abstract argumentation.
    Baumann, Doutre, Mailly, and Wallner (2021). Enforcement in formal
    argumentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Literal

from argumentation.dung import (
    ArgumentationFramework,
    cf2_extensions,
    complete_extensions,
    grounded_extension,
    ideal_extension,
    preferred_extensions,
    semi_stable_extensions,
    stable_extensions,
    stage_extensions,
)


SemanticsName = Literal[
    "grounded",
    "complete",
    "preferred",
    "stable",
    "semi-stable",
    "stage",
    "ideal",
    "cf2",
]
EnforcementMode = Literal["credulous", "skeptical", "extension"]
ExtensionVariant = Literal["strict", "non-strict"]


@dataclass(frozen=True)
class AFEdit:
    """Hamming edit over arguments and defeats."""

    add_arguments: frozenset[str] = frozenset()
    remove_arguments: frozenset[str] = frozenset()
    add_defeats: frozenset[tuple[str, str]] = frozenset()
    remove_defeats: frozenset[tuple[str, str]] = frozenset()

    @property
    def cost(self) -> int:
        return (
            len(self.add_arguments)
            + len(self.remove_arguments)
            + len(self.add_defeats)
            + len(self.remove_defeats)
        )


@dataclass(frozen=True)
class EnforcementResult:
    """Minimal edit and witness framework for an enforcement query."""

    mode: EnforcementMode
    semantics: SemanticsName
    edit: AFEdit
    witness_framework: ArgumentationFramework
    extensions: tuple[frozenset[str], ...]
    accepted_arguments: frozenset[str]

    @property
    def cost(self) -> int:
        return self.edit.cost


def apply_edit(framework: ArgumentationFramework, edit: AFEdit) -> ArgumentationFramework:
    """Return the AF obtained by applying ``edit`` to ``framework``."""
    arguments = (framework.arguments | edit.add_arguments) - edit.remove_arguments
    defeats = (framework.defeats - edit.remove_defeats) | edit.add_defeats
    defeats = frozenset(
        (attacker, target)
        for attacker, target in defeats
        if attacker in arguments and target in arguments
    )
    attacks = (
        None
        if framework.attacks is None
        else frozenset(
            (attacker, target)
            for attacker, target in framework.attacks
            if attacker in arguments and target in arguments
        )
    )
    return ArgumentationFramework(arguments=arguments, defeats=defeats, attacks=attacks)


def extensions_for(
    framework: ArgumentationFramework,
    semantics: SemanticsName,
) -> tuple[frozenset[str], ...]:
    """Return extensions for the supported Dung semantics."""
    if semantics == "grounded":
        return (grounded_extension(framework),)
    if semantics == "complete":
        return tuple(complete_extensions(framework))
    if semantics == "preferred":
        return tuple(preferred_extensions(framework))
    if semantics == "stable":
        return tuple(stable_extensions(framework))
    if semantics == "semi-stable":
        return tuple(semi_stable_extensions(framework))
    if semantics == "stage":
        return tuple(stage_extensions(framework))
    if semantics == "ideal":
        return (ideal_extension(framework),)
    if semantics == "cf2":
        return tuple(cf2_extensions(framework))
    raise ValueError(f"unsupported semantics: {semantics}")


def _credulously_accepted(extensions: tuple[frozenset[str], ...]) -> frozenset[str]:
    return frozenset().union(*extensions) if extensions else frozenset()


def _skeptically_accepted(extensions: tuple[frozenset[str], ...]) -> frozenset[str]:
    if not extensions:
        return frozenset()
    return frozenset.intersection(*extensions)


def _all_attack_edits(
    framework: ArgumentationFramework,
    *,
    max_cost: int,
) -> list[AFEdit]:
    possible_defeats = frozenset(
        (attacker, target)
        for attacker in framework.arguments
        for target in framework.arguments
    )
    removable = sorted(framework.defeats)
    addable = sorted(possible_defeats - framework.defeats)
    edits: list[AFEdit] = []
    for remove_count in range(max_cost + 1):
        for add_count in range(max_cost - remove_count + 1):
            for remove_defeats in combinations(removable, remove_count):
                for add_defeats in combinations(addable, add_count):
                    edits.append(
                        AFEdit(
                            add_defeats=frozenset(add_defeats),
                            remove_defeats=frozenset(remove_defeats),
                        )
                    )
    return sorted(
        edits,
        key=lambda edit: (
            edit.cost,
            tuple(sorted(edit.remove_defeats)),
            tuple(sorted(edit.add_defeats)),
        ),
    )


def _minimal_result(
    framework: ArgumentationFramework,
    *,
    semantics: SemanticsName,
    max_cost: int,
    mode: EnforcementMode,
    accepts: Callable[[tuple[frozenset[str], ...]], bool],
) -> EnforcementResult:
    for edit in _all_attack_edits(framework, max_cost=max_cost):
        witness = apply_edit(framework, edit)
        extensions = extensions_for(witness, semantics)
        if not accepts(extensions):
            continue
        accepted = (
            _skeptically_accepted(extensions)
            if mode == "skeptical"
            else _credulously_accepted(extensions)
        )
        return EnforcementResult(
            mode=mode,
            semantics=semantics,
            edit=edit,
            witness_framework=witness,
            extensions=extensions,
            accepted_arguments=accepted,
        )
    raise ValueError(
        f"no {mode} {semantics} enforcement found within max_cost={max_cost}"
    )


def enforce_credulous(
    framework: ArgumentationFramework,
    argument: str,
    *,
    semantics: SemanticsName = "preferred",
    max_cost: int = 2,
) -> EnforcementResult:
    """Minimally edit defeats so ``argument`` appears in some extension."""
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument}")
    return _minimal_result(
        framework,
        semantics=semantics,
        max_cost=max_cost,
        mode="credulous",
        accepts=lambda extensions: any(argument in extension for extension in extensions),
    )


def enforce_skeptical(
    framework: ArgumentationFramework,
    argument: str,
    *,
    semantics: SemanticsName = "preferred",
    max_cost: int = 2,
) -> EnforcementResult:
    """Minimally edit defeats so ``argument`` appears in every extension."""
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument}")
    return _minimal_result(
        framework,
        semantics=semantics,
        max_cost=max_cost,
        mode="skeptical",
        accepts=lambda extensions: bool(extensions)
        and all(argument in extension for extension in extensions),
    )


def enforce_extension(
    framework: ArgumentationFramework,
    target: frozenset[str],
    *,
    semantics: SemanticsName = "preferred",
    variant: ExtensionVariant = "strict",
    max_cost: int = 2,
) -> EnforcementResult:
    """Minimally edit defeats so ``target`` is accepted under ``semantics``.

    ``variant="strict"`` requires ``target`` itself to be an extension.
    ``variant="non-strict"`` requires an extension containing ``target``.
    """
    if not target <= framework.arguments:
        raise ValueError(f"target contains unknown arguments: {sorted(target - framework.arguments)!r}")
    if variant not in {"strict", "non-strict"}:
        raise ValueError(f"unsupported enforcement variant: {variant}")
    return _minimal_result(
        framework,
        semantics=semantics,
        max_cost=max_cost,
        mode="extension",
        accepts=(
            lambda extensions: target in extensions
            if variant == "strict"
            else any(target <= extension for extension in extensions)
        ),
    )
