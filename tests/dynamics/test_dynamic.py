from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.core.dung import ArgumentationFramework
from argumentation.dynamics.dynamic import (
    DynamicRecomputeOracle,
    DynamicArgumentationFramework,
    DynamicUpdate,
    IncrementalDynamicArgumentationFramework,
    incremental_extension_update,
    apply_update_stream,
    parse_update_stream,
)
from argumentation.dynamics.enforcement import extensions_for


def test_dynamic_queries_recompute_after_attack_updates() -> None:
    dynamic = DynamicArgumentationFramework(
        ArgumentationFramework(arguments=frozenset({"a", "b"}), defeats=frozenset())
    )

    assert dynamic.query_skeptical("b", semantics="grounded") is True

    dynamic.add_attack("a", "b")

    assert dynamic.query_credulous("b", semantics="preferred") is False
    assert dynamic.query_skeptical("a", semantics="grounded") is True


def test_dynamic_argument_removal_drops_incident_attacks() -> None:
    dynamic = DynamicArgumentationFramework(
        ArgumentationFramework(
            arguments=frozenset({"a", "b"}),
            defeats=frozenset({("a", "b")}),
        )
    )

    dynamic.remove_argument("a")

    assert dynamic.framework.arguments == frozenset({"b"})
    assert dynamic.framework.defeats == frozenset()


def test_parse_and_apply_update_stream() -> None:
    updates = parse_update_stream(
        """
        add_arg a
        add_arg b
        add_att a b
        del_att a b
        """
    )
    dynamic = apply_update_stream(
        DynamicArgumentationFramework(
            ArgumentationFramework(arguments=frozenset(), defeats=frozenset())
        ),
        updates,
    )

    assert dynamic.framework.arguments == frozenset({"a", "b"})
    assert dynamic.framework.defeats == frozenset()


def test_recompute_oracle_matches_direct_final_framework_for_update_stream() -> None:
    initial = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c")}),
    )
    updates = (
        DynamicUpdate("add_arg", "d"),
        DynamicUpdate("add_att", "d", "a"),
        DynamicUpdate("del_arg", "b"),
    )

    oracle = DynamicRecomputeOracle(initial)
    result = oracle.apply_all(updates)

    assert result.framework == ArgumentationFramework(
        arguments=frozenset({"a", "c", "d"}),
        defeats=frozenset({("d", "a")}),
    )
    assert result.extensions("grounded") == extensions_for(result.framework, "grounded")


@settings(max_examples=80)
@given(
    add_a=st.booleans(),
    add_b=st.booleans(),
    add_c=st.booleans(),
    del_a=st.booleans(),
    add_ab=st.booleans(),
    del_ab=st.booleans(),
)
def test_update_stream_operations_match_dynamic_track_set_effects(
    add_a: bool,
    add_b: bool,
    add_c: bool,
    del_a: bool,
    add_ab: bool,
    del_ab: bool,
) -> None:
    updates: list[DynamicUpdate] = []
    expected_arguments: set[str] = set()
    expected_defeats: set[tuple[str, str]] = set()
    for enabled, argument in ((add_a, "a"), (add_b, "b"), (add_c, "c")):
        if enabled:
            updates.append(DynamicUpdate("add_arg", argument))
            expected_arguments.add(argument)
    if add_ab and {"a", "b"} <= expected_arguments:
        updates.append(DynamicUpdate("add_att", "a", "b"))
        expected_defeats.add(("a", "b"))
    if del_ab:
        updates.append(DynamicUpdate("del_att", "a", "b"))
        expected_defeats.discard(("a", "b"))
    if del_a:
        updates.append(DynamicUpdate("del_arg", "a"))
        expected_arguments.discard("a")
        expected_defeats = {defeat for defeat in expected_defeats if "a" not in defeat}

    oracle = DynamicRecomputeOracle(
        ArgumentationFramework(arguments=frozenset(), defeats=frozenset())
    )

    assert oracle.apply_all(tuple(updates)).framework == ArgumentationFramework(
        arguments=frozenset(expected_arguments),
        defeats=frozenset(expected_defeats),
    )


def example_6_framework() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d", "e"}),
        defeats=frozenset(
            {
                ("a", "b"),
                ("b", "c"),
                ("b", "d"),
                ("c", "d"),
                ("c", "e"),
                ("e", "c"),
            }
        ),
    )


def test_incremental_algorithm_reuses_extension_for_irrelevant_stable_update() -> None:
    framework = example_6_framework()

    result = incremental_extension_update(
        framework,
        DynamicUpdate("add_att", "d", "d"),
        semantics="stable",
        initial_extension=frozenset({"a", "c"}),
    )

    assert result.extension == frozenset({"a", "c"})
    assert result.influenced == frozenset()
    assert result.used_incremental is True
    assert result.fallback_reason is None


def test_incremental_algorithm_falls_back_when_stable_reduced_af_has_no_extension() -> (
    None
):
    framework = example_6_framework()

    result = incremental_extension_update(
        framework,
        DynamicUpdate("add_att", "d", "d"),
        semantics="stable",
        initial_extension=frozenset({"a", "d", "e"}),
    )

    assert result.influenced == frozenset({"d"})
    assert result.reduced_framework == ArgumentationFramework(
        arguments=frozenset({"d"}),
        defeats=frozenset({("d", "d")}),
    )
    assert result.used_incremental is False
    assert result.fallback_reason == "reduced_solver_no_extension"
    assert result.extension in extensions_for(result.updated_framework, "stable")


