import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.core.optional_deps import OptionalDependencyUnavailable
from argumentation.solving import solver as solver_module
from argumentation.solving.solver import SolverBackendUnavailable
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal


def _dung_framework() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a"}),
        defeats=frozenset(),
    )


def _literal(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _aba_framework() -> ABAFramework:
    assumption = _literal("a")
    contrary = _literal("not_a")
    return ABAFramework(
        language=frozenset({assumption, contrary}),
        rules=frozenset(),
        assumptions=frozenset({assumption}),
        contrary={assumption: contrary},
    )


def _missing_python_sat() -> OptionalDependencyUnavailable:
    return OptionalDependencyUnavailable(
        feature="native ABA PrefSat solving",
        package="python-sat",
        install_hint="Install python-sat or use backend='native'.",
    )


def test_dung_enumeration_maps_only_dependency_absence(monkeypatch) -> None:
    calls = 0

    def missing(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise _missing_python_sat()

    monkeypatch.setattr(solver_module, "sat_extensions", missing)

    result = solver_module.solve_dung_extensions(
        _dung_framework(),
        semantics="stable",
        backend="sat",
    )

    assert calls == 1
    assert isinstance(result, SolverBackendUnavailable)
    assert result.reason == "native ABA PrefSat solving requires python-sat"
    assert result.install_hint == "Install python-sat or use backend='native'."


def test_dung_single_extension_propagates_invariant_without_retry(monkeypatch) -> None:
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("SAT preferred growth did not produce a strict superset")

    monkeypatch.setitem(solver_module._SAT_SINGLE_EXTENSION_FINDERS, "stable", broken)

    with pytest.raises(
        RuntimeError,
        match="SAT preferred growth did not produce a strict superset",
    ):
        solver_module.solve_dung_single_extension(
            _dung_framework(),
            semantics="stable",
            backend="sat",
        )

    assert calls == 1


def test_dung_single_extension_preserves_dependency_guidance(monkeypatch) -> None:
    calls = 0

    def missing(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise _missing_python_sat()

    monkeypatch.setitem(solver_module._SAT_SINGLE_EXTENSION_FINDERS, "stable", missing)

    result = solver_module.solve_dung_single_extension(
        _dung_framework(),
        semantics="stable",
        backend="sat",
    )

    assert calls == 1
    assert isinstance(result, SolverBackendUnavailable)
    assert result.install_hint == "Install python-sat or use backend='native'."


def test_dung_cone_acceptance_propagates_runtime_error_without_fallback(
    monkeypatch,
) -> None:
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("cone invariant failed")

    def forbidden(*args, **kwargs):
        raise AssertionError("flat SAT fallback must not mask a cone defect")

    monkeypatch.setattr(solver_module, "solve_cone_acceptance", broken)
    monkeypatch.setitem(solver_module._SAT_ACCEPTANCE_SOLVERS, "stable", forbidden)

    with pytest.raises(RuntimeError, match="cone invariant failed"):
        solver_module.solve_dung_acceptance(
            _dung_framework(),
            semantics="stable",
            task="credulous",
            query="a",
            backend="auto",
        )

    assert calls == 1


def test_dung_direct_acceptance_propagates_runtime_error_without_retry(
    monkeypatch,
) -> None:
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("direct acceptance invariant failed")

    monkeypatch.setitem(solver_module._SAT_ACCEPTANCE_SOLVERS, "stable", broken)

    with pytest.raises(RuntimeError, match="direct acceptance invariant failed"):
        solver_module.solve_dung_acceptance(
            _dung_framework(),
            semantics="stable",
            task="credulous",
            query="a",
            backend="sat",
        )

    assert calls == 1


def test_dung_enumerated_acceptance_maps_dependency_absence(monkeypatch) -> None:
    calls = 0

    def missing(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise _missing_python_sat()

    monkeypatch.setattr(solver_module, "sat_extensions", missing)

    result = solver_module.solve_dung_acceptance(
        _dung_framework(),
        semantics="grounded",
        task="credulous",
        query="a",
        backend="sat",
    )

    assert calls == 1
    assert isinstance(result, SolverBackendUnavailable)
    assert result.install_hint == "Install python-sat or use backend='native'."


def test_sparse_aba_single_extension_propagates_runtime_error(monkeypatch) -> None:
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("sparse ABA invariant failed")

    monkeypatch.setattr(
        solver_module,
        "sparse_narrow_native_sat_shape",
        lambda framework: True,
    )
    monkeypatch.setattr(solver_module, "native_sparse_narrow_aba_extension", broken)

    with pytest.raises(RuntimeError, match="sparse ABA invariant failed"):
        solver_module.solve_aba_single_extension(
            _aba_framework(),
            semantics="preferred",
            backend="sat",
        )

    assert calls == 1


def test_stable_aba_single_extension_propagates_runtime_error(monkeypatch) -> None:
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("stable ABA invariant failed")

    monkeypatch.setattr(solver_module, "sat_aba_stable_extension", broken)

    with pytest.raises(RuntimeError, match="stable ABA invariant failed"):
        solver_module.solve_aba_single_extension(
            _aba_framework(),
            semantics="stable",
            backend="sat",
        )

    assert calls == 1


def test_support_aba_single_extension_maps_dependency_absence(monkeypatch) -> None:
    calls = 0

    def missing(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise _missing_python_sat()

    monkeypatch.setattr(solver_module, "sat_aba_support_extension", missing)

    result = solver_module.solve_aba_single_extension(
        _aba_framework(),
        semantics="complete",
        backend="sat",
    )

    assert calls == 1
    assert isinstance(result, SolverBackendUnavailable)
    assert result.install_hint == "Install python-sat or use backend='native'."


def test_stable_aba_acceptance_propagates_runtime_error(monkeypatch) -> None:
    calls = 0

    def broken(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("stable ABA acceptance invariant failed")

    monkeypatch.setattr(solver_module, "sat_aba_stable_acceptance", broken)

    with pytest.raises(RuntimeError, match="stable ABA acceptance invariant failed"):
        solver_module.solve_aba_acceptance(
            _aba_framework(),
            semantics="stable",
            task="credulous",
            query=_literal("a"),
            backend="sat",
        )

    assert calls == 1


def test_support_aba_acceptance_maps_dependency_absence(monkeypatch) -> None:
    calls = 0

    def missing(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise _missing_python_sat()

    monkeypatch.setattr(solver_module, "sat_aba_support_acceptance", missing)

    result = solver_module.solve_aba_acceptance(
        _aba_framework(),
        semantics="complete",
        task="credulous",
        query=_literal("a"),
        backend="sat",
    )

    assert calls == 1
    assert isinstance(result, SolverBackendUnavailable)
    assert result.install_hint == "Install python-sat or use backend='native'."
