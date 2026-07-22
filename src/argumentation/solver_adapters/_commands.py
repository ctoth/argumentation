"""Shared command-resolution helpers for ICCMA-style subprocess adapters.

These helpers are byte-identical extractions from ``iccma_af.py`` and
``iccma_aba.py`` (confirmed via AST extraction during the B4 dedup refactor).
They resolve a binary/command-line string into an argv prefix, tokenize
command strings with shlex, strip outer quotes from tokens, normalize timeout
stream payloads, and split ICCMA problem/output strings.

Note: ``clingo.py`` has its own, genuinely different ``_resolve_command``
(no shlex tokenization, with a ``sys.executable -m clingo`` fallback) and is
intentionally NOT consolidated here.
"""

from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil


def _resolve_command(binary: str) -> list[str] | None:
    path = Path(binary)
    if path.exists():
        return [str(path)]
    parts = _split_command(binary)
    if not parts:
        return None
    executable = parts[0]
    executable_path = Path(executable)
    resolved = (
        str(executable_path) if executable_path.exists() else shutil.which(executable)
    )
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


def _timeout_stream(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _problem_prefix(problem: str) -> str:
    return problem.split("-", maxsplit=1)[0]


def _semantic_lines(stdout: str) -> list[str]:
    return [
        line.strip()
        for line in stdout.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
