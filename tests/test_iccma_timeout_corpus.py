from __future__ import annotations

import csv

from tools.iccma_timeout_corpus import collect_timeout_rows, summarize_timeout_rows


FIELDS = [
    "track",
    "subtrack",
    "instance_kind",
    "instance",
    "backend",
    "status",
    "reason",
    "elapsed_seconds",
    "answer",
    "extension_count",
    "witness_size",
    "witness",
    "arguments_or_atoms",
    "attacks",
    "assumptions",
    "rules",
    "contraries",
    "error",
]


def test_collect_timeout_rows_from_iccma_csv(tmp_path) -> None:
    csv_path = tmp_path / "iccma-2099-range-max-inclusion-cap100.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "track": "legacy",
                "subtrack": "DS-PR",
                "instance_kind": "apx",
                "instance": "instances/hard.apx",
                "backend": "auto",
                "status": "timeout",
                "reason": "timeout>12.0",
                "elapsed_seconds": "12.01",
                "arguments_or_atoms": "81",
                "attacks": "136",
            }
        )
        writer.writerow(
            {
                "track": "legacy",
                "subtrack": "SE-ST",
                "instance_kind": "apx",
                "instance": "instances/easy.apx",
                "backend": "auto",
                "status": "solved",
                "elapsed_seconds": "0.01",
                "arguments_or_atoms": "2",
            }
        )

    rows = collect_timeout_rows([csv_path])

    assert rows == [
        {
            "arguments_or_atoms": 81,
            "attacks": 136,
            "backend": "auto",
            "contraries": None,
            "elapsed_seconds": 12.01,
            "error": "",
            "instance": "instances/hard.apx",
            "instance_kind": "apx",
            "reason": "timeout>12.0",
            "rules": None,
            "source_csv": str(csv_path),
            "status": "timeout",
            "subtrack": "DS-PR",
            "track": "legacy",
            "year": 2099,
            "assumptions": None,
        }
    ]


def test_summarize_timeout_rows_groups_by_year_track_subtrack_and_kind() -> None:
    rows = [
        {
            "year": 2017,
            "track": "legacy",
            "subtrack": "DS-PR",
            "instance_kind": "apx",
        },
        {
            "year": 2017,
            "track": "legacy",
            "subtrack": "DS-PR",
            "instance_kind": "tgf",
        },
        {
            "year": 2025,
            "track": "aba",
            "subtrack": "SE-ST",
            "instance_kind": "aba",
        },
    ]

    assert summarize_timeout_rows(rows) == {
        "by_group": [
            {
                "count": 1,
                "instance_kind": "aba",
                "subtrack": "SE-ST",
                "track": "aba",
                "year": 2025,
            },
            {
                "count": 1,
                "instance_kind": "apx",
                "subtrack": "DS-PR",
                "track": "legacy",
                "year": 2017,
            },
            {
                "count": 1,
                "instance_kind": "tgf",
                "subtrack": "DS-PR",
                "track": "legacy",
                "year": 2017,
            },
        ],
        "total_timeouts": 3,
    }
