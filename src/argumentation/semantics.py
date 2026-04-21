"""Generic extension and acceptance dispatch for formal argumentation kernels."""

from __future__ import annotations

from typing import Final

from argumentation.bipolar import (
    BipolarArgumentationFramework,
    c_preferred_extensions,
    d_preferred_extensions,
    s_preferred_extensions,
    stable_extensions as bipolar_stable_extensions,
)
from argumentation.dung import (
    ArgumentationFramework,
    complete_extensions,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)
from argumentation.partial_af import (
    PartialArgumentationFramework,
    enumerate_completions,
)


class SemanticsUndefinedType:
    """Sentinel for acceptance queries with no extension family."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "SemanticsUndefined"


SemanticsUndefined: Final = SemanticsUndefinedType()


def _sorted_extensions(
    values: list[frozenset[str]] | tuple[frozenset[str], ...],
) -> tuple[frozenset[str], ...]:
    return tuple(sorted(
        (frozenset(value) for value in values),
        key=lambda extension: (len(extension), tuple(sorted(extension))),
    ))


def _unique_sorted_extensions(
    values: list[frozenset[str]] | tuple[frozenset[str], ...],
) -> tuple[frozenset[str], ...]:
    return _sorted_extensions(tuple(dict.fromkeys(frozenset(value) for value in values)))


def _dung_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    if semantics == "grounded":
        return (grounded_extension(framework),)
    if semantics == "complete":
        return _sorted_extensions(tuple(complete_extensions(framework)))
    if semantics == "preferred":
        return _sorted_extensions(tuple(preferred_extensions(framework)))
    if semantics == "stable":
        return _sorted_extensions(tuple(stable_extensions(framework)))
    raise ValueError(f"Unknown Dung semantics: {semantics}")


def _bipolar_extensions(
    framework: BipolarArgumentationFramework,
    *,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    if semantics == "d-preferred":
        return _sorted_extensions(tuple(d_preferred_extensions(framework)))
    if semantics == "s-preferred":
        return _sorted_extensions(tuple(s_preferred_extensions(framework)))
    if semantics == "c-preferred":
        return _sorted_extensions(tuple(c_preferred_extensions(framework)))
    if semantics == "bipolar-stable":
        return _sorted_extensions(tuple(bipolar_stable_extensions(framework)))
    raise ValueError(f"Unknown bipolar semantics: {semantics}")


def _partial_extensions(
    framework: PartialArgumentationFramework,
    *,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    if semantics not in {"grounded", "preferred", "stable"}:
        raise ValueError(f"Unknown partial-AF semantics: {semantics}")

    completion_extensions: list[frozenset[str]] = []
    for completion in enumerate_completions(framework):
        completion_extensions.extend(
            _dung_extensions(completion, semantics=semantics)
        )
    return _unique_sorted_extensions(tuple(completion_extensions))


def extensions(
    framework: object,
    *,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    """Return extensions for an argumentation-owned framework dataclass."""
    if isinstance(framework, PartialArgumentationFramework):
        return _partial_extensions(framework, semantics=semantics)
    if isinstance(framework, ArgumentationFramework):
        return _dung_extensions(framework, semantics=semantics)
    if isinstance(framework, BipolarArgumentationFramework):
        return _bipolar_extensions(framework, semantics=semantics)
    raise TypeError(f"Unsupported framework type: {type(framework)!r}")


def accepted_arguments(
    framework: object,
    *,
    semantics: str,
    mode: str = "credulous",
) -> frozenset[str] | SemanticsUndefinedType:
    """Return credulously or skeptically accepted arguments."""
    if mode not in {"credulous", "skeptical"}:
        raise ValueError("mode must be 'credulous' or 'skeptical'")

    extension_sets = extensions(framework, semantics=semantics)
    if not extension_sets:
        return SemanticsUndefined

    if mode == "credulous":
        accepted: set[str] = set()
        for extension in extension_sets:
            accepted.update(extension)
        return frozenset(accepted)

    skeptical = set(extension_sets[0])
    for extension in extension_sets[1:]:
        skeptical.intersection_update(extension)
    return frozenset(skeptical)


__all__ = ["SemanticsUndefined", "accepted_arguments", "extensions"]
