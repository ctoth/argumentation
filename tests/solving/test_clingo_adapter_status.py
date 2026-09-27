"""Transport-boundary contracts for the clingo subprocess adapter.

Clingo/clasp exit codes are result bits (https://github.com/potassco/clasp#exit-codes):
10 = SAT, 20 = search exhausted (UNSAT when alone), 30 = SAT and exhausted;
``python -m clingo`` exits 0. These tests replace ``subprocess.run`` and never
start a solver.
"""

from __future__ import annotations

from collections.abc import Callable
from subprocess import CompletedProcess
from typing import Any

import pytest

import argumentation.solver_adapters.clingo as clingo


def _fake_run(returncode: int, stdout: str) -> Callable[..., CompletedProcess[str]]:
    calls = 0

    def run(command: list[str], **_kwargs: Any) -> CompletedProcess[str]:
        nonlocal calls
        calls += 1
        assert calls == 1, "adapter must make exactly one process call"
        return CompletedProcess(command, returncode, stdout, "")

    return run


@pytest.fixture
def fake_clingo(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[int, str], None]:
    monkeypatch.setattr(clingo, "_resolve_command", lambda _binary: ["clingo"])

    def install(returncode: int, stdout: str) -> None:
        monkeypatch.setattr(clingo.subprocess, "run", _fake_run(returncode, stdout))

    return install


def _enumerate(known: frozenset[str] = frozenset({"a"})) -> object:
    return clingo.run_extension_enumeration_protocol(
        facts=(),
        encoding_modules=(),
        known_argument_ids=known,
        binary="clingo",
    )


def _grounded() -> object:
    return clingo.run_aspic_grounded_protocol(
        facts=(), known_literal_ids=frozenset(), binary="clingo"
    )


@pytest.mark.parametrize("returncode", [10, 30])
def test_native_satisfiable_exit_codes_are_success(
    fake_clingo: Callable[[int, str], None], returncode: int
) -> None:
    fake_clingo(returncode, "Answer: 1\naccepted_arg(a)\nSATISFIABLE\n")

    result = _grounded()

    assert isinstance(result, clingo.ClingoAnswerSetSuccess)
    assert result.accepted_argument_ids == frozenset({"a"})


def test_native_exhausted_enumeration_exit_code_is_success(
    fake_clingo: Callable[[int, str], None],
) -> None:
    fake_clingo(30, "Answer: 1\naccepted_arg(a)\nSATISFIABLE\n")

    result = _enumerate()

    assert isinstance(result, clingo.ClingoExtensionEnumerationSuccess)
    assert result.extensions == (frozenset({"a"}),)


def test_native_unsatisfiable_exit_code_is_a_completed_empty_enumeration(
    fake_clingo: Callable[[int, str], None],
) -> None:
    fake_clingo(20, "UNSATISFIABLE\n")

    result = _enumerate()

    assert isinstance(result, clingo.ClingoExtensionEnumerationSuccess)
    assert result.extensions == ()


def test_python_module_zero_exit_code_control(
    fake_clingo: Callable[[int, str], None],
) -> None:
    fake_clingo(0, "Answer: 1\naccepted_arg(a)\nSATISFIABLE\n")

    result = _enumerate()

    assert isinstance(result, clingo.ClingoExtensionEnumerationSuccess)
    assert result.extensions == (frozenset({"a"}),)


@pytest.mark.parametrize("returncode", [1, 11, 33, 65, 128])
def test_error_and_interrupt_exit_codes_remain_process_errors(
    fake_clingo: Callable[[int, str], None], returncode: int
) -> None:
    fake_clingo(returncode, "Answer: 1\naccepted_arg(a)\nSATISFIABLE\n")

    result = _enumerate()

    assert isinstance(result, clingo.ClingoProcessError)
    assert result.returncode == returncode
