from __future__ import annotations

from argumentation.core.dung import ArgumentationFramework
from argumentation.ranking.ranking import RankingResult, categoriser_ranking
from argumentation.ranking.ranking_axioms import (
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


def test_self_contradiction_ranks_self_attackers_no_higher_than_clean_arguments() -> (
    None
):
    framework = ArgumentationFramework(
        arguments=frozenset({"self", "clean"}),
        defeats=frozenset({("self", "self")}),
    )

    assert self_contradiction(framework, categoriser_ranking(framework))


def test_defense_and_strict_addition_precedence_reward_defended_attackers() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset(
            {"defended", "undefended", "attacker_a", "attacker_b", "helper"}
        ),
        defeats=frozenset(
            {
                ("attacker_a", "defended"),
                ("attacker_b", "undefended"),
                ("helper", "attacker_a"),
            }
        ),
    )
    result = categoriser_ranking(framework)

    assert defense_precedence(framework, result)
    assert strict_addition_of_defense_branch(framework, result)


def test_counter_transitivity_variants_follow_attacker_group_quality() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset(
            {"strong_attacker", "weak_attacker", "left", "right", "helper"}
        ),
        defeats=frozenset(
            {
                ("strong_attacker", "left"),
                ("weak_attacker", "right"),
                ("helper", "strong_attacker"),
            }
        ),
    )
    result = categoriser_ranking(framework)

    assert counter_transitivity(framework, result)
    assert strict_counter_transitivity(framework, result)
    assert quality_precedence(framework, result)


def _tiered_fixture(
    framework: ArgumentationFramework, tiers: tuple[str, ...]
) -> RankingResult:
    ranking = tuple(frozenset(tier) for tier in tiers)
    scores = {
        argument: float(len(ranking) - index)
        for index, tier in enumerate(ranking)
        for argument in tier
    }
    return RankingResult(scores, ranking, True, 1, "fixture")


def _renamed(
    framework: ArgumentationFramework, tiers: tuple[str, ...], mapping: dict[str, str]
) -> tuple[ArgumentationFramework, tuple[str, ...]]:
    def rename(argument: str) -> str:
        return mapping.get(argument, argument)

    renamed_framework = ArgumentationFramework(
        arguments=frozenset(rename(argument) for argument in framework.arguments),
        defeats=frozenset(
            (rename(source), rename(target)) for source, target in framework.defeats
        ),
    )
    renamed_tiers = tuple(
        "".join(rename(argument) for argument in tier) for tier in tiers
    )
    return renamed_framework, renamed_tiers


def test_counter_transitivity_is_invariant_under_renaming() -> None:
    """Amgoud & Ben-Naim 2013, p. 6, CT: if b's attackers dominate a's (some
    injective ``f`` from Arg(a) into Arg(b) with ``f(x) >= x``), then
    ``a >= b``; only the existence of such an ``f`` matters, not which
    candidate a greedy scan tries first. The attacker groups of
    L ({a, z}) and R ({d, b}) have identical tier profiles, so an injective
    matching exists both ways, L and R must tie, and the ranking below (which
    puts L above R) violates CT under every naming of the arguments."""
    framework = ArgumentationFramework(
        arguments=frozenset("abdzLR"),
        defeats=frozenset(
            {("a", "b"), ("a", "z"), ("a", "L"), ("z", "L"), ("d", "R"), ("b", "R")}
        ),
    )
    tiers = ("ad", "bz", "L", "R")

    assert counter_transitivity(framework, _tiered_fixture(framework, tiers)) is False
    renamed_framework, renamed_tiers = _renamed(framework, tiers, {"a": "y", "z": "c"})
    assert (
        counter_transitivity(
            renamed_framework, _tiered_fixture(renamed_framework, renamed_tiers)
        )
        is False
    )


def test_counter_transitivity_holds_when_tied_groups_are_tied_control() -> None:
    """Control: the same framework ranked with L and R tied satisfies CT."""
    framework = ArgumentationFramework(
        arguments=frozenset("abdzLR"),
        defeats=frozenset(
            {("a", "b"), ("a", "z"), ("a", "L"), ("z", "L"), ("d", "R"), ("b", "R")}
        ),
    )

    assert counter_transitivity(
        framework, _tiered_fixture(framework, ("ad", "bz", "LR"))
    )


def test_distributed_defense_precedence_prefers_spread_defense() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset(
            {
                "distributed",
                "concentrated",
                "da",
                "db",
                "ca",
                "cb",
                "d1",
                "d2",
                "c1",
            }
        ),
        defeats=frozenset(
            {
                ("da", "distributed"),
                ("db", "distributed"),
                ("ca", "concentrated"),
                ("cb", "concentrated"),
                ("d1", "da"),
                ("d2", "db"),
                ("c1", "ca"),
                ("c1", "cb"),
            }
        ),
    )

    assert distributed_defense_precedence(framework, categoriser_ranking(framework))


def _all_tied(framework: ArgumentationFramework) -> RankingResult:
    return RankingResult(
        {argument: 0.0 for argument in framework.arguments},
        (framework.arguments,),
        True,
        0,
        "all-tied",
    )


def test_self_contradiction_rejects_tie_with_self_attacker() -> None:
    """Bonzon et al. 2016, p. 2, SC: (a, a) not in R and (b, b) in R imply
    a > b, strictly; a tie with the self-attacker violates it."""
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}), defeats=frozenset({("b", "b")})
    )

    assert self_contradiction(framework, _all_tied(framework)) is False


def test_cardinality_precedence_rejects_ties_on_a_chain() -> None:
    """Bonzon et al. 2016, p. 2, CP: |R1-(a)| < |R1-(b)| implies a > b, with
    no requirement that attackers be unattacked and including zero attackers.
    In a -> b -> c, a has fewer attackers than b and c, so ties violate CP."""
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c")}),
    )

    assert cardinality_precedence(framework, _all_tied(framework)) is False
    assert cardinality_precedence(framework, categoriser_ranking(framework))


def _amgoud_example_3() -> ArgumentationFramework:
    return ArgumentationFramework(
        arguments=frozenset("abcdegh"),
        defeats=frozenset({("h", "c"), ("c", "a"), ("d", "a"), ("e", "b"), ("g", "b")}),
    )


def test_defense_precedence_needs_only_a_nonempty_defender_set() -> None:
    """Amgoud & Ben-Naim 2013, Example 3, and Bonzon et al. 2016, p. 2, DP:
    equal attacker counts, R2+(a) nonempty and R2+(b) empty imply a > b.
    a is attacked by c (defended by h) and d (undefended); b by e and g;
    tying a and b violates DP although not every attacker of a is attacked."""
    framework = _amgoud_example_3()

    assert defense_precedence(framework, _all_tied(framework)) is False


def test_defense_precedence_accepts_categoriser_on_example_3_control() -> None:
    """Control: the categoriser ranks a strictly above b on Example 3."""
    framework = _amgoud_example_3()

    assert defense_precedence(framework, categoriser_ranking(framework))
