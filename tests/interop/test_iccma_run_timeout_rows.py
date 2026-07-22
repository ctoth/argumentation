from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import iccma_run_timeout_rows
from tools.iccma_run_timeout_rows import (
    run_timeout_rows,
    selected_timeout_rows,
    summarize_results,
)
from tools.iccma_timeout_corpus import summarize_timeout_rows


ROOT = Path(__file__).resolve().parents[2]
CAP150_MANIFEST = ROOT / "tests" / "manifests" / "iccma2025-cap150-timeouts.json"
CAP200_MANIFEST = ROOT / "tests" / "manifests" / "iccma2025-cap200-timeouts.json"
ICCMA_2025_INPUT_ROOT = ROOT / "data" / "iccma" / "2025" / "extracted" / "instances"


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


def test_cap150_timeout_manifest_resolves_unique_rows_and_hashes() -> None:
    rows = json.loads(CAP150_MANIFEST.read_text(encoding="utf-8"))

    _assert_checked_manifest(rows, expected_len=16)


def test_cap150_timeout_summary_is_order_invariant() -> None:
    rows = json.loads(CAP150_MANIFEST.read_text(encoding="utf-8"))

    assert summarize_timeout_rows(rows) == summarize_timeout_rows(list(reversed(rows)))
    assert summarize_timeout_rows(rows) == {
        "by_group": [
            {
                "count": 11,
                "instance_kind": "aba",
                "subtrack": "SE-PR",
                "track": "aba",
                "year": 2025,
            },
            {
                "count": 1,
                "instance_kind": "aba",
                "subtrack": "SE-ST",
                "track": "aba",
                "year": 2025,
            },
            {
                "count": 2,
                "instance_kind": "af",
                "subtrack": "DC-ID",
                "track": "heuristics",
                "year": 2025,
            },
            {
                "count": 2,
                "instance_kind": "af",
                "subtrack": "SE-ID",
                "track": "main",
                "year": 2025,
            },
        ],
        "total_timeouts": 16,
    }


def test_cap150_timeout_manifest_filtering_matches_simple_oracle() -> None:
    rows = json.loads(CAP150_MANIFEST.read_text(encoding="utf-8"))

    selected = selected_timeout_rows(rows, years={2025}, subtrack="SE-PR")

    assert selected == [
        row for row in rows if row["year"] == 2025 and row["subtrack"] == "SE-PR"
    ]


def test_cap200_timeout_manifest_resolves_unique_rows_and_hashes() -> None:
    rows = json.loads(CAP200_MANIFEST.read_text(encoding="utf-8"))

    _assert_checked_manifest(rows, expected_len=49)


def test_cap200_timeout_summary_is_order_invariant() -> None:
    rows = json.loads(CAP200_MANIFEST.read_text(encoding="utf-8"))

    assert summarize_timeout_rows(rows) == summarize_timeout_rows(list(reversed(rows)))
    assert summarize_timeout_rows(rows) == {
        "by_group": [
            {
                "count": 27,
                "instance_kind": "aba",
                "subtrack": "SE-PR",
                "track": "aba",
                "year": 2025,
            },
            {
                "count": 15,
                "instance_kind": "aba",
                "subtrack": "SE-ST",
                "track": "aba",
                "year": 2025,
            },
            {
                "count": 2,
                "instance_kind": "af",
                "subtrack": "DS-PR",
                "track": "heuristics",
                "year": 2025,
            },
            {
                "count": 1,
                "instance_kind": "af",
                "subtrack": "DS-SST",
                "track": "heuristics",
                "year": 2025,
            },
            {
                "count": 2,
                "instance_kind": "af",
                "subtrack": "DS-PR",
                "track": "main",
                "year": 2025,
            },
            {
                "count": 1,
                "instance_kind": "af",
                "subtrack": "DS-SST",
                "track": "main",
                "year": 2025,
            },
            {
                "count": 1,
                "instance_kind": "af",
                "subtrack": "SE-SST",
                "track": "main",
                "year": 2025,
            },
        ],
        "total_timeouts": 49,
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


def test_run_timeout_rows_passes_iccma_binary_to_selected_runner(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run_selected(**kwargs):
        calls.append(kwargs)
        return {"status": "solved", "answer": None}

    monkeypatch.setattr(iccma_run_timeout_rows, "run_selected", fake_run_selected)

    results = run_timeout_rows(
        [
            {
                "year": 2025,
                "track": "aba",
                "subtrack": "SE-PR",
                "instance_kind": "aba",
                "instance": "ABAs/example.aba",
            }
        ],
        timeout_seconds=15.0,
        backend="iccma",
        data_root=ROOT / "data" / "iccma",
        iccma_binary="uv run scratch/sources/aspforaba/aspforaba/aspforaba.py",
    )

    assert results[0]["result"]["status"] == "solved"
    assert (
        calls[0]["iccma_binary"]
        == "uv run scratch/sources/aspforaba/aspforaba/aspforaba.py"
    )


def _logical_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row["year"],
        row["track"],
        row["subtrack"],
        row["instance_kind"],
        row["instance"],
    )


def _iccma2025_instance_path(row: dict[str, object]) -> Path:
    relative = Path(*str(row["instance"]).split("/"))
    return ICCMA_2025_INPUT_ROOT / relative


def _assert_checked_manifest(
    rows: list[dict[str, object]], *, expected_len: int
) -> None:
    assert len(rows) == expected_len
    assert len({_logical_key(row) for row in rows}) == len(rows)
    for row in rows:
        digest = row["input_sha256"]
        assert isinstance(digest, str)
        assert len(digest) == 64
        int(digest, 16)

    if not ICCMA_2025_INPUT_ROOT.exists():
        return

    for row in rows:
        path = _iccma2025_instance_path(row)
        assert path.exists()
        assert _sha256(path) == row["input_sha256"]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
