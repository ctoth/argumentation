from __future__ import annotations

from argumentation.dung import ArgumentationFramework, grounded_extension, preferred_extensions
from argumentation.setaf import (
    SETAF,
    admissible,
    conflict_free,
    grounded_extension as setaf_grounded_extension,
    preferred_extensions as setaf_preferred_extensions,
    stable_extensions,
)


def test_collective_attack_requires_all_attackers() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )

    assert conflict_free(framework, frozenset({"a", "c"})) is True
    assert conflict_free(framework, frozenset({"a", "b", "c"})) is False


def test_admissibility_defends_against_collective_attackers() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c", "x", "y"}),
        attacks=frozenset(
            {
                (frozenset({"a", "b"}), "c"),
                (frozenset({"x"}), "a"),
                (frozenset({"y"}), "b"),
            }
        ),
    )

    assert admissible(framework, frozenset({"c", "x"})) is False
    assert admissible(framework, frozenset({"c", "x", "y"})) is True


def test_singleton_setaf_reduces_to_dung_for_grounded_and_preferred() -> None:
    attacks = frozenset({(frozenset({"a"}), "b"), (frozenset({"b"}), "a")})
    setaf = SETAF(arguments=frozenset({"a", "b"}), attacks=attacks)
    dung = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b"), ("b", "a")}),
    )

    assert setaf_grounded_extension(setaf) == grounded_extension(dung)
    assert set(setaf_preferred_extensions(setaf)) == set(preferred_extensions(dung))


def test_stable_extensions_cover_outsiders_with_collective_attacks() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )

    assert stable_extensions(framework) == (frozenset({"a", "b"}),)
