from __future__ import annotations

from argumentation.adf import (
    ThreeValued,
    adf_to_dung,
    dung_to_adf,
    grounded_interpretation,
    interpretation_from_mapping,
)
from argumentation.dung import ArgumentationFramework, grounded_extension, stable_extensions


def test_dung_to_adf_preserves_grounded_single_attack() -> None:
    af = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    adf = dung_to_adf(af)

    assert grounded_interpretation(adf) == interpretation_from_mapping(
        {"a": ThreeValued.T, "b": ThreeValued.F}
    )
    assert adf_to_dung(adf) == af


def test_dung_to_adf_preserves_stable_extensions_for_mutual_attack() -> None:
    af = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    assert stable_extensions(adf_to_dung(dung_to_adf(af))) == stable_extensions(af)
    assert grounded_extension(adf_to_dung(dung_to_adf(af))) == grounded_extension(af)
