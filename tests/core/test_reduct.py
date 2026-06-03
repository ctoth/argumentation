from __future__ import annotations

from argumentation.core.reduct import SemanticReduct


def test_semantic_reduct_lifts_and_deduplicates_residual_extensions() -> None:
    reduct = SemanticReduct(
        original="original",
        residual="residual",
        fixed_in=frozenset({"a"}),
        fixed_out=frozenset({"b"}),
    )

    assert reduct.is_trivial is False
    assert reduct.lift(frozenset({"c"})) == frozenset({"a", "c"})
    assert reduct.lift_all([frozenset({"c"}), frozenset({"c"}), frozenset()]) == [
        frozenset({"a", "c"}),
        frozenset({"a"}),
    ]


def test_semantic_reduct_projects_fixed_requirements() -> None:
    reduct = SemanticReduct(
        original="original",
        residual="residual",
        fixed_in=frozenset({"in"}),
        fixed_out=frozenset({"out"}),
    )

    projected = reduct.project_requirements(
        required_in={"in", "residual_in"},
        required_out={"out", "residual_out"},
    )

    assert projected == (
        frozenset({"residual_in"}),
        frozenset({"residual_out"}),
    )


def test_semantic_reduct_rejects_conflicting_fixed_requirements() -> None:
    reduct = SemanticReduct(
        original="original",
        residual="residual",
        fixed_in=frozenset({"in"}),
        fixed_out=frozenset({"out"}),
    )

    assert reduct.project_requirements(required_in={"out"}) is None
    assert reduct.project_requirements(required_out={"in"}) is None


def test_semantic_reduct_rejects_residual_in_out_contradiction() -> None:
    reduct = SemanticReduct(
        original="original",
        residual="residual",
        fixed_in=frozenset({"in"}),
        fixed_out=frozenset({"out"}),
    )

    projected = reduct.project_requirements(
        required_in={"in", "a"},
        required_out={"out", "a"},
    )

    assert projected is None
