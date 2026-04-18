"""Tests for Cayrol-style bipolar argumentation and Dung attack metadata."""

from __future__ import annotations

from argumentation.bipolar import (
    BipolarArgumentationFramework,
    c_preferred_extensions,
    cayrol_derived_defeats,
    d_preferred_extensions,
    s_preferred_extensions,
)
from argumentation.dung import (
    ArgumentationFramework,
    admissible,
    complete_extensions,
    conflict_free,
    grounded_extension,
    stable_extensions,
)


class TestCayrolDerivedDefeats:
    def test_supported_defeat(self) -> None:
        supports = frozenset({("A", "B")})
        defeats = frozenset({("B", "C")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("A", "C") in derived

    def test_indirect_defeat(self) -> None:
        supports = frozenset({("B", "C")})
        defeats = frozenset({("A", "B")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("A", "C") in derived

    def test_no_supports_no_derived(self) -> None:
        defeats = frozenset({("A", "B")})
        derived = cayrol_derived_defeats(defeats, frozenset())
        assert derived == frozenset()

    def test_no_defeats_no_derived(self) -> None:
        supports = frozenset({("A", "B")})
        derived = cayrol_derived_defeats(frozenset(), supports)
        assert derived == frozenset()

    def test_chain_supported_defeat(self) -> None:
        supports = frozenset({("A", "B"), ("B", "C")})
        defeats = frozenset({("C", "D")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("A", "D") in derived
        assert ("B", "D") in derived

    def test_chain_indirect_defeat(self) -> None:
        supports = frozenset({("B", "C"), ("C", "D")})
        defeats = frozenset({("A", "B")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("A", "C") in derived
        assert ("A", "D") in derived

    def test_cayrol_derived_defeats_chain_transitively(self) -> None:
        supports = frozenset({("A", "B"), ("C", "D")})
        defeats = frozenset({("B", "C")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("A", "C") in derived
        assert ("B", "D") in derived
        assert ("A", "D") in derived

    def test_direct_defeat_not_duplicated(self) -> None:
        supports = frozenset({("A", "B")})
        defeats = frozenset({("A", "C")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("A", "C") not in derived

    def test_self_support_loop_terminates(self) -> None:
        supports = frozenset({("A", "B"), ("B", "A")})
        defeats = frozenset({("A", "C")})
        derived = cayrol_derived_defeats(defeats, supports)
        assert ("B", "C") in derived


class TestAttackBasedConflictFree:
    def test_defeat_based_cf_allows_single_undefeated_argument(self) -> None:
        defeats = frozenset({("A", "B")})
        assert not conflict_free(frozenset({"A", "B"}), defeats)
        assert conflict_free(frozenset({"B"}), defeats)

    def test_attack_based_cf_blocks_coexistence(self) -> None:
        attacks = frozenset({("A", "B"), ("B", "A")})
        assert not conflict_free(frozenset({"A", "B"}), attacks)

    def test_admissible_uses_attacks(self) -> None:
        args = frozenset({"A", "B"})
        attacks = frozenset({("B", "A")})
        defeats = frozenset()
        assert admissible(frozenset({"A", "B"}), args, defeats)
        assert not admissible(frozenset({"A", "B"}), args, defeats, attacks=attacks)

    def test_complete_extensions_with_attacks(self) -> None:
        framework = ArgumentationFramework(
            arguments=frozenset({"A", "B"}),
            defeats=frozenset(),
            attacks=frozenset({("A", "B")}),
        )
        exts = complete_extensions(framework)
        assert frozenset({"A", "B"}) not in exts

    def test_complete_extensions_attacks_with_defeats(self) -> None:
        framework = ArgumentationFramework(
            arguments=frozenset({"A", "B"}),
            defeats=frozenset({("A", "B")}),
            attacks=frozenset({("A", "B"), ("B", "A")}),
        )
        exts = complete_extensions(framework)
        assert frozenset({"A"}) in exts
        assert frozenset({"A", "B"}) not in exts

    def test_stable_extensions_with_attacks(self) -> None:
        framework = ArgumentationFramework(
            arguments=frozenset({"A", "B"}),
            defeats=frozenset(),
            attacks=frozenset({("A", "B"), ("B", "A")}),
        )
        exts = stable_extensions(framework)
        assert frozenset({"A", "B"}) not in exts

    def test_grounded_extension_ignores_attack_metadata(self) -> None:
        framework = ArgumentationFramework(
            arguments=frozenset({"A", "B"}),
            defeats=frozenset(),
            attacks=frozenset({("A", "B")}),
        )
        assert grounded_extension(framework) == frozenset({"A", "B"})


class TestBipolarExtensions:
    def test_bipolar_preferred_semantics_differ(self) -> None:
        framework = BipolarArgumentationFramework(
            arguments=frozenset({"A", "B", "C", "H"}),
            defeats=frozenset({("A", "B")}),
            supports=frozenset({("C", "B")}),
        )
        candidate = frozenset({"A", "C", "H"})
        assert candidate in d_preferred_extensions(framework)
        assert candidate not in s_preferred_extensions(framework)
        assert candidate not in c_preferred_extensions(framework)

    def test_bipolar_helpers_on_supported_defeat_fixture(self) -> None:
        framework = BipolarArgumentationFramework(
            arguments=frozenset({"A", "B", "C"}),
            defeats=frozenset({("B", "C")}),
            supports=frozenset({("A", "B")}),
        )
        assert frozenset({"A", "B"}) in d_preferred_extensions(framework)
        assert frozenset({"A", "B"}) in s_preferred_extensions(framework)
        assert frozenset({"A", "B"}) in c_preferred_extensions(framework)
