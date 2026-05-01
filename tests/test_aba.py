from __future__ import annotations

from hypothesis import given, settings, strategies as st

from argumentation import aba as native_aba
from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.solver import (
    AcceptanceSolverSuccess,
    ICCMAConfig,
    SingleExtensionSolverSuccess,
    SolverBackendUnavailable,
    solve_aba_acceptance,
    solve_aba_single_extension,
)


ABA_EXTENSION_ORACLES = {
    "complete": native_aba.complete_extensions,
    "preferred": native_aba.preferred_extensions,
    "stable": native_aba.stable_extensions,
    "grounded": lambda framework: (native_aba.grounded_extension(framework),),
    "ideal": lambda framework: (native_aba.ideal_extension(framework),),
}


@st.composite
def flat_aba_frameworks(draw):
    size = draw(st.integers(min_value=1, max_value=3))
    attacks = draw(
        st.frozensets(
            st.tuples(
                st.integers(min_value=1, max_value=size),
                st.integers(min_value=1, max_value=size),
            ),
            max_size=size * size,
        )
    )
    return _flat_aba(size, frozenset(attacks))


@given(flat_aba_frameworks(), st.sampled_from(sorted(ABA_EXTENSION_ORACLES)))
@settings(deadline=10000, max_examples=40)
def test_solve_aba_single_extension_native_returns_native_witness(
    framework: ABAFramework,
    semantics: str,
) -> None:
    result = solve_aba_single_extension(framework, semantics=semantics, backend="native")

    assert isinstance(result, SingleExtensionSolverSuccess)
    if result.extension is not None:
        assert result.extension in ABA_EXTENSION_ORACLES[semantics](framework)


@given(
    flat_aba_frameworks(),
    st.sampled_from(sorted(ABA_EXTENSION_ORACLES)),
    st.sampled_from(["credulous", "skeptical"]),
)
@settings(deadline=10000, max_examples=50)
def test_solve_aba_acceptance_native_matches_extension_quantification(
    framework: ABAFramework,
    semantics: str,
    task: str,
) -> None:
    query = sorted(framework.language, key=repr)[0]
    extensions = ABA_EXTENSION_ORACLES[semantics](framework)

    result = solve_aba_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=query,
        backend="native",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    if task == "credulous":
        assert result.answer is any(
            native_aba.derives(framework, extension, query)
            for extension in extensions
        )
        if result.witness is not None:
            assert native_aba.derives(framework, result.witness, query)
    else:
        assert result.answer is all(
            native_aba.derives(framework, extension, query)
            for extension in extensions
        )
        if result.counterexample is not None:
            assert not native_aba.derives(framework, result.counterexample, query)


def test_solve_aba_aspforaba_backend_is_typed_unavailable_without_contract() -> None:
    framework = _flat_aba(2, frozenset())

    result = solve_aba_single_extension(
        framework,
        semantics="stable",
        backend="aspforaba",
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "aspforaba"


def test_solve_aba_single_extension_auto_uses_stable_sat_without_native_enumeration(
    monkeypatch,
) -> None:
    framework = _flat_aba(70, frozenset((1, target) for target in range(2, 71)))

    def fail_native(*args, **kwargs):
        raise AssertionError("native ABA stable enumeration should not run")

    monkeypatch.setattr("argumentation.solver.aba_semantics.stable_extensions", fail_native)

    result = solve_aba_single_extension(framework, semantics="stable")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == frozenset({literal("a1")})


def test_solve_aba_acceptance_auto_uses_stable_sat_without_native_enumeration(
    monkeypatch,
) -> None:
    framework = _flat_aba(70, frozenset((1, target) for target in range(2, 71)))

    def fail_native(*args, **kwargs):
        raise AssertionError("native ABA stable enumeration should not run")

    monkeypatch.setattr("argumentation.solver.aba_semantics.stable_extensions", fail_native)

    result = solve_aba_acceptance(
        framework,
        semantics="stable",
        task="skeptical",
        query=literal("a2"),
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is False
    assert result.counterexample == frozenset({literal("a1")})


@given(flat_aba_frameworks())
@settings(deadline=10000, max_examples=40)
def test_solve_aba_single_extension_stable_sat_matches_native_oracle(
    framework: ABAFramework,
) -> None:
    native_extensions = native_aba.stable_extensions(framework)

    result = solve_aba_single_extension(framework, semantics="stable", backend="sat")

    assert isinstance(result, SingleExtensionSolverSuccess)
    if result.extension is None:
        assert native_extensions == ()
    else:
        assert result.extension in native_extensions


@given(flat_aba_frameworks(), st.sampled_from(["credulous", "skeptical"]))
@settings(deadline=10000, max_examples=50)
def test_solve_aba_acceptance_stable_sat_matches_native_oracle(
    framework: ABAFramework,
    task: str,
) -> None:
    query = sorted(framework.language, key=repr)[0]
    native_extensions = native_aba.stable_extensions(framework)

    result = solve_aba_acceptance(
        framework,
        semantics="stable",
        task=task,
        query=query,
        backend="sat",
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    if task == "credulous":
        assert result.answer is any(
            native_aba.derives(framework, extension, query)
            for extension in native_extensions
        )
    else:
        assert result.answer is all(
            native_aba.derives(framework, extension, query)
            for extension in native_extensions
        )


def test_solve_aba_single_extension_iccma_returns_verified_witness(monkeypatch) -> None:
    framework = _flat_aba(1, frozenset())

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.subprocess.run",
        lambda *args, **kwargs: completed(stdout="w 1\n"),
    )

    result = solve_aba_single_extension(
        framework,
        semantics="stable",
        backend="iccma",
        iccma=ICCMAConfig(binary="fake-aspforaba"),
    )

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == framework.assumptions


def test_solve_aba_acceptance_iccma_returns_verified_answer(monkeypatch) -> None:
    framework = _flat_aba(1, frozenset())
    query = literal("a1")

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.subprocess.run",
        lambda *args, **kwargs: completed(stdout="YES\n"),
    )

    result = solve_aba_acceptance(
        framework,
        semantics="complete",
        task="credulous",
        query=query,
        backend="iccma",
        iccma=ICCMAConfig(binary="fake-aspforaba"),
    )

    assert isinstance(result, AcceptanceSolverSuccess)
    assert result.answer is True
    assert result.witness is None
    assert result.counterexample is None


def _flat_aba(size: int, attacks: frozenset[tuple[int, int]]) -> ABAFramework:
    assumptions = {literal(f"a{index}") for index in range(1, size + 1)}
    contraries = {literal(f"c{index}") for index in range(1, size + 1)}
    assumption_by_index = {
        index: literal(f"a{index}") for index in range(1, size + 1)
    }
    contrary_by_index = {
        index: literal(f"c{index}") for index in range(1, size + 1)
    }
    return ABAFramework(
        language=frozenset(assumptions | contraries),
        rules=frozenset(
            Rule((assumption_by_index[attacker],), contrary_by_index[target], "strict")
            for attacker, target in attacks
        ),
        assumptions=frozenset(assumptions),
        contrary={
            assumption_by_index[index]: contrary_by_index[index]
            for index in range(1, size + 1)
        },
    )


def literal(name: str) -> Literal:
    return Literal(GroundAtom(name))


def completed(*, stdout: str):
    class Completed:
        returncode = 0
        stderr = ""

        def __init__(self, stdout: str) -> None:
            self.stdout = stdout

    return Completed(stdout)
