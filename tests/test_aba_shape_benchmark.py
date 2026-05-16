from __future__ import annotations

import json
from pathlib import Path
import subprocess

from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.iccma import write_aba
from tools import aba_shape_benchmark
from tools.aba_shape_benchmark import (
    AbaShape,
    BenchmarkJob,
    best_solved_backend,
    build_backend_command,
    build_jobs_from_instances,
    build_jobs_from_manifest,
    compute_aba_shape,
    run_backend_command,
    shape_buckets,
    solver_class,
    summarize,
)


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def framework_zero_rules() -> ABAFramework:
    a = lit("a")
    b = lit("b")
    ca = lit("ca")
    cb = lit("cb")
    return ABAFramework(
        language=frozenset({a, b, ca, cb}),
        rules=frozenset(),
        assumptions=frozenset({a, b}),
        contrary={a: ca, b: cb},
    )


def framework_mixed_rules() -> ABAFramework:
    a = lit("a")
    b = lit("b")
    c = lit("c")
    d = lit("d")
    x = lit("x")
    y = lit("y")
    z = lit("z")
    return ABAFramework(
        language=frozenset({a, b, c, d, x, y, z}),
        rules=frozenset(
            {
                Rule((), x, "strict"),
                Rule((a,), x, "strict"),
                Rule((a, b, c), y, "strict"),
                Rule((b,), y, "strict"),
            }
        ),
        assumptions=frozenset({a, b, c}),
        contrary={a: x, b: x, c: y},
    )


def test_compute_aba_shape_handles_zero_rules() -> None:
    shape = compute_aba_shape(framework_zero_rules())

    assert shape.assumptions == 2
    assert shape.language_literals == 4
    assert shape.rules == 0
    assert shape.contraries == 2
    assert shape.distinct_contrary_literals == 2
    assert shape.avg_rule_arity == 0.0
    assert shape.max_rule_arity == 0
    assert shape.zero_body_rules == 0
    assert shape.rules_per_head_max == 0
    assert shape.rules_per_head_avg == 0.0
    assert shape.rules_per_contrary_max == 0
    assert shape.rules_per_contrary_avg == 0.0
    assert shape.assumption_to_language_ratio == 0.5
    assert shape.rule_to_assumption_ratio == 0.0


def test_compute_aba_shape_counts_rule_arity_heads_and_contraries() -> None:
    shape = compute_aba_shape(framework_mixed_rules())

    assert shape.assumptions == 3
    assert shape.rules == 4
    assert shape.contraries == 3
    assert shape.distinct_contrary_literals == 2
    assert shape.avg_rule_arity == 1.25
    assert shape.max_rule_arity == 3
    assert shape.zero_body_rules == 1
    assert shape.rules_per_head_max == 2
    assert shape.rules_per_head_avg == 2.0
    assert shape.rules_per_contrary_max == 2
    assert shape.rules_per_contrary_avg == 2.0


def test_compute_aba_shape_reports_grounded_reduct_collapse() -> None:
    shape = compute_aba_shape(framework_mixed_rules())

    assert shape.preprocessing_collapsed is True
    assert shape.grounded_fixed_out >= 1
    assert shape.residual_assumptions < shape.assumptions


def test_solver_class_maps_subtracks_to_general_class() -> None:
    assert solver_class("aba", "SE-PR") == "aba/single-extension/preferred"
    assert solver_class("aba", "SE-ST") == "aba/single-extension/stable"
    assert solver_class("aba", "DS-PR") == "aba/skeptical-acceptance/preferred"


def test_shape_buckets_use_structural_fields_only() -> None:
    shape = AbaShape(
        assumptions=200,
        language_literals=400,
        rules=6000,
        contraries=200,
        distinct_contrary_literals=200,
        avg_rule_arity=2.0,
        max_rule_arity=6,
        zero_body_rules=0,
        rules_per_head_max=10,
        rules_per_head_avg=4.0,
        rules_per_contrary_max=5,
        rules_per_contrary_avg=2.0,
        assumption_to_language_ratio=0.5,
        rule_to_assumption_ratio=30.0,
        grounded_fixed_in=0,
        grounded_fixed_out=0,
        residual_assumptions=200,
        residual_rules=6000,
        preprocessing_collapsed=False,
    )

    assert shape_buckets(shape, "aba/single-extension/preferred") == {
        "assumption_size": "large",
        "rule_density": "dense",
        "max_arity": "high",
        "preprocessing": "not_collapsed",
        "solver_class": "aba/single-extension/preferred",
    }


