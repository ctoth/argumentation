from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.run_frontier_v1 import select_rows, summarize_by_class

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests" / "manifests" / "iccma2025-frontier-v1.json"
ICCMA_2025_INPUT_ROOT = ROOT / "data" / "iccma" / "2025" / "extracted" / "instances"

EXPECTED_CLASS_COUNTS = {"hard": 21, "boundary_melt": 4, "melt": 5}

EXPECTED_BOUNDARY_MELT = {
    ("AFs/crusti_g2io_125_0.5_31_17.af", "DC-CO"),
    ("AFs/scc_1554_2_0.4_0.2_3.af", "DC-CO"),
    ("AFs/ER_200_20_3.af", "DS-SST"),
    ("ABAs/aba_2000_0.3_10_10_4.aba", "SE-PR"),
}

EXPECTED_MELT = {
    ("AFs/mainkwt_250_100_50_100_100_0.4_0.3_0.4_0.3_0.4_0.3_0.2__5.af", "DS-PR"),
    ("AFs/mainkwt_250_150_75_100_200_0.4_0.3_0.4_0.3_0.4_0.3_0.2__5.af", "DS-PR"),
    ("AFs/mainkwt_250_150_75_150_200_0.4_0.3_0.4_0.3_0.4_0.3_0.2__4.af", "DS-PR"),
    ("AFs/ER_500_100_5.af", "DS-SST"),
    ("AFs/crusti_g2io_125_0.5_31_17.af", "DS-ST"),
}

EXPECTED_SUBTRACK_COUNTS = {
    "DC-CO": 6,
    "DS-PR": 9,
    "DS-SST": 3,
    "DS-ST": 3,
    "SE-PR": 5,
    "SE-ST": 4,
}

REQUIRED_FIELDS = {
    "year",
    "track",
    "subtrack",
    "instance_kind",
    "relative_path",
    "arguments_or_atoms",
    "recal_class",
    "input_sha256",
}


def load_manifest() -> list[dict[str, object]]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def cell(row: dict[str, object]) -> tuple[str, str]:
    return (str(row["relative_path"]), str(row["subtrack"]))


def test_manifest_has_thirty_unique_cells() -> None:
    rows = load_manifest()

    assert len(rows) == 30
    assert len({cell(row) for row in rows}) == 30


def test_manifest_class_counts_match_recal_outcome() -> None:
    rows = load_manifest()

    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["recal_class"])] = counts.get(str(row["recal_class"]), 0) + 1

    assert counts == EXPECTED_CLASS_COUNTS


def test_manifest_boundary_melt_and_melt_membership() -> None:
    rows = load_manifest()

    assert {
        cell(row) for row in rows if row["recal_class"] == "boundary_melt"
    } == EXPECTED_BOUNDARY_MELT
    assert {cell(row) for row in rows if row["recal_class"] == "melt"} == EXPECTED_MELT


def test_manifest_subtrack_coverage_matches_sample() -> None:
    rows = load_manifest()

    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["subtrack"])] = counts.get(str(row["subtrack"]), 0) + 1

    assert counts == EXPECTED_SUBTRACK_COUNTS


def test_manifest_rows_have_required_fields_and_hashes() -> None:
    rows = load_manifest()

    for row in rows:
        assert REQUIRED_FIELDS <= set(row)
        assert row["year"] == 2025
        digest = row["input_sha256"]
        assert isinstance(digest, str)
        assert len(digest) == 64
        int(digest, 16)

    if not ICCMA_2025_INPUT_ROOT.exists():
        return

    for row in rows:
        path = ICCMA_2025_INPUT_ROOT / Path(*str(row["relative_path"]).split("/"))
        assert path.exists()
        assert _sha256(path) == row["input_sha256"]


def test_select_rows_filters_by_subtrack() -> None:
    rows = [
        {"relative_path": "a.af", "subtrack": "DS-PR"},
        {"relative_path": "b.af", "subtrack": "DC-CO"},
        {"relative_path": "c.af", "subtrack": "DS-PR"},
    ]

    assert select_rows(rows, subtracks=None) == rows
    assert select_rows(rows, subtracks={"DS-PR"}) == [rows[0], rows[2]]


def test_summarize_by_class_reports_pass_rates() -> None:
    results = [
        {
            "source": {
                "relative_path": "a.af",
                "subtrack": "DS-PR",
                "recal_class": "hard",
            },
            "result": {"status": "timeout"},
        },
        {
            "source": {
                "relative_path": "b.af",
                "subtrack": "DC-CO",
                "recal_class": "melt",
            },
            "result": {"status": "solved"},
        },
        {
            "source": {
                "relative_path": "c.af",
                "subtrack": "DS-PR",
                "recal_class": "hard",
            },
            "result": {"status": "timeout"},
        },
    ]

    assert summarize_by_class(results) == {
        "total": {"rows": 3, "solved": 1, "timeout": 2, "other": 0},
        "by_class": {
            "hard": {"rows": 2, "solved": 0, "timeout": 2, "other": 0},
            "melt": {"rows": 1, "solved": 1, "timeout": 0, "other": 0},
        },
        "deviations": [],
    }


def test_summarize_by_class_flags_deviations() -> None:
    results = [
        {
            "source": {
                "relative_path": "a.af",
                "subtrack": "DS-PR",
                "recal_class": "hard",
            },
            "result": {"status": "solved"},
        },
        {
            "source": {
                "relative_path": "b.af",
                "subtrack": "DC-CO",
                "recal_class": "melt",
            },
            "result": {"status": "timeout"},
        },
    ]

    summary = summarize_by_class(results)

    assert summary["deviations"] == [
        {
            "relative_path": "a.af",
            "subtrack": "DS-PR",
            "recal_class": "hard",
            "status": "solved",
        },
        {
            "relative_path": "b.af",
            "subtrack": "DC-CO",
            "recal_class": "melt",
            "status": "timeout",
        },
    ]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
