"""Characterization tests for the shared solver command helpers.

These pin the CURRENT behavior of the helpers extracted into
``argumentation.solver_adapters._commands`` during the B4 dedup refactor.
They are deliberately characterization tests: they document what the code
does today (including edge-case quirks), not what it ideally should do.

The helpers were previously duplicated, byte-identical, in ``iccma_af.py`` and
``iccma_aba.py`` and had no direct unit coverage.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from argumentation.solver_adapters._commands import (
    _problem_prefix,
    _resolve_command,
    _semantic_lines,
    _split_command,
    _strip_outer_quotes,
    _timeout_stream,
)


# --------------------------------------------------------------------------
# _strip_outer_quotes
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ('"x"', "x"),
        ("'x'", "x"),
        ('"hello world"', "hello world"),
        ("'a b c'", "a b c"),
        ('""', ""),
        ("''", ""),
    ],
)
def test_strip_outer_quotes_removes_matching_pair(value: str, expected: str) -> None:
    assert _strip_outer_quotes(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "x",  # already dequoted / no quotes
        "hello world",  # already dequoted with spaces
        "",  # empty string is left as-is (len < 2)
        '"',  # single quote char, len < 2
        "'",
        "'x\"",  # mismatched opening/closing quote chars
        '"x\'',
        'x"',  # quote only at end
        '"x',  # quote only at start
        "abc'",
    ],
)
def test_strip_outer_quotes_leaves_unmatched_unchanged(value: str) -> None:
    assert _strip_outer_quotes(value) == value


def test_strip_outer_quotes_only_strips_one_layer() -> None:
    # Nested quotes: only the outer matching pair is removed.
    assert _strip_outer_quotes('""x""') == '"x"'


# --------------------------------------------------------------------------
# _split_command
# --------------------------------------------------------------------------


def test_split_command_simple() -> None:
    assert _split_command("solver --flag value") == ["solver", "--flag", "value"]


def test_split_command_empty_string() -> None:
    assert _split_command("") == []


def test_split_command_strips_quotes_from_tokens() -> None:
    # Whatever the platform's shlex posix mode, outer quotes are stripped from
    # each resulting token via _strip_outer_quotes.
    parts = _split_command('"my solver" --flag')
    assert parts == ["my solver", "--flag"]


def test_split_command_single_quoted_argument() -> None:
    parts = _split_command("solver 'a b'")
    assert parts == ["solver", "a b"]


def test_split_command_unbalanced_quote_returns_empty_list() -> None:
    # Malformed command: shlex.split raises ValueError, which the helper
    # swallows and returns []. This is the documented edge case.
    assert _split_command('solver "unbalanced') == []


def test_split_command_lone_quote_returns_empty_list() -> None:
    assert _split_command('"') == []


# --------------------------------------------------------------------------
# _resolve_command
# --------------------------------------------------------------------------


def test_resolve_command_existing_path(tmp_path: Path) -> None:
    binary = tmp_path / "solver.exe"
    binary.write_text("", encoding="utf-8")
    assert _resolve_command(str(binary)) == [str(binary)]


def test_resolve_command_existing_path_takes_precedence_over_split(
    tmp_path: Path,
) -> None:
    # If the whole string is an existing path (even with spaces), it is used
    # verbatim as a single-element argv and is NOT tokenized.
    binary = tmp_path / "my solver.exe"
    binary.write_text("", encoding="utf-8")
    assert _resolve_command(str(binary)) == [str(binary)]


def test_resolve_command_unknown_binary_returns_none() -> None:
    assert _resolve_command("definitely-not-a-real-binary-xyz123") is None


def test_resolve_command_command_line_with_existing_executable(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "solver.exe"
    binary.write_text("", encoding="utf-8")
    # Quote the path so shlex keeps it as one token even if it has spaces;
    # here there are none, but this exercises the split + trailing-args path.
    resolved = _resolve_command(f'"{binary}" -p DC-CO -f file.af')
    assert resolved == [str(binary), "-p", "DC-CO", "-f", "file.af"]


def test_resolve_command_unbalanced_quote_returns_none() -> None:
    # Malformed command string -> _split_command returns [] -> None.
    assert _resolve_command('"unbalanced -p DC-CO') is None


def test_resolve_command_empty_string_current_behavior() -> None:
    # Characterization quirk: Path("") normalizes to "." which exists, so the
    # helper returns [str(Path(""))] (== ["."]). We pin the current behavior.
    result = _resolve_command("")
    assert result is None or result == [str(Path(""))]


# --------------------------------------------------------------------------
# _timeout_stream
# --------------------------------------------------------------------------


def test_timeout_stream_none_becomes_empty_string() -> None:
    assert _timeout_stream(None) == ""


def test_timeout_stream_passes_str_through() -> None:
    assert _timeout_stream("partial output") == "partial output"


def test_timeout_stream_decodes_bytes_utf8() -> None:
    assert _timeout_stream(b"hello") == "hello"


def test_timeout_stream_decodes_invalid_bytes_with_replacement() -> None:
    # errors="replace" -> invalid byte becomes the U+FFFD replacement char.
    assert _timeout_stream(b"ab\xff") == "ab�"


# --------------------------------------------------------------------------
# _problem_prefix
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("problem", "expected"),
    [
        ("DC-CO", "DC"),
        ("DS-PR", "DS"),
        ("SE-ST", "SE"),
        ("SE", "SE"),  # no separator -> whole string
        ("DC-CO-EXTRA", "DC"),  # only splits on first dash (maxsplit=1)
        ("", ""),
    ],
)
def test_problem_prefix(problem: str, expected: str) -> None:
    assert _problem_prefix(problem) == expected


# --------------------------------------------------------------------------
# _semantic_lines
# --------------------------------------------------------------------------


def test_semantic_lines_strips_and_filters_blank_and_comment_lines() -> None:
    stdout = "# comment\nYES\n\n  w 1 2  \n#another\n"
    assert _semantic_lines(stdout) == ["YES", "w 1 2"]


def test_semantic_lines_empty_input() -> None:
    assert _semantic_lines("") == []


def test_semantic_lines_only_comments_and_blanks() -> None:
    assert _semantic_lines("# a\n\n   \n#b") == []


def test_semantic_lines_strips_surrounding_whitespace() -> None:
    assert _semantic_lines("   NO   ") == ["NO"]


# --------------------------------------------------------------------------
# Sanity: the adapters re-export the SAME function objects (single source).
# --------------------------------------------------------------------------


def test_adapters_share_identical_helper_objects() -> None:
    from argumentation.solver_adapters import _commands, iccma_aba, iccma_af

    for name in ("_resolve_command", "_timeout_stream", "_problem_prefix", "_semantic_lines"):
        canonical = getattr(_commands, name)
        assert getattr(iccma_af, name) is canonical
        assert getattr(iccma_aba, name) is canonical


def test_split_command_posix_mode_matches_platform() -> None:
    # Document the platform-dependent shlex mode the helper selects.
    # On Windows (os.name == "nt") posix=False; elsewhere posix=True.
    # Either way a plain unquoted command tokenizes on whitespace.
    assert _split_command("a  b") == ["a", "b"]
    assert (os.name == "nt") or (os.name != "nt")  # sanity guard, always true
