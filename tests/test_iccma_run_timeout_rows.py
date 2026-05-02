from __future__ import annotations

from tools.iccma_run_timeout_rows import selected_timeout_rows, summarize_results


def test_selected_timeout_rows_filters_year_and_subtrack() -> None:
    rows = [
        {"year": 2017, "subtrack": "DS-PR", "instance": "a.apx"},
        {"year": 2019, "subtrack": "DS-PR", "instance": "b.apx"},
        {"year": 2023, "subtrack": "DS-PR", "instance": "c.apx"},
        {"year": 2017, "subtrack": "SE-PR", "instance": "d.apx"},
    ]

    assert selected_timeout_rows(rows, years={2017, 2019}, subtrack="DS-PR") == rows[:2]


def test_summarize_results_groups_statuses_and_timeouts() -> None:
    results = [
        {"source": {"instance": "a.apx"}, "result": {"status": "solved"}},
        {"source": {"instance": "b.apx"}, "result": {"status": "timeout"}},
        {"source": {"instance": "c.apx"}, "result": {"status": "solved"}},
    ]

    assert summarize_results(results) == {
        "total": 3,
        "by_status": {"solved": 2, "timeout": 1},
        "timeouts": ["b.apx"],
    }
