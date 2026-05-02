from __future__ import annotations

import json
from pathlib import Path

from tools.iccma_trace_classify import classify_trace


def test_trace_classifier_detects_unique_attacker_churn(tmp_path: Path) -> None:
    trace_path = tmp_path / "hard.trace.jsonl"
    result_path = tmp_path / "hard.stdout.json"
    events = [
        _sat("preferred_skeptical_seed", 0, None, "seed"),
    ]
    for index in range(101):
        events.append(_sat("preferred_skeptical_adm_ext_att", index, index, f"a{index}"))
        events.append(
            _sat("preferred_skeptical_extend_attacker", index, index, f"w{index}")
        )
    trace_path.write_text(
        "\n".join(json.dumps(event, sort_keys=True) for event in events),
        encoding="utf-8",
    )
    result_path.write_text(
        json.dumps({"status": "timeout", "reason": "timeout>20.0"}),
        encoding="utf-8",
    )

    summary = classify_trace(trace_path, result_path=result_path)

    assert summary.classification == "unique-attacker-churn"
    assert summary.event_counts_by_utility["preferred_skeptical_adm_ext_att"] == 101
    assert summary.unique_fingerprints_by_utility[
        "preferred_skeptical_adm_ext_att"
    ] == 101
    assert summary.max_learned_count == 100
    assert summary.last_loop_index == 100
    assert summary.terminal_status == "timeout"


def test_trace_classifier_detects_quick_counterexample(tmp_path: Path) -> None:
    trace_path = tmp_path / "quick.trace.jsonl"
    result_path = tmp_path / "quick.stdout.json"
    events = [
        _sat("preferred_skeptical_seed", None, None, "seed"),
        _sat("preferred_skeptical_adm_ext_att", 0, 0, "attacker"),
        {
            **_sat("preferred_skeptical_extend_attacker", 0, 0, None),
            "model_extension_fingerprint": None,
            "model_extension_size": None,
            "result": "unsat",
        },
    ]
    trace_path.write_text(
        "\n".join(json.dumps(event, sort_keys=True) for event in events),
        encoding="utf-8",
    )
    result_path.write_text(
        json.dumps({"status": "solved", "answer": "false"}),
        encoding="utf-8",
    )

    summary = classify_trace(trace_path, result_path=result_path)

    assert summary.classification == "quick-counterexample"
    assert summary.event_count == 3
    assert summary.event_counts_by_utility["preferred_skeptical_adm_ext_att"] == 1
    assert summary.unique_fingerprints_by_utility[
        "preferred_skeptical_adm_ext_att"
    ] == 1
    assert summary.terminal_answer == "false"


def _sat(
    utility_name: str,
    loop_index: int | None,
    learned_count: int | None,
    fingerprint: str | None,
) -> dict[str, object]:
    return {
        "event": "sat_check",
        "utility_name": utility_name,
        "result": "sat",
        "elapsed_ms": "0.1",
        "arguments": 3,
        "attacks": 2,
        "model_extension_size": 1 if fingerprint is not None else None,
        "model_extension_fingerprint": fingerprint,
        "loop_index": loop_index,
        "learned_count": learned_count,
    }
