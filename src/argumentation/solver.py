"""Small solver-result wrappers for optional Z3 backends."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

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


DEFAULT_Z3_TIMEOUT_MS = 30_000


class SolverUnknownReason(StrEnum):
    TIMEOUT = "timeout"
    INCOMPLETE = "incomplete"
    OTHER = "other"


@dataclass(frozen=True)
class SolverSat:
    model: object | None = None


@dataclass(frozen=True)
class SolverUnsat:
    unsat_core: tuple[str, ...] = ()


@dataclass(frozen=True)
class SolverUnknown:
    reason: SolverUnknownReason
    hint: str


@dataclass(frozen=True)
class SolverBackendUnavailable:
    backend: str
    install_hint: str
    reason: str


@dataclass(frozen=True)
class ExtensionSolverSuccess:
    extensions: tuple[frozenset[str], ...]


SolverResult = SolverSat | SolverUnsat | SolverUnknown
ExtensionSolverResult = ExtensionSolverSuccess | SolverBackendUnavailable


class Z3UnknownError(Exception):
    """Raised when a two-valued caller receives a Z3 unknown result."""

    def __init__(self, result: SolverUnknown) -> None:
        self.result = result
        super().__init__(f"Z3 returned UNKNOWN ({result.reason.value}): {result.hint}")


def _unknown_reason(hint: str) -> SolverUnknownReason:
    normalized = hint.lower()
    if "timeout" in normalized or "canceled" in normalized:
        return SolverUnknownReason.TIMEOUT
    if "incomplete" in normalized or "unknown" in normalized:
        return SolverUnknownReason.INCOMPLETE
    return SolverUnknownReason.OTHER


def solver_result_from_z3(solver: Any) -> SolverResult:
    import z3

    check_result = solver.check()
    if check_result == z3.sat:
        return SolverSat(solver.model())
    if check_result == z3.unsat:
        return SolverUnsat(tuple(str(entry) for entry in solver.unsat_core()))
    hint = solver.reason_unknown() or "z3 returned unknown without a reason"
    return SolverUnknown(_unknown_reason(hint), hint)


def solve_dung_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    backend: str = "brute",
) -> ExtensionSolverResult:
    """Solve Dung extension queries with typed optional-backend unavailability."""
    if backend == "brute":
        return ExtensionSolverSuccess(
            _sorted_extensions(_brute_dung_extensions(framework, semantics))
        )
    if backend == "z3":
        unavailable = _z3_unavailable()
        if unavailable is not None:
            return unavailable
        if semantics not in {"complete", "preferred", "stable"}:
            return SolverBackendUnavailable(
                backend="z3",
                install_hint="Use backend='brute' for this semantics.",
                reason=f"z3 backend does not support {semantics!r} semantics",
            )
        return ExtensionSolverSuccess(
            _sorted_extensions(_z3_dung_extensions(framework, semantics))
        )
    return SolverBackendUnavailable(
        backend=backend,
        install_hint="Use backend='brute' or install an advertised optional backend.",
        reason=f"unknown backend: {backend!r}",
    )


def _z3_unavailable() -> SolverBackendUnavailable | None:
    if importlib.util.find_spec("z3") is not None:
        return None
    return SolverBackendUnavailable(
        backend="z3",
        install_hint="Install formal-argumentation[z3] to enable the z3 backend.",
        reason="z3 module is not importable",
    )


def _brute_dung_extensions(
    framework: ArgumentationFramework,
    semantics: str,
) -> list[frozenset[str]]:
    if semantics == "grounded":
        return [grounded_extension(framework)]
    if semantics == "complete":
        return complete_extensions(framework, backend="brute")
    if semantics == "preferred":
        return preferred_extensions(framework, backend="brute")
    if semantics == "stable":
        return stable_extensions(framework, backend="brute")
    if semantics == "semi-stable":
        return semi_stable_extensions(framework, backend="brute")
    if semantics == "stage":
        return stage_extensions(framework, backend="brute")
    if semantics == "ideal":
        return [ideal_extension(framework, backend="brute")]
    if semantics == "cf2":
        return cf2_extensions(framework, backend="brute")
    raise ValueError(f"Unknown Dung semantics: {semantics}")


def _z3_dung_extensions(
    framework: ArgumentationFramework,
    semantics: str,
) -> list[frozenset[str]]:
    from argumentation.dung_z3 import (
        z3_complete_extensions,
        z3_preferred_extensions,
        z3_stable_extensions,
    )

    if semantics == "complete":
        return z3_complete_extensions(framework)
    if semantics == "preferred":
        return z3_preferred_extensions(framework)
    if semantics == "stable":
        return z3_stable_extensions(framework)
    raise ValueError(f"z3 backend does not support semantics: {semantics}")


def _sorted_extensions(values: list[frozenset[str]]) -> tuple[frozenset[str], ...]:
    return tuple(
        sorted(
            values,
            key=lambda extension: (len(extension), tuple(sorted(extension))),
        )
    )
