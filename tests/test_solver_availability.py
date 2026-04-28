from argumentation.dung import ArgumentationFramework
from argumentation.solver import (
    ExtensionSolverSuccess,
    SolverBackendUnavailable,
    solve_dung_extensions,
)


def test_solve_dung_extensions_returns_extensions_for_single_labelling_backend() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    result = solve_dung_extensions(framework, semantics="stable")

    assert isinstance(result, ExtensionSolverSuccess)
    assert result.extensions == (frozenset({"a"}),)


def test_solve_dung_extensions_rejects_deleted_z3_backend() -> None:
    framework = ArgumentationFramework(arguments=frozenset(), defeats=frozenset())

    result = solve_dung_extensions(framework, semantics="stable", backend="z3")

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "z3"
    assert result.install_hint == "Use backend='labelling'."
