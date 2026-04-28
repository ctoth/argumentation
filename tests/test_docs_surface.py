from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_new_package_surfaces() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "argumentation.ranking",
        "argumentation.weighted",
        "argumentation.gradual",
        "argumentation.value_based",
        "argumentation.accrual",
    ):
        assert expected in readme

    assert (
        "adapted grounded edge-tracking TD backend" in readme
        or "adapted grounded edge-tracking tree-decomposition backend" in readme
    )
    readme_without_emphasis = readme.replace("*", "").casefold()
    assert "not the full popescu & wallner i/o/u witness-table dp" in readme_without_emphasis


def test_architecture_documents_new_package_surfaces() -> None:
    architecture = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")

    for expected in (
        "argumentation.ranking",
        "argumentation.weighted",
        "argumentation.gradual",
        "argumentation.value_based",
        "argumentation.accrual",
    ):
        assert expected in architecture

    assert "adapted grounded edge-tracking" in architecture
    assert "not the full Popescu & Wallner I/O/U witness-table DP" in architecture
