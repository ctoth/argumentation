from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable


STRUCTURAL_SIGNATURE_FIELDS = (
    "solver_class",
    "assumption_count",
    "rule_count",
    "max_rule_arity",
    "rule_density",
    "dependency_scc_count",
    "dependency_scc_max_size",
    "dependency_cycle_count_or_flag",
    "p_acyclic",
    "contrary_target_in_degree_max",
    "assumption_incidence_width_proxy",
    "rule_body_overlap_max",
    "rule_body_overlap_avg",
    "closure_growth_sample",
    "stable_obstruction_count",
    "tau_aba_primal_width_proxy",
)


@dataclass(frozen=True)
class EvidenceAnalysis:
    total_rows: int
    by_backend: dict[str, dict[str, int]]
    bucket_outcomes: list[dict[str, Any]]
    all_timeout_rows: list[dict[str, Any]]
    backend_wins_zero_counterexamples: list[dict[str, Any]]
    all_timeout_signatures: list[dict[str, Any]]
    mixed_signatures: list[dict[str, Any]]
    route_candidate_summary: list[dict[str, Any]]


def analyze_payload(payload: dict[str, Any]) -> EvidenceAnalysis:
    rows = list(payload["rows"])
    return EvidenceAnalysis(
        total_rows=len(rows),
        by_backend=_backend_summary(rows),
        bucket_outcomes=_bucket_outcomes(rows),
        all_timeout_rows=[
            _row_with_signature(row) for row in rows if row["all_timed_out"]
        ],
        backend_wins_zero_counterexamples=_backend_wins_zero_counterexamples(rows),
        all_timeout_signatures=_all_timeout_signatures(rows),
        mixed_signatures=_mixed_signatures(rows),
        route_candidate_summary=_route_candidate_summary(rows),
    )


def _backend_summary(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, int]]:
    statuses: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for backend, outcome in row["backend_outcomes"].items():
            statuses[backend][str(outcome)] += 1
    return {
        backend: dict(sorted(counter.items()))
        for backend, counter in sorted(statuses.items())
    }


def _bucket_outcomes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["shape_bucket_id"])].append(row)

    result: list[dict[str, Any]] = []
    for bucket_id, bucket_rows in sorted(grouped.items()):
        outcomes = Counter(
            "all_timeout"
            if row["all_timed_out"]
            else f"best:{row['best_solved_backend']}"
            for row in bucket_rows
        )
        result.append(
            {
                "bucket_id": bucket_id,
                "outcomes": dict(sorted(outcomes.items())),
                "total": len(bucket_rows),
                "all_timeout_rows": [
                    _row_with_signature(row)
                    for row in bucket_rows
                    if row["all_timed_out"]
                ],
                "mixed": len(outcomes) > 1,
            }
        )
    return result


def _backend_wins_zero_counterexamples(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[tuple[str, Any], ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_signature(row)].append(row)

    wins: list[dict[str, Any]] = []
    for signature, signature_rows in sorted(grouped.items()):
        solved = [
            row
            for row in signature_rows
            if row["best_solved_backend"] and not row["all_timed_out"]
        ]
        if len(solved) < 2:
            continue
        counts = Counter(str(row["best_solved_backend"]) for row in solved)
        backend, count = counts.most_common(1)[0]
        counterexamples = [
            _row_ref(row)
            for row in signature_rows
            if row["best_solved_backend"] != backend
        ]
        if counterexamples:
            continue
        wins.append(
            {
                "backend": backend,
                "evidence_count": count,
                "signature": dict(signature),
                "evidence_rows": [_row_ref(row) for row in signature_rows],
            }
        )
    return wins


def _all_timeout_signatures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[tuple[str, Any], ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_signature(row)].append(row)

    signatures: list[dict[str, Any]] = []
    for signature, signature_rows in sorted(grouped.items()):
        if len(signature_rows) < 2:
            continue
        if all(row["all_timed_out"] for row in signature_rows):
            signatures.append(
                {
                    "evidence_count": len(signature_rows),
                    "signature": dict(signature),
                    "evidence_rows": [_row_ref(row) for row in signature_rows],
                }
            )
    return signatures


def _mixed_signatures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[tuple[str, Any], ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_signature(row)].append(row)

    signatures: list[dict[str, Any]] = []
    for signature, signature_rows in sorted(grouped.items()):
        outcomes = Counter(
            "all_timeout"
            if row["all_timed_out"]
            else f"best:{row['best_solved_backend']}"
            for row in signature_rows
        )
        if len(signature_rows) < 2 or len(outcomes) < 2:
            continue
        signatures.append(
            {
                "outcomes": dict(sorted(outcomes.items())),
                "signature": dict(signature),
                "evidence_rows": [_row_ref(row) for row in signature_rows],
            }
        )
    return signatures


def _route_candidate_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for candidate in row["route_candidates"]:
            grouped[str(candidate["predicate"])].append(row)

    summary: list[dict[str, Any]] = []
    for predicate, candidate_rows in sorted(grouped.items()):
        counterexample_count = sum(
            len(row["route_counterexamples"].get(predicate, ()))
            for row in candidate_rows
        )
        summary.append(
            {
                "predicate": predicate,
                "candidate_rows": len(candidate_rows),
                "counterexample_count": counterexample_count,
                "production_ready": counterexample_count == 0
                and len(candidate_rows) >= 2,
            }
        )
    return summary


def _signature(row: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    shape = row["shape"]
    values: dict[str, Any] = {"solver_class": row["solver_class"]}
    for field in STRUCTURAL_SIGNATURE_FIELDS:
        if field == "solver_class":
            continue
        values[field] = shape[field]
    return tuple(sorted(values.items()))


def _row_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "instance": row["instance"],
        "subtrack": row["subtrack"],
        "solver_class": row["solver_class"],
        "best_solved_backend": row["best_solved_backend"],
        "all_timed_out": row["all_timed_out"],
    }


def _row_with_signature(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **_row_ref(row),
        "shape_bucket_id": row["shape_bucket_id"],
        "signature": dict(_signature(row)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze ABA route evidence from shape benchmark JSON."
    )
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args(argv)

    payload = json.loads(args.input_json.read_text(encoding="utf-8"))
    analysis = analyze_payload(payload)
    output = {
        "total_rows": analysis.total_rows,
        "by_backend": analysis.by_backend,
        "bucket_outcomes": analysis.bucket_outcomes,
        "all_timeout_rows": analysis.all_timeout_rows,
        "backend_wins_zero_counterexamples": analysis.backend_wins_zero_counterexamples,
        "all_timeout_signatures": analysis.all_timeout_signatures,
        "mixed_signatures": analysis.mixed_signatures,
        "route_candidate_summary": analysis.route_candidate_summary,
    }
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
