from __future__ import annotations

import lzma
from pathlib import Path

from tools.iccma_data import classify_file
from tools.iccma2025_run_native import (
    find_query_path,
    infer_task_matrix,
    read_instance_text,
    resolve_instance_path,
    RunConfig,
    run_child,
    run_or_skip,
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


def test_run_child_streams_range_bound_sat_check_events(tmp_path, capsys) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "cycle.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text(
        "arg(a).\narg(b).\narg(c).\natt(a,b).\natt(b,c).\natt(c,a).\n",
        encoding="utf-8",
    )
    job = {
        "root": str(tmp_path),
        "backend": "auto",
        "iccma_binary": None,
        "solver_timeout_seconds": 5.0,
        "instance": {
            "kind": "apx",
            "relative_path": "cycle.apx",
            "arguments_or_atoms": 3,
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
