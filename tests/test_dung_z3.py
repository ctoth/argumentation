"""Tests for z3-backed Dung extension computation.

Verifies z3 SAT encodings produce identical results to the brute-force
reference implementations in dung.py using Hypothesis property testing.
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from argumentation.dung import (
    ArgumentationFramework,
    stable_extensions,
    complete_extensions,
    preferred_extensions,
)
from argumentation.dung_z3 import (
    z3_stable_extensions,
    z3_complete_extensions,
    z3_preferred_extensions,
    credulously_accepted,
    skeptically_accepted,
)
from tests.test_dung import argumentation_frameworks, af, af_with_attacks_superset


class TestZ3StableConcrete:
    """Concrete stable extension tests."""

    def test_empty_framework(self):
        framework = af(set(), set())
        assert set(z3_stable_extensions(framework)) == set(stable_extensions(framework))

    def test_unattacked_wins(self):
        framework = af({"A", "B"}, {("A", "B")})
        assert set(z3_stable_extensions(framework)) == {frozenset({"A"})}

    def test_nixon_diamond(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        result = set(z3_stable_extensions(framework))
        assert result == {frozenset({"A"}), frozenset({"B"})}

    def test_odd_cycle_no_stable(self):
        """Odd cycle has no stable extension."""
        framework = af({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")})
        assert z3_stable_extensions(framework) == []

    def test_self_attacker(self):
        """Self-attacking A with target B: no stable extension exists."""
        framework = af({"A", "B"}, {("A", "A"), ("A", "B")})
        # Brute-force oracle: empty set can't defeat B, {B} can't defeat A, etc.
        assert set(z3_stable_extensions(framework)) == set(
            stable_extensions(framework)
        )


class TestZ3CompleteConcrete:
    def test_empty_framework(self):
        framework = af(set(), set())
        assert set(z3_complete_extensions(framework)) == set(
            complete_extensions(framework)
        )

    def test_unattacked_wins(self):
        framework = af({"A", "B"}, {("A", "B")})
        assert set(z3_complete_extensions(framework)) == set(
            complete_extensions(framework)
        )

    def test_nixon_diamond(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        assert set(z3_complete_extensions(framework)) == set(
            complete_extensions(framework)
        )


class TestZ3PreferredConcrete:
    def test_empty_framework(self):
        framework = af(set(), set())
        assert set(z3_preferred_extensions(framework)) == set(
            preferred_extensions(framework)
        )

    def test_nixon_diamond(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        assert set(z3_preferred_extensions(framework)) == set(
            preferred_extensions(framework)
        )


class TestZ3MatchesBruteForce:
    """Hypothesis property tests: z3 matches brute-force for all semantics."""

    pytestmark = [pytest.mark.property, pytest.mark.differential]

    @given(argumentation_frameworks())
    @settings(deadline=10000)
    def test_stable_matches(self, framework):
        assert set(z3_stable_extensions(framework)) == set(
            stable_extensions(framework)
        )

    @given(argumentation_frameworks())
    @settings(deadline=10000)
    def test_complete_matches(self, framework):
        assert set(z3_complete_extensions(framework)) == set(
            complete_extensions(framework)
        )

    @given(argumentation_frameworks())
    @settings(deadline=10000)
    def test_preferred_matches(self, framework):
        assert set(z3_preferred_extensions(framework)) == set(
            preferred_extensions(framework)
        )


class TestZ3MatchesBruteForceWithAttacksDefeatsDivergence:
    """Property tests for AFs where attacks is a superset of defeats.

    These characterize the extended Modgil & Prakken semantics:
    conflict-freeness is checked against attacks while defense is checked
    against defeats. The z3 backend must match the brute-force reference
    on these mixed-relation frameworks too.
    """

    pytestmark = [pytest.mark.property, pytest.mark.differential]

    @given(af_with_attacks_superset())
    @settings(deadline=10000)
    def test_stable_matches(self, framework):
        assert set(z3_stable_extensions(framework)) == set(
            stable_extensions(framework, backend="brute")
        )

    @given(af_with_attacks_superset())
    @settings(deadline=10000)
    def test_complete_matches(self, framework):
        assert set(z3_complete_extensions(framework)) == set(
            complete_extensions(framework, backend="brute")
        )

    @given(af_with_attacks_superset())
    @settings(deadline=10000)
    def test_preferred_matches(self, framework):
        assert set(z3_preferred_extensions(framework)) == set(
            preferred_extensions(framework, backend="brute")
        )


class TestAcceptability:
    """Tests for credulous/skeptical acceptance queries."""

    def test_credulous_nixon_diamond(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        # Both A and B are credulously accepted under stable semantics
        assert credulously_accepted(framework, "A", semantics="stable") is True
        assert credulously_accepted(framework, "B", semantics="stable") is True

    def test_skeptical_nixon_diamond(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        # Neither A nor B is skeptically accepted (not in ALL extensions)
        assert skeptically_accepted(framework, "A", semantics="stable") is False
        assert skeptically_accepted(framework, "B", semantics="stable") is False

    def test_skeptical_unattacked(self):
        framework = af({"A", "B"}, {("A", "B")})
        assert skeptically_accepted(framework, "A", semantics="stable") is True
        assert skeptically_accepted(framework, "B", semantics="stable") is False

    def test_credulous_no_stable(self):
        """Odd cycle: no stable extension, so nothing is credulously accepted."""
        framework = af({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")})
        assert credulously_accepted(framework, "A", semantics="stable") is False

    def test_credulous_complete(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        # Under complete semantics, A is in {A} extension
        assert credulously_accepted(framework, "A", semantics="complete") is True

    def test_skeptical_complete(self):
        framework = af({"A", "B"}, {("A", "B"), ("B", "A")})
        # Under complete, {} is an extension, so A is not in all
        assert skeptically_accepted(framework, "A", semantics="complete") is False


class TestHardInstances:
    """Hand-crafted instances known to stress SAT solvers."""

    def test_symmetric_chain_10(self):
        """Long symmetric attack chain: a1<->a2<->a3<->...<->a10."""
        args = {f"a{i}" for i in range(10)}
        attacks = set()
        for i in range(9):
            attacks.add((f"a{i}", f"a{i+1}"))
            attacks.add((f"a{i+1}", f"a{i}"))
        framework = af(args, attacks)
        assert set(z3_stable_extensions(framework)) == set(
            stable_extensions(framework)
        )
        assert set(z3_preferred_extensions(framework)) == set(
            preferred_extensions(framework)
        )

    def test_odd_cycle_7(self):
        """Odd cycle of 7 -- no stable extension exists."""
        args = {f"a{i}" for i in range(7)}
        attacks = {(f"a{i}", f"a{(i+1)%7}") for i in range(7)}
        framework = af(args, attacks)
        assert z3_stable_extensions(framework) == []
        assert set(z3_complete_extensions(framework)) == set(
            complete_extensions(framework)
        )
