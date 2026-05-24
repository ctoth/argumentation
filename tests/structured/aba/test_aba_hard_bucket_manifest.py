from __future__ import annotations

import json
from pathlib import Path

from tools.aba_shape_benchmark import benchmark_profile_path, build_jobs_from_manifest
from tools.run_aba_hard_bucket import benchmark_args, parse_args, selected_manifest


MANIFEST = Path("tests") / "manifests" / "aba-hard-bucket-targets.json"


def _rows() -> list[dict[str, object]]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_hard_bucket_manifest_has_exact_target_and_control_rows() -> None:
    rows = _rows()

    assert len(rows) == 12
    assert [row["target_id"] for row in rows] == [
        "T1",
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
        "T8",
        "T9",
        "C1",
        "C2",
        "C3",
    ]
    assert sum(str(row["target_id"]).startswith("T") for row in rows) == 9
    assert sum(str(row["target_id"]).startswith("C") for row in rows) == 3


def test_hard_bucket_manifest_has_no_duplicate_instance_subtrack_pairs() -> None:
    rows = _rows()
    pairs = [(row["instance"], row["subtrack"]) for row in rows]

    assert len(pairs) == len(set(pairs))


def test_hard_bucket_manifest_loads_as_benchmark_jobs_without_labels(tmp_path: Path) -> None:
    rows = _rows()

    jobs = build_jobs_from_manifest(
        rows,
        data_root=tmp_path,
        years={2025},
        subtracks={"SE-PR", "SE-ST"},
        instance_kind="aba",
    )

    assert len(jobs) == 12
    assert all(job.year == 2025 for job in jobs)
    assert all(job.instance_kind == "aba" for job in jobs)
    assert not any(hasattr(job, "target_id") for job in jobs)
    assert not any(hasattr(job, "gate_role") for job in jobs)


def test_hard_bucket_runner_defaults_to_exact_manifest_backend_matrix() -> None:
    args = parse_args([])
    command = benchmark_args(args)

    assert command[command.index("--timeouts") + 1] == str(MANIFEST)
    assert command[command.index("--timeout-seconds") + 1] == "30.0"
    assert command[command.index("--instance-kind") + 1] == "aba"
    assert command[command.index("--profile-format") + 1] == "speedscope"
    assert command[command.index("--profile-duration-seconds") + 1] == "25.0"
    assert "aba-hard-bucket-targets" in command[command.index("--profile-dir") + 1]
    assert _values_after(command, "--backend") == ["auto", "asp", "sat"]
    assert _values_after(command, "--subtrack") == ["SE-PR", "SE-ST"]


def test_hard_bucket_runner_explicit_backend_and_subtrack_replace_defaults() -> None:
    args = parse_args(["--backend", "sat", "--subtrack", "SE-PR"])
    command = benchmark_args(args)

    assert _values_after(command, "--backend") == ["sat"]
    assert _values_after(command, "--subtrack") == ["SE-PR"]


def test_hard_bucket_profile_paths_are_stable_and_backend_specific(tmp_path: Path) -> None:
    jobs = build_jobs_from_manifest(
        _rows(),
        data_root=tmp_path,
        years={2025},
        subtracks={"SE-PR", "SE-ST"},
        instance_kind="aba",
    )
    job = jobs[0]

    first = benchmark_profile_path(
        tmp_path / "profiles",
        job,
        backend="asp",
        profile_format="speedscope",
    )
    second = benchmark_profile_path(
        tmp_path / "profiles",
        job,
        backend="asp",
        profile_format="speedscope",
    )
    other_backend = benchmark_profile_path(
        tmp_path / "profiles",
        job,
        backend="sat",
        profile_format="speedscope",
    )

    assert first == second
    assert first != other_backend
    assert first is not None
    assert first.parent == tmp_path / "profiles"
    assert first.name.startswith("aba-SE-PR-asp-")
    assert first.name.endswith(".speedscope.json")


def test_hard_bucket_target_filter_writes_diagnostic_manifest(tmp_path: Path) -> None:
    output_json = tmp_path / "runs" / "selected.json"
    args = parse_args(
        [
            "--target-id",
            "T1",
            "--target-id",
            "C3",
            "--output-json",
            str(output_json),
        ]
    )

    manifest = selected_manifest(args)
    rows = json.loads(manifest.read_text(encoding="utf-8"))

    assert manifest == output_json.with_suffix(".manifest.json")
    assert [row["target_id"] for row in rows] == ["T1", "C3"]
    assert benchmark_args(args, manifest=manifest)[1] == str(manifest)


def _values_after(command: list[str], flag: str) -> list[str]:
    return [command[index + 1] for index, value in enumerate(command[:-1]) if value == flag]
