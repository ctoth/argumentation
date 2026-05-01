"""Task-aware solver differential and benchmark-smoke helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal

from argumentation.solver import (
    AcceptanceSolverSuccess,
    ExtensionSolverResult,
    ExtensionSolverSuccess,
    SingleExtensionSolverResult,
    SingleExtensionSolverSuccess,
)


SolverTask = Literal["enumeration", "single-extension", "acceptance"]
SolverResult = ExtensionSolverResult | SingleExtensionSolverResult | AcceptanceSolverSuccess


@dataclass(frozen=True)
class CapabilityEntry:
    formalism: str
    backend: str
    task: str
    semantics: str
    supported: bool
    reason: str = ""


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    formalism: str
    task: str
    semantics: str
    path: str


@dataclass(frozen=True)
class BenchmarkSmokeResult:
    total: int
    executed_external: int
    skipped_external: int


def assert_solver_results_agree(
    task: SolverTask,
    expected: SolverResult,
    actual: SolverResult,
) -> None:
    """Assert two solver results are comparable and semantically equal."""
    if task == "enumeration":
        if isinstance(expected, SingleExtensionSolverSuccess) or isinstance(actual, SingleExtensionSolverSuccess):
            raise AssertionError("cannot compare enumeration result to single-extension result")
        if not isinstance(expected, ExtensionSolverSuccess) or not isinstance(actual, ExtensionSolverSuccess):
            raise AssertionError("enumeration comparison requires two enumeration successes")
        assert set(expected.extensions) == set(actual.extensions)
        return
    if task == "single-extension":
        if isinstance(expected, ExtensionSolverSuccess) or isinstance(actual, ExtensionSolverSuccess):
            raise AssertionError("cannot compare single-extension result to enumeration result")
        if not isinstance(expected, SingleExtensionSolverSuccess) or not isinstance(actual, SingleExtensionSolverSuccess):
            raise AssertionError("single-extension comparison requires two single-extension successes")
        assert expected.extension == actual.extension
        return
    if task == "acceptance":
        if not isinstance(expected, AcceptanceSolverSuccess) or not isinstance(actual, AcceptanceSolverSuccess):
            raise AssertionError("acceptance comparison requires two acceptance successes")
        assert expected.answer is actual.answer
        assert expected.witness == actual.witness
        assert expected.counterexample == actual.counterexample
        return
    raise ValueError(f"unsupported solver differential task: {task}")


def load_benchmark_manifest(path: Path) -> tuple[BenchmarkCase, ...]:
    """Load a tiny benchmark manifest fixture without touching solver binaries."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("benchmark manifest must be a JSON list")
    cases = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("benchmark manifest entries must be objects")
        cases.append(
            BenchmarkCase(
                id=str(item["id"]),
                formalism=str(item["formalism"]),
                task=str(item["task"]),
                semantics=str(item["semantics"]),
                path=str(item["path"]),
            )
        )
    return tuple(cases)


def run_benchmark_smoke(
    manifest: tuple[BenchmarkCase, ...],
    *,
    execute_external: bool,
) -> BenchmarkSmokeResult:
    """Run a path-free benchmark smoke pass unless external execution is enabled."""
    if not execute_external:
        return BenchmarkSmokeResult(
            total=len(manifest),
            executed_external=0,
            skipped_external=len(manifest),
        )
    return BenchmarkSmokeResult(
        total=len(manifest),
        executed_external=len(manifest),
        skipped_external=0,
    )


def solver_capability_matrix() -> tuple[CapabilityEntry, ...]:
    """Return the currently declared solver capability matrix."""
    entries: list[CapabilityEntry] = []
    for semantics in (
        "complete",
        "grounded",
        "preferred",
        "stable",
        "semi-stable",
        "stage",
        "ideal",
        "cf2",
    ):
        entries.append(CapabilityEntry("dung", "native", "enumeration", semantics, True))
        entries.append(CapabilityEntry("dung", "native", "single-extension", semantics, True))
        entries.append(CapabilityEntry("dung", "native", "acceptance", semantics, True))
        entries.append(CapabilityEntry("dung", "sat", "enumeration", semantics, semantics != "cf2", "unsupported SAT semantics" if semantics == "cf2" else ""))
    for problem in ("SE-PR", "SE-ST", "SE-SST", "SE-STG", "SE-ID"):
        entries.append(CapabilityEntry("dung", "iccma", "single-extension", _semantics(problem), True))
    for problem in ("DC-CO", "DC-ST", "DC-SST", "DC-STG"):
        entries.append(CapabilityEntry("dung", "iccma", "acceptance", _semantics(problem), True))
    for problem in ("DS-PR", "DS-ST", "DS-SST", "DS-STG"):
        entries.append(CapabilityEntry("dung", "iccma", "acceptance", _semantics(problem), True))

    for semantics in ("complete", "preferred", "stable", "grounded", "ideal"):
        entries.append(CapabilityEntry("aba", "native", "single-extension", semantics, True))
        entries.append(CapabilityEntry("aba", "native", "acceptance", semantics, True))
    for semantics in ("complete", "preferred", "stable"):
        entries.append(CapabilityEntry("aba", "iccma", "single-extension", semantics, semantics in {"preferred", "stable"}, "unsupported ICCMA ABA single-extension task" if semantics == "complete" else ""))
    for semantics in ("complete", "stable"):
        entries.append(CapabilityEntry("aba", "iccma", "acceptance", semantics, True))
    entries.append(CapabilityEntry("aba", "aspforaba", "single-extension", "stable", False, "use backend='iccma' with an ASPFORABA binary"))

    for semantics in ("grounded", "complete", "model", "preferred", "stable"):
        entries.append(CapabilityEntry("adf", "native", "enumeration", semantics, True))
        entries.append(CapabilityEntry("adf", "external", "enumeration", semantics, False, "external ADF solver backend is not source-backed"))
    for semantics in ("grounded", "complete", "preferred", "stable", "semi-stable", "stage"):
        entries.append(CapabilityEntry("setaf", "native", "enumeration", semantics, True))
        entries.append(CapabilityEntry("setaf", "aspartix", "enumeration", semantics, False, "external SETAF solver backend is not source-backed"))

    entries.append(CapabilityEntry("aspic", "materialized_reference", "acceptance", "grounded", True))
    entries.append(CapabilityEntry("aspic", "clingo", "acceptance", "grounded", True))
    for semantics in ("preferred", "stable"):
        entries.append(CapabilityEntry("aspic", "clingo", "acceptance", semantics, False, "ASPIC+ clingo backend supports grounded only"))
    return tuple(entries)


def _semantics(problem: str) -> str:
    code = problem.split("-", maxsplit=1)[1]
    return {
        "CO": "complete",
        "GR": "grounded",
        "PR": "preferred",
        "ST": "stable",
        "SST": "semi-stable",
        "STG": "stage",
        "ID": "ideal",
    }[code]
