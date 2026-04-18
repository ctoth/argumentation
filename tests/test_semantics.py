from __future__ import annotations

import pytest

from argumentation.bipolar import BipolarArgumentationFramework
from argumentation.dung import ArgumentationFramework
from argumentation.partial_af import PartialArgumentationFramework
from argumentation.semantics import accepted_arguments, extensions


def test_dung_extensions_dispatches_standard_semantics() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c")}),
    )

    assert extensions(framework, semantics="grounded") == (frozenset({"a", "c"}),)
    assert extensions(framework, semantics="complete") == (frozenset({"a", "c"}),)
    assert extensions(framework, semantics="preferred") == (frozenset({"a", "c"}),)
    assert extensions(framework, semantics="stable") == (frozenset({"a", "c"}),)


def test_accepted_arguments_supports_credulous_and_skeptical_modes() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    assert accepted_arguments(
        framework,
        semantics="preferred",
        mode="credulous",
    ) == frozenset({"a", "b"})
    assert accepted_arguments(
        framework,
        semantics="preferred",
        mode="skeptical",
    ) == frozenset()


def test_bipolar_extensions_dispatch_preferred_and_stable_variants() -> None:
    framework = BipolarArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("b", "c")}),
        supports=frozenset({("a", "b")}),
    )

    assert extensions(framework, semantics="d-preferred")
    assert extensions(framework, semantics="s-preferred")
    assert extensions(framework, semantics="c-preferred")
    assert extensions(framework, semantics="bipolar-stable")


def test_partial_af_extensions_are_completion_based() -> None:
    framework = PartialArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        attacks=frozenset({("a", "b")}),
        ignorance=frozenset({("b", "a")}),
        non_attacks=frozenset({("a", "a"), ("b", "b")}),
    )

    assert extensions(framework, semantics="grounded") == (
        frozenset(),
        frozenset({"a"}),
    )
    assert accepted_arguments(
        framework,
        semantics="grounded",
        mode="credulous",
    ) == frozenset({"a"})
    assert accepted_arguments(
        framework,
        semantics="grounded",
        mode="skeptical",
    ) == frozenset()


def test_semantics_rejects_unknown_framework_and_mode() -> None:
    with pytest.raises(TypeError):
        extensions(object(), semantics="grounded")
    with pytest.raises(ValueError, match="mode"):
        accepted_arguments(
            ArgumentationFramework(arguments=frozenset(), defeats=frozenset()),
            semantics="grounded",
            mode="both",
        )
