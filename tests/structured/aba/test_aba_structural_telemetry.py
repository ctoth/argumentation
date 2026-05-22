from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


# Paper anchors reread before authoring:
# - Cerutti 2013 page 008 and Cerutti 2015 page 002: complete-labelling SAT
#   search iterates over structural variables, not benchmark path labels.
# - Dvorak 2014 pages 006-007: complexity-sensitive procedures need operational
#   structure signals before choosing a search route.
# - de Kleer 1986 pages 001-002: cached assumption contexts should be explicit
#   structural data, not hidden special-case labels.
# - Popescu 2023 pages 002-003: ABA closure, attack, and graph structure are the
#   right basis for telemetry.

FORBIDDEN_IDENTITY_KEYS = {
    "abcgen",
    "archive",
    "basename",
    "filename",
    "iccma",
    "instance",
    "label",
    "parent",
    "path",
    "relative_path",
    "year",
}

REQUIRED_TELEMETRY_KEYS = {
    "atoms",
    "assumptions",
    "rules",
    "contraries",
    "is_flat",
    "rule_body_width_histogram",
    "max_rule_body_width",
    "rule_head_fanin_max",
    "body_literal_fanout_max",
    "contrary_fanin_max",
    "contrary_fanout_max",
    "assumption_to_atom_ratio",
    "rule_to_assumption_ratio",
    "rule_dependency_scc_count",
    "rule_dependency_max_scc_size",
    "assumption_dependency_scc_count",
    "assumption_dependency_max_scc_size",
    "closure_probe_count",
    "closure_probe_max_growth",
}


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


@st.composite
def small_flat_aba_frameworks(draw):
    assumption_count = draw(st.integers(min_value=1, max_value=5))
    derived_count = draw(st.integers(min_value=1, max_value=6))
    assumptions = [lit(f"a{i}") for i in range(assumption_count)]
    contraries = [lit(f"c{i}") for i in range(assumption_count)]
    derived = [lit(f"d{i}") for i in range(derived_count)]
    language = frozenset([*assumptions, *contraries, *derived])
    contrary = {assumption: contraries[index] for index, assumption in enumerate(assumptions)}
    possible_bodies = [*assumptions, *derived]
    rule_specs = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=derived_count - 1),
                st.lists(
                    st.integers(min_value=0, max_value=len(possible_bodies) - 1),
                    min_size=0,
                    max_size=3,
                    unique=True,
                ),
            ),
            min_size=0,
            max_size=8,
        )
    )
    rules = frozenset(
        Rule(
            tuple(possible_bodies[index] for index in body_indexes),
            derived[head_index],
            "strict",
        )
        for head_index, body_indexes in rule_specs
    )
    return ABAFramework(
        language=language,
        rules=rules,
        assumptions=frozenset(assumptions),
        contrary=contrary,
    )


@given(small_flat_aba_frameworks())
@settings(max_examples=40)
def test_telemetry_is_deterministic_and_omits_identity_keys(framework) -> None:
    from argumentation.structured.aba.aba_telemetry import aba_structural_telemetry

    first = aba_structural_telemetry(framework)
    second = aba_structural_telemetry(framework)

    assert first == second
    assert REQUIRED_TELEMETRY_KEYS <= set(first)
    assert not (FORBIDDEN_IDENTITY_KEYS & set(first))
    assert first["atoms"] == len(framework.language)
    assert first["assumptions"] == len(framework.assumptions)
    assert first["rules"] == len(framework.rules)
    assert first["contraries"] == len(framework.contrary)


@given(small_flat_aba_frameworks())
@settings(max_examples=40)
def test_telemetry_is_rule_order_invariant(framework) -> None:
    from argumentation.structured.aba.aba_telemetry import aba_structural_telemetry

    reordered = ABAFramework(
        language=framework.language,
        rules=frozenset(reversed(tuple(framework.rules))),
        assumptions=framework.assumptions,
        contrary=framework.contrary,
    )

    assert aba_structural_telemetry(framework) == aba_structural_telemetry(reordered)


def test_duplicate_syntactic_rules_do_not_create_fake_atoms_or_assumptions() -> None:
    from argumentation.structured.aba.aba_telemetry import aba_structural_telemetry
    from argumentation.iccma import parse_aba

    framework = parse_aba(
        "\n".join(
            [
                "p aba",
                "a a",
                "c a ca",
                "r x a",
                "r x a",
            ]
        )
        + "\n"
    )

    telemetry = aba_structural_telemetry(framework)

    assert telemetry["atoms"] == 3
    assert telemetry["assumptions"] == 1
    assert telemetry["rules"] == 1


def test_deep_rule_dependency_chain_does_not_recurse_over_python_stack() -> None:
    from argumentation.structured.aba.aba_telemetry import aba_structural_telemetry

    assumption = lit("a")
    contrary = lit("ca")
    derived = [lit(f"d{i}") for i in range(1200)]
    rules = [
        Rule((assumption,), derived[0], "strict"),
        *[
            Rule((derived[index - 1],), derived[index], "strict")
            for index in range(1, len(derived))
        ],
    ]
    framework = ABAFramework(
        language=frozenset([assumption, contrary, *derived]),
        rules=frozenset(rules),
        assumptions=frozenset({assumption}),
        contrary={assumption: contrary},
    )

    telemetry = aba_structural_telemetry(framework)

    assert telemetry["rules"] == 1200
    assert telemetry["rule_dependency_scc_count"] == 1200
    assert telemetry["rule_dependency_max_scc_size"] == 1
