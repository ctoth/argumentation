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

This module is now a thin re-export facade. The implementation lives in three
sibling modules:
- `probabilistic_treedecomp_construction` — TD/nice-TD construction + validation
- `probabilistic_paper_td` — paper-faithful I/O/U witness-table DP
- `probabilistic_grounded_td` — adapted grounded edge-tracking DP
"""

from __future__ import annotations

from argumentation.probabilistic.probabilistic_grounded_td import (
    DPTable,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    ExactDPDiagnostics,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    GroundedOutcomeProbabilities,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    GroundedOutcomeWitness,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    GroundedOutcomeWitnesses,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    compute_exact_dp,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    compute_exact_dp_with_diagnostics,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    supports_exact_dp,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
)
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
    DPTableSummary,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    NiceTDNode,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    NiceTreeDecomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    TreeDecomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    _build_primal_graph,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    _nice_td_post_order,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    compute_tree_decomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    estimate_treewidth,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    to_nice_tree_decomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
    validate_tree_decomposition,  # noqa: F401  re-exported for probabilistic_treedecomp.<name> compatibility
)
