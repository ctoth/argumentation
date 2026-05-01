"""Deterministic ASPIC+ encoding surfaces for direct reasoning backends."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from argumentation.aspic import (
    ArgumentationSystem,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
    conc,
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
    literal_by_id: dict[str, Literal] = field(default_factory=dict)


@dataclass(frozen=True)
class ASPICQueryResult:
    """Result for a package-native ASPIC+ query surface."""

    status: str
    semantics: str
    backend: str
    accepted_argument_ids: frozenset[str]
    accepted_conclusions: frozenset[Literal]
    encoding: ASPICEncoding
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
    literal_by_id: dict[str, Literal] = {}

    def literal_id(literal: Literal) -> str:
        encoded = _literal_id(literal)
        existing = literal_by_id.setdefault(encoded, literal)
        if existing != literal:
            raise ValueError(
                "ASP literal id collision: "
                f"{encoded!r} maps to both {existing!r} and {literal!r}"
            )
        return encoded

    for axiom in kb.axioms:
        facts.add(f"axiom({literal_id(axiom)}).")
    for premise in kb.premises:
        facts.add(f"premise({literal_id(premise)}).")

    for rule in system.strict_rules:
        rule_id = strict_rule_ids[rule]
        facts.add(f"s_head({rule_id},{literal_id(rule.consequent)}).")
        for antecedent in rule.antecedents:
            facts.add(f"s_body({rule_id},{literal_id(antecedent)}).")

    for rule in system.defeasible_rules:
        rule_id = defeasible_rule_ids[rule]
        facts.add(f"d_head({rule_id},{literal_id(rule.consequent)}).")
        for antecedent in rule.antecedents:
            facts.add(f"d_body({rule_id},{literal_id(antecedent)}).")

    for left, right in system.contrariness.contradictories:
        left_id = literal_id(left)
        right_id = literal_id(right)
        facts.add(f"contrary({left_id},{right_id}).")
        facts.add(f"contrary({right_id},{left_id}).")
        facts.add(f"ctrd({left_id},{right_id}).")
        facts.add(f"ctrd({right_id},{left_id}).")
    for left, right in system.contrariness.contraries:
        facts.add(f"contrary({literal_id(left)},{literal_id(right)}).")

    for weaker, stronger in pref.rule_order:
        facts.add(
            f"preferred({_rule_id(stronger, strict_rule_ids, defeasible_rule_ids)},"
            f"{_rule_id(weaker, strict_rule_ids, defeasible_rule_ids)})."
        )
    for weaker, stronger in pref.premise_order:
        facts.add(f"preferred({literal_id(stronger)},{literal_id(weaker)}).")

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
        literal_by_id=literal_by_id,
    )


def solve_aspic_grounded(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    pref: PreferenceConfig,
) -> ASPICQueryResult:
    """Evaluate grounded ASPIC+ acceptance through the reference projection.

    This is the tested direct package query surface. Its current backend is the
    materialized ASPIC-to-Dung reference path; optional ASP/clingo backends can
    attach to the same encoding/result contract in later slices.
    """
    from argumentation.dung import grounded_extension

    encoding = encode_aspic_theory(system, kb, pref)
    projection = build_abstract_framework(system, kb, pref)
    accepted_argument_ids = grounded_extension(projection.framework)
    accepted_conclusions = frozenset(
        conc(projection.id_to_argument[argument_id])
        for argument_id in accepted_argument_ids
    )
    return ASPICQueryResult(
        status="success",
        semantics="grounded",
        backend="materialized_reference",
        accepted_argument_ids=accepted_argument_ids,
        accepted_conclusions=accepted_conclusions,
        encoding=encoding,
        metadata={
            "encoding": encoding.metadata["encoding"],
            "projection": "aspic_abstract_framework",
        },
    )


def solve_aspic_with_backend(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    pref: PreferenceConfig,
    *,
    backend: str,
    semantics: str = "grounded",
    binary: str = "clingo",
    timeout_seconds: float = 30.0,
) -> ASPICQueryResult:
    """Dispatch an ASPIC+ query to a named optional backend."""
    if backend == "materialized_reference" and semantics == "grounded":
        return solve_aspic_grounded(system, kb, pref)

    encoding = encode_aspic_theory(system, kb, pref)
    if backend == "clingo":
        if semantics != "grounded":
            return ASPICQueryResult(
                status="unavailable_backend",
                semantics=semantics,
                backend=backend,
                accepted_argument_ids=frozenset(),
                accepted_conclusions=frozenset(),
                encoding=encoding,
                metadata={
                    "reason": "ASPIC+ clingo backend supports grounded only",
                    "encoding": encoding.metadata["encoding"],
                },
            )
        from argumentation.solver_adapters import clingo

        result = clingo.run_aspic_grounded_protocol(
            facts=encoding.facts,
            known_literal_ids=frozenset(encoding.literal_by_id),
            binary=binary,
            timeout_seconds=timeout_seconds,
        )
        if isinstance(result, clingo.ClingoAnswerSetSuccess):
            return ASPICQueryResult(
                status="success",
                semantics=semantics,
                backend=backend,
                accepted_argument_ids=result.accepted_argument_ids,
                accepted_conclusions=frozenset(
                    encoding.literal_by_id[literal_id]
                    for literal_id in result.accepted_literal_ids
                ),
                encoding=encoding,
                metadata={
                    "encoding": encoding.metadata["encoding"],
                    "stdout": result.stdout,
                },
            )
        if isinstance(result, clingo.ClingoUnavailable):
            return _backend_failure_result(
                status="unavailable_backend",
                semantics=semantics,
                backend=backend,
                encoding=encoding,
                reason=result.reason,
            )
        if isinstance(result, clingo.ClingoProcessError):
            return _backend_failure_result(
                status="backend_error",
                semantics=semantics,
                backend=backend,
                encoding=encoding,
                reason=result.reason,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        return _backend_failure_result(
            status="protocol_error",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason=result.reason,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    return ASPICQueryResult(
        status="unavailable_backend",
        semantics=semantics,
        backend=backend,
        accepted_argument_ids=frozenset(),
        accepted_conclusions=frozenset(),
        encoding=encoding,
        metadata={
            "reason": "backend is not installed or registered",
            "encoding": encoding.metadata["encoding"],
        },
    )


def _backend_failure_result(
    *,
    status: str,
    semantics: str,
    backend: str,
    encoding: ASPICEncoding,
    reason: str,
    stdout: str = "",
    stderr: str = "",
) -> ASPICQueryResult:
    metadata = {
        "reason": reason,
        "encoding": encoding.metadata["encoding"],
    }
    if stdout:
        metadata["stdout"] = stdout
    if stderr:
        metadata["stderr"] = stderr
    return ASPICQueryResult(
        status=status,
        semantics=semantics,
        backend=backend,
        accepted_argument_ids=frozenset(),
        accepted_conclusions=frozenset(),
        encoding=encoding,
        metadata=metadata,
    )


def _literal_id(literal: Literal) -> str:
    rendered = repr(literal)
    if rendered.startswith("~"):
        rendered = f"n_{rendered[1:]}"
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", rendered)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "literal"
    if cleaned[0].isupper():
        cleaned = cleaned[0].lower() + cleaned[1:]
    if not cleaned[0].islower():
        cleaned = f"l_{cleaned}"
    return cleaned


def _strict_rule_ids(rules: frozenset[Rule]) -> dict[Rule, str]:
    return {
        rule: f"s_{index}"
        for index, rule in enumerate(sorted(rules, key=repr))
    }


def _defeasible_rule_ids(rules: frozenset[Rule]) -> dict[Rule, str]:
    rules_by_name: dict[str, list[Rule]] = {}
    for rule in rules:
        if rule.name is not None:
            rules_by_name.setdefault(rule.name, []).append(rule)
    duplicates = sorted(
        (name, rules)
        for name, rules in rules_by_name.items()
        if len(rules) > 1
    )
    if duplicates:
        name, duplicate_rules = duplicates[0]
        raise ValueError(
            f"duplicate defeasible rule name: {name!r} "
            f"attached to {len(duplicate_rules)} rules"
        )
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


__all__ = [
    "ASPICEncoding",
    "ASPICQueryResult",
    "encode_aspic_theory",
    "solve_aspic_grounded",
    "solve_aspic_with_backend",
]
