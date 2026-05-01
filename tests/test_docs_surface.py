from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_new_package_surfaces() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "argumentation.ranking",
        "argumentation.weighted",
        "argumentation.gradual",
        "argumentation.subjective_aspic",
        "argumentation.vaf",
        "argumentation.practical_reasoning",
        "argumentation.ranking_axioms",
        "argumentation.accrual",
        "argumentation.setaf",
        "argumentation.enforcement",
        "argumentation.caf",
        "argumentation.dynamic",
        "argumentation.approximate",
        "argumentation.epistemic",
        "argumentation.llm_surface",
    ):
        assert expected in readme

    assert (
        "adapted grounded edge-tracking TD backend" in readme
        or "adapted grounded edge-tracking tree-decomposition backend" in readme
    )
    readme_without_emphasis = " ".join(readme.replace("*", "").casefold().split())
    assert "not the full popescu & wallner i/o/u witness-table dp" in readme_without_emphasis


def test_architecture_documents_new_package_surfaces() -> None:
    architecture = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")

    for expected in (
        "argumentation.ranking",
        "argumentation.weighted",
        "argumentation.gradual",
        "argumentation.subjective_aspic",
        "argumentation.vaf",
        "argumentation.practical_reasoning",
        "argumentation.ranking_axioms",
        "argumentation.accrual",
        "argumentation.setaf",
        "argumentation.enforcement",
        "argumentation.caf",
        "argumentation.dynamic",
        "argumentation.approximate",
        "argumentation.epistemic",
        "argumentation.llm_surface",
    ):
        assert expected in architecture

    assert "adapted grounded edge-tracking" in architecture
    assert "not the full Popescu & Wallner I/O/U witness-table DP" in architecture


def test_readme_documents_solver_contracts_and_capabilities() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "solver_capability_matrix",
        "ExtensionEnumerationSuccess",
        "SingleExtensionSuccess",
        "AcceptanceSuccess",
        "ICCMA_ABA_SOLVER",
        "ASPFORABA_SOLVER",
        "one witness, not full enumeration",
        "unsupported task/semantics/backend combinations return typed unavailable",
        "External callers supply already-projected frameworks",
        "does not own caller",
        "identity, storage, merge policy, provenance, or rendering policy",
    ):
        assert expected in readme

    assert "there is no ABA solver dispatcher yet" not in readme


def test_architecture_documents_solver_contracts_and_capabilities() -> None:
    architecture = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")

    for expected in (
        "solver_capability_matrix",
        "ExtensionEnumerationSuccess",
        "SingleExtensionSuccess",
        "AcceptanceSuccess",
        "ICCMA_AF_SOLVER",
        "ASPFORABA_SOLVER",
        "one ICCMA witness is not full enumeration",
        "unsupported combinations return typed unavailable",
        "External callers supply already-projected frameworks",
        "not own caller",
        "identity, storage, merge policy, provenance, or rendering",
    ):
        assert expected in architecture

    assert "there is no ABA solver dispatcher yet" not in architecture
