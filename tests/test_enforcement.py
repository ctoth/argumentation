from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.dung import ArgumentationFramework, stable_extensions
from argumentation.enforcement import (
    AFEdit,
    apply_edit,
    enforce_credulous,
    enforce_extension,
    enforce_expansion_credulous,
    enforce_skeptical,
    is_normal_expansion,
    is_strong_expansion,
    is_weak_expansion,
)


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def test_credulous_enforcement_returns_minimal_hamming_change() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    result = enforce_credulous(framework, "b", semantics="preferred")

    assert result.cost == 1
    assert "b" in result.accepted_arguments
    assert any("b" in extension for extension in result.extensions)
    assert result.witness_framework == apply_edit(framework, result.edit)


def test_skeptical_enforcement_makes_argument_accepted_in_every_extension() -> None:
    framework = af({"a", "b"}, {("a", "b"), ("b", "a")})

    result = enforce_skeptical(framework, "a", semantics="stable")

    assert result.cost == 1
    assert result.accepted_arguments == frozenset({"a"})
    assert result.extensions == (frozenset({"a"}),)


def test_extension_enforcement_makes_target_a_stable_extension() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    result = enforce_extension(framework, frozenset({"b"}), semantics="stable")

    assert result.cost == 1
    assert frozenset({"b"}) in stable_extensions(result.witness_framework)


def test_apply_edit_can_add_and_remove_arguments_and_defeats() -> None:
    framework = af({"a", "b"}, {("a", "b")})
    edit = AFEdit(
        add_arguments=frozenset({"c"}),
        remove_arguments=frozenset({"a"}),
        add_defeats=frozenset({("c", "b")}),
        remove_defeats=frozenset({("a", "b")}),
    )

    assert apply_edit(framework, edit) == af({"b", "c"}, {("c", "b")})


def test_fixed_argument_extension_enforcement_matches_wallner_example_strict() -> None:
    framework = af(
        {"a", "b", "c", "d"},
        {("b", "a"), ("b", "c"), ("c", "a"), ("c", "d"), ("d", "b")},
    )

    result = enforce_extension(
        framework,
        frozenset({"a"}),
        semantics="complete",
        variant="strict",
        max_cost=2,
    )

    assert result.cost == 2
    assert result.edit.remove_defeats == frozenset({("b", "a"), ("c", "a")})
    assert result.edit.add_defeats == frozenset()
    assert frozenset({"a"}) in result.extensions


def test_fixed_argument_extension_enforcement_matches_wallner_example_non_strict() -> None:
    framework = af(
        {"a", "b", "c", "d"},
        {("b", "a"), ("b", "c"), ("c", "a"), ("c", "d"), ("d", "b")},
    )

    result = enforce_extension(
        framework,
        frozenset({"a"}),
        semantics="complete",
        variant="non-strict",
        max_cost=1,
    )

    assert result.cost == 1
    assert result.edit.add_defeats == frozenset({("d", "c")})
    assert result.edit.remove_defeats == frozenset()
    assert any(frozenset({"a"}) < extension for extension in result.extensions)


def test_expansion_credulous_enforcement_rejects_old_attack_deletion() -> None:
    framework = af({"a", "b"}, {("a", "b")})

    result = enforce_expansion_credulous(
        framework,
        "b",
        semantics="preferred",
        kind="normal",
        candidate_new_arguments=frozenset({"x1"}),
        max_new_arguments=1,
        max_added_defeats=1,
    )

    assert result.cost == 2
    assert result.expansion.new_arguments == frozenset({"x1"})
    assert result.expansion.added_defeats == frozenset({("x1", "a")})
    assert framework.defeats <= result.witness_framework.defeats
    assert result.witness_framework.defeats & {("b", "a")} == frozenset()
    assert is_normal_expansion(framework, result.witness_framework)
    assert any("b" in extension for extension in result.extensions)


@settings(max_examples=100)
@given(
    old_defeat_ab=st.booleans(),
    old_defeat_ba=st.booleans(),
    old_old_add_ab=st.booleans(),
    old_old_add_ba=st.booleans(),
    old_to_new=st.booleans(),
    new_to_old=st.booleans(),
    new_to_new=st.booleans(),
)
def test_normal_expansion_iff_old_material_preserved_and_only_new_interactions_added(
    old_defeat_ab: bool,
    old_defeat_ba: bool,
    old_old_add_ab: bool,
    old_old_add_ba: bool,
    old_to_new: bool,
    new_to_old: bool,
    new_to_new: bool,
) -> None:
    old_defeats = {
        defeat
        for include, defeat in (
            (old_defeat_ab, ("a", "b")),
            (old_defeat_ba, ("b", "a")),
        )
        if include
    }
    original = af({"a", "b"}, old_defeats)
    expanded_defeats = set(old_defeats)
    if old_old_add_ab:
        expanded_defeats.add(("a", "b"))
    if old_old_add_ba:
        expanded_defeats.add(("b", "a"))
    if old_to_new:
        expanded_defeats.add(("a", "x"))
    if new_to_old:
        expanded_defeats.add(("x", "a"))
    if new_to_new:
        expanded_defeats.add(("x", "x"))
    expanded = af({"a", "b", "x"}, expanded_defeats)

    added_defeats = expanded.defeats - original.defeats
    expected = original.defeats <= expanded.defeats and all(
        source == "x" or target == "x" for source, target in added_defeats
    )

    assert is_normal_expansion(original, expanded) is expected


def test_strong_and_weak_expansion_restrict_attack_direction_between_old_and_new() -> None:
    original = af({"a"}, set())

    old_attacks_new = af({"a", "x"}, {("a", "x")})
    new_attacks_old = af({"a", "x"}, {("x", "a")})
    new_attacks_new = af({"a", "x"}, {("x", "x")})

    assert is_normal_expansion(original, old_attacks_new)
    assert is_normal_expansion(original, new_attacks_old)
    assert is_normal_expansion(original, new_attacks_new)

    assert not is_strong_expansion(original, old_attacks_new)
    assert is_weak_expansion(original, old_attacks_new)

    assert is_strong_expansion(original, new_attacks_old)
    assert not is_weak_expansion(original, new_attacks_old)

    assert is_strong_expansion(original, new_attacks_new)
    assert is_weak_expansion(original, new_attacks_new)
