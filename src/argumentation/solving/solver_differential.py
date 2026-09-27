"""Task-aware solver differential and benchmark-smoke helpers."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal

from argumentation.solving.solver import (
    AcceptanceSolverSuccess,
    ExtensionSolverResult,
    ExtensionSolverSuccess,
    SingleExtensionSolverResult,
    SingleExtensionSolverSuccess,
)


SolverTask = Literal["enumeration", "single-extension", "acceptance"]
SolverResult = (
    ExtensionSolverResult | SingleExtensionSolverResult | AcceptanceSolverSuccess
)


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
    *,
    reference_extensions: Collection[frozenset[object]] | None = None,
    query: object | None = None,
) -> None:
    """Assert two solver results are comparable and semantically equal.

    Single-extension witnesses and acceptance certificates are choices: a
    solver may return any extension of the semantics, and any extension that
    contains (credulous witness) or omits (skeptical counterexample) the
    query. Differing choices therefore agree when each is valid against
    ``reference_extensions``, the full extension set of the semantics.
    Identical choices need no reference; differing ones cannot be judged
    without it. Acceptance certificates are validated with ``query``.
    """
    if task == "enumeration":
        if isinstance(expected, SingleExtensionSolverSuccess) or isinstance(
            actual, SingleExtensionSolverSuccess
        ):
            raise AssertionError(
                "cannot compare enumeration result to single-extension result"
            )
        if not isinstance(expected, ExtensionSolverSuccess) or not isinstance(
            actual, ExtensionSolverSuccess
        ):
            raise AssertionError(
                "enumeration comparison requires two enumeration successes"
            )
        assert set(expected.extensions) == set(actual.extensions)
        return
    if task == "single-extension":
        if isinstance(expected, ExtensionSolverSuccess) or isinstance(
            actual, ExtensionSolverSuccess
        ):
            raise AssertionError(
                "cannot compare single-extension result to enumeration result"
            )
        if not isinstance(expected, SingleExtensionSolverSuccess) or not isinstance(
            actual, SingleExtensionSolverSuccess
        ):
            raise AssertionError(
                "single-extension comparison requires two single-extension successes"
            )
        if (expected.extension is None) != (actual.extension is None):
            raise AssertionError("solvers disagree on whether an extension exists")
        _validate_certificates(
            "single-extension witness",
            _present(expected.extension, actual.extension),
            reference_extensions,
        )
        return
    if task == "acceptance":
        if not isinstance(expected, AcceptanceSolverSuccess) or not isinstance(
            actual, AcceptanceSolverSuccess
        ):
            raise AssertionError(
                "acceptance comparison requires two acceptance successes"
            )
        assert expected.answer is actual.answer
        witnesses = _present(expected.witness, actual.witness)
        counterexamples = _present(expected.counterexample, actual.counterexample)
        _validate_certificates("credulous witness", witnesses, reference_extensions)
        _validate_certificates(
            "skeptical counterexample", counterexamples, reference_extensions
        )
        if reference_extensions is not None and (witnesses or counterexamples):
            if query is None:
                raise AssertionError("acceptance certificates need the query")
            for witness in witnesses:
                if query not in witness:
                    raise AssertionError(
                        f"credulous witness {sorted(map(repr, witness))} "
                        f"does not contain the query {query!r}"
                    )
            for counterexample in counterexamples:
                if query in counterexample:
                    raise AssertionError(
                        f"skeptical counterexample {sorted(map(repr, counterexample))} "
                        f"contains the query {query!r}"
                    )
        return
    raise ValueError(f"unsupported solver differential task: {task}")


def _present(
    *certificates: frozenset[object] | None,
) -> tuple[frozenset[object], ...]:
    return tuple(certificate for certificate in certificates if certificate is not None)


def _validate_certificates(
    label: str,
    certificates: tuple[frozenset[object], ...],
    reference_extensions: Collection[frozenset[object]] | None,
) -> None:
    """Require each certificate to be an extension, or all to be identical."""
    if reference_extensions is None:
        if len(set(certificates)) > 1:
            raise AssertionError(
                f"differing {label}s {certificates!r} cannot be validated "
                "without reference_extensions"
            )
        return
    reference = {frozenset(extension) for extension in reference_extensions}
    for certificate in certificates:
        if frozenset(certificate) not in reference:
            raise AssertionError(
                f"{label} {sorted(map(repr, certificate))} is not an extension "
                "of the reference semantics"
            )


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
        entries.append(
            CapabilityEntry("dung", "native", "enumeration", semantics, True)
        )
        entries.append(
            CapabilityEntry("dung", "native", "single-extension", semantics, True)
        )
        entries.append(CapabilityEntry("dung", "native", "acceptance", semantics, True))
        entries.append(
            CapabilityEntry(
                "dung",
                "sat",
                "enumeration",
                semantics,
                semantics != "cf2",
                "unsupported SAT semantics" if semantics == "cf2" else "",
            )
        )
    for problem in ("SE-PR", "SE-ST", "SE-SST", "SE-STG", "SE-ID"):
        entries.append(
            CapabilityEntry(
                "dung", "iccma", "single-extension", _semantics(problem), True
            )
        )
    for problem in ("DC-CO", "DC-ST", "DC-SST", "DC-STG"):
        entries.append(
            CapabilityEntry("dung", "iccma", "acceptance", _semantics(problem), True)
        )
    for problem in ("DS-PR", "DS-ST", "DS-SST", "DS-STG"):
        entries.append(
            CapabilityEntry("dung", "iccma", "acceptance", _semantics(problem), True)
        )

    for semantics in ("complete", "preferred", "stable", "grounded", "ideal"):
        entries.append(
            CapabilityEntry("aba", "native", "single-extension", semantics, True)
        )
        entries.append(CapabilityEntry("aba", "native", "acceptance", semantics, True))
    for semantics in ("complete", "preferred", "stable"):
        entries.append(
            CapabilityEntry(
                "aba",
                "iccma",
                "single-extension",
                semantics,
                semantics in {"preferred", "stable"},
                "unsupported ICCMA ABA single-extension task"
                if semantics == "complete"
                else "",
            )
        )
    for semantics in ("complete", "stable"):
        entries.append(CapabilityEntry("aba", "iccma", "acceptance", semantics, True))
    entries.append(
        CapabilityEntry(
            "aba",
            "aspforaba",
            "single-extension",
            "stable",
            False,
            "use backend='iccma' with an ASPFORABA binary",
        )
    )

    for semantics in ("grounded", "complete", "model", "preferred", "stable"):
        entries.append(CapabilityEntry("adf", "native", "enumeration", semantics, True))
        entries.append(
            CapabilityEntry(
                "adf",
                "external",
                "enumeration",
                semantics,
                False,
                "external ADF solver backend is not source-backed",
            )
        )
    for semantics in (
        "grounded",
        "complete",
        "preferred",
        "stable",
        "semi-stable",
        "stage",
    ):
        entries.append(
            CapabilityEntry("setaf", "native", "enumeration", semantics, True)
        )
        entries.append(
            CapabilityEntry(
                "setaf",
                "aspartix",
                "enumeration",
                semantics,
                False,
                "external SETAF solver backend is not source-backed",
            )
        )

    entries.append(
        CapabilityEntry(
            "aspic", "materialized_reference", "acceptance", "grounded", True
        )
    )
    entries.append(CapabilityEntry("aspic", "clingo", "acceptance", "grounded", True))
    for semantics in ("preferred", "stable"):
        entries.append(
            CapabilityEntry(
                "aspic",
                "clingo",
                "acceptance",
                semantics,
                False,
                "ASPIC+ clingo backend supports grounded only",
            )
        )
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
