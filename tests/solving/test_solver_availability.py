import pytest

from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom
from argumentation.structured.aspic.aspic import Literal
from argumentation.structured.aspic.aspic import Rule
from argumentation.core.dung import ArgumentationFramework
from argumentation.core.dung import complete_extensions
from argumentation.core.dung import grounded_extension
from argumentation.core.dung import preferred_extensions
from argumentation.core.dung import stable_extensions
import argumentation.solving.solver as solver_module
from argumentation.solving.solver import (
    AcceptanceSolverSuccess,
    ExtensionSolverSuccess,
    SingleExtensionSolverSuccess,
    SolverBackendError,
    SolverBackendUnavailable,
    solve_aba_acceptance,
    solve_aba_single_extension,
    solve_dung_acceptance,
    solve_dung_extensions,
    solve_dung_single_extension,
)
from hypothesis import given, settings, strategies as st
from tests.core.test_dung import argumentation_frameworks
from argumentation.solver_adapters.iccma_af import (
    ICCMAOutput,
    ICCMAOutputKind,
    ICCMASolverError,
    ICCMASolverProtocolError,
    ICCMASolverSuccess,
    ICCMASolverUnavailable,
)


def _literal(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _simple_aba_framework() -> ABAFramework:
    a = _literal("a")
    b = _literal("b")
    ca = _literal("ca")
    cb = _literal("cb")
    return ABAFramework(
        language=frozenset({a, b, ca, cb}),
        rules=frozenset(),
        assumptions=frozenset({a, b}),
        contrary={a: ca, b: cb},
    )


def _large_dense_aba_framework() -> ABAFramework:
    assumptions = tuple(_literal(f"a{index}") for index in range(151))
    contraries = {_literal(f"a{index}"): _literal(f"ca{index}") for index in range(151)}
    heads = tuple(
        _literal(f"h{index}_{offset}") for index in range(151) for offset in range(26)
    )
    rules = frozenset(
        Rule((assumptions[index],), heads[index * 26 + offset], "strict")
        for index in range(151)
        for offset in range(26)
    )
    return ABAFramework(
        language=frozenset(assumptions)
        | frozenset(contraries.values())
        | frozenset(heads),
        rules=rules,
        assumptions=frozenset(assumptions),
        contrary=contraries,
    )


def _large_dense_non_sparse_narrow_aba_framework() -> ABAFramework:
    """Mirror the ICCMA aba_2000 shape: large dense flat, but not sparse-narrow.

    Fails sparse_narrow_native_sat_shape for the same reasons as
    ABAs/aba_2000_0.1_5_5_1.aba: assumptions < 700, rule bodies wider than 2,
    and shared contrary targets (multiplicity 3).
    """
    assumptions = tuple(_literal(f"a{index}") for index in range(200))
    contraries = {
        assumptions[index]: _literal(f"ca{index // 3}") for index in range(200)
    }
    heads = tuple(
        _literal(f"h{index}_{offset}") for index in range(200) for offset in range(26)
    )
    rules = frozenset(
        Rule(
            tuple(assumptions[(index + step) % 200] for step in range(5)),
            heads[index * 26 + offset],
            "strict",
        )
        for index in range(200)
        for offset in range(26)
    )
    return ABAFramework(
        language=frozenset(assumptions)
        | frozenset(contraries.values())
        | frozenset(heads),
        rules=rules,
        assumptions=frozenset(assumptions),
        contrary=contraries,
    )


def _sparse_narrow_large_dense_aba_framework() -> ABAFramework:
    """Mirror the ICCMA abcgen shape: sparse-narrow AND large dense flat."""
    assumptions = tuple(_literal(f"a{index}") for index in range(700))
    contraries = {assumptions[index]: _literal(f"ca{index}") for index in range(700)}
    heads = tuple(
        _literal(f"h{index}_{offset}") for index in range(700) for offset in range(26)
    )
    rules = frozenset(
        Rule((assumptions[index],), heads[index * 26 + offset], "strict")
        for index in range(700)
        for offset in range(26)
    )
    return ABAFramework(
        language=frozenset(assumptions)
        | frozenset(contraries.values())
        | frozenset(heads),
        rules=rules,
        assumptions=frozenset(assumptions),
        contrary=contraries,
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


def test_default_aba_single_extension_uses_multishot_when_clingo_available(
    monkeypatch,
) -> None:
    pytest.importorskip("clingo")
    framework = _simple_aba_framework()

    def forbidden_sat(*args, **kwargs):
        raise AssertionError("ABA preferred witness should use clingo multishot")

    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)
    monkeypatch.setattr(solver_module, "sat_aba_support_extension", forbidden_sat)

    result = solve_aba_single_extension(framework, semantics="preferred")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension is not None


def test_default_aba_stable_single_extension_uses_multishot_when_clingo_available(
    monkeypatch,
) -> None:
    pytest.importorskip("clingo")
    framework = _simple_aba_framework()

    def forbidden_sat(*args, **kwargs):
        raise AssertionError("ABA stable witness should use clingo multishot")

    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)
    monkeypatch.setattr(solver_module, "sat_aba_stable_extension", forbidden_sat)

    result = solve_aba_single_extension(framework, semantics="stable")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension is not None


