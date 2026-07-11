"""Frozen probe-6 semantic contract for bounded ABA cutset composition."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import combinations

from hypothesis import given, seed, settings
from hypothesis import strategies as st
import pytest

from argumentation.structured.aba import aba as native_aba
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_sat import support_extensions
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from scripts.aba_backdoor_cutset_reference import (
    AmbiguousAttackOwnership,
    CollectiveAttack,
    ContractBoundsExceeded,
    MissingPathCoverage,
    NonSeparatorError,
    OracleDisagreement,
    PathCounters,
    assert_support_oracle_admissible,
    compose_for_cutset,
    exhaustive_admissible,
    qualifying_cutsets,
    require_path_coverage,
)


def _lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _framework(
    assumptions: Iterable[Literal],
    contrary: Mapping[Literal, Literal],
    rules: Iterable[Rule] = (),
    extra_language: Iterable[Literal] = (),
) -> ABAFramework:
    assumption_set = frozenset(assumptions)
    rule_set = frozenset(rules)
    language = (
        assumption_set
        | frozenset(contrary.values())
        | frozenset(extra_language)
        | frozenset(rule.consequent for rule in rule_set)
        | frozenset(item for rule in rule_set for item in rule.antecedents)
    )
    return ABAFramework(
        language=language,
        rules=rule_set,
        assumptions=assumption_set,
        contrary=dict(contrary),
    )


def _fixtures() -> dict[str, tuple[ABAFramework, frozenset[Literal]]]:
    a, b, c, d, k = (_lit(name) for name in ("a", "b", "c", "d", "k"))
    ca, cb, cc, cd, ck = (_lit(name) for name in ("ca", "cb", "cc", "cd", "ck"))
    p, z = (_lit(name) for name in ("p", "z"))
    return {
        "empty_framework": (_framework((), {}), frozenset()),
        "fact_derived_cut_target": (
            _framework(
                {a, b, k},
                {a: ca, b: cb, k: ck},
                {Rule((), p, "strict"), Rule((p,), ck, "strict")},
                {p},
            ),
            frozenset(),
        ),
        "selected_cut_collective_activation": (
            _framework(
                {a, b, c, k},
                {a: ca, b: cb, c: cc, k: ck},
                {Rule((k, a), cb, "strict")},
            ),
            frozenset({k}),
        ),
        "cut_attack_conflict": (
            _framework(
                {a, b, k},
                {a: ca, b: cb, k: ck},
                {Rule((a,), ck, "strict")},
            ),
            frozenset({k}),
        ),
        "cut_defense_obligation": (
            _framework(
                {a, b, c, k},
                {a: ca, b: cb, c: cc, k: ck},
                {Rule((a,), ck, "strict"), Rule((b,), ca, "strict")},
            ),
            frozenset({k}),
        ),
        # This is the literal frozen fixture.  Both rule factors share ck, so
        # deleting k leaves a and b in one assumption-bearing component.
        "two_component_cut_attack_union": (
            _framework(
                {a, b, k},
                {a: ca, b: cb, k: ck},
                {Rule((a,), ck, "strict"), Rule((b,), ck, "strict")},
            ),
            frozenset({k}),
        ),
        "self_and_assumption_contrary": (
            _framework({a, b}, {a: a, b: cb}),
            frozenset(),
        ),
        "shared_contrary_targets": (
            _framework(
                {a, b, c, d, k},
                {a: z, b: z, c: cc, d: cd, k: ck},
                {Rule((k, c), z, "strict")},
                {z},
            ),
            frozenset({k}),
        ),
        "global_maximality_across_states": (
            _framework(
                {a, b, c, k},
                {a: ca, b: cb, c: cc, k: ck},
                {Rule((a,), cb, "strict"), Rule((b,), ca, "strict")},
            ),
            frozenset({k}),
        ),
        "already_independent_k_empty": (
            _framework(
                {a, b, c, d},
                {a: ca, b: cb, c: cc, d: cd},
                {Rule((a,), cb, "strict"), Rule((c,), cd, "strict")},
            ),
            frozenset(),
        ),
    }


def _assert_exact(framework: ABAFramework, cutset: frozenset[Literal]) -> None:
    result = compose_for_cutset(framework, cutset)
    reference_admissible = exhaustive_admissible(framework)
    direct_admissible = frozenset(
        candidate
        for candidate in _subsets(framework.assumptions)
        if native_aba.admissible(framework, candidate)
    )
    assert result.admissible_lifts == reference_admissible
    assert result.admissible_lifts == direct_admissible
    assert_support_oracle_admissible(framework, result.admissible_lifts)
    direct_preferred = frozenset(native_aba.preferred_extensions(framework))
    support_preferred = frozenset(support_extensions(framework, "preferred"))
    assert result.preferred_extensions == direct_preferred
    assert result.preferred_extensions == support_preferred


def _subsets(items: frozenset[Literal]) -> tuple[frozenset[Literal], ...]:
    ordered = tuple(sorted(items, key=repr))
    return tuple(
        frozenset(choice)
        for size in range(len(ordered) + 1)
        for choice in combinations(ordered, size)
    )


@pytest.mark.parametrize(
    ("name", "framework", "cutset"),
    ((name, *value) for name, value in _fixtures().items()),
    ids=_fixtures().keys(),
)
def test_ten_named_fixtures(
    name: str,
    framework: ABAFramework,
    cutset: frozenset[Literal],
) -> None:
    if name == "two_component_cut_attack_union":
        with pytest.raises(NonSeparatorError, match="one assumption-bearing component"):
            compose_for_cutset(framework, cutset)
        return
    _assert_exact(framework, cutset)


def test_named_paths_are_observed() -> None:
    totals: dict[str, int] = {}
    for name, (framework, cutset) in _fixtures().items():
        if name == "two_component_cut_attack_union":
            continue
        result = compose_for_cutset(framework, cutset)
        for field, value in vars(result.paths).items():
            totals[field] = totals.get(field, 0) + value

    required = {
        "factual_normalizations",
        "selected_cut_states",
        "rejected_cut_states",
        "attacked_cut_signatures",
        "cut_defense_obligations_created",
        "cut_defense_obligations_discharged",
        "inactive_collective_tails",
        "activated_collective_tails",
        "independent_residual_components",
        "deduplication_passes",
        "incomparable_preferred_maxima",
    }
    assert {name for name in required if totals.get(name, 0) == 0} == set()


def test_adversarial_fixed_k_is_rejected_as_non_separator() -> None:
    x, u, v, c, t = (_lit(name) for name in ("x", "u", "v", "c", "t"))
    nc = _lit("nc")
    framework = _framework(
        {x, u, v, c},
        {x: u, u: v, v: x, c: nc},
        {
            Rule((u,), t, "strict"),
            Rule((v,), t, "strict"),
            Rule((x, t), nc, "strict"),
        },
        {t},
    )
    assert frozenset({x}) not in qualifying_cutsets(framework)
    with pytest.raises(NonSeparatorError, match="one assumption-bearing component"):
        compose_for_cutset(framework, frozenset({x}))


def test_bounds_and_ownership_fail_closed() -> None:
    assumptions = {_lit(f"a{index}") for index in range(6)}
    contraries = {
        assumption: _lit(f"c{index}")
        for index, assumption in enumerate(sorted(assumptions, key=repr))
    }
    with pytest.raises(ContractBoundsExceeded, match="assumptions"):
        qualifying_cutsets(_framework(assumptions, contraries))

    a, b, k = (_lit(name) for name in ("oa", "ob", "ok"))
    attack = CollectiveAttack(frozenset({a, b}), k)
    from scripts.aba_backdoor_cutset_reference import assign_attack_owner

    with pytest.raises(AmbiguousAttackOwnership, match="multiple residual components"):
        assign_attack_owner(
            attack,
            frozenset({k}),
            (frozenset({a}), frozenset({b})),
        )


def test_missing_paths_and_oracle_disagreement_fail_closed() -> None:
    with pytest.raises(MissingPathCoverage, match="unexercised path counters"):
        require_path_coverage(
            PathCounters(),
            frozenset({"factual_normalizations"}),
        )

    a, ca = (_lit(name) for name in ("oracle_a", "oracle_ca"))
    framework = _framework({a}, {a: ca})
    with pytest.raises(OracleDisagreement, match="support admissibility disagreement"):
        assert_support_oracle_admissible(framework, frozenset())


@st.composite
def _bounded_frameworks(draw: st.DrawFn) -> ABAFramework:
    assumption_count = draw(st.integers(min_value=0, max_value=5))
    assumptions = tuple(_lit(f"ga{index}") for index in range(assumption_count))
    non_assumptions = tuple(_lit(f"gn{index}") for index in range(4))
    contrary_pool = (*assumptions, *non_assumptions)
    contrary = (
        {assumption: draw(st.sampled_from(contrary_pool)) for assumption in assumptions}
        if assumptions
        else {}
    )
    rule_count = draw(st.integers(min_value=0, max_value=8))
    rules: set[Rule] = set()
    for index in range(rule_count):
        body = draw(
            st.lists(
                st.sampled_from((*assumptions, *non_assumptions)),
                min_size=0,
                max_size=3,
                unique=True,
            )
        )
        head = draw(st.sampled_from(non_assumptions))
        rules.add(Rule(tuple(body), head, "strict", f"g{index}"))
    return _framework(assumptions, contrary, rules, non_assumptions)


@seed(6006)
@given(_bounded_frameworks())
@settings(max_examples=300, deadline=None)
def test_every_bounded_qualifying_cutset_is_exact(framework: ABAFramework) -> None:
    for cutset in qualifying_cutsets(framework):
        _assert_exact(framework, cutset)
