"""Differential comparison must accept any valid witness, not one fixed choice.

Stage extensions are conflict-free sets with subset-maximal range (Dvorak et
al. 2014, Def 3; papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/
notes.md). A single-extension solver may return any of them, and a credulous
witness may be any extension containing the query.
"""

from __future__ import annotations

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.solving.solver import (
    AcceptanceSolverSuccess,
    SingleExtensionSolverSuccess,
    solve_dung_extensions,
    solve_dung_single_extension,
)
from argumentation.solving.solver_differential import assert_solver_results_agree

# b attacks itself, a attacks c, c attacks b: the stage extensions are {a}
# (range {a, c}) and {c} (range {b, c}).
STAGE_FRAMEWORK = ArgumentationFramework(
    frozenset("abc"), frozenset({("b", "b"), ("a", "c"), ("c", "b")})
)


def _stage_extensions() -> tuple[frozenset[str], ...]:
    result = solve_dung_extensions(STAGE_FRAMEWORK, semantics="stage", backend="native")
    return tuple(result.extensions)  # type: ignore[union-attr]


def test_single_extension_accepts_different_valid_witnesses() -> None:
    """Issue #73: native and SAT may pick different stage extensions."""
    reference = _stage_extensions()
    assert set(reference) == {frozenset({"a"}), frozenset({"c"})}

    assert_solver_results_agree(
        "single-extension",
        SingleExtensionSolverSuccess(frozenset({"a"})),
        SingleExtensionSolverSuccess(frozenset({"c"})),
        reference_extensions=reference,
    )


def test_single_extension_solvers_agree_on_issue_framework() -> None:
    """Issue #73 reproduction with the real backends."""
    native = solve_dung_single_extension(
        STAGE_FRAMEWORK, semantics="stage", backend="native"
    )
    sat = solve_dung_single_extension(STAGE_FRAMEWORK, semantics="stage", backend="sat")

    assert_solver_results_agree(
        "single-extension", native, sat, reference_extensions=_stage_extensions()
    )


def test_single_extension_rejects_witness_that_is_not_an_extension() -> None:
    """Issue #73 control: {b} is not conflict-free (b attacks b), so it is
    no stage extension and the comparison must still fail."""
    with pytest.raises(AssertionError, match="not an extension"):
        assert_solver_results_agree(
            "single-extension",
            SingleExtensionSolverSuccess(frozenset({"a"})),
            SingleExtensionSolverSuccess(frozenset({"b"})),
            reference_extensions=_stage_extensions(),
        )


def test_single_extension_differing_witnesses_need_reference() -> None:
    """Issue #73: without reference extensions, differing witnesses cannot be
    validated, so the helper says so instead of reporting a disagreement."""
    with pytest.raises(AssertionError, match="reference_extensions"):
        assert_solver_results_agree(
            "single-extension",
            SingleExtensionSolverSuccess(frozenset({"a"})),
            SingleExtensionSolverSuccess(frozenset({"c"})),
        )


def test_single_extension_rejects_existence_disagreement() -> None:
    """Issue #73 control: one solver finding no extension is a real disagreement."""
    with pytest.raises(AssertionError, match="whether an extension exists"):
        assert_solver_results_agree(
            "single-extension",
            SingleExtensionSolverSuccess(frozenset({"a"})),
            SingleExtensionSolverSuccess(None),
            reference_extensions=_stage_extensions(),
        )


def test_single_extension_identical_witnesses_need_no_reference() -> None:
    """Issue #73 control: identical witnesses agree as before."""
    assert_solver_results_agree(
        "single-extension",
        SingleExtensionSolverSuccess(frozenset({"a"})),
        SingleExtensionSolverSuccess(frozenset({"a"})),
    )


def test_acceptance_accepts_different_valid_credulous_witnesses() -> None:
    """Issue #73: any extension containing the query is a valid credulous
    witness, so {a, d} and {c, d} both certify that d is accepted."""
    reference = (frozenset({"a", "d"}), frozenset({"c", "d"}))

    assert_solver_results_agree(
        "acceptance",
        AcceptanceSolverSuccess(answer=True, witness=frozenset({"a", "d"})),
        AcceptanceSolverSuccess(answer=True, witness=frozenset({"c", "d"})),
        reference_extensions=reference,
        query="d",
    )


def test_acceptance_accepts_different_valid_skeptical_counterexamples() -> None:
    """Issue #73: any extension omitting the query refutes skeptical acceptance."""
    reference = (frozenset({"a"}), frozenset({"c"}), frozenset({"a", "d"}))

    assert_solver_results_agree(
        "acceptance",
        AcceptanceSolverSuccess(answer=False, counterexample=frozenset({"a"})),
        AcceptanceSolverSuccess(answer=False, counterexample=frozenset({"c"})),
        reference_extensions=reference,
        query="d",
    )


def test_acceptance_rejects_witness_without_query() -> None:
    """Issue #73 control: a credulous witness must contain the query."""
    reference = (frozenset({"a"}), frozenset({"c", "d"}))

    with pytest.raises(AssertionError, match="does not contain the query"):
        assert_solver_results_agree(
            "acceptance",
            AcceptanceSolverSuccess(answer=True, witness=frozenset({"c", "d"})),
            AcceptanceSolverSuccess(answer=True, witness=frozenset({"a"})),
            reference_extensions=reference,
            query="d",
        )


def test_acceptance_rejects_different_answers() -> None:
    """Issue #73 control: the answers themselves must still agree."""
    with pytest.raises(AssertionError):
        assert_solver_results_agree(
            "acceptance",
            AcceptanceSolverSuccess(answer=True, witness=frozenset({"a"})),
            AcceptanceSolverSuccess(answer=False, counterexample=frozenset({"c"})),
            reference_extensions=(frozenset({"a"}), frozenset({"c"})),
            query="a",
        )
