from argumentation.dung import ArgumentationFramework
from argumentation.dung import complete_extensions
from argumentation.dung import grounded_extension
from argumentation.dung import preferred_extensions
from argumentation.dung import stable_extensions
import argumentation.solver as solver_module
from argumentation.solver import (
    AcceptanceSolverSuccess,
    ExtensionSolverSuccess,
    SingleExtensionSolverSuccess,
    SolverBackendError,
    SolverBackendUnavailable,
    solve_dung_acceptance,
    solve_dung_extensions,
    solve_dung_single_extension,
)
from hypothesis import given, settings, strategies as st
from tests.test_dung import argumentation_frameworks
from argumentation.solver_adapters.iccma_af import (
    ICCMAOutput,
    ICCMAOutputKind,
    ICCMASolverError,
    ICCMASolverProtocolError,
    ICCMASolverSuccess,
    ICCMASolverUnavailable,
)


NATIVE_EXTENSION_ORACLES = {
    "complete": complete_extensions,
    "grounded": lambda framework: [grounded_extension(framework)],
    "preferred": preferred_extensions,
    "stable": stable_extensions,
    "semi-stable": solver_module.semi_stable_extensions,
    "stage": solver_module.stage_extensions,
    "ideal": lambda framework: [solver_module.ideal_extension(framework)],
}


def test_solve_dung_extensions_defaults_to_auto_backend() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    result = solve_dung_extensions(framework, semantics="stable")

    assert isinstance(result, ExtensionSolverSuccess)
    assert result.extensions == (frozenset({"a"}),)


def test_solve_dung_extensions_default_auto_uses_sat_for_stable(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default stable solving should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_extensions(framework, semantics="stable")

    assert isinstance(result, ExtensionSolverSuccess)
    assert result.extensions == (frozenset({"a"}),)


@given(
    argumentation_frameworks(max_args=4),
    st.sampled_from(sorted(NATIVE_EXTENSION_ORACLES)),
)
@settings(deadline=10000, max_examples=40)
def test_native_backend_matches_direct_dung_semantic_oracles(
    framework: ArgumentationFramework,
    semantics: str,
) -> None:
    result = solve_dung_extensions(framework, semantics=semantics, backend="native")

    assert isinstance(result, ExtensionSolverSuccess)
    assert set(result.extensions) == set(NATIVE_EXTENSION_ORACLES[semantics](framework))


def test_solve_dung_extensions_rejects_deleted_labelling_backend() -> None:
    framework = ArgumentationFramework(arguments=frozenset(), defeats=frozenset())

    result = solve_dung_extensions(framework, semantics="stable", backend="labelling")

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "labelling"
    assert result.install_hint == "Use backend='native'."


def test_solve_dung_extensions_rejects_deleted_z3_backend() -> None:
    framework = ArgumentationFramework(arguments=frozenset(), defeats=frozenset())

    result = solve_dung_extensions(framework, semantics="stable", backend="z3")

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "z3"
    assert result.install_hint == "Use backend='native'."


def test_solve_dung_extensions_reports_unavailable_external_sat_backend() -> None:
    framework = ArgumentationFramework(arguments=frozenset({"a"}), defeats=frozenset())

    result = solve_dung_extensions(
        framework,
        semantics="stable",
        backend="sat",
        sat=solver_module.SATConfig(require_external=True),
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "sat"
    assert result.reason == "external SAT backend is not configured"


def test_sat_backend_solves_stable_single_extension_without_native_enumeration() -> None:
    arguments = frozenset(str(index) for index in range(1, 71))
    defeats = frozenset(
        {("1", str(index)) for index in range(2, 71)} | {("2", "3"), ("3", "2")}
    )
    framework = ArgumentationFramework(arguments=arguments, defeats=defeats)

    result = solve_dung_single_extension(
        framework,
        semantics="stable",
        backend="sat",
    )

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"1"})


def test_sat_backend_solves_stable_acceptance_without_native_enumeration() -> None:
    arguments = frozenset(str(index) for index in range(1, 71))
    defeats = frozenset(
        {("1", str(index)) for index in range(2, 71)} | {("2", "3"), ("3", "2")}
    )
    framework = ArgumentationFramework(arguments=arguments, defeats=defeats)

    result = solve_dung_acceptance(
        framework,
        semantics="stable",
        task="credulous",
        query="1",
        backend="sat",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is True
    assert result.witness == frozenset({"1"})


def test_default_single_extension_uses_auto_stable_sat_backend() -> None:
    arguments = frozenset(str(index) for index in range(1, 71))
    defeats = frozenset(
        {("1", str(index)) for index in range(2, 71)} | {("2", "3"), ("3", "2")}
    )
    framework = ArgumentationFramework(arguments=arguments, defeats=defeats)

    result = solve_dung_single_extension(framework, semantics="stable")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"1"})


