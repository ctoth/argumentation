from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from argumentation import aba as native_aba
from argumentation import aba_sat
from argumentation.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
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


@pytest.mark.parametrize("semantics", ["complete", "preferred"])
def test_solve_aba_single_extension_auto_uses_support_sat_without_enumeration(
    monkeypatch,
    semantics: str,
) -> None:
    framework = _flat_aba(70, frozenset((1, target) for target in range(2, 71)))

    def fail_support_enumeration(*args, **kwargs):
        raise AssertionError("ABA support extension enumeration should not run")

    monkeypatch.setattr(
        "argumentation.solver.sat_aba_support_extensions",
        fail_support_enumeration,
    )

    result = solve_aba_single_extension(framework, semantics=semantics)

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension is not None


@pytest.mark.parametrize("semantics", ["complete", "preferred"])
@pytest.mark.parametrize("task", ["credulous", "skeptical"])
def test_solve_aba_acceptance_auto_uses_support_sat_without_enumeration(
    monkeypatch,
    semantics: str,
    task: str,
) -> None:
    framework = _flat_aba(70, frozenset((1, target) for target in range(2, 71)))

    def fail_support_enumeration(*args, **kwargs):
        raise AssertionError("ABA support acceptance enumeration should not run")

    monkeypatch.setattr(
        "argumentation.solver.sat_aba_support_extensions",
        fail_support_enumeration,
    )

    result = solve_aba_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=literal("a1"),
    )

    assert isinstance(result, AcceptanceSolverSuccess)


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


@given(flat_aba_frameworks(), st.sampled_from(["complete", "preferred"]))
@settings(deadline=10000, max_examples=40)
def test_solve_aba_single_extension_support_sat_matches_native_oracle(
    framework: ABAFramework,
    semantics: str,
) -> None:
    native_extensions = ABA_EXTENSION_ORACLES[semantics](framework)

    result = solve_aba_single_extension(framework, semantics=semantics, backend="sat")

    assert isinstance(result, SingleExtensionSolverSuccess)
    if result.extension is None:
        assert native_extensions == ()
    else:
        assert result.extension in native_extensions


@given(flat_aba_frameworks(), st.data())
@settings(deadline=10000, max_examples=40)
def test_ranked_closure_matches_native_closure(
    framework: ABAFramework,
    data: st.DataObject,
) -> None:
    assumptions = tuple(sorted(framework.assumptions, key=repr))
    selected = data.draw(st.frozensets(st.sampled_from(assumptions)))
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"test_in_{index}")
        for index, assumption in enumerate(assumptions)
    }
    solver = z3.Solver()
    derived = aba_sat._add_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption, variable in variables.items():
        solver.add(variable == (assumption in selected))

    assert solver.check() == z3.sat
    model = solver.model()
    ranked_closure = frozenset(
        literal
        for literal, variable in derived.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )

    assert ranked_closure == native_aba._closure(framework, selected)


@given(flat_aba_frameworks(), st.data())
@settings(deadline=10000, max_examples=40)
def test_bitvec_ranked_closure_matches_native_closure(
    framework: ABAFramework,
    data: st.DataObject,
) -> None:
    assumptions = tuple(sorted(framework.assumptions, key=repr))
    selected = data.draw(st.frozensets(st.sampled_from(assumptions)))
    z3 = aba_sat._load_z3()
    variables = {
        assumption: z3.Bool(f"test_bv_in_{index}")
        for index, assumption in enumerate(assumptions)
    }
    solver = z3.Solver()
    derived = aba_sat._add_bitvec_ranked_closure_constraints(z3, solver, framework, variables)
    for assumption, variable in variables.items():
        solver.add(variable == (assumption in selected))

    assert solver.check() == z3.sat
    model = solver.model()
    ranked_closure = frozenset(
        literal
        for literal, variable in derived.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )

    assert ranked_closure == native_aba._closure(framework, selected)


def test_rules_by_consequent_groups_rules_deterministically() -> None:
    a1 = literal("a1")
    a2 = literal("a2")
    x = literal("x")
    y = literal("y")
    z = literal("z")
    first = Rule((a2,), x, "strict")
    second = Rule((a1,), x, "strict")
    third = Rule((x,), y, "strict")
    framework = ABAFramework(
        language=frozenset({a1, a2, x, y, z}),
        rules=frozenset({third, first, second}),
        assumptions=frozenset({a1, a2}),
        contrary={a1: y, a2: z},
    )

    grouped = aba_sat._rules_by_consequent(framework, tuple(sorted(framework.language, key=repr)))

    assert grouped[x] == tuple(sorted((first, second), key=repr))
    assert grouped[y] == (third,)
    assert grouped[z] == ()


def test_assumption_kernel_stable_witness_attacks_every_outsider() -> None:
    framework = _flat_aba(4, frozenset({(1, 2), (1, 3), (1, 4)}))
    kernel = aba_sat.AssumptionKernel.from_framework(framework)

    witness = kernel.stable_extension()

    assert witness == frozenset({literal("a1")})
    assert all(
        kernel.attacks(witness, assumption)
        for assumption in framework.assumptions - witness
    )


