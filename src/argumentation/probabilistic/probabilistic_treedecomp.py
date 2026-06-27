"""Tree decomposition and exact grounded DP for probabilistic argumentation.

This module reuses the tree-decomposition setup used by Popescu & Wallner
(2024), but the executable DP is currently an adapted grounded-semantics
edge-tracking backend, not their full I/O/U witness-table algorithm.

Current native support is intentionally narrower than the paper:
grounded semantics on defeat-only probabilistic worlds where
`attacks == defeats` and there are no support relations. Richer worlds
are rejected by this backend.

**Known limitation:** The tree decomposition DP currently tracks full edge sets
and forgotten arguments in table keys, giving row count O(2^|defeats| * 2^|args|).
This provides zero asymptotic improvement over brute-force enumeration.
Effective for AFs with treewidth <= ~15. A principled redesign would track
only local state per bag, achieving the theoretical O(2^tw) bound.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from argumentation.core.dung import ArgumentationFramework
from argumentation.probabilistic.probabilistic_paper_td import (
    PaperTDArgumentWitness,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    PaperTDExactResult,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    PaperTDLabel,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    PaperTDRow,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    compute_paper_exact_extension_probability,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    paper_forget_rows,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    paper_introduce_rows,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    paper_join_rows,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    paper_leaf_rows,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
)
from argumentation.probabilistic.probabilistic_treedecomp_construction import (
    DPTableSummary,
    NiceTDNode,
    NiceTreeDecomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    TreeDecomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    _build_primal_graph,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    _nice_td_post_order,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    compute_tree_decomposition,
    estimate_treewidth,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    to_nice_tree_decomposition,
    validate_tree_decomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
)

if TYPE_CHECKING:
    from argumentation.probabilistic.probabilistic import ProbabilisticAF


def supports_exact_dp(
    praf: ProbabilisticAF,
    semantics: str,
) -> bool:
    """Return whether the current DP can evaluate this PrAF natively."""
    if semantics != "grounded":
        return False
    if getattr(praf, "supports", frozenset()):
        return False
    if praf.framework.attacks is not None and praf.framework.attacks != praf.framework.defeats:
        return False
    return True


# ===================================================================
# Data structures
# ===================================================================

@dataclass(frozen=True)
class GroundedOutcomeProbabilities:
    """Probability mass for one argument's grounded status outcomes."""

    accepted: float
    rejected: float
    undecided: float
    absent: float


@dataclass(frozen=True)
class GroundedOutcomeWitness:
    """One realized subworld witnessing an argument outcome."""

    argument: str
    outcome: str
    present_arguments: frozenset[str]
    active_defeats: frozenset[tuple[str, str]]
    probability: float


@dataclass(frozen=True)
class GroundedOutcomeWitnesses:
    """Example realized subworlds for each possible grounded outcome."""

    accepted: GroundedOutcomeWitness | None = None
    rejected: GroundedOutcomeWitness | None = None
    undecided: GroundedOutcomeWitness | None = None
    absent: GroundedOutcomeWitness | None = None


@dataclass(frozen=True)
class ExactDPDiagnostics:
    """Acceptance probabilities plus auditable table-level DP diagnostics."""

    acceptance_probs: dict[str, float]
    status_probabilities: dict[str, GroundedOutcomeProbabilities]
    status_witnesses: dict[str, GroundedOutcomeWitnesses]
    table_summaries: tuple[DPTableSummary, ...]
    treewidth: int
    node_count: int
    component_count: int
    root_table_rows: int
    root_probability_mass: float


def compute_exact_dp(
    praf: ProbabilisticAF,
    semantics: str = "grounded",
) -> dict[str, float]:
    """Exact grounded acceptance via the adapted edge-tracking TD backend.

    For grounded semantics, the current backend processes a nice tree
    decomposition bottom-up while tracking realized edge configurations and
    present forgotten arguments. It then computes the grounded fixpoint for
    each root row. This is exact for the supported defeat-only constellation
    PrAFs, but it is not the full Popescu & Wallner I/O/U witness-table DP.

    Unsupported semantics or relation structures are rejected.

    Known limitation: table keys include accumulated edge configurations and
    forgotten arguments, so this implementation does not yet achieve the
    paper's treewidth-sensitive asymptotic bound.
    """
    if not supports_exact_dp(praf, semantics):
        raise ValueError(
            "exact_dp only supports grounded semantics on defeat-only probabilistic frameworks"
        )

    return _compute_grounded_dp(praf)


