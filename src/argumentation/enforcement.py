"""Unconstrained minimal-change enforcement for abstract AFs.

The module provides a brute-force reference oracle for small Dung AFs.  It is
intended as the executable specification for later SAT/MaxSAT-backed
enforcement: enumerate bounded add/remove edits, apply each edit, and keep the
least-cost witness that makes the requested acceptance condition true.

This is not Baumann-style expansion enforcement: it may add or remove attacks
between existing arguments, and the edit data type can represent argument and
attack deletions.  Those operations are deliberately outside the conservative,
normal, strong, and weak expansion settings used in Baumann's framework.

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
ExpansionKind = Literal["normal", "strong", "weak"]


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


@dataclass(frozen=True)
class Expansion:
    """Baumann-style expansion witness from an original AF to an expanded AF."""

    original: ArgumentationFramework
    expanded: ArgumentationFramework

    @property
    def new_arguments(self) -> frozenset[str]:
        return self.expanded.arguments - self.original.arguments

    @property
    def added_defeats(self) -> frozenset[tuple[str, str]]:
        return self.expanded.defeats - self.original.defeats

    @property
    def cost(self) -> int:
        return len(self.new_arguments) + len(self.added_defeats)


@dataclass(frozen=True)
class ExpansionEnforcementResult:
    """Minimal expansion witness for an enforcement query."""

    mode: EnforcementMode
    semantics: SemanticsName
    kind: ExpansionKind
    expansion: Expansion
    witness_framework: ArgumentationFramework
    extensions: tuple[frozenset[str], ...]
    accepted_arguments: frozenset[str]

    @property
    def cost(self) -> int:
        return self.expansion.cost


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


def build_expansion(
    framework: ArgumentationFramework,
    *,
    new_arguments: frozenset[str] = frozenset(),
    added_defeats: frozenset[tuple[str, str]] = frozenset(),
) -> ArgumentationFramework:
    """Return ``framework`` expanded with fresh arguments and added defeats."""
    overlap = framework.arguments & new_arguments
    if overlap:
        raise ValueError(f"new arguments already exist: {sorted(overlap)!r}")
    arguments = framework.arguments | new_arguments
    unknown = frozenset(
        argument
        for defeat in added_defeats
        for argument in defeat
        if argument not in arguments
    )
    if unknown:
        raise ValueError(f"added defeats mention unknown arguments: {sorted(unknown)!r}")
    defeats = framework.defeats | added_defeats
    attacks = None if framework.attacks is None else framework.attacks | added_defeats
    return ArgumentationFramework(arguments=arguments, defeats=defeats, attacks=attacks)


def is_expansion(
    original: ArgumentationFramework,
    expanded: ArgumentationFramework,
) -> bool:
    """Return whether ``expanded`` preserves all old arguments and defeats."""
    return original.arguments <= expanded.arguments and original.defeats <= expanded.defeats


def is_normal_expansion(
    original: ArgumentationFramework,
    expanded: ArgumentationFramework,
) -> bool:
    """Return whether ``expanded`` is a normal expansion of ``original``.

    Baumann normal expansions preserve the old AF and every added attack has
    at least one endpoint among the freshly added arguments.
    """
    if not is_expansion(original, expanded):
        return False
    new_arguments = expanded.arguments - original.arguments
    return all(
        attacker in new_arguments or target in new_arguments
        for attacker, target in expanded.defeats - original.defeats
    )


def is_strong_expansion(
    original: ArgumentationFramework,
    expanded: ArgumentationFramework,
) -> bool:
    """Return whether ``expanded`` is a strong expansion of ``original``."""
    if not is_normal_expansion(original, expanded):
        return False
    new_arguments = expanded.arguments - original.arguments
    return all(
        not (attacker in original.arguments and target in new_arguments)
        for attacker, target in expanded.defeats - original.defeats
    )


def is_weak_expansion(
    original: ArgumentationFramework,
    expanded: ArgumentationFramework,
) -> bool:
    """Return whether ``expanded`` is a weak expansion of ``original``."""
    if not is_normal_expansion(original, expanded):
        return False
    new_arguments = expanded.arguments - original.arguments
    return all(
        not (attacker in new_arguments and target in original.arguments)
        for attacker, target in expanded.defeats - original.defeats
    )


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


def _expansion_predicate(kind: ExpansionKind) -> Callable[
    [ArgumentationFramework, ArgumentationFramework],
    bool,
]:
    if kind == "normal":
        return is_normal_expansion
    if kind == "strong":
        return is_strong_expansion
    if kind == "weak":
        return is_weak_expansion
    raise ValueError(f"unsupported expansion kind: {kind}")


def _all_expansions(
    framework: ArgumentationFramework,
    *,
    kind: ExpansionKind,
    candidate_new_arguments: frozenset[str],
    max_new_arguments: int,
    max_added_defeats: int,
) -> list[Expansion]:
    if max_new_arguments < 0:
        raise ValueError("max_new_arguments must be non-negative")
    if max_added_defeats < 0:
        raise ValueError("max_added_defeats must be non-negative")
    overlap = framework.arguments & candidate_new_arguments
    if overlap:
        raise ValueError(f"candidate new arguments already exist: {sorted(overlap)!r}")

    predicate = _expansion_predicate(kind)
    expansions: list[Expansion] = []
    new_argument_pool = sorted(candidate_new_arguments)
    for new_count in range(min(max_new_arguments, len(new_argument_pool)) + 1):
        for new_arguments_tuple in combinations(new_argument_pool, new_count):
            new_arguments = frozenset(new_arguments_tuple)
            arguments = framework.arguments | new_arguments
            possible_added_defeats = sorted(
                (attacker, target)
                for attacker in arguments
                for target in arguments
                if (attacker, target) not in framework.defeats
                and (attacker in new_arguments or target in new_arguments)
            )
            for added_count in range(min(max_added_defeats, len(possible_added_defeats)) + 1):
                for added_defeats_tuple in combinations(possible_added_defeats, added_count):
                    expanded = build_expansion(
                        framework,
                        new_arguments=new_arguments,
                        added_defeats=frozenset(added_defeats_tuple),
                    )
                    if predicate(framework, expanded):
                        expansions.append(Expansion(framework, expanded))

    return sorted(
        expansions,
        key=lambda expansion: (
            expansion.cost,
            tuple(sorted(expansion.new_arguments)),
            tuple(sorted(expansion.added_defeats)),
        ),
    )


def _minimal_expansion_result(
    framework: ArgumentationFramework,
    *,
    semantics: SemanticsName,
    kind: ExpansionKind,
    candidate_new_arguments: frozenset[str],
    max_new_arguments: int,
    max_added_defeats: int,
    mode: EnforcementMode,
    accepts: Callable[[tuple[frozenset[str], ...]], bool],
) -> ExpansionEnforcementResult:
    for expansion in _all_expansions(
        framework,
        kind=kind,
        candidate_new_arguments=candidate_new_arguments,
        max_new_arguments=max_new_arguments,
        max_added_defeats=max_added_defeats,
    ):
        extensions = extensions_for(expansion.expanded, semantics)
        if not accepts(extensions):
            continue
        accepted = (
            _skeptically_accepted(extensions)
            if mode == "skeptical"
            else _credulously_accepted(extensions)
        )
        return ExpansionEnforcementResult(
            mode=mode,
            semantics=semantics,
            kind=kind,
            expansion=expansion,
            witness_framework=expansion.expanded,
            extensions=extensions,
            accepted_arguments=accepted,
        )
    raise ValueError(
        f"no {kind} expansion {mode} {semantics} enforcement found "
        f"within max_new_arguments={max_new_arguments}, "
        f"max_added_defeats={max_added_defeats}"
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


def enforce_expansion_credulous(
    framework: ArgumentationFramework,
    argument: str,
    *,
    semantics: SemanticsName = "preferred",
    kind: ExpansionKind = "normal",
    candidate_new_arguments: frozenset[str] = frozenset({"x1", "x2"}),
    max_new_arguments: int = 1,
    max_added_defeats: int = 2,
) -> ExpansionEnforcementResult:
    """Find a minimal Baumann-style expansion credulously enforcing ``argument``."""
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument}")
    return _minimal_expansion_result(
        framework,
        semantics=semantics,
        kind=kind,
        candidate_new_arguments=candidate_new_arguments,
        max_new_arguments=max_new_arguments,
        max_added_defeats=max_added_defeats,
        mode="credulous",
        accepts=lambda extensions: any(argument in extension for extension in extensions),
    )


def enforce_expansion_skeptical(
    framework: ArgumentationFramework,
    argument: str,
    *,
    semantics: SemanticsName = "preferred",
    kind: ExpansionKind = "normal",
    candidate_new_arguments: frozenset[str] = frozenset({"x1", "x2"}),
    max_new_arguments: int = 1,
    max_added_defeats: int = 2,
) -> ExpansionEnforcementResult:
    """Find a minimal Baumann-style expansion skeptically enforcing ``argument``."""
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument}")
    return _minimal_expansion_result(
        framework,
        semantics=semantics,
        kind=kind,
        candidate_new_arguments=candidate_new_arguments,
        max_new_arguments=max_new_arguments,
        max_added_defeats=max_added_defeats,
        mode="skeptical",
        accepts=lambda extensions: bool(extensions)
        and all(argument in extension for extension in extensions),
    )


def enforce_expansion_extension(
    framework: ArgumentationFramework,
    target: frozenset[str],
    *,
    semantics: SemanticsName = "preferred",
    variant: ExtensionVariant = "strict",
    kind: ExpansionKind = "normal",
    candidate_new_arguments: frozenset[str] = frozenset({"x1", "x2"}),
    max_new_arguments: int = 1,
    max_added_defeats: int = 2,
) -> ExpansionEnforcementResult:
    """Find a minimal Baumann-style expansion enforcing an extension target."""
    if not target <= framework.arguments:
        raise ValueError(f"target contains unknown arguments: {sorted(target - framework.arguments)!r}")
    if variant not in {"strict", "non-strict"}:
        raise ValueError(f"unsupported enforcement variant: {variant}")
    return _minimal_expansion_result(
        framework,
        semantics=semantics,
        kind=kind,
        candidate_new_arguments=candidate_new_arguments,
        max_new_arguments=max_new_arguments,
        max_added_defeats=max_added_defeats,
        mode="extension",
        accepts=(
            lambda extensions: target in extensions
            if variant == "strict"
            else any(target <= extension for extension in extensions)
        ),
    )
