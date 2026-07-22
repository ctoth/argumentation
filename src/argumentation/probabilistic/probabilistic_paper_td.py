"""Paper-faithful I/O/U witness-table tree-decomposition DP.

Implements the Popescu & Wallner (2024) complete-semantics extension-probability
dynamic program over a nice tree decomposition using I/O/U-labelled rows with
witnesses. Construction machinery is imported from
`probabilistic_treedecomp_construction`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product
from typing import TYPE_CHECKING

from argumentation.core.dung import ArgumentationFramework
from argumentation.probabilistic.probabilistic_treedecomp_construction import (
    DPTableSummary,
    _nice_td_post_order,
    compute_tree_decomposition,
    to_nice_tree_decomposition,
)

if TYPE_CHECKING:
    from argumentation.probabilistic.probabilistic import ProbabilisticAF


@dataclass(frozen=True)
class PaperTDExactResult:
    """Exact complete-extension probability from the paper-style TD evaluator."""

    extension_probability: float
    table_summaries: tuple[DPTableSummary, ...]
    argument_witnesses: dict[str, PaperTDArgumentWitness]
    treewidth: int
    node_count: int
    root_table_rows: int
    root_probability_mass: float
    backend: str = "popescu_wallner_iou_witness_td"


@dataclass(frozen=True)
class PaperTDArgumentWitness:
    """Lifted label and witness metadata for one queried extension result."""

    argument: str
    label: PaperTDLabel
    witnesses: frozenset[str]


class PaperTDLabel(Enum):
    """The I/O/U labels used by Popescu and Wallner's TD tables."""

    IN = "I"
    OUT = "O"
    UNDECIDED = "U"


@dataclass
class PaperTDRow:
    """One row `(s, w, p)` in the paper-faithful TD dynamic program.

    Popescu and Wallner 2024, p.590 defines a row as a structure `s`, a
    witness `w`, and a probability `p`. The structure is represented here by
    the visible subframework components and its partial labelling.
    """

    present_arguments: frozenset[str]
    active_defeats: frozenset[tuple[str, str]]
    labels: dict[str, PaperTDLabel]
    witnesses: dict[str, str]
    probability: float


def paper_leaf_rows() -> tuple[PaperTDRow, ...]:
    """Return the unit table for a nice-TD leaf node.

    Popescu and Wallner 2024, Algorithm 1 line 4 initializes a leaf table with
    the empty structure, empty witness, and probability 1.
    """
    return (
        PaperTDRow(
            present_arguments=frozenset(),
            active_defeats=frozenset(),
            labels={},
            witnesses={},
            probability=1.0,
        ),
    )


def paper_introduce_rows(
    child_rows: tuple[PaperTDRow, ...],
    *,
    argument: str,
    bag: frozenset[str],
    all_defeats: frozenset[tuple[str, str]],
    p_argument: float,
    p_defeats: dict[tuple[str, str], float],
    queried_in: frozenset[str],
) -> tuple[PaperTDRow, ...]:
    """Apply the paper TD introduce transition for one argument.

    This implements the first narrow part of Popescu and Wallner 2024,
    Algorithm 2: branch on whether the introduced argument is present, branch
    on incident defeats when present, label resulting structures, update simple
    OUT/UNDEC witnesses, and filter rows that violate required in-arguments.
    """
    introduced_rows: list[PaperTDRow] = []
    for row in child_rows:
        if p_argument != 1.0:
            absent_row = PaperTDRow(
                present_arguments=row.present_arguments,
                active_defeats=row.active_defeats,
                labels=dict(row.labels),
                witnesses=dict(row.witnesses),
                probability=row.probability * (1.0 - p_argument),
            )
            if argument not in queried_in and _paper_td_accepts_required_in(
                absent_row, queried_in
            ):
                introduced_rows.append(absent_row)

        present_arguments = row.present_arguments | frozenset({argument})
        incident_defeats = tuple(
            sorted(
                defeat
                for defeat in all_defeats
                if argument in defeat
                and defeat[0] in present_arguments
                and defeat[1] in present_arguments
            )
        )
        for selected in product((False, True), repeat=len(incident_defeats)):
            active_defeats = set(row.active_defeats)
            p_edges = 1.0
            for included, defeat in zip(selected, incident_defeats, strict=True):
                probability = p_defeats.get(defeat, 1.0)
                if included:
                    active_defeats.add(defeat)
                    p_edges *= probability
                else:
                    p_edges *= 1.0 - probability

            if p_edges < 1e-18:
                continue

            for labels in _paper_td_introduced_labelings(
                argument,
                frozenset(active_defeats),
                prior_labels=row.labels,
                queried_in=queried_in,
            ):
                witnesses = _paper_td_update_witnesses(
                    labels,
                    frozenset(active_defeats),
                    row.witnesses,
                )
                present_row = PaperTDRow(
                    present_arguments=present_arguments,
                    active_defeats=frozenset(active_defeats),
                    labels=labels,
                    witnesses=witnesses,
                    probability=row.probability * p_argument * p_edges,
                )
                if _paper_td_accepts_required_in(present_row, queried_in):
                    introduced_rows.append(present_row)

    return tuple(
        sorted(
            _paper_td_merge_rows(introduced_rows),
            key=_paper_td_row_sort_key,
        )
    )


