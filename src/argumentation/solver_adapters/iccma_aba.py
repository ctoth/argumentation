"""Subprocess adapter for ICCMA-style flat-ABA solvers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

from argumentation.aba import ABAFramework
from argumentation.aspic import Literal
from argumentation.iccma import write_numeric_aba
from argumentation.solver_results import (
    SolverProcessError,
    SolverProtocolError,
    SolverUnavailable,
)


ACCEPTANCE_TASK_TO_PREFIX = {
    "credulous": "DC",
    "skeptical": "DS",
}

SEMANTICS_TO_CODE = {
    "complete": "CO",
    "preferred": "PR",
    "stable": "ST",
}

SUPPORTED_ABA_PROBLEMS = frozenset(
    {
        "DC-CO",
        "DC-ST",
        "DS-PR",
        "DS-ST",
        "SE-PR",
        "SE-ST",
    }
)


class ICCMAABAOutputKind(Enum):
    """Kinds of ICCMA 2023 ABA solver output supported by this adapter."""

    DECISION = "decision"
    SINGLE_EXTENSION = "single_extension"


class ICCMAABAOutputParseError(ValueError):
    """Raised when ABA solver stdout does not match the selected ICCMA task."""


@dataclass(frozen=True)
class ICCMAABAOutput:
    problem: str
    kind: ICCMAABAOutputKind
    raw_stdout: str
    answer: bool | None = None
    witness: frozenset[Literal] | None = None
    extensions: tuple[frozenset[Literal], ...] = ()
    no_extension: bool = False


@dataclass(frozen=True)
class ICCMAABASolverSuccess:
    backend: str
    problem: str
    output: ICCMAABAOutput
    stdout: str

    @property
    def answer(self) -> bool | None:
        return self.output.answer

    @property
    def witness(self) -> frozenset[Literal] | None:
        return self.output.witness

    @property
    def extensions(self) -> tuple[frozenset[Literal], ...]:
        return self.output.extensions


ICCMAABASolverUnavailable = SolverUnavailable
ICCMAABASolverError = SolverProcessError
ICCMAABASolverProtocolError = SolverProtocolError


ICCMAABASolverResult = (
    ICCMAABASolverSuccess
    | ICCMAABASolverUnavailable
    | ICCMAABASolverError
    | ICCMAABASolverProtocolError
)


def parse_iccma_aba_output(
    problem: str,
    stdout: str,
    *,
    framework: ABAFramework,
    query: Literal | None = None,
) -> ICCMAABAOutput:
    """Parse ICCMA 2023 ABA solver stdout for DC, DS, and SE tasks."""
    prefix = _problem_prefix(problem)
    lines = _semantic_lines(stdout)
    if prefix == "SE":
        return _parse_single_extension_output(problem, stdout, lines, framework)
    if prefix in {"DC", "DS"}:
        if query is None:
            raise ICCMAABAOutputParseError(f"{problem} output parsing requires a query")
        return _parse_decision_output(problem, stdout, lines)
    raise ICCMAABAOutputParseError(f"unsupported ICCMA ABA problem: {problem}")


def solve_aba_extensions(
    framework: ABAFramework,
    *,
    semantics: str,
    binary: str,
    timeout_seconds: float = 30.0,
) -> ICCMAABASolverResult:
    """Invoke an ICCMA ABA solver for a single-extension query."""
    problem = _problem("SE", semantics)
    if not supports_aba_problem("SE", semantics):
        return _unsupported_problem(binary, problem)
    return _run_iccma_aba_solver(
        framework,
        problem=problem,
        binary=binary,
        timeout_seconds=timeout_seconds,
    )


def solve_aba_acceptance(
    framework: ABAFramework,
    *,
    semantics: str,
    task: str,
    query: Literal,
    binary: str,
    timeout_seconds: float = 30.0,
) -> ICCMAABASolverResult:
    """Invoke an ICCMA ABA solver for a credulous or skeptical query."""
    prefix = ACCEPTANCE_TASK_TO_PREFIX.get(task)
    if prefix is None:
        raise ValueError(f"unsupported ICCMA ABA acceptance task: {task}")
    if query not in framework.language:
        raise ValueError(f"query literal is not in framework language: {query!r}")
    problem = _problem(prefix, semantics)
    if not supports_aba_problem(prefix, semantics):
        return _unsupported_problem(binary, problem)
    return _run_iccma_aba_solver(
        framework,
        problem=problem,
        binary=binary,
        timeout_seconds=timeout_seconds,
        query=query,
    )


def supports_aba_problem(task: str, semantics: str) -> bool:
    prefix = ACCEPTANCE_TASK_TO_PREFIX.get(task, task)
    semantics_code = SEMANTICS_TO_CODE.get(semantics)
    return semantics_code is not None and f"{prefix}-{semantics_code}" in SUPPORTED_ABA_PROBLEMS


def _run_iccma_aba_solver(
    framework: ABAFramework,
    *,
    problem: str,
    binary: str,
    timeout_seconds: float,
    query: Literal | None = None,
) -> ICCMAABASolverResult:
    resolved = _resolve_command(binary)
    if resolved is None:
        return ICCMAABASolverUnavailable(
            backend=binary,
            reason="command executable not found on PATH",
            install_hint=(
                "Install an ICCMA-protocol ABA solver and pass its binary path or "
                "command line."
            ),
        )

    path = _write_temp_aba(framework)
    try:
        completed = subprocess.run(
            _command(resolved, problem, path, framework, query),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    finally:
        path.unlink(missing_ok=True)

    if completed.returncode != 0:
        return ICCMAABASolverError(
            backend=binary,
            problem=problem,
            returncode=completed.returncode,
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    try:
        output = parse_iccma_aba_output(
            problem,
            completed.stdout,
            framework=framework,
            query=query,
        )
    except ICCMAABAOutputParseError as exc:
        return ICCMAABASolverProtocolError(
            backend=binary,
            problem=problem,
            message=str(exc),
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    return ICCMAABASolverSuccess(
        backend=binary,
        problem=problem,
        output=output,
        stdout=completed.stdout,
    )


def _parse_single_extension_output(
    problem: str,
    stdout: str,
    lines: list[str],
    framework: ABAFramework,
) -> ICCMAABAOutput:
    if lines == ["NO"]:
        return ICCMAABAOutput(
            problem=problem,
            kind=ICCMAABAOutputKind.SINGLE_EXTENSION,
            raw_stdout=stdout,
            no_extension=True,
        )
    if len(lines) != 1:
        raise ICCMAABAOutputParseError("SE output must be one witness line or NO")
    witness = _parse_witness_line(lines[0], framework)
    return ICCMAABAOutput(
        problem=problem,
        kind=ICCMAABAOutputKind.SINGLE_EXTENSION,
        raw_stdout=stdout,
        witness=witness,
        extensions=(witness,),
    )


def _parse_decision_output(
    problem: str,
    stdout: str,
    lines: list[str],
) -> ICCMAABAOutput:
    if len(lines) != 1 or lines[0] not in {"YES", "NO"}:
        raise ICCMAABAOutputParseError("ABA decision output must be exactly YES or NO")
    return ICCMAABAOutput(
        problem=problem,
        kind=ICCMAABAOutputKind.DECISION,
        raw_stdout=stdout,
        answer=lines[0] == "YES",
    )


def _parse_witness_line(line: str, framework: ABAFramework) -> frozenset[Literal]:
    parts = line.split()
    if not parts or parts[0] != "w":
        raise ICCMAABAOutputParseError(f"invalid witness line: {line!r}")
    witness: set[Literal] = set()
    by_id = _literal_by_id(framework)
    for atom_id in parts[1:]:
        if not atom_id.isdigit() or atom_id not in by_id:
            raise ICCMAABAOutputParseError(f"invalid witness atom in line: {line!r}")
        literal = by_id[atom_id]
        if literal not in framework.assumptions:
            raise ICCMAABAOutputParseError("SE witness must contain only assumptions")
        witness.add(literal)
    return frozenset(witness)


def _command(
    resolved: list[str],
    problem: str,
    path: Path,
    framework: ABAFramework,
    query: Literal | None,
) -> list[str]:
    command = [*resolved, "-p", problem, "-f", str(path)]
    if query is not None:
        command.extend(["-a", _literal_id(framework, query)])
    return command


def _problem(prefix: str, semantics: str) -> str:
    semantics_code = SEMANTICS_TO_CODE.get(semantics)
    if semantics_code is None:
        raise ValueError(f"unsupported ICCMA ABA semantics: {semantics}")
    return f"{prefix}-{semantics_code}"


def _unsupported_problem(binary: str, problem: str) -> ICCMAABASolverUnavailable:
    return ICCMAABASolverUnavailable(
        backend=binary,
        reason=f"unsupported ICCMA 2023 ABA problem: {problem}",
        install_hint="Use an ICCMA 2023 ABA subtrack problem.",
    )


def _resolve_command(binary: str) -> list[str] | None:
    path = Path(binary)
    if path.exists():
        return [str(path)]
    parts = _split_command(binary)
    if not parts:
        return None
    executable = parts[0]
    executable_path = Path(executable)
    resolved = str(executable_path) if executable_path.exists() else shutil.which(executable)
    if resolved is None:
        return None
    return [resolved, *parts[1:]]


def _split_command(command: str) -> list[str]:
    try:
        parts = shlex.split(command, posix=os.name != "nt")
    except ValueError:
        return []
    return [_strip_outer_quotes(part) for part in parts]


def _strip_outer_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _write_temp_aba(framework: ABAFramework) -> Path:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".aba",
        delete=False,
    ) as handle:
        handle.write(write_numeric_aba(framework))
        return Path(handle.name)


def _literal_id(framework: ABAFramework, literal: Literal) -> str:
    ids = {value: atom_id for atom_id, value in _literal_by_id(framework).items()}
    try:
        return ids[literal]
    except KeyError as exc:
        raise ValueError(f"literal is not in framework language: {literal!r}") from exc


def _literal_by_id(framework: ABAFramework) -> dict[str, Literal]:
    return {
        str(index): literal
        for index, literal in enumerate(sorted(framework.language, key=repr), start=1)
    }


def _problem_prefix(problem: str) -> str:
    return problem.split("-", maxsplit=1)[0]


def _semantic_lines(stdout: str) -> list[str]:
    return [
        line.strip()
        for line in stdout.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
