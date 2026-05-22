from __future__ import annotations

import json
import lzma
from io import StringIO
from pathlib import Path

from tools.iccma_data import classify_file
from tools.iccma2025_run_native import (
    build_worker_command,
    find_query_path,
    infer_task_matrix,
    parse_worker_stdout,
    read_instance_text,
    resolve_instance_path,
    RunConfig,
    run_native,
    run_child,
    run_or_skip,
    solve_aba_job,
    worker_profile_path,
    write_csv,
)


def test_infer_task_matrix_uses_supported_legacy_result_subtracks(tmp_path) -> None:
    results = tmp_path / "extracted" / "results"
    results.mkdir(parents=True)
    (results / "DC-ST.results").write_text("", encoding="utf-8")
    (results / "EE-CO.results").write_text("", encoding="utf-8")
    (results / "SE-STG.results").write_text("", encoding="utf-8")
    (results / "D3.results").write_text("", encoding="utf-8")

    matrix = infer_task_matrix(tmp_path, [{"kind": "apx"}])

    assert matrix == [
        {"track": "legacy", "subtrack": "DC-ST", "instance_kind": "af"},
        {"track": "legacy", "subtrack": "SE-STG", "instance_kind": "af"},
    ]


def test_resolve_instance_path_handles_2017_archive_prefix_layout(tmp_path) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "A" / "A" / "2" / "case.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\n", encoding="utf-8")

    resolved = resolve_instance_path(
        tmp_path,
        {"archive": "benchmarks-a", "relative_path": "A/2/case.apx"},
    )

    assert resolved == instance_path


def test_compressed_query_companion_lookup_and_read(tmp_path) -> None:
    instance_path = tmp_path / "case.apx.lzma"
    query_path = tmp_path / "case.apx_arg.lzma"
    instance_path.write_bytes(lzma.compress(b"arg(a).\n"))
    query_path.write_bytes(lzma.compress(b"a\n"))

    assert find_query_path(instance_path) == query_path
    assert read_instance_text(query_path) == "a\n"


def test_manifest_counts_compressed_apx_instances(tmp_path) -> None:
    instance_path = tmp_path / "case.apx.lzma"
    instance_path.write_bytes(lzma.compress(b"arg(a).\narg(b).\natt(a,b).\n"))

    row = classify_file("instances", "case.apx.lzma", instance_path)

    assert row.kind == "compressed_apx"
    assert row.parse_status == "ok"
    assert row.arguments_or_atoms == 2
    assert row.attacks == 1


def test_run_or_skip_applies_cap_to_uncounted_compressed_apx(tmp_path, monkeypatch) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "case.apx.lzma"
    instance_path.parent.mkdir(parents=True)
    payload = "".join(f"arg(a{i}).\n" for i in range(21))
    instance_path.write_bytes(lzma.compress(payload.encode("utf-8")))

    def fail_run_child(*args, **kwargs):
        raise AssertionError("oversized compressed AF should be skipped before worker launch")

    monkeypatch.setattr("tools.iccma2025_run_native.run_child", fail_run_child)
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=20,
        max_aba_assumptions=10,
        timeout_seconds=5.0,
        progress=False,
        event_log_path=None,
    )
    instance = {
        "kind": "compressed_apx",
        "relative_path": "case.apx.lzma",
        "arguments_or_atoms": None,
    }
    task = {"track": "legacy", "subtrack": "SE-PR", "instance_kind": "af"}

    row = run_or_skip(config, instance, task)

    assert row["status"] == "skipped"
    assert row["reason"] == "af_argument_cap>20"
    assert row["arguments_or_atoms"] == 21


def test_run_or_skip_skips_missing_acceptance_query_before_worker(
    tmp_path,
    monkeypatch,
) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "case.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\n", encoding="utf-8")

    def fail_run_child(*args, **kwargs):
        raise AssertionError("queryless acceptance row should be skipped before worker launch")

    monkeypatch.setattr("tools.iccma2025_run_native.run_child", fail_run_child)
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=20,
        max_aba_assumptions=10,
        timeout_seconds=5.0,
        progress=False,
        event_log_path=None,
    )
    instance = {
        "kind": "apx",
        "relative_path": "case.apx",
        "arguments_or_atoms": 1,
    }
    task = {"track": "legacy", "subtrack": "DS-PR", "instance_kind": "af"}

    row = run_or_skip(config, instance, task)

    assert row["status"] == "skipped"
    assert row["reason"] == "missing_query"


