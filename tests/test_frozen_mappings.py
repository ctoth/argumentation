"""Frozen framework types must own immutable snapshots of their mapping fields.

Issue #27: frozen dataclasses validated their mapping inputs and then kept the
caller's mutable dict (or a mutable copy), so a caller could bypass the
validated ranges after construction. Each framework's defining function is
fixed once the framework is built, e.g. the initial weight function of a
weighted bipolar graph (Potyka 2018, Def 1), a PrAF's P_A and P_D (Li et al.
2011, Def 2, p.2), a VAF valuation (Bench-Capon 2003), and an ABA contrary
map (Bondarenko et al. 1997).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.core.dung import ArgumentationFramework
from argumentation.core.labelling import Label, Labelling
from argumentation.dynamics.af_revision import ExtensionRevisionState
from argumentation.frameworks.adf import AbstractDialecticalFramework, Atom, True_
from argumentation.frameworks.caf import ClaimAugmentedAF
from argumentation.frameworks.practical_reasoning import (
    ActionBasedAlternatingTransitionSystem,
)
from argumentation.frameworks.vaf import ValueBasedArgumentationFramework
from argumentation.gradual.gradual import (
    WeightedBipolarGraph,
    quadratic_energy_strengths,
)
from argumentation.probabilistic.epistemic import (
    LinearAtomicConstraint,
    LinearRelation,
    ProbabilityFunction,
)
from argumentation.probabilistic.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
)
from argumentation.ranking.weighted import WeightedArgumentationFramework
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal

# Each case builds a framework from caller-owned dicts and names the fields
# holding them. The builder returns (framework, {field_name: caller_dict}).
Builder = Callable[[], tuple[Any, dict[str, dict[Any, Any]]]]


def _labelling() -> tuple[Any, dict[str, dict[Any, Any]]]:
    statuses: dict[Any, Any] = {"a": Label.IN}
    return Labelling(statuses), {"statuses": statuses}


def _revision_state() -> tuple[Any, dict[str, dict[Any, Any]]]:
    ranking: dict[Any, Any] = {frozenset({"a"}): 0, frozenset(): 1}
    state = ExtensionRevisionState(
        arguments=frozenset({"a"}),
        extensions=(frozenset({"a"}),),
        ranking=ranking,
    )
    return state, {"ranking": ranking}


def _adf() -> tuple[Any, dict[str, dict[Any, Any]]]:
    conditions: dict[Any, Any] = {"a": True_(), "b": Atom("a")}
    framework = AbstractDialecticalFramework(
        statements=frozenset({"a", "b"}),
        links=frozenset({("a", "b")}),
        acceptance_conditions=conditions,
    )
    return framework, {"acceptance_conditions": conditions}


def _caf() -> tuple[Any, dict[str, dict[Any, Any]]]:
    claims: dict[Any, Any] = {"a": "x", "b": "y"}
    framework = ClaimAugmentedAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")})),
        claims,
    )
    return framework, {"claims": claims}


def _aats() -> tuple[Any, dict[str, dict[Any, Any]]]:
    preconditions: dict[Any, Any] = {"go": frozenset({"q0"})}
    transitions: dict[Any, Any] = {("q0", "go"): "q1"}
    interpretation: dict[Any, Any] = {"q0": frozenset(), "q1": frozenset({"p"})}
    valuation: dict[Any, Any] = {("q0", "q1", "v"): "+"}
    system = ActionBasedAlternatingTransitionSystem(
        states=frozenset({"q0", "q1"}),
        initial_state="q0",
        agents=frozenset({"agent"}),
        actions=frozenset({"go"}),
        preconditions=preconditions,
        transitions=transitions,
        propositions=frozenset({"p"}),
        interpretation=interpretation,
        values=frozenset({"v"}),
        valuation=valuation,
    )
    return system, {
        "preconditions": preconditions,
        "transitions": transitions,
        "interpretation": interpretation,
        "valuation": valuation,
    }


def _vaf() -> tuple[Any, dict[str, dict[Any, Any]]]:
    valuation: dict[Any, Any] = {"a": "v1", "b": "v2"}
    framework = ValueBasedArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        attacks=frozenset({("a", "b")}),
        values=frozenset({"v1", "v2"}),
        valuation=valuation,
    )
    return framework, {"valuation": valuation}


def _weighted_bipolar_graph() -> tuple[Any, dict[str, dict[Any, Any]]]:
    weights: dict[Any, Any] = {"a": 0.5}
    return WeightedBipolarGraph(frozenset({"a"}), weights), {"initial_weights": weights}


def _probability_function() -> tuple[Any, dict[str, dict[Any, Any]]]:
    probabilities: dict[Any, Any] = {frozenset(): 0.25, frozenset({"a"}): 0.75}
    function = ProbabilityFunction(frozenset({"a"}), probabilities)
    return function, {"probabilities": probabilities}


def _linear_constraint() -> tuple[Any, dict[str, dict[Any, Any]]]:
    coefficients: dict[Any, Any] = {"a": 1.0, "b": -1.0}
    constraint = LinearAtomicConstraint(coefficients, LinearRelation.LE, 0.0)
    return constraint, {"coefficients": coefficients}


def _praf() -> tuple[Any, dict[str, dict[Any, Any]]]:
    edge = ("a", "b")
    p_args: dict[Any, Any] = {"a": 0.5, "b": 1.0}
    p_defeats: dict[Any, Any] = {edge: 0.5}
    p_attacks: dict[Any, Any] = {edge: 0.5}
    p_supports: dict[Any, Any] = {("b", "a"): 0.5}
    praf = ProbabilisticAF(
        ArgumentationFramework(frozenset({"a", "b"}), frozenset({edge})),
        p_args,
        p_defeats,
        p_attacks=p_attacks,
        supports=frozenset({("b", "a")}),
        p_supports=p_supports,
    )
    return praf, {
        "p_args": p_args,
        "p_defeats": p_defeats,
        "p_attacks": p_attacks,
        "p_supports": p_supports,
    }


def _weighted_af() -> tuple[Any, dict[str, dict[Any, Any]]]:
    weights: dict[Any, Any] = {("a", "b"): 2.0}
    framework = WeightedArgumentationFramework(
        frozenset({"a", "b"}), frozenset({("a", "b")}), weights
    )
    return framework, {"weights": weights}


def _aba() -> tuple[Any, dict[str, dict[Any, Any]]]:
    assumption = Literal(GroundAtom("alpha"))
    contrary_literal = Literal(GroundAtom("beta"))
    contrary: dict[Any, Any] = {assumption: contrary_literal}
    framework = ABAFramework(
        language=frozenset({assumption, contrary_literal}),
        rules=frozenset(),
        assumptions=frozenset({assumption}),
        contrary=contrary,
    )
    return framework, {"contrary": contrary}


BUILDERS: dict[str, Builder] = {
    "Labelling": _labelling,
    "ExtensionRevisionState": _revision_state,
    "AbstractDialecticalFramework": _adf,
    "ClaimAugmentedAF": _caf,
    "ActionBasedAlternatingTransitionSystem": _aats,
    "ValueBasedArgumentationFramework": _vaf,
    "WeightedBipolarGraph": _weighted_bipolar_graph,
    "ProbabilityFunction": _probability_function,
    "LinearAtomicConstraint": _linear_constraint,
    "ProbabilisticAF": _praf,
    "WeightedArgumentationFramework": _weighted_af,
    "ABAFramework": _aba,
}


@pytest.mark.parametrize("builder", BUILDERS.values(), ids=BUILDERS.keys())
def test_mapping_fields_reject_item_assignment(builder: Builder) -> None:
    """Issue #27: a frozen framework's mapping fields are read-only."""
    framework, caller_dicts = builder()

    for field_name in caller_dicts:
        mapping = getattr(framework, field_name)
        assert isinstance(mapping, Mapping)
        key = next(iter(mapping))
        with pytest.raises(TypeError):
            mapping[key] = mapping[key]  # type: ignore[index]


