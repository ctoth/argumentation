from __future__ import annotations

import pytest

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import ProbabilisticAF, compute_probabilistic_acceptance
from argumentation.probabilistic_treedecomp import (
    PaperTDLabel,
    PaperTDRow,
    compute_paper_exact_extension_probability,
    paper_forget_rows,
    paper_introduce_rows,
    paper_join_rows,
    paper_leaf_rows,
)


def test_paper_td_leaf_table_starts_with_empty_structure_and_unit_mass() -> None:
    rows = paper_leaf_rows()

    assert rows == (
        PaperTDRow(
            present_arguments=frozenset(),
            active_defeats=frozenset(),
            labels={},
            witnesses={},
            probability=1.0,
        ),
    )


def test_paper_td_introduce_filters_absent_target_argument() -> None:
    rows = paper_introduce_rows(
        paper_leaf_rows(),
        argument="a",
        bag=frozenset({"a"}),
        all_defeats=frozenset(),
        p_argument=0.8,
        p_defeats={},
        queried_in=frozenset({"a"}),
    )

    assert rows == (
        PaperTDRow(
            present_arguments=frozenset({"a"}),
            active_defeats=frozenset(),
            labels={"a": PaperTDLabel.IN},
            witnesses={},
            probability=pytest.approx(0.8),
        ),
    )


def test_paper_td_introduce_branches_absent_and_unattacked_present_argument() -> None:
    rows = paper_introduce_rows(
        paper_leaf_rows(),
        argument="b",
        bag=frozenset({"b"}),
        all_defeats=frozenset(),
        p_argument=0.75,
        p_defeats={},
        queried_in=frozenset(),
    )

    assert rows[0] == PaperTDRow(
        present_arguments=frozenset(),
        active_defeats=frozenset(),
        labels={},
        witnesses={},
        probability=pytest.approx(0.25),
    )
    assert {
        row.labels["b"]
        for row in rows[1:]
    } == {PaperTDLabel.IN, PaperTDLabel.OUT, PaperTDLabel.UNDECIDED}
    assert all(row.probability == pytest.approx(0.75) for row in rows[1:])


def test_paper_td_introduce_records_out_witness_for_attacked_argument() -> None:
    rows = paper_introduce_rows(
        (
            PaperTDRow(
                present_arguments=frozenset({"a"}),
                active_defeats=frozenset(),
                labels={"a": PaperTDLabel.IN},
                witnesses={},
                probability=1.0,
            ),
        ),
        argument="b",
        bag=frozenset({"a", "b"}),
        all_defeats=frozenset({("a", "b")}),
        p_argument=1.0,
        p_defeats={("a", "b"): 0.6},
        queried_in=frozenset(),
    )

    out_rows = [
        row
        for row in rows
        if row.labels.get("b") is PaperTDLabel.OUT and row.witnesses
    ]
    assert len(out_rows) == 1
    assert out_rows[0].active_defeats == frozenset({("a", "b")})
    assert out_rows[0].witnesses == {"b": "a"}
    assert out_rows[0].probability == pytest.approx(0.6)


def test_paper_td_forget_filters_out_without_witness_and_removes_local_state() -> None:
    rows = paper_forget_rows(
        (
            PaperTDRow(
                present_arguments=frozenset({"a", "b"}),
                active_defeats=frozenset({("a", "b")}),
                labels={"a": PaperTDLabel.IN, "b": PaperTDLabel.OUT},
                witnesses={},
                probability=0.2,
            ),
            PaperTDRow(
                present_arguments=frozenset({"a", "b"}),
                active_defeats=frozenset({("a", "b")}),
                labels={"a": PaperTDLabel.IN, "b": PaperTDLabel.OUT},
                witnesses={"b": "a"},
                probability=0.3,
            ),
        ),
        argument="b",
    )

    assert rows == (
        PaperTDRow(
            present_arguments=frozenset({"a"}),
            active_defeats=frozenset(),
            labels={"a": PaperTDLabel.IN},
            witnesses={},
            probability=pytest.approx(0.3),
        ),
    )