def test_run_native_filters_exact_instance_and_subtrack_before_solving(
    tmp_path,
    monkeypatch,
) -> None:
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "iccma-2025-manifest.json").write_text(
        json.dumps(
            [
                {
                    "kind": "apx",
                    "relative_path": "keep.apx",
                    "arguments_or_atoms": 1,
                },
                {
                    "kind": "apx",
                    "relative_path": "skip.apx",
                    "arguments_or_atoms": 1,
                },
            ]
        ),
        encoding="utf-8",
    )
    (manifests / "iccma-2025-task-matrix.json").write_text(
        json.dumps(
            [
                {"track": "main", "subtrack": "SE-CO", "instance_kind": "af"},
                {"track": "main", "subtrack": "SE-PR", "instance_kind": "af"},
            ]
        ),
        encoding="utf-8",
    )
    seen: list[tuple[str, str]] = []

    def record_job(_config, instance, task):
        seen.append((instance["relative_path"], task["subtrack"]))
        return {
            "instance": instance["relative_path"],
            "subtrack": task["subtrack"],
            "status": "solved",
        }

    monkeypatch.setattr("tools.iccma2025_run_native.run_or_skip", record_job)
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=100,
        max_aba_assumptions=100,
        timeout_seconds=5.0,
        progress=False,
        event_log_path=None,
        only_instances=frozenset({"keep.apx"}),
        only_subtracks=frozenset({"SE-CO"}),
    )

    rows = run_native(config)

    assert seen == [("keep.apx", "SE-CO")]
    assert rows == [
        {
            "instance": "keep.apx",
            "subtrack": "SE-CO",
            "status": "solved",
        }
    ]


def test_run_child_streams_sat_check_events(tmp_path, capsys) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "case.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\narg(b).\natt(a,b).\n", encoding="utf-8")
    Path(str(instance_path) + ".arg").write_text("b\n", encoding="utf-8")
    job = {
        "root": str(tmp_path),
        "backend": "auto",
        "iccma_binary": None,
        "solver_timeout_seconds": 5.0,
        "instance": {
            "kind": "apx",
            "relative_path": "case.apx",
            "arguments_or_atoms": 2,
        },
        "task": {
            "track": "legacy",
            "subtrack": "DS-PR",
            "instance_kind": "af",
        },
    }

    result = run_child(job, timeout_seconds=15.0)

    assert result["status"] == "solved"
    assert result["answer"] == "false"
    stderr = capsys.readouterr().err
    assert '"event": "sat_check"' in stderr
    assert '"subtrack": "DS-PR"' in stderr


def test_run_child_writes_sat_check_events_to_event_log(tmp_path, capsys) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "case.apx"
    event_log_path = tmp_path / "events.jsonl"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\narg(b).\natt(a,b).\n", encoding="utf-8")
    Path(str(instance_path) + ".arg").write_text("b\n", encoding="utf-8")
    job = {
        "root": str(tmp_path),
        "backend": "auto",
        "iccma_binary": None,
        "solver_timeout_seconds": 5.0,
        "event_log_path": str(event_log_path),
        "instance": {
            "kind": "apx",
            "relative_path": "case.apx",
            "arguments_or_atoms": 2,
        },
        "task": {
            "track": "legacy",
            "subtrack": "DS-PR",
            "instance_kind": "af",
        },
    }

    result = run_child(job, timeout_seconds=15.0)

    assert result["status"] == "solved"
    assert capsys.readouterr().err == ""
    event_log = event_log_path.read_text(encoding="utf-8")
    assert '"event": "sat_check"' in event_log
    assert '"subtrack": "DS-PR"' in event_log


def test_run_child_streams_range_bound_sat_check_events(tmp_path, capsys) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "self_attacks.apx"
    instance_path.parent.mkdir(parents=True)
    # Self-attackers chained so none is a pure self-loop sink (which the AF
    # preprocessing layer would otherwise eliminate): the only conflict-free set
    # is still empty, so the range search exercises the max_range_at_least path.
    instance_path.write_text(
        "arg(a).\narg(b).\narg(c).\narg(d).\n"
        "att(a,a).\natt(b,b).\natt(c,c).\natt(d,d).\n"
        "att(b,a).\natt(c,b).\natt(d,c).\n",
        encoding="utf-8",
    )
    job = {
        "root": str(tmp_path),
        "backend": "auto",
        "iccma_binary": None,
        "solver_timeout_seconds": 5.0,
        "instance": {
            "kind": "apx",
            "relative_path": "self_attacks.apx",
            "arguments_or_atoms": 4,
        },
        "task": {
            "track": "legacy",
            "subtrack": "SE-STG",
            "instance_kind": "af",
        },
    }

    result = run_child(job, timeout_seconds=15.0)

    assert result["status"] == "solved"
    stderr = capsys.readouterr().err
    assert '"utility_name": "stage_max_range_at_least"' in stderr
    assert '"range_bound":' in stderr
    assert '"range_constraint": "at_least"' in stderr