def paper_forget_rows(
    child_rows: tuple[PaperTDRow, ...],
    *,
    argument: str,
    exact_extension: frozenset[str] | None = None,
) -> tuple[PaperTDRow, ...]:
    """Apply the paper TD forget transition for one argument.

    Popescu and Wallner 2024, Algorithm 3 filters rows whose forgotten
    out/undecided label lacks a witness, then removes the forgotten argument,
    incident defeats, and witness facts from the row state.
    """
    forgotten_rows: list[PaperTDRow] = []
    for row in child_rows:
        label = row.labels.get(argument)
        if exact_extension is not None:
            if argument in exact_extension and label is not PaperTDLabel.IN:
                continue
            if argument not in exact_extension and label is PaperTDLabel.IN:
                continue
        if not _paper_td_forget_accepts(row, argument):
            continue

        labels = {
            row_argument: row_label
            for row_argument, row_label in row.labels.items()
            if row_argument != argument
        }
        witnesses = {
            row_argument: witness
            for row_argument, witness in row.witnesses.items()
            if row_argument != argument
        }
        forgotten_rows.append(
            PaperTDRow(
                present_arguments=row.present_arguments - frozenset({argument}),
                active_defeats=frozenset(
                    defeat for defeat in row.active_defeats if argument not in defeat
                ),
                labels=labels,
                witnesses=witnesses,
                probability=row.probability,
            )
        )

    return tuple(
        sorted(
            _paper_td_merge_rows(forgotten_rows),
            key=_paper_td_row_sort_key,
        )
    )


def paper_join_rows(
    left_rows: tuple[PaperTDRow, ...],
    right_rows: tuple[PaperTDRow, ...],
    *,
    bag: frozenset[str],
    p_arguments: dict[str, float],
    p_defeats: dict[tuple[str, str], float],
    all_defeats: frozenset[tuple[str, str]],
) -> tuple[PaperTDRow, ...]:
    """Apply the paper TD join transition for two child tables.

    Popescu and Wallner 2024, Algorithm 4 combines compatible rows and divides
    out the probability mass common to both child tables for the current bag.
    """
    joined_rows: list[PaperTDRow] = []
    right_by_structure: dict[
        tuple[
            frozenset[str],
            frozenset[tuple[str, str]],
            tuple[tuple[str, PaperTDLabel], ...],
        ],
        list[PaperTDRow],
    ] = {}
    for right in right_rows:
        right_by_structure.setdefault(_paper_td_structure_key(right), []).append(right)

    for left in left_rows:
        for right in right_by_structure.get(_paper_td_structure_key(left), ()):
            witnesses = dict(left.witnesses)
            for argument, witness in right.witnesses.items():
                witnesses.setdefault(argument, witness)

            common_probability = _paper_td_common_probability(
                left,
                bag=bag,
                p_arguments=p_arguments,
                p_defeats=p_defeats,
                all_defeats=all_defeats,
            )
            if common_probability < 1e-18:
                continue
            joined_rows.append(
                PaperTDRow(
                    present_arguments=left.present_arguments,
                    active_defeats=left.active_defeats,
                    labels=dict(left.labels),
                    witnesses=witnesses,
                    probability=left.probability
                    * right.probability
                    / common_probability,
                )
            )

    return tuple(
        sorted(
            _paper_td_merge_rows(joined_rows),
            key=_paper_td_row_sort_key,
        )
    )


