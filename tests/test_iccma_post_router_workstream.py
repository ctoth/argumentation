from __future__ import annotations

import sys
from pathlib import Path

from tools.iccma_post_router_workstream import (
    WorkstreamConfig,
    build_cap_command,
    build_replay_command,
    cap_output_paths,
    parse_args,
    summarize_fresh_timeouts,
    summarize_result_classes,
    summarize_timeout_classes,
    solver_class,
)


def _config(tmp_path: Path) -> WorkstreamConfig:
    return WorkstreamConfig(
        root=tmp_path / "2025",
        data_root=tmp_path,
        timeout_manifest=tmp_path / "timeouts.json",
        label="post-router-test",
        backend="auto",
        max_af_arguments=200,
        max_aba_assumptions=200,
        timeout_seconds=25.0,
        replay_timeout_seconds=30.0,
        stale_subtracks=("SE-PR", "SE-ST"),
    )


def test_build_replay_command_targets_stale_timeout_subtrack(tmp_path: Path) -> None:
    config = _config(tmp_path)
    output_path = tmp_path / "runs" / "SE-PR.json"

    command = build_replay_command(config, subtrack="SE-PR", output_path=output_path)

    assert command[:2] == [sys.executable, "tools/iccma_run_timeout_rows.py"]
    assert command[command.index("--timeouts") + 1] == str(config.timeout_manifest)
    assert command[command.index("--subtrack") + 1] == "SE-PR"
    assert command[command.index("--timeout-seconds") + 1] == "30.0"
    assert command[command.index("--backend") + 1] == "auto"
    assert command[command.index("--output") + 1] == str(output_path)


def test_build_cap_command_runs_bounded_cap_with_event_log(tmp_path: Path) -> None:
    config = _config(tmp_path)
    event_log_path = tmp_path / "events.jsonl"

    command = build_cap_command(config, event_log_path=event_log_path)

    assert command[:2] == [sys.executable, "tools/iccma2025_run_native.py"]
    assert command[command.index("--max-af-arguments") + 1] == "200"
    assert command[command.index("--max-aba-assumptions") + 1] == "200"
    assert command[command.index("--timeout-seconds") + 1] == "25.0"
    assert command[command.index("--event-log-path") + 1] == str(event_log_path)
    assert "--no-progress" not in command


def test_parse_args_defaults_to_post_router_cap200() -> None:
    config = parse_args([])

    assert config.max_af_arguments == 200
    assert config.max_aba_assumptions == 200
    assert config.timeout_seconds == 25.0
    assert config.replay_timeout_seconds == 30.0
    assert config.stale_subtracks == ("SE-PR", "SE-ST")


def test_cap_output_paths_uses_contest_tag(tmp_path: Path) -> None:
    root = tmp_path / "2025"
    manifests = root / "manifests"
    manifests.mkdir(parents=True)
    (manifests / "iccma-2025-manifest.json").write_text("[]\n", encoding="utf-8")
    config = WorkstreamConfig(
        root=root,
        data_root=tmp_path,
        timeout_manifest=tmp_path / "timeouts.json",
        label="post-router-test",
        backend="auto",
        max_af_arguments=200,
        max_aba_assumptions=200,
        timeout_seconds=25.0,
        replay_timeout_seconds=30.0,
        stale_subtracks=("SE-PR",),
    )

    paths = cap_output_paths(config)

    assert paths["csv"] == root / "runs" / "iccma-2025-post-router-test.csv"
    assert paths["summary"] == root / "runs" / "iccma-2025-post-router-test-summary.json"


def test_summarize_fresh_timeouts_reports_missing_csv(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"

    summary = summarize_fresh_timeouts(missing)

    assert summary == {
        "missing_csv": str(missing),
        "total_timeouts": None,
        "by_group": [],
        "by_solver_class": [],
    }


def test_solver_class_maps_iccma_subtrack_to_general_solver_class() -> None:
    assert solver_class("aba", "SE-PR") == "aba/single-extension/preferred"
    assert solver_class("af", "DS-SST") == "af/skeptical-acceptance/semi-stable"


def test_summarize_result_classes_groups_by_general_solver_class() -> None:
    results = [
        {
            "source": {"instance_kind": "aba", "subtrack": "SE-PR"},
            "result": {"status": "solved"},
        },
        {
            "source": {"instance_kind": "aba", "subtrack": "SE-PR"},
            "result": {"status": "timeout"},
        },
        {
            "source": {"instance_kind": "aba", "subtrack": "SE-ST"},
            "result": {"status": "solved"},
        },
    ]

    assert summarize_result_classes(results) == [
        {
            "solver_class": "aba/single-extension/preferred",
            "by_status": {"solved": 1, "timeout": 1},
            "total": 2,
        },
        {
            "solver_class": "aba/single-extension/stable",
            "by_status": {"solved": 1},
            "total": 1,
        },
    ]


def test_summarize_timeout_classes_counts_general_solver_classes() -> None:
    rows = [
        {"instance_kind": "aba", "subtrack": "SE-PR"},
        {"instance_kind": "aba", "subtrack": "SE-PR"},
        {"instance_kind": "af", "subtrack": "DS-SST"},
    ]

    assert summarize_timeout_classes(rows) == [
        {"solver_class": "aba/single-extension/preferred", "timeouts": 2},
        {"solver_class": "af/skeptical-acceptance/semi-stable", "timeouts": 1},
    ]
