from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

import argumentation
from argumentation.vaf import ValueBasedArgumentationFramework


def test_vaf_module_is_exported() -> None:
    assert argumentation.vaf.ValueBasedArgumentationFramework is ValueBasedArgumentationFramework
    assert "vaf" in argumentation.__all__


def test_successful_attacks_follow_bench_capon_defeat_condition() -> None:
    # Bench-Capon 2003 p. 436, Definition 5.3: A defeats B iff A attacks B and
    # B's value is not preferred to A's value by the audience.
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({("a", "b"), ("b", "c")}),
        values=frozenset({"red", "blue"}),
        valuation={"a": "red", "b": "blue", "c": "blue"},
        audience=("blue", "red"),
    )

    assert vaf.successful_attacks() == frozenset({("b", "c")})
    assert vaf.with_audience(("red", "blue")).successful_attacks() == frozenset({
        ("a", "b"),
        ("b", "c"),
    })


def test_objective_and_subjective_acceptance_match_figure_2() -> None:
    # Bench-Capon 2003 p. 437, Figure 2: A(red)->B(blue)->C(blue). A is
    # objectively acceptable; B and C are only subjectively acceptable.
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"A", "B", "C"}),
        attacks=frozenset({("A", "B"), ("B", "C")}),
        values=frozenset({"red", "blue"}),
        valuation={"A": "red", "B": "blue", "C": "blue"},
    )

    assert vaf.preferred_extensions_for_audience(("red", "blue")) == [frozenset({"A", "C"})]
    assert vaf.preferred_extensions_for_audience(("blue", "red")) == [frozenset({"A", "B"})]
    assert vaf.objectively_acceptable() == frozenset({"A"})
    assert vaf.subjectively_acceptable() == frozenset({"A", "B", "C"})
    assert vaf.indefensible() == frozenset()


def test_same_value_attacks_always_succeed_even_when_audience_orders_other_values() -> None:
    # Bench-Capon 2003 p. 436: all attacks succeed when both arguments relate
    # to the same value.
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        attacks=frozenset({("a", "b")}),
        values=frozenset({"security", "cost"}),
        valuation={"a": "security", "b": "security"},
        audience=("cost", "security"),
    )

    assert vaf.successful_attacks() == frozenset({("a", "b")})


@given(
    attacker_value=st.sampled_from(("v0", "v1", "v2")),
    target_value=st.sampled_from(("v0", "v1", "v2")),
    audience=st.permutations(("v0", "v1", "v2")).map(tuple),
)
def test_generated_vaf_attacks_succeed_exactly_when_target_value_is_not_strictly_preferred(
    attacker_value: str,
    target_value: str,
    audience: tuple[str, str, str],
) -> None:
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"attacker", "target"}),
        attacks=frozenset({("attacker", "target")}),
        values=frozenset({"v0", "v1", "v2"}),
        valuation={"attacker": attacker_value, "target": target_value},
        audience=audience,
    )

    audience_rank = {value: index for index, value in enumerate(audience)}
    target_strictly_preferred = audience_rank[target_value] < audience_rank[attacker_value]
    expected = frozenset() if target_strictly_preferred else frozenset({("attacker", "target")})

    assert vaf.successful_attacks() == expected
