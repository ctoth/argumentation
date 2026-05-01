from __future__ import annotations

import lzma

from tools.iccma2025_run_native import (
    find_query_path,
    infer_task_matrix,
    read_instance_text,
    resolve_instance_path,
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
    with lzma.open(instance_path, mode="wt", encoding="utf-8") as handle:
        handle.write("arg(a).\n")
    with lzma.open(query_path, mode="wt", encoding="utf-8") as handle:
        handle.write("a\n")

    assert find_query_path(instance_path) == query_path
    assert read_instance_text(query_path) == "a\n"
