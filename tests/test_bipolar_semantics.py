"""Tests for explicit Cayrol 2005 bipolar semantics."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.bipolar import (
    BipolarArgumentationFramework,
    c_admissible,
    c_preferred_extensions,
    conflict_free,
    d_admissible,
    d_preferred_extensions,
    defends,
    derived_set_defeats,
    s_admissible,
    s_preferred_extensions,
    safe,
    set_defeats,
    set_supports,
    stable_extensions,
    support_closed,
)


def baf(
    args: set[str],
    defeats: set[tuple[str, str]],
    supports: set[tuple[str, str]],
) -> BipolarArgumentationFramework:
    return BipolarArgumentationFramework(
        arguments=frozenset(args),
        defeats=frozenset(defeats),
        supports=frozenset(supports),
    )


class TestCayrolDefinitions:
    def test_set_support_and_set_defeat_match_example_2_left_fragment(self):
        framework = baf(
            {"A", "B", "C", "D", "E", "G", "H"},
            {("G", "A"), ("E", "C"), ("H", "B"), ("C", "D")},
            {("A", "B"), ("B", "C")},
        )
        assert set_supports(frozenset({"A"}), "B", framework)
        assert set_supports(frozenset({"A"}), "C", framework)
        assert set_defeats(frozenset({"B"}), "D", framework)
        assert set_defeats(frozenset({"H"}), "C", framework)

    def test_bipolar_d_admissible_differs_from_s_admissible_when_safety_fails(self):
        framework = baf(
            {"A", "B", "C", "D", "F"},
            {("C", "D")},
            {("A", "B"), ("B", "C"), ("F", "D")},
        )
        candidate = frozenset({"B", "F"})
        assert conflict_free(candidate, framework)
        assert defends(candidate, "B", framework)
        assert defends(candidate, "F", framework)
        assert d_admissible(candidate, framework)
        assert not safe(candidate, framework)
        assert not s_admissible(candidate, framework)

    def test_bipolar_c_admissible_requires_support_closure(self):
        framework = baf(
            {"A", "B"},
            set(),
            {("A", "B")},
        )
        candidate = frozenset({"A"})
        assert conflict_free(candidate, framework)
        assert d_admissible(candidate, framework)
        assert s_admissible(candidate, framework)
        assert not support_closed(candidate, framework)
        assert not c_admissible(candidate, framework)

    def test_cayrol_example_2_set_classifications(self):
        framework = baf(
            {"A", "B", "C", "D", "E", "F", "G", "H"},
            {("G", "A"), ("E", "C"), ("H", "B"), ("C", "D")},
            {("A", "B"), ("B", "C"), ("F", "D")},
        )
        assert conflict_free(frozenset({"A", "H"}), framework)
        assert not safe(frozenset({"A", "H"}), framework)
        assert conflict_free(frozenset({"B", "F"}), framework)
        assert not safe(frozenset({"B", "F"}), framework)
        assert not conflict_free(frozenset({"H", "C"}), framework)
        assert not conflict_free(frozenset({"B", "D"}), framework)
        assert safe(frozenset({"G", "H", "E"}), framework)

    def test_preferred_hierarchy_distinguishes_d_s_c(self):
        framework = baf(
            {"A", "B", "C", "H"},
            {("H", "B"), ("A", "C")},
            {("A", "B"), ("C", "A")},
        )
        assert frozenset({"A", "H"}) in d_preferred_extensions(framework)
        assert frozenset({"A", "H"}) not in s_preferred_extensions(framework)
        assert frozenset({"A", "H"}) not in c_preferred_extensions(framework)


@st.composite
def bipolar_frameworks(draw, max_args: int = 6):
    args = draw(
        st.frozensets(
            st.text(alphabet="abcdef", min_size=1, max_size=2),
            min_size=1,
            max_size=max_args,
        )
    )
    arg_list = sorted(args)
    pairs = [
        (source, target)
        for source in arg_list
        for target in arg_list
        if source != target
    ]
    defeats = draw(
        st.frozensets(
            st.sampled_from(pairs),
            max_size=len(pairs),
        )
    ) if pairs else frozenset()
    support_pairs = [pair for pair in pairs if pair not in defeats]
    supports = draw(
        st.frozensets(
            st.sampled_from(support_pairs),
            max_size=len(support_pairs),
        )
    ) if support_pairs else frozenset()
    return BipolarArgumentationFramework(
        arguments=args,
        defeats=defeats,
        supports=supports,
    )


_PROP_SETTINGS = settings(deadline=None)


class TestCayrolProperties:
    @given(bipolar_frameworks())
    @_PROP_SETTINGS
    def test_safe_implies_conflict_free(self, framework):
        candidate = frozenset(sorted(framework.arguments)[: len(framework.arguments) // 2])
        if safe(candidate, framework):
            assert conflict_free(candidate, framework)

    @given(bipolar_frameworks())
    @_PROP_SETTINGS
    def test_conflict_free_and_support_closed_implies_safe(self, framework):
        candidate = frozenset(
            arg for index, arg in enumerate(sorted(framework.arguments)) if index % 2 == 0
        )
        if conflict_free(candidate, framework) and support_closed(candidate, framework):
            assert safe(candidate, framework)

    @given(bipolar_frameworks())
    @_PROP_SETTINGS
    def test_c_implies_s_implies_d(self, framework):
        candidate = frozenset(
            arg for index, arg in enumerate(sorted(framework.arguments)) if index % 2 == 0
        )
        if c_admissible(candidate, framework):
            assert s_admissible(candidate, framework)
        if s_admissible(candidate, framework):
            assert d_admissible(candidate, framework)

    @given(bipolar_frameworks())
    @_PROP_SETTINGS
    def test_set_defeat_is_monotone_in_the_attacking_set(self, framework):
        ordered = sorted(framework.arguments)
        subset = frozenset(ordered[: len(ordered) // 2])
        superset = frozenset(ordered)
        for target in framework.arguments:
            if set_defeats(subset, target, framework):
                assert set_defeats(superset, target, framework)

    @given(bipolar_frameworks())
    @_PROP_SETTINGS
    def test_derived_set_defeats_is_idempotent(self, framework):
        first = derived_set_defeats(framework)
        second = derived_set_defeats(
            BipolarArgumentationFramework(
                arguments=framework.arguments,
                defeats=first,
                supports=framework.supports,
            )
        )
        assert second == first

    @given(bipolar_frameworks())
    @_PROP_SETTINGS
    def test_stable_extensions_are_d_admissible(self, framework):
        for extension in stable_extensions(framework):
            assert d_admissible(extension, framework)


# ── Support cycle and self-support property tests (audit-2026-03-28) ──

from argumentation.bipolar import cayrol_derived_defeats


@st.composite
def bipolar_frameworks_with_cycles(draw, max_args: int = 5):
    """Generate bipolar frameworks that may include self-supports and support cycles.

    The standard bipolar_frameworks() strategy excludes self-edges.
    This strategy allows self-supports (A supports A) and support cycles
    (A supports B, B supports A) to test termination guarantees.
    """
    args = draw(
        st.frozensets(
            st.text(alphabet="abcde", min_size=1, max_size=2),
            min_size=2,
            max_size=max_args,
        )
    )
    arg_list = sorted(args)
    # All pairs INCLUDING self-edges for supports
    all_pairs = [(s, t) for s in arg_list for t in arg_list]
    non_self_pairs = [(s, t) for s, t in all_pairs if s != t]

    # Defeats: no self-defeats (standard)
    defeats = draw(
        st.frozensets(
            st.sampled_from(non_self_pairs),
            max_size=len(non_self_pairs),
        )
    ) if non_self_pairs else frozenset()

    # Supports: allow self-supports, exclude edges that are defeats
    support_candidates = [p for p in all_pairs if p not in defeats]
    supports = draw(
        st.frozensets(
            st.sampled_from(support_candidates),
            max_size=len(support_candidates),
        )
    ) if support_candidates else frozenset()

    return BipolarArgumentationFramework(
        arguments=args,
        defeats=defeats,
        supports=supports,
    )


class TestBipolarCycleProperties:
    """Property tests for bipolar frameworks with support cycles.

    Cayrol & Lagasquie-Schiex (2005): derived defeats must reach a fixpoint
    even when support cycles exist. The working_defeats set grows monotonically
    and is bounded by |args|^2, guaranteeing termination.
    """

    @given(bipolar_frameworks_with_cycles())
    @_PROP_SETTINGS
    def test_derived_defeats_terminates_with_self_supports(self, framework):
        """cayrol_derived_defeats terminates even with self-supports (A→A)."""
        derived = cayrol_derived_defeats(framework.defeats, framework.supports)
        assert isinstance(derived, frozenset)

    @given(bipolar_frameworks_with_cycles())
    @_PROP_SETTINGS
    def test_derived_defeats_no_self_defeats(self, framework):
        """Derived defeats never include self-defeats (A, A).

        Self-defeats are filtered by cayrol_derived_defeats (source != target).
        """
        derived = cayrol_derived_defeats(framework.defeats, framework.supports)
        for src, tgt in derived:
            assert src != tgt, f"Self-defeat ({src}, {src}) in derived defeats"

    @given(bipolar_frameworks_with_cycles())
    @_PROP_SETTINGS
    def test_derived_defeats_idempotent_with_cycles(self, framework):
        """Applying derived_set_defeats twice gives the same result — even with cycles."""
        first = derived_set_defeats(framework)
        second = derived_set_defeats(
            BipolarArgumentationFramework(
                arguments=framework.arguments,
                defeats=first,
                supports=framework.supports,
            )
        )
        assert second == first, (
            f"Not idempotent: first pass added {first - framework.defeats}, "
            f"second pass added {second - first}"
        )

    @given(bipolar_frameworks_with_cycles())
    @_PROP_SETTINGS
    def test_derived_defeats_bounded_by_argument_pairs(self, framework):
        """Total defeats (original + derived) bounded by |args|^2.

        The defeat closure cannot exceed the total number of possible
        directed pairs (excluding self-edges).
        """
        derived = cayrol_derived_defeats(framework.defeats, framework.supports)
        total = framework.defeats | derived
        n = len(framework.arguments)
        max_possible = n * (n - 1)  # directed pairs, no self-edges
        assert len(total) <= max_possible

    @given(bipolar_frameworks_with_cycles())
    @_PROP_SETTINGS
    def test_support_closed_terminates_with_cycles(self, framework):
        """support_closed check terminates even with support cycles."""
        candidate = frozenset(sorted(framework.arguments)[:len(framework.arguments) // 2])
        # Just verify it returns a boolean without hanging
        result = support_closed(candidate, framework)
        assert isinstance(result, bool)

    @given(bipolar_frameworks_with_cycles())
    @_PROP_SETTINGS
    def test_safe_implies_conflict_free_with_cycles(self, framework):
        """safe(S) => conflict_free(S) holds even with support cycles."""
        candidate = frozenset(sorted(framework.arguments)[:len(framework.arguments) // 2])
        if safe(candidate, framework):
            assert conflict_free(candidate, framework)
