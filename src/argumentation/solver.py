"""Small solver-result wrappers for extension queries."""

from __future__ import annotations

from dataclasses import dataclass

from argumentation import aba as aba_semantics
from argumentation import adf as adf_semantics
from argumentation import setaf as setaf_semantics
from argumentation.aba import ABAFramework, ABAInput, ABAPlusFramework
from argumentation.aba_sat import (
    sat_stable_extension as sat_aba_stable_extension,
    support_acceptance as sat_aba_support_acceptance,
    support_extensions as sat_aba_support_extensions,
)
from argumentation.adf import AbstractDialecticalFramework
from argumentation.aspic import Literal
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
from argumentation.sat_encoding import (
    sat_complete_extension,
    sat_extensions,
    sat_preferred_extension,
    sat_semi_stable_extension,
    sat_stable_extension,
    sat_stage_extension,
)
from argumentation.setaf import SETAF
from argumentation.solver_adapters import iccma_aba, iccma_af
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
class ICCMAConfig:
    """ICCMA subprocess configuration for solver backends."""

    binary: str
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class SATConfig:
    """Configuration for package-native or externally supplied SAT solving."""

    require_external: bool = False


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


def solve_adf_models(
    framework: AbstractDialecticalFramework,
    *,
    semantics: str,
    backend: str = "auto",
) -> ExtensionSolverResult:
    """Solve ADF model queries through native semantics or a declared backend."""
    if backend == "auto":
        backend = "native"
    if backend == "native":
        return ExtensionSolverSuccess(_adf_models(framework, semantics))
    return SolverBackendUnavailable(
        backend=backend,
        reason="external ADF solver backend is not source-backed",
        install_hint="Use backend='native' or add a primary-source-backed ADF adapter.",
    )


def solve_setaf_extensions(
    framework: SETAF,
    *,
    semantics: str,
    backend: str = "auto",
) -> ExtensionSolverResult:
    """Solve SETAF extension queries through native semantics or a declared backend."""
    if backend == "auto":
        backend = "native"
    if backend == "native":
        return ExtensionSolverSuccess(_setaf_extensions(framework, semantics))
    return SolverBackendUnavailable(
        backend=backend,
        reason="external SETAF solver backend is not source-backed",
        install_hint="Use backend='native' or add a primary-source-backed SETAF adapter.",
    )


def solve_aba_single_extension(
    framework: ABAInput,
    *,
    semantics: str,
    backend: str = "auto",
    iccma: ICCMAConfig | None = None,
) -> SingleExtensionSolverResult:
    """Solve one flat ABA extension witness query."""
    backend = _auto_aba_backend(backend, semantics)
    if backend == "sat":
        if not isinstance(framework, ABAFramework):
            return _aba_sat_requires_flat_framework()
        if semantics == "stable":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_aba_stable_extension(framework),
                )
            except RuntimeError as exc:
                return _aba_sat_runtime_unavailable(exc)
        if semantics in {"complete", "preferred"}:
            extensions = _sorted_object_extensions(
                sat_aba_support_extensions(framework, semantics)
            )
            return SingleExtensionSolverSuccess(
                extension=extensions[0] if extensions else None,
            )
        return _aba_sat_unsupported_semantics(semantics)
    if backend == "native":
        extensions = _sorted_object_extensions(_aba_extensions(framework, semantics))
        return SingleExtensionSolverSuccess(
            extension=extensions[0] if extensions else None,
        )
    if backend == "iccma":
        if iccma is None:
            return _missing_iccma_config()
        return _solve_iccma_aba_single_extension(framework, semantics, iccma)
    if backend == "aspforaba":
        return _aspforaba_unavailable()
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='native'.",
        reason=f"unknown backend: {backend!r}",
    )