def compute_exact_dp_with_diagnostics(
    praf: ProbabilisticAF,
    semantics: str = "grounded",
) -> ExactDPDiagnostics:
    """Exact grounded acceptance with diagnostics for the current DP tables."""
    if not supports_exact_dp(praf, semantics):
        raise ValueError(
            "exact_dp only supports grounded semantics on defeat-only probabilistic frameworks"
        )

    return _compute_grounded_dp_with_diagnostics(praf)


# ===================================================================
# Grounded-semantics tree-decomposition DP
# Reuses Popescu & Wallner-style nice tree decompositions, but the executable
# grounded backend below is edge-tracking rather than their I/O/U witness DP.
#
# Adapted for grounded semantics: instead of tracking I/O/U labels
# (which enumerate ALL complete labellings including non-grounded),
# we track the presence/absence of bag arguments and the active edge
# configuration. The grounded labelling is computed via fixpoint at
# forget time. This ensures exactly one labelling per subworld.
#
# Per research-popescu-pacc-report.md: P_ext = P_acc for grounded
# (unique extension per subframework).
# ===================================================================

# Row key: (bag_state, active_edges, present_forgotten) → probability.
#   bag_state: tuple of (arg, present:bool) pairs for args in bag.
#   active_edges: frozenset of realized defeat edges (accumulated).
#   present_forgotten: frozenset of forgotten args that were present.
_RowKey = tuple[
    tuple[tuple[str, bool], ...],      # bag_state
    frozenset[tuple[str, str]],        # active_edges
    frozenset[str],                    # present_forgotten
]
DPTable = dict[_RowKey, float]


@dataclass(frozen=True)
class _GroundedDPComponentResult:
    acceptance_probs: dict[str, float]
    status_probabilities: dict[str, GroundedOutcomeProbabilities]
    status_witnesses: dict[str, GroundedOutcomeWitnesses]
    table_summaries: tuple[DPTableSummary, ...]
    treewidth: int
    node_count: int
    root_table_rows: int
    root_probability_mass: float


def _make_key(
    bag_state: dict[str, bool],
    active_edges: frozenset[tuple[str, str]],
    present_forgotten: frozenset[str],
) -> _RowKey:
    """Build an immutable table key."""
    state_tuple = tuple(sorted(bag_state.items()))
    return (state_tuple, active_edges, present_forgotten)


def _add_to_table(
    table: DPTable,
    bag_state: dict[str, bool],
    active_edges: frozenset[tuple[str, str]],
    present_forgotten: frozenset[str],
    prob: float,
) -> None:
    """Add probability to a table row, creating it if needed."""
    if prob < 1e-18:
        return
    key = _make_key(bag_state, active_edges, present_forgotten)
    table[key] = table.get(key, 0.0) + prob


def _compute_grounded_dp(praf: ProbabilisticAF) -> dict[str, float]:
    """Tree-decomposition DP for grounded semantics.

    Per Popescu & Wallner (2024, Algorithms 1-3): processes a nice tree
    decomposition bottom-up with I/O/U labelling tables and witness
    mechanism.

    Per Hunter & Thimm (2017, Prop 18): acceptance probability separates
    over connected components. Each component is solved independently.

    For grounded semantics, each subframework has exactly one grounded
    extension (Dung 1995, Theorem 25), so P_ext = P_acc.
    """
    return _compute_grounded_dp_with_diagnostics(praf).acceptance_probs


