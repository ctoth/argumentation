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
from argumentation.solver_adapters import iccma_af


@dataclass(frozen=True)
class SolverBackendUnavailable:
    backend: str
    install_hint: str
    reason: str


@dataclass(frozen=True)
class SolverBackendError:
    backend: str
    reason: str
    details: dict[str, str]


@dataclass(frozen=True)
class ICCMAAFBackend:
    """Explicit ICCMA 2023 AF subprocess backend for Dung extension queries."""

    binary: str
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class ExtensionSolverSuccess:
    extensions: tuple[frozenset[str], ...]


ExtensionSolverResult = (
    ExtensionSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
)


def solve_dung_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str | ICCMAAFBackend = "labelling",
) -> ExtensionSolverResult:
    """Solve Dung extension queries through a package or external backend."""
    if isinstance(backend, ICCMAAFBackend):
        return _solve_iccma_dung_extensions(framework, semantics, backend)
    if backend == "labelling":
        return ExtensionSolverSuccess(
            _sorted_extensions(_dung_extensions(framework, semantics))
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='labelling'.",
        reason=f"unknown backend: {backend!r}",
    )


def _solve_iccma_dung_extensions(
    framework: ArgumentationFramework,
    semantics: str,
    backend: ICCMAAFBackend,
) -> ExtensionSolverResult:
    result = iccma_af.solve_af_extensions(
        framework=framework,
        semantics=semantics,
        binary=backend.binary,
        timeout_seconds=backend.timeout_seconds,
    )
    if isinstance(result, iccma_af.ICCMASolverSuccess):
        return ExtensionSolverSuccess(_sorted_extensions(list(result.extensions)))
    if isinstance(result, iccma_af.ICCMASolverUnavailable):
        return SolverBackendUnavailable(
            backend=result.backend,
            install_hint=result.install_hint,
            reason=result.reason,
        )
    if isinstance(result, iccma_af.ICCMASolverError):
        return SolverBackendError(
            backend=result.backend,
            reason=f"solver exited with code {result.returncode}",
            details={
                "problem": result.problem,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        )
    return SolverBackendError(
        backend=result.backend,
        reason=result.message,
        details={
            "problem": result.problem,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
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
