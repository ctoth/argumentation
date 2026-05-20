from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from argumentation.aba_telemetry import STRUCTURAL_TELEMETRY_KEYS


FIXTURE_PATH = Path("tests/manifests/iccma2025-abcgen-10x10.json")
FORBIDDEN_FEATURE_KEYS = {
    "archive",
    "basename",
    "filename",
    "instance",
    "label",
    "parent",
    "path",
    "relative_path",
    "year",
}


def test_abcgen_10x10_fixture_is_structural_not_identity_based() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    rows = payload["rows"]
    pairs = payload["pairs"]
    cluster = payload["selection"]["structural_cluster"]

    assert len([row for row in rows if row["status"] == "timeout"]) == 10
    assert len([row for row in rows if row["status"] == "solved"]) == 10
    assert len(pairs) == 10
    assert cluster == "sparse_assumption_language|narrow_rule_bodies"

    for row in rows:
        assert row["structural_cluster"] == cluster
        telemetry = row["telemetry"]
        assert STRUCTURAL_TELEMETRY_KEYS <= set(telemetry)
        assert not (FORBIDDEN_FEATURE_KEYS & set(telemetry))
        assert telemetry["assumption_to_atom_ratio"] < 0.5
        assert telemetry["max_rule_body_width"] <= 3

    distinctive_counter: Counter[str] = Counter()
    for pair in pairs:
        assert pair["distinctive_features"]
        assert pair["decision_features"]
        assert not (FORBIDDEN_FEATURE_KEYS & set(pair["distinctive_features"]))
        assert not (FORBIDDEN_FEATURE_KEYS & set(pair["decision_features"]))
        assert set(pair["decision_features"]) <= STRUCTURAL_TELEMETRY_KEYS
        distinctive_counter.update(pair["distinctive_features"])

    assert any(count >= 3 for count in distinctive_counter.values())
