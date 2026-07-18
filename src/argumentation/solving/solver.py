"""Small solver-result wrappers for extension queries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import importlib.util

from argumentation.core.optional_deps import OptionalDependencyUnavailable
from argumentation.structured.aba import aba as aba_semantics
from argumentation.frameworks import adf as adf_semantics
from argumentation.frameworks import setaf as setaf_semantics
from argumentation.structured.aba.aba import ABAFramework, ABAInput, ABAPlusFramework
from argumentation.structured.aba.aba_sat import (
    native_sparse_narrow_sat_extension as native_sparse_narrow_aba_extension,
    sat_stable_acceptance as sat_aba_stable_acceptance,
    sat_stable_extension as sat_aba_stable_extension,
    sat_support_acceptance as sat_aba_support_acceptance,
    sat_support_extension as sat_aba_support_extension,
    support_extensions as sat_aba_support_extensions,
)
from argumentation.solving.af_sat import (
    AfSatCheckTimeout,
    SATTraceSink,
    find_complete_extension,
    find_ideal_extension,
    find_preferred_extension,
    find_semi_stable_extension,
    find_stable_extension,
    find_stage_extension,
    is_preferred_skeptically_accepted,
)
from argumentation.frameworks.adf import AbstractDialecticalFramework
from argumentation.structured.aspic.aspic import Literal
from argumentation.core.dung import (
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
from argumentation.structured.aba.aba_route_policy import large_dense_flat_aba_shape
from argumentation.structured.aba.aba_route_policy import sparse_narrow_native_sat_shape
from argumentation.solving.sat_encoding import (
    sat_extensions,
)
from argumentation.core.scc_recursive import (
    SCC_RECURSIVE_SEMANTICS,
    scc_extensions,
)
from argumentation.solving.af_scc_cone import (
    PREFERRED_CONE_MIN_DEFEATS,
    solve_cone_acceptance,
)
from argumentation.frameworks.setaf import SETAF
from argumentation.solver_adapters import iccma_aba, iccma_af
from argumentation.core.solver_results import (
    AcceptanceSuccess,
    ExtensionEnumerationSuccess,
    SingleExtensionSuccess,
    SolverProcessError,
    SolverProtocolError,
    SolverTimeout,
    SolverUnavailable,
)


SolverBackendUnavailable = SolverUnavailable
SolverBackendError = SolverProcessError
SolverBackendTimeout = SolverTimeout


@dataclass(frozen=True)
class ICCMAConfig:
    """ICCMA subprocess configuration for solver backends."""

    binary: str
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class SATConfig:
    """Configuration for package-native or externally supplied SAT solving.

    ``check_budget_seconds`` is an optional per-check Z3 time budget (seconds,
    ``None`` = unlimited). When the budget is exhausted the SAT layer raises a
    structured timeout instead of collapsing Z3 ``unknown`` into a sat/unsat
    answer.
    """

    require_external: bool = False
    trace_sink: SATTraceSink | None = None
    metadata: Mapping[str, object] | None = None
    check_budget_seconds: float | None = None


ExtensionSolverSuccess = ExtensionEnumerationSuccess
SingleExtensionSolverSuccess = SingleExtensionSuccess
AcceptanceSolverSuccess = AcceptanceSuccess


ExtensionSolverResult = (
    ExtensionSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
    | SolverBackendTimeout
    | SolverProtocolError
)
SingleExtensionSolverResult = (
    SingleExtensionSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
    | SolverBackendTimeout
    | SolverProtocolError
)
AcceptanceSolverResult = (
    AcceptanceSolverSuccess
    | SolverBackendUnavailable
    | SolverBackendError
    | SolverBackendTimeout
    | SolverProtocolError
)


def _flat_sat_engine(kind: str, framework: ArgumentationFramework) -> str:
    """Z3 engine for a FLAT (non-cone) AF SAT op, per the exp/af-satcore-flat
    74-cell A/B probe (2026-07-10, completed in 2026-07-17-af-flat-satcore.md).

    ``Tactic('sat')`` (sat-core) is answer-identical to the default SMT core on
    these purely propositional labelling encodings but far faster at scale.
    ``kind``:
    - ``"complete"`` / ``"preferred_witness"``: sat-core unconditional
      (win-or-tie every probed cell; some ER timeouts -> solved).
    - ``"cdas_skeptical"``: sat-core only above the defeat threshold; the
      non-incremental sat core has a small-instance CDAS-loop pathology
      (BA_160_80_2: 0.42s -> 11.55s) below it.
    - anything else (``"stable"``, ``"ideal"``): smt (no win, one measured loss).
    Semi-stable/stage never reach here for sat-core: their range-maximal loop
    uses pseudo-Boolean constraints Tactic('sat') cannot express.
    """
    if kind in ("complete", "preferred_witness"):
        return "sat-core"
    if kind == "cdas_skeptical":
        if len(framework.defeats) >= PREFERRED_CONE_MIN_DEFEATS:
            return "sat-core"
    return "smt"


# Dung single-extension SAT finders keyed by semantics. Every finder shares the
# (framework, *, trace_sink, metadata) signature, so the dispatch in
# solve_dung_single_extension is one table lookup plus one try/except wrapper.
_SAT_SINGLE_EXTENSION_FINDERS = {
    "stable": find_stable_extension,
    "complete": find_complete_extension,
    "preferred": find_preferred_extension,
    "semi-stable": find_semi_stable_extension,
    "stage": find_stage_extension,
    "ideal": find_ideal_extension,
}


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
    clingo_control_args: tuple[str, ...] = (),
    collect_clingo_statistics: bool = False,
    clingo_solve_timeout_seconds: float | None = None,
) -> SingleExtensionSolverResult:
    """Solve one flat ABA extension witness query."""
    backend = _auto_aba_backend_for_framework(
        backend,
        semantics,
        task="single-extension",
        framework=framework,
    )
    if backend == "sat":
        if not isinstance(framework, ABAFramework):
            return _aba_sat_requires_flat_framework()
        if (
            semantics in {"preferred", "stable"}
            and sparse_narrow_native_sat_shape(framework)
        ):
            try:
                result = native_sparse_narrow_aba_extension(framework, semantics)
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
            return SingleExtensionSolverSuccess(
                extension=result.extension,
                metadata=result.route_metadata | result.telemetry,
            )
        if semantics == "stable":
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_aba_stable_extension(framework),
                )
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
        if semantics in {"complete", "preferred"}:
            try:
                return SingleExtensionSolverSuccess(
                    extension=sat_aba_support_extension(framework, semantics),
                )
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
        return _aba_sat_unsupported_semantics(semantics)
    if backend in {"asp", "clingo"}:
        if not isinstance(framework, ABAFramework):
            return _aba_asp_requires_flat_framework(backend)
        return _solve_asp_aba_single_extension(
            framework,
            semantics,
            backend,
            clingo_control_args=clingo_control_args,
            collect_clingo_statistics=collect_clingo_statistics,
            clingo_solve_timeout_seconds=clingo_solve_timeout_seconds,
        )
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
    backend = _auto_aba_backend_for_framework(
        backend,
        semantics,
        task=task,
        framework=framework,
    )
    if backend == "sat":
        if not isinstance(framework, ABAFramework):
            return _aba_sat_requires_flat_framework()
        if semantics == "stable":
            try:
                return _solve_sat_stable_aba_acceptance(framework, task, query)
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
        if semantics in {"complete", "preferred"}:
            try:
                answer, witness = sat_aba_support_acceptance(
                    framework,
                    semantics=semantics,
                    task=task,
                    query=query,
                )
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
            return AcceptanceSolverSuccess(
                answer=answer,
                witness=witness if task == "credulous" and answer else None,
                counterexample=witness if task == "skeptical" and not answer else None,
            )
        return _aba_sat_unsupported_semantics(semantics)
    if backend in {"asp", "clingo"}:
        if not isinstance(framework, ABAFramework):
            return _aba_asp_requires_flat_framework(backend)
        return _solve_asp_aba_acceptance(framework, semantics, task, query, backend)
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
        try:
            return ExtensionSolverSuccess(sat_extensions(framework, semantics))
        except OptionalDependencyUnavailable as exc:
            return _optional_dependency_unavailable(exc)
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
        trace_sink, metadata, check_budget_seconds = _sat_options(sat)
        find_single = _SAT_SINGLE_EXTENSION_FINDERS.get(semantics)
        if find_single is not None:
            # Only complete/preferred finders accept an engine and are routed to
            # sat-core (SE-CO / SE-PR); stable/semi-stable/stage/ideal keep smt.
            single_kwargs: dict[str, object] = dict(
                trace_sink=trace_sink,
                metadata=metadata,
                check_budget_seconds=check_budget_seconds,
            )
            if semantics == "complete":
                single_kwargs["engine"] = _flat_sat_engine("complete", framework)
            elif semantics == "preferred":
                single_kwargs["engine"] = _flat_sat_engine("preferred_witness", framework)
            try:
                return SingleExtensionSolverSuccess(
                    extension=find_single(framework, **single_kwargs),
                )
            except AfSatCheckTimeout as exc:
                return _sat_check_timeout(exc, semantics)
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
        try:
            extensions = sat_extensions(framework, semantics)
        except OptionalDependencyUnavailable as exc:
            return _optional_dependency_unavailable(exc)
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
    requested_backend = backend
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
        trace_sink, metadata, check_budget_seconds = _sat_options(sat)
        if requested_backend == "auto":
            # Query-directed SCC-cone path (sound per the derivations in
            # experiments/2026-07-10-af-scc-acceptance.md); None means the
            # cone does not apply or is inconclusive -> flat path below.
            try:
                cone_result = solve_cone_acceptance(
                    framework,
                    semantics=semantics,
                    task=task,
                    query=query,
                    trace_sink=trace_sink,
                    metadata=metadata,
                    check_budget_seconds=check_budget_seconds,
                )
            except AfSatCheckTimeout as exc:
                return _sat_check_timeout(exc, semantics)
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
            if cone_result is not None:
                return cone_result
        solve_dedicated = _dedicated_sat_acceptance_solver(semantics, task)
        if solve_dedicated is not None:
            try:
                return solve_dedicated(
                    framework,
                    task,
                    query,
                    trace_sink=trace_sink,
                    metadata=metadata,
                    check_budget_seconds=check_budget_seconds,
                )
            except AfSatCheckTimeout as exc:
                return _sat_check_timeout(exc, semantics)
            except OptionalDependencyUnavailable as exc:
                return _optional_dependency_unavailable(exc)
        try:
            extensions = sat_extensions(framework, semantics)
        except OptionalDependencyUnavailable as exc:
            return _optional_dependency_unavailable(exc)
        return _solve_dung_acceptance_from_extensions(extensions, task, query)
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
            if semantics in {"complete", "ideal", "preferred", "semi-stable", "stable", "stage"}
            else "native"
        )
    return backend


def _auto_dung_acceptance_backend(backend: str, semantics: str, task: str) -> str:
    if backend == "auto":
        if semantics in {"complete", "ideal", "semi-stable", "stable", "stage"}:
            return "sat"
        if semantics == "preferred" and task in {"credulous", "skeptical"}:
            return "sat"
        return "native"
    return backend


def _auto_aba_backend(backend: str, semantics: str, *, task: str) -> str:
    if backend == "auto":
        if (
            _has_clingo()
            and (
                semantics == "grounded"
                or (
                    semantics == "preferred"
                    and task in {"single-extension", "skeptical"}
                )
                or (semantics == "stable" and task == "single-extension")
            )
        ):
            return "asp"
        return "sat" if semantics in {"complete", "preferred", "stable"} else "native"
    return backend


def _auto_aba_backend_for_framework(
    backend: str,
    semantics: str,
    *,
    task: str,
    framework: ABAInput,
) -> str:
    if (
        backend == "auto"
        and semantics == "preferred"
        and task == "single-extension"
        and isinstance(framework, ABAFramework)
        and sparse_narrow_native_sat_shape(framework)
    ):
        return "sat"
    if (
        backend == "auto"
        and semantics == "stable"
        and task == "single-extension"
        and isinstance(framework, ABAFramework)
        and large_dense_flat_aba_shape(framework)
        and sparse_narrow_native_sat_shape(framework)
    ):
        return "sat"
    return _auto_aba_backend(backend, semantics, task=task)


def _has_clingo() -> bool:
    return importlib.util.find_spec("clingo") is not None


def _external_sat_unavailable() -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason="external SAT backend is not configured",
        install_hint="Use SATConfig(require_external=False) for the package-native SAT enumerator.",
    )


def _sat_options(
    sat: SATConfig | None,
) -> tuple[SATTraceSink | None, Mapping[str, object] | None, float | None]:
    if sat is None:
        return None, None, None
    return sat.trace_sink, sat.metadata, sat.check_budget_seconds


def _sat_check_timeout(exc: AfSatCheckTimeout, semantics: str) -> SolverBackendTimeout:
    return SolverBackendTimeout(
        backend="sat",
        problem=f"AF-{semantics}",
        message=str(exc),
        metadata={
            "utility_name": exc.utility_name,
            "check_budget_seconds": exc.check_budget_seconds,
        },
    )


def _optional_dependency_unavailable(
    exc: OptionalDependencyUnavailable,
) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason=str(exc),
        install_hint=exc.install_hint,
    )


def _aba_sat_requires_flat_framework() -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason="ABA stable SAT backend requires a flat ABAFramework",
        install_hint="Use backend='native' for ABAPlusFramework inputs.",
    )


def _aba_asp_requires_flat_framework(backend: str) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend=backend,
        reason="ABA ASP backend requires a flat ABAFramework",
        install_hint="Use backend='native' for ABAPlusFramework inputs.",
    )


def _aba_sat_unsupported_semantics(semantics: str) -> SolverBackendUnavailable:
    return SolverBackendUnavailable(
        backend="sat",
        reason=f"ABA SAT backend does not support {semantics!r} semantics",
        install_hint="Use backend='native' or backend='iccma'.",
    )


def _solve_asp_aba_single_extension(
    framework: ABAFramework,
    semantics: str,
    backend: str,
    *,
    clingo_control_args: tuple[str, ...] = (),
    collect_clingo_statistics: bool = False,
    clingo_solve_timeout_seconds: float | None = None,
) -> SingleExtensionSolverResult:
    from argumentation.structured.aba.aba_asp import solve_aba_with_backend

    result = solve_aba_with_backend(
        framework,
        backend=backend,
        semantics=semantics,
        task="single-extension",
        clingo_control_args=clingo_control_args,
        collect_clingo_statistics=collect_clingo_statistics,
        clingo_solve_timeout_seconds=clingo_solve_timeout_seconds,
    )
    if result.status == "success":
        extension = result.extensions[0] if result.extensions else None
        return SingleExtensionSolverSuccess(extension=extension, metadata=dict(result.metadata))
    return _aba_asp_failure(result)


def _solve_asp_aba_acceptance(
    framework: ABAFramework,
    semantics: str,
    task: str,
    query: Literal,
    backend: str,
) -> AcceptanceSolverResult:
    from argumentation.structured.aba.aba_asp import solve_aba_with_backend

    result = solve_aba_with_backend(
        framework,
        backend=backend,
        semantics=semantics,
        task=task,
        query=query,
    )
    if result.status == "success" and result.answer is not None:
        return AcceptanceSolverSuccess(
            answer=result.answer,
            witness=result.witness if task == "credulous" and result.answer else None,
            counterexample=(
                result.counterexample if task == "skeptical" and not result.answer else None
            ),
            metadata=dict(result.metadata),
        )
    return _aba_asp_failure(result)


def _aba_asp_failure(
    result,
) -> SolverBackendUnavailable | SolverBackendError | SolverBackendTimeout | SolverProtocolError:
    reason = result.metadata.get("reason", result.status)
    stdout = result.metadata.get("stdout", "")
    stderr = result.metadata.get("stderr", "")
    problem = f"ABA-{result.semantics.upper()}"
    if result.status == "unavailable_backend":
        return SolverBackendUnavailable(
            backend=result.backend,
            reason=reason,
            install_hint="Install the clingo Python package or use backend='sat'/'native'.",
        )
    if result.status == "backend_error":
        return SolverBackendError(
            backend=result.backend,
            problem=problem,
            returncode=1,
            stdout=stdout,
            stderr=stderr or reason,
        )
    if result.status == "timeout":
        return SolverBackendTimeout(
            backend=result.backend,
            problem=problem,
            message=reason,
            metadata=dict(result.metadata),
        )
    return SolverProtocolError(
        backend=result.backend,
        problem=problem,
        message=reason,
        stdout=stdout,
        stderr=stderr,
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
    if task in {"credulous", "skeptical"}:
        answer, witness = sat_aba_stable_acceptance(framework, task=task, query=query)
        return AcceptanceSolverSuccess(
            answer=answer,
            witness=witness if task == "credulous" and answer else None,
            counterexample=witness if task == "skeptical" and not answer else None,
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


def _solve_sat_acceptance(
    find_extension,
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
    engine: str | None = None,
) -> AcceptanceSolverSuccess:
    """Credulous (require_in→witness) / skeptical (require_out→counterexample)
    SAT acceptance against any find_*_extension finder sharing the
    (framework, *, require_in/require_out, trace_sink, metadata,
    check_budget_seconds) signature. ``engine`` is forwarded only when set, so
    finders without an engine parameter (semi-stable, stage) keep working."""
    shared = dict(
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    if engine is not None:
        shared["engine"] = engine
    if task == "credulous":
        witness = find_extension(framework, require_in=query, **shared)
        return AcceptanceSolverSuccess(
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = find_extension(framework, require_out=query, **shared)
        return AcceptanceSolverSuccess(
            answer=counterexample is None,
            counterexample=counterexample,
        )
    raise ValueError(f"unsupported Dung acceptance task: {task}")


def _solve_sat_stable_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    return _solve_sat_acceptance(
        find_stable_extension,
        framework,
        task,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )


def _solve_sat_complete_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    return _solve_sat_acceptance(
        find_complete_extension,
        framework,
        task,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=_flat_sat_engine("complete", framework),
    )


def _solve_sat_preferred_credulous_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    del task  # dispatch guarantees task == "credulous"
    witness = find_preferred_extension(
        framework,
        require_in=query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=_flat_sat_engine("preferred_witness", framework),
    )
    return AcceptanceSolverSuccess(
        answer=witness is not None,
        witness=witness,
    )


def _solve_sat_preferred_skeptical_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    del task  # dispatch guarantees task == "skeptical"
    answer = is_preferred_skeptically_accepted(
        framework,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=_flat_sat_engine("cdas_skeptical", framework),
    )
    return AcceptanceSolverSuccess(
        answer=answer,
    )


def _solve_sat_ideal_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    extension = find_ideal_extension(
        framework,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    if task == "credulous":
        return AcceptanceSolverSuccess(
            answer=query in extension,
            witness=extension if query in extension else None,
        )
    if task == "skeptical":
        return AcceptanceSolverSuccess(
            answer=query in extension,
            counterexample=None if query in extension else extension,
        )
    raise ValueError(f"unsupported Dung acceptance task: {task}")


def _solve_sat_semi_stable_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    return _solve_sat_acceptance(
        find_semi_stable_extension,
        framework,
        task,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )


def _solve_sat_stage_acceptance(
    framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSolverSuccess:
    return _solve_sat_acceptance(
        find_stage_extension,
        framework,
        task,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )


# Dung SAT acceptance helpers keyed by semantics. Every helper shares the
# (framework, task, query, *, trace_sink, metadata, check_budget_seconds)
# signature; preferred is task-specific, so it is dispatched separately in
# _dedicated_sat_acceptance_solver.
_SAT_ACCEPTANCE_SOLVERS = {
    "stable": _solve_sat_stable_acceptance,
    "complete": _solve_sat_complete_acceptance,
    "ideal": _solve_sat_ideal_acceptance,
    "semi-stable": _solve_sat_semi_stable_acceptance,
    "stage": _solve_sat_stage_acceptance,
}


def _dedicated_sat_acceptance_solver(semantics: str, task: str):
    """Return the dedicated SAT acceptance helper, or None for the
    enumeration fallback."""
    if semantics == "preferred":
        if task == "credulous":
            return _solve_sat_preferred_credulous_acceptance
        if task == "skeptical":
            return _solve_sat_preferred_skeptical_acceptance
        return None
    return _SAT_ACCEPTANCE_SOLVERS.get(semantics)


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
    # complete / preferred / stable: route through the SCC-recursive layer
    # (Wave B2), which composes the Wave A grounded-reduct preprocessing with
    # Baroni-Giacomin-Guida SCC decomposition. Transparent: identical results,
    # faster on layered/many-small-SCC AFs, ~1.0x on a single giant SCC.
    if semantics in SCC_RECURSIVE_SEMANTICS:
        return scc_extensions(framework, semantics)
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
