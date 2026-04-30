from __future__ import annotations

from argumentation.caf import (
    ClaimAugmentedAF,
    claim_level_extensions,
    concurrence_holds,
    extensions,
    inherited_extensions,
)
from argumentation.dung import ArgumentationFramework, stable_extensions


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_inherited_claim_extensions_project_dung_extensions() -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})
    caf = ClaimAugmentedAF(framework=framework, claims={"a": "A", "b": "B"})

    assert set(inherited_extensions(caf, semantics="stable")) == {
        frozenset({"A"}),
        frozenset({"B"}),
    }
    assert {
        frozenset(caf.claims[arg] for arg in extension)
        for extension in stable_extensions(framework)
    } == set(inherited_extensions(caf, semantics="stable"))


def test_duplicate_argument_claims_collapse_inherited_extensions() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2"}, set()),
        claims={"a1": "A", "a2": "A"},
    )

    assert inherited_extensions(caf, semantics="preferred") == (frozenset({"A"}),)


def test_claim_level_extensions_maximize_claim_sets() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("a1", "b"), ("b", "a1")}),
        claims={"a1": "A", "a2": "A", "b": "B"},
    )

    assert claim_level_extensions(caf, semantics="naive") == (
        frozenset({"A", "B"}),
    )


def test_bijective_claims_have_inherited_claim_level_concurrence() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a", "b"}, {("a", "b"), ("b", "a")}),
        claims={"a": "A", "b": "B"},
    )

    assert concurrence_holds(caf, semantics="stable") is True
    assert extensions(caf, semantics="stable", view="inherited") == inherited_extensions(
        caf,
        semantics="stable",
    )
    assert extensions(caf, semantics="stable", view="claim_level") == claim_level_extensions(
        caf,
        semantics="stable",
    )


def test_claim_level_stable_uses_claim_defeat_range() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a1", "a2", "b"}, {("a2", "a2"), ("a2", "a1"), ("a1", "b")}),
        claims={"a1": "A", "a2": "A", "b": "B"},
    )

    assert inherited_extensions(caf, semantics="stable") == ()
    assert claim_level_extensions(caf, semantics="stable") == (frozenset({"A"}),)
    assert claim_level_extensions(caf, semantics="stable-admissible") == ()


def test_claim_level_stage_maximizes_claim_ranges() -> None:
    caf = ClaimAugmentedAF(
        framework=af({"a", "b", "c1", "c2"}, {("b", "a"), ("b", "c1"), ("c1", "c1"), ("c2", "c2")}),
        claims={"a": "A", "b": "B", "c1": "C", "c2": "C"},
    )

    assert set(claim_level_extensions(caf, semantics="stage")) == {
        frozenset({"A"}),
        frozenset({"B"}),
    }