@pytest.mark.parametrize("builder", BUILDERS.values(), ids=BUILDERS.keys())
def test_mapping_fields_do_not_alias_caller_dicts(builder: Builder) -> None:
    """Issue #27: clearing the caller's dict after construction does not
    change the framework's validated mapping."""
    framework, caller_dicts = builder()
    snapshots = {
        field_name: dict(getattr(framework, field_name)) for field_name in caller_dicts
    }

    for caller_dict in caller_dicts.values():
        caller_dict.clear()

    for field_name, snapshot in snapshots.items():
        assert dict(getattr(framework, field_name)) == snapshot
        assert snapshot


def test_weighted_bipolar_graph_weights_cannot_leave_unit_interval() -> None:
    """Issue #27 counterexample: after validation the initial weight function
    maps into [0, 1] (Potyka 2018, Def 1); writing 2.0 must fail."""
    graph = WeightedBipolarGraph(frozenset({"a"}), {"a": 0.5})

    with pytest.raises(TypeError):
        graph.initial_weights["a"] = 2.0  # type: ignore[index]

    strengths = quadratic_energy_strengths(graph).strengths
    assert all(0.0 <= value <= 1.0 for value in strengths.values())


_weights = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)


@given(
    weights=st.dictionaries(
        st.sampled_from(["a", "b", "c"]), _weights, min_size=1, max_size=3
    ),
    tampered=st.floats(min_value=1.5, max_value=10.0),
)
@settings(max_examples=40, deadline=None)
def test_mutating_caller_weights_after_construction_keeps_semantics(
    weights: dict[str, float],
    tampered: float,
) -> None:
    """Issue #27 property: strengths computed after the caller rewrites its
    weight dict equal those of a graph built from an untouched copy."""
    arguments = frozenset(weights)
    attacks = frozenset({(x, y) for x in arguments for y in arguments if x < y})
    caller_weights = dict(weights)
    graph = WeightedBipolarGraph(arguments, caller_weights, attacks=attacks)
    reference = WeightedBipolarGraph(arguments, dict(weights), attacks=attacks)

    for argument in caller_weights:
        caller_weights[argument] = tampered
    caller_weights["intruder"] = tampered

    assert quadratic_energy_strengths(graph) == quadratic_energy_strengths(reference)


@given(
    p_a=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    p_defeat=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
@settings(max_examples=40, deadline=None)
def test_mutating_caller_probabilities_after_construction_keeps_semantics(
    p_a: float,
    p_defeat: float,
) -> None:
    """Issue #27 property: PrAF acceptance (Li et al. 2011, Eq 2, p.4) is fixed
    at construction even if the caller rewrites P_A and P_D afterwards."""
    framework = ArgumentationFramework(frozenset({"a", "b"}), frozenset({("a", "b")}))
    p_args = {"a": p_a, "b": 1.0}
    p_defeats = {("a", "b"): p_defeat}
    praf = ProbabilisticAF(framework, p_args, p_defeats)
    reference = ProbabilisticAF(framework, dict(p_args), dict(p_defeats))

    p_args["a"] = 7.0
    p_defeats.clear()

    assert compute_probabilistic_acceptance(
        praf, strategy="exact_enum"
    ) == compute_probabilistic_acceptance(reference, strategy="exact_enum")
