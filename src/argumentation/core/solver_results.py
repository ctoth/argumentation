"""Shared solver result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SolverUnavailable:
    backend: str
    reason: str
    install_hint: str


@dataclass(frozen=True)
class SolverProcessError:
    backend: str
    problem: str
    returncode: int
    stderr: str
    stdout: str

    @property
    def reason(self) -> str:
        return f"solver exited with code {self.returncode}"

    @property
    def details(self) -> dict[str, str]:
        return {
            "problem": self.problem,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(frozen=True)
class SolverProtocolError:
    backend: str
    problem: str
    message: str
    stderr: str
    stdout: str

    @property
    def reason(self) -> str:
        return self.message

    @property
    def details(self) -> dict[str, str]:
        return {
            "problem": self.problem,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(frozen=True)
class SolverTimeout:
    backend: str
    problem: str
    message: str
    metadata: dict[str, Any] | None = None

    @property
    def reason(self) -> str:
        return self.message


@dataclass(frozen=True)
class ExtensionEnumerationSuccess:
    extensions: tuple[frozenset[object], ...]
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class SingleExtensionSuccess:
    extension: frozenset[object] | None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AcceptanceSuccess:
    answer: bool
    witness: frozenset[object] | None = None
    counterexample: frozenset[object] | None = None
    metadata: dict[str, Any] | None = None
