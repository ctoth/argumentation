from __future__ import annotations

import json

import pytest
from hypothesis import given, settings, strategies as st

from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.dung import ArgumentationFramework
from argumentation.solver import (
    AcceptanceSolverSuccess,
    ExtensionSolverSuccess,
    SingleExtensionSolverSuccess,
    solve_aba_acceptance,
    solve_dung_extensions,
)
from argumentation.solver_differential import (
    assert_solver_results_agree,
    load_benchmark_manifest,
    run_benchmark_smoke,
    solver_capability_matrix,
)
from tests.test_dung import argumentation_frameworks


@given(argumentation_frameworks(max_args=4), st.sampled_from(["complete", "stable"]))
@settings(deadline=10000, max_examples=30)
def test_differential_helper_compares_generated_dung_enumeration(
    framework: ArgumentationFramework,
    semantics: str,
) -> None:
    native = solve_dung_extensions(framework, semantics=semantics, backend="native")
    sat = solve_dung_extensions(framework, semantics=semantics, backend="sat")

    assert_solver_results_agree("enumeration", native, sat)


@given(
    flat_aba_frameworks(),
    st.sampled_from(["complete", "stable"]),
    st.sampled_from(["credulous", "skeptical"]),
)
@settings(deadline=10000, max_examples=30)
def test_differential_helper_compares_generated_aba_acceptance(
    framework: ABAFramework,
    semantics: str,
    task: str,
) -> None:
    query = sorted(framework.language, key=repr)[0]
    native = solve_aba_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=query,
    )

    assert_solver_results_agree("acceptance", native, native)


def test_differential_helper_rejects_enumeration_single_extension_mismatch() -> None:
    with pytest.raises(
        AssertionError,
        match="cannot compare enumeration result to single-extension result",
    ):
        assert_solver_results_agree(
            "enumeration",
            ExtensionSolverSuccess((frozenset({"a"}),)),
            SingleExtensionSolverSuccess(frozenset({"a"})),
        )


def test_benchmark_smoke_reads_manifest_without_external_solver_execution(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            [
                {
                    "id": "tiny-af",
                    "formalism": "af",
                    "task": "SE",
                    "semantics": "stable",
                    "path": "fixtures/tiny.af",
                }
            ]
        ),
        encoding="utf-8",
    )

    manifest = load_benchmark_manifest(manifest_path)
    result = run_benchmark_smoke(manifest, execute_external=False)

    assert result.total == 1
    assert result.executed_external == 0
    assert result.skipped_external == 1


def test_capability_matrix_reports_unsupported_combinations_explicitly() -> None:
    matrix = solver_capability_matrix()

    assert matrix
    assert any(not entry.supported for entry in matrix)
    assert all(entry.reason for entry in matrix if not entry.supported)
    assert any(
        entry.formalism == "aba"
        and entry.backend == "iccma"
        and entry.task == "single-extension"
        and entry.semantics == "stable"
        and entry.supported
        for entry in matrix
    )


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
