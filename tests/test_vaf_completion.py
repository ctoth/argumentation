from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from argumentation.vaf import ValueBasedArgumentationFramework
from argumentation.vaf_completion import (
    FACT_VALUE,
    ArgumentChain,
    ArgumentLine,
    VAFArgumentStatus,
    build_lines_of_argument,
    classify_line_of_argument,
    fact_first_audiences,
    is_skeptically_objective_under_fact_uncertainty,
    make_argument_chain,
    two_value_cycle_extension,
)


def test_argument_chain_validates_definition_6_3_and_parity() -> None:
    # Bench-Capon 2003 p. 438, Definition 6.3: a chain is same-valued,
    # starts without an in-chain attacker, and then alternates by parity.
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2", "a3"}),
        attacks=frozenset({("a1", "a2"), ("a2", "a3")}),
        values=frozenset({"life"}),
        valuation={"a1": "life", "a2": "life", "a3": "life"},
        audience=("life",),
    )

    chain = make_argument_chain(vaf, ("a1", "a2", "a3"))

    assert chain.value == "life"
    assert chain.odd_arguments() == frozenset({"a1", "a3"})
    assert chain.even_arguments() == frozenset({"a2"})
    assert chain.accepted_arguments(start_accepted=True) == frozenset({"a1", "a3"})
    assert chain.accepted_arguments(start_accepted=False) == frozenset({"a2"})


def test_argument_chain_rejects_mixed_values_and_non_linear_attackers() -> None:
    # Bench-Capon 2003 p. 438 requires one value and one predecessor attack per
    # non-first chain argument.
    mixed_values = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2"}),
        attacks=frozenset({("a1", "a2")}),
        values=frozenset({"life", "property"}),
        valuation={"a1": "life", "a2": "property"},
        audience=("life", "property"),
    )
    with pytest.raises(ValueError, match="same value"):
        make_argument_chain(mixed_values, ("a1", "a2"))

    two_chain_attackers = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2", "x"}),
        attacks=frozenset({("a1", "x"), ("x", "a2"), ("a1", "a2")}),
        values=frozenset({"life"}),
        valuation={"a1": "life", "a2": "life", "x": "life"},
        audience=("life",),
    )
    with pytest.raises(ValueError, match="only by its predecessor"):
        make_argument_chain(two_chain_attackers, ("a1", "x", "a2"))


def test_line_of_argument_builds_distinct_value_chains_and_stops_on_repeat() -> None:
    # Bench-Capon 2003 p. 439, Definition 6.5: each later chain's last
    # argument attacks the first argument of the previous chain, with no
    # repeated value in the line.
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"r1", "r2", "b1", "r0"}),
        attacks=frozenset({("r1", "r2"), ("b1", "r1"), ("r0", "b1")}),
        values=frozenset({"red", "blue"}),
        valuation={"r1": "red", "r2": "red", "b1": "blue", "r0": "red"},
        audience=("red", "blue"),
    )

    lines = build_lines_of_argument(vaf, "r2")

    assert lines == (
        ArgumentLine(
            chains=(
                ArgumentChain(arguments=("r1", "r2"), value="red"),
                ArgumentChain(arguments=("b1",), value="blue"),
            ),
            target="r2",
            terminated_by_repeated_value=True,
        ),
    )


def test_theorem_6_6_classifies_objective_subjective_and_indefensible_cases() -> None:
    # Bench-Capon 2003 p. 440, Theorem 6.6: for no single-valued cycles and at
    # most one attacker per argument, line parity determines status.
    objective_line = ArgumentLine(
        chains=(ArgumentChain(arguments=("a1",), value="life"),),
        target="a1",
    )
    objective_vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1"}),
        attacks=frozenset(),
        values=frozenset({"life"}),
        valuation={"a1": "life"},
        audience=("life",),
    )
    assert classify_line_of_argument(objective_vaf, objective_line) is VAFArgumentStatus.OBJECTIVE

    indefensible_vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2"}),
        attacks=frozenset({("a1", "a2")}),
        values=frozenset({"life"}),
        valuation={"a1": "life", "a2": "life"},
        audience=("life",),
    )
    indefensible_line = ArgumentLine(
        chains=(ArgumentChain(arguments=("a1", "a2"), value="life"),),
        target="a2",
    )
    assert classify_line_of_argument(indefensible_vaf, indefensible_line) is (
        VAFArgumentStatus.INDEFENSIBLE
    )

    subjective_vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2", "b1"}),
        attacks=frozenset({("a1", "a2"), ("b1", "a1")}),
        values=frozenset({"life", "property"}),
        valuation={"a1": "life", "a2": "life", "b1": "property"},
        audience=("life", "property"),
    )
    subjective_line = ArgumentLine(
        chains=(
            ArgumentChain(arguments=("a1", "a2"), value="life"),
            ArgumentChain(arguments=("b1",), value="property"),
        ),
        target="a2",
    )
    assert classify_line_of_argument(subjective_vaf, subjective_line) is (
        VAFArgumentStatus.SUBJECTIVE
    )