def test_default_acceptance_uses_auto_stable_sat_backend() -> None:
    arguments = frozenset(str(index) for index in range(1, 71))
    defeats = frozenset(
        {("1", str(index)) for index in range(2, 71)} | {("2", "3"), ("3", "2")}
    )
    framework = ArgumentationFramework(arguments=arguments, defeats=defeats)

    result = solve_dung_acceptance(
        framework,
        semantics="stable",
        task="skeptical",
        query="2",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is False
    assert result.counterexample == frozenset({"1"})


def test_default_single_extension_uses_auto_complete_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default complete solving should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_single_extension(framework, semantics="complete")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"a"})


def test_default_acceptance_uses_auto_complete_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default complete solving should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    credulous = solve_dung_acceptance(
        framework,
        semantics="complete",
        task="credulous",
        query="a",
    )
    skeptical = solve_dung_acceptance(
        framework,
        semantics="complete",
        task="skeptical",
        query="b",
    )

    assert isinstance(credulous, AcceptanceSolverSuccess)
    assert credulous.answer is True
    assert credulous.witness == frozenset({"a"})
    assert isinstance(skeptical, AcceptanceSolverSuccess)
    assert skeptical.answer is False
    assert skeptical.counterexample == frozenset({"a"})


def test_default_single_extension_uses_auto_preferred_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default preferred witness should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_single_extension(framework, semantics="preferred")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"a"})


def test_default_credulous_acceptance_uses_auto_preferred_sat_backend(
    monkeypatch,
) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default preferred acceptance should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_acceptance(
        framework,
        semantics="preferred",
        task="credulous",
        query="a",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is True
    assert result.witness == frozenset({"a"})


def test_default_skeptical_preferred_acceptance_uses_auto_sat_backend(
    monkeypatch,
) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default skeptical preferred acceptance should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_acceptance(
        framework,
        semantics="preferred",
        task="skeptical",
        query="b",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is False
    assert result.counterexample is None


def test_default_single_extension_uses_auto_semi_stable_sat_backend(
    monkeypatch,
) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default semi-stable witness should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_single_extension(framework, semantics="semi-stable")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"a"})


def test_default_single_extension_uses_auto_stage_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default stage witness should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    result = solve_dung_single_extension(framework, semantics="stage")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"a"})


def test_default_single_extension_uses_auto_ideal_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default ideal witness should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)
    monkeypatch.setattr(
        solver_module,
        "preferred_extensions",
        forbidden_native_extensions,
    )

    result = solve_dung_single_extension(framework, semantics="ideal")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({"a"})


