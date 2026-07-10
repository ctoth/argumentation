"""--jobs N on the native ICCMA runner must not change results, order, or logs.

The runner's row loop dispatches each row to its own worker subprocess; with
``--jobs N`` up to N rows run concurrently.  These tests pin the contract:
``--jobs 1`` (the default) is the exact serial loop, ``--jobs 2`` produces
identical per-row (status, answer) in identical manifest/job order with an
identical summary, the progress JSONL stays well-formed under concurrent
writers, and a CPU-contention caveat is printed only when jobs > 1.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import pytest

from tools.iccma2025_run_native import main, RunConfig, run_native

APX_CHAIN = "arg(a).\narg(b).\natt(a,b).\n"


def write_runner_fixture(tmp_path: Path) -> Path:
    """4 rows: {case1 (query a), case2 (query b)} x {DC-CO, DS-PR}."""
    root = tmp_path / "root"
    instances = root / "extracted" / "instances"
    instances.mkdir(parents=True)
    for name, query in (("case1.apx", "a"), ("case2.apx", "b")):
        (instances / name).write_text(APX_CHAIN, encoding="utf-8")
        (instances / f"{name}.arg").write_text(f"{query}\n", encoding="utf-8")

    manifests = root / "manifests"
    manifests.mkdir()
    (manifests / "iccma-2025-manifest.json").write_text(
        json.dumps(
            [
                {"kind": "apx", "relative_path": "case1.apx", "arguments_or_atoms": 2},
                {"kind": "apx", "relative_path": "case2.apx", "arguments_or_atoms": 2},
            ]
        ),
        encoding="utf-8",
    )
    (manifests / "iccma-2025-task-matrix.json").write_text(
        json.dumps(
            [
                {"track": "legacy", "subtrack": "DC-CO", "instance_kind": "af"},
                {"track": "legacy", "subtrack": "DS-PR", "instance_kind": "af"},
            ]
        ),
        encoding="utf-8",
    )
    return root


def run_runner(root: Path, *, label: str, jobs: int) -> list[dict[str, Any]]:
    exit_code = main(
        [
            "--root",
            str(root),
            "--label",
            label,
            "--timeout-seconds",
            "2",
            "--jobs",
            str(jobs),
            "--event-log-path",
            str(root / "runs" / f"{label}-events.jsonl"),
        ]
    )
    assert exit_code == 0
    output_path = root / "runs" / f"iccma-2025-{label}.json"
    return json.loads(output_path.read_text(encoding="utf-8"))


def row_cells(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [(row["instance"], row["subtrack"]) for row in rows]


def row_outcomes(rows: list[dict[str, Any]]) -> list[tuple[str, Any]]:
    return [(row["status"], row["answer"]) for row in rows]


def load_summary(root: Path, label: str) -> dict[str, Any]:
    path = root / "runs" / f"iccma-2025-{label}-summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_parallel_jobs_match_serial_results_and_job_order(tmp_path: Path) -> None:
    root = write_runner_fixture(tmp_path)

    serial = run_runner(root, label="serial", jobs=1)
    parallel = run_runner(root, label="parallel", jobs=2)

    expected_cells = [
        ("case1.apx", "DC-CO"),
        ("case1.apx", "DS-PR"),
        ("case2.apx", "DC-CO"),
        ("case2.apx", "DS-PR"),
    ]
    assert row_cells(serial) == expected_cells
    assert row_cells(parallel) == expected_cells
    assert row_outcomes(parallel) == row_outcomes(serial)
    assert row_outcomes(serial) == [
        ("solved", "true"),
        ("solved", "true"),
        ("solved", "false"),
        ("solved", "false"),
    ]
    assert load_summary(root, "parallel") == load_summary(root, "serial")
    assert load_summary(root, "serial")["by_status"] == {"solved": 4}


def test_parallel_event_log_lines_stay_wellformed(tmp_path: Path) -> None:
    root = write_runner_fixture(tmp_path)

    run_runner(root, label="parallel-log", jobs=2)

    lines = (
        (root / "runs" / "parallel-log-events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    events = [json.loads(line) for line in lines]
    starts = [event for event in events if event["event"] == "iccma_row_start"]
    rows = [event for event in events if event["event"] == "iccma_row"]
    assert sorted(event["index"] for event in starts) == [1, 2, 3, 4]
    assert sorted(event["index"] for event in rows) == [1, 2, 3, 4]
    assert all(event["total"] == 4 for event in starts + rows)


def test_run_native_parallel_keeps_job_order_despite_completion_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Later-submitted rows finish first; output must stay in job order."""
    total = 12
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "iccma-2025-manifest.json").write_text(
        json.dumps(
            [
                {
                    "kind": "apx",
                    "relative_path": f"case{index:02d}.apx",
                    "arguments_or_atoms": 1,
                }
                for index in range(1, total + 1)
            ]
        ),
        encoding="utf-8",
    )
    (manifests / "iccma-2025-task-matrix.json").write_text(
        json.dumps([{"track": "legacy", "subtrack": "SE-CO", "instance_kind": "af"}]),
        encoding="utf-8",
    )
    event_log_path = tmp_path / "events.jsonl"
    event_log_path.write_text("", encoding="utf-8")

    def reversed_latency_run_child(job: dict[str, Any], *, timeout_seconds: float):
        index = int(re.search(r"case(\d+)", job["instance"]["relative_path"]).group(1))
        time.sleep((total - index) * 0.01)
        return {"status": "solved", "reason": None, "answer": None, "error": None}

    monkeypatch.setattr(
        "tools.iccma2025_run_native.run_child", reversed_latency_run_child
    )
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=100,
        max_aba_assumptions=10,
        timeout_seconds=5.0,
        progress=True,
        event_log_path=event_log_path,
        jobs=4,
    )

    rows = run_native(config)

    assert [row["instance"] for row in rows] == [
        f"case{index:02d}.apx" for index in range(1, total + 1)
    ]
    events = [
        json.loads(line)
        for line in event_log_path.read_text(encoding="utf-8").splitlines()
    ]
    row_events = [event for event in events if event["event"] == "iccma_row"]
    start_events = [event for event in events if event["event"] == "iccma_row_start"]
    assert len(row_events) == total
    assert len(start_events) == total
    assert sorted(event["index"] for event in row_events) == list(range(1, total + 1))
    for event in row_events:
        assert event["instance"] == f"case{event['index']:02d}.apx"


def test_jobs_defaults_to_exact_serial(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, RunConfig] = {}

    def capture_run_native(config: RunConfig) -> list[dict[str, Any]]:
        captured["config"] = config
        return []

    monkeypatch.setattr("tools.iccma2025_run_native.run_native", capture_run_native)

    exit_code = main(["--root", str(tmp_path), "--label", "default-jobs"])

    assert exit_code == 0
    assert captured["config"].jobs == 1


def test_caveat_printed_only_when_parallel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    caveat = "include CPU contention noise"
    monkeypatch.setattr("tools.iccma2025_run_native.run_native", lambda config: [])

    main(["--root", str(tmp_path), "--label", "serial-quiet", "--jobs", "1"])
    assert caveat not in capsys.readouterr().out

    main(["--root", str(tmp_path), "--label", "parallel-noisy", "--jobs", "2"])
    assert caveat in capsys.readouterr().out
