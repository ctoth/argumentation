from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict

from hypothesis import given, settings

from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import Literal, Rule
from tests.aba_hypothesis_generators import (
    flat_aba_frameworks,
    flat_aba_specs,
    renamed_framework,
)
from tools.aba_shape_benchmark import compute_aba_shape, shape_buckets


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_renaming_preserves_every_shape_field(framework: ABAFramework) -> None:
    renamed, _ = renamed_framework(framework)

    assert compute_aba_shape(renamed) == compute_aba_shape(framework)


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_renaming_preserves_bucketed_shape_fields(framework: ABAFramework) -> None:
    renamed, _ = renamed_framework(framework)
    solver_class = "aba/single-extension/preferred"

    assert shape_buckets(compute_aba_shape(renamed), solver_class) == shape_buckets(
        compute_aba_shape(framework),
        solver_class,
    )


@given(flat_aba_specs())
@settings(max_examples=40)
def test_permuting_rules_preserves_shape(spec) -> None:
    forward = spec.to_framework()
    reversed_rules = ABAFramework(
        language=spec.language,
        assumptions=spec.assumptions,
        contrary=spec.contrary,
        rules=frozenset(reversed(spec.rules)),
    )

    assert compute_aba_shape(reversed_rules) == compute_aba_shape(forward)


@given(flat_aba_specs())
@settings(max_examples=40)
def test_permuting_contrary_declarations_preserves_shape(spec) -> None:
    framework = spec.to_framework()
    reversed_contrary = dict(reversed(tuple(spec.contrary.items())))
    permuted = ABAFramework(
        language=spec.language,
        assumptions=spec.assumptions,
        contrary=reversed_contrary,
        rules=frozenset(spec.rules),
    )

    assert compute_aba_shape(permuted) == compute_aba_shape(framework)


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_adding_unreachable_rule_preserves_grounded_and_acyclic_fields(
    framework: ABAFramework,
) -> None:
    before = compute_aba_shape(framework)
    head, body = _fresh_pair(framework)
    expanded = ABAFramework(
        language=framework.language | frozenset({head, body}),
        assumptions=framework.assumptions,
        contrary=framework.contrary,
        rules=framework.rules | frozenset({Rule((body,), head, "strict")}),
    )
    after = compute_aba_shape(expanded)

    assert after.rule_count == before.rule_count + 1
    assert after.grounded_in_count == before.grounded_in_count
    assert after.grounded_out_count == before.grounded_out_count
    assert after.p_acyclic == before.p_acyclic


@given(flat_aba_frameworks(max_rules=6))
@settings(max_examples=40)
def test_duplicate_semantic_rule_changes_density_not_boolean_shape(
    framework: ABAFramework,
) -> None:
    if not framework.rules:
        return
    rule = sorted(framework.rules, key=repr)[0]
    duplicate = Rule(rule.antecedents, rule.consequent, rule.kind, "duplicate")
    expanded = ABAFramework(
        language=framework.language,
        assumptions=framework.assumptions,
        contrary=framework.contrary,
        rules=framework.rules | frozenset({duplicate}),
    )
    before = compute_aba_shape(framework)
    after = compute_aba_shape(expanded)

    assert after.rule_count == before.rule_count + 1
    assert after.rule_density >= before.rule_density
    assert after.is_flat == before.is_flat
    assert after.p_acyclic == before.p_acyclic


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_removing_zero_body_facts_cannot_increase_closure_size(
    framework: ABAFramework,
) -> None:
    without_facts = ABAFramework(
        language=framework.language,
        assumptions=framework.assumptions,
        contrary=framework.contrary,
        rules=frozenset(rule for rule in framework.rules if rule.antecedents),
    )

    assert len(_closure(without_facts, framework.assumptions)) <= len(
        _closure(framework, framework.assumptions)
    )


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_p_acyclicity_matches_independent_dependency_graph(
    framework: ABAFramework,
) -> None:
    assert compute_aba_shape(framework).p_acyclic is _paper_p_acyclic(framework)


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_scc_count_and_size_match_independent_graph(framework: ABAFramework) -> None:
    components = _independent_sccs(framework)
    shape = compute_aba_shape(framework)

    assert shape.dependency_scc_count == len(components)
    assert shape.dependency_scc_max_size == max((len(component) for component in components), default=0)