def test_default_acceptance_uses_auto_ideal_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default ideal acceptance should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)
    monkeypatch.setattr(
        solver_module,
        "preferred_extensions",
        forbidden_native_extensions,
    )

    result = solve_dung_acceptance(
        framework,
        semantics="ideal",
        task="skeptical",
        query="a",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is True


def test_default_acceptance_uses_auto_semi_stable_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default semi-stable acceptance should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    credulous = solve_dung_acceptance(
        framework,
        semantics="semi-stable",
        task="credulous",
        query="a",
    )
    skeptical = solve_dung_acceptance(
        framework,
        semantics="semi-stable",
        task="skeptical",
        query="b",
    )

    assert isinstance(credulous, AcceptanceSolverSuccess)
    assert credulous.answer is True
    assert credulous.witness == frozenset({"a"})
    assert isinstance(skeptical, AcceptanceSolverSuccess)
    assert skeptical.answer is False
    assert skeptical.counterexample == frozenset({"a"})


def test_default_acceptance_uses_auto_stage_sat_backend(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError("default stage acceptance should not call native enumeration")

    monkeypatch.setattr(solver_module, "_dung_extensions", forbidden_native_extensions)

    credulous = solve_dung_acceptance(
        framework,
        semantics="stage",
        task="credulous",
        query="a",
    )
    skeptical = solve_dung_acceptance(
        framework,
        semantics="stage",
        task="skeptical",
        query="b",
    )

    assert isinstance(credulous, AcceptanceSolverSuccess)
    assert credulous.answer is True
    assert credulous.witness == frozenset({"a"})
    assert isinstance(skeptical, AcceptanceSolverSuccess)
    assert skeptical.answer is False
    assert skeptical.counterexample == frozenset({"a"})


@given(
    argumentation_frameworks(max_args=4),
    st.sampled_from(sorted(NATIVE_EXTENSION_ORACLES)),
)
@settings(deadline=10000, max_examples=40)
def test_sat_backend_enumeration_matches_native_dung_oracles(
    framework: ArgumentationFramework,
    semantics: str,
) -> None:
    result = solve_dung_extensions(framework, semantics=semantics, backend="sat")

    assert isinstance(result, ExtensionSolverSuccess)
    assert set(result.extensions) == set(NATIVE_EXTENSION_ORACLES[semantics](framework))


@given(
    argumentation_frameworks(max_args=4),
    st.sampled_from(sorted(NATIVE_EXTENSION_ORACLES)),
)
@settings(deadline=10000, max_examples=40)
def test_sat_backend_acceptance_matches_native_backend(
    framework: ArgumentationFramework,
    semantics: str,
) -> None:
    query = sorted(framework.arguments)[0]

    for task in ("credulous", "skeptical"):
        sat_result = solve_dung_acceptance(
            framework,
            semantics=semantics,
            task=task,
            query=query,
            backend="sat",
        )
        native_result = solve_dung_acceptance(
            framework,
            semantics=semantics,
            task=task,
            query=query,
            backend="native",
        )

        assert isinstance(sat_result, AcceptanceSolverSuccess)
        assert isinstance(native_result, AcceptanceSolverSuccess)
        assert sat_result.answer is native_result.answer
        if semantics == "preferred" and task == "skeptical":
            assert sat_result.witness is None
            assert sat_result.counterexample is None
        else:
            assert sat_result == native_result


def test_solve_dung_extensions_rejects_iccma_single_witness_backend() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2", "3"}),
        defeats=frozenset({("1", "2"), ("2", "1")}),
    )

    result = solve_dung_extensions(
        framework,
        semantics="preferred",
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="fake-iccma"),
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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="fake-iccma", timeout_seconds=7.5),
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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="missing"),
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "missing"
    assert result.reason == "binary not found on PATH"


def test_solve_dung_single_extension_requires_iccma_config_before_subprocess(
    monkeypatch,
) -> None:
    framework = ArgumentationFramework(arguments=frozenset({"1"}), defeats=frozenset())
    calls = []

    def fake_solve_af_extensions(*, framework, semantics, binary, timeout_seconds):
        calls.append((framework, semantics, binary, timeout_seconds))
        return ICCMASolverUnavailable(
            backend=binary,
            reason="should not be reached",
            install_hint="should not be reached",
        )

    monkeypatch.setattr(
        "argumentation.solver.iccma_af.solve_af_extensions",
        fake_solve_af_extensions,
    )

    result = solve_dung_single_extension(
        framework,
        semantics="grounded",
        backend="iccma",
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "iccma"
    assert result.reason == "missing ICCMA solver configuration"
    assert calls == []


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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="bad-solver"),
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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="bad-protocol"),
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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="bad-protocol"),
    )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.problem == "DC-ST"
    assert result.stdout == "MAYBE\n"


def test_solve_dung_acceptance_requires_iccma_config_before_subprocess(
    monkeypatch,
) -> None:
    framework = ArgumentationFramework(arguments=frozenset({"1"}), defeats=frozenset())
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
        return ICCMASolverUnavailable(
            backend=binary,
            reason="should not be reached",
            install_hint="should not be reached",
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
        backend="iccma",
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "iccma"
    assert result.reason == "missing ICCMA solver configuration"
    assert calls == []


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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="fake-iccma", timeout_seconds=7.5),
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
        backend="iccma",
        iccma=solver_module.ICCMAConfig(binary="fake-iccma"),
    )
    single = solve_dung_single_extension(framework, semantics="preferred")

    assert isinstance(enumeration, SolverBackendUnavailable)
    assert enumeration.reason == "ICCMA AF SE tasks return one extension witness, not enumeration"
    assert isinstance(single, SingleExtensionSolverSuccess)
    assert not isinstance(single, ExtensionSolverSuccess)