def test_assumption_kernel_stable_returns_none_when_no_stable_extension_exists() -> None:
    a = literal("a")
    ca = literal("ca")
    framework = ABAFramework(
        language=frozenset({a, ca}),
        rules=frozenset({Rule((a,), ca, "strict")}),
        assumptions=frozenset({a}),
        contrary={a: ca},
    )
    kernel = aba_sat.AssumptionKernel.from_framework(framework)

    assert kernel.stable_extension() is None


def test_assumption_kernel_preferred_grows_nonstable_admissible_witness() -> None:
    framework = _flat_aba(2, frozenset({(1, 1)}))
    kernel = aba_sat.AssumptionKernel.from_framework(framework)

    witness = kernel.preferred_extension()

    assert witness == frozenset({literal("a2")})
    assert native_aba.admissible(framework, witness)
    assert not any(
        witness < candidate and native_aba.admissible(framework, candidate)
        for candidate in native_aba._all_subsets(framework.assumptions)
    )


@given(flat_aba_frameworks())
@settings(deadline=10000, max_examples=40)
def test_assumption_kernel_stable_matches_native_oracle(
    framework: ABAFramework,
) -> None:
    kernel = aba_sat.AssumptionKernel.from_framework(framework)
    witness = kernel.stable_extension()
    native_extensions = native_aba.stable_extensions(framework)

    if witness is None:
        assert native_extensions == ()
    else:
        assert witness in native_extensions


@given(flat_aba_frameworks())
@settings(deadline=10000, max_examples=40)
def test_assumption_kernel_preferred_matches_native_oracle(
    framework: ABAFramework,
) -> None:
    kernel = aba_sat.AssumptionKernel.from_framework(framework)
    witness = kernel.preferred_extension()

    assert witness in native_aba.preferred_extensions(framework)


@given(flat_aba_frameworks(), st.data())
@settings(deadline=10000, max_examples=40)
def test_preferred_support_sat_preserves_required_assumptions(
    framework: ABAFramework,
    data: st.DataObject,
) -> None:
    assumptions = tuple(sorted(framework.assumptions, key=repr))
    required = data.draw(st.frozensets(st.sampled_from(assumptions), max_size=2))

    witness = aba_sat.sat_support_extension(
        framework,
        "preferred",
        require_assumptions=required,
    )

    if witness is None:
        assert not any(required <= extension for extension in native_aba.preferred_extensions(framework))
    else:
        assert required <= witness
        assert witness in native_aba.preferred_extensions(framework)


@given(flat_aba_frameworks(), st.sampled_from(["require_derived", "require_not_derived"]))
@settings(deadline=10000, max_examples=40)
def test_preferred_support_sat_query_constraints_match_derivability(
    framework: ABAFramework,
    constraint: str,
) -> None:
    query = sorted(framework.language, key=repr)[0]

    witness = aba_sat.sat_support_extension(
        framework,
        "preferred",
        require_derived=query if constraint == "require_derived" else None,
        require_not_derived=query if constraint == "require_not_derived" else None,
    )

    if witness is None:
        native_witnesses = native_aba.preferred_extensions(framework)
        if constraint == "require_derived":
            assert not any(native_aba.derives(framework, extension, query) for extension in native_witnesses)
        else:
            assert not any(not native_aba.derives(framework, extension, query) for extension in native_witnesses)
    elif constraint == "require_derived":
        assert native_aba.derives(framework, witness, query)
        assert witness in native_aba.preferred_extensions(framework)
    else:
        assert not native_aba.derives(framework, witness, query)
        assert witness in native_aba.preferred_extensions(framework)


@given(flat_aba_frameworks())
@settings(deadline=10000, max_examples=40)
def test_stable_shortcut_witness_is_preferred_member(framework: ABAFramework) -> None:
    witness = aba_sat.sat_stable_extension(framework)

    if witness is not None:
        assert witness in native_aba.preferred_extensions(framework)


def test_preferred_witness_uses_stable_shortcut_before_preprocessing(monkeypatch) -> None:
    framework = _flat_aba(3, frozenset({(1, 2)}))

    def forbidden_simplification(*args, **kwargs):
        raise AssertionError("preferred stable shortcut should run before ABA preprocessing")

    monkeypatch.setattr(aba_sat, "_aba_simplification", forbidden_simplification)

    witness = aba_sat.sat_support_extension(framework, "preferred")

    assert witness in native_aba.stable_extensions(framework)
    assert witness in native_aba.preferred_extensions(framework)


@given(
    flat_aba_frameworks(),
    st.sampled_from(["complete", "preferred"]),
    st.sampled_from(["credulous", "skeptical"]),
)
@settings(deadline=10000, max_examples=60)
def test_solve_aba_acceptance_support_sat_matches_native_oracle(
    framework: ABAFramework,
    semantics: str,
    task: str,
) -> None:
    query = sorted(framework.language, key=repr)[0]
    native_extensions = ABA_EXTENSION_ORACLES[semantics](framework)

    result = solve_aba_acceptance(
        framework,
        semantics=semantics,
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
