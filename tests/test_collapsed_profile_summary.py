from __future__ import annotations

from tools.collapsed_profile_summary import (
    hot_frames,
    parse_collapsed_line,
    serializable_top,
)


def test_parse_collapsed_line_extracts_stack_and_count() -> None:
    assert parse_collapsed_line("root;worker;leaf 7") == (
        ["root", "worker", "leaf"],
        7,
    )


def test_hot_frames_counts_exclusive_and_inclusive_samples() -> None:
    counters = hot_frames(
        [
            "root;worker;leaf 7",
            "root;worker;other 3",
            "invalid line",
        ]
    )

    assert counters["exclusive"] == {"leaf": 7, "other": 3}
    assert counters["inclusive"] == {"root": 10, "worker": 10, "leaf": 7, "other": 3}


def test_serializable_top_reports_share_of_profile_samples() -> None:
    rows = serializable_top(
        hot_frames(["root;worker;leaf 7", "root;worker;other 3"])["inclusive"],
        2,
        total_samples=10,
    )

    assert rows == [
        {"frame": "root", "samples": 10, "share": 1.0},
        {"frame": "worker", "samples": 10, "share": 1.0},
    ]
