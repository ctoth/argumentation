"""SCC-recursive solving for the SCC-recursive Dung semantics (complete, preferred, stable).

Wave B2 of the graph-theory speedup workstream. Implements the Baroni-Giacomin-Guida
(AIJ 168, 2005) SCC-recursive schema (Def 20, Thm 43) on top of the Wave A
:func:`argumentation.core.preprocessing.simplify_af` grounded reduct.

Pipeline for ``complete`` / ``preferred`` / ``stable`` enumeration:

1. ``simplify_af(framework, semantics=...)`` -> residual AF + lift data.
2. SCC-decompose the residual; if it is one SCC (or trivially small / empty) skip
   straight to the flat base solve -- zero decomposition overhead.
3. Otherwise process SCCs in topological order of the condensation; for each SCC
   ``S`` and each partial extension ``E`` chosen over ancestor SCCs, compute the
   ``D(S,E)`` / ``U(S,E)`` / ``UP(S,E)`` sets per [BG&G05] Def 18, restrict to
   ``UP(S,E)``, recurse ``GF(AF|UP(S,E), U(S,E) cap C)``; cross-product the
   per-SCC partial results.
4. Lift each residual extension back through ``simplification.lift``.

Base function (single-SCC sub-AF ``AF`` with membership restricted to ``C``):

* complete  -> ``CE(AF, C)``  -- admissible-in-``C`` sets ``E`` with
  ``F_AF(E) cap C subseteq E``  ([BG&G05] CE def, Def 23).
* preferred -> ``PE(AF, C)``  -- the ``subseteq``-maximal elements of ``CE(AF, C)``.
* stable    -> ``SE(AF, C)`` = ``SE(AF)``  -- ``C`` is provably inert for stable
  ([BG&G05] p. 188).

Resolution of spec ``UNRESOLVED`` item #1 (the ``(AF, C)``-restricted base solve
encoding): rather than threading a "force not-IN" constraint through the Z3
single-extension finders in ``af_sat.py`` (which (a) cannot enumerate and (b) only
expose a "force OUT" knob, which the spec flags as the *wrong* semantics for the
``C`` restriction), we enumerate the base case directly over the subsets of the
sub-AF using the ``argumentation.core.dung`` primitives (``admissible``,
``characteristic_fn``, ``conflict_free``). Sub-AFs handed to the base solve are
single SCCs of the post-preprocessing residual, hence small, so brute-force
enumeration over their subsets is cheap and -- critically -- exact against the
``[BG&G05]`` definitions, which the oracle tests confirm. This is *not* a
reimplementation of the flat SAT solver: it is the same finite-candidate
enumeration ``dung.complete_extensions`` / ``preferred_extensions`` /
``stable_extensions`` already use, specialised with the ``C`` membership filter.

DC/DS (credulous/skeptical acceptance) for these three semantics is routed through
full enumeration (spec ``UNRESOLVED`` item #2 -- query-driven pruning deferred);
correct, not maximally clever, as the prompt permits for this wave.

Hard stop: only complete / preferred / stable. Semi-stable, stage, grounded, ideal,
admissible keep their existing flat paths -- they are not (cleanly) SCC-recursive.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from itertools import combinations

from argumentation.core.dung import (
    ArgumentationFramework,
    _attackers_index,
    _strongly_connected_components,
    _subframework,
    admissible,
    characteristic_fn,
    complete_extensions,
    preferred_extensions,
    stable_extensions,
)
from argumentation.core.preprocessing import AfSimplification, simplify_af

SCC_RECURSIVE_SEMANTICS: frozenset[str] = frozenset(
    {"complete", "preferred", "stable"}
)


@dataclass
class _SolveTelemetry:
    """Diagnostics for the most recent SCC-recursive solve (test/inspection only)."""

    semantics: str | None = None
    residual_size: int | None = None
    residual_scc_count: int | None = None
    flat_fast_path: bool | None = None
    decompose_requested: bool | None = None
    notes: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.semantics = None
        self.residual_size = None
        self.residual_scc_count = None
        self.flat_fast_path = None
        self.decompose_requested = None
        self.notes = []


LAST_SOLVE = _SolveTelemetry()


# --------------------------------------------------------------------------- #
# Base function: standard semantics on a single sub-AF, membership restricted to C
# --------------------------------------------------------------------------- #


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = sorted(arguments)
    out: list[frozenset[str]] = []
    for size in range(len(ordered) + 1):
        for combo in combinations(ordered, size):
            out.append(frozenset(combo))
    return out


def _base_complete_in_c(
    af: ArgumentationFramework, c: frozenset[str]
) -> list[frozenset[str]]:
    attackers_index = _attackers_index(af.defeats)
    out: list[frozenset[str]] = []
    for candidate in _all_subsets(af.arguments):
        if not candidate <= c:
            continue
        if not admissible(
            candidate,
            af.arguments,
            af.defeats,
            attacks=af.attacks,
            attackers_index=attackers_index,
        ):
            continue
        # F_AF(candidate) cap C subseteq candidate  (fixpoint condition, in C)
        defended = characteristic_fn(
            candidate, af.arguments, af.defeats, attackers_index=attackers_index
        )
        if (defended & c) <= candidate:
            out.append(candidate)
    return out


def _base_preferred_in_c(
    af: ArgumentationFramework, c: frozenset[str]
) -> list[frozenset[str]]:
    completes = _base_complete_in_c(af, c)
    return [e for e in completes if not any(e < other for other in completes)]


def _flat_enumerate(
    semantics: str, af: ArgumentationFramework
) -> list[frozenset[str]]:
    """The existing flat (non-SCC, non-preprocessed) enumerator for ``semantics``.

    This is exactly the path ``decompose=False`` and the previous (pre-Wave-B2)
    ``solver`` / ``sat_encoding`` code used -- we do *not* reimplement it.
    """
    if semantics == "complete":
        return complete_extensions(af)
    if semantics == "preferred":
        return preferred_extensions(af)
    if semantics == "stable":
        return stable_extensions(af)
    raise ValueError(f"not an SCC-recursive semantics: {semantics!r}")


def _base_solve(
    semantics: str, af: ArgumentationFramework, c: frozenset[str]
) -> list[frozenset[str]]:
    # When membership is unrestricted (top-level call, or any sub-AF reached with
    # C == its whole argument set) the (AF, C) base function collapses to the plain
    # semantics -> use the existing flat enumerator. The brute-force-over-subsets
    # path is only taken when C genuinely restricts, which (per the schema) happens
    # only at recursion depth >= 1 on small disconnected sub-AFs of a single SCC.
    if c >= af.arguments:
        return _flat_enumerate(semantics, af)
    if semantics == "complete":
        return _base_complete_in_c(af, c)
    if semantics == "preferred":
        return _base_preferred_in_c(af, c)
    if semantics == "stable":
        # C is provably inert for stable ([BG&G05] p. 188): SE(AF, C) = SE(AF).
        return _flat_enumerate(semantics, af)
    raise ValueError(f"not an SCC-recursive semantics: {semantics!r}")


# --------------------------------------------------------------------------- #
# Condensation + topological order
# --------------------------------------------------------------------------- #


def _topological_scc_order(
    sccs: list[frozenset[str]],
    defeats: frozenset[tuple[str, str]],
) -> list[frozenset[str]]:
    """Return the SCCs in a topological order of the condensation (parents first)."""
    index_of: dict[str, int] = {}
    for i, scc in enumerate(sccs):
        for arg in scc:
            index_of[arg] = i
    succ: list[set[int]] = [set() for _ in sccs]
    indeg = [0] * len(sccs)
    for src, dst in defeats:
        i, j = index_of[src], index_of[dst]
        if i != j and j not in succ[i]:
            succ[i].add(j)
            indeg[j] += 1
    # deterministic: break ties by sorted member tuple
    order_key = [tuple(sorted(scc)) for scc in sccs]
    ready = deque(sorted((i for i in range(len(sccs)) if indeg[i] == 0), key=lambda i: order_key[i]))
    result: list[int] = []
    while ready:
        i = ready.popleft()
        result.append(i)
        new_ready: list[int] = []
        for j in succ[i]:
            indeg[j] -= 1
            if indeg[j] == 0:
                new_ready.append(j)
        for j in sorted(new_ready, key=lambda j: order_key[j]):
            ready.append(j)
    if len(result) != len(sccs):  # pragma: no cover -- condensation is always a DAG
        raise RuntimeError("condensation is not a DAG -- SCC computation is wrong")
    return [sccs[i] for i in result]


# --------------------------------------------------------------------------- #
# The recursive enumerator GF(AF, C)
# --------------------------------------------------------------------------- #


def _gf(
    semantics: str, af: ArgumentationFramework, c: frozenset[str]
) -> list[frozenset[str]]:
    sccs = _strongly_connected_components(af.arguments, af.defeats)
    if len(sccs) <= 1:
        return _base_solve(semantics, af, c)

    attackers_index = _attackers_index(af.defeats)
    scc_of: dict[str, frozenset[str]] = {}
    for scc in sccs:
        for arg in scc:
            scc_of[arg] = scc

    order = _topological_scc_order(sccs, af.defeats)

    partials: list[frozenset[str]] = [frozenset()]
    for scc in order:
        # outparents(S): arguments outside S that attack some node of S
        outparents = frozenset(
            src for src, dst in af.defeats if dst in scc and src not in scc
        )
        new_partials: list[frozenset[str]] = []
        for e in partials:
            e_out = e & outparents  # part of E that lies outside S
            d_set = {
                a
                for a in scc
                if any((b, a) in af.defeats for b in e_out)
            }
            up_set = scc - d_set
            u_set = set()
            for a in up_set:
                # a not attacked from outside by E:
                if any((b, a) in af.defeats for b in e_out):
                    continue
                ext_attackers = (attackers_index.get(a, frozenset()) & outparents)
                # every external attacker b of a is itself attacked by E
                if all(any((d, b) in af.defeats for d in e) for b in ext_attackers):
                    u_set.add(a)
            sub_af = _subframework(af, frozenset(up_set))
            sub_c = frozenset(u_set) & c
            for e_s in _gf(semantics, sub_af, sub_c):
                new_partials.append(e | e_s)
        partials = new_partials
    return partials


# --------------------------------------------------------------------------- #
# Public enumeration API
# --------------------------------------------------------------------------- #


def _normalize_semantics(semantics: str) -> str:
    return semantics.strip().lower().replace("_", "-")


def scc_extensions(
    framework: ArgumentationFramework,
    semantics: str,
    *,
    decompose: bool = True,
) -> list[frozenset[str]]:
    """Enumerate complete / preferred / stable extensions via the SCC-recursive schema.

    ``decompose=False`` opts out of the SCC layer (and the preprocessing layer):
    the framework is solved by the base function directly. The result is always
    identical to the flat path -- this is a transparent speedup.
    """
    semantics = _normalize_semantics(semantics)
    if semantics not in SCC_RECURSIVE_SEMANTICS:
        raise ValueError(
            f"scc_extensions only handles {sorted(SCC_RECURSIVE_SEMANTICS)}, got {semantics!r}"
        )

    LAST_SOLVE.reset()
    LAST_SOLVE.semantics = semantics
    LAST_SOLVE.decompose_requested = decompose

    if not decompose:
        LAST_SOLVE.flat_fast_path = True
        LAST_SOLVE.notes.append("decompose=False -> flat base solve on whole AF")
        return _base_solve(semantics, framework, framework.arguments)

    simplification: AfSimplification = simplify_af(framework, semantics=semantics)
    residual = simplification.residual
    LAST_SOLVE.residual_size = len(residual.arguments)

    sccs = _strongly_connected_components(residual.arguments, residual.defeats)
    LAST_SOLVE.residual_scc_count = len(sccs)

    if len(sccs) <= 1:
        # Empty residual or one SCC: skip decomposition machinery, call the base
        # (flat) solve on the residual directly. Zero SCC-layer overhead.
        LAST_SOLVE.flat_fast_path = True
        LAST_SOLVE.notes.append(
            f"residual has {len(sccs)} SCC(s) -> flat base solve on residual"
        )
        residual_extensions = _base_solve(semantics, residual, residual.arguments)
    else:
        LAST_SOLVE.flat_fast_path = False
        LAST_SOLVE.notes.append(f"residual has {len(sccs)} SCCs -> SCC recursion")
        residual_extensions = _gf(semantics, residual, residual.arguments)

    return simplification.lift_all(residual_extensions)


# --------------------------------------------------------------------------- #
# DC/DS via enumeration
# --------------------------------------------------------------------------- #


def scc_credulously_accepted(
    framework: ArgumentationFramework,
    semantics: str,
    argument: str,
    *,
    decompose: bool = True,
) -> bool:
    """DC-sigma: is ``argument`` in some sigma-extension? (sigma in {complete, preferred, stable})."""
    return any(
        argument in extension
        for extension in scc_extensions(framework, semantics, decompose=decompose)
    )


def scc_skeptically_accepted(
    framework: ArgumentationFramework,
    semantics: str,
    argument: str,
    *,
    decompose: bool = True,
) -> bool:
    """DS-sigma: is ``argument`` in every sigma-extension? (vacuously True if none)."""
    extensions = scc_extensions(framework, semantics, decompose=decompose)
    return all(argument in extension for extension in extensions)


__all__ = [
    "LAST_SOLVE",
    "SCC_RECURSIVE_SEMANTICS",
    "scc_credulously_accepted",
    "scc_extensions",
    "scc_skeptically_accepted",
]
