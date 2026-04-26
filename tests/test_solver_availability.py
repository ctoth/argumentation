from __future__ import annotations

import importlib.util

from argumentation.dung import ArgumentationFramework
from argumentation.solver import (
    ExtensionSolverSuccess,
    SolverBackendUnavailable,
    solve_dung_extensions,
)


def test_solve_dung_extensions_returns_extensions_for_available_brute_backend() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    result = solve_dung_extensions(framework, semantics="stable", backend="brute")

    assert isinstance(result, ExtensionSolverSuccess)
    assert result.extensions == (frozenset({"a"}),)


def test_solve_dung_extensions_reports_missing_z3_as_typed_result(monkeypatch) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str):
        if name == "z3":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    framework = ArgumentationFramework(arguments=frozenset(), defeats=frozenset())

    result = solve_dung_extensions(framework, semantics="stable", backend="z3")

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "z3"
    assert "formal-argumentation[z3]" in result.install_hint