def compute_paper_exact_extension_probability(
    praf: ProbabilisticAF,
    *,
    queried_set: frozenset[str],
    semantics: str = "complete",
) -> PaperTDExactResult:
    """Compute exact `P-Ext` for complete semantics via paper-style TD rows.

    Popescu and Wallner 2024, Algorithm 1 evaluates a nice tree decomposition
    bottom-up using I/O/U-labelled rows with witnesses. This public surface is
    intentionally scoped to the paper's complete-semantics extension query.
    """
    if semantics != "complete":
        raise ValueError(
            "paper TD exact extension probability currently supports complete semantics"
        )
    if getattr(praf, "supports", frozenset()):
        raise ValueError(
            "paper TD exact extension probability does not support support relations"
        )
    if (
        praf.framework.attacks is not None
        and praf.framework.attacks != praf.framework.defeats
    ):
        raise ValueError(
            "paper TD exact extension probability requires attacks == defeats"
        )

    unknown = sorted(queried_set - praf.framework.arguments)
    if unknown:
        raise ValueError(f"queried_set contains unknown arguments: {unknown!r}")

    from argumentation.probabilistic.probabilistic import _expectation

    p_arguments = {
        argument: _expectation(praf.p_args[argument])
        for argument in praf.framework.arguments
    }
    p_defeats = {
        defeat: _expectation(praf.p_defeats[defeat])
        for defeat in praf.framework.defeats
    }

    td = compute_tree_decomposition(praf.framework)
    ntd = to_nice_tree_decomposition(td)
    post_order = _nice_td_post_order(ntd)
    tables: dict[int, tuple[PaperTDRow, ...]] = {}
    summaries: list[DPTableSummary] = []

    for node_id in post_order:
        node = ntd.nodes[node_id]
        if node.node_type == "leaf":
            table = paper_leaf_rows()
        elif node.node_type == "introduce":
            assert node.introduced is not None
            table = paper_introduce_rows(
                tables[node.children[0]],
                argument=node.introduced,
                bag=node.bag,
                all_defeats=praf.framework.defeats,
                p_argument=p_arguments[node.introduced],
                p_defeats=p_defeats,
                queried_in=queried_set,
            )
        elif node.node_type == "forget":
            assert node.forgotten is not None
            table = paper_forget_rows(
                tables[node.children[0]],
                argument=node.forgotten,
                exact_extension=queried_set,
            )
        elif node.node_type == "join":
            table = paper_join_rows(
                tables[node.children[0]],
                tables[node.children[1]],
                bag=node.bag,
                p_arguments=p_arguments,
                p_defeats=p_defeats,
                all_defeats=praf.framework.defeats,
            )
        else:
            raise ValueError(f"Unknown nice TD node type: {node.node_type!r}")

        tables[node_id] = table
        summaries.append(
            DPTableSummary(
                component_index=0,
                node_id=node_id,
                node_type=node.node_type,
                bag=node.bag,
                row_count=len(table),
                probability_mass=sum(row.probability for row in table),
            )
        )
        for child in node.children:
            tables.pop(child, None)

    root_table = tables.get(ntd.root, ())
    root_probability_mass = sum(row.probability for row in root_table)
    return PaperTDExactResult(
        extension_probability=root_probability_mass,
        table_summaries=tuple(summaries),
        argument_witnesses=_paper_td_lift_argument_witnesses(
            praf.framework,
            queried_set,
        ),
        treewidth=td.width,
        node_count=len(ntd.nodes),
        root_table_rows=len(root_table),
        root_probability_mass=root_probability_mass,
    )


def _paper_td_lift_argument_witnesses(
    framework: ArgumentationFramework,
    queried_set: frozenset[str],
) -> dict[str, PaperTDArgumentWitness]:
    witnesses: dict[str, PaperTDArgumentWitness] = {}
    for argument in sorted(framework.arguments):
        if argument in queried_set:
            witnesses[argument] = PaperTDArgumentWitness(
                argument=argument,
                label=PaperTDLabel.IN,
                witnesses=frozenset(),
            )
            continue
        out_witnesses = frozenset(
            attacker
            for attacker, target in framework.defeats
            if target == argument and attacker in queried_set
        )
        if out_witnesses:
            witnesses[argument] = PaperTDArgumentWitness(
                argument=argument,
                label=PaperTDLabel.OUT,
                witnesses=out_witnesses,
            )
        else:
            witnesses[argument] = PaperTDArgumentWitness(
                argument=argument,
                label=PaperTDLabel.UNDECIDED,
                witnesses=frozenset(),
            )
    return witnesses


def _paper_td_accepts_required_in(
    row: PaperTDRow,
    queried_in: frozenset[str],
) -> bool:
    return all(
        argument not in row.labels or row.labels[argument] is PaperTDLabel.IN
        for argument in queried_in
    )


def _paper_td_introduced_labelings(
    argument: str,
    active_defeats: frozenset[tuple[str, str]],
    *,
    prior_labels: dict[str, PaperTDLabel],
    queried_in: frozenset[str],
) -> tuple[dict[str, PaperTDLabel], ...]:
    choices = (
        (PaperTDLabel.IN,)
        if argument in queried_in
        else (PaperTDLabel.IN, PaperTDLabel.OUT, PaperTDLabel.UNDECIDED)
    )
    rows: list[dict[str, PaperTDLabel]] = []
    for choice in choices:
        labels = dict(prior_labels)
        labels[argument] = choice
        if choice is PaperTDLabel.IN and not _paper_td_conflict_free_in_label(
            argument,
            labels,
            active_defeats,
        ):
            continue
        rows.append(labels)
    return tuple(rows)


