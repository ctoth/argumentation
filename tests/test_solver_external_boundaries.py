from __future__ import annotations

from hypothesis import given, settings, strategies as st

import argumentation.solver as solver_module
from argumentation.adf import (
    AbstractDialecticalFramework,
    ThreeValued,
    dung_to_adf,
    interpretation_to_mapping,
)
from argumentation.dung import (
    ArgumentationFramework,
    complete_extensions,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)
from argumentation.setaf import SETAF
from argumentation.solver import (
    ExtensionSolverSuccess,
    SolverBackendUnavailable,
    solve_adf_models,
    solve_setaf_extensions,
)
from tests.test_dung import argumentation_frameworks


ADF_DUNG_ORACLES = {
    "complete": complete_extensions,
    "grounded": lambda framework: [grounded_extension(framework)],
    "preferred": preferred_extensions,
    "stable": stable_extensions,
}

SETAF_DUNG_ORACLES = {
    "complete": complete_extensions,
    "grounded": lambda framework: [grounded_extension(framework)],
    "preferred": preferred_extensions,
    "stable": stable_extensions,
    "semi-stable": solver_module.semi_stable_extensions,
    "stage": solver_module.stage_extensions,
}


@given(
    argumentation_frameworks(max_args=4),
    st.sampled_from(sorted(ADF_DUNG_ORACLES)),
)
@settings(deadline=10000, max_examples=40)
def test_adf_native_models_preserve_dung_encoding(
    framework: ArgumentationFramework,
    semantics: str,
) -> None:
    result = solve_adf_models(dung_to_adf(framework), semantics=semantics)

    assert isinstance(result, ExtensionSolverSuccess)
    assert {_true_statements(model) for model in result.extensions} == set(
        ADF_DUNG_ORACLES[semantics](framework)
    )


@given(
    argumentation_frameworks(max_args=4),
    st.sampled_from(sorted(SETAF_DUNG_ORACLES)),
)
@settings(deadline=10000, max_examples=40)
def test_setaf_native_extensions_preserve_singleton_tail_dung_reduction(
    framework: ArgumentationFramework,
    semantics: str,
) -> None:
    setaf = SETAF(
        arguments=framework.arguments,
        attacks=frozenset(
            (frozenset({attacker}), target)
            for attacker, target in framework.defeats
        ),
    )

    result = solve_setaf_extensions(setaf, semantics=semantics)

    assert isinstance(result, ExtensionSolverSuccess)
    assert set(result.extensions) == set(SETAF_DUNG_ORACLES[semantics](framework))


@given(st.sampled_from(sorted(ADF_DUNG_ORACLES)))
@settings(deadline=10000, max_examples=10)
def test_adf_external_backend_is_unavailable_before_any_subprocess_claim(
    semantics: str,
) -> None:
    result = solve_adf_models(
        empty_adf(),
        semantics=semantics,
        backend="diamond",
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "diamond"
    assert result.reason == "external ADF solver backend is not source-backed"


@given(st.sampled_from(sorted(SETAF_DUNG_ORACLES)))
@settings(deadline=10000, max_examples=10)
def test_setaf_external_backend_is_unavailable_before_any_subprocess_claim(
    semantics: str,
) -> None:
    result = solve_setaf_extensions(
        SETAF(arguments=frozenset({"a"}), attacks=frozenset()),
        semantics=semantics,
        backend="aspartix",
    )

    assert isinstance(result, SolverBackendUnavailable)
    assert result.backend == "aspartix"
    assert result.reason == "external SETAF solver backend is not source-backed"


def empty_adf() -> AbstractDialecticalFramework:
    return dung_to_adf(ArgumentationFramework(arguments=frozenset(), defeats=frozenset()))


def _true_statements(model: frozenset[object]) -> frozenset[str]:
    values = interpretation_to_mapping(_adf_interpretation(model))
    return frozenset(
        statement
        for statement, value in values.items()
        if value is ThreeValued.T
    )


def _adf_interpretation(model: frozenset[object]):
    return frozenset(
        (statement, value)
        for statement, value in model
        if isinstance(statement, str) and isinstance(value, ThreeValued)
    )
