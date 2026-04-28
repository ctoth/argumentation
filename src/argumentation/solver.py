"""Small solver-result wrappers for extension queries."""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class SolverBackendUnavailable:
    backend: str
    install_hint: str
    reason: str


@dataclass(frozen=True)
class ExtensionSolverSuccess:
    extensions: tuple[frozenset[str], ...]


ExtensionSolverResult = ExtensionSolverSuccess | SolverBackendUnavailable


def solve_dung_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str = "labelling",
) -> ExtensionSolverResult:
    """Solve Dung extension queries through the package's single Dung path."""
    if backend == "labelling":
        return ExtensionSolverSuccess(
            _sorted_extensions(_dung_extensions(framework, semantics))
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='labelling'.",
        reason=f"unknown backend: {backend!r}",
    )


def _dung_extensions(
    framework: ArgumentationFramework,
    semantics: str,
) -> list[frozenset[str]]:
    if semantics == "grounded":
        return [grounded_extension(framework)]
    if semantics == "complete":
        return complete_extensions(framework)
    if semantics == "preferred":
        return preferred_extensions(framework)
    if semantics == "stable":
        return stable_extensions(framework)
    if semantics == "semi-stable":
        return semi_stable_extensions(framework)
    if semantics == "stage":
        return stage_extensions(framework)
    if semantics == "ideal":
        return [ideal_extension(framework)]
    if semantics == "cf2":
        return cf2_extensions(framework)
    raise ValueError(f"Unknown Dung semantics: {semantics}")


def _sorted_extensions(values: list[frozenset[str]]) -> tuple[frozenset[str], ...]:
    return tuple(
        sorted(
            values,
            key=lambda extension: (len(extension), tuple(sorted(extension))),
        )
    )