def test_build_worker_command_wraps_profiled_worker_with_py_spy(tmp_path) -> None:
    profile_path = tmp_path / "profiles" / "row.speedscope.json"
    job_path = tmp_path / "job.json"
    command = build_worker_command(
        {
            "profile_path": str(profile_path),
            "profile_format": "speedscope",
            "profile_duration_seconds": 25.0,
        },
        job_path,
    )

    assert command[:6] == ["uv", "tool", "run", "py-spy", "record", "--subprocesses"]
    assert command[command.index("--duration") + 1] == "25"
    assert "--output" in command
    assert str(profile_path) in command
    assert Path(command[-3]).name == "iccma2025_run_native.py"
    assert command[-2:] == ["_worker", str(job_path)]


def test_worker_profile_path_is_stable_and_filterable(tmp_path) -> None:
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=200,
        max_aba_assumptions=10,
        timeout_seconds=5.0,
        progress=False,
        event_log_path=None,
        profile_workers_dir=tmp_path / "profiles",
        profile_workers_format="raw",
        profile_worker_subtracks=frozenset({"DS-PR"}),
    )
    instance = {
        "kind": "apx",
        "relative_path": "nested/path/Hard Case.apx",
    }
    task = {"track": "main", "subtrack": "DS-PR", "instance_kind": "af"}

    path = worker_profile_path(config, instance, task)

    assert path.parent == tmp_path / "profiles"
    assert path.name.startswith("main-DS-PR-Hard_Case.apx-")
    assert path.name.endswith(".raw.txt")


def test_run_or_skip_sets_profile_duration_inside_row_timeout(tmp_path, monkeypatch) -> None:
    captured: dict[str, object] = {}

    def record_run_child(job, *, timeout_seconds):
        captured["job"] = job
        captured["timeout_seconds"] = timeout_seconds
        return {"status": "profiled", "reason": "profile_duration_elapsed"}

    monkeypatch.setattr("tools.iccma2025_run_native.run_child", record_run_child)
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=100,
        max_aba_assumptions=100,
        timeout_seconds=30.0,
        progress=False,
        event_log_path=None,
        profile_workers_dir=tmp_path / "profiles",
        profile_workers_format="speedscope",
        profile_worker_subtracks=frozenset({"SE-PR"}),
    )

    row = run_or_skip(
        config,
        {
            "kind": "apx",
            "relative_path": "case.apx",
            "arguments_or_atoms": 1,
        },
        {"track": "main", "subtrack": "SE-PR", "instance_kind": "af"},
    )

    assert row["status"] == "profiled"
    assert captured["timeout_seconds"] == 30.0
    job = captured["job"]
    assert job["profile_duration_seconds"] == 29.0
    assert job["profile_path"]


def test_write_csv_accepts_profiled_rows(tmp_path) -> None:
    output = tmp_path / "rows.csv"

    write_csv(
        output,
        [
            {
                "track": "main",
                "subtrack": "SE-PR",
                "instance_kind": "aba",
                "instance": "case.aba",
                "backend": "auto",
                "status": "profiled",
                "reason": "profile_duration_elapsed",
                "elapsed_seconds": "30.000000",
                "answer": None,
                "profile_path": "profiles/case.speedscope.json",
                "solver_metadata": {"native_cnf_solver_checks": 1},
                "future_diagnostic_field": "ignored",
            }
        ],
    )

    header = output.read_text(encoding="utf-8").splitlines()[0]
    assert "profile_path" in header
    assert "solver_metadata" in header


