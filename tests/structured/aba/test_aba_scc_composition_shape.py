"""Focused contracts for the probe-5 SCC operational-shape diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from argumentation.structured.aspic.aspic import GroundAtom, Literal
from scripts.aba_scc_composition_reference import (
    CollectiveAttack,
    CollectiveFramework,
    ComponentBoundary,
    ConditionedAttack,
    ReferenceCaps,
)
from scripts.measure_aba_scc_composition_shape import (
    MeasurementFailure,
    full_boundary_item_count,
    has_strict_residual_reduction,
    load_baseline_timeout_frameworks,
    reject_holdout_path,
    require_cap,
    useful_scc_participation,
)


def _lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_manifest_filtering_selects_unique_baseline_timeout_frameworks(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "population-dev.json"
    manifest.write_text(
        json.dumps(
            {
                "partition": "development",
                "metric_config": {"subtracks": ["SE-ST", "SE-PR"]},
                "instances": [
                    {
                        "relative_path": "benchmarks/aba/hard.aba",
                        "assumptions": 3,
                        "atoms": 7,
                        "sorted_index": 0,
                    },
                    {
                        "relative_path": "benchmarks/aba/easy.aba",
                        "assumptions": 2,
                        "atoms": 5,
                        "sorted_index": 1,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    baseline = tmp_path / "baseline.md"
    baseline.write_text(
        "\n".join(
            (
                "| instance | subtrack | status | run1 | run2 | run3 |",
                "|---|---|---|---|---|---|",
                "| easy.aba | SE-PR | solved | 1 | 1 | 1 |",
                "| easy.aba | SE-ST | solved | 1 | 1 | 1 |",
                "| hard.aba | SE-PR | timeout | 10 | 10 | 10 |",
                "| hard.aba | SE-ST | timeout | 10 | 10 | 10 |",
            )
        ),
        encoding="utf-8",
    )

    selected = load_baseline_timeout_frameworks(manifest, baseline)

    assert [row.relative_path for row in selected] == ["benchmarks/aba/hard.aba"]
    assert selected[0].baseline_timeout_subtracks == ("SE-PR", "SE-ST")
    assert selected[0].manifest_assumptions == 3


def test_useful_sccs_are_exactly_inter_scc_attack_path_participants() -> None:
    a, b, c, isolated = (_lit(name) for name in ("a", "b", "c", "isolated"))
    cross = CollectiveAttack(frozenset({a, b}), c)
    local = CollectiveAttack(frozenset({isolated}), isolated)
    collective = CollectiveFramework(
        assumptions=frozenset({a, b, c, isolated}),
        attacks=frozenset({cross, local}),
        fact_attacked=frozenset(),
        components=(
            frozenset({a}),
            frozenset({b}),
            frozenset({c}),
            frozenset({isolated}),
        ),
        caps=ReferenceCaps(),
    )

    participation = useful_scc_participation(collective)

    assert participation.useful_scc_indices == (0, 1, 2)
    assert participation.inter_scc_attack_count == 1
    assert participation.cross_scc_collective_tail_count == 1
    assert participation.maximum_cross_scc_tail_width == 2


def test_residual_reduction_must_be_strict() -> None:
    assert has_strict_residual_reduction(10, 9)
    assert not has_strict_residual_reduction(10, 10)
    assert not has_strict_residual_reduction(10, 11)


def test_full_boundary_accounting_includes_every_stored_set_tail_and_m() -> None:
    a, b, c = (_lit(name) for name in ("a", "b", "c"))
    attack = CollectiveAttack(frozenset({a, b}), c)
    conditioned = ConditionedAttack(
        original=attack,
        residual_tail=frozenset({b}),
        mitigated=True,
    )
    boundary = ComponentBoundary(
        component=frozenset({b, c}),
        selected=frozenset({a}),
        attacked=frozenset({a, c}),
        defeated=frozenset({c}),
        provisionally_defeated=frozenset({b}),
        undefeated=frozenset({c}),
        undefeated_or_provisional=frozenset({b, c}),
        candidates=frozenset({c}),
        attacks=(conditioned,),
        mitigated=(conditioned,),
    )

    assert full_boundary_item_count(boundary) == 16


def test_cap_failure_is_fail_closed_and_names_the_structural_field() -> None:
    with pytest.raises(
        MeasurementFailure,
        match=r"branch_state_count cap exceeded: 65,537 > 65,536",
    ):
        require_cap("branch_state_count", 65_537, 65_536)


def test_holdout_path_is_rejected_before_access(tmp_path: Path) -> None:
    holdout = tmp_path / "population-holdout.json"

    with pytest.raises(MeasurementFailure, match="holdout path rejected"):
        reject_holdout_path(holdout)
