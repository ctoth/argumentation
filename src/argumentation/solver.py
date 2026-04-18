"""Small solver-result wrappers for optional Z3 backends."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import z3


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


SolverResult = SolverSat | SolverUnsat | SolverUnknown


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


def solver_result_from_z3(solver: z3.Solver) -> SolverResult:
    check_result = solver.check()
    if check_result == z3.sat:
        return SolverSat(solver.model())
    if check_result == z3.unsat:
        return SolverUnsat(tuple(str(entry) for entry in solver.unsat_core()))
    hint = solver.reason_unknown() or "z3 returned unknown without a reason"
    return SolverUnknown(_unknown_reason(hint), hint)
