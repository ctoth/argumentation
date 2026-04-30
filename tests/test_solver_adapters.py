from __future__ import annotations

from types import SimpleNamespace

from argumentation.dung import ArgumentationFramework
from argumentation.solver_adapters.iccma_af import (
    ICCMASolverError,
    ICCMASolverSuccess,
    ICCMASolverUnavailable,
    parse_extension_witnesses,
    solve_af_extensions,
)


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_parse_iccma_witness_output() -> None:
    assert parse_extension_witnesses("w 1 3\nw 2\n") == (
        frozenset({"1", "3"}),
        frozenset({"2"}),
    )


def test_iccma_af_adapter_invokes_custom_binary(monkeypatch) -> None:
    framework = af({"1", "2"}, {("1", "2")})
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )

    def fake_run(command, *, capture_output, text, timeout, check):
        calls.append(command)
        assert capture_output is True
        assert text is True
        assert timeout == 5.0
        assert check is False
        input_path = command[-1]
        assert input_path.endswith(".apx")
        return SimpleNamespace(returncode=0, stdout="w 1\n", stderr="")

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.subprocess.run",
        fake_run,
    )

    result = solve_af_extensions(
        framework,
        semantics="stable",
        binary="fake-iccma-solver",
        timeout_seconds=5.0,
    )

    assert isinstance(result, ICCMASolverSuccess)
    assert result.extensions == (frozenset({"1"}),)
    assert calls and calls[0][:2] == ["fake-iccma-solver", "SE-ST"]


def test_iccma_af_adapter_reports_missing_binary(monkeypatch) -> None:
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: None,
    )

    result = solve_af_extensions(
        af({"1"}, set()),
        semantics="grounded",
        binary="missing-solver",
    )

    assert isinstance(result, ICCMASolverUnavailable)
    assert result.backend == "missing-solver"


def test_iccma_af_adapter_reports_solver_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="bad input"),
    )

    result = solve_af_extensions(
        af({"1"}, set()),
        semantics="stable",
        binary="fake-iccma-solver",
    )

    assert isinstance(result, ICCMASolverError)
    assert result.returncode == 2
    assert result.stderr == "bad input"
