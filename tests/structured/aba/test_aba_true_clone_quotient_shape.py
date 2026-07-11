"""Frozen Probe 8 Gate B deterministic structural-shape contract."""

from __future__ import annotations

import json

from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from scripts.aba_true_clone_quotient_reference import (
    SemanticBounds,
    normalize_framework,
)
from scripts.probe_aba_true_clone_quotient_shape import analyze_normalized_shape


def _literal(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _framework(*, near_clone: bool = False) -> ABAFramework:
    a = _literal("a")
    b = _literal("b")
    c = _literal("c")
    ca = _literal("ca")
    cb = _literal("cb")
    x = _literal("x")
    rules = {
        Rule((a, b), x, "strict"),
        Rule((c,), ca, "strict"),
    }
    if near_clone:
        rules.add(Rule((a,), cb, "strict"))
    return ABAFramework(
        language=frozenset({a, b, c, ca, cb, x}),
        rules=frozenset(rules),
        assumptions=frozenset({a, b, c}),
        contrary={a: ca, b: ca, c: cb},
    )


def _analyze(framework: ABAFramework) -> dict[str, object]:
    normalized = normalize_framework(
        framework,
        bounds=SemanticBounds(
            assumptions=16,
            rules=32,
            literals=64,
            body_width=16,
        ),
    )
    return analyze_normalized_shape(normalized.serialized)


def test_color_refinement_only_proposes_and_gate_a_verifier_certifies() -> None:
    telemetry = _analyze(_framework())

    classes = telemetry["certified_classes"]
    assert isinstance(classes, list)
    assert len(classes) == 1
    certified = classes[0]
    assert isinstance(certified, dict)
    assert certified["size"] == 2
    assert len(certified["members"]) == 2
    assert len(telemetry["verified_transpositions"]) == 1
    assert telemetry["rejected_transpositions"] == []
    assert telemetry["all_certificates_revalidated"] is True
    assert telemetry["largest_class"] == 2


def test_near_clone_is_not_certified() -> None:
    telemetry = _analyze(_framework(near_clone=True))

    assert telemetry["certified_classes"] == []
    assert telemetry["largest_class"] == 1
    assert telemetry["all_certificates_revalidated"] is True


def test_exact_state_math_credits_a_size_two_class_without_ceiling() -> None:
    telemetry = _analyze(_framework())
    states = telemetry["multiplicity_state_counts"]
    assert isinstance(states, dict)
    assert states == {"original": "8", "quotient": "6"}
    reduction = telemetry["unceiled_symmetric_decision_reduction"]
    assert isinstance(reduction, float)
    assert 0.415 < reduction < 0.416


def test_rule_template_multiplicity_reconstructs_every_original_rule() -> None:
    telemetry = _analyze(_framework())
    templates = telemetry["rule_templates"]
    assert isinstance(templates, dict)
    assert templates["original_count"] == 2
    assert templates["quotient_count"] == 2
    assert templates["reconstructs_original_multiset"] is True
    assert sum(item["multiplicity"] for item in templates["quotient_templates"]) == 2


def test_machine_readable_telemetry_is_deterministic_and_complete() -> None:
    first = _analyze(_framework())
    second = _analyze(_framework())
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert set(first) == {
        "normalized_sha256",
        "counts",
        "refinement_rounds",
        "candidate_buckets",
        "verified_transpositions",
        "rejected_transpositions",
        "certified_classes",
        "certified_class_count",
        "largest_class",
        "multiplicity_state_counts",
        "unceiled_symmetric_decision_reduction",
        "rule_templates",
        "all_certificates_revalidated",
    }
    counts = first["counts"]
    assert isinstance(counts, dict)
    assert counts == {
        "assumptions": 3,
        "rules": 2,
        "literals": 6,
        "nodes": 8,
        "incidences": 8,
    }