def _compute_grounded_dp_with_diagnostics(praf: ProbabilisticAF) -> ExactDPDiagnostics:
    af = praf.framework
    args_list = sorted(af.arguments)

    if not args_list:
        return ExactDPDiagnostics(
            acceptance_probs={},
            status_probabilities={},
            status_witnesses={},
            table_summaries=(),
            treewidth=0,
            node_count=0,
            component_count=0,
            root_table_rows=0,
            root_probability_mass=1.0,
        )

    from argumentation.probabilistic.probabilistic import _expectation

    p_arg: dict[str, float] = {
        a: _expectation(praf.p_args[a]) for a in af.arguments
    }
    p_defeat: dict[tuple[str, str], float] = {
        d: _expectation(praf.p_defeats[d]) for d in af.defeats
    }

    from argumentation.probabilistic.probabilistic_components import connected_components
    components = connected_components(praf)

    acceptance: dict[str, float] = {}
    status_probabilities: dict[str, GroundedOutcomeProbabilities] = {}
    status_witnesses: dict[str, GroundedOutcomeWitnesses] = {}
    summaries: list[DPTableSummary] = []
    treewidth = 0
    node_count = 0
    root_table_rows = 0
    root_probability_mass = 1.0

    for component_index, comp_args in enumerate(components):
        comp_defeats = frozenset(
            (f, t) for f, t in af.defeats
            if f in comp_args and t in comp_args
        )
        comp_af = ArgumentationFramework(
            arguments=frozenset(comp_args),
            defeats=comp_defeats,
            attacks=(
                frozenset(
                    (f, t) for f, t in af.attacks
                    if f in comp_args and t in comp_args
                ) if af.attacks is not None else None
            ),
        )
        comp_result = _compute_grounded_dp_component_result(
            comp_af, p_arg, p_defeat, component_index,
        )
        acceptance.update(comp_result.acceptance_probs)
        status_probabilities.update(comp_result.status_probabilities)
        status_witnesses.update(comp_result.status_witnesses)
        summaries.extend(comp_result.table_summaries)
        treewidth = max(treewidth, comp_result.treewidth)
        node_count += comp_result.node_count
        root_table_rows += comp_result.root_table_rows
        root_probability_mass *= comp_result.root_probability_mass

    return ExactDPDiagnostics(
        acceptance_probs=acceptance,
        status_probabilities=status_probabilities,
        status_witnesses=status_witnesses,
        table_summaries=tuple(summaries),
        treewidth=treewidth,
        node_count=node_count,
        component_count=len(components),
        root_table_rows=root_table_rows,
        root_probability_mass=root_probability_mass,
    )