def test_solve_aba_job_passes_clingo_diagnostics_to_single_extension(
    tmp_path, monkeypatch
) -> None:
    from argumentation.solver import SingleExtensionSolverSuccess

    instance_path = tmp_path / "extracted" / "instances" / "case.aba"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("ignored by parser monkeypatch\n", encoding="utf-8")
    framework = object()
    captured = {}

    monkeypatch.setattr("argumentation.iccma.parse_aba", lambda text: framework)

    def fake_solve(framework_arg, **kwargs):
        captured["framework"] = framework_arg
        captured["kwargs"] = kwargs
        return SingleExtensionSolverSuccess(
            extension=frozenset(),
            metadata={
                "solver": "clingo_multishot",
                "clingo_control_args": ("--models=0", "--warn=none", "--configuration=frumpy"),
                "clingo_statistics": {"solving": {"solvers": {"choices": 7.0}}},
            },
        )

    monkeypatch.setattr("argumentation.solver.solve_aba_single_extension", fake_solve)

    result = solve_aba_job(
        {
            "root": str(tmp_path),
            "backend": "auto",
            "solver_timeout_seconds": 40,
            "clingo_control_args": ["--configuration=frumpy"],
            "collect_clingo_statistics": True,
            "instance": {
                "kind": "aba",
                "relative_path": "case.aba",
                "arguments_or_atoms": 1,
            },
            "task": {
                "track": "main",
                "subtrack": "SE-ST",
                "instance_kind": "aba",
            },
        }
    )

    assert captured["framework"] is framework
    assert captured["kwargs"]["semantics"] == "stable"
    assert captured["kwargs"]["backend"] == "auto"
    assert captured["kwargs"]["clingo_control_args"] == ("--configuration=frumpy",)
    assert captured["kwargs"]["collect_clingo_statistics"] is True
    assert captured["kwargs"]["clingo_solve_timeout_seconds"] == 39.0
    assert result["solver_metadata"]["clingo_statistics"] == {
        "solving": {"solvers": {"choices": 7.0}}
    }


def test_solve_aba_job_defaults_clingo_diagnostics_to_disabled(tmp_path, monkeypatch) -> None:
    from argumentation.solver import SingleExtensionSolverSuccess

    instance_path = tmp_path / "extracted" / "instances" / "case.aba"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("ignored by parser monkeypatch\n", encoding="utf-8")
    captured = {}

    monkeypatch.setattr("argumentation.iccma.parse_aba", lambda text: object())

    def fake_solve(framework_arg, **kwargs):
        captured["kwargs"] = kwargs
        return SingleExtensionSolverSuccess(
            extension=frozenset(),
            metadata={
                "solver": "clingo_multishot",
                "clingo_control_args": ("--models=0", "--warn=none"),
            },
        )

    monkeypatch.setattr("argumentation.solver.solve_aba_single_extension", fake_solve)

    solve_aba_job(
        {
            "root": str(tmp_path),
            "backend": "auto",
            "solver_timeout_seconds": 40,
            "instance": {
                "kind": "aba",
                "relative_path": "case.aba",
                "arguments_or_atoms": 1,
            },
            "task": {
                "track": "main",
                "subtrack": "SE-ST",
                "instance_kind": "aba",
            },
        }
    )

    assert captured["kwargs"]["clingo_control_args"] == ()
    assert captured["kwargs"]["collect_clingo_statistics"] is False
    assert captured["kwargs"]["clingo_solve_timeout_seconds"] is None


def test_parse_worker_stdout_accepts_py_spy_wrapped_output() -> None:
    parsed = parse_worker_stdout(
        "py-spy> Sampling process 100 times a second.\n"
        '{"answer": "false", "status": "solved"}\n'
        "py-spy> Wrote speedscope file.\n"
    )

    assert parsed == {"answer": "false", "status": "solved"}


def test_run_child_reports_profile_duration_without_worker_json(tmp_path, monkeypatch) -> None:
    profile_path = tmp_path / "profiles" / "row.speedscope.json"

    class CompletedProfileProcess:
        stdout = StringIO("py-spy> Sampling process 100 times a second for 1 seconds...\n")
        stderr = StringIO("")

        def wait(self, timeout):
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            profile_path.write_text("{}", encoding="utf-8")
            return 0

        def kill(self):
            raise AssertionError("profiled worker should not need timeout kill")

    monkeypatch.setattr(
        "tools.iccma2025_run_native.subprocess.Popen",
        lambda *args, **kwargs: CompletedProfileProcess(),
    )

    result = run_child(
        {
            "profile_path": str(profile_path),
            "profile_duration_seconds": 1,
        },
        timeout_seconds=2.0,
    )

    assert result == {
        "status": "profiled",
        "reason": "profile_duration_elapsed",
        "error": None,
        "profile_path": str(profile_path),
    }
