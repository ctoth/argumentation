from __future__ import annotations

import argumentation
from argumentation.dung import ArgumentationFramework
from argumentation.ranking import categoriser_ranking
from argumentation.ranking_axioms import (
    cardinality_precedence,
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
