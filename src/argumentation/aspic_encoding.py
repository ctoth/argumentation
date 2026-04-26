"""Deterministic ASPIC+ encoding surfaces for direct reasoning backends."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from argumentation.aspic import (
    ArgumentationSystem,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
)


@dataclass(frozen=True)
class ASPICEncoding:
    """Stable ASP-style fact encoding of an ASPIC+ theory.

    The fact vocabulary follows the input representation used by Lehtonen,
    Niskanen, and Jarvisalo 2024, Section 5: axioms, premises, strict and
    defeasible rule heads/bodies, contrariness, and preference facts.
    """

    facts: tuple[str, ...]
    signature: str
    metadata: dict[str, str]


def encode_aspic_theory(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    pref: PreferenceConfig,
) -> ASPICEncoding:
    """Encode an ASPIC+ theory into deterministic ASP-style input facts."""
    strict_rule_ids = _strict_rule_ids(system.strict_rules)
    defeasible_rule_ids = _defeasible_rule_ids(system.defeasible_rules)
    facts: set[str] = set()

    for axiom in kb.axioms:
        facts.add(f"axiom({_literal_id(axiom)}).")
    for premise in kb.premises:
        facts.add(f"premise({_literal_id(premise)}).")

    for rule in system.strict_rules:
        rule_id = strict_rule_ids[rule]
        facts.add(f"s_head({rule_id},{_literal_id(rule.consequent)}).")
        for antecedent in rule.antecedents:
            facts.add(f"s_body({rule_id},{_literal_id(antecedent)}).")

    for rule in system.defeasible_rules:
        rule_id = defeasible_rule_ids[rule]
        facts.add(f"d_head({rule_id},{_literal_id(rule.consequent)}).")
        for antecedent in rule.antecedents:
            facts.add(f"d_body({rule_id},{_literal_id(antecedent)}).")

    for left, right in system.contrariness.contradictories:
        left_id = _literal_id(left)
        right_id = _literal_id(right)
        facts.add(f"contrary({left_id},{right_id}).")
        facts.add(f"contrary({right_id},{left_id}).")
        facts.add(f"ctrd({left_id},{right_id}).")
        facts.add(f"ctrd({right_id},{left_id}).")
    for left, right in system.contrariness.contraries:
        facts.add(f"contrary({_literal_id(left)},{_literal_id(right)}).")

    for weaker, stronger in pref.rule_order:
        facts.add(
            f"preferred({_rule_id(stronger, strict_rule_ids, defeasible_rule_ids)},"
            f"{_rule_id(weaker, strict_rule_ids, defeasible_rule_ids)})."
        )
    for weaker, stronger in pref.premise_order:
        facts.add(f"preferred({_literal_id(stronger)},{_literal_id(weaker)}).")

    ordered_facts = tuple(sorted(facts))
    signature = hashlib.sha256("\n".join(ordered_facts).encode("utf-8")).hexdigest()
    return ASPICEncoding(
        facts=ordered_facts,
        signature=signature,
        metadata={
            "encoding": "lehtonen_2024_assumption_facts",
            "comparison": pref.comparison,
            "link": pref.link,
        },
    )


def _literal_id(literal: Literal) -> str:
    return repr(literal)


def _strict_rule_ids(rules: frozenset[Rule]) -> dict[Rule, str]:
    return {
        rule: f"s_{index}"
        for index, rule in enumerate(sorted(rules, key=repr))
    }


def _defeasible_rule_ids(rules: frozenset[Rule]) -> dict[Rule, str]:
    named: dict[Rule, str] = {}
    for index, rule in enumerate(sorted(rules, key=repr)):
        named[rule] = rule.name or f"d_{index}"
    return named


def _rule_id(
    rule: Rule,
    strict_rule_ids: dict[Rule, str],
    defeasible_rule_ids: dict[Rule, str],
) -> str:
    if rule in strict_rule_ids:
        return strict_rule_ids[rule]
    return defeasible_rule_ids[rule]


__all__ = ["ASPICEncoding", "encode_aspic_theory"]
