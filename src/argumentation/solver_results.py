"""Shared solver result types."""

from __future__ import annotations

from dataclasses import dataclass


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


@dataclass(frozen=True)
class SolverProtocolError:
    backend: str
    problem: str
    message: str
    stderr: str
    stdout: str


@dataclass(frozen=True)
class ExtensionEnumerationSuccess:
    extensions: tuple[frozenset[str], ...]


@dataclass(frozen=True)
class SingleExtensionSuccess:
    extension: frozenset[str] | None


@dataclass(frozen=True)
class AcceptanceSuccess:
    answer: bool
    witness: frozenset[str] | None = None
    counterexample: frozenset[str] | None = None