def test_theorem_6_6_classifier_fails_outside_preconditions() -> None:
    # Bench-Capon 2003 p. 440 states the classifier for no single-valued cycles
    # and at most one attacker per argument.
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset({"a1", "a2", "a3"}),
        attacks=frozenset({("a1", "a2"), ("a3", "a2")}),
        values=frozenset({"life"}),
        valuation={"a1": "life", "a2": "life", "a3": "life"},
        audience=("life",),
    )
    line = ArgumentLine(
        chains=(ArgumentChain(arguments=("a1", "a2"), value="life"),),
        target="a2",
    )

    with pytest.raises(ValueError, match="at most one attacker"):
        classify_line_of_argument(vaf, line)


def _two_value_cycle(length_a: int, length_b: int, preferred: str) -> tuple[
    ValueBasedArgumentationFramework,
    tuple[ArgumentChain, ArgumentChain],
    tuple[str, str],
]:
    a_args = tuple(f"a{i}" for i in range(1, length_a + 1))
    b_args = tuple(f"b{i}" for i in range(1, length_b + 1))
    attacks = {(a_args[i], a_args[i + 1]) for i in range(len(a_args) - 1)}
    attacks.update((b_args[i], b_args[i + 1]) for i in range(len(b_args) - 1))
    attacks.add((a_args[-1], b_args[0]))
    attacks.add((b_args[-1], a_args[0]))
    vaf = ValueBasedArgumentationFramework(
        arguments=frozenset(a_args + b_args),
        attacks=frozenset(attacks),
        values=frozenset({"a-value", "b-value"}),
        valuation={**dict.fromkeys(a_args, "a-value"), **dict.fromkeys(b_args, "b-value")},
        audience=(preferred, "b-value" if preferred == "a-value" else "a-value"),
    )
    return (
        vaf,
        (
            ArgumentChain(arguments=a_args, value="a-value"),
            ArgumentChain(arguments=b_args, value="b-value"),
        ),
        vaf.audience or (),
    )


def test_corollary_6_7_two_value_cycle_matches_preferred_extension() -> None:
    # Bench-Capon 2003 pp. 440-441, Corollary 6.7: the parity construction for
    # two-valued cycles matches the audience-specific preferred extension.
    vaf, chains, audience = _two_value_cycle(2, 3, "a-value")

    assert two_value_cycle_extension(vaf, chains, audience) == frozenset({"a1", "b1", "b3"})
    assert vaf.preferred_extensions_for_audience(audience) == [frozenset({"a1", "b1", "b3"})]


@given(
    length_a=st.integers(min_value=1, max_value=4),
    length_b=st.integers(min_value=1, max_value=4),
    preferred=st.sampled_from(("a-value", "b-value")),
)
def test_generated_two_value_cycles_match_corollary_6_7_and_preferred_extensions(
    length_a: int,
    length_b: int,
    preferred: str,
) -> None:
    vaf, chains, audience = _two_value_cycle(length_a, length_b, preferred)

    corollary_extension = two_value_cycle_extension(vaf, chains, audience)

    assert vaf.preferred_extensions_for_audience(audience) == [corollary_extension]


def test_fact_value_is_ranked_above_every_ordinary_value() -> None:
    # Bench-Capon 2003 p. 444: the fact value is given the highest preference
    # for every reasonable audience.
    audiences = fact_first_audiences(frozenset({FACT_VALUE, "life", "property"}))

    assert set(audiences) == {
        (FACT_VALUE, "life", "property"),
        (FACT_VALUE, "property", "life"),
    }


def test_fact_argument_blocks_ordinary_attack_and_uncertainty_has_multiple_extensions() -> None:
    # Bench-Capon 2003 pp. 444-447: accepted facts outrank ordinary values, but
    # factual uncertainty can create multiple preferred extensions.
    fact_blocks_life = ValueBasedArgumentationFramework(
        arguments=frozenset({"G", "F"}),
        attacks=frozenset({("G", "F"), ("F", "G")}),
        values=frozenset({FACT_VALUE, "life"}),
        valuation={"G": FACT_VALUE, "F": "life"},
        audience=(FACT_VALUE, "life"),
    )
    assert fact_blocks_life.successful_attacks() == frozenset({("G", "F")})
    assert fact_blocks_life.preferred_extensions_for_audience((FACT_VALUE, "life")) == [
        frozenset({"G"})
    ]

    factual_uncertainty = ValueBasedArgumentationFramework(
        arguments=frozenset({"G", "H", "K"}),
        attacks=frozenset({("G", "H"), ("H", "G")}),
        values=frozenset({FACT_VALUE, "life"}),
        valuation={"G": FACT_VALUE, "H": FACT_VALUE, "K": "life"},
        audiences=((FACT_VALUE, "life"),),
    )
    assert factual_uncertainty.preferred_extensions_for_audience((FACT_VALUE, "life")) == [
        frozenset({"G", "K"}),
        frozenset({"H", "K"}),
    ]
    assert is_skeptically_objective_under_fact_uncertainty(factual_uncertainty, "K")
    assert not is_skeptically_objective_under_fact_uncertainty(factual_uncertainty, "G")


@given(
    ordinary_values=st.lists(
        st.sampled_from(("life", "property", "liberty")),
        min_size=1,
        max_size=3,
        unique=True,
    )
)
def test_generated_fact_first_audiences_always_rank_facts_highest(
    ordinary_values: list[str],
) -> None:
    # Bench-Capon 2003 p. 444: fact is above every ordinary value for every
    # reasonable audience.
    values = frozenset([FACT_VALUE, *ordinary_values])

    for audience in fact_first_audiences(values):
        assert audience[0] == FACT_VALUE
        assert frozenset(audience) == values
