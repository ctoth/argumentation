from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import ProbabilisticAF, compute_probabilistic_acceptance
from argumentation.probabilistic_treedecomp import (
    compute_exact_dp,
    compute_exact_dp_with_diagnostics,
    compute_tree_decomposition,
    estimate_treewidth,
    supports_exact_dp,
    to_nice_tree_decomposition,
    validate_tree_decomposition,
)


def _praf(
    arguments: set[str],
    defeats: set[tuple[str, str]],
    *,
    p_defeat: float = 0.5,
) -> ProbabilisticAF:
    framework = ArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(defeats),
    )
    return ProbabilisticAF(
        framework=framework,
        p_args={arg: 1.0 for arg in arguments},
        p_defeats={edge: p_defeat for edge in defeats},
    )


def test_treewidth_estimation_for_empty_path_and_clique() -> None:
    assert estimate_treewidth(ArgumentationFramework(frozenset(), frozenset())) == 0
    assert estimate_treewidth(
        ArgumentationFramework(
            arguments=frozenset({"a", "b", "c"}),
            defeats=frozenset({("a", "b"), ("b", "c")}),
        )
    ) == 1
    assert estimate_treewidth(
        ArgumentationFramework(
            arguments=frozenset({"a", "b", "c"}),
            defeats=frozenset({
                ("a", "b"),
                ("b", "a"),
                ("a", "c"),
                ("c", "a"),
                ("b", "c"),
                ("c", "b"),
            }),
        )
    ) == 2


def test_tree_decomposition_validates_path_framework() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c"}),
        defeats=frozenset({("a", "b"), ("b", "c")}),
    )

    decomposition = compute_tree_decomposition(framework)
    nice = to_nice_tree_decomposition(decomposition)

    validate_tree_decomposition(decomposition, framework)
    assert nice.root in nice.nodes


def test_exact_dp_matches_exact_enumeration_on_grounded_path() -> None:
    praf = _praf({"a", "b", "c"}, {("a", "b"), ("b", "c")}, p_defeat=0.5)

    exact = compute_probabilistic_acceptance(
        praf,
        semantics="grounded",
        strategy="exact_enum",
    )
    dp = compute_probabilistic_acceptance(
        praf,
        semantics="grounded",
        strategy="exact_dp",
    )

    assert dp.strategy_used == "exact_dp"
    assert dp.acceptance_probs == pytest.approx(exact.acceptance_probs)
    assert dp.strategy_metadata == {
        "backend": "grounded_edge_tracking_td",
        "paper_conformance": "adapted_not_popescu_iou_witness_dp",
    }


def test_exact_dp_diagnostics_expose_grounded_table_summaries() -> None:
    praf = _praf({"a", "b", "c"}, {("a", "b"), ("b", "c")}, p_defeat=0.5)

    diagnostics = compute_exact_dp_with_diagnostics(praf, semantics="grounded")

    assert diagnostics.acceptance_probs == pytest.approx(compute_exact_dp(praf))
    assert diagnostics.treewidth == 1
    assert diagnostics.node_count >= 1
    assert diagnostics.component_count == 1
    assert diagnostics.root_table_rows >= 1
    assert diagnostics.root_probability_mass == pytest.approx(1.0)
    assert diagnostics.table_summaries
    assert {summary.node_type for summary in diagnostics.table_summaries} >= {
        "leaf",
        "introduce",
        "forget",
    }
    assert all(summary.row_count >= 1 for summary in diagnostics.table_summaries)


def test_exact_dp_diagnostics_expose_grounded_status_witnesses() -> None:
    praf = _praf(
        {"a", "b", "c", "x", "y"},
        {("a", "b"), ("b", "c"), ("x", "y"), ("y", "x")},
        p_defeat=1.0,
    )

    diagnostics = compute_exact_dp_with_diagnostics(praf, semantics="grounded")

    assert diagnostics.acceptance_probs == pytest.approx(compute_exact_dp(praf))
    assert diagnostics.component_count == 2
    assert diagnostics.status_probabilities["a"].accepted == pytest.approx(1.0)
    assert diagnostics.status_probabilities["b"].rejected == pytest.approx(1.0)
    assert diagnostics.status_probabilities["x"].undecided == pytest.approx(1.0)
    assert diagnostics.status_probabilities["y"].undecided == pytest.approx(1.0)

    accepted_witness = diagnostics.status_witnesses["a"].accepted
    rejected_witness = diagnostics.status_witnesses["b"].rejected
    undecided_witness = diagnostics.status_witnesses["x"].undecided

    assert accepted_witness is not None
    assert accepted_witness.argument == "a"
    assert accepted_witness.present_arguments >= frozenset({"a", "b", "c"})

    assert rejected_witness is not None
    assert rejected_witness.argument == "b"
    assert ("a", "b") in rejected_witness.active_defeats

    assert undecided_witness is not None
    assert undecided_witness.argument == "x"
    assert {("x", "y"), ("y", "x")} <= undecided_witness.active_defeats


def test_exact_dp_rejects_richer_support_worlds() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(arguments=frozenset({"a", "b"}), defeats=frozenset()),
        p_args={"a": 1.0, "b": 1.0},
        p_defeats={},
        supports=frozenset({("a", "b")}),
        p_supports={("a", "b"): 1.0},
    )

    assert not supports_exact_dp(praf, "grounded")
    with pytest.raises(ValueError, match="exact_dp"):
        compute_probabilistic_acceptance(praf, strategy="exact_dp")