def test_incremental_algorithm_combines_reduced_preferred_extension_without_fallback() -> (
    None
):
    framework = example_6_framework()

    result = incremental_extension_update(
        framework,
        DynamicUpdate("add_att", "d", "d"),
        semantics="preferred",
        initial_extension=frozenset({"a", "d", "e"}),
    )

    assert result.influenced == frozenset({"d"})
    assert result.reduced_extension == frozenset()
    assert result.extension == frozenset({"a", "e"})
    assert result.used_incremental is True
    assert result.fallback_reason is None
    assert result.extension in extensions_for(result.updated_framework, "preferred")


def test_incremental_state_queries_expose_witnesses_and_counterexamples() -> None:
    dynamic = IncrementalDynamicArgumentationFramework(
        example_6_framework(),
        semantics="stable",
        current_extension=frozenset({"a", "d", "e"}),
    )

    result = dynamic.apply(DynamicUpdate("add_att", "d", "d"))

    assert result.used_incremental is False
    assert result.fallback_reason == "reduced_solver_no_extension"
    assert dynamic.current_extension == frozenset({"a", "c"})

    credulous = dynamic.query_credulous("c")
    skeptical = dynamic.query_skeptical("d")

    assert credulous.accepted is True
    assert credulous.witness == frozenset({"a", "c"})
    assert skeptical.accepted is False
    assert skeptical.counterexample == frozenset({"a", "c"})


def test_incremental_state_reports_honest_recompute_for_unsupported_update_kind() -> (
    None
):
    dynamic = IncrementalDynamicArgumentationFramework(
        ArgumentationFramework(arguments=frozenset({"a"}), defeats=frozenset()),
        semantics="grounded",
        current_extension=frozenset({"a"}),
    )

    result = dynamic.apply(DynamicUpdate("add_arg", "b"))

    assert result.used_incremental is False
    assert result.fallback_reason == "unsupported_update_kind"
    assert result.updated_framework.arguments == frozenset({"a", "b"})
    assert dynamic.current_extension == frozenset({"a", "b"})


def _preference_filtered_af() -> ArgumentationFramework:
    """a attacks b, but a preference blocks the defeat (Modgil & Prakken 2018)."""
    return ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset(),
        attacks=frozenset({("a", "b")}),
    )


def test_noop_updates_preserve_pre_preference_attacks() -> None:
    """Issue #5: a set-wise no-op change must leave the framework unchanged.

    Cayrol et al. 2014, Definition 7, defines each change operation on
    ``(A, R)`` purely by the added or removed argument/interaction, so
    adding an argument already in ``A`` or removing an interaction not in
    ``R`` yields the same AF. The pre-preference attack relation is part of
    that AF: Modgil & Prakken 2018, Definition 14, checks conflict-freeness
    against attacks, so dropping it changes the naive extensions.
    """
    framework = _preference_filtered_af()
    for update in (
        DynamicUpdate("add_arg", "a"),
        DynamicUpdate("del_arg", "missing"),
        DynamicUpdate("del_att", "b", "a"),
    ):
        dynamic = DynamicArgumentationFramework(framework)
        dynamic.apply(update)

        assert dynamic.framework == framework, update
    oracle = DynamicRecomputeOracle(framework).apply(DynamicUpdate("add_arg", "a"))
    assert oracle.framework == framework


def test_argument_updates_keep_unaffected_attacks() -> None:
    """Issue #5: removing argument Z drops only Z's interactions (Cayrol 2014, Def 7)."""
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("c", "a")}),
        attacks=frozenset({("a", "b"), ("c", "a")}),
    )
    dynamic = DynamicArgumentationFramework(framework)

    dynamic.add_argument("d")
    assert dynamic.framework.attacks == framework.attacks

    dynamic.remove_argument("c")
    assert dynamic.framework == ArgumentationFramework(
        arguments=frozenset({"a", "b", "d"}),
        defeats=frozenset(),
        attacks=frozenset({("a", "b")}),
    )


def test_attack_updates_change_both_relations_of_mixed_framework() -> None:
    """Issue #5 control: an added interaction is a successful attack.

    A defeat is an attack that survives preference filtering (Modgil &
    Prakken 2018, Definition 9), so adding an interaction adds it to both
    relations and removing it removes it from both.
    """
    dynamic = DynamicArgumentationFramework(_preference_filtered_af())

    dynamic.add_attack("b", "a")
    assert dynamic.framework.defeats == frozenset({("b", "a")})
    assert dynamic.framework.attacks == frozenset({("a", "b"), ("b", "a")})

    dynamic.remove_attack("a", "b")
    assert dynamic.framework.defeats == frozenset({("b", "a")})
    assert dynamic.framework.attacks == frozenset({("b", "a")})

    plain = DynamicArgumentationFramework(
        ArgumentationFramework(arguments=frozenset({"a", "b"}), defeats=frozenset())
    )
    plain.add_attack("a", "b")
    assert plain.framework.attacks is None
    assert plain.framework.defeats == frozenset({("a", "b")})
