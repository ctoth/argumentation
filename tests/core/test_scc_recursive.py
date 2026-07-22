"""Oracle-equivalence tests for the Wave B2 SCC-recursive solver.

For complete / preferred / stable: the SCC-recursive result (with preprocessing +
SCC decomposition) lifted to the full argument set MUST equal
  - the flat path (``decompose=False``), and
  - the brute-force reference in ``argumentation.core.dung``
exactly -- same set of extensions, same DC/DS answers -- on every AF.
"""

from __future__ import annotations

import random

import pytest

from argumentation.core.dung import (
    ArgumentationFramework,
    complete_extensions,
    preferred_extensions,
    stable_extensions,
)
from argumentation.core.scc_recursive import (
    LAST_SOLVE,
    scc_credulously_accepted,
    scc_extensions,
    scc_skeptically_accepted,
)

SEMANTICS = ("complete", "preferred", "stable")


def _brute(af: ArgumentationFramework, semantics: str) -> set[frozenset[str]]:
    table = {
        "complete": complete_extensions,
        "preferred": preferred_extensions,
        "stable": stable_extensions,
    }
    return set(table[semantics](af))


def _af(arguments, edges) -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset(arguments), defeats=frozenset(edges)
    )


# --------------------------------------------------------------------------- #
# Hand-built battery of multi-SCC AFs
# --------------------------------------------------------------------------- #

HAND_BUILT: list[ArgumentationFramework] = [
    # empty AF
    _af([], []),
    # single argument, no edges
    _af(["a"], []),
    # single self-loop (size-1 SCC with self-loop): CO/PR -> {emptyset}, ST -> none
    _af(["a"], [("a", "a")]),
    # single 3-cycle (one SCC)
    _af(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]),
    # long grounding chain feeding a 2-cycle
    _af(
        ["a", "b", "c", "d", "e"],
        [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "d")],
    ),
    # two 2-cycles, one feeding the other (residual has 2 SCCs)
    _af(
        ["d", "e", "f", "g"],
        [("d", "e"), ("e", "d"), ("f", "g"), ("g", "f"), ("e", "f"), ("d", "g")],
    ),
    # diamond condensation of 2-cycles: A -> {B, C} -> D
    _af(
        ["a1", "a2", "b1", "b2", "c1", "c2", "d1", "d2"],
        [
            ("a1", "a2"),
            ("a2", "a1"),
            ("b1", "b2"),
            ("b2", "b1"),
            ("c1", "c2"),
            ("c2", "c1"),
            ("d1", "d2"),
            ("d2", "d1"),
            ("a1", "b1"),
            ("a2", "c1"),
            ("b1", "d1"),
            ("c1", "d2"),
        ],
    ),
    # parallel independent SCCs: a 2-cycle and a 3-cycle, disconnected
    _af(
        ["p", "q", "r", "s", "t"],
        [("p", "q"), ("q", "p"), ("r", "s"), ("s", "t"), ("t", "r")],
    ),
    # SCC attacked by an UNDEC upstream argument (the D-set case): odd cycle x->y->z->x
    # is fully undec; it attacks a downstream 2-cycle u<->v via z->u.
    _af(
        ["x", "y", "z", "u", "v"],
        [("x", "y"), ("y", "z"), ("z", "x"), ("z", "u"), ("u", "v"), ("v", "u")],
    ),
    # self-loop inside a larger SCC: a<->b plus (a,a)
    _af(["a", "b"], [("a", "b"), ("b", "a"), ("a", "a")]),
    # mixed: chain w -> 2-cycle, plus self-loop sink k, plus isolated m
    _af(
        ["w", "c1", "c2", "k", "m"],
        [("w", "c1"), ("c1", "c2"), ("c2", "c1"), ("k", "k")],
    ),
    # size-3 SCC feeding a size-1: full triangle a<->b<->c<->a then c->d
    _af(
        ["a", "b", "c", "d"],
        [
            ("a", "b"),
            ("b", "a"),
            ("b", "c"),
            ("c", "b"),
            ("a", "c"),
            ("c", "a"),
            ("c", "d"),
        ],
    ),
]


