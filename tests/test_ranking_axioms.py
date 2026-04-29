from __future__ import annotations

import argumentation
from argumentation.dung import ArgumentationFramework
from argumentation.ranking import categoriser_ranking
from argumentation.ranking_axioms import (
    abstraction,
    cardinality_precedence,
    counter_transitivity,
    defense_precedence,
    distributed_defense_precedence,
    independence,
    quality_precedence,
    self_contradiction,
    strict_addition_of_defense_branch,
    strict_counter_transitivity,
    strict_preference_transitive,
    void_precedence,
)


def test_ranking_axioms_module_is_exported() -> None:
    assert argumentation.ranking_axioms.void_precedence is void_precedence
    assert "ranking_axioms" in argumentation.__all__


def test_strict_preference_transitive_checks_ranking_result() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c")}),
    )

    assert strict_preference_transitive(categoriser_ranking(framework))


def test_void_precedence_prefers_unattacked_over_attacked() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )

    assert void_precedence(framework, categoriser_ranking(framework))


def test_cardinality_precedence_prefers_fewer_unattacked_attackers() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d", "e"}),
        defeats=frozenset({("a", "d"), ("b", "e"), ("c", "e")}),
    )

    assert cardinality_precedence(framework, categoriser_ranking(framework))


def test_abstraction_and_independence_ignore_names_and_disconnected_context() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "x", "y"}),
        defeats=frozenset({("a", "b"), ("x", "y")}),
    )

    assert abstraction(categoriser_ranking, framework)
    assert independence(categoriser_ranking, framework)


def test_self_contradiction_ranks_self_attackers_no_higher_than_clean_arguments() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"self", "clean"}),
        defeats=frozenset({("self", "self")}),
    )

    assert self_contradiction(framework, categoriser_ranking(framework))


def test_defense_and_strict_addition_precedence_reward_defended_attackers() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"defended", "undefended", "attacker_a", "attacker_b", "helper"}),
        defeats=frozenset({
            ("attacker_a", "defended"),
            ("attacker_b", "undefended"),
            ("helper", "attacker_a"),
        }),
    )
    result = categoriser_ranking(framework)

    assert defense_precedence(framework, result)
    assert strict_addition_of_defense_branch(framework, result)


def test_counter_transitivity_variants_follow_attacker_group_quality() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"strong_attacker", "weak_attacker", "left", "right", "helper"}),
        defeats=frozenset({
            ("strong_attacker", "left"),
            ("weak_attacker", "right"),
            ("helper", "strong_attacker"),
        }),
    )
    result = categoriser_ranking(framework)

    assert counter_transitivity(framework, result)
    assert strict_counter_transitivity(framework, result)
    assert quality_precedence(framework, result)


def test_distributed_defense_precedence_prefers_spread_defense() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({
            "distributed",
            "concentrated",
            "da",
            "db",
            "ca",
            "cb",
            "d1",
            "d2",
            "c1",
        }),
        defeats=frozenset({
            ("da", "distributed"),
            ("db", "distributed"),
            ("ca", "concentrated"),
            ("cb", "concentrated"),
            ("d1", "da"),
            ("d2", "db"),
            ("c1", "ca"),
            ("c1", "cb"),
        }),
    )

    assert distributed_defense_precedence(framework, categoriser_ranking(framework))