@given(flat_aba_specs())
@settings(max_examples=40)
def test_contrary_target_in_degree_is_invariant_under_order_and_renaming(spec) -> None:
    framework = spec.to_framework()
    permuted = ABAFramework(
        language=spec.language,
        assumptions=spec.assumptions,
        contrary=dict(reversed(tuple(spec.contrary.items()))),
        rules=frozenset(spec.rules),
    )
    renamed, _ = renamed_framework(framework)

    keys = {
        "contrary_target_in_degree_max",
        "contrary_target_in_degree_avg",
        "contrary_target_entropy",
    }
    assert _project_shape(framework, keys) == _project_shape(permuted, keys)
    assert _project_shape(framework, keys) == _project_shape(renamed, keys)


@given(flat_aba_frameworks())
@settings(max_examples=40)
def test_closure_growth_is_monotone_when_adding_assumptions(
    framework: ABAFramework,
) -> None:
    ordered = sorted(framework.assumptions, key=repr)
    smaller = frozenset(ordered[: max(0, len(ordered) - 1)])
    larger = framework.assumptions

    assert _closure(framework, smaller) <= _closure(framework, larger)


def _project_shape(framework: ABAFramework, keys: set[str]) -> dict[str, object]:
    data = asdict(compute_aba_shape(framework))
    return {key: data[key] for key in keys}


def _fresh_pair(framework: ABAFramework) -> tuple[Literal, Literal]:
    _, mapping = renamed_framework(framework, prefix="fresh")
    used = set(mapping.values()) | framework.language
    index = 0
    while True:
        head = next(iter(renamed_framework(framework, prefix=f"h{index}")[1].values()))
        body = next(iter(renamed_framework(framework, prefix=f"b{index}")[1].values()))
        if head not in used and body not in used and head != body:
            return head, body
        index += 1


def _closure(framework: ABAFramework, premises: frozenset[Literal]) -> frozenset[Literal]:
    closure = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if all(antecedent in closure for antecedent in rule.antecedents):
                if rule.consequent not in closure:
                    closure.add(rule.consequent)
                    changed = True
    return frozenset(closure)


def _paper_p_acyclic(framework: ABAFramework) -> bool:
    graph = _dependency_graph(framework)
    return not any(len(component) > 1 for component in _sccs(graph)) and not any(
        node in successors for node, successors in graph.items()
    )


def _independent_sccs(framework: ABAFramework) -> list[frozenset[Literal]]:
    return _sccs(_dependency_graph(framework))


def _dependency_graph(framework: ABAFramework) -> dict[Literal, set[Literal]]:
    graph: dict[Literal, set[Literal]] = defaultdict(set)
    for literal in framework.language - framework.assumptions:
        graph[literal]
    for rule in framework.rules:
        if rule.consequent in framework.assumptions:
            continue
        graph[rule.consequent]
        for antecedent in rule.antecedents:
            if antecedent in framework.assumptions:
                continue
            graph[antecedent].add(rule.consequent)
    return graph


def _sccs(graph: dict[Literal, set[Literal]]) -> list[frozenset[Literal]]:
    remaining = set(graph)
    components: list[frozenset[Literal]] = []
    reverse: dict[Literal, set[Literal]] = defaultdict(set)
    for source, targets in graph.items():
        for target in targets:
            reverse[target].add(source)
            remaining.add(target)
    while remaining:
        seed = remaining.pop()
        forward = _reachable(seed, graph)
        backward = _reachable(seed, reverse)
        component = frozenset(forward & backward)
        components.append(component)
        remaining -= component
    return components


def _reachable(seed: Literal, graph: dict[Literal, set[Literal]]) -> set[Literal]:
    seen = {seed}
    stack = [seed]
    while stack:
        node = stack.pop()
        for successor in graph.get(node, ()):
            if successor not in seen:
                seen.add(successor)
                stack.append(successor)
    return seen