def solve_aba_acceptance(
    framework: ABAInput,
    *,
    semantics: str,
    task: str,
    query: Literal,
    backend: str = "auto",
    iccma: ICCMAConfig | None = None,
) -> AcceptanceSolverResult:
    """Solve flat ABA credulous or skeptical acceptance queries."""
    if query not in _aba_base(framework).language:
        raise ValueError(f"query literal is not in framework language: {query!r}")
    backend = _auto_aba_backend(backend, semantics)
    if backend == "sat":
        if not isinstance(framework, ABAFramework):
            return _aba_sat_requires_flat_framework()
        if semantics == "stable":
            try:
                return _solve_sat_stable_aba_acceptance(framework, task, query)
            except RuntimeError as exc:
                return _aba_sat_runtime_unavailable(exc)
        if semantics in {"complete", "preferred"}:
            answer, witness = sat_aba_support_acceptance(
                framework,
                semantics=semantics,
                task=task,
                query=query,
            )
            return AcceptanceSolverSuccess(
                answer=answer,
                witness=witness if task == "credulous" and answer else None,
                counterexample=witness if task == "skeptical" and not answer else None,
            )
        return _aba_sat_unsupported_semantics(semantics)
    if backend == "native":
        return _solve_native_aba_acceptance(framework, semantics, task, query)
    if backend == "iccma":
        if iccma is None:
            return _missing_iccma_config()
        return _solve_iccma_aba_acceptance(framework, semantics, task, query, iccma)
    if backend == "aspforaba":
        return _aspforaba_unavailable()
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='native'.",
        reason=f"unknown backend: {backend!r}",
    )


def solve_dung_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str = "auto",
    iccma: ICCMAConfig | None = None,
    sat: SATConfig | None = None,
) -> ExtensionSolverResult:
    """Solve Dung extension queries through a package or external backend."""
    backend = _auto_dung_extension_backend(backend, semantics)
    if backend == "iccma":
        return SolverBackendUnavailable(
            backend=iccma.binary if iccma is not None else "iccma",
            install_hint="Use solve_dung_single_extension for ICCMA AF SE tasks.",
            reason="ICCMA AF SE tasks return one extension witness, not enumeration",
        )
    if backend == "sat":
        if sat is not None and sat.require_external:
            return _external_sat_unavailable()
        return ExtensionSolverSuccess(sat_extensions(framework, semantics))
    if backend == "native":
        return ExtensionSolverSuccess(
            _sorted_extensions(_dung_extensions(framework, semantics))
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='native'.",
        reason=f"unknown backend: {backend!r}",
    )


def solve_dung_single_extension(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str = "auto",
    iccma: ICCMAConfig | None = None,
    sat: SATConfig | None = None,
) -> SingleExtensionSolverResult:
    """Solve one Dung extension witness query."""
    backend = _auto_dung_single_backend(backend, semantics)
    if backend == "iccma":
        if iccma is None:
            return _missing_iccma_config()
        return _solve_iccma_dung_single_extension(framework, semantics, iccma)
    if backend == "native":
        extensions = _sorted_extensions(_dung_extensions(framework, semantics))
        return SingleExtensionSolverSuccess(
            extension=extensions[0] if extensions else None,
        )
    if backend == "sat":
        if sat is not None and sat.require_external:
            return _external_sat_unavailable()
        if semantics == "stable":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_stable_extension(framework),
                )
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        if semantics == "complete":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_complete_extension(framework),
                )
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        if semantics == "preferred":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_preferred_extension(framework),
                )
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        if semantics == "semi-stable":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_semi_stable_extension(framework),
                )
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        if semantics == "stage":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_stage_extension(framework),
                )
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        extensions = sat_extensions(framework, semantics)
        return SingleExtensionSolverSuccess(
            extension=extensions[0] if extensions else None,
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='native'.",
        reason=f"unknown backend: {backend!r}",
    )


