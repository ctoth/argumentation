"""Semantics-preserving preprocessing for Dung abstract argumentation frameworks.

Wave A of the graph-theory speedup workstream: shrink an AF before it is handed
to the SAT (Z3) or ASP encoder, then lift the answer back. This implements the
de-facto standard competitive-solver preprocessing (mu-toksia / pyglaf /
ASPARTIX-V):

* **Grounded reduct.** Compute the grounded extension ``G`` (least fixed point of
  the characteristic function, O(V+E)). Every ``a in G`` is IN in every extension
  of every admissibility-based semantics; every ``a`` attacked by ``G`` is OUT in
  every such extension. Delete ``G`` and ``G+`` (the arguments ``G`` attacks) plus
  all incident attacks; solve only the residual; re-union ``G`` into every answer.
* **Isolated-argument elimination.** An argument with no incoming and no outgoing
  attacks is unattacked, hence in ``G`` -- so it is already removed by the grounded
  reduct. Tracked here only as a documented consequence.
* **Self-loop sinks.** An argument ``a`` with ``(a, a)`` in the attack relation can
  never be in any conflict-free set, so it is OUT in every extension of every
  semantics this library supports. If such an ``a`` has *no other* incident edges
  (a pure self-loop sink) it can be deleted outright without changing any
  extension -- *except for the stable semantics*: ``a`` is attacked only by itself,
  so no conflict-free set ever covers it, hence the AF has no stable extension;
  deleting ``a`` would spuriously create one. So this removal is gated off for
  ``stable``. Self-loop arguments with outgoing attacks are *also* not removed --
  deleting them would spuriously unblock their targets (a target attacked only by
  self-attackers can never be IN, but would become unattacked in the residual).
  The SAT/ASP encoders already handle ``(a, a)`` correctly via conflict-freeness,
  so leaving them in is sound, just less reduced.

Reductions detected but deliberately **not applied** (see report):

* **Symmetric-AF special case** (Coste-Marquis et al., ECSQARU 2005): detected via
  :func:`is_symmetric_irreflexive`; a full polynomial special-case solver is out of
  scope for Wave A. TODO.
* **Baumann / Oikarinen-Woltran kernels** (``af_revision.stable_kernel`` /
  ``baumann_2015_kernel``): their preservation guarantees are stated for strong
  equivalence / revision, not obviously matched to "solve this task on this AF".
  Not applied -- soundness beats speed. TODO: confirm the guarantee per semantics.

Validity of the grounded reduct by semantics (the only reduction applied):

* ``complete`` -- standard reduct result: ``complete(AF) = {G u E : E in complete(residual)}``.
* ``preferred`` -- maximal complete; the offset ``G`` is constant so maximality transfers.
* ``stable`` -- ``G`` is in every stable extension, ``G+`` in none; coverage transfers.
* ``semi-stable`` -- semi-stable extensions are complete extensions (so contain ``G``,
  exclude ``G+``) with maximal range; range = ``G u G+`` (constant) ``u`` residual-range,
  so maximality transfers.
* ``stage`` -- NOT covered by the grounded reduct (see the NOTE on
  :data:`GROUNDED_REDUCT_SEMANTICS`): stage extensions are conflict-free, not complete,
  and need not contain ``G`` or exclude ``G+``.
* ``grounded`` -- the residual's grounded extension is empty by construction, so
  ``grounded(AF) = G`` directly (the reduct degenerates to "return G").
* ``ideal`` -- contained in the intersection of preferred extensions, all of which
  contain ``G`` and exclude ``G+``; the maximal admissible subset transfers.

Reference: Niskanen & Jaervisalo, "mu-toksia: An Efficient Abstract Argumentation
Reasoner" (KR 2020); Dvorak et al., "ASPARTIX-V19/-V21"; folklore grounded reduct.
"""

from __future__ import annotations

from argumentation.core.dung import (
    ArgumentationFramework,
    grounded_extension,
)
from argumentation.core.finite import predecessors_index, successors_index
from argumentation.core.reduct import SemanticReduct

# Semantics for which the grounded reduct is semantics-preserving (see module docstring).
GROUNDED_REDUCT_SEMANTICS: frozenset[str] = frozenset(
    {
        "complete",
        "preferred",
        "stable",
        "semi-stable",
        "grounded",
        "ideal",
    }
)
# NOTE: ``admissible`` is also deliberately absent. Admissible sets need not
# contain the grounded extension (the empty set is admissible), so
# ``adm(AF) != {G u E : E in adm(residual)}`` -- the reduct would drop every
# admissible set that does not already contain ``G``.
# NOTE: ``stage`` is deliberately absent. Stage extensions are conflict-free
# range-maximal sets, NOT complete extensions, so they need not contain the
# grounded extension nor exclude the grounded-attacked arguments. Concrete
# counterexample: AF = ({a,b,c}, {(a,a),(b,c),(c,a)}) has grounded {b}, but {c} is
# a stage extension (range {a,c}, incomparable to range {b,c} of {b}). Applying the
# grounded reduct would wrongly force c OUT. Stage gets only the always-sound
# self-loop-sink removal.