@pytest.mark.parametrize("af", HAND_BUILT)
@pytest.mark.parametrize("semantics", SEMANTICS)
def test_hand_built_oracle_equivalence(
    af: ArgumentationFramework, semantics: str
) -> None:
    reference = _brute(af, semantics)
    decomposed = set(scc_extensions(af, semantics))
    flat = set(scc_extensions(af, semantics, decompose=False))
    assert decomposed == reference
    assert flat == reference

    # DC/DS for every argument must agree with the reference
    for argument in af.arguments:
        ref_dc = any(argument in e for e in reference)
        ref_ds = all(argument in e for e in reference)
        assert scc_credulously_accepted(af, semantics, argument) == ref_dc
        assert scc_skeptically_accepted(af, semantics, argument) == ref_ds


# --------------------------------------------------------------------------- #
# Random AF battery (>= 150 instances of varied size/density)
# --------------------------------------------------------------------------- #


def _random_afs(count: int, seed: int) -> list[ArgumentationFramework]:
    rng = random.Random(seed)
    out: list[ArgumentationFramework] = []
    for _ in range(count):
        n = rng.randint(0, 8)
        args = [f"a{i}" for i in range(n)]
        density = rng.choice([0.1, 0.2, 0.3, 0.45])
        allow_self_loops = rng.random() < 0.3
        edges = set()
        for a in args:
            for b in args:
                if a == b and not allow_self_loops:
                    continue
                if rng.random() < density:
                    edges.add((a, b))
        out.append(_af(args, edges))
    return out


@pytest.mark.parametrize("af", _random_afs(180, seed=20260512))
@pytest.mark.parametrize("semantics", SEMANTICS)
def test_random_oracle_equivalence(af: ArgumentationFramework, semantics: str) -> None:
    reference = _brute(af, semantics)
    decomposed = set(scc_extensions(af, semantics))
    flat = set(scc_extensions(af, semantics, decompose=False))
    assert decomposed == reference
    assert flat == reference

    if af.arguments:
        argument = sorted(af.arguments)[0]
        ref_dc = any(argument in e for e in reference)
        ref_ds = all(argument in e for e in reference)
        assert scc_credulously_accepted(af, semantics, argument) == ref_dc
        assert scc_skeptically_accepted(af, semantics, argument) == ref_ds


def test_recursion_path_is_actually_exercised() -> None:
    """At least some random instances must trigger the SCC recursion (not just the
    flat fast path) -- otherwise the test battery proves nothing about the recursion."""
    recursed = 0
    for af in _random_afs(300, seed=1):
        scc_extensions(af, "complete")
        if LAST_SOLVE.flat_fast_path is False:
            recursed += 1
    assert recursed > 0


# --------------------------------------------------------------------------- #
# Fast-path behaviour for single-SCC and empty-residual inputs
# --------------------------------------------------------------------------- #


def test_single_scc_input_takes_flat_path() -> None:
    af = _af(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
    result = scc_extensions(af, "complete")
    assert LAST_SOLVE.flat_fast_path is True
    assert LAST_SOLVE.residual_scc_count == 1
    assert result == [frozenset()]


def test_empty_residual_takes_flat_path() -> None:
    # A chain with no cycles -> grounded reduct empties the residual entirely.
    af = _af(["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "d")])
    result = scc_extensions(af, "complete")
    assert LAST_SOLVE.flat_fast_path is True
    assert LAST_SOLVE.residual_size == 0
    # grounded {a, c}, so the unique complete extension is {a, c}
    assert result == [frozenset({"a", "c"})]


def test_empty_af_takes_flat_path_and_returns_empty_extension() -> None:
    af = _af([], [])
    for semantics in SEMANTICS:
        result = scc_extensions(af, semantics)
        assert LAST_SOLVE.flat_fast_path is True
        assert result == [frozenset()]


def test_decompose_false_opt_out_matches_flat() -> None:
    af = _af(
        ["d", "e", "f", "g"],
        [("d", "e"), ("e", "d"), ("f", "g"), ("g", "f"), ("e", "f")],
    )
    for semantics in SEMANTICS:
        opted_out = set(scc_extensions(af, semantics, decompose=False))
        assert LAST_SOLVE.flat_fast_path is True
        assert opted_out == _brute(af, semantics)


def test_rejects_non_scc_recursive_semantics() -> None:
    af = _af(["a"], [])
    for semantics in ("semi-stable", "stage", "grounded", "ideal", "admissible"):
        with pytest.raises(ValueError):
            scc_extensions(af, semantics)
