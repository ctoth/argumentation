"""Ground Gunray defeasible-Datalog theories into propositional ASPIC+.

This module is intentionally a consumer of Gunray's public
``DefeasibleTheory`` and ``inspect_grounding`` surfaces. Propstore already
owns authored predicate/rule documents and translates them to Gunray; this
module avoids adding a second document schema in ``argumentation``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal as TypingLiteral

from argumentation.structured.aspic.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    Scalar,
)
from argumentation.core.preference import strict_partial_order_closure

if TYPE_CHECKING:
    from gunray import DefeasibleTheory, GroundingInspection, GroundRuleInstance


@dataclass(frozen=True)
class GroundRuleOrigin:
    """Structured origin for a generated grounded ASPIC+ rule."""

    source_rule_id: str
    substitution: tuple[tuple[str, Scalar], ...]
    role: TypingLiteral["ground", "undercut"]
    target_rule: Rule | None = None


@dataclass(frozen=True)
class GroundedDatalogTheory:
    """ASPIC+ projection of a grounded Gunray defeasible theory."""

    system: ArgumentationSystem
    kb: KnowledgeBase
    pref: PreferenceConfig
    inspection: "GroundingInspection"
    source_to_ground_rules: Mapping[str, frozenset[Rule]]
    rule_origins: Mapping[Rule, GroundRuleOrigin]
    non_approximated_predicates: frozenset[str]


def ground_defeasible_theory(
    theory: "DefeasibleTheory",
    *,
    comparison: str = "elitist",
    link: str = "last",
    simplify: bool = True,
) -> GroundedDatalogTheory:
    """Ground a Gunray ``DefeasibleTheory`` into ASPIC+ objects.

    The returned ``ArgumentationSystem``, ``KnowledgeBase``, and
    ``PreferenceConfig`` are ordinary propositional ASPIC+ structures and can
    be passed to ``build_arguments`` or ``build_abstract_framework``.
    Strong-negated Gunray predicates such as ``~flies("opus")`` are normalized
    to ASPIC literals ``Literal(GroundAtom("flies", ("opus",)), negated=True)``
    rather than being treated as predicates literally named ``"~flies"``.
    """

    gunray = _require_gunray()
    inspection = gunray.inspect_grounding(theory)
    return grounding_inspection_to_aspic(
        inspection,
        superiority=theory.superiority,
        conflicts=theory.conflicts,
        comparison=comparison,
        link=link,
        simplify=simplify,
    )


def grounding_inspection_to_aspic(
    inspection: "GroundingInspection",
    *,
    superiority: tuple[tuple[str, str], ...] = (),
    conflicts: tuple[tuple[str, str], ...] = (),
    comparison: str = "elitist",
    link: str = "last",
    simplify: bool = True,
) -> GroundedDatalogTheory:
    """Project a Gunray ``GroundingInspection`` into ASPIC+ objects.

    This is the direct integration point for callers that already ran Gunray
    and kept the inspection report, such as propstore's ``GroundedRulesBundle``.
    """

    simplification = inspection.simplification

    if simplify:
        fact_atoms = simplification.definite_fact_atoms
        strict_instances = simplification.strict_rules_for_argumentation
        defeasible_instances = simplification.defeasible_rules_for_argumentation
        defeater_instances = simplification.defeater_rules_for_argumentation
        non_approximated = frozenset(simplification.non_approximated_predicates)
    else:
        fact_atoms = inspection.fact_atoms
        strict_instances = inspection.strict_rules
        defeasible_instances = inspection.defeasible_rules
        defeater_instances = inspection.defeater_rules
        non_approximated = frozenset()

    axioms = frozenset(_literal_from_ground_atom(atom) for atom in fact_atoms)
    rule_origins: dict[Rule, GroundRuleOrigin] = {}
    # Distinct authored rules can ground to one ASPIC+ rule; keep every
    # (rule, origin) pair so no source id is dropped.
    ground_origins: list[tuple[Rule, GroundRuleOrigin]] = []
    strict_rules = tuple(
        _rule_from_instance(
            instance,
            kind="strict",
            name=None,
            origins=rule_origins,
            ground_origins=ground_origins,
        )
        for instance in strict_instances
    )
    # Generated rule names n(r) are literals of L that undercuts target, so
    # they must be fresh with respect to every authored predicate.
    reserved_names = _authored_predicates(
        fact_atoms,
        (*strict_instances, *defeasible_instances, *defeater_instances),
    )
    defeasible_rules = []
    for index, instance in enumerate(defeasible_instances):
        defeasible_rules.append(
            _rule_from_instance(
                instance,
                kind="defeasible",
                name=_fresh_rule_name(f"gr{index}", reserved_names),
                origins=rule_origins,
                ground_origins=ground_origins,
            )
        )
    defeasible_rules.extend(
        _undercut_rules_from_defeaters(
            defeater_instances,
            defeasible_rules,
            rule_origins,
            reserved_names,
        )
    )

    source_to_ground = _source_to_ground_rules(ground_origins)
    pref = PreferenceConfig(
        rule_order=_project_rule_order(superiority, source_to_ground),
        premise_order=frozenset(),
        comparison=comparison,
        link=link,
    )
    kb = KnowledgeBase(axioms=axioms, premises=frozenset())

    language = _language_from_parts(axioms, strict_rules, tuple(defeasible_rules))
    contrariness = _contrariness_from_language(language, conflicts)
    system = ArgumentationSystem(
        language=language,
        contrariness=contrariness,
        strict_rules=frozenset(strict_rules),
        defeasible_rules=frozenset(defeasible_rules),
    )
    return GroundedDatalogTheory(
        system=system,
        kb=kb,
        pref=pref,
        inspection=inspection,
        source_to_ground_rules=source_to_ground,
        rule_origins=rule_origins,
        non_approximated_predicates=non_approximated,
    )


def _require_gunray() -> Any:
    try:
        import gunray
    except ImportError as exc:
        raise ImportError(
            "argumentation Datalog grounding requires the [grounding] extra: "
            "install formal-argumentation[grounding]"
        ) from exc
    return gunray


def _literal_from_ground_atom(atom: Any) -> Literal:
    predicate = str(atom.predicate)
    negated = predicate.startswith("~")
    if negated:
        predicate = predicate[1:]
    return Literal(
        atom=GroundAtom(predicate=predicate, arguments=tuple(atom.arguments)),
        negated=negated,
    )


def _rule_from_instance(
    instance: "GroundRuleInstance",
    *,
    kind: str,
    name: str | None,
    origins: dict[Rule, GroundRuleOrigin],
    ground_origins: list[tuple[Rule, GroundRuleOrigin]],
) -> Rule:
    if getattr(instance, "default_negated_body", ()):
        raise ValueError("ASPIC+ grounding does not accept default-negated rule bodies")
    rule = Rule(
        antecedents=tuple(_literal_from_ground_atom(atom) for atom in instance.body),
        consequent=_literal_from_ground_atom(instance.head),
        kind=kind,
        name=name,
    )
    origin = GroundRuleOrigin(
        source_rule_id=instance.rule_id,
        substitution=tuple((name, value) for name, value in instance.substitution),
        role="ground",
    )
    origins.setdefault(rule, origin)
    ground_origins.append((rule, origin))
    return rule


def _undercut_rules_from_defeaters(
    defeater_instances: tuple["GroundRuleInstance", ...],
    target_rules: list[Rule],
    origins: dict[Rule, GroundRuleOrigin],
    reserved_names: set[str],
) -> tuple[Rule, ...]:
    undercut_rules: list[Rule] = []
    for instance in defeater_instances:
        if getattr(instance, "default_negated_body", ()):
            raise ValueError(
                "ASPIC+ grounding does not accept default-negated defeater bodies"
            )
        defeater_head = _literal_from_ground_atom(instance.head)
        antecedents = tuple(_literal_from_ground_atom(atom) for atom in instance.body)
        defeater_targets = _defeater_targets(defeater_head, target_rules, origins)
        for target_rule in defeater_targets:
            if target_rule.name is None:
                continue
            rule = Rule(
                antecedents=antecedents,
                consequent=Literal(GroundAtom(target_rule.name), negated=True),
                kind="defeasible",
                name=_fresh_rule_name(f"uc{len(undercut_rules)}", reserved_names),
            )
            origins[rule] = GroundRuleOrigin(
                source_rule_id=instance.rule_id,
                substitution=tuple(
                    (name, value) for name, value in instance.substitution
                ),
                role="undercut",
                target_rule=target_rule,
            )
            undercut_rules.append(rule)
    return tuple(undercut_rules)


def _authored_predicates(
    fact_atoms: Any,
    instances: tuple["GroundRuleInstance", ...],
) -> set[str]:
    atoms = [*fact_atoms]
    for instance in instances:
        atoms.append(instance.head)
        atoms.extend(instance.body)
    return {_literal_from_ground_atom(atom).atom.predicate for atom in atoms}


def _fresh_rule_name(preferred: str, reserved_names: set[str]) -> str:
    """Return ``preferred`` or a suffixed variant not yet reserved, and reserve it."""
    name = preferred
    suffix = 0
    while name in reserved_names:
        suffix += 1
        name = f"{preferred}_{suffix}"
    reserved_names.add(name)
    return name


def _defeater_targets(
    defeater_head: Literal,
    rules: list[Rule],
    origins: Mapping[Rule, GroundRuleOrigin],
) -> tuple[Rule, ...]:
    if defeater_head.negated:
        # ``~r(t1, ..., tn)`` names the instance of rule ``r`` whose
        # substitution values, in Gunray's variable order, are ``t1..tn``
        # (Diller et al. 2025: each ground instance r theta is a separate
        # rule). A nullary ``~r`` names every instance of ``r``.
        source_id_targets = tuple(
            rule
            for rule in rules
            if rule.name is not None
            and origins[rule].source_rule_id == defeater_head.atom.predicate
            and (
                not defeater_head.atom.arguments
                or GroundAtom(
                    defeater_head.atom.predicate,
                    tuple(value for _name, value in origins[rule].substitution),
                )
                == defeater_head.atom
            )
        )
        if source_id_targets:
            return source_id_targets
    return tuple(
        rule
        for rule in rules
        if rule.name is not None and rule.consequent == defeater_head.contrary
    )


def _source_to_ground_rules(
    ground_origins: list[tuple[Rule, GroundRuleOrigin]],
) -> Mapping[str, frozenset[Rule]]:
    grouped: dict[str, set[Rule]] = {}
    for rule, origin in ground_origins:
        grouped.setdefault(origin.source_rule_id, set()).add(rule)
    return {source_id: frozenset(rules) for source_id, rules in grouped.items()}


def _project_rule_order(
    superiority: tuple[tuple[str, str], ...],
    source_to_ground: Mapping[str, frozenset[Rule]],
) -> frozenset[tuple[Rule, Rule]]:
    projected: set[tuple[Rule, Rule]] = set()
    for superior_id, inferior_id in superiority:
        stronger_rules = source_to_ground.get(superior_id, frozenset())
        weaker_rules = source_to_ground.get(inferior_id, frozenset())
        for weaker in weaker_rules:
            for stronger in stronger_rules:
                if weaker != stronger:
                    projected.add((weaker, stronger))
    return strict_partial_order_closure(projected)


def _language_from_parts(
    axioms: frozenset[Literal],
    strict_rules: tuple[Rule, ...],
    defeasible_rules: tuple[Rule, ...],
) -> frozenset[Literal]:
    language: set[Literal] = set(axioms)
    for rule in (*strict_rules, *defeasible_rules):
        language.add(rule.consequent)
        language.update(rule.antecedents)
        if rule.name is not None:
            language.add(Literal(GroundAtom(rule.name)))
            language.add(Literal(GroundAtom(rule.name), negated=True))

    closed_language = set(language)
    for literal in language:
        closed_language.add(literal.contrary)
    return frozenset(closed_language)


def _contrariness_from_language(
    language: frozenset[Literal],
    conflicts: tuple[tuple[str, str], ...],
) -> ContrarinessFn:
    contradictories = {
        (literal, literal.contrary)
        for literal in language
        if literal.contrary in language and not literal.negated
    }
    contraries: set[tuple[Literal, Literal]] = set()

    by_shape: dict[tuple[str, tuple[Scalar, ...]], set[Literal]] = {}
    for literal in language:
        key = (literal.atom.predicate, tuple(literal.atom.arguments))
        by_shape.setdefault(key, set()).add(literal)

    for left_predicate, right_predicate in conflicts:
        for left, right in _conflict_literals(
            left_predicate, right_predicate, by_shape
        ):
            if left == right:
                continue
            if left.contrary == right or right.contrary == left:
                contradictories.add((left, right))
            else:
                contraries.add((left, right))
                contraries.add((right, left))

    return ContrarinessFn(
        contradictories=frozenset(contradictories),
        contraries=frozenset(contraries),
    )


def _conflict_literals(
    left_predicate: str,
    right_predicate: str,
    by_shape: Mapping[tuple[str, tuple[Scalar, ...]], set[Literal]],
) -> tuple[tuple[Literal, Literal], ...]:
    left_name, left_negated = _decode_predicate_polarity(left_predicate)
    right_name, right_negated = _decode_predicate_polarity(right_predicate)

    keys = {
        args for predicate, args in by_shape if predicate in {left_name, right_name}
    }
    pairs: list[tuple[Literal, Literal]] = []
    for args in keys:
        left = Literal(GroundAtom(left_name, args), left_negated)
        right = Literal(GroundAtom(right_name, args), right_negated)
        pairs.append((left, right))
    return tuple(pairs)


def _decode_predicate_polarity(predicate: str) -> tuple[str, bool]:
    if predicate.startswith("~"):
        return predicate[1:], True
    return predicate, False


__all__ = [
    "GroundedDatalogTheory",
    "GroundRuleOrigin",
    "ground_defeasible_theory",
    "grounding_inspection_to_aspic",
]
