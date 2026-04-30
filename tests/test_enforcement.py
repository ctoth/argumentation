from __future__ import annotations

from argumentation.dung import ArgumentationFramework, stable_extensions
from argumentation.enforcement import (
    AFEdit,
    apply_edit,
    enforce_credulous,
    enforce_extension,
    enforce_skeptical,
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
