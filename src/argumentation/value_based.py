"""Value-based filtering helpers for ASPIC+ inputs."""

from __future__ import annotations

from dataclasses import dataclass

from argumentation.aspic import (
    ASPICAbstractProjection,
    ArgumentationSystem,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
)


@dataclass(frozen=True)
class SubjectiveArgumentationTheory:
    """A value-filtered ASPIC+ theory plus its abstract projection."""

    system: ArgumentationSystem
    knowledge_base: KnowledgeBase
    preference: PreferenceConfig
    projection: ASPICAbstractProjection


def complementary_literals(
    propositions: frozenset[Literal],
    clean: frozenset[Literal],
) -> frozenset[Literal]:
    """Return complements of positive propositions rejected by a value filter.

    Wallner et al. 2024, Definition 11: rejected positive propositions are
    represented by complementary literals in the agent's subjective base.
    """
    _validate_positive_propositions(propositions)
    unknown_clean = clean - propositions
    if unknown_clean:
        raise ValueError(f"clean contains unknown propositions: {sorted(map(repr, unknown_clean))!r}")
    return frozenset(
        proposition.contrary
        for proposition in propositions - clean
    )


def subjective_knowledge_base(
    knowledge_base: KnowledgeBase,
    *,
    propositions: frozenset[Literal],
    clean: frozenset[Literal],
) -> KnowledgeBase:
    """Filter ordinary premises and add complements for rejected propositions.

    Axioms are preserved. Ordinary premises rejected by the agent's value filter
    are removed, and their complementary literals are added as ordinary premises.
    """
    complements = complementary_literals(propositions, clean)
    rejected = propositions - clean
    return KnowledgeBase(
        axioms=knowledge_base.axioms,
        premises=frozenset(
            (knowledge_base.premises - rejected) | complements
        ),
    )


def subjective_defeasible_rules(
    rules: frozenset[Rule],
    *,
    clean: frozenset[Literal],
) -> frozenset[Rule]:
    """Return defeasible rules whose body, head, and name pass the value filter.

    Wallner et al. 2024, Definition 13: a defeasible rule survives when its
    body, head, and rule name are all in the agent's clean proposition base.
    """
    surviving: set[Rule] = set()
    for rule in rules:
        if rule.kind != "defeasible":
            raise ValueError("subjective_defeasible_rules expects defeasible rules")
        if rule.name is None:
            raise ValueError("defeasible rules must have a name for value filtering")
        required = frozenset(rule.antecedents) | {rule.consequent, _rule_name_literal(rule)}
        if required <= clean:
            surviving.add(rule)
    return frozenset(surviving)


def subjective_argumentation_theory(
    system: ArgumentationSystem,
    knowledge_base: KnowledgeBase,
    preference: PreferenceConfig,
    *,
    propositions: frozenset[Literal],
    clean: frozenset[Literal],
) -> SubjectiveArgumentationTheory:
    """Build a subjective ASPIC+ theory and projected AF for one value filter.

    Wallner et al. 2024, Definitions 12-14: ordinary premises are filtered and
    complemented, defeasible rules are filtered by body/head/name, and strict
    rules are preserved.
    """
    subjective_kb = subjective_knowledge_base(
        knowledge_base,
        propositions=propositions,
        clean=clean,
    )
    subjective_rules = subjective_defeasible_rules(
        system.defeasible_rules,
        clean=clean,
    )
    subjective_system = ArgumentationSystem(
        language=system.language,
        contrariness=system.contrariness,
        strict_rules=system.strict_rules,
        defeasible_rules=subjective_rules,
    )
    subjective_preference = PreferenceConfig(
        rule_order=frozenset(
            (weaker, stronger)
            for weaker, stronger in preference.rule_order
            if weaker in subjective_rules and stronger in subjective_rules
        ),
        premise_order=frozenset(
            (weaker, stronger)
            for weaker, stronger in preference.premise_order
            if weaker in subjective_kb.premises and stronger in subjective_kb.premises
        ),
        comparison=preference.comparison,
        link=preference.link,
    )
    projection = build_abstract_framework(
        subjective_system,
        subjective_kb,
        subjective_preference,
    )
    return SubjectiveArgumentationTheory(
        system=subjective_system,
        knowledge_base=subjective_kb,
        preference=subjective_preference,
        projection=projection,
    )


def _rule_name_literal(rule: Rule) -> Literal:
    if rule.name is None:
        raise ValueError("defeasible rules must have a name for value filtering")
    return Literal(GroundAtom(rule.name))


def _validate_positive_propositions(propositions: frozenset[Literal]) -> None:
    negated = sorted(repr(proposition) for proposition in propositions if proposition.negated)
    if negated:
        raise ValueError(f"propositions must be positive literals: {negated!r}")
