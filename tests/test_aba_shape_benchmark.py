from __future__ import annotations

import json
from pathlib import Path
import sys

from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.iccma import write_aba
from tools import aba_shape_benchmark
from tools.aba_shape_benchmark import (
    AbaShape,
    BenchmarkJob,
    backend_job,
    benchmark_rows,
    best_solved_backend,
    build_backend_command,
    build_jobs_from_instances,
    build_jobs_from_manifest,
    compute_aba_shape,
    propose_portfolio_rules,
    run_backend_command,
    shape_bucket_id,
    shape_buckets,
    solver_class,
    summarize,
    validate_result,
)


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def shape_for_bucket(
    *,
    assumptions: int,
    rule_density: float,
    max_arity: int,
    grounded_shape_status: str = "exact",
) -> AbaShape:
    rules = int(rule_density * max(assumptions, 1))
    return AbaShape(
        is_flat=True,
        is_normal=True,
        assumption_count=assumptions,
        atom_count=max(assumptions, 1),
        rule_count=rules,
        contrary_count=assumptions,
        assumptions=assumptions,
        language_literals=max(assumptions, 1),
        rules=rules,
        contraries=assumptions,
        distinct_contrary_literals=assumptions,
        avg_rule_arity=0.0,
        max_rule_arity=max_arity,
        zero_body_rules=0,
        rules_per_head_max=0,
        rules_per_head_avg=0.0,
        rules_per_contrary_max=0,
        rules_per_contrary_avg=0.0,
        assumption_to_language_ratio=1.0,
        rule_to_assumption_ratio=rule_density,
        grounded_fixed_in=0,
        grounded_fixed_out=0,
        residual_assumptions=assumptions,
        residual_rules=0,
        preprocessing_collapsed=False,
        grounded_shape_status=grounded_shape_status,
        rule_density=rule_density,
        dependency_scc_count=0,
        dependency_scc_max_size=0,
        dependency_cycle_count_or_flag=0,
        p_acyclic=True,
        contrary_target_in_degree_max=1 if assumptions else 0,
        contrary_target_in_degree_avg=1.0 if assumptions else 0.0,
        contrary_target_entropy=0.0,
        assumption_incidence_width_proxy=0,
        rule_body_overlap_max=0,
        rule_body_overlap_avg=0.0,
        closure_growth_sample=0.0,
        grounded_iteration_count=0,
        grounded_in_count=0,
        grounded_out_count=0,
        stable_obstruction_count=0,
        tau_aba_primal_width_proxy=0,
    )


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
    assert shape.grounded_shape_status == "exact"


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
    assert shape.grounded_shape_status == "exact"


def test_compute_aba_shape_skips_expensive_grounded_reduct() -> None:
    assumptions = frozenset(lit(f"a{index}") for index in range(40))
    contraries = {assumption: lit(f"c{index}") for index, assumption in enumerate(assumptions)}
    language = assumptions | frozenset(contraries.values()) | frozenset({lit("x")})
    rules = frozenset(
        Rule((assumption,), lit("x"), "strict")
        for assumption in assumptions
    )
    framework = ABAFramework(
        language=language,
        rules=rules,
        assumptions=assumptions,
        contrary=contraries,
    )

    shape = compute_aba_shape(framework)

    assert shape.grounded_shape_status == "skipped_cost"
    assert shape.residual_assumptions == shape.assumptions
    assert shape.residual_rules == shape.rules


def test_compute_aba_shape_handles_long_dependency_chain_iteratively() -> None:
    assumption = lit("a")
    chain = tuple(lit(f"x{index}") for index in range(1200))
    framework = ABAFramework(
        language=frozenset((assumption, *chain)),
        rules=frozenset(
            Rule((chain[index],), chain[index + 1], "strict")
            for index in range(len(chain) - 1)
        )
        | frozenset({Rule((assumption,), chain[0], "strict")}),
        assumptions=frozenset({assumption}),
        contrary={assumption: chain[-1]},
    )

    shape = compute_aba_shape(framework)

    assert shape.dependency_scc_count == len(chain)
    assert shape.dependency_scc_max_size == 1
    assert shape.p_acyclic is True


def test_compute_aba_shape_uses_bounded_rule_body_overlap_memory() -> None:
    shared = lit("shared")
    heads = tuple(lit(f"h{index}") for index in range(1500))
    framework = ABAFramework(
        language=frozenset((shared, *heads)),
        rules=frozenset(Rule((shared,), head, "strict") for head in heads),
        assumptions=frozenset({shared}),
        contrary={shared: heads[-1]},
    )

    shape = compute_aba_shape(framework)

    assert shape.rule_body_overlap_max == 1
    assert shape.rule_body_overlap_avg == 1.0


