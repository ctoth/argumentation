from __future__ import annotations

from collections import defaultdict

import pytest
from hypothesis import given, settings

from argumentation.aba import ABAFramework, NotFlatABAError
from argumentation.structured.aspic.aspic import Literal, Rule
from argumentation.iccma import parse_aba, write_aba
from tests.aba_hypothesis_generators import (
    cyclic_dependency_frameworks,
    flat_aba_frameworks,
    flat_aba_specs,
    non_flat_aba_specs,
    p_acyclic_frameworks,
    renamed_framework,
)
from tools.aba_shape_benchmark import compute_aba_shape


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_generated_frameworks_parse_back_into_equivalent_frameworks(
    framework: ABAFramework,
) -> None:
    assert parse_aba(write_aba(framework)) == framework


@given(flat_aba_specs())
@settings(max_examples=40)
def test_generated_rule_order_is_not_semantically_meaningful(spec) -> None:
    forward = spec.to_framework()
    reversed_rules = ABAFramework(
        language=spec.language,
        assumptions=spec.assumptions,
        contrary=spec.contrary,
        rules=frozenset(reversed(spec.rules)),
    )

    assert reversed_rules == forward
    assert compute_aba_shape(reversed_rules) == compute_aba_shape(forward)


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_generated_atom_renaming_maps_are_bijective(framework: ABAFramework) -> None:
    renamed, mapping = renamed_framework(framework)

    assert set(mapping) == set(framework.language)
    assert len(set(mapping.values())) == len(mapping)
    assert renamed.language == frozenset(mapping.values())


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_generated_flat_frameworks_have_no_assumption_rule_bodies(
    framework: ABAFramework,
) -> None:
    assert all(
        antecedent not in framework.assumptions
        for rule in framework.rules
        for antecedent in rule.antecedents
    )


@given(non_flat_aba_specs())
@settings(max_examples=20)
def test_non_flat_generator_produces_rejected_assumption_heads(spec) -> None:
    with pytest.raises(NotFlatABAError):
        spec.to_framework()


@given(p_acyclic_frameworks())
@settings(max_examples=40)
def test_generated_p_acyclic_frameworks_match_paper_dependency_definition(
    framework: ABAFramework,
) -> None:
    assert compute_aba_shape(framework).p_acyclic is True
    assert _paper_p_acyclic(framework) is True


@given(cyclic_dependency_frameworks())
def test_cyclic_dependency_generator_has_non_assumption_cycle(
    framework: ABAFramework,
) -> None:
    assert compute_aba_shape(framework).p_acyclic is False
    assert _paper_p_acyclic(framework) is False


def _paper_p_acyclic(framework: ABAFramework) -> bool:
    graph: dict[Literal, set[Literal]] = defaultdict(set)
    for literal in framework.language - framework.assumptions:
        graph[literal]
    for rule in framework.rules:
        if rule.consequent in framework.assumptions:
            continue
        for antecedent in rule.antecedents:
            if antecedent in framework.assumptions:
                continue
            graph[antecedent].add(rule.consequent)
    return not _has_cycle(graph)


def _has_cycle(graph: dict[Literal, set[Literal]]) -> bool:
    visiting: set[Literal] = set()
    visited: set[Literal] = set()

    def visit(node: Literal) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for successor in graph[node]:
            if visit(successor):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)