def test_large_dense_aba_stable_single_extension_auto_uses_asp_when_not_sparse_narrow(
    monkeypatch,
) -> None:
    framework = _large_dense_aba_framework()
    witness = frozenset({min(framework.assumptions, key=repr)})

    def forbidden_sat(*args, **kwargs):
        raise AssertionError(
            "large dense non-sparse-narrow ABA stable auto route should use clingo"
        )

    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)
    monkeypatch.setattr(solver_module, "sat_aba_stable_extension", forbidden_sat)
    monkeypatch.setattr(
        solver_module,
        "_solve_asp_aba_single_extension",
        lambda *args, **kwargs: SingleExtensionSolverSuccess(extension=witness),
    )

    result = solve_aba_single_extension(framework, semantics="stable")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == witness


def test_stable_single_extension_auto_backend_is_asp_for_large_dense_non_sparse_narrow(
    monkeypatch,
) -> None:
    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)

    backend = solver_module._auto_aba_backend_for_framework(
        "auto",
        "stable",
        task="single-extension",
        framework=_large_dense_non_sparse_narrow_aba_framework(),
    )

    assert backend == "asp"


def test_stable_single_extension_auto_backend_stays_sat_for_sparse_narrow(
    monkeypatch,
) -> None:
    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)

    backend = solver_module._auto_aba_backend_for_framework(
        "auto",
        "stable",
        task="single-extension",
        framework=_sparse_narrow_large_dense_aba_framework(),
    )

    assert backend == "sat"


def test_default_aba_acceptance_uses_multishot_when_clingo_available(
    monkeypatch,
) -> None:
    pytest.importorskip("clingo")
    framework = _simple_aba_framework()

    def forbidden_sat(*args, **kwargs):
        raise AssertionError("ABA auto should prefer clingo multishot over SAT")

    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)
    monkeypatch.setattr(solver_module, "sat_aba_support_acceptance", forbidden_sat)

    result = solve_aba_acceptance(
        framework,
        semantics="preferred",
        task="skeptical",
        query=_literal("a"),
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is True


def test_solve_dung_extensions_default_auto_uses_sat_for_stable(monkeypatch) -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    def forbidden_native_extensions(*args, **kwargs):
        raise AssertionError(
            "default stable solving should not call native enumeration"
        )

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


def test_sat_backend_solves_stable_single_extension_without_native_enumeration() -> (
    None
):
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
        raise AssertionError(
            "default complete solving should not call native enumeration"
        )

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
        raise AssertionError(
            "default complete solving should not call native enumeration"
        )

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
        raise AssertionError(
            "default preferred witness should not call native enumeration"
        )

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
        raise AssertionError(
            "default preferred acceptance should not call native enumeration"
        )

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
        raise AssertionError(
            "default skeptical preferred acceptance should not call native enumeration"
        )

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
        raise AssertionError(
            "default semi-stable witness should not call native enumeration"
        )

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
        raise AssertionError(
            "default ideal acceptance should not call native enumeration"
        )

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
        raise AssertionError(
            "default semi-stable acceptance should not call native enumeration"
        )

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
        raise AssertionError(
            "default stage acceptance should not call native enumeration"
        )

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
        _assert_dung_acceptance_witness_is_semantic(
            framework,
            semantics,
            task,
            query,
            sat_result,
        )


def _assert_dung_acceptance_witness_is_semantic(
    framework: ArgumentationFramework,
    semantics: str,
    task: str,
    query: str,
    result: AcceptanceSolverSuccess,
) -> None:
    extensions = set(NATIVE_EXTENSION_ORACLES[semantics](framework))
    if task == "credulous":
        if result.answer:
            assert result.witness in extensions
            assert result.witness is not None and query in result.witness
        else:
            assert result.witness is None
        return
    if result.answer:
        assert result.counterexample is None
    elif result.counterexample is not None:
        assert result.counterexample in extensions
        assert query not in result.counterexample


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
    assert (
        result.reason
        == "ICCMA AF SE tasks return one extension witness, not enumeration"
    )


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
        "argumentation.solving.solver.iccma_af.solve_af_extensions",
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
        "argumentation.solving.solver.iccma_af.solve_af_extensions",
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
        "argumentation.solving.solver.iccma_af.solve_af_extensions",
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
        "argumentation.solving.solver.iccma_af.solve_af_extensions",
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


def test_solve_dung_single_extension_preserves_iccma_protocol_error(
    monkeypatch,
) -> None:
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
        "argumentation.solving.solver.iccma_af.solve_af_extensions",
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
        "argumentation.solving.solver.iccma_af.solve_af_acceptance",
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
        "argumentation.solving.solver.iccma_af.solve_af_acceptance",
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
        "argumentation.solving.solver.iccma_af.solve_af_acceptance",
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
    assert (
        enumeration.reason
        == "ICCMA AF SE tasks return one extension witness, not enumeration"
    )
    assert isinstance(single, SingleExtensionSolverSuccess)
    assert not isinstance(single, ExtensionSolverSuccess)
