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

from dataclasses import dataclass, field
from enum import Enum
from itertools import product
from typing import TYPE_CHECKING

from argumentation.labelling import Label, Labelling
from argumentation.dung import ArgumentationFramework

if TYPE_CHECKING:
    from argumentation.probabilistic import ProbabilisticAF


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

@dataclass
class TreeDecomposition:
    """Tree decomposition of an AF's primal graph.

    Per Popescu & Wallner (2024, p.4-5): bags satisfy
    - Every argument appears in at least one bag
    - For every attack, some bag contains both endpoints
    - Bags containing the same argument form a connected subtree
    """

    bags: dict[int, frozenset[str]]  # node_id -> set of arguments
    adj: dict[int, set[int]]  # adjacency list for the tree
    root: int
    width: int  # max bag size - 1


@dataclass
class NiceTDNode:
    """A node in a nice tree decomposition.

    Per Popescu & Wallner (2024, p.5): four node types.
    """

    bag: frozenset[str]
    node_type: str  # "leaf", "introduce", "forget", "join"
    introduced: str | None = None  # for introduce nodes
    forgotten: str | None = None  # for forget nodes
    children: list[int] = field(default_factory=list)


@dataclass
class NiceTreeDecomposition:
    """Nice TD with typed nodes.

    Per Popescu & Wallner (2024, p.5): leaf (empty bag), introduce (add one),
    forget (remove one), join (two children with identical bags).
    """

    nodes: dict[int, NiceTDNode]
    root: int


@dataclass(frozen=True)
class DPTableSummary:
    """Summary of one dynamic-programming table built for a nice TD node."""

    component_index: int
    node_id: int
    node_type: str
    bag: frozenset[str]
    row_count: int
    probability_mass: float


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
            if _paper_td_accepts_required_in(absent_row, queried_in):
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

            for labels in _paper_td_complete_labels(
                present_arguments,
                frozenset(active_defeats),
                prior_labels=row.labels,
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


def _paper_td_accepts_required_in(
    row: PaperTDRow,
    queried_in: frozenset[str],
) -> bool:
    return all(row.labels.get(argument) is PaperTDLabel.IN for argument in queried_in)


def _paper_td_complete_labels(
    present_arguments: frozenset[str],
    active_defeats: frozenset[tuple[str, str]],
    *,
    prior_labels: dict[str, PaperTDLabel],
) -> tuple[dict[str, PaperTDLabel], ...]:
    framework = ArgumentationFramework(
        arguments=present_arguments,
        defeats=active_defeats,
    )
    rows: list[dict[str, PaperTDLabel]] = []
    from argumentation.dung import complete_extensions

    for extension in complete_extensions(framework, backend="brute"):
        labelling = Labelling.from_extension(framework, extension)
        labels = {
            argument: _paper_td_label_from_dung(label)
            for argument, label in labelling.statuses.items()
        }
        if all(labels.get(argument) is label for argument, label in prior_labels.items()):
            rows.append(labels)
    return tuple(sorted(rows, key=lambda labels: tuple(sorted(labels.items()))))


def _paper_td_label_from_dung(label: Label) -> PaperTDLabel:
    if label is Label.IN:
        return PaperTDLabel.IN
    if label is Label.OUT:
        return PaperTDLabel.OUT
    return PaperTDLabel.UNDECIDED


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
                    if target == argument and labels.get(source) is PaperTDLabel.UNDECIDED
                ),
                None,
            )
            if attacker is not None:
                witnesses[argument] = attacker
    return witnesses


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
        tuple(sorted((argument, label.value) for argument, label in row.labels.items())),
        tuple(sorted(row.witnesses.items())),
    )


# ===================================================================
# Treewidth estimation: min-degree heuristic
# ===================================================================

