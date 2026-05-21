from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation import solver
from argumentation.aba import ABAFramework
from argumentation.aba_sat import NativeSparseNarrowSatResult
from argumentation.aba_route_policy import (
    SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
    sparse_narrow_native_sat_shape,
)
from argumentation.aspic import GroundAtom, Literal, Rule


FORBIDDEN_LOCATOR_KEYS = {
    "archive",
    "basename",
    "filename",
    "instance",
    "label",
    "parent",
    "path",
    "relative_path",
    "year",
}


def test_sparse_narrow_page_image_contract_is_complete() -> None:
    assert len(SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES) == 16
    assert all(path.endswith(".png") for path in SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES)


@given(
    assumptions=st.integers(min_value=700, max_value=706),
    rule_ratio=st.integers(min_value=4, max_value=7),
)
@settings(max_examples=8, deadline=None)
def test_sparse_narrow_route_is_shape_based(assumptions: int, rule_ratio: int) -> None:
    framework = sparse_narrow_framework(assumptions, rule_ratio=rule_ratio)

    assert sparse_narrow_native_sat_shape(framework)


def test_sparse_narrow_route_rejects_locator_metadata() -> None:
    framework = sparse_narrow_framework(700, rule_ratio=4)
    left = {
        "path": "C:/iccma/2025/ABAs/abcgen_c7_atoms100_asms200.aba",
        "filename": "abcgen_c7_atoms100_asms200.aba",
        "year": 2025,
        "relative_path": "ABAs/abcgen_c7_atoms100_asms200.aba",
    }
    right = {
        "path": "D:/renamed/local/input.aba",
        "filename": "input.aba",
        "year": 2011,
        "relative_path": "renamed/input.aba",
    }

    assert sparse_narrow_native_sat_shape(framework, locator_metadata=left)
    assert sparse_narrow_native_sat_shape(framework, locator_metadata=right)


def test_auto_single_extension_sparse_narrow_stable_uses_clingo_when_available(monkeypatch) -> None:
    framework = sparse_narrow_framework(700, rule_ratio=4)
    monkeypatch.setattr(solver, "_has_clingo", lambda: True)

    def asp_spy(
        received: ABAFramework,
        routed_semantics: str,
        backend: str,
        *,
        clingo_control_args=(),
        collect_clingo_statistics=False,
    ):
        assert received == framework
        assert routed_semantics == "stable"
        assert backend == "asp"
        assert clingo_control_args == ()
        assert collect_clingo_statistics is False
        return solver.SingleExtensionSolverSuccess(
            extension=frozenset(),
            metadata={
                "backend": "asp",
                "semantics": "stable",
                "solver": "clingo_multishot",
                "algorithm": "first-model-witness",
                "clingo_control_args": ("--models=0", "--warn=none"),
            },
        )

    def forbidden_native(*args, **kwargs):
        raise AssertionError("sparse/narrow stable auto route must call clingo")

    monkeypatch.setattr(solver, "_solve_asp_aba_single_extension", asp_spy)
    monkeypatch.setattr(solver, "native_sparse_narrow_aba_extension", forbidden_native)
    result = solver.solve_aba_single_extension(
        framework,
        semantics="stable",
        backend="auto",
    )

    assert result.metadata is not None
    assert result.metadata["backend"] == "asp"
    assert result.metadata["semantics"] == "stable"
    assert result.metadata["solver"] == "clingo_multishot"
    assert result.metadata["algorithm"] == "first-model-witness"
    assert result.metadata["clingo_control_args"] == ("--models=0", "--warn=none")
    assert "clingo_statistics" not in result.metadata


