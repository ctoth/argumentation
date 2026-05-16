from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from argumentation import aba as native_aba
from argumentation.aba import ABAFramework, AssumptionSet
from argumentation.aba_preprocessing import simplify_aba
from argumentation.aspic import GroundAtom, Literal
from argumentation.iccma import parse_aba
from tools.iccma2025_run_native import TASK_TO_SEMANTICS
from tools.iccma_run_selected import run_selected


DEFAULT_ROOT = Path("data") / "iccma" / "2025"
DEFAULT_DATA_ROOT = Path("data") / "iccma"
DEFAULT_SUBTRACKS = ("SE-PR", "SE-ST")
DEFAULT_BACKENDS = ("auto", "asp", "sat")

TASK_PREFIXES = {
    "DC": "credulous-acceptance",
    "DS": "skeptical-acceptance",
    "SE": "single-extension",
}

ASSUMPTION_SIZE_THRESHOLDS = {"small_max": 50, "medium_max": 150}
RULE_DENSITY_THRESHOLDS = {"sparse_max": 5.0, "medium_max": 25.0}
MAX_ARITY_THRESHOLDS = {"low_max": 2, "medium_max": 5}


@dataclass(frozen=True)
class AbaShape:
    assumptions: int
    language_literals: int
    rules: int
    contraries: int
    distinct_contrary_literals: int
    avg_rule_arity: float
    max_rule_arity: int
    zero_body_rules: int
    rules_per_head_max: int
    rules_per_head_avg: float
    rules_per_contrary_max: int
    rules_per_contrary_avg: float
    assumption_to_language_ratio: float
    rule_to_assumption_ratio: float
    grounded_fixed_in: int
    grounded_fixed_out: int
    residual_assumptions: int
    residual_rules: int
    preprocessing_collapsed: bool


@dataclass(frozen=True)
class BenchmarkJob:
    year: int | None
    track: str
    subtrack: str
    instance_kind: str
    instance: str
    root: Path
    path: Path
    arguments_or_atoms: int | None = None


def compute_aba_shape(framework: ABAFramework) -> AbaShape:
    arities = [len(rule.antecedents) for rule in framework.rules]
    rules_by_head = Counter(rule.consequent for rule in framework.rules)
    contrary_literals = tuple(framework.contrary.values())
    rules_by_contrary = Counter(
        rule.consequent for rule in framework.rules if rule.consequent in set(contrary_literals)
    )
    simplification = simplify_aba(framework, semantics="preferred")
    assumptions = len(framework.assumptions)
    language_literals = len(framework.language)
    rules = len(framework.rules)
    return AbaShape(
        assumptions=assumptions,
        language_literals=language_literals,
        rules=rules,
        contraries=len(framework.contrary),
        distinct_contrary_literals=len(set(contrary_literals)),
        avg_rule_arity=_average(arities),
        max_rule_arity=max(arities, default=0),
        zero_body_rules=sum(1 for arity in arities if arity == 0),
        rules_per_head_max=max(rules_by_head.values(), default=0),
        rules_per_head_avg=_average(rules_by_head.values()),
        rules_per_contrary_max=max(rules_by_contrary.values(), default=0),
        rules_per_contrary_avg=_average(rules_by_contrary.values()),
        assumption_to_language_ratio=_ratio(assumptions, language_literals),
        rule_to_assumption_ratio=_ratio(rules, assumptions),
        grounded_fixed_in=len(simplification.fixed_in),
        grounded_fixed_out=len(simplification.fixed_out),
        residual_assumptions=len(simplification.residual.assumptions),
        residual_rules=len(simplification.residual.rules),
        preprocessing_collapsed=not simplification.is_trivial,
    )


def _average(values: Iterable[int]) -> float:
    materialized = list(values)
    if not materialized:
        return 0.0
    return sum(materialized) / len(materialized)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def solver_class(instance_kind: object, subtrack: object) -> str:
    parts = str(subtrack).split("-", maxsplit=1)
    if len(parts) != 2:
        return f"{instance_kind}/unknown/{subtrack}"
    task_prefix, semantic_tag = parts
    task = TASK_PREFIXES.get(task_prefix, task_prefix.lower())
    semantics = TASK_TO_SEMANTICS.get(semantic_tag, semantic_tag.lower())
    return f"{instance_kind}/{task}/{semantics}"


