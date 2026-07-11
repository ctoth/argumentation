"""Frozen Probe 8 Gate A contract for multiplicity-aware ABA true clones."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json

from hypothesis import Phase, given, seed, settings
from hypothesis import strategies as st
import pytest

from argumentation.structured.aba import aba as native_aba
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_sat import support_extensions
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule
from scripts.aba_true_clone_quotient_reference import (
    ContractBoundsExceeded,
    QuotientState,
    canonical_witness,
    certify_true_clone_classes,
    evaluate_preferred_quotient,
    expand_state,
    normalize_framework,
    process_memory_limit,
)


FIXED_SEED = 2026071108
FROZEN_FIXTURE_NAMES = (
    "true_clone_size2_complete_family",
    "true_clone_size3_complete_family",
    "true_clone_size3_partial_k1",
    "true_clone_size3_partial_k2",
    "conjunctive_support_true_clones",
    "factual_attacker_true_clones",
    "mutual_and_self_attack_true_clones",
    "no_stable_but_preferred_true_clones",
    "near_clone_distinct_contrary_rejected",
    "near_clone_rule_signature_rejected",
    "entangled_ab_attacker_matching_rejected",
    "multi_class_orbit_expansion_no_loss_or_duplicate",
)


@pytest.fixture(scope="module", autouse=True)
def _hard_process_memory_cap() -> Iterable[None]:
    with process_memory_limit(512 * 1024 * 1024):
        yield


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


@dataclass(frozen=True)
class FrozenFixture:
    framework: ABAFramework
    expected_classes: frozenset[frozenset[str]] = frozenset()
    rejected_pairs: frozenset[frozenset[str]] = frozenset()
    explicit_orbits: tuple[tuple[frozenset[str], int, int], ...] = ()
    has_no_stable_extension: bool = False


def _fixtures() -> dict[str, FrozenFixture]:
    fixtures: dict[str, FrozenFixture] = {}

    a, b, c = (_lit(name) for name in ("s2_a", "s2_b", "s2_c"))
    fixtures["true_clone_size2_complete_family"] = FrozenFixture(
        _framework({a, b}, {a: c, b: c}),
        frozenset({frozenset({"s2_a", "s2_b"})}),
    )

    a, b, c, bar = (_lit(name) for name in ("s3_a", "s3_b", "s3_c", "s3_bar"))
    fixtures["true_clone_size3_complete_family"] = FrozenFixture(
        _framework({a, b, c}, {a: bar, b: bar, c: bar}),
        frozenset({frozenset({"s3_a", "s3_b", "s3_c"})}),
    )

    a, b, c, bar = (_lit(name) for name in ("k1_a", "k1_b", "k1_c", "k1_bar"))
    fixtures["true_clone_size3_partial_k1"] = FrozenFixture(
        _framework(
            {a, b, c},
            {a: bar, b: bar, c: bar},
            {Rule((a, b, c), bar, "strict", "k1_all")},
        ),
        frozenset({frozenset({"k1_a", "k1_b", "k1_c"})}),
        explicit_orbits=((frozenset({"k1_a", "k1_b", "k1_c"}), 1, 3),),
    )

    a, b, c, bar = (_lit(name) for name in ("k2_a", "k2_b", "k2_c", "k2_bar"))
    fixtures["true_clone_size3_partial_k2"] = FrozenFixture(
        _framework(
            {a, b, c},
            {a: bar, b: bar, c: bar},
            {Rule((a, b, c), bar, "strict", "k2_all")},
        ),
        frozenset({frozenset({"k2_a", "k2_b", "k2_c"})}),
        explicit_orbits=((frozenset({"k2_a", "k2_b", "k2_c"}), 2, 3),),
    )

    a, b, x, bar, bar_x = (
        _lit(name) for name in ("conj_a", "conj_b", "conj_x", "conj_bar", "conj_bar_x")
    )
    fixtures["conjunctive_support_true_clones"] = FrozenFixture(
        _framework(
            {a, b, x},
            {a: bar, b: bar, x: bar_x},
            {Rule((a, b, x), bar, "strict", "conj")},
        ),
        frozenset({frozenset({"conj_a", "conj_b"})}),
    )

    a, b, bar = (_lit(name) for name in ("fact_a", "fact_b", "fact_bar"))
    fixtures["factual_attacker_true_clones"] = FrozenFixture(
        _framework(
            {a, b},
            {a: bar, b: bar},
            {
                Rule((), bar, "strict", "fact"),
                Rule((), bar, "strict", "fact-duplicate"),
            },
        ),
        frozenset({frozenset({"fact_a", "fact_b"})}),
    )

    ma, mb, sa, sb = (_lit(name) for name in ("mut_a", "mut_b", "self_a", "self_b"))
    fixtures["mutual_and_self_attack_true_clones"] = FrozenFixture(
        _framework(
            {ma, mb, sa, sb},
            {ma: mb, mb: ma, sa: sa, sb: sb},
        ),
        frozenset(
            {
                frozenset({"mut_a", "mut_b"}),
                frozenset({"self_a", "self_b"}),
            }
        ),
        explicit_orbits=((frozenset({"mut_a", "mut_b"}), 1, 2),),
    )

    a, b, bar, x, y, z = (
        _lit(name)
        for name in ("nost_a", "nost_b", "nost_bar", "nost_x", "nost_y", "nost_z")
    )
    fixtures["no_stable_but_preferred_true_clones"] = FrozenFixture(
        _framework(
            {a, b, x, y, z},
            {a: bar, b: bar, x: z, y: x, z: y},
        ),
        frozenset({frozenset({"nost_a", "nost_b"})}),
        has_no_stable_extension=True,
    )

    a, b, ca, cb = (_lit(name) for name in ("nc_a", "nc_b", "nc_ca", "nc_cb"))
    fixtures["near_clone_distinct_contrary_rejected"] = FrozenFixture(
        _framework({a, b}, {a: ca, b: cb}),
        rejected_pairs=frozenset({frozenset({"nc_a", "nc_b"})}),
    )

    ha, hb, ba, bb, fa, fb, shared = (
        _lit(name)
        for name in (
            "head_a",
            "head_b",
            "body_a",
            "body_b",
            "fact_a2",
            "fact_b2",
            "near_bar",
        )
    )
    p, q, r, u, v, outside = (
        _lit(name)
        for name in ("near_p", "near_q", "near_r", "near_u", "near_v", "near_out")
    )
    fixtures["near_clone_rule_signature_rejected"] = FrozenFixture(
        _framework(
            {ha, hb, ba, bb, fa, fb, outside},
            {
                ha: shared,
                hb: shared,
                ba: shared,
                bb: shared,
                fa: shared,
                fb: shared,
                outside: v,
            },
            {
                Rule((ha,), p, "strict", "head-left"),
                Rule((hb,), q, "strict", "head-right"),
                Rule((ba, outside), r, "strict", "body-left"),
                Rule((bb,), r, "strict", "body-right"),
                Rule((fa,), u, "strict", "fact-left"),
                Rule((fb,), u, "strict", "fact-right"),
                Rule((), u, "strict", "fact-only"),
            },
            {p, q, r, u, v},
        ),
        rejected_pairs=frozenset(
            {
                frozenset({"head_a", "head_b"}),
                frozenset({"body_a", "body_b"}),
                frozenset({"fact_a2", "fact_b2"}),
            }
        ),
    )

    a1, a2, b1, b2, ca1, ca2, cb1, cb2 = (
        _lit(name)
        for name in (
            "ent_a1",
            "ent_a2",
            "ent_b1",
            "ent_b2",
            "ent_ca1",
            "ent_ca2",
            "ent_cb1",
            "ent_cb2",
        )
    )
    fixtures["entangled_ab_attacker_matching_rejected"] = FrozenFixture(
        _framework(
            {a1, a2, b1, b2},
            {a1: ca1, a2: ca2, b1: cb1, b2: cb2},
            {
                Rule((b1,), ca1, "strict", "ent-a1"),
                Rule((b2,), ca2, "strict", "ent-a2"),
                Rule((a1,), cb1, "strict", "ent-b1"),
                Rule((a2,), cb2, "strict", "ent-b2"),
            },
        ),
        rejected_pairs=frozenset(
            {
                frozenset({"ent_a1", "ent_a2"}),
                frozenset({"ent_b1", "ent_b2"}),
            }
        ),
    )

    a, b, x, y, z, ca, cx = (
        _lit(name)
        for name in (
            "multi_a",
            "multi_b",
            "multi_x",
            "multi_y",
            "multi_z",
            "multi_ca",
            "multi_cx",
        )
    )
    fixtures["multi_class_orbit_expansion_no_loss_or_duplicate"] = FrozenFixture(
        _framework(
            {a, b, x, y, z},
            {a: ca, b: ca, x: cx, y: cx, z: cx},
            {Rule((x, y, z), cx, "strict", "multi-all")},
        ),
        frozenset(
            {
                frozenset({"multi_a", "multi_b"}),
                frozenset({"multi_x", "multi_y", "multi_z"}),
            }
        ),
        explicit_orbits=((frozenset({"multi_x", "multi_y", "multi_z"}), 2, 3),),
    )
    assert tuple(fixtures) == FROZEN_FIXTURE_NAMES
    return fixtures


def _names(items: frozenset[Literal]) -> frozenset[str]:
    return frozenset(item.atom.predicate for item in items)


def _class_names(framework: ABAFramework) -> frozenset[frozenset[str]]:
    normalized = normalize_framework(framework)
    return frozenset(
        frozenset(
            normalized.literal_for(member).atom.predicate
            for member in certificate.members
        )
        for certificate in certify_true_clone_classes(normalized.serialized)
    )


def _assert_complete_family(framework: ABAFramework) -> None:
    result = evaluate_preferred_quotient(framework)
    native = frozenset(native_aba.preferred_extensions(framework))
    support = frozenset(support_extensions(framework, "preferred"))
    assert result.lifted_preferred_family == native
    assert result.lifted_preferred_family == support
    assert canonical_witness(result.lifted_preferred_family) == min(
        result.lifted_preferred_family,
        key=lambda extension: tuple(sorted(map(repr, extension))),
    )


@pytest.mark.parametrize(
    ("name", "fixture"),
    _fixtures().items(),
    ids=FROZEN_FIXTURE_NAMES,
)
def test_twelve_frozen_named_fixtures(name: str, fixture: FrozenFixture) -> None:
    classes = _class_names(fixture.framework)
    assert fixture.expected_classes <= classes
    assert all(pair not in classes for pair in fixture.rejected_pairs)
    _assert_complete_family(fixture.framework)
    if fixture.has_no_stable_extension:
        assert native_aba.stable_extensions(fixture.framework) == ()
    if name == "factual_attacker_true_clones":
        document = json.loads(normalize_framework(fixture.framework).serialized)
        assert sum(row[0] == "factual" for row in document["incidences"]) == 2
        assert sum(row[1].startswith("rule:") for row in document["nodes"]) == 2

    normalized = normalize_framework(fixture.framework)
    certificates = certify_true_clone_classes(normalized.serialized)
    by_names = {
        frozenset(
            normalized.literal_for(member).atom.predicate for member in item.members
        ): item
        for item in certificates
    }
    for class_names, multiplicity, expected_size in fixture.explicit_orbits:
        certificate = by_names[class_names]
        state = QuotientState(
            multiplicities=(multiplicity,),
            selected_singletons=frozenset(),
        )
        orbit = expand_state((certificate,), state, normalized)
        assert len(orbit) == expected_size
        assert all(len(extension) == multiplicity for extension in orbit)


def test_reference_bounds_fail_closed_before_exhaustive_reasoning() -> None:
    assumptions = tuple(_lit(f"bound_a{index}") for index in range(9))
    contrary = {
        assumption: _lit(f"bound_c{index}")
        for index, assumption in enumerate(assumptions)
    }
    with pytest.raises(ContractBoundsExceeded, match="assumptions"):
        evaluate_preferred_quotient(_framework(assumptions, contrary))

    a, ca = _lit("bound_rule_a"), _lit("bound_rule_ca")
    rules = {
        Rule((), _lit(f"bound_head{index}"), "strict", f"bound-rule-{index}")
        for index in range(17)
    }
    with pytest.raises(ContractBoundsExceeded, match="rules"):
        evaluate_preferred_quotient(_framework({a}, {a: ca}, rules))


@st.composite
def _bounded_frameworks(draw: st.DrawFn) -> ABAFramework:
    assumption_count = draw(st.integers(min_value=0, max_value=6))
    assumptions = tuple(_lit(f"gen_a{index}") for index in range(assumption_count))
    non_assumptions = tuple(_lit(f"gen_n{index}") for index in range(4))
    contrary_pool = (*assumptions, *non_assumptions)
    contrary = {
        assumption: draw(st.sampled_from(contrary_pool)) for assumption in assumptions
    }
    rule_count = draw(st.integers(min_value=0, max_value=10))
    rules: set[Rule] = set()
    all_literals = (*assumptions, *non_assumptions)
    for index in range(rule_count):
        body = draw(
            st.lists(
                st.sampled_from(all_literals),
                min_size=0,
                max_size=min(3, len(all_literals)),
                unique=True,
            )
        )
        head = draw(st.sampled_from(non_assumptions))
        rules.add(Rule(tuple(body), head, "strict", f"generated-{index}"))
    return _framework(assumptions, contrary, rules, non_assumptions)


_GENERATED_DIAGNOSTICS: list[dict[str, object]] = []


@seed(FIXED_SEED)
@given(_bounded_frameworks())
@settings(max_examples=300, deadline=None, database=None, phases=(Phase.generate,))
def test_exactly_300_fixed_seed_bounded_frameworks(framework: ABAFramework) -> None:
    result = evaluate_preferred_quotient(framework)
    native = frozenset(native_aba.preferred_extensions(framework))
    support = frozenset(support_extensions(framework, "preferred"))
    assert result.lifted_preferred_family == native
    assert result.lifted_preferred_family == support
    diagnostic: dict[str, object] = {
        "seed": FIXED_SEED,
        "framework_index": len(_GENERATED_DIAGNOSTICS),
        "normalized_framework_sha256": result.normalized_sha256,
        "assumptions": len(framework.assumptions),
        "rules": len(framework.rules),
        "certified_classes": [
            [
                result.normalized.literal_for(member).atom.predicate
                for member in item.members
            ]
            for item in result.classes
        ],
        "reference_family_size": len(result.lifted_preferred_family),
        "native_family_size": len(native),
        "support_family_size": len(support),
    }
    _GENERATED_DIAGNOSTICS.append(diagnostic)
    print(json.dumps(diagnostic, sort_keys=True))


def test_generated_population_count_and_nonvacuous_coverage() -> None:
    assert len(_GENERATED_DIAGNOSTICS) == 300
    assert [item["framework_index"] for item in _GENERATED_DIAGNOSTICS] == list(
        range(300)
    )

    fixtures = _fixtures()
    certified_sizes = {
        len(class_names)
        for fixture in fixtures.values()
        for class_names in _class_names(fixture.framework)
    }
    assert {2, 3} <= certified_sizes
    partial_orbits = [
        orbit
        for fixture in fixtures.values()
        for orbit in fixture.explicit_orbits
        if 0 < orbit[1] < len(orbit[0])
    ]
    assert partial_orbits
