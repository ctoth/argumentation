"""Oracle-equivalence tests for the Wave A AF preprocessing layer.

The preprocessing layer (:mod:`argumentation.core.preprocessing`) must be exactly
semantics-preserving: solving the reduced AF and lifting the answer back must
equal solving the original AF, for every supported semantics. These tests pin
that against the brute-force reference semantics in :mod:`argumentation.core.dung`
and against the unsimplified SAT path.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.solving.af_sat import (
    find_complete_extension,
    find_ideal_extension,
    find_preferred_extension,
    find_semi_stable_extension,
    find_stable_extension,
    find_stage_extension,
    is_preferred_skeptically_accepted,
)
from argumentation.core.dung import (
    ArgumentationFramework,
    grounded_extension,
    preferred_extensions,
    semi_stable_extensions,
    stable_extensions,
    stage_extensions,
)
from argumentation.core.dung import complete_extensions as native_complete_extensions
from argumentation.core.dung import ideal_extension as native_ideal_extension
from argumentation.core.preprocessing import (
    is_symmetric_irreflexive,
    isolated_arguments,
    simplify_af,
)
from argumentation.core.reduct import SemanticReduct

z3 = pytest.importorskip("z3")  # noqa: F841


def _af(args, defeats):
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


# A battery of small, deliberately diverse AFs.
_BATTERY: list[ArgumentationFramework] = [
    _af({"a"}, set()),  # single isolated argument
    _af({"a"}, {("a", "a")}),  # single self-attacker
    _af({"a", "b"}, {("a", "b")}),  # one-way attack: non-trivial grounded
    _af({"a", "b"}, {("a", "b"), ("b", "a")}),  # symmetric 2-cycle
    _af({"a", "b", "c"}, {("a", "b"), ("b", "c")}),  # acyclic chain
    _af({"a", "b", "c"}, {("a", "b"), ("b", "c"), ("c", "a")}),  # 3-cycle
    _af({"a", "b", "c", "d"}, {("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")}),  # two 2-cycles
    _af({"a", "b", "c"}, {("a", "a"), ("a", "b"), ("b", "c")}),  # self-attacker with out-edges
    _af({"a", "b", "c", "d"}, {("a", "a"), ("b", "b")}),  # only self-loop sinks (+ isolated)
    _af({"a", "b", "c"}, {("a", "a"), ("b", "c"), ("c", "a")}),  # stage breaks naive grounded reduct
    _af(
        {"a", "b", "c", "d", "e"},
        {("a", "b"), ("b", "c"), ("c", "b"), ("d", "e"), ("e", "d")},
    ),  # grounded {a}, then a 2-cycle and another 2-cycle
    _af(
        {"a", "b", "c", "d"},
        {("a", "c"), ("b", "a"), ("c", "b"), ("a", "d")},
    ),  # 3-cycle plus a dominated leaf
]


@st.composite
def _random_af(draw, max_args: int = 4):
    args = draw(
        st.frozensets(
            st.text(alphabet="abcd", min_size=1, max_size=2),
            min_size=1,
            max_size=max_args,
        )
    )
    arg_list = sorted(args)
    defeats = draw(
        st.frozensets(
            st.tuples(st.sampled_from(arg_list), st.sampled_from(arg_list)),
            max_size=len(arg_list) ** 2,
        )
    )
    return ArgumentationFramework(arguments=args, defeats=defeats)


# ── Direct invariants of simplify_af ────────────────────────────────


def _check_simplification_shape(
    framework: ArgumentationFramework,
    simplification: SemanticReduct[ArgumentationFramework, str],
) -> None:
    assert simplification.original is framework
    assert simplification.fixed_in <= framework.arguments
    assert simplification.fixed_out <= framework.arguments
    assert simplification.fixed_in.isdisjoint(simplification.fixed_out)
    removed = simplification.fixed_in | simplification.fixed_out
    assert simplification.residual.arguments == framework.arguments - removed
    # Residual carries exactly the attacks among its surviving arguments.
    for attacker, target in framework.defeats:
        if attacker in simplification.residual.arguments and target in simplification.residual.arguments:
            assert (attacker, target) in simplification.residual.defeats
    for attacker, target in simplification.residual.defeats:
        assert (attacker, target) in framework.defeats


@pytest.mark.parametrize("framework", _BATTERY)
def test_simplify_af_shape_on_battery(framework: ArgumentationFramework) -> None:
    for semantics in ("complete", "preferred", "stable", "semi_stable", "stage", "grounded", "ideal", None):
        simplification = simplify_af(framework, semantics=semantics)
        _check_simplification_shape(framework, simplification)


@given(_random_af(max_args=5))
@settings(deadline=None, max_examples=80)
def test_simplify_af_shape_random(framework: ArgumentationFramework) -> None:
    for semantics in ("complete", "preferred", "stable", "semi_stable", "stage", "grounded", "ideal"):
        _check_simplification_shape(framework, simplify_af(framework, semantics=semantics))


def test_grounded_reduct_fixes_grounded_in_and_attacked_out() -> None:
    framework = _af({"a", "b", "c"}, {("a", "b"), ("b", "c")})
    simplification = simplify_af(framework, semantics="complete")
    assert simplification.fixed_in == frozenset({"a", "c"})
    assert simplification.fixed_out == frozenset({"b"})
    assert not simplification.residual.arguments


def test_self_loop_sink_removed_except_for_stable() -> None:
    framework = _af({"a", "b"}, {("a", "a")})
    # b is unattacked -> grounded; a is a pure self-loop sink.
    non_stable = simplify_af(framework, semantics="complete")
    assert "a" in non_stable.fixed_out
    stable_view = simplify_af(framework, semantics="stable")
    assert "a" not in stable_view.fixed_out
    assert "a" in stable_view.residual.arguments


def test_diagnostics() -> None:
    framework = _af({"a", "b", "c"}, {("a", "b"), ("b", "a")})
    assert isolated_arguments(framework) == frozenset({"c"})
    assert is_symmetric_irreflexive(_af({"a", "b"}, {("a", "b"), ("b", "a")}))
    assert not is_symmetric_irreflexive(_af({"a"}, {("a", "a")}))
    assert not is_symmetric_irreflexive(_af({"a", "b"}, {("a", "b")}))
    assert not is_symmetric_irreflexive(_af({"a"}, set()))


# ── Oracle equivalence: simplified SAT path == brute-force reference ─


def _native_extensions(framework: ArgumentationFramework, semantics: str) -> set[frozenset[str]]:
    if semantics == "complete":
        return set(native_complete_extensions(framework))
    if semantics == "preferred":
        return set(preferred_extensions(framework))
    if semantics == "stable":
        return set(stable_extensions(framework))
    if semantics == "semi_stable":
        return set(semi_stable_extensions(framework))
    if semantics == "stage":
        return set(stage_extensions(framework))
    if semantics == "grounded":
        return {grounded_extension(framework)}
    if semantics == "ideal":
        return {native_ideal_extension(framework)}
    raise AssertionError(semantics)


_FINDERS = {
    "complete": find_complete_extension,
    "preferred": find_preferred_extension,
    "stable": find_stable_extension,
    "semi_stable": find_semi_stable_extension,
    "stage": find_stage_extension,
}


def _assert_finder_matches_oracle(framework: ArgumentationFramework, semantics: str) -> None:
    finder = _FINDERS[semantics]
    native = _native_extensions(framework, semantics)
    with_simplify = finder(framework, simplify=True)
    without_simplify = finder(framework, simplify=False)
    # Existence agrees with the oracle and with the unsimplified path.
    assert (with_simplify is None) == (not native)
    assert (without_simplify is None) == (not native)
    if native:
        assert with_simplify in native
        assert without_simplify in native
    # require_in / require_out: existence agrees with the oracle, witness valid.
    for query in sorted(framework.arguments):
        with_query = {extension for extension in native if query in extension}
        wit_in = finder(framework, require_in=query, simplify=True)
        assert (wit_in is None) == (not with_query)
        if with_query:
            assert wit_in in with_query
        without_query = {extension for extension in native if query not in extension}
        wit_out = finder(framework, require_out=query, simplify=True)
        assert (wit_out is None) == (not without_query)
        if without_query:
            assert wit_out in without_query


@pytest.mark.parametrize("framework", _BATTERY)
@pytest.mark.parametrize("semantics", sorted(_FINDERS))
def test_finder_matches_oracle_on_battery(framework: ArgumentationFramework, semantics: str) -> None:
    _assert_finder_matches_oracle(framework, semantics)


@given(_random_af(max_args=4))
@settings(deadline=None, max_examples=120)
def test_finder_matches_oracle_random(framework: ArgumentationFramework) -> None:
    for semantics in _FINDERS:
        _assert_finder_matches_oracle(framework, semantics)


@pytest.mark.parametrize("framework", _BATTERY)
def test_ideal_matches_oracle_on_battery(framework: ArgumentationFramework) -> None:
    expected = native_ideal_extension(framework)
    assert find_ideal_extension(framework, simplify=True) == expected
    assert find_ideal_extension(framework, simplify=False) == expected


@given(_random_af(max_args=4))
@settings(deadline=None, max_examples=120)
def test_ideal_matches_oracle_random(framework: ArgumentationFramework) -> None:
    expected = native_ideal_extension(framework)
    assert find_ideal_extension(framework, simplify=True) == expected


def _native_skeptical_preferred(framework: ArgumentationFramework, query: str) -> bool:
    extensions = preferred_extensions(framework)
    if not extensions:
        return True  # vacuously skeptically accepted (no preferred extension)
    return all(query in extension for extension in extensions)


@pytest.mark.parametrize("framework", _BATTERY)
def test_skeptical_preferred_matches_oracle_on_battery(framework: ArgumentationFramework) -> None:
    for query in sorted(framework.arguments):
        expected = _native_skeptical_preferred(framework, query)
        assert is_preferred_skeptically_accepted(framework, query, simplify=True) == expected
        assert is_preferred_skeptically_accepted(framework, query, simplify=False) == expected


@given(_random_af(max_args=4))
@settings(deadline=None, max_examples=120)
def test_skeptical_preferred_matches_oracle_random(framework: ArgumentationFramework) -> None:
    for query in sorted(framework.arguments):
        expected = _native_skeptical_preferred(framework, query)
        assert is_preferred_skeptically_accepted(framework, query, simplify=True) == expected
