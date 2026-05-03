from __future__ import annotations

import json
from pathlib import Path

from tools.iccma_run_timeout_rows import selected_timeout_rows, summarize_results


ROOT = Path(__file__).resolve().parents[1]


def test_selected_timeout_rows_filters_year_and_subtrack() -> None:
    rows = [
        {"year": 2017, "subtrack": "DS-PR", "instance": "a.apx"},
        {"year": 2019, "subtrack": "DS-PR", "instance": "b.apx"},
        {"year": 2023, "subtrack": "DS-PR", "instance": "c.apx"},
        {"year": 2017, "subtrack": "SE-PR", "instance": "d.apx"},
    ]

    assert selected_timeout_rows(rows, years={2017, 2019}, subtrack="DS-PR") == rows[:2]
    assert selected_timeout_rows(rows[:2], years=None, subtrack=None) == rows[:2]


def test_remaining_eight_manifest_is_source_of_truth() -> None:
    manifest_path = ROOT / "data" / "iccma" / "timeouts" / "dspr-remaining-eight.json"
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(rows) == 8
    assert {row["subtrack"] for row in rows} == {"DS-PR"}
    assert {row["year"] for row in rows} == {2017, 2019}
    assert {row["instance"] for row in rows} == {
        "B/4/irvine-shuttle_20091229_1547.gml.80.apx",
        "B/4/irvine-shuttle_20091229_1547.gml.80.tgf",
        "D/2/BA_60_60_3.apx",
        "D/2/BA_60_60_3.tgf",
        "instances/Small-result-b76.apx",
        "instances/Small-result-b88.apx",
        "instances/Small-result-b90.apx",
        "instances/Small-result-b97.apx",
    }


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
