"""Subprocess helper for clingo-backed ASP-style solver protocols."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from argumentation.core.solver_results import (
    SolverProcessError,
    SolverProtocolError,
    SolverUnavailable,
)
from argumentation.solver_adapters._commands import _timeout_stream


# Clasp exit codes are result bits: 10 SAT, 20 search exhausted, 30 both;
# ``python -m clingo`` exits 0. Other codes (interrupt, memory, error) fail.
_COMPLETED_RETURNCODES = frozenset({0, 10, 20, 30})
_ACCEPTED_ARG_RE = re.compile(r"^accepted_arg\((?P<id>[A-Za-z_][A-Za-z0-9_]*)\)$")
_ACCEPTED_LIT_RE = re.compile(r"^accepted_lit\((?P<id>[A-Za-z_][A-Za-z0-9_]*)\)$")
_CLINGO_CONTROL_TOKENS = {
    "Answer:",
    "SATISFIABLE",
    "UNSATISFIABLE",
    "UNKNOWN",
    "OPTIMUM",
    "FOUND",
    "Models",
    "Calls",
    "Time",
    "CPU",
}


@dataclass(frozen=True)
class ClingoAnswerSetSuccess:
    backend: str
    accepted_argument_ids: frozenset[str]
    accepted_literal_ids: frozenset[str]
    stdout: str


@dataclass(frozen=True)
class ClingoExtensionEnumerationSuccess:
    backend: str
    extensions: tuple[frozenset[str], ...]
    extension_literal_ids: tuple[frozenset[str], ...]
    stdout: str


ClingoUnavailable = SolverUnavailable
ClingoProcessError = SolverProcessError
ClingoProtocolError = SolverProtocolError


ClingoResult = (
    ClingoAnswerSetSuccess
    | ClingoExtensionEnumerationSuccess
    | ClingoUnavailable
    | ClingoProcessError
    | ClingoProtocolError
)
ClingoExtensionEnumerationResult = (
    ClingoExtensionEnumerationSuccess
    | ClingoUnavailable
    | ClingoProcessError
    | ClingoProtocolError
)
ClingoAnswerSetResult = (
    ClingoAnswerSetSuccess
    | ClingoUnavailable
    | ClingoProcessError
    | ClingoProtocolError
)


def run_extension_enumeration_protocol(
    *,
    facts: tuple[str, ...],
    encoding_modules: tuple[str, ...],
    known_argument_ids: frozenset[str],
    known_literal_ids: frozenset[str] = frozenset(),
    binary: str,
    timeout_seconds: float = 30.0,
    problem: str = "ASP-EXT",
) -> ClingoExtensionEnumerationResult:
    """Run clingo over facts plus packaged modules and parse all extensions."""
    command_prefix = _resolve_command(binary)
    if command_prefix is None:
        return ClingoUnavailable(
            backend=binary,
            reason="binary not found on PATH",
            install_hint="Install clingo or pass binary=... to the backend solver.",
        )

    try:
        modules = tuple(_read_encoding_module(module) for module in encoding_modules)
    except FileNotFoundError as exc:
        return ClingoProtocolError(
            backend=binary,
            problem=problem,
            message=f"packaged encoding module not found: {exc.filename}",
            stderr="",
            stdout="",
        )

    path = _write_temp_program(facts, modules=modules)
    try:
        completed = subprocess.run(
            [*command_prefix, str(path), "0"],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _timeout_error(binary, problem, exc)
    finally:
        path.unlink(missing_ok=True)

    if completed.returncode not in _COMPLETED_RETURNCODES:
        return ClingoProcessError(
            backend=binary,
            problem=problem,
            returncode=completed.returncode,
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    try:
        _require_completed_search(completed, require_exhausted=True)
        extensions, extension_literal_ids = _parse_extension_answer_sets(
            completed.stdout,
            known_argument_ids=known_argument_ids,
            known_literal_ids=known_literal_ids,
        )
    except ValueError as exc:
        return ClingoProtocolError(
            backend=binary,
            problem=problem,
            message=str(exc),
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    return ClingoExtensionEnumerationSuccess(
        backend=binary,
        extensions=extensions,
        extension_literal_ids=extension_literal_ids,
        stdout=completed.stdout,
    )


def run_aspic_grounded_protocol(
    *,
    facts: tuple[str, ...],
    known_literal_ids: frozenset[str],
    binary: str,
    timeout_seconds: float = 30.0,
) -> ClingoAnswerSetResult:
    """Run clingo and parse ASPIC grounded accepted-atom protocol output."""
    command_prefix = _resolve_command(binary)
    if command_prefix is None:
        return ClingoUnavailable(
            backend=binary,
            reason="binary not found on PATH",
            install_hint="Install clingo or pass binary=... to solve_aspic_with_backend.",
        )

    path = _write_temp_program(facts)
    try:
        completed = subprocess.run(
            [*command_prefix, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _timeout_error(binary, "ASPIC-GR", exc)
    finally:
        path.unlink(missing_ok=True)

    if completed.returncode not in _COMPLETED_RETURNCODES:
        return ClingoProcessError(
            backend=binary,
            problem="ASPIC-GR",
            returncode=completed.returncode,
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    try:
        _require_completed_search(completed, require_exhausted=False)
        accepted_argument_ids, accepted_literal_ids = _parse_grounded_answer_set(
            completed.stdout,
            known_literal_ids=known_literal_ids,
        )
    except ValueError as exc:
        return ClingoProtocolError(
            backend=binary,
            problem="ASPIC-GR",
            message=str(exc),
            stderr=completed.stderr,
            stdout=completed.stdout,
        )

    return ClingoAnswerSetSuccess(
        backend=binary,
        accepted_argument_ids=accepted_argument_ids,
        accepted_literal_ids=accepted_literal_ids,
        stdout=completed.stdout,
    )


def _timeout_error(
    binary: str, problem: str, exc: subprocess.TimeoutExpired
) -> SolverProcessError:
    """Report a timed-out run like the ICCMA adapters: code -1, partial streams."""
    return ClingoProcessError(
        backend=binary,
        problem=problem,
        returncode=-1,
        stderr=_timeout_stream(exc.stderr),
        stdout=_timeout_stream(exc.stdout),
    )


_COMPLETED_STATUSES = frozenset({"SATISFIABLE", "UNSATISFIABLE", "OPTIMUM FOUND"})
_STATUS_LINES = _COMPLETED_STATUSES | {"UNKNOWN"}


def _require_completed_search(
    completed: subprocess.CompletedProcess[str],
    *,
    require_exhausted: bool,
) -> None:
    """Raise ``ValueError`` unless clingo reported a completed search.

    The final status line must be SATISFIABLE, UNSATISFIABLE or OPTIMUM
    FOUND; UNKNOWN, empty or truncated output is not a result. When all
    models are required, native exit code 10 (SAT without the exhaustion
    bit) means the enumeration stopped early.
    """
    statuses = [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.strip() in _STATUS_LINES
    ]
    if not statuses:
        raise ValueError("clingo output has no solver status (empty or truncated)")
    if statuses[-1] not in _COMPLETED_STATUSES:
        raise ValueError(f"clingo search did not complete: {statuses[-1]}")
    if require_exhausted and completed.returncode == 10:
        raise ValueError("clingo stopped before exhausting the model enumeration")


def _parse_grounded_answer_set(
    stdout: str,
    *,
    known_literal_ids: frozenset[str],
) -> tuple[frozenset[str], frozenset[str]]:
    accepted_argument_ids: set[str] = set()
    accepted_literal_ids: set[str] = set()
    for token in stdout.split():
        if token.isdigit() or token in _CLINGO_CONTROL_TOKENS:
            continue
        arg_match = _ACCEPTED_ARG_RE.fullmatch(token)
        if arg_match is not None:
            accepted_argument_ids.add(arg_match.group("id"))
            continue
        lit_match = _ACCEPTED_LIT_RE.fullmatch(token)
        if lit_match is not None:
            literal_id = lit_match.group("id")
            if literal_id not in known_literal_ids:
                raise ValueError("accepted literal id is not in the ASPIC encoding")
            accepted_literal_ids.add(literal_id)
            continue
    return frozenset(accepted_argument_ids), frozenset(accepted_literal_ids)


def _parse_extension_answer_sets(
    stdout: str,
    *,
    known_argument_ids: frozenset[str],
    known_literal_ids: frozenset[str],
) -> tuple[tuple[frozenset[str], ...], tuple[frozenset[str], ...]]:
    answer_sets: list[tuple[frozenset[str], frozenset[str]]] = []
    current_args: set[str] | None = None
    current_lits: set[str] | None = None

    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("Answer:"):
            if current_args is not None and current_lits is not None:
                answer_sets.append((frozenset(current_args), frozenset(current_lits)))
            current_args = set()
            current_lits = set()
            continue
        if current_args is None or current_lits is None:
            continue
        if not stripped:
            continue
        if stripped in _CLINGO_CONTROL_TOKENS or stripped.startswith("Optimization:"):
            answer_sets.append((frozenset(current_args), frozenset(current_lits)))
            current_args = None
            current_lits = None
            continue
        for token in stripped.split():
            arg_match = _ACCEPTED_ARG_RE.fullmatch(token)
            if arg_match is not None:
                argument_id = arg_match.group("id")
                if argument_id not in known_argument_ids:
                    raise ValueError("accepted argument id is not in the encoding")
                current_args.add(argument_id)
                continue
            lit_match = _ACCEPTED_LIT_RE.fullmatch(token)
            if lit_match is not None:
                literal_id = lit_match.group("id")
                if known_literal_ids and literal_id not in known_literal_ids:
                    raise ValueError("accepted literal id is not in the encoding")
                current_lits.add(literal_id)
                continue
            if token not in _CLINGO_CONTROL_TOKENS and not token.isdigit():
                raise ValueError(f"unexpected clingo output token: {token}")

    if current_args is not None and current_lits is not None:
        answer_sets.append((frozenset(current_args), frozenset(current_lits)))

    answer_sets = sorted(
        set(answer_sets),
        key=lambda item: (len(item[0]), tuple(sorted(item[0])), tuple(sorted(item[1]))),
    )
    return (
        tuple(extension for extension, _literal_ids in answer_sets),
        tuple(literal_ids for _extension, literal_ids in answer_sets),
    )


def _resolve_command(binary: str) -> list[str] | None:
    path = Path(binary)
    if path.exists():
        return [str(path)]
    resolved = shutil.which(binary)
    if resolved is not None:
        return [resolved]
    if binary == "clingo" and importlib.util.find_spec("clingo") is not None:
        return [sys.executable, "-m", "clingo"]
    return None


def _read_encoding_module(name: str) -> str:
    return (
        resources.files("argumentation")
        .joinpath("encodings", name)
        .read_text(encoding="utf-8")
    )


def _write_temp_program(
    facts: tuple[str, ...],
    *,
    modules: tuple[str, ...] = (),
) -> Path:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".lp",
        delete=False,
    ) as handle:
        for module in modules:
            handle.write(module)
            if not module.endswith("\n"):
                handle.write("\n")
        for fact in facts:
            handle.write(fact)
            handle.write("\n")
        return Path(handle.name)
