from __future__ import annotations

import json

from tools.iccma_compare_range_traces import compare_runs


def test_compare_runs_summarizes_status_and_range_utility_counts(tmp_path) -> None:
    before_rows = tmp_path / "before.json"
    after_rows = tmp_path / "after.json"
    before_events = tmp_path / "before.events.jsonl"
    after_events = tmp_path / "after.events.jsonl"

    before_rows.write_text(
        json.dumps(
            [
                {"status": "solved", "subtrack": "SE-STG", "instance": "a.apx"},
                {"status": "timeout", "subtrack": "SE-STG", "instance": "b.apx"},
            ]
        ),
        encoding="utf-8",
    )
    after_rows.write_text(
        json.dumps(
            [
                {"status": "solved", "subtrack": "SE-STG", "instance": "a.apx"},
                {"status": "solved", "subtrack": "SE-STG", "instance": "b.apx"},
            ]
        ),
        encoding="utf-8",
    )
    before_events.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event": "sat_check",
                        "utility_name": "stage_seed",
                        "subtrack": "SE-STG",
                    }
                ),
                json.dumps(
                    {
                        "event": "sat_check",
                        "utility_name": "stage_seed",
                        "subtrack": "SE-STG",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    after_events.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event": "sat_check",
                        "utility_name": "stage_full_range_shortcut",
                        "subtrack": "SE-STG",
                    }
                ),
                json.dumps(
                    {
                        "event": "sat_check",
                        "utility_name": "stage_max_range_at_least",
                        "subtrack": "SE-STG",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    comparison = compare_runs(
        before_rows=before_rows,
        after_rows=after_rows,
        before_events=before_events,
        after_events=after_events,
    )

    assert comparison["status_delta"]["solved"] == 1
    assert comparison["status_delta"]["timeout"] == -1
    assert comparison["utility_delta"]["stage_seed"] == -2
    assert comparison["utility_delta"]["stage_full_range_shortcut"] == 1
    assert comparison["utility_delta"]["stage_max_range_at_least"] == 1
