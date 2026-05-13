"""Wave B2 before/after benchmark: SCC-recursive vs flat for complete/preferred/stable.

Generates AF instances (layered / many-small-SCC favourable cases, and single-giant-SCC
no-help controls), times enumeration of complete/preferred/stable plus a DS-PR query,
on the flat path (decompose=False) vs the SCC path (decompose=True).
"""

from __future__ import annotations

import random
import time

from argumentation.dung import ArgumentationFramework
from argumentation.labelling import ExactEnumerationExceeded
from argumentation.scc_recursive import scc_extensions, scc_skeptically_accepted


def layered_cycles(n_layers: int, cycle_len: int, seed: int) -> ArgumentationFramework:
    """A chain of `n_layers` cycles, each of `cycle_len` nodes, layer i attacks layer i+1.
    Plus a deterministic feeder chain so the grounded reduct does *not* eat everything."""
    rng = random.Random(seed)
    args: list[str] = []
    edges: set[tuple[str, str]] = set()
    layers: list[list[str]] = []
    for layer in range(n_layers):
        nodes = [f"L{layer}_{i}" for i in range(cycle_len)]
        layers.append(nodes)
        args.extend(nodes)
        for i in range(cycle_len):
            edges.add((nodes[i], nodes[(i + 1) % cycle_len]))
    for layer in range(n_layers - 1):
        # one cross edge from layer to layer+1
        edges.add((layers[layer][0], layers[layer + 1][rng.randrange(cycle_len)]))
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(edges))


def many_small_sccs(n_sccs: int, seed: int) -> ArgumentationFramework:
    """Tree-of-2-cycles: n_sccs 2-cycles arranged in a binary tree of attacks."""
    args: list[str] = []
    edges: set[tuple[str, str]] = set()
    sccs: list[tuple[str, str]] = []
    for k in range(n_sccs):
        a, b = f"s{k}a", f"s{k}b"
        sccs.append((a, b))
        args += [a, b]
        edges.add((a, b))
        edges.add((b, a))
    for k in range(n_sccs):
        parent = (k - 1) // 2
        if parent >= 0:
            edges.add((sccs[parent][0], sccs[k][0]))
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(edges))


def giant_scc(n: int, density: float, seed: int) -> ArgumentationFramework:
    """A single dense strongly-connected AF: a Hamiltonian cycle plus random chords."""
    rng = random.Random(seed)
    args = [f"g{i}" for i in range(n)]
    edges: set[tuple[str, str]] = set()
    for i in range(n):
        edges.add((args[i], args[(i + 1) % n]))  # ensures strong connectivity
    for a in args:
        for b in args:
            if a != b and rng.random() < density:
                edges.add((a, b))
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(edges))


def time_call(fn, repeats: int = 3):
    """Returns best wall-clock seconds, or the string 'EXCEEDED' if the flat path
    blew its exact-enumeration budget (in which case the SCC path is strictly better)."""
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        try:
            fn()
        except ExactEnumerationExceeded:
            return "EXCEEDED"
        best = min(best, time.perf_counter() - t0)
    return best


def _fmt(x) -> str:
    return "  EXCEEDED" if isinstance(x, str) else f"{x * 1e3:8.2f}ms"


def _speed(flat, scc) -> str:
    if isinstance(flat, str):
        return "  inf (flat exceeded budget)"
    if isinstance(scc, str) or scc <= 0:
        return "   n/a"
    return f"{flat / scc:6.2f}x"


def bench_instance(name: str, af: ArgumentationFramework) -> None:
    print(f"\n=== {name}  (|A|={len(af.arguments)}, |->|={len(af.defeats)}) ===")
    for semantics in ("complete", "preferred", "stable"):
        flat = time_call(lambda s=semantics: scc_extensions(af, s, decompose=False))
        scc = time_call(lambda s=semantics: scc_extensions(af, s, decompose=True))
        try:
            n_ext = len(scc_extensions(af, semantics, decompose=True))
        except ExactEnumerationExceeded:
            n_ext = -1
        print(
            f"  EE-{semantics:9s}: flat={_fmt(flat)}  scc={_fmt(scc)}  "
            f"speedup={_speed(flat, scc)}  (#ext={n_ext})"
        )
    arg = sorted(af.arguments)[0] if af.arguments else None
    if arg is not None:
        flat = time_call(lambda: scc_skeptically_accepted(af, "preferred", arg, decompose=False))
        scc = time_call(lambda: scc_skeptically_accepted(af, "preferred", arg, decompose=True))
        print(f"  DS-PR({arg})  : flat={_fmt(flat)}  scc={_fmt(scc)}  speedup={_speed(flat, scc)}")


if __name__ == "__main__":
    # Small enough that the flat path stays within its 65536-subset budget:
    bench_instance("layered_cycles(4 layers x 3-cycle)", layered_cycles(4, 3, seed=1))
    bench_instance("layered_cycles(3 layers x 4-cycle)", layered_cycles(3, 4, seed=2))
    bench_instance("many_small_sccs(6 two-cycles, tree)", many_small_sccs(6, seed=3))
    bench_instance("many_small_sccs(7 two-cycles, tree)", many_small_sccs(7, seed=4))
    # Larger -- flat path exceeds its budget, SCC path still solves it:
    bench_instance("layered_cycles(6 layers x 3-cycle) [big]", layered_cycles(6, 3, seed=5))
    bench_instance("many_small_sccs(15 two-cycles, tree) [big]", many_small_sccs(15, seed=6))
    # Single giant SCC -- no-help control, expect ~1.0x:
    bench_instance("giant_scc(13 nodes, density 0.15) [no-help control]", giant_scc(13, 0.15, seed=7))
    bench_instance("giant_scc(14 nodes, density 0.10) [no-help control]", giant_scc(14, 0.10, seed=8))