def _compute_grounded_dp_component_result(
    af: ArgumentationFramework,
    p_arg: dict[str, float],
    p_defeat: dict[tuple[str, str], float],
    component_index: int,
) -> _GroundedDPComponentResult:
    """Edge-tracking DP for one connected component (grounded semantics).

    Instead of I/O/U labels, tracks which defeat edges are active in each
    subworld. The grounded labelling is computed via fixpoint at forget
    time. This guarantees exactly one labelling per subworld, matching
    the brute-force enumeration.

    Per Popescu & Wallner (2024, Algorithms 1-3): processes a nice tree
    decomposition bottom-up. Adapted for grounded: edge configurations
    replace I/O/U partial labellings.
    """
    args_list = sorted(af.arguments)

    if not args_list:
        return _GroundedDPComponentResult({}, {}, {}, (), 0, 0, 0, 1.0)

    defeat_set: set[tuple[str, str]] = set(af.defeats)

    # Compute tree decomposition and nice TD.
    td = compute_tree_decomposition(af)
    ntd = to_nice_tree_decomposition(td)

    # Post-order traversal.
    post_order: list[int] = []
    visit_stack: list[tuple[int, bool]] = [(ntd.root, False)]
    while visit_stack:
        nid, processed = visit_stack.pop()
        if processed:
            post_order.append(nid)
            continue
        visit_stack.append((nid, True))
        node = ntd.nodes[nid]
        for child in reversed(node.children):
            visit_stack.append((child, False))

    # Assign edge ownership to prevent double-counting at joins.
    # Each edge's P_D is factored at exactly one introduce node.
    owned_edges: set[tuple[str, str]] = set()
    introduce_owns_edges: dict[int, set[tuple[str, str]]] = {}

    for nid in post_order:
        node = ntd.nodes[nid]
        if node.node_type == "introduce":
            v = node.introduced
            assert v is not None
            child_bag = node.bag - {v}
            node_edges: set[tuple[str, str]] = set()
            # Edges between v and existing bag members.
            for edge in defeat_set:
                src, tgt = edge
                if src == v and tgt in child_bag and edge not in owned_edges:
                    node_edges.add(edge)
                    owned_edges.add(edge)
                elif tgt == v and src in child_bag and edge not in owned_edges:
                    node_edges.add(edge)
                    owned_edges.add(edge)
                elif src == v and tgt == v and edge not in owned_edges:
                    node_edges.add(edge)
                    owned_edges.add(edge)
            introduce_owns_edges[nid] = node_edges

    # DP tables.
    tables: dict[int, DPTable] = {}
    table_summaries: list[DPTableSummary] = []

    for nid in post_order:
        node = ntd.nodes[nid]

        if node.node_type == "leaf":
            tables[nid] = {
                _make_key({}, frozenset(), frozenset()): 1.0
            }

        elif node.node_type == "introduce":
            tables[nid] = _dp_introduce(
                node, tables[node.children[0]], p_defeat,
                introduce_owns_edges[nid],
            )

        elif node.node_type == "forget":
            tables[nid] = _dp_forget(
                node, tables[node.children[0]], p_arg,
            )

        elif node.node_type == "join":
            tables[nid] = _dp_join(
                node, tables[node.children[0]], tables[node.children[1]],
            )

        table = tables[nid]
        table_summaries.append(
            DPTableSummary(
                component_index=component_index,
                node_id=nid,
                node_type=node.node_type,
                bag=node.bag,
                row_count=len(table),
                probability_mass=sum(table.values()),
            )
        )

        # Free child tables.
        for child in node.children:
            if child in tables:
                del tables[child]

    # At the root, compute grounded extensions and accumulate acceptance.
    # Each row has present_forgotten (all present args) and active_edges.
    # Run the grounded fixpoint on each configuration.
    acceptance: dict[str, float] = {a: 0.0 for a in args_list}
    status_totals: dict[str, dict[str, float]] = {
        a: {"accepted": 0.0, "rejected": 0.0, "undecided": 0.0, "absent": 0.0}
        for a in args_list
    }
    witness_rows: dict[str, dict[str, GroundedOutcomeWitness]] = {
        a: {} for a in args_list
    }
    root_table = tables.get(ntd.root, {})
    root_probability_mass = sum(root_table.values())
    for (_, edges_fs, present_fs), prob in root_table.items():
        if prob < 1e-18:
            continue
        # Compute grounded extension for this subworld.
        present = set(present_fs)
        sub_attackers: dict[str, set[str]] = {a: set() for a in present}
        for src, tgt in edges_fs:
            if src in present and tgt in present:
                sub_attackers[tgt].add(src)
        # Fixpoint (Dung 1995, Definition 20).
        labels: dict[str, str] = {a: "U" for a in present}
        changed = True
        while changed:
            changed = False
            for a in present:
                if labels[a] != "U":
                    continue
                atts = sub_attackers[a]
                if all(labels[att] == "O" for att in atts):
                    labels[a] = "I"
                    changed = True
                elif any(labels[att] == "I" for att in atts):
                    labels[a] = "O"
                    changed = True
        for a in args_list:
            if a not in present:
                outcome = "absent"
            elif labels[a] == "I":
                outcome = "accepted"
                acceptance[a] += prob
            elif labels[a] == "O":
                outcome = "rejected"
            else:
                outcome = "undecided"

            status_totals[a][outcome] += prob
            if outcome not in witness_rows[a]:
                witness_rows[a][outcome] = GroundedOutcomeWitness(
                    argument=a,
                    outcome=outcome,
                    present_arguments=frozenset(present),
                    active_defeats=edges_fs,
                    probability=prob,
                )

    status_probabilities = {
        a: GroundedOutcomeProbabilities(
            accepted=status_totals[a]["accepted"],
            rejected=status_totals[a]["rejected"],
            undecided=status_totals[a]["undecided"],
            absent=status_totals[a]["absent"],
        )
        for a in args_list
    }
    status_witnesses = {
        a: GroundedOutcomeWitnesses(
            accepted=witness_rows[a].get("accepted"),
            rejected=witness_rows[a].get("rejected"),
            undecided=witness_rows[a].get("undecided"),
            absent=witness_rows[a].get("absent"),
        )
        for a in args_list
    }

    return _GroundedDPComponentResult(
        acceptance_probs=acceptance,
        status_probabilities=status_probabilities,
        status_witnesses=status_witnesses,
        table_summaries=tuple(table_summaries),
        treewidth=td.width,
        node_count=len(ntd.nodes),
        root_table_rows=len(root_table),
        root_probability_mass=root_probability_mass,
    )