def _paper_td_conflict_free_in_label(
    argument: str,
    labels: dict[str, PaperTDLabel],
    active_defeats: frozenset[tuple[str, str]],
) -> bool:
    for source, target in active_defeats:
        if source == argument and labels.get(target) is PaperTDLabel.IN:
            return False
        if target == argument and labels.get(source) is PaperTDLabel.IN:
            return False
    return True


def _paper_td_forget_accepts(row: PaperTDRow, argument: str) -> bool:
    label = row.labels.get(argument)
    if label is None:
        return True
    if label is PaperTDLabel.IN:
        return all(
            labels_attacker is PaperTDLabel.OUT
            for source, target in row.active_defeats
            if target == argument
            for labels_attacker in (row.labels.get(source),)
        )
    if label is PaperTDLabel.OUT:
        return argument in row.witnesses
    return argument in row.witnesses and not any(
        target == argument and row.labels.get(source) is PaperTDLabel.IN
        for source, target in row.active_defeats
    )


def _paper_td_update_witnesses(
    labels: dict[str, PaperTDLabel],
    active_defeats: frozenset[tuple[str, str]],
    prior_witnesses: dict[str, str],
) -> dict[str, str]:
    witnesses = dict(prior_witnesses)
    for argument, label in sorted(labels.items()):
        if label is PaperTDLabel.IN:
            witnesses.pop(argument, None)
            continue
        if argument in witnesses:
            continue
        if label is PaperTDLabel.OUT:
            attacker = next(
                (
                    source
                    for source, target in sorted(active_defeats)
                    if target == argument and labels.get(source) is PaperTDLabel.IN
                ),
                None,
            )
            if attacker is not None:
                witnesses[argument] = attacker
        elif label is PaperTDLabel.UNDECIDED:
            attacker = next(
                (
                    source
                    for source, target in sorted(active_defeats)
                    if target == argument
                    and labels.get(source) is PaperTDLabel.UNDECIDED
                ),
                None,
            )
            if attacker is not None:
                witnesses[argument] = attacker
    return witnesses


def _paper_td_structure_key(
    row: PaperTDRow,
) -> tuple[
    frozenset[str],
    frozenset[tuple[str, str]],
    tuple[tuple[str, PaperTDLabel], ...],
]:
    return (
        row.present_arguments,
        row.active_defeats,
        tuple(sorted(row.labels.items())),
    )


def _paper_td_common_probability(
    row: PaperTDRow,
    *,
    bag: frozenset[str],
    p_arguments: dict[str, float],
    p_defeats: dict[tuple[str, str], float],
    all_defeats: frozenset[tuple[str, str]],
) -> float:
    probability = 1.0
    for argument in sorted(bag):
        p_argument = p_arguments.get(argument, 1.0)
        if argument in row.present_arguments:
            probability *= p_argument
        else:
            probability *= 1.0 - p_argument

    bag_defeats = sorted(
        defeat for defeat in all_defeats if defeat[0] in bag and defeat[1] in bag
    )
    for defeat in bag_defeats:
        p_defeat = p_defeats.get(defeat, 1.0)
        if defeat in row.active_defeats:
            probability *= p_defeat
        else:
            probability *= 1.0 - p_defeat
    return probability


def _paper_td_merge_rows(rows: list[PaperTDRow]) -> tuple[PaperTDRow, ...]:
    merged: dict[
        tuple[
            frozenset[str],
            frozenset[tuple[str, str]],
            tuple[tuple[str, PaperTDLabel], ...],
            tuple[tuple[str, str], ...],
        ],
        PaperTDRow,
    ] = {}
    for row in rows:
        key = (
            row.present_arguments,
            row.active_defeats,
            tuple(sorted(row.labels.items())),
            tuple(sorted(row.witnesses.items())),
        )
        if key in merged:
            merged[key].probability += row.probability
        else:
            merged[key] = PaperTDRow(
                present_arguments=row.present_arguments,
                active_defeats=row.active_defeats,
                labels=dict(row.labels),
                witnesses=dict(row.witnesses),
                probability=row.probability,
            )
    return tuple(merged.values())


def _paper_td_row_sort_key(
    row: PaperTDRow,
) -> tuple[
    tuple[str, ...],
    tuple[tuple[str, str], ...],
    tuple[tuple[str, str], ...],
    tuple[tuple[str, str], ...],
]:
    return (
        tuple(sorted(row.present_arguments)),
        tuple(sorted(row.active_defeats)),
        tuple(
            sorted((argument, label.value) for argument, label in row.labels.items())
        ),
        tuple(sorted(row.witnesses.items())),
    )
