"""Contracts for flat-AF sat-core engine routing (exp 7A completion).

Preregistered RED before implementation. Asserts the per-op engine predicate,
that the choice is observable in SAT telemetry, that stable/ideal keep smt, and
that the routing is answer-preserving against the native enumerator.
"""

from __future__ import annotations

import random

import pytest

from argumentation.core.dung import ArgumentationFramework
from argumentation.solving.af_scc_cone import PREFERRED_CONE_MIN_DEFEATS
from argumentation.solving.solver import (
    SATConfig,
    solve_dung_acceptance,
    solve_dung_single_extension,
)
from argumentation.solving.solver import _flat_sat_engine  # RED: not yet defined


def _three_cycle() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c"), ("c", "a")}),
    )


def _dense_framework(size: int, extra_edges: int, seed: int) -> ArgumentationFramework:
    rng = random.Random(seed)
    args = [f"a{i}" for i in range(size)]
    defeats = {(args[i], args[(i + 1) % size]) for i in range(size)}
    for _ in range(extra_edges):
        u, v = rng.randrange(size), rng.randrange(size)
        if u != v:
            defeats.add((args[u], args[v]))
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def _big_defeat_framework() -> ArgumentationFramework:
    """>= PREFERRED_CONE_MIN_DEFEATS defeats, cheaply (dense small arg set)."""
    n = 200  # 200*199 = 39800 ordered pairs > 15000
    args = [f"a{i}" for i in range(n)]
    defeats = {(args[i], args[j]) for i in range(n) for j in range(n) if i != j}
    assert len(defeats) >= PREFERRED_CONE_MIN_DEFEATS
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


# --- Contract (a): engine-resolution predicate ---------------------------------


def test_flat_engine_complete_is_satcore():
    assert _flat_sat_engine("complete", _three_cycle()) == "sat-core"


def test_flat_engine_preferred_witness_is_satcore():
    assert _flat_sat_engine("preferred_witness", _three_cycle()) == "sat-core"


def test_flat_engine_cdas_small_is_smt():
    small = _dense_framework(20, 20, seed=1)
    assert len(small.defeats) < PREFERRED_CONE_MIN_DEFEATS
    assert _flat_sat_engine("cdas_skeptical", small) == "smt"


def test_flat_engine_cdas_big_is_satcore():
    assert _flat_sat_engine("cdas_skeptical", _big_defeat_framework()) == "sat-core"


def test_flat_engine_stable_and_ideal_keep_smt():
    fw = _dense_framework(20, 20, seed=2)
    assert _flat_sat_engine("stable", fw) == "smt"
    assert _flat_sat_engine("ideal", fw) == "smt"


# --- Contract (a)/(c): engine observable in telemetry --------------------------


def _engines_seen(framework, *, semantics, task, query):
    seen: list[str] = []

    def sink(check):
        eng = getattr(check, "engine", None)
        if eng is not None:
            seen.append(eng)

    solve_dung_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=query,
        backend="sat",
        sat=SATConfig(trace_sink=sink),
    )
    return seen


def test_flat_complete_acceptance_emits_satcore_engine():
    seen = _engines_seen(
        _three_cycle(), semantics="complete", task="credulous", query="a"
    )
    assert seen and all(e == "sat-core" for e in seen)


def test_flat_stable_acceptance_emits_smt_engine():
    seen = _engines_seen(
        _three_cycle(), semantics="stable", task="credulous", query="a"
    )
    assert seen and all(e == "smt" for e in seen)


# --- Contract (b): answer preservation vs native enumerator --------------------


@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize(
    "semantics,task",
    [
        ("complete", "credulous"),
        ("complete", "skeptical"),
        ("preferred", "credulous"),
        ("preferred", "skeptical"),
    ],
)
def test_flat_routing_answers_match_native(seed, semantics, task):
    fw = _dense_framework(9, 7, seed=seed)
    query = sorted(fw.arguments)[0]
    routed = solve_dung_acceptance(
        fw, semantics=semantics, task=task, query=query, backend="sat"
    )
    native = solve_dung_acceptance(
        fw, semantics=semantics, task=task, query=query, backend="native"
    )
    assert routed.answer == native.answer


@pytest.mark.parametrize("seed", range(6))
def test_flat_se_preferred_matches_native_membership(seed):
    fw = _dense_framework(9, 7, seed=seed)
    ext = solve_dung_single_extension(
        fw, semantics="preferred", backend="sat"
    ).extension
    # A returned preferred extension must be a genuine preferred extension:
    # every argument in it is credulously preferred-accepted natively.
    for arg in ext or frozenset():
        native = solve_dung_acceptance(
            fw, semantics="preferred", task="credulous", query=arg, backend="native"
        )
        assert native.answer is True