def _build_primal_graph(
    framework: ArgumentationFramework,
) -> dict[str, set[str]]:
    """Build undirected primal graph from the semantic attack relation.

    Per Popescu & Wallner (2024, p.4): primal graph has arguments as
    nodes, undirected edges between attack endpoints.
    """
    adj: dict[str, set[str]] = {a: set() for a in framework.arguments}
    relation = framework.attacks if framework.attacks is not None else framework.defeats
    for src, tgt in relation:
        if src == tgt:
            continue
        adj[src].add(tgt)
        adj[tgt].add(src)
    return adj


def estimate_treewidth(framework: ArgumentationFramework) -> int:
    """Estimate treewidth using min-degree heuristic.

    Per Popescu & Wallner (2024, p.4): primal graph has arguments as
    nodes, edges between attack endpoints. Min-degree heuristic gives
    upper bound on treewidth.

    The min-degree heuristic repeatedly removes the vertex with minimum
    degree, adding edges between its neighbors (fill-in). The maximum
    degree at removal time is an upper bound on treewidth.
    """
    if not framework.arguments:
        return 0

    adj = _build_primal_graph(framework)

    # Work on a mutable copy
    remaining = set(adj.keys())
    neighbors: dict[str, set[str]] = {v: set(adj[v]) for v in remaining}
    tw = 0

    while remaining:
        # Find vertex with minimum degree among remaining
        min_v = min(remaining, key=lambda v: len(neighbors[v] & remaining))
        nbrs = neighbors[min_v] & remaining
        deg = len(nbrs)
        tw = max(tw, deg)

        # Add fill-in edges between neighbors (make them a clique)
        nbrs_list = sorted(nbrs)
        for i in range(len(nbrs_list)):
            for j in range(i + 1, len(nbrs_list)):
                u, w = nbrs_list[i], nbrs_list[j]
                neighbors[u].add(w)
                neighbors[w].add(u)

        # Remove the vertex
        remaining.discard(min_v)

    return tw


# ===================================================================
# Tree decomposition computation
# ===================================================================

def compute_tree_decomposition(
    framework: ArgumentationFramework,
) -> TreeDecomposition:
    """Compute tree decomposition via min-degree elimination ordering.

    Returns a tree where each node (bag) contains a subset of arguments.
    Per Popescu & Wallner (2024, p.4-5): bags satisfy vertex coverage,
    edge coverage, and running intersection (connectedness).
    """
    if not framework.arguments:
        return TreeDecomposition(bags={0: frozenset()}, adj={0: set()}, root=0, width=0)

    adj = _build_primal_graph(framework)
    remaining = set(adj.keys())
    neighbors: dict[str, set[str]] = {v: set(adj[v]) for v in remaining}

    # Elimination ordering produces bags
    bags: dict[int, frozenset[str]] = {}
    bag_id = 0
    # Map: vertex -> bag_id where it was eliminated
    vertex_bag: dict[str, int] = {}
    bag_vertex: dict[int, str] = {}
    width = 0

    while remaining:
        min_v = min(remaining, key=lambda v: len(neighbors[v] & remaining))
        nbrs = neighbors[min_v] & remaining

        # Bag = {min_v} ∪ neighbors in remaining
        bag = frozenset({min_v}) | nbrs
        bags[bag_id] = bag
        vertex_bag[min_v] = bag_id
        bag_vertex[bag_id] = min_v
        width = max(width, len(bag) - 1)

        # Fill-in
        nbrs_list = sorted(nbrs)
        for i in range(len(nbrs_list)):
            for j in range(i + 1, len(nbrs_list)):
                u, w = nbrs_list[i], nbrs_list[j]
                neighbors[u].add(w)
                neighbors[w].add(u)

        remaining.discard(min_v)
        bag_id += 1

    # Build tree edges from the elimination ordering. For each bag B_i created
    # when eliminating v_i, connect it to the bag of the earliest later-eliminated
    # vertex still present in B_i \ {v_i}. This is the standard elimination-based
    # reconstruction and ensures B_i \ {v_i} is contained in the parent bag.
    tree_adj: dict[int, set[int]] = {i: set() for i in bags}
    for current_bag_id, current_bag in bags.items():
        eliminated_vertex = bag_vertex[current_bag_id]
        remaining_in_bag = current_bag - {eliminated_vertex}
        if remaining_in_bag:
            parent = min(vertex_bag[vertex] for vertex in remaining_in_bag)
            tree_adj[current_bag_id].add(parent)
            tree_adj[parent].add(current_bag_id)

    root = max(bags) if bags else 0
    td = TreeDecomposition(bags=bags, adj=tree_adj, root=root, width=width)
    validate_tree_decomposition(td, framework)
    return td