def test_build_jobs_from_manifest_filters_and_deduplicates(tmp_path: Path) -> None:
    rows = [
        {
            "year": 2025,
            "track": "aba",
            "subtrack": "SE-PR",
            "instance_kind": "aba",
            "instance": "ABAs/example.aba",
            "arguments_or_atoms": 10,
        },
        {
            "year": 2025,
            "track": "aba",
            "subtrack": "SE-PR",
            "instance_kind": "aba",
            "instance": "ABAs/example.aba",
            "arguments_or_atoms": 10,
        },
        {
            "year": 2025,
            "track": "aba",
            "subtrack": "SE-ST",
            "instance_kind": "aba",
            "instance": "ABAs/example.aba",
        },
    ]

    jobs = build_jobs_from_manifest(
        rows,
        data_root=tmp_path,
        years={2025},
        subtracks={"SE-PR"},
        instance_kind="aba",
    )

    assert jobs == [
        BenchmarkJob(
            year=2025,
            track="aba",
            subtrack="SE-PR",
            instance_kind="aba",
            instance="ABAs/example.aba",
            root=tmp_path / "2025",
            path=tmp_path / "2025" / "extracted" / "instances" / "ABAs" / "example.aba",
            arguments_or_atoms=10,
        )
    ]


def test_build_jobs_from_instances_preserves_path_only_as_locator(tmp_path: Path) -> None:
    root = tmp_path / "2025"
    instance_path = root / "extracted" / "instances" / "ABAs" / "shape-name-ignored.aba"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text(write_aba(framework_zero_rules()), encoding="utf-8")

    jobs = build_jobs_from_instances([instance_path], root=root, subtracks=("SE-PR", "SE-ST"))
    shapes = [
        compute_aba_shape(
            aba_shape_benchmark.parse_aba(job.path.read_text(encoding="utf-8"))
        )
        for job in jobs
    ]

    assert [job.instance for job in jobs] == [
        "ABAs/shape-name-ignored.aba",
        "ABAs/shape-name-ignored.aba",
    ]
    assert shapes[0] == shapes[1]
    assert all("shape-name-ignored" not in json.dumps(shape.__dict__) for shape in shapes)


def test_best_solved_backend_ignores_timeout_and_invalid() -> None:
    assert (
        best_solved_backend(
            {
                "asp": {
                    "status": "solved",
                    "elapsed_seconds": 2.0,
                    "validation": {"status": "invalid"},
                },
                "sat": {
                    "status": "solved",
                    "elapsed_seconds": 3.0,
                    "validation": {"status": "valid"},
                },
                "auto": {"status": "timeout", "elapsed_seconds": 1.0},
            }
        )
        == "sat"
    )


def test_build_backend_command_uses_explicit_backend_and_task(tmp_path: Path) -> None:
    job = BenchmarkJob(
        year=2025,
        track="aba",
        subtrack="SE-PR",
        instance_kind="aba",
        instance="ABAs/example.aba",
        root=tmp_path / "2025",
        path=tmp_path / "2025" / "extracted" / "instances" / "ABAs" / "example.aba",
        arguments_or_atoms=10,
    )

    command = build_backend_command(job, backend="asp", timeout_seconds=7.5)

    assert command[1] == "tools/iccma_run_selected.py"
    assert command[command.index("--backend") + 1] == "asp"
    assert command[command.index("--subtrack") + 1] == "SE-PR"
    assert command[command.index("--timeout-seconds") + 1] == "7.5"
    assert command[command.index("--arguments-or-atoms") + 1] == "10"


def test_run_backend_command_reports_outer_timeout(monkeypatch) -> None:
    def timeout_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(aba_shape_benchmark.subprocess, "run", timeout_run)

    result = run_backend_command(
        ["ignored"],
        timeout_seconds=0.1,
    )

    assert result["status"] == "timeout"
    assert result["reason"] == "benchmark_timeout>0.1"


def test_summary_is_order_invariant() -> None:
    row_a = {
        "solver_class": "aba/single-extension/preferred",
        "buckets": {"solver_class": "aba/single-extension/preferred", "assumption_size": "small"},
        "backend_results": {
            "auto": {"status": "solved"},
            "asp": {"status": "solved"},
            "sat": {"status": "timeout"},
        },
        "best_solved_backend": "auto",
        "all_timed_out": False,
    }
    row_b = {
        "solver_class": "aba/single-extension/stable",
        "buckets": {"solver_class": "aba/single-extension/stable", "assumption_size": "small"},
        "backend_results": {
            "auto": {"status": "timeout"},
            "asp": {"status": "timeout"},
            "sat": {"status": "timeout"},
        },
        "best_solved_backend": None,
        "all_timed_out": True,
    }

    assert summarize([row_a, row_b], backends=("auto", "asp", "sat")) == summarize(
        [row_b, row_a],
        backends=("auto", "asp", "sat"),
    )
