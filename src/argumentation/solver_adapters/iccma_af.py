"""Subprocess adapter for ICCMA-style abstract-AF solvers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile

from argumentation.dung import ArgumentationFramework
from argumentation.iccma import write_af


SEMANTICS_TO_PROBLEM = {
    "complete": "SE-CO",
    "grounded": "SE-GR",
    "preferred": "SE-PR",
    "stable": "SE-ST",
    "semi-stable": "SE-SST",
    "stage": "SE-STG",
    "ideal": "SE-ID",
}


@dataclass(frozen=True)
class ICCMASolverSuccess:
    backend: str
    problem: str
    extensions: tuple[frozenset[str], ...]
    stdout: str


@dataclass(frozen=True)
class ICCMASolverUnavailable:
    backend: str
    reason: str
    install_hint: str


@dataclass(frozen=True)
class ICCMASolverError:
    backend: str
    problem: str
    returncode: int
    stderr: str
    stdout: str


ICCMASolverResult = ICCMASolverSuccess | ICCMASolverUnavailable | ICCMASolverError


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
            [resolved, problem, str(path)],
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

    return ICCMASolverSuccess(
        backend=binary,
        problem=problem,
        extensions=parse_extension_witnesses(completed.stdout),
        stdout=completed.stdout,
    )


def _resolve_binary(binary: str) -> str | None:
    path = Path(binary)
    if path.exists():
        return str(path)
    return shutil.which(binary)


def _write_temp_af(framework: ArgumentationFramework) -> Path:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".apx",
        delete=False,
    ) as handle:
        handle.write(write_af(framework))
        return Path(handle.name)
