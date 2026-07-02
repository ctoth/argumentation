"""Harness plumbing: AF worker SAT budget derivation and timeout-row mapping."""

from __future__ import annotations

from pathlib import Path

from argumentation.core.solver_results import SolverTimeout

from tools.iccma2025_run_native import solve_af_job


def _write_af_instance(tmp_path: Path, *, with_query: bool) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "case.af"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("p af 2\n1 2\n", encoding="utf-8")
    if with_query:
        Path(str(instance_path) + ".arg").write_text("1\n", encoding="utf-8")


def _af_job(tmp_path: Path, *, subtrack: str) -> dict[str, object]:
    return {
        "root": str(tmp_path),
        "backend": "auto",
        "solver_timeout_seconds": 15.0,
        "instance": {
            "kind": "af",
            "relative_path": "case.af",
            "arguments_or_atoms": 2,
        },
        "task": {
            "track": "main",
            "subtrack": subtrack,
            "instance_kind": "af",
        },
    }


def test_solve_af_job_derives_sat_check_budget_from_timeout(
    tmp_path, monkeypatch
) -> None:
    _write_af_instance(tmp_path, with_query=True)
    framework = object()
    captured: dict[str, object] = {}

    monkeypatch.setattr("argumentation.interop.iccma.parse_af", lambda text: framework)

    def fake_solve(framework_arg, **kwargs):
        from argumentation.solving.solver import AcceptanceSolverSuccess

        captured["kwargs"] = kwargs
        return AcceptanceSolverSuccess(answer=True)

    monkeypatch.setattr(
        "argumentation.solving.solver.solve_dung_acceptance", fake_solve
    )

    solve_af_job(_af_job(tmp_path, subtrack="DS-PR"))

    sat_config = captured["kwargs"]["sat"]
    # Mirrors the clingo derivation convention:
    # max(0.1, solver_timeout_seconds - 1.0) (tools/iccma2025_run_native.py).
    assert sat_config.check_budget_seconds == 14.0


def test_solve_af_job_maps_acceptance_solver_timeout_to_timeout_row(
    tmp_path, monkeypatch
) -> None:
    _write_af_instance(tmp_path, with_query=True)

    monkeypatch.setattr("argumentation.interop.iccma.parse_af", lambda text: object())

    def timed_out_solve(framework_arg, **kwargs):
        return SolverTimeout(
            backend="sat",
            problem="AF-preferred",
            message="Z3 returned unknown on AF SAT check 'preferred_skeptical_seed'",
            metadata={"check_budget_seconds": 14.0},
        )

    monkeypatch.setattr(
        "argumentation.solving.solver.solve_dung_acceptance", timed_out_solve
    )

    result = solve_af_job(_af_job(tmp_path, subtrack="DS-PR"))

    assert result["status"] == "timeout"
    assert result["reason"] == (
        "Z3 returned unknown on AF SAT check 'preferred_skeptical_seed'"
    )
    assert result["answer"] is None
    assert result["error"] is None
    assert result["solver_metadata"] == {"check_budget_seconds": 14.0}


def test_solve_af_job_maps_single_extension_solver_timeout_to_timeout_row(
    tmp_path, monkeypatch
) -> None:
    _write_af_instance(tmp_path, with_query=False)

    monkeypatch.setattr("argumentation.interop.iccma.parse_af", lambda text: object())

    def timed_out_solve(framework_arg, **kwargs):
        return SolverTimeout(
            backend="sat",
            problem="AF-stable",
            message="Z3 returned unknown on AF SAT check 'stable_extension'",
            metadata={"check_budget_seconds": 14.0},
        )

    monkeypatch.setattr(
        "argumentation.solving.solver.solve_dung_single_extension", timed_out_solve
    )

    result = solve_af_job(_af_job(tmp_path, subtrack="SE-ST"))

    assert result["status"] == "timeout"
    assert result["answer"] is None
    assert result["solver_metadata"] == {"check_budget_seconds": 14.0}
