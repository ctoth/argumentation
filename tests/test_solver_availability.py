from argumentation.dung import ArgumentationFramework
from argumentation.dung import preferred_extensions
from argumentation.solver import (
    AcceptanceSolverSuccess,
    ExtensionSolverSuccess,
    ICCMAAFBackend,
    SingleExtensionSolverSuccess,
    SolverBackendError,
    SolverBackendUnavailable,
    solve_dung_acceptance,
    solve_dung_extensions,
    solve_dung_single_extension,
)
from hypothesis import given, settings, strategies as st
from argumentation.solver_adapters.iccma_af import (
    ICCMAOutput,
    ICCMAOutputKind,
    ICCMASolverError,
    ICCMASolverProtocolError,
    ICCMASolverSuccess,
    ICCMASolverUnavailable,
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


def test_solve_dung_extensions_rejects_iccma_single_witness_backend() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2", "3"}),
        defeats=frozenset({("1", "2"), ("2", "1")}),
    )

    result = solve_dung_extensions(
        framework,
        semantics="preferred",
        backend=ICCMAAFBackend(binary="fake-iccma"),
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.reason == "ICCMA AF SE tasks return one extension witness, not enumeration"


def test_solve_dung_single_extension_routes_explicit_iccma_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2"}),
        defeats=frozenset({("1", "2")}),
    )
    calls = []

    def fake_solve_af_extensions(*, framework, semantics, binary, timeout_seconds):
        calls.append((framework, semantics, binary, timeout_seconds))
        return ICCMASolverSuccess(
            backend=binary,
            problem="SE-ST",
            stdout="w 1\n",
            output=ICCMAOutput(
                problem="SE-ST",
                kind=ICCMAOutputKind.SINGLE_EXTENSION,
                raw_stdout="w 1\n",
                extensions=(frozenset({"1"}),),
                witness=frozenset({"1"}),
            ),
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_extensions",
        fake_solve_af_extensions,
    )

    result = solve_dung_single_extension(
        framework,
        semantics="stable",
        backend=ICCMAAFBackend(binary="fake-iccma", timeout_seconds=7.5),
    )

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"1"})
    assert calls == [(framework, "stable", "fake-iccma", 7.5)]


