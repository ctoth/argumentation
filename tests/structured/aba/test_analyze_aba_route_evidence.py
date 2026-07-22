from __future__ import annotations

from tools.analyze_aba_route_evidence import analyze_payload


def test_analyze_payload_classifies_zero_counterexample_wins_and_mixed_signatures() -> (
    None
):
    payload = {
        "rows": [
            _row("a.aba", "SE-PR", "asp", False, {"asp": "solved", "sat": "timeout"}),
            _row("b.aba", "SE-PR", "asp", False, {"asp": "solved", "sat": "timeout"}),
            _row("c.aba", "SE-ST", None, True, {"asp": "timeout", "sat": "timeout"}),
            _row("d.aba", "SE-ST", "sat", False, {"asp": "timeout", "sat": "solved"}),
        ]
    }

    analysis = analyze_payload(payload)

    assert analysis.by_backend == {
        "asp": {"solved": 2, "timeout": 2},
        "sat": {"solved": 1, "timeout": 3},
    }
    assert analysis.bucket_outcomes == [
        {
            "bucket_id": "preferred-bucket",
            "outcomes": {"best:asp": 2},
            "total": 2,
            "all_timeout_rows": [],
            "mixed": False,
        },
        {
            "bucket_id": "stable-bucket",
            "outcomes": {"all_timeout": 1, "best:sat": 1},
            "total": 2,
            "all_timeout_rows": [
                {
                    **_ref("c.aba", "SE-ST", None, True),
                    "shape_bucket_id": "stable-bucket",
                    "signature": _signature("aba/single-extension/stable"),
                }
            ],
            "mixed": True,
        },
    ]
    assert analysis.all_timeout_rows == [
        {
            **_ref("c.aba", "SE-ST", None, True),
            "shape_bucket_id": "stable-bucket",
            "signature": _signature("aba/single-extension/stable"),
        }
    ]
    assert analysis.backend_wins_zero_counterexamples == [
        {
            "backend": "asp",
            "evidence_count": 2,
            "signature": _signature("aba/single-extension/preferred"),
            "evidence_rows": [
                _ref("a.aba", "SE-PR", "asp", False),
                _ref("b.aba", "SE-PR", "asp", False),
            ],
        }
    ]
    assert analysis.all_timeout_signatures == []
    assert analysis.mixed_signatures == [
        {
            "outcomes": {"all_timeout": 1, "best:sat": 1},
            "signature": _signature("aba/single-extension/stable"),
            "evidence_rows": [
                _ref("c.aba", "SE-ST", None, True),
                _ref("d.aba", "SE-ST", "sat", False),
            ],
        }
    ]
    assert analysis.route_candidate_summary == [
        {
            "predicate": "flat_direct_asp_candidate",
            "candidate_rows": 4,
            "counterexample_count": 2,
            "production_ready": False,
        }
    ]


def test_analyze_payload_classifies_repeated_all_timeout_signature() -> None:
    payload = {
        "rows": [
            _row("a.aba", "SE-PR", None, True, {"asp": "timeout", "sat": "timeout"}),
            _row("b.aba", "SE-PR", None, True, {"asp": "timeout", "sat": "timeout"}),
        ]
    }

    analysis = analyze_payload(payload)

    assert analysis.all_timeout_signatures == [
        {
            "evidence_count": 2,
            "signature": _signature("aba/single-extension/preferred"),
            "evidence_rows": [
                _ref("a.aba", "SE-PR", None, True),
                _ref("b.aba", "SE-PR", None, True),
            ],
        }
    ]


def _row(
    instance: str,
    subtrack: str,
    best_backend: str | None,
    all_timed_out: bool,
    backend_outcomes: dict[str, str],
) -> dict:
    solver_class = (
        "aba/single-extension/stable"
        if subtrack == "SE-ST"
        else "aba/single-extension/preferred"
    )
    route_counterexamples = {"flat_direct_asp_candidate": []}
    if best_backend != "asp":
        route_counterexamples["flat_direct_asp_candidate"] = [
            {
                "backend": "asp",
                "status": backend_outcomes["asp"],
                "validation_status": "not_checked",
                "best_solved_backend": best_backend,
            }
        ]
    return {
        "instance": instance,
        "subtrack": subtrack,
        "solver_class": solver_class,
        "shape_bucket_id": "stable-bucket"
        if subtrack == "SE-ST"
        else "preferred-bucket",
        "best_solved_backend": best_backend,
        "all_timed_out": all_timed_out,
        "backend_outcomes": backend_outcomes,
        "route_candidates": [{"predicate": "flat_direct_asp_candidate"}],
        "route_counterexamples": route_counterexamples,
        "shape": {
            "assumption_count": 10,
            "rule_count": 20,
            "max_rule_arity": 3,
            "rule_density": "medium",
            "dependency_scc_count": 2,
            "dependency_scc_max_size": 1,
            "dependency_cycle_count_or_flag": 0,
            "p_acyclic": True,
            "contrary_target_in_degree_max": 1,
            "assumption_incidence_width_proxy": 4,
            "rule_body_overlap_max": 1,
            "rule_body_overlap_avg": 0.5,
            "closure_growth_sample": 0.25,
            "stable_obstruction_count": 0,
            "tau_aba_primal_width_proxy": 5,
        },
    }


def _signature(solver_class: str) -> dict:
    return {
        "assumption_count": 10,
        "assumption_incidence_width_proxy": 4,
        "contrary_target_in_degree_max": 1,
        "closure_growth_sample": 0.25,
        "dependency_cycle_count_or_flag": 0,
        "dependency_scc_count": 2,
        "dependency_scc_max_size": 1,
        "max_rule_arity": 3,
        "p_acyclic": True,
        "rule_body_overlap_avg": 0.5,
        "rule_body_overlap_max": 1,
        "rule_count": 20,
        "rule_density": "medium",
        "solver_class": solver_class,
        "stable_obstruction_count": 0,
        "tau_aba_primal_width_proxy": 5,
    }


def _ref(
    instance: str, subtrack: str, best_backend: str | None, all_timed_out: bool
) -> dict:
    solver_class = (
        "aba/single-extension/stable"
        if subtrack == "SE-ST"
        else "aba/single-extension/preferred"
    )
    return {
        "instance": instance,
        "subtrack": subtrack,
        "solver_class": solver_class,
        "best_solved_backend": best_backend,
        "all_timed_out": all_timed_out,
    }
