from __future__ import annotations

from dataclasses import asdict

from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from tools.aba_shape_benchmark import compute_aba_shape


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def framework(
    *,
    assumptions: set[str],
    contraries: dict[str, str],
    rules: list[tuple[str, tuple[str, ...]]],
) -> ABAFramework:
    assumption_literals = {name: lit(name) for name in assumptions}
    contrary_literals = {name: lit(name) for name in contraries.values()}
    rule_literals = {name: lit(name) for head, body in rules for name in (head, *body)}
    all_literals = assumption_literals | contrary_literals | rule_literals
    return ABAFramework(
        language=frozenset(all_literals.values()),
        assumptions=frozenset(assumption_literals.values()),
        contrary={
            all_literals[assumption]: all_literals[contrary]
            for assumption, contrary in contraries.items()
        },
        rules=frozenset(
            Rule(tuple(all_literals[item] for item in body), all_literals[head], "strict")
            for head, body in rules
        ),
    )


def test_shape_contract_has_no_path_fields() -> None:
    shape = compute_aba_shape(
        framework(
            assumptions={"a"},
            contraries={"a": "ca"},
            rules=[("x", ("a",))],
        )
    )

    forbidden = {"path", "filename", "instance", "directory", "year", "track", "subtrack"}

    assert not (set(asdict(shape)) & forbidden)


def test_p_acyclic_ignores_assumption_premises() -> None:
    shape = compute_aba_shape(
        framework(
            assumptions={"a"},
            contraries={"a": "ca"},
            rules=[
                ("x", ("a",)),
                ("y", ("x",)),
            ],
        )
    )

    assert shape.p_acyclic is True
    assert shape.dependency_cycle_count_or_flag == 0


def test_p_acyclic_detects_non_assumption_dependency_cycle() -> None:
    shape = compute_aba_shape(
        framework(
            assumptions={"a"},
            contraries={"a": "ca"},
            rules=[
                ("x", ("y",)),
                ("y", ("x",)),
            ],
        )
    )

    assert shape.p_acyclic is False
    assert shape.dependency_cycle_count_or_flag == 1
    assert shape.dependency_scc_max_size == 2


def test_tau_aba_proxy_uses_atoms_rules_heads_bodies_contraries() -> None:
    no_rules = compute_aba_shape(
        framework(
            assumptions={"a"},
            contraries={"a": "ca"},
            rules=[],
        )
    )
    with_rule_body = compute_aba_shape(
        framework(
            assumptions={"a", "b"},
            contraries={"a": "ca", "b": "cb"},
            rules=[("x", ("a", "b", "ca"))],
        )
    )

    assert no_rules.tau_aba_primal_width_proxy >= 1
    assert with_rule_body.tau_aba_primal_width_proxy > no_rules.tau_aba_primal_width_proxy


def test_normal_framework_marks_preferred_stable_coincidence_candidate() -> None:
    shape = compute_aba_shape(
        framework(
            assumptions={"a", "b"},
            contraries={"a": "ca", "b": "cb"},
            rules=[],
        )
    )

    assert shape.is_normal is True


def test_flat_framework_marks_empty_set_admissible_candidate() -> None:
    shape = compute_aba_shape(
        framework(
            assumptions={"a"},
            contraries={"a": "ca"},
            rules=[("x", ("a",))],
        )
    )

    assert shape.is_flat is True
    assert shape.assumption_count == shape.assumptions
    assert shape.atom_count == shape.language_literals
    assert shape.rule_count == shape.rules
    assert shape.contrary_count == shape.contraries