def test_explicit_sat_single_extension_sparse_narrow_stable_uses_native_sat(monkeypatch) -> None:
    framework = sparse_narrow_framework(700, rule_ratio=4)
    monkeypatch.setattr(solver, "_has_clingo", lambda: True)

    def forbidden_asp(*args, **kwargs):
        raise AssertionError("explicit sparse/narrow SAT route must not call clingo")

    def native_spy(received: ABAFramework, routed_semantics: str):
        assert received == framework
        assert routed_semantics == "stable"
        return NativeSparseNarrowSatResult(
            extension=frozenset(),
            telemetry={
                "clingo_solver_calls": 0,
                "native_sparse_narrow_solver_checks": 1,
                "native_sparse_narrow_z3_main_checks": 0,
            },
            route_metadata={
                "backend": "sat",
                "algorithm": "native_sparse_narrow_sat",
                "semantics": "stable",
                "clingo_solver_calls": 0,
                "paper_page_images": SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
            },
        )

    monkeypatch.setattr(solver, "_solve_asp_aba_single_extension", forbidden_asp)
    monkeypatch.setattr(solver, "native_sparse_narrow_aba_extension", native_spy)
    result = solver.solve_aba_single_extension(
        framework,
        semantics="stable",
        backend="sat",
    )

    assert result.metadata is not None
    assert result.metadata["backend"] == "sat"
    assert result.metadata["algorithm"] == "native_sparse_narrow_sat"
    assert result.metadata["semantics"] == "stable"
    assert result.metadata["clingo_solver_calls"] == 0
    assert result.metadata["paper_page_images"] == SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES
    assert not (FORBIDDEN_LOCATOR_KEYS & set(result.metadata))


def test_auto_single_extension_sparse_narrow_preferred_keeps_native_sat(monkeypatch) -> None:
    framework = sparse_narrow_framework(700, rule_ratio=4)
    monkeypatch.setattr(solver, "_has_clingo", lambda: True)

    def forbidden_asp(*args, **kwargs):
        raise AssertionError("preferred sparse/narrow auto route is not owned by this workstream")

    def native_spy(received: ABAFramework, routed_semantics: str):
        assert received == framework
        assert routed_semantics == "preferred"
        return NativeSparseNarrowSatResult(
            extension=frozenset(),
            telemetry={
                "clingo_solver_calls": 0,
                "native_sparse_narrow_solver_checks": 1,
                "native_sparse_narrow_z3_main_checks": 0,
            },
            route_metadata={
                "backend": "sat",
                "algorithm": "native_sparse_narrow_sat",
                "semantics": "preferred",
                "clingo_solver_calls": 0,
                "paper_page_images": SPARSE_NARROW_NATIVE_SAT_PAGE_IMAGES,
            },
        )

    monkeypatch.setattr(solver, "_solve_asp_aba_single_extension", forbidden_asp)
    monkeypatch.setattr(solver, "native_sparse_narrow_aba_extension", native_spy)
    result = solver.solve_aba_single_extension(
        framework,
        semantics="preferred",
        backend="auto",
    )

    assert result.metadata is not None
    assert result.metadata["backend"] == "sat"
    assert result.metadata["algorithm"] == "native_sparse_narrow_sat"
    assert result.metadata["semantics"] == "preferred"


def sparse_narrow_framework(assumptions: int, *, rule_ratio: int) -> ABAFramework:
    assumption_literals = tuple(lit(f"a{index}") for index in range(assumptions))
    atom_count = assumptions * 4
    atoms = tuple(lit(f"x{index}") for index in range(atom_count))
    rules = []
    for index in range(assumptions * rule_ratio):
        head = atoms[index % atom_count]
        if index % 5 == 0:
            body = (assumption_literals[index % assumptions],)
        else:
            body = (
                assumption_literals[index % assumptions],
                atoms[(index * 3 + 1) % atom_count],
            )
        rules.append(Rule(body, head, "strict"))
    return ABAFramework(
        language=frozenset((*assumption_literals, *atoms)),
        assumptions=frozenset(assumption_literals),
        contrary={
            assumption: atoms[index % atom_count]
            for index, assumption in enumerate(assumption_literals)
        },
        rules=frozenset(rules),
    )


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))
