from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.dung import ArgumentationFramework
from argumentation.dynamic import (
    DynamicRecomputeOracle,
    DynamicArgumentationFramework,
    DynamicUpdate,
    incremental_extension_update,
    apply_update_stream,
    parse_update_stream,
)
from argumentation.enforcement import extensions_for


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
        expected_defeats = {
            defeat for defeat in expected_defeats if "a" not in defeat
        }

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


def test_incremental_algorithm_falls_back_when_stable_reduced_af_has_no_extension() -> None:
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


def test_incremental_algorithm_combines_reduced_preferred_extension_without_fallback() -> None:
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
