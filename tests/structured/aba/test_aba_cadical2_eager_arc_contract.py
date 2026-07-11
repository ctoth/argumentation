"""Deterministic operational contract for the Probe 7 diagnostic owner."""

from __future__ import annotations

from scripts.probe_iccma2023_cadical221_eager_arc import (
    PINNED_CADICAL_COMMIT,
    build_contract_fixture_manifest,
    validate_complete_model,
    validate_probe_manifest,
)


def test_cadical221_eager_arc_manifest_contract() -> None:
    manifest = build_contract_fixture_manifest()
    control = manifest["control"]
    candidate = manifest["candidate"]

    assert candidate["engine_api"] == "cadical-direct"
    assert candidate["engine_version"] == "2.2.1"
    assert candidate["source_commit"] == PINNED_CADICAL_COMMIT
    assert PINNED_CADICAL_COMMIT == "4198d817d0dcde5b1240eefbff70b555b7df2af9"

    for hash_name in (
        "formula_sha256",
        "variable_map_sha256",
        "clause_stream_sha256",
        "phase_vector_sha256",
    ):
        assert candidate[hash_name] == control[hash_name]
        assert len(candidate[hash_name]) == 64

    assert candidate["eager_path"] is True
    assert candidate["solver_calls"] == 1
    assert candidate["refinements"] == 0
    assert candidate["lazy_fallback"] is False

    for statistic in ("conflicts", "decisions", "propagations", "restarts"):
        assert isinstance(candidate[statistic], int)
        assert candidate[statistic] >= 0

    semantics = manifest["semantic_authorities"]
    assert semantics["aba_fixture_authority"] == "support_extensions"
    assert semantics["sat_model_validator"] == "complete-clause-signed-literal"
    assert semantics["signed_val_semantics_checked"] is True
    assert semantics["unsat_authority"] == "independent-proof-checker"
    assert semantics["proof_formula_sha256"] == candidate["formula_sha256"]
    assert semantics["proof_checker_name"] != "cadical"
    assert semantics["proof_checker_exit_status"] == 0
    assert len(semantics["proof_sha256"]) == 64

    validate_probe_manifest(manifest)


def test_complete_model_validator_preserves_signed_val_semantics() -> None:
    clauses = ((1, -2), (-1, 2))
    signed_values = {1: 1, -1: -1, 2: 2, -2: -2}

    validate_complete_model(clauses, signed_values, variable_count=2)


def test_complete_model_validator_rejects_collapsed_negative_queries() -> None:
    clauses = ((-1,),)
    collapsed_values = {1: 1, -1: 1}

    try:
        validate_complete_model(clauses, collapsed_values, variable_count=1)
    except ValueError as error:
        assert "signed" in str(error)
    else:
        raise AssertionError("collapsed signed-literal values were accepted")