def _dp_introduce(
    node: NiceTDNode,
    child_table: DPTable,
    p_defeat: dict[tuple[str, str], float],
    owns_edges: set[tuple[str, str]],
) -> DPTable:
    """Introduce v: add v to bag, branch on owned edge presence.

    For each child row, generate rows with v present or absent.
    For v present, branch on each owned edge's presence/absence.
    P_A is NOT applied here (deferred to forget time).
    """
    v = node.introduced
    assert v is not None
    new_table: DPTable = {}

    # Owned edges involving v and current bag members.
    owned_list = sorted(owns_edges)
    n_owned = len(owned_list)

    for (state_tuple, edges_fs, present_forgotten), prob in child_table.items():
        if prob < 1e-18:
            continue
        bag_state = dict(state_tuple)

        # === v absent ===
        new_state = dict(bag_state)
        new_state[v] = False
        _add_to_table(new_table, new_state, edges_fs, present_forgotten, prob)

        # === v present ===
        # Branch on owned edges.
        for edge_mask in range(1 << n_owned):
            p_edges = 1.0
            new_edges = set(edges_fs)
            for ei, edge in enumerate(owned_list):
                if edge_mask & (1 << ei):
                    p_edges *= p_defeat[edge]
                    new_edges.add(edge)
                else:
                    p_edges *= (1.0 - p_defeat[edge])

            if p_edges < 1e-18:
                continue

            new_state_p = dict(bag_state)
            new_state_p[v] = True
            _add_to_table(
                new_table, new_state_p, frozenset(new_edges),
                present_forgotten, prob * p_edges,
            )

    return new_table


def _dp_forget(
    node: NiceTDNode,
    child_table: DPTable,
    p_arg: dict[str, float],
) -> DPTable:
    """Forget v: apply P_A, move v from bag to forgotten set.

    Grounded label computation is deferred to the root.
    """
    v = node.forgotten
    assert v is not None
    new_table: DPTable = {}

    for (state_tuple, edges_fs, present_forgotten), prob in child_table.items():
        if prob < 1e-18:
            continue
        bag_state = dict(state_tuple)
        v_present = bag_state.get(v, False)

        # Apply P_A(v) — each argument forgotten exactly once.
        pa_v = p_arg.get(v, 1.0)
        if v_present:
            adjusted_prob = prob * pa_v
        else:
            adjusted_prob = prob * (1.0 - pa_v)

        if adjusted_prob < 1e-18:
            continue

        # Move v from bag to forgotten tracking.
        new_state = {a: p for a, p in bag_state.items() if a != v}
        new_present_forgotten = (
            present_forgotten | {v} if v_present else present_forgotten
        )

        _add_to_table(
            new_table, new_state, edges_fs,
            new_present_forgotten, adjusted_prob,
        )

    return new_table


def _dp_join(
    node: NiceTDNode,
    left_table: DPTable,
    right_table: DPTable,
) -> DPTable:
    """Join: combine rows with matching bag states.

    Per Popescu & Wallner (2024, p.6): compatible rows are combined.
    Probabilities multiply, edge sets and accepted sets are unioned.
    """
    new_table: DPTable = {}

    # Index right table by bag_state for fast lookup.
    right_by_state: dict[
        tuple[tuple[str, bool], ...],
        list[tuple[frozenset[tuple[str, str]], frozenset[str], float]],
    ] = {}
    for (state_tuple, edges_fs, pf), prob in right_table.items():
        if prob < 1e-18:
            continue
        right_by_state.setdefault(state_tuple, []).append(
            (edges_fs, pf, prob)
        )

    for (left_state, left_edges, left_pf), left_prob in left_table.items():
        if left_prob < 1e-18:
            continue
        if left_state not in right_by_state:
            continue
        for right_edges, right_pf, right_prob in right_by_state[left_state]:
            combined_prob = left_prob * right_prob
            combined_edges = left_edges | right_edges
            combined_pf = left_pf | right_pf
            key = (left_state, combined_edges, combined_pf)
            new_table[key] = new_table.get(key, 0.0) + combined_prob

    return new_table