def solve_dung_acceptance(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    task: str,
    query: str,
    backend: str = "auto",
    iccma: ICCMAConfig | None = None,
    sat: SATConfig | None = None,
) -> AcceptanceSolverResult:
    """Solve Dung credulous or skeptical acceptance queries."""
    if query not in framework.arguments:
        raise ValueError(f"query argument is not in framework: {query!r}")
    backend = _auto_dung_acceptance_backend(backend, semantics, task)
    if backend == "iccma":
        if iccma is None:
            return _missing_iccma_config()
        return _solve_iccma_dung_acceptance(framework, semantics, task, query, iccma)
    if backend == "native":
        return _solve_native_dung_acceptance(framework, semantics, task, query)
    if backend == "sat":
        if sat is not None and sat.require_external:
            return _external_sat_unavailable()
        if semantics == "stable":
            try:
                return _solve_sat_stable_acceptance(framework, task, query)
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        if semantics == "complete":
            try:
                return _solve_sat_complete_acceptance(framework, task, query)
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        if semantics == "preferred" and task == "credulous":
            try:
                return _solve_sat_preferred_credulous_acceptance(framework, query)
            except RuntimeError as exc:
                return _sat_runtime_unavailable(exc)
        return _solve_dung_acceptance_from_extensions(
            sat_extensions(framework, semantics),
            task,
            query,
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='native'.",
        reason=f"unknown backend: {backend!r}",
    )


def _missing_iccma_config() -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="iccma",
        reason="missing ICCMA solver configuration",
        install_hint="Pass iccma=ICCMAConfig(binary=...).",
    )


def _auto_dung_extension_backend(backend: str, semantics: str) -> str:
    if backend == "auto":
        return "sat" if semantics in {"complete", "stable"} else "native"
    return backend


def _auto_dung_single_backend(backend: str, semantics: str) -> str:
    if backend == "auto":
        return (
            "sat"
            if semantics in {"complete", "preferred", "semi-stable", "stable", "stage"}
            else "native"
        )
    return backend


def _auto_dung_acceptance_backend(backend: str, semantics: str, task: str) -> str:
    if backend == "auto":
        if semantics in {"complete", "stable"}:
            return "sat"
        if semantics == "preferred" and task == "credulous":
            return "sat"
        return "native"
    return backend


def _auto_aba_backend(backend: str, semantics: str) -> str:
    if backend == "auto":
        return "sat" if semantics in {"complete", "preferred", "stable"} else "native"
    return backend


def _external_sat_unavailable() -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason="external SAT backend is not configured",
        install_hint="Use SATConfig(require_external=False) for the package-native SAT enumerator.",
    )


def _sat_runtime_unavailable(exc: RuntimeError) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason=str(exc),
        install_hint="Install the z3-solver extra or use backend='native'.",
    )


def _aba_sat_runtime_unavailable(exc: RuntimeError) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason=str(exc),
        install_hint="Install the z3-solver extra or use backend='native'.",
    )


def _aba_sat_requires_flat_framework() -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason="ABA stable SAT backend requires a flat ABAFramework",
        install_hint="Use backend='native' for ABAPlusFramework inputs.",
    )


def _aba_sat_unsupported_semantics(semantics: str) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason=f"ABA SAT backend does not support {semantics!r} semantics",
        install_hint="Use backend='native' or backend='iccma'.",
    )


def _aspforaba_unavailable() -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="aspforaba",
        reason="ASPFORABA invocation contract is not configured",
        install_hint="Use backend='native' for flat ABA queries.",
    )


