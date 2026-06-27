"""Structural telemetry for flat ABA frameworks."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from argumentation.core.finite import strongly_connected_components
from argumentation.structured.aba._closure import horn_closure
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import Literal


STRUCTURAL_TELEMETRY_KEYS = frozenset(
    {
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
)


def aba_structural_telemetry(framework: ABAFramework) -> dict[str, object]:
    rules = tuple(sorted(framework.rules, key=_rule_key))
    assumptions = tuple(sorted(framework.assumptions, key=repr))
    rule_body_widths = [len(rule.antecedents) for rule in rules]
    rule_dependency = _rule_dependency_graph(rules)
    assumption_dependency = _assumption_dependency_graph(framework, assumptions, rules)
    closure_growth = _closure_probe_growth(framework, assumptions, rules)
    atom_count = len(framework.language)
    assumption_count = len(assumptions)

    return {
        "atoms": atom_count,
        "assumptions": assumption_count,
        "rules": len(rules),
        "contraries": len(framework.contrary),
        "is_flat": not (set(assumptions) & {rule.consequent for rule in rules}),
        "rule_body_width_histogram": _string_histogram(rule_body_widths),
        "max_rule_body_width": max(rule_body_widths, default=0),
        "rule_head_fanin_max": _max_count(rule.consequent for rule in rules),
        "body_literal_fanout_max": _max_count(
            literal for rule in rules for literal in rule.antecedents
        ),
        "contrary_fanin_max": _max_count(framework.contrary.values()),
        "contrary_fanout_max": 1 if framework.contrary else 0,
        "assumption_to_atom_ratio": _ratio(assumption_count, atom_count),
        "rule_to_assumption_ratio": _ratio(len(rules), assumption_count),
        "rule_dependency_scc_count": _scc_count(rule_dependency),
        "rule_dependency_max_scc_size": _max_scc_size(rule_dependency),
        "assumption_dependency_scc_count": _scc_count(assumption_dependency),
        "assumption_dependency_max_scc_size": _max_scc_size(assumption_dependency),
        "closure_probe_count": len(closure_growth),
        "closure_probe_max_growth": max(closure_growth, default=0),
    }


def _rule_key(rule) -> tuple[str, tuple[str, ...]]:
    return (repr(rule.consequent), tuple(sorted(map(repr, rule.antecedents))))


def _string_histogram(values: Iterable[int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items())}


def _max_count(values: Iterable[Literal]) -> int:
    counts = Counter(values)
    return max(counts.values(), default=0)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _rule_dependency_graph(rules: tuple) -> dict[int, set[int]]:
    rules_by_body_literal: defaultdict[Literal, set[int]] = defaultdict(set)
    for index, rule in enumerate(rules):
        for literal in rule.antecedents:
            rules_by_body_literal[literal].add(index)
    graph = {index: set() for index in range(len(rules))}
    for index, rule in enumerate(rules):
        graph[index].update(rules_by_body_literal.get(rule.consequent, set()))
    return graph


def _assumption_dependency_graph(
    framework: ABAFramework,
    assumptions: tuple[Literal, ...],
    rules: tuple,
) -> dict[int, set[int]]:
    assumption_index = {assumption: index for index, assumption in enumerate(assumptions)}
    targets_by_contrary = {
        contrary: assumption_index[assumption]
        for assumption, contrary in framework.contrary.items()
        if assumption in assumption_index
    }
    graph = {index: set() for index in range(len(assumptions))}
    for rule in rules:
        target_index = targets_by_contrary.get(rule.consequent)
        if target_index is None:
            continue
        for literal in rule.antecedents:
            source_index = assumption_index.get(literal)
            if source_index is not None:
                graph[source_index].add(target_index)
    return graph


def _closure_probe_growth(
    framework: ABAFramework,
    assumptions: tuple[Literal, ...],
    rules: tuple,
) -> list[int]:
    probes = assumptions[: min(16, len(assumptions))]
    return [
        max(0, len(_closure_from((assumption,), rules)) - 1)
        for assumption in probes
    ]


def _closure_from(initial: Iterable[Literal], rules: tuple) -> frozenset[Literal]:
    return horn_closure(initial, rules)


def _scc_count(graph: dict[int, set[int]]) -> int:
    return len(_strongly_connected_components(graph))


def _max_scc_size(graph: dict[int, set[int]]) -> int:
    return max((len(component) for component in _strongly_connected_components(graph)), default=0)


def _strongly_connected_components(graph: dict[int, set[int]]) -> list[set[int]]:
    return [set(component) for component in strongly_connected_components(graph)]


__all__ = ["STRUCTURAL_TELEMETRY_KEYS", "aba_structural_telemetry"]