def validate_tree_decomposition(
    td: TreeDecomposition,
    framework: ArgumentationFramework | None = None,
) -> None:
    """Validate that a TD is internally well-formed and optionally AF-complete."""
    bag_ids = set(td.bags)
    if not bag_ids:
        raise ValueError("tree decomposition must contain at least one bag")
    if td.root not in bag_ids:
        raise ValueError("tree decomposition root must reference an existing bag")

    for bag_id in bag_ids:
        neighbors = td.adj.get(bag_id, set())
        for neighbor in neighbors:
            if neighbor not in bag_ids:
                raise ValueError("tree decomposition adjacency references an unknown bag")
            if bag_id not in td.adj.get(neighbor, set()):
                raise ValueError("tree decomposition adjacency must be symmetric")

    visited: set[int] = set()
    stack = [td.root]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        stack.extend(td.adj.get(node, set()) - visited)

    if visited != bag_ids:
        raise ValueError("tree decomposition adjacency must form a connected tree")

    edge_count = sum(len(td.adj.get(bag_id, set())) for bag_id in bag_ids) // 2
    if edge_count != len(bag_ids) - 1:
        raise ValueError("tree decomposition adjacency must form a connected tree")

    actual_width = max(len(bag) - 1 for bag in td.bags.values())
    if td.width != actual_width:
        raise ValueError(
            f"tree decomposition width mismatch: expected {actual_width}, got {td.width}"
        )

    covered_arguments = set().union(*td.bags.values())
    for argument in sorted(covered_arguments):
        containing = {
            bag_id
            for bag_id, bag in td.bags.items()
            if argument in bag
        }
        component: set[int] = set()
        stack = [next(iter(containing))]
        while stack:
            node = stack.pop()
            if node in component or node not in containing:
                continue
            component.add(node)
            stack.extend(td.adj.get(node, set()) - component)
        if component != containing:
            raise ValueError(
                f"tree decomposition running intersection violated for argument '{argument}'"
            )

    if framework is None:
        return

    framework_arguments = set(framework.arguments)
    extra_arguments = covered_arguments - framework_arguments
    if extra_arguments:
        raise ValueError(
            f"tree decomposition contains arguments outside the framework: {sorted(extra_arguments)}"
        )
    missing_arguments = framework_arguments - covered_arguments
    if missing_arguments:
        raise ValueError(
            f"tree decomposition does not cover all arguments: {sorted(missing_arguments)}"
        )

    relation = framework.attacks if framework.attacks is not None else framework.defeats
    for src, tgt in relation:
        if not any(src in bag and tgt in bag for bag in td.bags.values()):
            raise ValueError(
                f"tree decomposition does not cover edge ({src}, {tgt})"
            )


# ===================================================================
# Nice tree decomposition conversion
# ===================================================================