def test_validate_result_skips_expensive_python_validation() -> None:
    assumptions = frozenset(lit(f"a{index}") for index in range(40))
    contraries = {assumption: lit(f"c{index}") for index, assumption in enumerate(assumptions)}
    language = assumptions | frozenset(contraries.values()) | frozenset({lit("x")})
    rules = frozenset(Rule((assumption,), lit("x"), "strict") for assumption in assumptions)
    framework = ABAFramework(
        language=language,
        rules=rules,
        assumptions=assumptions,
        contrary=contraries,
    )

    result = validate_result(framework, "SE-PR", {"status": "solved", "witness": "a0"})

    assert result == {
        "status": "not_checked",
        "reason": "validation_cost>1000",
        "check": "skipped_cost",
    }


def test_solver_class_maps_subtracks_to_general_class() -> None:
    assert solver_class("aba", "SE-PR") == "aba/single-extension/preferred"
    assert solver_class("aba", "SE-ST") == "aba/single-extension/stable"
    assert solver_class("aba", "DS-PR") == "aba/skeptical-acceptance/preferred"


def test_shape_buckets_use_structural_fields_only() -> None:
    shape = shape_for_bucket(assumptions=200, rule_density=30.0, max_arity=6)

    assert shape_buckets(shape, "aba/single-extension/preferred") == {
        "assumption_size": "large",
        "rule_density": "dense",
        "max_arity": "high",
        "preprocessing": "not_collapsed",
        "solver_class": "aba/single-extension/preferred",
    }


def test_shape_bucket_id_is_deterministic() -> None:
    buckets = {
        "solver_class": "aba/single-extension/preferred",
        "max_arity": "low",
        "assumption_size": "small",
        "rule_density": "sparse",
        "preprocessing": "not_collapsed",
    }

    assert shape_bucket_id(buckets) == (
        "assumption_size=small|max_arity=low|preprocessing=not_collapsed|"
        "rule_density=sparse|solver_class=aba/single-extension/preferred"
    )