def test_solve_dung_single_extension_maps_iccma_unavailable(monkeypatch) -> None:
    framework = ArgumentationFramework(arguments=frozenset({"1"}), defeats=frozenset())

    def fake_solve_af_extensions(*, framework, semantics, binary, timeout_seconds):
        return ICCMASolverUnavailable(
            backend=binary,
            reason="binary not found on PATH",
            install_hint="install solver",
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_extensions",
        fake_solve_af_extensions,
    )

    result = solve_dung_single_extension(
        framework,
        semantics="grounded",
        backend=ICCMAAFBackend(binary="missing"),
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "missing"
    assert result.reason == "binary not found on PATH"


def test_solve_dung_single_extension_maps_iccma_solver_error(monkeypatch) -> None:
    framework = ArgumentationFramework(arguments=frozenset({"1"}), defeats=frozenset())

    def fake_solve_af_extensions(*, framework, semantics, binary, timeout_seconds):
        return ICCMASolverError(
            backend=binary,
            problem="SE-ST",
            returncode=2,
            stderr="bad input",
            stdout="",
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_extensions",
        fake_solve_af_extensions,
    )

    result = solve_dung_single_extension(
        framework,
        semantics="stable",
        backend=ICCMAAFBackend(binary="bad-solver"),
    )

    assert isinstance(result, SolverBackendError)
    assert result.backend == "bad-solver"
    assert result.reason == "solver exited with code 2"
    assert result.details["stderr"] == "bad input"


def test_solve_dung_single_extension_preserves_iccma_protocol_error(monkeypatch) -> None:
    framework = ArgumentationFramework(arguments=frozenset({"1"}), defeats=frozenset())

    def fake_solve_af_extensions(*, framework, semantics, binary, timeout_seconds):
        return ICCMASolverProtocolError(
            backend=binary,
            problem="SE-ST",
            message="SE output must be one witness line or NO",
            stderr="solver stderr",
            stdout="w 1\nw 2\n",
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_extensions",
        fake_solve_af_extensions,
    )

    result = solve_dung_single_extension(
        framework,
        semantics="stable",
        backend=ICCMAAFBackend(binary="bad-protocol"),
    )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.problem == "SE-ST"
    assert result.stdout == "w 1\nw 2\n"


def test_solve_dung_acceptance_preserves_iccma_protocol_error(monkeypatch) -> None:
    framework = ArgumentationFramework(arguments=frozenset({"1"}), defeats=frozenset())

    def fake_solve_af_acceptance(
        *,
        framework,
        semantics,
        task,
        query,
        binary,
        timeout_seconds,
        certificate_required,
    ):
        return ICCMASolverProtocolError(
            backend=binary,
            problem="DC-ST",
            message="decision output must start with YES or NO",
            stderr="solver stderr",
            stdout="MAYBE\n",
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_acceptance",
        fake_solve_af_acceptance,
    )

    result = solve_dung_acceptance(
        framework,
        semantics="stable",
        task="credulous",
        query="1",
        backend=ICCMAAFBackend(binary="bad-protocol"),
    )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.problem == "DC-ST"
    assert result.stdout == "MAYBE\n"


def test_solve_dung_acceptance_native_backend_returns_witnesses() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    credulous = solve_dung_acceptance(
        framework,
        semantics="stable",
        task="credulous",
        query="a",
    )
    skeptical = solve_dung_acceptance(
        framework,
        semantics="stable",
        task="skeptical",
        query="b",
    )

    assert isinstance(credulous, AcceptanceSolverSuccess)
    assert credulous.answer is True
    assert credulous.witness == frozenset({"a"})
    assert isinstance(skeptical, AcceptanceSolverSuccess)
    assert skeptical.answer is False
    assert skeptical.counterexample == frozenset({"a"})


def test_solve_dung_acceptance_routes_explicit_iccma_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2"}),
        defeats=frozenset({("1", "2")}),
    )
    calls = []

    def fake_solve_af_acceptance(
        *,
        framework,
        semantics,
        task,
        query,
        binary,
        timeout_seconds,
        certificate_required,
    ):
        calls.append(
            (
                framework,
                semantics,
                task,
                query,
                binary,
                timeout_seconds,
                certificate_required,
            )
        )
        return ICCMASolverSuccess(
            backend=binary,
            problem="DC-ST",
            stdout="YES\nw 1\n",
            output=ICCMAOutput(
                problem="DC-ST",
                kind=ICCMAOutputKind.DECISION,
                raw_stdout="YES\nw 1\n",
                answer=True,
                witness=frozenset({"1"}),
                extensions=(frozenset({"1"}),),
            ),
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_acceptance",
        fake_solve_af_acceptance,
    )

    result = solve_dung_acceptance(
        framework,
        semantics="stable",
        task="credulous",
        query="1",
        backend=ICCMAAFBackend(binary="fake-iccma", timeout_seconds=7.5),
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is True
    assert result.witness == frozenset({"1"})
    assert calls == [(framework, "stable", "credulous", "1", "fake-iccma", 7.5, True)]


def complete_mutual_attack_frameworks():
    return st.integers(min_value=2, max_value=5).map(
        lambda size: ArgumentationFramework(
            arguments=frozenset(str(index) for index in range(1, size + 1)),
            defeats=frozenset(
                (str(attacker), str(target))
                for attacker in range(1, size + 1)
                for target in range(1, size + 1)
                if attacker != target
            ),
        )
    )


def test_solver_success_result_types_are_task_specific() -> None:
    assert ExtensionSolverSuccess is not SingleExtensionSolverSuccess
    assert ExtensionSolverSuccess is not AcceptanceSolverSuccess
    assert SingleExtensionSolverSuccess is not AcceptanceSolverSuccess


@given(complete_mutual_attack_frameworks())
@settings(deadline=10000, max_examples=20)
def test_iccma_single_extension_backend_is_not_enumeration_for_multi_extension_afs(
    framework: ArgumentationFramework,
) -> None:
    # Complete mutual attack graphs have one preferred extension per argument.
    assert len(preferred_extensions(framework)) == len(framework.arguments)

    enumeration = solve_dung_extensions(
        framework,
        semantics="preferred",
        backend=ICCMAAFBackend(binary="fake-iccma"),
    )
    single = solve_dung_single_extension(framework, semantics="preferred")

    assert isinstance(enumeration, SolverBackendUnavailable)
    assert enumeration.reason == "ICCMA AF SE tasks return one extension witness, not enumeration"
    assert isinstance(single, SingleExtensionSolverSuccess)
    assert not isinstance(single, ExtensionSolverSuccess)