def test_paper_td_join_divides_out_common_bag_probability() -> None:
    rows = paper_join_rows(
        (
            PaperTDRow(
                present_arguments=frozenset({"a"}),
                active_defeats=frozenset(),
                labels={"a": PaperTDLabel.IN},
                witnesses={},
                probability=0.4,
            ),
        ),
        (
            PaperTDRow(
                present_arguments=frozenset({"a"}),
                active_defeats=frozenset(),
                labels={"a": PaperTDLabel.IN},
                witnesses={},
                probability=0.5,
            ),
        ),
        bag=frozenset({"a"}),
        p_arguments={"a": 0.8},
        p_defeats={},
        all_defeats=frozenset(),
    )

    assert rows == (
        PaperTDRow(
            present_arguments=frozenset({"a"}),
            active_defeats=frozenset(),
            labels={"a": PaperTDLabel.IN},
            witnesses={},
            probability=pytest.approx(0.25),
        ),
    )


def test_paper_td_evaluator_matches_enumeration_on_complete_extension_query() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(
            arguments=frozenset({"a", "b", "c"}),
            defeats=frozenset({("a", "b"), ("b", "c")}),
        ),
        p_args={"a": 1.0, "b": 1.0, "c": 1.0},
        p_defeats={("a", "b"): 0.7, ("b", "c"): 0.4},
    )

    expected = compute_probabilistic_acceptance(
        praf,
        semantics="complete",
        strategy="exact_enum",
        query_kind="extension_probability",
        queried_set=frozenset({"a", "c"}),
    )
    result = compute_paper_exact_extension_probability(
        praf,
        queried_set=frozenset({"a", "c"}),
    )

    assert result.extension_probability == pytest.approx(expected.extension_probability)
    assert result.backend == "popescu_wallner_iou_witness_td"
    assert result.table_summaries


def test_paper_td_evaluator_lifts_witness_metadata_for_rejected_arguments() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(
            arguments=frozenset({"a", "b", "c"}),
            defeats=frozenset({("a", "b"), ("c", "b")}),
        ),
        p_args={"a": 1.0, "b": 1.0, "c": 1.0},
        p_defeats={("a", "b"): 1.0, ("c", "b"): 1.0},
    )

    result = compute_paper_exact_extension_probability(
        praf,
        queried_set=frozenset({"a", "c"}),
    )

    assert result.argument_witnesses["a"].label is PaperTDLabel.IN
    assert result.argument_witnesses["c"].label is PaperTDLabel.IN
    assert result.argument_witnesses["b"].label is PaperTDLabel.OUT
    assert result.argument_witnesses["b"].witnesses <= frozenset({"a", "c"})
    assert result.argument_witnesses["b"].witnesses


def test_probabilistic_acceptance_routes_paper_td_without_old_exact_dp_backend() -> None:
    praf = ProbabilisticAF(
        framework=ArgumentationFramework(
            arguments=frozenset({"a", "b", "c"}),
            defeats=frozenset({("a", "b"), ("b", "c")}),
        ),
        p_args={"a": 1.0, "b": 1.0, "c": 1.0},
        p_defeats={("a", "b"): 0.7, ("b", "c"): 0.4},
    )

    result = compute_probabilistic_acceptance(
        praf,
        semantics="complete",
        strategy="paper_td",
        query_kind="extension_probability",
        queried_set=frozenset({"a", "c"}),
    )

    assert result.strategy_used == "paper_td"
    assert result.extension_probability == pytest.approx(0.7)
    assert result.strategy_metadata is not None
    assert result.strategy_metadata["backend"] == "popescu_wallner_iou_witness_td"
    assert result.strategy_metadata["paper_conformance"] == "popescu_wallner_2024_algorithm_1"


@pytest.mark.differential
def test_paper_td_evaluator_matches_enumeration_on_low_treewidth_queries() -> None:
    frameworks = (
        (
            frozenset({"a", "b"}),
            frozenset({("a", "b")}),
            {"a": 0.9, "b": 0.8},
            {("a", "b"): 0.5},
            frozenset({"a"}),
        ),
        (
            frozenset({"a", "b", "c"}),
            frozenset({("a", "b"), ("c", "b")}),
            {"a": 1.0, "b": 0.75, "c": 0.8},
            {("a", "b"): 0.6, ("c", "b"): 0.7},
            frozenset({"a", "c"}),
        ),
    )

    for arguments, defeats, p_args, p_defeats, queried_set in frameworks:
        praf = ProbabilisticAF(
            framework=ArgumentationFramework(arguments=arguments, defeats=defeats),
            p_args=p_args,
            p_defeats=p_defeats,
        )

        expected = compute_probabilistic_acceptance(
            praf,
            semantics="complete",
            strategy="exact_enum",
            query_kind="extension_probability",
            queried_set=queried_set,
        )
        result = compute_paper_exact_extension_probability(
            praf,
            queried_set=queried_set,
        )

        assert result.extension_probability == pytest.approx(expected.extension_probability)