def to_nice_tree_decomposition(
    td: TreeDecomposition,
) -> NiceTreeDecomposition:
    """Convert to nice tree decomposition with 4 node types.

    Per Popescu & Wallner (2024, p.5):
    - Leaf: empty bag, no children
    - Introduce(v): adds argument v, one child
    - Forget(v): removes argument v, one child
    - Join: two children with identical bags
    """
    validate_tree_decomposition(td)
    nodes: dict[int, NiceTDNode] = {}
    next_id = max(td.bags.keys()) + 1 if td.bags else 0

    def _new_id() -> int:
        nonlocal next_id
        nid = next_id
        next_id += 1
        return nid

    # BFS from root to determine parent-child relationships in the rooted tree
    children_map: dict[int, list[int]] = {n: [] for n in td.bags}
    visited = {td.root}
    queue = [td.root]
    while queue:
        node = queue.pop(0)
        for neighbor in td.adj.get(node, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                children_map[node].append(neighbor)
                queue.append(neighbor)

    def _build_introduce_chain(
        target_bag: frozenset[str],
        start_bag: frozenset[str],
        child_id: int,
    ) -> int:
        """Build a chain of introduce nodes from start_bag up to target_bag."""
        to_add = sorted(target_bag - start_bag)
        current_bag = start_bag
        current_child = child_id
        for v in to_add:
            nid = _new_id()
            current_bag = current_bag | frozenset({v})
            nodes[nid] = NiceTDNode(
                bag=current_bag,
                node_type="introduce",
                introduced=v,
                children=[current_child],
            )
            current_child = nid
        return current_child

    def _build_forget_chain(
        target_bag: frozenset[str],
        start_bag: frozenset[str],
        child_id: int,
    ) -> int:
        """Build a chain of forget nodes from start_bag down to target_bag."""
        to_remove = sorted(start_bag - target_bag)
        current_bag = start_bag
        current_child = child_id
        for v in to_remove:
            nid = _new_id()
            current_bag = current_bag - frozenset({v})
            nodes[nid] = NiceTDNode(
                bag=current_bag,
                node_type="forget",
                forgotten=v,
                children=[current_child],
            )
            current_child = nid
        return current_child

    def _convert(td_node: int) -> int:
        """Recursively convert a TD node to nice TD nodes. Returns the ID of the top node."""
        bag = td.bags[td_node]
        kids = children_map[td_node]

        if not kids:
            # Leaf case: build leaf (empty bag) then introduce chain up to bag
            leaf_id = _new_id()
            nodes[leaf_id] = NiceTDNode(
                bag=frozenset(),
                node_type="leaf",
                children=[],
            )
            if not bag:
                return leaf_id
            return _build_introduce_chain(bag, frozenset(), leaf_id)

        # Recursively convert children
        converted_kids = []
        for kid in kids:
            kid_top = _convert(kid)
            # The child's top node has bag = td.bags[kid] (after introduces).
            # We need to adapt it to match our bag for joining.
            child_bag = td.bags[kid]

            # First forget extra vertices the child has that we don't
            extra = child_bag - bag
            if extra:
                kid_top = _build_forget_chain(child_bag - extra, child_bag, kid_top)

            # Then introduce vertices we have that the child doesn't
            missing = bag - child_bag
            adapted_bag = child_bag - extra
            if missing:
                kid_top = _build_introduce_chain(bag, adapted_bag, kid_top)

            converted_kids.append(kid_top)

        if len(converted_kids) == 1:
            return converted_kids[0]

        # Multiple children: build a binary join tree
        while len(converted_kids) > 1:
            left = converted_kids.pop(0)
            right = converted_kids.pop(0)
            join_id = _new_id()
            nodes[join_id] = NiceTDNode(
                bag=bag,
                node_type="join",
                children=[left, right],
            )
            converted_kids.insert(0, join_id)

        return converted_kids[0]

    top = _convert(td.root)

    # Now add forget nodes at the top for the root bag -> empty bag
    root_bag = nodes[top].bag if top in nodes else td.bags[td.root]
    final_top = _build_forget_chain(frozenset(), root_bag, top)

    return NiceTreeDecomposition(nodes=nodes, root=final_top)


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

    from argumentation.probabilistic import _expectation

    p_arg: dict[str, float] = {
        a: _expectation(praf.p_args[a]) for a in af.arguments
    }
    p_defeat: dict[tuple[str, str], float] = {
        d: _expectation(praf.p_defeats[d]) for d in af.defeats
    }

    from argumentation.probabilistic_components import connected_components
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


def _compute_grounded_dp_component(
    af: ArgumentationFramework,
    p_arg: dict[str, float],
    p_defeat: dict[tuple[str, str], float],
) -> dict[str, float]:
    return _compute_grounded_dp_component_result(
        af, p_arg, p_defeat, component_index=0,
    ).acceptance_probs


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
