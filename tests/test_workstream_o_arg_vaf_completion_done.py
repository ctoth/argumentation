from __future__ import annotations

from argumentation.vaf import ValueBasedArgumentationFramework
from argumentation.vaf_completion import (
    FACT_VALUE,
    ArgumentChain,
    ArgumentLine,
    VAFArgumentStatus,
    classify_line_of_argument,
    is_skeptically_objective_under_fact_uncertainty,
    two_value_cycle_extension,
)


def test_workstream_o_arg_vaf_completion_done() -> None:
    # Bench-Capon 2003 pp. 438-447: chain/line parity, two-value-cycle
    # corollary, and fact-valued uncertainty are public package behavior.
    line_vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2", "b1"}),
        attacks=frozenset({("a1", "a2"), ("b1", "a1")}),
        values=frozenset({"life", "property"}),
        valuation={"a1": "life", "a2": "life", "b1": "property"},
        audience=("life", "property"),
    )
    line = ArgumentLine(
        chains=(
            ArgumentChain(arguments=("a1", "a2"), value="life"),
            ArgumentChain(arguments=("b1",), value="property"),
        ),
        target="a2",
    )
    assert classify_line_of_argument(line_vaf, line) is VAFArgumentStatus.SUBJECTIVE

    cycle_vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2", "b1"}),
        attacks=frozenset({("a1", "a2"), ("a2", "b1"), ("b1", "a1")}),
        values=frozenset({"a-value", "b-value"}),
        valuation={"a1": "a-value", "a2": "a-value", "b1": "b-value"},
        audience=("a-value", "b-value"),
    )
    cycle_extension = two_value_cycle_extension(
        cycle_vaf,
        (
            ArgumentChain(arguments=("a1", "a2"), value="a-value"),
            ArgumentChain(arguments=("b1",), value="b-value"),
        ),
        ("a-value", "b-value"),
    )
    assert cycle_extension == frozenset({"a1", "b1"})
    assert cycle_vaf.preferred_extensions_for_audience(("a-value", "b-value")) == [
        cycle_extension
    ]

    factual_uncertainty = ValueBasedArgumentationFramework(
        arguments=frozenset({"G", "H", "K"}),
        attacks=frozenset({("G", "H"), ("H", "G")}),
        values=frozenset({FACT_VALUE, "life"}),
        valuation={"G": FACT_VALUE, "H": FACT_VALUE, "K": "life"},
        audiences=((FACT_VALUE, "life"),),
    )
    assert is_skeptically_objective_under_fact_uncertainty(factual_uncertainty, "K")
    assert not is_skeptically_objective_under_fact_uncertainty(factual_uncertainty, "G")
