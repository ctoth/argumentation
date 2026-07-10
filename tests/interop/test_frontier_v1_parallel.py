"""--jobs N on the frontier driver must not change results or row order."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.run_frontier_v1 import default_jobs, main

APX_CHAIN = "arg(a).\narg(b).\natt(a,b).\n"
APX_SINGLE = "arg(a).\n"


def write_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    instances = tmp_path / "root" / "extracted" / "instances"
    instances.mkdir(parents=True)
    for name, content, query in (
        ("case1.apx", APX_CHAIN, "a"),
        ("case2.apx", APX_CHAIN, "b"),
        ("case3.apx", APX_SINGLE, None),
        ("case4.apx", APX_CHAIN, "a"),
    ):
        (instances / name).write_text(content, encoding="utf-8")
        if query is not None:
            (instances / f"{name}.arg").write_text(f"{query}\n", encoding="utf-8")

    rows = [
        {
            "year": 2025,
            "track": "legacy",
            "subtrack": subtrack,
            "instance_kind": "apx",
            "relative_path": relative_path,
            "arguments_or_atoms": arguments,
            "recal_class": recal_class,
        }
        for subtrack, relative_path, arguments, recal_class in (
            ("DC-CO", "case1.apx", 2, "melt"),
            ("DC-CO", "case2.apx", 2, "melt"),
            ("SE-ST", "case3.apx", 1, "boundary_melt"),
            ("DS-PR", "case4.apx", 2, "melt"),
        )
    ]
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(rows), encoding="utf-8")
    return manifest, tmp_path / "root", tmp_path / "out"


def run_sweep(
    manifest: Path, root: Path, output_dir: Path, *, label: str, jobs: int
) -> dict[str, object]:
    exit_code = main(
        [
            "--manifest",
            str(manifest),
            "--root",
            str(root),
            "--output-dir",
            str(output_dir),
            "--timeout-seconds",
            "2",
            "--label",
            label,
            "--jobs",
            str(jobs),
        ]
    )
    assert exit_code == 0
    output_path = output_dir / f"iccma-2025-{label}-all.json"
    return json.loads(output_path.read_text(encoding="utf-8"))


def row_cells(payload: dict[str, object]) -> list[tuple[str, str]]:
    results: list[dict[str, dict[str, str]]] = payload["results"]  # type: ignore[assignment]
    return [
        (item["source"]["relative_path"], item["source"]["subtrack"])
        for item in results
    ]


def row_outcomes(payload: dict[str, object]) -> list[tuple[str, object]]:
    results: list[dict[str, dict[str, object]]] = payload["results"]  # type: ignore[assignment]
    return [
        (str(item["result"]["status"]), item["result"].get("answer"))
        for item in results
    ]


def test_parallel_jobs_match_serial_results_and_manifest_order(tmp_path: Path) -> None:
    manifest, root, output_dir = write_fixture(tmp_path)

    serial = run_sweep(manifest, root, output_dir, label="serial", jobs=1)
    parallel = run_sweep(manifest, root, output_dir, label="parallel", jobs=2)

    expected_cells = [
        ("case1.apx", "DC-CO"),
        ("case2.apx", "DC-CO"),
        ("case3.apx", "SE-ST"),
        ("case4.apx", "DS-PR"),
    ]
    assert row_cells(serial) == expected_cells
    assert row_cells(parallel) == expected_cells
    assert row_outcomes(parallel) == row_outcomes(serial)
    assert row_outcomes(serial) == [
        ("solved", "true"),
        ("solved", "false"),
        ("solved", None),
        ("solved", "true"),
    ]
    assert parallel["summary"] == serial["summary"]
    assert set(parallel) == set(serial)


def test_parallel_run_prints_contention_caveat(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest, root, output_dir = write_fixture(tmp_path)

    run_sweep(manifest, root, output_dir, label="serial-quiet", jobs=1)
    assert "contention" not in capsys.readouterr().out

    run_sweep(manifest, root, output_dir, label="parallel-noisy", jobs=2)
    assert "contention" in capsys.readouterr().out


def test_default_jobs_is_bounded() -> None:
    jobs = default_jobs()

    assert 1 <= jobs <= 8
