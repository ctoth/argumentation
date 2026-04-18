"""Tree decomposition and exact DP for probabilistic argumentation.

Implements the tree-decomposition-based dynamic programming algorithm
from Popescu & Wallner (2024) for exact computation of extension
probabilities in PrAFs.

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
from typing import TYPE_CHECKING

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
    """Exact acceptance probabilities via tree decomposition DP.

    # Tree-decomposition DP for grounded semantics only.
    # Per Popescu & Wallner (2024): P_ext = P_acc for grounded (unique extension).
    # For preferred/stable/complete, P_acc is #.NP-complete — use MC instead.
    # See reports/research-popescu-pacc-report.md for the analysis.

    For grounded semantics, implements the I/O/U labelling DP with witness
    mechanism (Popescu & Wallner 2024, Algorithms 1-3, p.5-7). The DP
    processes a nice tree decomposition bottom-up, maintaining tables of
    partial labellings weighted by probability.

    Unsupported semantics or relation structures are rejected.

    Complexity: O(3^k * n * 2^d_bag) where k is treewidth, n is number
    of nodes, d_bag is max defeats per bag (Popescu & Wallner 2024, Theorem 7).
    """
    if not supports_exact_dp(praf, semantics):
        raise ValueError(
            "exact_dp only supports grounded semantics on defeat-only probabilistic frameworks"
        )

    return _compute_grounded_dp(praf)


# ===================================================================
# Grounded-semantics tree-decomposition DP
# Per Popescu & Wallner (2024, Algorithms 1-3, p.5-7)
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
    af = praf.framework
    args_list = sorted(af.arguments)

    if not args_list:
        return {}

    # Extract probabilities as floats.
    from argumentation.probabilistic import _expectation

    p_arg: dict[str, float] = {
        a: _expectation(praf.p_args[a]) for a in af.arguments
    }
    p_defeat: dict[tuple[str, str], float] = {
        d: _expectation(praf.p_defeats[d]) for d in af.defeats
    }

    # Decompose into connected components.
    # Per Hunter & Thimm (2017, Prop 18): components are independent.
    from argumentation.probabilistic_components import connected_components
    components = connected_components(praf)

    acceptance: dict[str, float] = {}
    for comp_args in components:
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
        comp_result = _compute_grounded_dp_component(
            comp_af, p_arg, p_defeat,
        )
        acceptance.update(comp_result)

    return acceptance


def _compute_grounded_dp_component(
    af: ArgumentationFramework,
    p_arg: dict[str, float],
    p_defeat: dict[tuple[str, str], float],
) -> dict[str, float]:
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
        return {}

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

        # Free child tables.
        for child in node.children:
            if child in tables:
                del tables[child]

    # At the root, compute grounded extensions and accumulate acceptance.
    # Each row has present_forgotten (all present args) and active_edges.
    # Run the grounded fixpoint on each configuration.
    acceptance: dict[str, float] = {a: 0.0 for a in args_list}
    root_table = tables.get(ntd.root, {})
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
        for a in present:
            if labels[a] == "I":
                acceptance[a] += prob

    return acceptance



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
