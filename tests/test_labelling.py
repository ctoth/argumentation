from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from argumentation.dung import (
    ArgumentationFramework,
    complete_extensions,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)
from argumentation.labelling import Label, Labelling


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


class TestLabellingValueObject:
    def test_labels_are_the_three_standard_statuses(self) -> None:
        assert Label.IN.value == "in"
        assert Label.OUT.value == "out"
        assert Label.UNDEC.value == "undec"

    def test_labelling_is_immutable_and_normalizes_statuses(self) -> None:
        labelling = Labelling.from_statuses(
            arguments=frozenset({"a", "b", "c"}),
            statuses={"a": Label.IN, "b": "out", "c": Label.UNDEC},
        )

        assert labelling.in_arguments == frozenset({"a"})
        assert labelling.out_arguments == frozenset({"b"})
        assert labelling.undecided_arguments == frozenset({"c"})
        with pytest.raises(FrozenInstanceError):
            labelling.statuses = {}  # type: ignore[misc]

    def test_labelling_rejects_missing_extra_and_unknown_statuses(self) -> None:
        with pytest.raises(ValueError, match="exactly"):
            Labelling.from_statuses(
                arguments=frozenset({"a", "b"}),
                statuses={"a": Label.IN},
            )
        with pytest.raises(ValueError, match="exactly"):
            Labelling.from_statuses(
                arguments=frozenset({"a"}),
                statuses={"a": Label.IN, "b": Label.OUT},
            )
        with pytest.raises(ValueError, match="label"):
            Labelling.from_statuses(
                arguments=frozenset({"a"}),
                statuses={"a": "accepted"},
            )

    def test_range_is_in_arguments_plus_out_arguments(self) -> None:
        labelling = Labelling.from_statuses(
            arguments=frozenset({"a", "b", "c"}),
            statuses={"a": Label.IN, "b": Label.OUT, "c": Label.UNDEC},
        )

        assert labelling.range == frozenset({"a", "b"})
        assert labelling.extension == frozenset({"a"})


class TestExtensionLabellingConversion:
    def test_extension_conversion_marks_defeated_outsiders_out(self) -> None:
        framework = af(
            {"a", "b", "c"},
            {("a", "b"), ("b", "c")},
        )

        labelling = Labelling.from_extension(framework, frozenset({"a", "c"}))

        assert labelling.in_arguments == frozenset({"a", "c"})
        assert labelling.out_arguments == frozenset({"b"})
        assert labelling.undecided_arguments == frozenset()
        assert labelling.extension == frozenset({"a", "c"})

    def test_extension_conversion_leaves_unattacked_outsiders_undecided(self) -> None:
        framework = af(
            {"a", "b"},
            {("a", "b"), ("b", "a")},
        )

        labelling = Labelling.from_extension(framework, frozenset())

        assert labelling.in_arguments == frozenset()
        assert labelling.out_arguments == frozenset()
        assert labelling.undecided_arguments == frozenset({"a", "b"})

    def test_extension_conversion_rejects_unknown_arguments(self) -> None:
        framework = af({"a"}, set())

        with pytest.raises(ValueError, match="extension"):
            Labelling.from_extension(framework, frozenset({"missing"}))

    def test_complete_grounded_preferred_and_stable_round_trip(self) -> None:
        framework = af(
            {"a", "b", "c"},
            {("a", "b"), ("b", "a"), ("b", "c")},
        )
        extension_families = [
            [grounded_extension(framework)],
            complete_extensions(framework, backend="brute"),
            preferred_extensions(framework, backend="brute"),
            stable_extensions(framework, backend="brute"),
        ]

        for extensions in extension_families:
            assert extensions
            for extension in extensions:
                labelling = Labelling.from_extension(framework, extension)
                assert labelling.extension == extension
