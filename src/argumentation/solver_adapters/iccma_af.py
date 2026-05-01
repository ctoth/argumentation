"""Subprocess adapter for ICCMA-style abstract-AF solvers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import shutil
import subprocess
import tempfile

from argumentation.dung import ArgumentationFramework
from argumentation.iccma import write_af
from argumentation.solver_results import (
    SolverProcessError,
    SolverProtocolError,
    SolverUnavailable,
)


SEMANTICS_TO_PROBLEM = {
    "complete": "SE-CO",
    "grounded": "SE-GR",
    "preferred": "SE-PR",
    "stable": "SE-ST",
    "semi-stable": "SE-SST",
    "stage": "SE-STG",
    "ideal": "SE-ID",
}

ACCEPTANCE_TASK_TO_PREFIX = {
    "credulous": "DC",
    "skeptical": "DS",
}

SEMANTICS_TO_CODE = {
    "complete": "CO",
    "grounded": "GR",
    "preferred": "PR",
    "stable": "ST",
    "semi-stable": "SST",
    "stage": "STG",
    "ideal": "ID",
}


class ICCMAOutputKind(Enum):
    """Kinds of ICCMA 2023 AF solver output supported by this adapter."""

    DECISION = "decision"
    SINGLE_EXTENSION = "single_extension"


class ICCMAOutputParseError(ValueError):
    """Raised when solver stdout does not match the selected ICCMA task."""


@dataclass(frozen=True)
class ICCMAOutput:
    problem: str
    kind: ICCMAOutputKind
    raw_stdout: str
    answer: bool | None = None
    witness: frozenset[str] | None = None
    extensions: tuple[frozenset[str], ...] = ()
    no_extension: bool = False


@dataclass(frozen=True)
class ICCMASolverSuccess:
    backend: str
    problem: str
    output: ICCMAOutput
    stdout: str

    @property
    def answer(self) -> bool | None:
        return self.output.answer

    @property
    def witness(self) -> frozenset[str] | None:
        return self.output.witness

    @property
    def extensions(self) -> tuple[frozenset[str], ...]:
        return self.output.extensions


ICCMASolverUnavailable = SolverUnavailable
ICCMASolverError = SolverProcessError
ICCMASolverProtocolError = SolverProtocolError


ICCMASolverResult = (
    ICCMASolverSuccess
    | ICCMASolverUnavailable
    | ICCMASolverError
    | ICCMASolverProtocolError
)


def parse_extension_witnesses(output: str) -> tuple[frozenset[str], ...]:
    """Parse ICCMA witness lines such as ``w 1 3``."""
    extensions: list[frozenset[str]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[]":
            extensions.append(frozenset())
            continue
        if line.startswith("w"):
            parts = line.split()
            extensions.append(frozenset(parts[1:]))
    return tuple(extensions)


def parse_iccma_output(
    problem: str,
    stdout: str,
    *,
    query: str | None = None,
    certificate_required: bool = True,
) -> ICCMAOutput:
    """Parse ICCMA 2023 AF solver stdout for DC, DS, and SE tasks."""
    prefix = _problem_prefix(problem)
    lines = _semantic_lines(stdout)
    if prefix == "SE":
        return _parse_single_extension_output(problem, stdout, lines)
    if prefix in {"DC", "DS"}:
        if query is None:
            raise ICCMAOutputParseError(f"{problem} output parsing requires a query")
        return _parse_decision_output(
            problem,
            stdout,
            lines,
            query=query,
            certificate_required=certificate_required,
        )
    raise ICCMAOutputParseError(f"unsupported ICCMA AF problem: {problem}")


def solve_af_extensions(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    binary: str,
    timeout_seconds: float = 30.0,
) -> ICCMASolverResult:
    """Invoke an ICCMA AF solver for a single-extension query."""
    problem = SEMANTICS_TO_PROBLEM.get(semantics)
    if problem is None:
        raise ValueError(f"unsupported ICCMA AF semantics: {semantics}")

    return _run_iccma_af_solver(
        framework,
        problem=problem,
        binary=binary,
        timeout_seconds=timeout_seconds,
    )


def solve_af_acceptance(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    task: str,
    query: str,
    binary: str,
    timeout_seconds: float = 30.0,
    certificate_required: bool = True,
) -> ICCMASolverResult:
    """Invoke an ICCMA AF solver for a credulous or skeptical query."""
    prefix = ACCEPTANCE_TASK_TO_PREFIX.get(task)
    if prefix is None:
        raise ValueError(f"unsupported ICCMA AF acceptance task: {task}")
    semantics_code = SEMANTICS_TO_CODE.get(semantics)
    if semantics_code is None:
        raise ValueError(f"unsupported ICCMA AF semantics: {semantics}")
    if query not in framework.arguments:
        raise ValueError(f"query argument is not in framework: {query!r}")

    return _run_iccma_af_solver(
        framework,
        problem=f"{prefix}-{semantics_code}",
        binary=binary,
        timeout_seconds=timeout_seconds,
        query=query,
        certificate_required=certificate_required,
    )


def _run_iccma_af_solver(
    framework: ArgumentationFramework,
    *,
    problem: str,
    binary: str,
    timeout_seconds: float,
    query: str | None = None,
    certificate_required: bool = True,
) -> ICCMASolverResult:
    resolved = _resolve_binary(binary)
    if resolved is None:
        return ICCMASolverUnavailable(
            backend=binary,
            reason="binary not found on PATH",
            install_hint="Install an ICCMA-protocol AF solver and pass its binary path.",
        )

    path = _write_temp_af(framework)
    try:
        completed = subprocess.run(
            _command(resolved, problem, path, query),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    finally:
        path.unlink(missing_ok=True)

    if completed.returncode != 0:
        return ICCMASolverError(
            backend=binary,
            problem=problem,
            returncode=completed.returncode,
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    try:
        output = parse_iccma_output(
            problem,
            completed.stdout,
            query=query,
            certificate_required=certificate_required,
        )
    except ICCMAOutputParseError as exc:
        return ICCMASolverProtocolError(
            backend=binary,
            problem=problem,
            message=str(exc),
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    return ICCMASolverSuccess(
        backend=binary,
        problem=problem,
        output=output,
        stdout=completed.stdout,
    )


def _command(resolved: str, problem: str, path: Path, query: str | None) -> list[str]:
    command = [resolved, "-p", problem, "-f", str(path)]
    if query is not None:
        command.extend(["-a", query])
    return command


def _resolve_binary(binary: str) -> str | None:
    path = Path(binary)
    if path.exists():
        return str(path)
    return shutil.which(binary)


def _write_temp_af(framework: ArgumentationFramework) -> Path:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".af",
        delete=False,
    ) as handle:
        handle.write(write_af(framework))
        return Path(handle.name)


def _problem_prefix(problem: str) -> str:
    return problem.split("-", maxsplit=1)[0]


def _semantic_lines(stdout: str) -> list[str]:
    return [
        line.strip()
        for line in stdout.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _parse_single_extension_output(
    problem: str,
    stdout: str,
    lines: list[str],
) -> ICCMAOutput:
    if lines == ["NO"]:
        return ICCMAOutput(
            problem=problem,
            kind=ICCMAOutputKind.SINGLE_EXTENSION,
            raw_stdout=stdout,
            no_extension=True,
        )
    if len(lines) != 1:
        raise ICCMAOutputParseError("SE output must be one witness line or NO")
    witness = _parse_witness_line(lines[0])
    return ICCMAOutput(
        problem=problem,
        kind=ICCMAOutputKind.SINGLE_EXTENSION,
        raw_stdout=stdout,
        witness=witness,
        extensions=(witness,),
    )


def _parse_decision_output(
    problem: str,
    stdout: str,
    lines: list[str],
    *,
    query: str,
    certificate_required: bool,
) -> ICCMAOutput:
    if not lines or lines[0] not in {"YES", "NO"}:
        raise ICCMAOutputParseError("decision output must start with YES or NO")
    if not certificate_required:
        if len(lines) != 1:
            raise ICCMAOutputParseError("non-certificate decision output must be YES or NO")
        return ICCMAOutput(
            problem=problem,
            kind=ICCMAOutputKind.DECISION,
            raw_stdout=stdout,
            answer=lines[0] == "YES",
        )

    prefix = _problem_prefix(problem)
    if prefix == "DC":
        return _parse_credulous_decision(problem, stdout, lines, query)
    if prefix == "DS":
        return _parse_skeptical_decision(problem, stdout, lines, query)
    raise ICCMAOutputParseError(f"unsupported decision problem: {problem}")


def _parse_credulous_decision(
    problem: str,
    stdout: str,
    lines: list[str],
    query: str,
) -> ICCMAOutput:
    if lines[0] == "NO":
        if len(lines) != 1:
            raise ICCMAOutputParseError("DC NO output must not include a witness")
        return ICCMAOutput(
            problem=problem,
            kind=ICCMAOutputKind.DECISION,
            raw_stdout=stdout,
            answer=False,
        )
    if len(lines) != 2:
        raise ICCMAOutputParseError("DC YES output must include one witness")
    witness = _parse_witness_line(lines[1])
    if query not in witness:
        raise ICCMAOutputParseError("DC YES witness must contain query")
    return ICCMAOutput(
        problem=problem,
        kind=ICCMAOutputKind.DECISION,
        raw_stdout=stdout,
        answer=True,
        witness=witness,
        extensions=(witness,),
    )


def _parse_skeptical_decision(
    problem: str,
    stdout: str,
    lines: list[str],
    query: str,
) -> ICCMAOutput:
    if lines[0] == "YES":
        if len(lines) != 1:
            raise ICCMAOutputParseError("DS YES output must not include a witness")
        return ICCMAOutput(
            problem=problem,
            kind=ICCMAOutputKind.DECISION,
            raw_stdout=stdout,
            answer=True,
        )
    if len(lines) != 2:
        raise ICCMAOutputParseError("DS NO output must include one counterexample")
    witness = _parse_witness_line(lines[1])
    if query in witness:
        raise ICCMAOutputParseError("DS NO counterexample must omit query")
    return ICCMAOutput(
        problem=problem,
        kind=ICCMAOutputKind.DECISION,
        raw_stdout=stdout,
        answer=False,
        witness=witness,
        extensions=(witness,),
    )


def _parse_witness_line(line: str) -> frozenset[str]:
    parts = line.split()
    if not parts or parts[0] != "w":
        raise ICCMAOutputParseError(f"invalid witness line: {line!r}")
    witness = parts[1:]
    if not all(argument.isdigit() for argument in witness):
        raise ICCMAOutputParseError(f"invalid witness argument in line: {line!r}")
    return frozenset(witness)