def test_shape_bucket_boundaries_are_inclusive() -> None:
    def bucketed(*, assumptions: int, rule_density: float, max_arity: int) -> dict[str, str]:
        shape = shape_for_bucket(
            assumptions=assumptions,
            rule_density=rule_density,
            max_arity=max_arity,
        )
        return shape_buckets(shape, "aba/single-extension/preferred")

    assert bucketed(assumptions=50, rule_density=5.0, max_arity=2) == {
        "assumption_size": "small",
        "rule_density": "sparse",
        "max_arity": "low",
        "preprocessing": "not_collapsed",
        "solver_class": "aba/single-extension/preferred",
    }
    assert bucketed(assumptions=51, rule_density=5.1, max_arity=3) == {
        "assumption_size": "medium",
        "rule_density": "medium",
        "max_arity": "medium",
        "preprocessing": "not_collapsed",
        "solver_class": "aba/single-extension/preferred",
    }
    assert bucketed(assumptions=150, rule_density=25.0, max_arity=5) == {
        "assumption_size": "medium",
        "rule_density": "medium",
        "max_arity": "medium",
        "preprocessing": "not_collapsed",
        "solver_class": "aba/single-extension/preferred",
    }
    assert bucketed(assumptions=151, rule_density=25.1, max_arity=6) == {
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


def test_benchmark_rows_emit_paper_route_features(monkeypatch, tmp_path: Path) -> None:
    instance_path = tmp_path / "2025" / "extracted" / "instances" / "ABAs" / "example.aba"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text(write_aba(framework_zero_rules()), encoding="utf-8")
    job = BenchmarkJob(
        year=2025,
        track="aba",
        subtrack="SE-PR",
        instance_kind="aba",
        instance="ABAs/example.aba",
        root=tmp_path / "2025",
        path=instance_path,
        arguments_or_atoms=4,
    )

    def backend_matrix(job, *, framework, backends, timeout_seconds):
        return {
            "asp": {
                "status": "solved",
                "elapsed_seconds": 0.1,
                "validation": {"status": "valid"},
                "witness_size": 0,
            },
            "sat": {
                "status": "timeout",
                "elapsed_seconds": timeout_seconds,
                "validation": {"status": "not_checked"},
            },
        }

    monkeypatch.setattr(aba_shape_benchmark, "run_backend_matrix", backend_matrix)

    rows = benchmark_rows([job], backends=("asp", "sat"), timeout_seconds=30)

    row = rows[0]
    assert set(row["shape"]) == set(AbaShape.__dataclass_fields__)
    assert row["shape_bucket_id"] == shape_bucket_id(row["buckets"])
    assert row["backend_outcomes"] == {"asp": "solved", "sat": "timeout"}
    assert row["witness_validation_results"] == {"asp": "valid", "sat": "not_checked"}
    assert row["route_candidates"]
    assert row["route_counterexamples"].keys() == {
        candidate["predicate"] for candidate in row["route_candidates"]
    }
    assert row["route_evidence_ids"] == []
    assert "path" not in row["shape"]
    assert "filename" not in row["shape"]
    assert "parent_directory" not in row["shape"]


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

    assert command[0] == sys.executable
    assert Path(command[1]).name == "iccma2025_run_native.py"
    assert command[2:] == ["_worker", "{job_path}"]
    payload = backend_job(job, backend="asp", timeout_seconds=7.5)
    assert payload["backend"] == "asp"
    assert payload["solver_timeout_seconds"] == 7.5
    assert payload["task"]["subtrack"] == "SE-PR"
    assert payload["instance"]["arguments_or_atoms"] == 10


def test_run_backend_command_reports_outer_timeout(monkeypatch) -> None:
    def timeout_child(job, *, timeout_seconds):
        return {"status": "timeout", "reason": f"timeout>{timeout_seconds}", "error": None}

    monkeypatch.setattr(aba_shape_benchmark, "run_native_child", timeout_child)

    result = run_backend_command(
        ["ignored"],
        job_payload={"ignored": True},
        timeout_seconds=0.1,
    )

    assert result["status"] == "timeout"
    assert result["reason"] == "timeout>0.1"


def test_benchmark_rows_keep_commands_out_of_feature_payload(monkeypatch, tmp_path: Path) -> None:
    instance_path = tmp_path / "2025" / "extracted" / "instances" / "ABAs" / "example.aba"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text(write_aba(framework_zero_rules()), encoding="utf-8")
    job = BenchmarkJob(
        year=2025,
        track="aba",
        subtrack="SE-PR",
        instance_kind="aba",
        instance="ABAs/example.aba",
        root=tmp_path / "2025",
        path=instance_path,
        arguments_or_atoms=4,
    )

    def solved_child(job_payload, *, timeout_seconds):
        return {"status": "solved", "witness": "", "backend": job_payload["backend"]}

    monkeypatch.setattr(aba_shape_benchmark, "run_native_child", solved_child)

    rows = benchmark_rows([job], backends=("asp",), timeout_seconds=30)

    assert "command" not in rows[0]["backend_results"]["asp"]


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


def test_portfolio_proposal_requires_no_bucket_counterexamples() -> None:
    bucket = {"solver_class": "aba/single-extension/preferred", "assumption_size": "small"}
    rows = [
        {
            "instance": "first.aba",
            "subtrack": "SE-PR",
            "solver_class": "aba/single-extension/preferred",
            "buckets": bucket,
            "backend_results": {"asp": {"status": "solved"}, "auto": {"status": "solved"}},
            "best_solved_backend": "asp",
            "all_timed_out": False,
        },
        {
            "instance": "second.aba",
            "subtrack": "SE-PR",
            "solver_class": "aba/single-extension/preferred",
            "buckets": bucket,
            "backend_results": {"asp": {"status": "solved"}, "auto": {"status": "solved"}},
            "best_solved_backend": "auto",
            "all_timed_out": False,
        },
    ]

    assert propose_portfolio_rules(rows, backends=("auto", "asp")) == []


def test_portfolio_proposal_records_evidence_and_empty_failures() -> None:
    bucket = {"solver_class": "aba/single-extension/preferred", "assumption_size": "small"}
    rows = [
        {
            "instance": "first.aba",
            "subtrack": "SE-PR",
            "solver_class": "aba/single-extension/preferred",
            "buckets": bucket,
            "backend_results": {"asp": {"status": "solved"}, "auto": {"status": "timeout"}},
            "best_solved_backend": "asp",
            "all_timed_out": False,
        },
        {
            "instance": "second.aba",
            "subtrack": "SE-PR",
            "solver_class": "aba/single-extension/preferred",
            "buckets": bucket,
            "backend_results": {"asp": {"status": "solved"}, "auto": {"status": "timeout"}},
            "best_solved_backend": "asp",
            "all_timed_out": False,
        },
    ]

    proposals = propose_portfolio_rules(rows, backends=("auto", "asp"))

    assert proposals == [
        {
            "backend": "asp",
            "candidate_rule": "prefer asp when shape_predicate matches",
            "confidence": "medium",
            "counterexamples": [],
            "evidence_rows": [
                {
                    "instance": "first.aba",
                    "solver_class": "aba/single-extension/preferred",
                    "subtrack": "SE-PR",
                },
                {
                    "instance": "second.aba",
                    "solver_class": "aba/single-extension/preferred",
                    "subtrack": "SE-PR",
                },
            ],
            "failures": [],
            "shape_predicate": bucket,
            "solver_classes": ["aba/single-extension/preferred"],
        }
    ]
