from __future__ import annotations

import pytest

from argumentation.probabilistic_treedecomp import (
    PaperTDLabel,
    PaperTDRow,
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

    assert rows == (
        PaperTDRow(
            present_arguments=frozenset(),
            active_defeats=frozenset(),
            labels={},
            witnesses={},
            probability=pytest.approx(0.25),
        ),
        PaperTDRow(
            present_arguments=frozenset({"b"}),
            active_defeats=frozenset(),
            labels={"b": PaperTDLabel.IN},
            witnesses={},
            probability=pytest.approx(0.75),
        ),
    )


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

    out_rows = [row for row in rows if row.labels.get("b") is PaperTDLabel.OUT]
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