def shape_buckets(shape: AbaShape, solver_class_name: str) -> dict[str, str]:
    return {
        "assumption_size": _bucket_int(
            shape.assumptions,
            small_max=ASSUMPTION_SIZE_THRESHOLDS["small_max"],
            medium_max=ASSUMPTION_SIZE_THRESHOLDS["medium_max"],
        ),
        "rule_density": _bucket_float(
            shape.rule_to_assumption_ratio,
            sparse_max=RULE_DENSITY_THRESHOLDS["sparse_max"],
            medium_max=RULE_DENSITY_THRESHOLDS["medium_max"],
        ),
        "max_arity": _bucket_int(
            shape.max_rule_arity,
            small_max=MAX_ARITY_THRESHOLDS["low_max"],
            medium_max=MAX_ARITY_THRESHOLDS["medium_max"],
            labels=("low", "medium", "high"),
        ),
        "preprocessing": "collapsed" if shape.preprocessing_collapsed else "not_collapsed",
        "solver_class": solver_class_name,
    }


def _bucket_int(
    value: int,
    *,
    small_max: int,
    medium_max: int,
    labels: tuple[str, str, str] = ("small", "medium", "large"),
) -> str:
    if value <= small_max:
        return labels[0]
    if value <= medium_max:
        return labels[1]
    return labels[2]


def _bucket_float(value: float, *, sparse_max: float, medium_max: float) -> str:
    if value <= sparse_max:
        return "sparse"
    if value <= medium_max:
        return "medium"
    return "dense"


