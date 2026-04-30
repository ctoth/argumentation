from __future__ import annotations

from argumentation.dung import ArgumentationFramework
from argumentation.dynamic import (
    DynamicArgumentationFramework,
    apply_update_stream,
    parse_update_stream,
)


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
