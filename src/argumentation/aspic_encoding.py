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
    extensions: tuple[frozenset[str], ...] = tuple()
    extension_conclusions: tuple[frozenset[Literal], ...] = tuple()
    answer: bool | None = None
    witness: frozenset[str] | None = None
    counterexample: frozenset[str] | None = None


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
    task: str = "enum",
    query: Literal | None = None,
    binary: str = "clingo",
    timeout_seconds: float = 30.0,
) -> ASPICQueryResult:
    """Dispatch an ASPIC+ query to a named optional backend."""
    encoding = encode_aspic_theory(system, kb, pref)
    if semantics not in {"grounded", "admissible", "complete", "stable", "preferred"}:
        return _backend_failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason=f"unsupported ASPIC+ semantics: {semantics}",
        )
    if backend == "asp" and pref.link == "weakest":
        return _backend_failure_result(
            status="unavailable_backend",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason="ASP backend covers last-link only; weakest-link grounded is NP-hard per Lehtonen 2024 Prop 17",
        )

    if backend == "materialized_reference":
        projection = build_abstract_framework(system, kb, pref)
        extensions = _materialized_extensions(projection.framework, semantics)
        return _aspic_task_result(
            projection=projection,
            encoding=encoding,
            semantics=semantics,
            backend=backend,
            task=task,
            query=query,
            extensions=extensions,
            metadata={
                "encoding": encoding.metadata["encoding"],
                "projection": "aspic_abstract_framework",
            },
        )

    if backend in {"asp", "clingo"}:
        from argumentation.solver_adapters import clingo

        if not pref.rule_order and not pref.premise_order:
            facts, element_ids = _source_aspic_facts(system, kb, pref, encoding)
            module_semantics = "complete" if semantics == "grounded" else semantics
            module_semantics = "admissible" if module_semantics == "preferred" else module_semantics
            result = clingo.run_extension_enumeration_protocol(
                facts=facts,
                encoding_modules=(f"aspic_{module_semantics}.lp",),
                known_argument_ids=element_ids,
                known_literal_ids=frozenset(encoding.literal_by_id),
                binary=binary,
                timeout_seconds=timeout_seconds,
                problem=f"ASPIC-SOURCE-{semantics.upper()}",
            )
            if isinstance(result, clingo.ClingoExtensionEnumerationSuccess):
                extensions = result.extensions
                extension_literal_ids = result.extension_literal_ids
                if semantics == "preferred":
                    kept = _maximal_extension_indexes(extensions)
                    extensions = tuple(extensions[index] for index in kept)
                    extension_literal_ids = tuple(extension_literal_ids[index] for index in kept)
                elif semantics == "grounded":
                    kept = _minimal_extension_indexes(extensions)
                    extensions = tuple(extensions[index] for index in kept)
                    extension_literal_ids = tuple(extension_literal_ids[index] for index in kept)
                return _aspic_source_task_result(
                    encoding=encoding,
                    semantics=semantics,
                    backend=backend,
                    task=task,
                    query=query,
                    extensions=extensions,
                    extension_literal_ids=extension_literal_ids,
                    metadata={
                        "encoding": encoding.metadata["encoding"],
                        "projection": "source_assumption_pair",
                        "solver": "clingo",
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
            status = "backend_error" if isinstance(result, clingo.ClingoProcessError) else "protocol_error"
            return _backend_failure_result(
                status=status,
                semantics=semantics,
                backend=backend,
                encoding=encoding,
                reason=result.reason,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        projection = build_abstract_framework(system, kb, pref)
        module_semantics = "complete" if semantics == "grounded" else semantics
        module_semantics = "admissible" if module_semantics == "preferred" else module_semantics
        result = clingo.run_extension_enumeration_protocol(
            facts=_projection_facts(projection),
            encoding_modules=(f"dung_{module_semantics}.lp",),
            known_argument_ids=projection.framework.arguments,
            binary=binary,
            timeout_seconds=timeout_seconds,
            problem=f"ASPIC-{semantics.upper()}",
        )
        if isinstance(result, clingo.ClingoExtensionEnumerationSuccess):
            extensions = result.extensions
            if semantics == "preferred":
                extensions = _maximal_extensions(extensions)
            elif semantics == "grounded":
                extensions = _minimal_extensions(extensions)
            return _aspic_task_result(
                projection=projection,
                encoding=encoding,
                semantics=semantics,
                backend=backend,
                task=task,
                query=query,
                extensions=extensions,
                metadata={
                    "encoding": encoding.metadata["encoding"],
                    "projection": "aspic_abstract_framework",
                    "solver": "clingo",
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


def _materialized_extensions(framework, semantics: str) -> tuple[frozenset[str], ...]:
    from argumentation import dung

    if semantics == "grounded":
        return (dung.grounded_extension(framework),)
    if semantics == "admissible":
        return tuple(
            candidate
            for candidate in dung._all_subsets(framework.arguments)
            if dung.admissible(
                candidate,
                framework.arguments,
                framework.defeats,
                attacks=framework.attacks,
            )
        )
    if semantics == "complete":
        return tuple(dung.complete_extensions(framework))
    if semantics == "stable":
        return tuple(dung.stable_extensions(framework))
    if semantics == "preferred":
        return tuple(dung.preferred_extensions(framework))
    raise ValueError(f"unsupported ASPIC+ semantics: {semantics}")


def _source_aspic_facts(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    pref: PreferenceConfig,
    encoding: ASPICEncoding,
) -> tuple[tuple[str, ...], frozenset[str]]:
    strict_rule_ids = _strict_rule_ids(system.strict_rules)
    defeasible_rule_ids = _defeasible_rule_ids(system.defeasible_rules)
    facts = set(encoding.facts)
    element_ids = frozenset(
        {_literal_id(premise) for premise in kb.premises}
        | set(defeasible_rule_ids.values())
    )
    supports = _source_literal_supports(system, kb, strict_rule_ids, defeasible_rule_ids)
    support_index = 0
    for literal, literal_supports in sorted(supports.items(), key=lambda item: repr(item[0])):
        for support in sorted(literal_supports, key=lambda item: (len(item), tuple(sorted(item)))):
            support_id = f"sup_{support_index}"
            support_index += 1
            facts.add(f"support_concludes({support_id},{_literal_id(literal)}).")
            for element_id in sorted(support):
                facts.add(f"support_member({support_id},{element_id}).")
    return tuple(sorted(facts)), element_ids


def _source_literal_supports(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    strict_rule_ids: dict[Rule, str],
    defeasible_rule_ids: dict[Rule, str],
) -> dict[Literal, frozenset[frozenset[str]]]:
    supports: dict[Literal, set[frozenset[str]]] = {
        literal: set() for literal in system.language
    }
    for axiom in kb.axioms:
        supports.setdefault(axiom, set()).add(frozenset())
    for premise in kb.premises:
        supports.setdefault(premise, set()).add(frozenset({_literal_id(premise)}))

    changed = True
    while changed:
        changed = False
        for rule in sorted(system.strict_rules | system.defeasible_rules, key=repr):
            antecedent_supports = tuple(
                supports.get(antecedent, set())
                for antecedent in rule.antecedents
            )
            for support in _combine_source_supports(antecedent_supports):
                if rule.kind == "defeasible":
                    support = frozenset(support | frozenset({defeasible_rule_ids[rule]}))
                if _add_minimal_source_support(supports.setdefault(rule.consequent, set()), support):
                    changed = True
    return {literal: frozenset(values) for literal, values in supports.items()}


def _combine_source_supports(
    support_sets: tuple[set[frozenset[str]], ...],
) -> set[frozenset[str]]:
    if not support_sets:
        return {frozenset()}
    combined: set[frozenset[str]] = {frozenset()}
    for choices in support_sets:
        if not choices:
            return set()
        combined = {
            frozenset(left | right)
            for left in combined
            for right in choices
        }
    return _minimal_source_supports(combined)


def _minimal_source_supports(supports: set[frozenset[str]]) -> set[frozenset[str]]:
    minimal: set[frozenset[str]] = set()
    for support in sorted(supports, key=lambda item: (len(item), tuple(sorted(item)))):
        _add_minimal_source_support(minimal, support)
    return minimal


def _add_minimal_source_support(
    supports: set[frozenset[str]],
    candidate: frozenset[str],
) -> bool:
    if any(existing <= candidate for existing in supports):
        return False
    supersets = {existing for existing in supports if candidate < existing}
    supports.difference_update(supersets)
    supports.add(candidate)
    return True


def _projection_facts(projection) -> tuple[str, ...]:
    facts: set[str] = set()
    for argument_id in projection.framework.arguments:
        facts.add(f"arg({argument_id}).")
    relation = projection.framework.attacks or projection.framework.defeats
    for attacker, target in relation:
        facts.add(f"attack({attacker},{target}).")
    for attacker, target in projection.framework.defeats:
        facts.add(f"defeat({attacker},{target}).")
    return tuple(sorted(facts))


def _aspic_task_result(
    *,
    projection,
    encoding: ASPICEncoding,
    semantics: str,
    backend: str,
    task: str,
    query: Literal | None,
    extensions: tuple[frozenset[str], ...],
    metadata: dict[str, str],
) -> ASPICQueryResult:
    extension_conclusions = tuple(
        frozenset(conc(projection.id_to_argument[argument_id]) for argument_id in extension)
        for extension in extensions
    )
    if task == "enum":
        selected = extensions[0] if len(extensions) == 1 else frozenset()
        return ASPICQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            accepted_argument_ids=selected,
            accepted_conclusions=_conclusions_for_ids(projection, selected),
            encoding=encoding,
            metadata=metadata | {"task": task},
            extensions=extensions,
            extension_conclusions=extension_conclusions,
        )
    if query is None:
        return _backend_failure_result(
            status="protocol_error",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason="credulous and skeptical ASPIC+ tasks require query",
        )
    if task == "credulous":
        witness = next(
            (
                extension
                for extension, conclusions in zip(extensions, extension_conclusions, strict=True)
                if query in conclusions
            ),
            None,
        )
        return ASPICQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            accepted_argument_ids=witness or frozenset(),
            accepted_conclusions=_conclusions_for_ids(projection, witness or frozenset()),
            encoding=encoding,
            metadata=metadata | {"task": task},
            extensions=extensions,
            extension_conclusions=extension_conclusions,
            answer=witness is not None,
            witness=witness,
        )
    if task == "skeptical":
        counterexample = next(
            (
                extension
                for extension, conclusions in zip(extensions, extension_conclusions, strict=True)
                if query not in conclusions
            ),
            None,
        )
        return ASPICQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            accepted_argument_ids=counterexample or frozenset(),
            accepted_conclusions=_conclusions_for_ids(projection, counterexample or frozenset()),
            encoding=encoding,
            metadata=metadata | {"task": task},
            extensions=extensions,
            extension_conclusions=extension_conclusions,
            answer=counterexample is None,
            counterexample=counterexample,
        )
    return _backend_failure_result(
        status="unavailable_backend",
        semantics=semantics,
        backend=backend,
        encoding=encoding,
        reason=f"unsupported ASPIC+ task: {task}",
    )


def _aspic_source_task_result(
    *,
    encoding: ASPICEncoding,
    semantics: str,
    backend: str,
    task: str,
    query: Literal | None,
    extensions: tuple[frozenset[str], ...],
    extension_literal_ids: tuple[frozenset[str], ...],
    metadata: dict[str, str],
) -> ASPICQueryResult:
    extension_conclusions = tuple(
        frozenset(encoding.literal_by_id[literal_id] for literal_id in literal_ids)
        for literal_ids in extension_literal_ids
    )
    if task == "enum":
        selected_index = 0 if len(extensions) == 1 else None
        return ASPICQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            accepted_argument_ids=extensions[selected_index] if selected_index is not None else frozenset(),
            accepted_conclusions=extension_conclusions[selected_index] if selected_index is not None else frozenset(),
            encoding=encoding,
            metadata=metadata | {"task": task},
            extensions=extensions,
            extension_conclusions=extension_conclusions,
        )
    if query is None:
        return _backend_failure_result(
            status="protocol_error",
            semantics=semantics,
            backend=backend,
            encoding=encoding,
            reason="credulous and skeptical ASPIC+ tasks require query",
        )
    if task == "credulous":
        witness_index = next(
            (index for index, conclusions in enumerate(extension_conclusions) if query in conclusions),
            None,
        )
        return ASPICQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            accepted_argument_ids=extensions[witness_index] if witness_index is not None else frozenset(),
            accepted_conclusions=extension_conclusions[witness_index] if witness_index is not None else frozenset(),
            encoding=encoding,
            metadata=metadata | {"task": task},
            extensions=extensions,
            extension_conclusions=extension_conclusions,
            answer=witness_index is not None,
            witness=extensions[witness_index] if witness_index is not None else None,
        )
    if task == "skeptical":
        counterexample_index = next(
            (index for index, conclusions in enumerate(extension_conclusions) if query not in conclusions),
            None,
        )
        return ASPICQueryResult(
            status="success",
            semantics=semantics,
            backend=backend,
            accepted_argument_ids=extensions[counterexample_index] if counterexample_index is not None else frozenset(),
            accepted_conclusions=extension_conclusions[counterexample_index] if counterexample_index is not None else frozenset(),
            encoding=encoding,
            metadata=metadata | {"task": task},
            extensions=extensions,
            extension_conclusions=extension_conclusions,
            answer=counterexample_index is None,
            counterexample=extensions[counterexample_index] if counterexample_index is not None else None,
        )
    return _backend_failure_result(
        status="unavailable_backend",
        semantics=semantics,
        backend=backend,
        encoding=encoding,
        reason=f"unsupported ASPIC+ task: {task}",
    )