def is_symmetric_irreflexive(framework: ArgumentationFramework) -> bool:
    """True when the defeat relation is symmetric and irreflexive.

    Such AFs are coherent (Coste-Marquis et al., ECSQARU 2005) and several tasks
    become polynomial; Wave A only *detects* this, it does not exploit it.
    """
    defeats = framework.defeats
    for attacker, target in defeats:
        if attacker == target:
            return False
        if (target, attacker) not in defeats:
            return False
    return bool(defeats)


def _pure_self_loop_sinks(framework: ArgumentationFramework) -> frozenset[str]:
    """Self-attackers whose only incident edge is the self-loop itself."""
    incident: dict[str, int] = {}
    self_loops: set[str] = set()
    for attacker, target in framework.defeats:
        if attacker == target:
            self_loops.add(attacker)
        incident[attacker] = incident.get(attacker, 0) + 1
        incident[target] = incident.get(target, 0) + 1
    # A pure self-loop sink ``a`` contributes exactly one edge ``(a, a)`` which the
    # loop above counted twice (once as attacker, once as target) -> incident == 2.
    return frozenset(arg for arg in self_loops if incident.get(arg, 0) == 2)


def simplify_af(
    framework: ArgumentationFramework,
    *,
    semantics: str | None = None,
) -> SemanticReduct[ArgumentationFramework, str]:
    """Compute a semantics-preserving reduced AF and the lift-back data.

    When ``semantics`` is given and is not in :data:`GROUNDED_REDUCT_SEMANTICS`, the
    grounded reduct is *not* applied (only the always-sound pure self-loop sink
    removal is). When ``semantics`` is ``None`` the grounded reduct is applied --
    callers are responsible for only calling this for supported semantics.
    """
    apply_grounded = semantics is None or semantics in GROUNDED_REDUCT_SEMANTICS

    fixed_in: frozenset[str] = frozenset()
    fixed_out: frozenset[str] = frozenset()

    if apply_grounded:
        grounded = grounded_extension(framework)
        attacked_by_grounded = _attacked_by(grounded, framework.defeats)
        fixed_in = grounded
        fixed_out = attacked_by_grounded
    # Pure self-loop sink removal is sound for every supported semantics except
    # stable (a self-loop sink can never be covered, so it is the obstruction to a
    # stable extension existing -- deleting it would spuriously create one).
    allow_sink_removal = semantics is None or semantics != "stable"
    if allow_sink_removal:
        sinks = _pure_self_loop_sinks(framework) - fixed_in
        fixed_out = fixed_out | sinks

    removed = fixed_in | fixed_out
    if not removed:
        return SemanticReduct(
            original=framework,
            residual=framework,
            fixed_in=frozenset(),
            fixed_out=frozenset(),
        )

    residual_arguments = framework.arguments - removed
    residual_defeats = frozenset(
        (attacker, target)
        for attacker, target in framework.defeats
        if attacker in residual_arguments and target in residual_arguments
    )
    residual_attacks = (
        None
        if framework.attacks is None
        else frozenset(
            (attacker, target)
            for attacker, target in framework.attacks
            if attacker in residual_arguments and target in residual_arguments
        )
    )
    residual = ArgumentationFramework(
        arguments=residual_arguments,
        defeats=residual_defeats,
        attacks=residual_attacks,
    )
    return SemanticReduct(
        original=framework,
        residual=residual,
        fixed_in=fixed_in,
        fixed_out=fixed_out,
    )


def isolated_arguments(framework: ArgumentationFramework) -> frozenset[str]:
    """Arguments with no incoming and no outgoing attacks (a diagnostic helper)."""
    attackers = predecessors_index(framework.defeats)
    targets = successors_index(framework.defeats)
    return frozenset(
        argument
        for argument in framework.arguments
        if not attackers.get(argument) and not targets.get(argument)
    )


def _attacked_by(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    return frozenset(target for attacker, target in defeats if attacker in arguments)


__all__ = [
    "GROUNDED_REDUCT_SEMANTICS",
    "isolated_arguments",
    "is_symmetric_irreflexive",
    "simplify_af",
]