def build_jobs_from_manifest(
    rows: list[dict[str, Any]],
    *,
    data_root: Path,
    years: set[int] | None,
    subtracks: set[str] | None,
    instance_kind: str,
) -> list[BenchmarkJob]:
    jobs: list[BenchmarkJob] = []
    seen: set[tuple[int | None, str, str, str, str]] = set()
    for row in rows:
        year = row.get("year")
        if years is not None and year not in years:
            continue
        if row.get("instance_kind") != instance_kind:
            continue
        if subtracks is not None and row.get("subtrack") not in subtracks:
            continue
        key = (
            year,
            str(row.get("track", "")),
            str(row.get("subtrack", "")),
            str(row.get("instance_kind", "")),
            str(row.get("instance", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        root = data_root / str(year)
        path = root / "extracted" / "instances" / Path(*str(row["instance"]).split("/"))
        jobs.append(
            BenchmarkJob(
                year=year,
                track=str(row.get("track", "aba")),
                subtrack=str(row["subtrack"]),
                instance_kind=str(row["instance_kind"]),
                instance=str(row["instance"]),
                root=root,
                path=path,
                arguments_or_atoms=row.get("arguments_or_atoms"),
            )
        )
    return jobs


def build_jobs_from_instances(
    paths: list[Path],
    *,
    root: Path,
    subtracks: tuple[str, ...],
) -> list[BenchmarkJob]:
    jobs: list[BenchmarkJob] = []
    instances_root = root / "extracted" / "instances"
    for path in paths:
        resolved = path.resolve()
        relative = _relative_instance_path(resolved, instances_root.resolve())
        framework = parse_aba(resolved.read_text(encoding="utf-8"))
        for subtrack in subtracks:
            jobs.append(
                BenchmarkJob(
                    year=_year_from_root(root),
                    track="aba",
                    subtrack=subtrack,
                    instance_kind="aba",
                    instance=relative.as_posix(),
                    root=root,
                    path=resolved,
                    arguments_or_atoms=len(framework.language),
                )
            )
    return jobs


def _relative_instance_path(path: Path, instances_root: Path) -> Path:
    try:
        return path.relative_to(instances_root)
    except ValueError as exc:
        raise ValueError(f"explicit instances must live under {instances_root}: {path}") from exc


def _year_from_root(root: Path) -> int | None:
    return int(root.name) if root.name.isdigit() else None


def run_backend_matrix(
    job: BenchmarkJob,
    *,
    framework: ABAFramework,
    backends: tuple[str, ...],
    timeout_seconds: float,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for backend in backends:
        started = time.perf_counter()
        result = run_selected(
            root=job.root,
            relative_path=job.instance,
            kind="aba",
            subtrack=job.subtrack,
            backend=backend,
            timeout_seconds=timeout_seconds,
            arguments_or_atoms=job.arguments_or_atoms,
            track=job.track,
            instance_kind=job.instance_kind,
        )
        elapsed = time.perf_counter() - started
        materialized = dict(result)
        materialized["elapsed_seconds"] = elapsed
        materialized["validation"] = validate_result(framework, job.subtrack, materialized)
        results[backend] = materialized
    return results


def validate_result(framework: ABAFramework, subtrack: str, result: dict[str, Any]) -> dict[str, Any]:
    if result.get("status") != "solved":
        return {"status": "not_checked", "reason": "solver did not return solved"}
    witness_text = result.get("witness")
    if witness_text is None:
        return {"status": "not_checked", "reason": "no witness"}
    witness = _parse_witness(framework, str(witness_text))
    semantics = solver_class("aba", subtrack).split("/")[-1]
    if semantics == "stable":
        valid = native_aba.closed(framework, witness) and native_aba.conflict_free(framework, witness) and all(
            native_aba.attacks(framework, witness, frozenset({assumption}))
            for assumption in framework.assumptions - witness
        )
        return {"status": "valid" if valid else "invalid", "check": "stable"}
    if semantics == "preferred":
        valid = native_aba.admissible(framework, witness)
        return {
            "status": "valid" if valid else "invalid",
            "check": "preferred_admissible_necessary",
        }
    return {"status": "not_checked", "reason": f"unsupported semantics: {semantics}"}


def _parse_witness(framework: ABAFramework, witness_text: str) -> AssumptionSet:
    assumptions_by_repr = {repr(assumption): assumption for assumption in framework.assumptions}
    result: set[Literal] = set()
    for token in witness_text.split():
        assumption = assumptions_by_repr.get(token)
        if assumption is None:
            assumption = Literal(GroundAtom(token))
        result.add(assumption)
    return frozenset(result)


def best_solved_backend(backend_results: dict[str, dict[str, Any]]) -> str | None:
    solved = [
        (backend, result)
        for backend, result in backend_results.items()
        if result.get("status") == "solved" and result.get("validation", {}).get("status") != "invalid"
    ]
    if not solved:
        return None
    return min(solved, key=lambda item: float(item[1].get("elapsed_seconds", float("inf"))))[0]


def benchmark_rows(
    jobs: list[BenchmarkJob],
    *,
    backends: tuple[str, ...],
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, job in enumerate(jobs, start=1):
        framework = parse_aba(job.path.read_text(encoding="utf-8"))
        shape = compute_aba_shape(framework)
        class_name = solver_class(job.instance_kind, job.subtrack)
        backend_results = run_backend_matrix(
            job,
            framework=framework,
            backends=backends,
            timeout_seconds=timeout_seconds,
        )
        best = best_solved_backend(backend_results)
        row = {
            "index": index,
            "year": job.year,
            "track": job.track,
            "subtrack": job.subtrack,
            "instance_kind": job.instance_kind,
            "instance": job.instance,
            "solver_class": class_name,
            "shape": asdict(shape),
            "buckets": shape_buckets(shape, class_name),
            "backend_results": backend_results,
            "best_solved_backend": best,
            "all_timed_out": all(result.get("status") == "timeout" for result in backend_results.values()),
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "event": "aba_shape_row",
                    "index": index,
                    "total": len(jobs),
                    "instance": job.instance,
                    "subtrack": job.subtrack,
                    "best_solved_backend": best,
                    "all_timed_out": row["all_timed_out"],
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
    return rows


def summarize(rows: list[dict[str, Any]], *, backends: tuple[str, ...]) -> dict[str, Any]:
    return {
        "by_solver_class": _count_by(rows, "solver_class"),
        "by_backend": _backend_summary(rows, backends),
        "shape_buckets": _shape_bucket_summary(rows),
        "portfolio_proposals": propose_portfolio_rules(rows, backends=backends),
        "total_rows": len(rows),
    }


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(row[key]) for row in rows)
    return dict(sorted(counts.items()))


def _backend_summary(rows: list[dict[str, Any]], backends: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for backend in backends:
        statuses = Counter(str(row["backend_results"][backend].get("status")) for row in rows)
        summary[backend] = dict(sorted(statuses.items()))
    return summary


def _shape_bucket_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[tuple[str, str], ...], Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = tuple(sorted(row["buckets"].items()))
        status = "all_timeout" if row["all_timed_out"] else f"best:{row['best_solved_backend']}"
        counts[key][status] += 1
    return [
        {"bucket": dict(key), "outcomes": dict(sorted(counter.items())), "total": sum(counter.values())}
        for key, counter in sorted(counts.items())
    ]


def propose_portfolio_rules(rows: list[dict[str, Any]], *, backends: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[tuple[str, str], ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(sorted(row["buckets"].items()))].append(row)
    proposals: list[dict[str, Any]] = []
    for key, bucket_rows in sorted(grouped.items()):
        solved_best = [row["best_solved_backend"] for row in bucket_rows if row["best_solved_backend"]]
        if len(bucket_rows) < 2 or not solved_best:
            continue
        counts = Counter(solved_best)
        backend, count = counts.most_common(1)[0]
        counterexamples = [
            row["instance"]
            for row in bucket_rows
            if row["backend_results"][backend].get("status") != "solved"
        ]
        if counterexamples:
            continue
        proposals.append(
            {
                "backend": backend,
                "confidence": "medium" if count == len(bucket_rows) else "low",
                "evidence_rows": len(bucket_rows),
                "shape_predicate": dict(key),
                "solver_classes": sorted({row["solver_class"] for row in bucket_rows}),
            }
        )
    return proposals


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], *, backends: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "instance",
        "subtrack",
        "solver_class",
        "backend",
        "status",
        "elapsed_seconds",
        "reason",
        "witness_size",
        "validation_status",
        "best_solved_backend",
        "all_timed_out",
    ]
    shape_fields = list(AbaShape.__dataclass_fields__)
    bucket_fields = ["assumption_size", "rule_density", "max_arity", "preprocessing"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*fields, *shape_fields, *bucket_fields])
        writer.writeheader()
        for row in rows:
            for backend in backends:
                result = row["backend_results"][backend]
                writer.writerow(
                    {
                        **{field: row["shape"][field] for field in shape_fields},
                        **{field: row["buckets"][field] for field in bucket_fields},
                        "all_timed_out": row["all_timed_out"],
                        "backend": backend,
                        "best_solved_backend": row["best_solved_backend"],
                        "elapsed_seconds": result.get("elapsed_seconds"),
                        "instance": row["instance"],
                        "reason": result.get("reason"),
                        "solver_class": row["solver_class"],
                        "status": result.get("status"),
                        "subtrack": row["subtrack"],
                        "validation_status": result.get("validation", {}).get("status"),
                        "witness_size": result.get("witness_size"),
                    }
                )


def build_payload(
    rows: list[dict[str, Any]],
    *,
    backends: tuple[str, ...],
    timeout_seconds: float,
) -> dict[str, Any]:
    return {
        "config": {
            "backend_candidates": list(backends),
            "bucket_thresholds": {
                "assumption_size": ASSUMPTION_SIZE_THRESHOLDS,
                "max_arity": MAX_ARITY_THRESHOLDS,
                "rule_density": RULE_DENSITY_THRESHOLDS,
            },
            "timeout_seconds": timeout_seconds,
        },
        "rows": rows,
        "summary": summarize(rows, backends=backends),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark ABA solver backends by framework shape.")
    parser.add_argument("--instance", action="append", type=Path, default=[])
    parser.add_argument("--timeouts", type=Path)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--year", action="append", type=int)
    parser.add_argument("--subtrack", action="append", default=[])
    parser.add_argument("--instance-kind", default="aba")
    parser.add_argument("--backend", action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    subtracks = tuple(args.subtrack) or DEFAULT_SUBTRACKS
    backends = tuple(args.backend) or DEFAULT_BACKENDS
    jobs: list[BenchmarkJob] = []
    if args.timeouts is not None:
        rows = json.loads(args.timeouts.read_text(encoding="utf-8"))
        jobs.extend(
            build_jobs_from_manifest(
                rows,
                data_root=args.data_root,
                years=None if args.year is None else set(args.year),
                subtracks=set(subtracks),
                instance_kind=args.instance_kind,
            )
        )
    if args.instance:
        jobs.extend(build_jobs_from_instances(args.instance, root=args.root, subtracks=subtracks))
    if not jobs:
        raise SystemExit("no ABA benchmark jobs selected")
    rows = benchmark_rows(jobs, backends=backends, timeout_seconds=args.timeout_seconds)
    payload = build_payload(rows, backends=backends, timeout_seconds=args.timeout_seconds)
    write_json(args.output_json, payload)
    write_csv(args.output_csv, rows, backends=backends)
    print(json.dumps({"output_json": str(args.output_json), "output_csv": str(args.output_csv), "summary": payload["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
