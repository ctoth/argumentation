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
from argumentation.solver_results import (
    AcceptanceSuccess,
    ExtensionEnumerationSuccess,
    SingleExtensionSuccess,
    SolverProcessError,
    SolverProtocolError,
    SolverUnavailable,
)


SolverBackendUnavailable = SolverUnavailable
SolverBackendError = SolverProcessError


@dataclass(frozen=True)
class ICCMAAFBackend:
    """Explicit ICCMA 2023 AF subprocess backend for Dung extension queries."""

    binary: str
    timeout_seconds: float = 30.0


ExtensionSolverSuccess = ExtensionEnumerationSuccess
SingleExtensionSolverSuccess = SingleExtensionSuccess
AcceptanceSolverSuccess = AcceptanceSuccess


ExtensionSolverResult = (
    ExtensionSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
    | SolverProtocolError
)
SingleExtensionSolverResult = (
    SingleExtensionSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
    | SolverProtocolError
)
AcceptanceSolverResult = (
    AcceptanceSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
    | SolverProtocolError
)


def solve_dung_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str | ICCMAAFBackend = "labelling",
) -> ExtensionSolverResult:
    """Solve Dung extension queries through a package or external backend."""
    if isinstance(backend, ICCMAAFBackend):
        return SolverBackendUnavailable(
            backend=backend.binary,
            install_hint="Use solve_dung_single_extension for ICCMA AF SE tasks.",
            reason="ICCMA AF SE tasks return one extension witness, not enumeration",
        )
    if backend == "labelling":
        return ExtensionSolverSuccess(
            _sorted_extensions(_dung_extensions(framework, semantics))
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='labelling'.",
        reason=f"unknown backend: {backend!r}",
    )


def solve_dung_single_extension(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str | ICCMAAFBackend = "labelling",
) -> SingleExtensionSolverResult:
    """Solve one Dung extension witness query."""
    if isinstance(backend, ICCMAAFBackend):
        return _solve_iccma_dung_single_extension(framework, semantics, backend)
    if backend == "labelling":
        extensions = _sorted_extensions(_dung_extensions(framework, semantics))
        return SingleExtensionSolverSuccess(
            extension=extensions[0] if extensions else None,
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='labelling'.",
        reason=f"unknown backend: {backend!r}",
    )


def solve_dung_acceptance(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    task: str,
    query: str,
    backend: str | ICCMAAFBackend = "labelling",
) -> AcceptanceSolverResult:
    """Solve Dung credulous or skeptical acceptance queries."""
    if query not in framework.arguments:
        raise ValueError(f"query argument is not in framework: {query!r}")
    if isinstance(backend, ICCMAAFBackend):
        return _solve_iccma_dung_acceptance(framework, semantics, task, query, backend)
    if backend == "labelling":
        return _solve_native_dung_acceptance(framework, semantics, task, query)
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='labelling'.",
        reason=f"unknown backend: {backend!r}",
    )


def _solve_native_dung_acceptance(
    framework: ArgumentationFramework,
    semantics: str,
    task: str,
    query: str,
) -> AcceptanceSolverSuccess:
    extensions = _sorted_extensions(_dung_extensions(framework, semantics))
    if task == "credulous":
        witness = next(
            (extension for extension in extensions if query in extension),
            None,
        )
        return AcceptanceSolverSuccess(
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = next(
            (extension for extension in extensions if query not in extension),
            None,
        )
        return AcceptanceSolverSuccess(
            answer=counterexample is None,
            counterexample=counterexample,
        )
    raise ValueError(f"unsupported Dung acceptance task: {task}")


def _solve_iccma_dung_single_extension(
    framework: ArgumentationFramework,
    semantics: str,
    backend: ICCMAAFBackend,
) -> SingleExtensionSolverResult:
    result = iccma_af.solve_af_extensions(
        framework=framework,
        semantics=semantics,
        binary=backend.binary,
        timeout_seconds=backend.timeout_seconds,
    )
    if isinstance(result, iccma_af.ICCMASolverSuccess):
        return SingleExtensionSolverSuccess(
            extension=result.witness if not result.output.no_extension else None,
        )
    if isinstance(result, iccma_af.ICCMASolverUnavailable):
        return result
    if isinstance(result, iccma_af.ICCMASolverError):
        return result
    return result


def _solve_iccma_dung_acceptance(
    framework: ArgumentationFramework,
    semantics: str,
    task: str,
    query: str,
    backend: ICCMAAFBackend,
) -> AcceptanceSolverResult:
    result = iccma_af.solve_af_acceptance(
        framework=framework,
        semantics=semantics,
        task=task,
        query=query,
        binary=backend.binary,
        timeout_seconds=backend.timeout_seconds,
        certificate_required=True,
    )
    if isinstance(result, iccma_af.ICCMASolverSuccess):
        return AcceptanceSolverSuccess(
            answer=result.answer is True,
            witness=result.witness if result.answer is True else None,
            counterexample=result.witness if result.answer is False else None,
        )
    if isinstance(result, iccma_af.ICCMASolverUnavailable):
        return result
    if isinstance(result, iccma_af.ICCMASolverError):
        return result
    return result


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