def _solve_native_aba_acceptance(
    framework: ABAInput,
    semantics: str,
    task: str,
    query: Literal,
) -> AcceptanceSolverSuccess:
    extensions = _sorted_object_extensions(_aba_extensions(framework, semantics))
    base = _aba_base(framework)
    if task == "credulous":
        witness = next(
            (
                extension
                for extension in extensions
                if aba_semantics.derives(base, _literal_extension(extension), query)
            ),
            None,
        )
        return AcceptanceSolverSuccess(
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = next(
            (
                extension
                for extension in extensions
                if not aba_semantics.derives(base, _literal_extension(extension), query)
            ),
            None,
        )
        return AcceptanceSolverSuccess(
            answer=counterexample is None,
            counterexample=counterexample,
        )
    raise ValueError(f"unsupported ABA acceptance task: {task}")


def _solve_sat_stable_aba_acceptance(
    framework: ABAFramework,
    task: str,
    query: Literal,
) -> AcceptanceSolverSuccess:
    if task == "credulous":
        witness = sat_aba_stable_extension(framework, require_derived=query)
        return AcceptanceSolverSuccess(
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = sat_aba_stable_extension(
            framework,
            require_not_derived=query,
        )
        return AcceptanceSolverSuccess(
            answer=counterexample is None,
            counterexample=counterexample,
        )
    raise ValueError(f"unsupported ABA acceptance task: {task}")


def _solve_native_dung_acceptance(
    framework: ArgumentationFramework,
    semantics: str,
    task: str,
    query: str,
) -> AcceptanceSolverSuccess:
    extensions = _sorted_extensions(_dung_extensions(framework, semantics))
    return _solve_dung_acceptance_from_extensions(extensions, task, query)


def _solve_sat_stable_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
) -> AcceptanceSolverSuccess:
    if task == "credulous":
        witness = sat_stable_extension(framework, require_in=query)
        return AcceptanceSolverSuccess(
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = sat_stable_extension(framework, require_out=query)
        return AcceptanceSolverSuccess(
            answer=counterexample is None,
            counterexample=counterexample,
        )
    raise ValueError(f"unsupported Dung acceptance task: {task}")


def _solve_sat_complete_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
) -> AcceptanceSolverSuccess:
    if task == "credulous":
        witness = sat_complete_extension(framework, require_in=query)
        return AcceptanceSolverSuccess(
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = sat_complete_extension(framework, require_out=query)
        return AcceptanceSolverSuccess(
            answer=counterexample is None,
            counterexample=counterexample,
        )
    raise ValueError(f"unsupported Dung acceptance task: {task}")


def _solve_sat_preferred_credulous_acceptance(
    framework: ArgumentationFramework,
    query: str,
) -> AcceptanceSolverSuccess:
    witness = sat_preferred_extension(framework, require_in=query)
    return AcceptanceSolverSuccess(
        answer=witness is not None,
        witness=witness,
    )


def _solve_dung_acceptance_from_extensions(
    extensions: tuple[frozenset[str], ...],
    task: str,
    query: str,
) -> AcceptanceSolverSuccess:
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
    backend: ICCMAConfig,
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


def _solve_iccma_aba_single_extension(
    framework: ABAInput,
    semantics: str,
    backend: ICCMAConfig,
) -> SingleExtensionSolverResult:
    if not isinstance(framework, ABAFramework):
        return _iccma_aba_requires_flat_framework(backend)
    result = iccma_aba.solve_aba_extensions(
        framework=framework,
        semantics=semantics,
        binary=backend.binary,
        timeout_seconds=backend.timeout_seconds,
    )
    if isinstance(result, iccma_aba.ICCMAABASolverSuccess):
        return SingleExtensionSolverSuccess(
            extension=result.witness if not result.output.no_extension else None,
        )
    if isinstance(result, iccma_aba.ICCMAABASolverUnavailable):
        return result
    if isinstance(result, iccma_aba.ICCMAABASolverError):
        return result
    return result


def _solve_iccma_dung_acceptance(
    framework: ArgumentationFramework,
    semantics: str,
    task: str,
    query: str,
    backend: ICCMAConfig,
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


def _solve_iccma_aba_acceptance(
    framework: ABAInput,
    semantics: str,
    task: str,
    query: Literal,
    backend: ICCMAConfig,
) -> AcceptanceSolverResult:
    if not isinstance(framework, ABAFramework):
        return _iccma_aba_requires_flat_framework(backend)
    result = iccma_aba.solve_aba_acceptance(
        framework=framework,
        semantics=semantics,
        task=task,
        query=query,
        binary=backend.binary,
        timeout_seconds=backend.timeout_seconds,
    )
    if isinstance(result, iccma_aba.ICCMAABASolverSuccess):
        return AcceptanceSolverSuccess(
            answer=result.answer is True,
        )
    if isinstance(result, iccma_aba.ICCMAABASolverUnavailable):
        return result
    if isinstance(result, iccma_aba.ICCMAABASolverError):
        return result
    return result


def _iccma_aba_requires_flat_framework(
    backend: ICCMAConfig,
) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend=backend.binary,
        reason="ICCMA ABA backend requires a flat ABAFramework",
        install_hint="Use backend='native' for ABAPlusFramework inputs.",
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


def _adf_models(
    framework: AbstractDialecticalFramework,
    semantics: str,
) -> tuple[frozenset[object], ...]:
    if semantics == "grounded":
        return (frozenset(adf_semantics.grounded_interpretation(framework)),)
    if semantics == "complete":
        return tuple(frozenset(model) for model in adf_semantics.complete_models(framework))
    if semantics == "model":
        return tuple(frozenset(model) for model in adf_semantics.model_models(framework))
    if semantics == "preferred":
        return tuple(frozenset(model) for model in adf_semantics.preferred_models(framework))
    if semantics == "stable":
        return tuple(frozenset(model) for model in adf_semantics.stable_models(framework))
    raise ValueError(f"Unknown ADF semantics: {semantics}")


def _setaf_extensions(
    framework: SETAF,
    semantics: str,
) -> tuple[frozenset[object], ...]:
    if semantics == "grounded":
        return (frozenset(setaf_semantics.grounded_extension(framework)),)
    if semantics == "complete":
        return tuple(frozenset(extension) for extension in setaf_semantics.complete_extensions(framework))
    if semantics == "preferred":
        return tuple(frozenset(extension) for extension in setaf_semantics.preferred_extensions(framework))
    if semantics == "stable":
        return tuple(frozenset(extension) for extension in setaf_semantics.stable_extensions(framework))
    if semantics == "semi-stable":
        return tuple(frozenset(extension) for extension in setaf_semantics.semi_stable_extensions(framework))
    if semantics == "stage":
        return tuple(frozenset(extension) for extension in setaf_semantics.stage_extensions(framework))
    raise ValueError(f"Unknown SETAF semantics: {semantics}")


def _aba_extensions(
    framework: ABAInput,
    semantics: str,
) -> tuple[frozenset[Literal], ...]:
    if semantics == "grounded":
        return (aba_semantics.grounded_extension(framework),)
    if semantics == "complete":
        return aba_semantics.complete_extensions(framework)
    if semantics == "preferred":
        return aba_semantics.preferred_extensions(framework)
    if semantics == "stable":
        return aba_semantics.stable_extensions(framework)
    if semantics == "well-founded":
        return (aba_semantics.well_founded_extension(framework),)
    if semantics == "ideal":
        return (aba_semantics.ideal_extension(framework),)
    raise ValueError(f"Unknown ABA semantics: {semantics}")


def _aba_base(framework: ABAInput) -> ABAFramework:
    return framework.framework if isinstance(framework, ABAPlusFramework) else framework


def _literal_extension(extension: frozenset[object]) -> frozenset[Literal]:
    if all(isinstance(item, Literal) for item in extension):
        return frozenset(item for item in extension if isinstance(item, Literal))
    raise TypeError("ABA extension contains non-literal members")


def _sorted_extensions(values: list[frozenset[str]]) -> tuple[frozenset[str], ...]:
    return tuple(
        sorted(
            values,
            key=lambda extension: (len(extension), tuple(sorted(extension))),
        )
    )


def _sorted_object_extensions(
    values: tuple[frozenset[Literal], ...],
) -> tuple[frozenset[object], ...]:
    return tuple(
        sorted(
            (frozenset(extension) for extension in values),
            key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
        )
    )