def _conclusions_for_ids(projection, argument_ids: frozenset[str]) -> frozenset[Literal]:
    return frozenset(conc(projection.id_to_argument[argument_id]) for argument_id in argument_ids)


def _maximal_extensions(extensions: tuple[frozenset[str], ...]) -> tuple[frozenset[str], ...]:
    return tuple(extension for extension in extensions if not any(extension < other for other in extensions))


def _minimal_extensions(extensions: tuple[frozenset[str], ...]) -> tuple[frozenset[str], ...]:
    if not extensions:
        return tuple()
    minimal = [extension for extension in extensions if not any(other < extension for other in extensions)]
    return tuple(sorted(minimal, key=lambda extension: (len(extension), tuple(sorted(extension)))))[:1]


def _maximal_extension_indexes(extensions: tuple[frozenset[str], ...]) -> tuple[int, ...]:
    return tuple(
        index
        for index, extension in enumerate(extensions)
        if not any(extension < other for other in extensions)
    )


def _minimal_extension_indexes(extensions: tuple[frozenset[str], ...]) -> tuple[int, ...]:
    if not extensions:
        return tuple()
    candidates = [
        (index, extension)
        for index, extension in enumerate(extensions)
        if not any(other < extension for other in extensions)
    ]
    index, _extension = min(candidates, key=lambda item: (len(item[1]), tuple(sorted(item[1]))))
    return (index,)


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
