from __future__ import annotations

import json
import time

import pytest

from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_incremental import AbaIncrementalSolver, IncrementalTelemetry
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
import argumentation.solver as solver_module
from argumentation.solver import SingleExtensionSolverSuccess, solve_aba_single_extension
from tests import performance_contracts
from tests.performance_contracts import (
    CALIBRATION_ENV,
    ENABLE_ENV,
    assert_elapsed_within_budget,
    calibrated_budget,
    machine_slowdown_factor,
    require_perf_contracts_enabled,
)
from tools import perf_calibrate


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def no_attack_framework(size: int) -> ABAFramework:
    assumptions = frozenset(lit(f"a{index}") for index in range(size))
    contraries = {assumption: lit(f"ca{index}") for index, assumption in enumerate(assumptions)}
    return ABAFramework(
        language=assumptions | frozenset(contraries.values()),
        rules=frozenset(),
        assumptions=assumptions,
        contrary=contraries,
    )


def large_dense_stable_framework() -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(151))
    contraries = {assumption: lit(f"ca{index}") for index, assumption in enumerate(assumptions)}
    heads = tuple(lit(f"h{index}_{offset}") for index in range(151) for offset in range(26))
    rules = frozenset(
        Rule((assumptions[index],), heads[index * 26 + offset], "strict")
        for index in range(151)
        for offset in range(26)
    )
    return ABAFramework(
        language=frozenset(assumptions) | frozenset(contraries.values()) | frozenset(heads),
        rules=rules,
        assumptions=frozenset(assumptions),
        contrary=contraries,
    )


def test_calibration_payload_has_expected_shape() -> None:
    payload = perf_calibrate.calibration_payload(repeat=1)

    assert payload["schema_version"] == perf_calibrate.SCHEMA_VERSION
    assert payload["machine"]["python_version"]
    assert payload["machine"]["cpu_count"] >= 1
    names = {record["name"] for record in payload["benchmarks"]}
    assert {
        "python_integer_loop",
        "aba_parse",
        "aba_closure",
        "clingo_small_solve",
        "z3_small_check",
    } <= names
    for record in payload["benchmarks"]:
        assert record["status"] in {"ok", "skipped"}
        if record["status"] == "ok":
            assert record["elapsed_seconds"] >= 0
            assert record["median_seconds"] >= 0


def test_calibrated_budget_uses_fallback_without_calibration(monkeypatch) -> None:
    monkeypatch.delenv(CALIBRATION_ENV, raising=False)

    assert calibrated_budget("aba_no_attack_preferred") == (
        performance_contracts.FALLBACK_BUDGETS_SECONDS["aba_no_attack_preferred"]
    )


def test_calibrated_budget_uses_machine_slowdown_from_calibration(
    monkeypatch,
    tmp_path,
) -> None:
    payload = {
        "benchmarks": [
            {"name": "python_integer_loop", "status": "ok", "median_seconds": 0.04},
            {"name": "aba_parse", "status": "ok", "median_seconds": 0.004},
            {"name": "aba_closure", "status": "ok", "median_seconds": 0.002},
        ]
    }
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv(CALIBRATION_ENV, str(path))

    assert machine_slowdown_factor(payload) == 2.0
    assert calibrated_budget("aba_no_attack_preferred") == 0.5


def test_require_perf_contracts_enabled_skips_by_default(monkeypatch) -> None:
    monkeypatch.delenv(ENABLE_ENV, raising=False)

    with pytest.raises(pytest.skip.Exception):
        require_perf_contracts_enabled()


def test_no_attack_preferred_has_bounded_solver_calls() -> None:
    pytest.importorskip("clingo")
    framework = no_attack_framework(10)
    telemetry = IncrementalTelemetry()

    witness = AbaIncrementalSolver(framework).find_preferred_extension(telemetry=telemetry)

    assert witness == framework.assumptions
    assert telemetry.solver_calls <= 2
    assert telemetry.outer_iterations <= 1


def test_large_dense_stable_auto_route_uses_sat_without_asp(monkeypatch) -> None:
    framework = large_dense_stable_framework()
    witness = frozenset({min(framework.assumptions, key=repr)})

    def forbidden_asp(*args, **kwargs):
        raise AssertionError("large dense stable route should use SAT")

    monkeypatch.setattr(solver_module, "_has_clingo", lambda: True)
    monkeypatch.setattr(solver_module, "_solve_asp_aba_single_extension", forbidden_asp)
    monkeypatch.setattr(solver_module, "sat_aba_stable_extension", lambda framework: witness)

    result = solve_aba_single_extension(framework, semantics="stable")

    assert isinstance(result, SingleExtensionSolverSuccess)
    assert result.extension == witness


def test_opt_in_wall_clock_smoke_contract() -> None:
    require_perf_contracts_enabled()

    start = time.perf_counter()
    perf_calibrate.python_integer_loop()
    assert_elapsed_within_budget(time.perf_counter() - start, "python_integer_loop")
