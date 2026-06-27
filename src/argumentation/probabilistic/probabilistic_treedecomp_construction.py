"""Tree decomposition construction and validation for probabilistic argumentation.

Shared leaf module: the nice tree-decomposition machinery reused by both the
paper-style I/O/U witness DP (`probabilistic_paper_td`) and the adapted
grounded edge-tracking DP (`probabilistic_grounded_td`). Imports only
`argumentation.core.dung`.

Per Popescu & Wallner (2024): primal graph, min-degree elimination ordering,
tree decomposition, and conversion to a nice tree decomposition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from argumentation.core.dung import ArgumentationFramework


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


def _nice_td_post_order(ntd: NiceTreeDecomposition) -> list[int]:
    post_order: list[int] = []
    visit_stack: list[tuple[int, bool]] = [(ntd.root, False)]
    while visit_stack:
        node_id, processed = visit_stack.pop()
        if processed:
            post_order.append(node_id)
            continue
        visit_stack.append((node_id, True))
        node = ntd.nodes[node_id]
        for child in reversed(node.children):
            visit_stack.append((child, False))
    return post_order
