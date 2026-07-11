"""Executable semantic contract for bounded collective-attack SCC recursion."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from argumentation.structured.aba import aba as native_aba
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_sat import support_extensions
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from scripts.aba_scc_composition_reference import (
    CollectiveAttack,
    build_collective_framework,
    preferred_extensions,
    stable_extensions,
)


def _lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _framework(
    assumptions: Iterable[Literal],
    contrary: Mapping[Literal, Literal],
    rules: Iterable[Rule],
    extra_language: Iterable[Literal] = (),
) -> ABAFramework:
    rule_set = frozenset(rules)
    assumption_set = frozenset(assumptions)
    language = (
        assumption_set
        | frozenset(contrary.values())
        | frozenset(extra_language)
        | frozenset(rule.consequent for rule in rule_set)
        | frozenset(body for rule in rule_set for body in rule.antecedents)
    )
    return ABAFramework(
        language=language,
        rules=rule_set,
        assumptions=assumption_set,
        contrary=dict(contrary),
    )


def _assert_oracle_equality(framework: ABAFramework) -> None:
    stable = stable_extensions(framework)
    preferred = preferred_extensions(framework)
    assert set(stable.extensions) == set(native_aba.stable_extensions(framework))
    assert set(stable.extensions) == set(support_extensions(framework, "stable"))
    assert set(preferred.extensions) == set(native_aba.preferred_extensions(framework))
    assert set(preferred.extensions) == set(support_extensions(framework, "preferred"))


def _fixtures() -> dict[str, ABAFramework]:
    a, b, c = (_lit(name) for name in ("a", "b", "c"))
    ca, cb, cc = (_lit(name) for name in ("ca", "cb", "cc"))
    x, y, z = (_lit(name) for name in ("x", "y", "z"))
    return {
        "multi_body_cross_scc": _framework(
            {a, b, c},
            {a: ca, b: cb, c: cc},
            {Rule((a, b), cc, "strict")},
        ),
        "empty_factual": _framework(
            {a, b},
            {a: ca, b: cb},
            {Rule((), ca, "strict")},
        ),
        "derived_chain": _framework(
            {a, b},
            {a: ca, b: cb},
            {
                Rule((a,), x, "strict"),
                Rule((x,), y, "strict"),
                Rule((y,), cb, "strict"),
            },
            {x, y},
        ),
        "unseeded_cycle": _framework(
            {a, b},
            {a: ca, b: cb},
            {
                Rule((x,), y, "strict"),
                Rule((y,), x, "strict"),
                Rule((x,), cb, "strict"),
            },
            {x, y},
        ),
        "self_attack_no_stable": _framework(
            {a},
            {a: ca},
            {Rule((a,), ca, "strict")},
        ),
        "incomparable_preferred": _framework(
            {a, b},
            {a: ca, b: cb},
            {Rule((a,), cb, "strict"), Rule((b,), ca, "strict")},
        ),
        "no_stable_with_preferred": _framework(
            {a, b},
            {a: ca, b: cb},
            {Rule((a,), ca, "strict")},
        ),
        "shared_assumption_valued_contrary": _framework(
            {a, b, c},
            {a: c, b: c, c: cc},
            {Rule((a,), cc, "strict"), Rule((c,), ca, "strict")},
            {ca},
        ),
    }


@pytest.mark.parametrize("framework", _fixtures().values(), ids=_fixtures().keys())
def test_named_semantic_fixtures_match_both_oracles(framework: ABAFramework) -> None:
    _assert_oracle_equality(framework)


def test_contract_exercises_collective_cross_scc_conditioning() -> None:
    framework = _fixtures()["multi_body_cross_scc"]
    collective = build_collective_framework(framework)
    stable = stable_extensions(framework)
    preferred = preferred_extensions(framework)

    assert len(collective.components) == 3
    assert (
        CollectiveAttack(frozenset({_lit("a"), _lit("b")}), _lit("c"))
        in collective.attacks
    )
    assert stable.extensions == (frozenset({_lit("a"), _lit("b")}),)
    assert preferred.extensions == stable.extensions
    assert stable.trace.cross_scc_collective_tails >= 1
    assert stable.trace.partially_activated_tails >= 1


def test_factual_normalization_and_stable_branch_annihilation_are_observed() -> None:
    factual = stable_extensions(_fixtures()["empty_factual"])
    no_stable = stable_extensions(_fixtures()["self_attack_no_stable"])

    assert factual.trace.normalized_fact_attacked >= 1
    assert no_stable.extensions == ()
    assert no_stable.trace.annihilated_stable_branches >= 1


def test_preferred_state_records_defeated_tails_and_mitigation() -> None:
    a, b, c = (_lit(name) for name in ("a", "b", "c"))
    ca, cb, cc = (_lit(name) for name in ("ca", "cb", "cc"))
    framework = _framework(
        {a, b, c},
        {a: ca, b: cb, c: cc},
        {
            Rule((a,), ca, "strict"),
            Rule((a, b), cc, "strict"),
            Rule((c,), cb, "strict"),
        },
    )

    result = preferred_extensions(framework)

    assert result.extensions == (frozenset({c}),)
    assert result.trace.nonempty_candidate_states >= 1
    assert result.trace.mitigated_attacks >= 1
    assert result.trace.maximum_boundary_items <= result.trace.boundary_item_cap

    x = _lit("x")
    cx = _lit("cx")
    defeated_tail = _framework(
        {x, a, b, c},
        {x: cx, a: ca, b: cb, c: cc},
        {Rule((x,), ca, "strict"), Rule((a, b), cc, "strict")},
    )
    defeated_result = preferred_extensions(defeated_tail)
    _assert_oracle_equality(defeated_tail)
    assert defeated_result.trace.defeated_collective_tails >= 1


def test_derived_mutual_attack_is_one_support_primal_scc() -> None:
    a, b = (_lit(name) for name in ("a", "b"))
    ca, cb, x, y = (_lit(name) for name in ("ca", "cb", "x", "y"))
    framework = _framework(
        {a, b},
        {a: ca, b: cb},
        {
            Rule((a,), x, "strict"),
            Rule((x,), cb, "strict"),
            Rule((b,), y, "strict"),
            Rule((y,), ca, "strict"),
        },
        {x, y},
    )

    assert build_collective_framework(framework).components == (frozenset({a, b}),)
    _assert_oracle_equality(framework)


@st.composite
def _bounded_flat_frameworks(draw: st.DrawFn) -> ABAFramework:
    assumption_count = draw(st.integers(min_value=0, max_value=5))
    assumptions = tuple(_lit(f"a{index}") for index in range(assumption_count))
    derived = tuple(_lit(f"d{index}") for index in range(4))
    ordinary_contraries = tuple(_lit(f"c{index}") for index in range(assumption_count))
    contrary_pool = (*ordinary_contraries, *assumptions)
    contrary = (
        {assumption: draw(st.sampled_from(contrary_pool)) for assumption in assumptions}
        if assumptions
        else {}
    )
    non_assumption_heads = tuple(dict.fromkeys((*ordinary_contraries, *derived)))
    body_pool = (*assumptions, *derived)
    rule_count = draw(st.integers(min_value=0, max_value=8))
    rules: set[Rule] = set()
    if non_assumption_heads:
        for rule_index in range(rule_count):
            body = draw(
                st.lists(
                    st.sampled_from(body_pool),
                    min_size=0,
                    max_size=min(3, len(body_pool)),
                    unique=True,
                )
            )
            head = draw(st.sampled_from(non_assumption_heads))
            rules.add(Rule(tuple(body), head, "strict", f"r{rule_index}"))
    return _framework(assumptions, contrary, rules, derived)


@given(_bounded_flat_frameworks())
@settings(max_examples=100, deadline=None)
def test_bounded_stable_family_is_exact(framework: ABAFramework) -> None:
    result = stable_extensions(framework)
    assert set(result.extensions) == set(native_aba.stable_extensions(framework))
    assert set(result.extensions) == set(support_extensions(framework, "stable"))


@given(_bounded_flat_frameworks())
@settings(max_examples=100, deadline=None)
def test_bounded_preferred_family_is_exact(framework: ABAFramework) -> None:
    result = preferred_extensions(framework)
    assert set(result.extensions) == set(native_aba.preferred_extensions(framework))
    assert set(result.extensions) == set(support_extensions(framework, "preferred"))
