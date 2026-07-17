from __future__ import annotations

import json

import pytest

from tools.iccma2025_run_native import (
    RunConfig,
    budget_for_task,
    load_task_budgets,
    profile_duration_seconds,
    run_native,
    run_or_skip,
)


def _config(tmp_path, **overrides) -> RunConfig:
    base = dict(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=100,
        max_aba_assumptions=100,
        timeout_seconds=5.0,
        progress=False,
        event_log_path=None,
    )
    base.update(overrides)
    return RunConfig(**base)


def test_load_task_budgets_none_is_empty() -> None:
    assert load_task_budgets(None) == {}


def test_load_task_budgets_parses_numbers(tmp_path) -> None:
    path = tmp_path / "budgets.json"
    path.write_text(json.dumps({"DS-PR": 600, "SE-ST": 1200.5}), encoding="utf-8")

    assert load_task_budgets(path) == {"DS-PR": 600.0, "SE-ST": 1200.5}


@pytest.mark.parametrize(
    "payload",
    [
        [1, 2, 3],
        {"DS-PR": "600"},
        {"DS-PR": True},
        {"DS-PR": 0},
        {"DS-PR": -5},
    ],
)
def test_load_task_budgets_rejects_malformed(tmp_path, payload) -> None:
    path = tmp_path / "budgets.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError):
        load_task_budgets(path)


def test_budget_for_task_falls_back_to_flat_timeout(tmp_path) -> None:
    config = _config(tmp_path, timeout_seconds=7.5)
    task = {"track": "main", "subtrack": "DC-CO", "instance_kind": "af"}

    assert budget_for_task(config, task) == 7.5


def test_budget_for_task_uses_configured_subtrack_budget(tmp_path) -> None:
    config = _config(tmp_path, timeout_seconds=5.0, task_budgets={"DS-PR": 600.0})

    assert budget_for_task(config, {"subtrack": "DS-PR"}) == 600.0
    assert budget_for_task(config, {"subtrack": "SE-ST"}) == 5.0


def test_profile_duration_tracks_budget() -> None:
    assert profile_duration_seconds(600.0) == 599.0
    assert profile_duration_seconds(0.5) == 1.0


def test_empty_budgets_dispatch_is_byte_identical_to_flat_timeout(tmp_path, monkeypatch) -> None:
    """With no budgets the worker job and kill timeout must match the flat run exactly."""
    instance_path = tmp_path / "extracted" / "instances" / "case.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\n", encoding="utf-8")

    captured: list[tuple[dict[str, object], float]] = []

    def record_run_child(job, *, timeout_seconds):
        captured.append((job, timeout_seconds))
        return {"status": "solved", "reason": None, "answer": "true", "error": None}

    monkeypatch.setattr("tools.iccma2025_run_native.run_child", record_run_child)

    instance = {"kind": "apx", "relative_path": "case.apx", "arguments_or_atoms": 1}
    task = {"track": "main", "subtrack": "SE-CO", "instance_kind": "af"}

    flat = _config(tmp_path, timeout_seconds=5.0)
    empty_budgets = _config(tmp_path, timeout_seconds=5.0, task_budgets={})
    run_or_skip(flat, instance, task)
    run_or_skip(empty_budgets, instance, task)

    (flat_job, flat_timeout), (budget_job, budget_timeout) = captured
    assert flat_timeout == budget_timeout == 5.0
    assert flat_job == budget_job
    assert flat_job["solver_timeout_seconds"] == 5.0


def test_per_subtrack_budget_overrides_kill_and_solver_timeout(tmp_path, monkeypatch) -> None:
    """A configured subtrack budget must flow to BOTH the subprocess kill and the solver budget."""
    instance_path = tmp_path / "extracted" / "instances" / "case.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def record_run_child(job, *, timeout_seconds):
        captured["job"] = job
        captured["timeout_seconds"] = timeout_seconds
        return {"status": "solved", "reason": None, "answer": "true", "error": None}

    monkeypatch.setattr("tools.iccma2025_run_native.run_child", record_run_child)

    config = _config(tmp_path, timeout_seconds=5.0, task_budgets={"DS-PR": 600.0})
    instance = {"kind": "apx", "relative_path": "case.apx", "arguments_or_atoms": 1}
    # SE avoids the acceptance-query skip path so the worker job is actually built.
    task = {"track": "main", "subtrack": "SE-ST", "instance_kind": "af"}

    # SE-ST has no budget -> flat 5.0
    run_or_skip(config, instance, task)
    assert captured["timeout_seconds"] == 5.0
    assert captured["job"]["solver_timeout_seconds"] == 5.0

    # A budgeted SE subtrack -> 600 on both.
    config_budgeted = _config(tmp_path, timeout_seconds=5.0, task_budgets={"SE-ST": 600.0})
    run_or_skip(config_budgeted, instance, task)
    assert captured["timeout_seconds"] == 600.0
    assert captured["job"]["solver_timeout_seconds"] == 600.0


def test_only_tracks_filters_redundant_track_before_solving(tmp_path, monkeypatch) -> None:
    """--only-track drops the duplicate solve of the same instance under another track."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "iccma-2025-manifest.json").write_text(
        json.dumps([{"kind": "apx", "relative_path": "keep.apx", "arguments_or_atoms": 1}]),
        encoding="utf-8",
    )
    (manifests / "iccma-2025-task-matrix.json").write_text(
        json.dumps(
            [
                {"track": "main", "subtrack": "SE-CO", "instance_kind": "af"},
                {"track": "heuristics", "subtrack": "SE-CO", "instance_kind": "af"},
            ]
        ),
        encoding="utf-8",
    )
    seen: list[tuple[str, str]] = []

    def record_job(_config, instance, task):
        seen.append((task["track"], task["subtrack"]))
        return {"instance": instance["relative_path"], "track": task["track"], "status": "solved"}

    monkeypatch.setattr("tools.iccma2025_run_native.run_or_skip", record_job)
    config = _config(tmp_path, only_tracks=frozenset({"main"}))

    run_native(config)

    assert seen == [("main", "SE-CO")]


def test_empty_only_tracks_runs_every_track(tmp_path, monkeypatch) -> None:
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "iccma-2025-manifest.json").write_text(
        json.dumps([{"kind": "apx", "relative_path": "keep.apx", "arguments_or_atoms": 1}]),
        encoding="utf-8",
    )
    (manifests / "iccma-2025-task-matrix.json").write_text(
        json.dumps(
            [
                {"track": "main", "subtrack": "SE-CO", "instance_kind": "af"},
                {"track": "heuristics", "subtrack": "SE-CO", "instance_kind": "af"},
            ]
        ),
        encoding="utf-8",
    )
    seen: list[str] = []

    def record_job(_config, instance, task):
        seen.append(task["track"])
        return {"instance": instance["relative_path"], "track": task["track"], "status": "solved"}

    monkeypatch.setattr("tools.iccma2025_run_native.run_or_skip", record_job)
    config = _config(tmp_path)

    run_native(config)

    assert seen == ["main", "heuristics"]
