"""Query-directed SCC-cone acceptance for Dung AFs.

Implements the sound cone restriction derived in
``experiments/2026-07-10-af-scc-acceptance.md`` from the Baroni-Giacomin-Guida
SCC-recursive schema (AIJ 168, 2005; Def 17-20, Thm 43):

* The ancestor cone ``U`` of the query's SCC is unattacked from outside, so
  every SCC-recursive semantics projects onto it
  (``E in E_sigma(AF) => E cap U in E_sigma(AF|U)``).
* Complete and preferred additionally lift (every cone extension extends to a
  full extension), so DC/DS on ``AF`` equals DC/DS on ``AF|U``.
* Stable does not lift (stable extensions may fail to exist downstream), so
  only the one-sided rules are used: DC-ST cone-NO and DS-ST cone-YES are
  conclusive; anything else falls back to the flat path.

The cone decision itself is delegated to the existing ``af_sat`` finders on
the (much smaller) cone sub-framework -- ``GF`` restricted to the cone is, by
Def 20, exactly the semantics of ``AF|U``, so no per-SCC recursion is needed
at solve time.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field

from argumentation.core.dung import (
    ArgumentationFramework,
    _strongly_connected_components,
    _subframework,
)
from argumentation.core.finite import predecessors_index, successors_index
from argumentation.core.solver_results import AcceptanceSuccess
from argumentation.solving.af_sat import (
    SATTraceSink,
    find_complete_extension,
    find_stable_extension,
    is_preferred_skeptically_accepted,
)

CONE_SEMANTICS: frozenset[str] = frozenset({"complete", "preferred", "stable"})

# The cone sub-problems are purely propositional labelling queries; the Z3
# CDCL sat core decides them orders of magnitude faster than the default SMT
# core (measured on the crusti_g2io_175 cone: 265 s -> 1.6 s for the
# require_in complete-labelling check).
CONE_SAT_ENGINE = "sat-core"

# DS-PR routes through the cone only when the cone is large enough that the
# flat CDAS solver is at risk (its kernel-build/solve pathologies start well
# above this size). On small cones the multi-check CDAS loop is
# high-variance under the non-incremental sat-core engine (measured on
# BA_160_80_2, cone 232 defeats: 95-97 s vs <1 s flat) while the measured
# cone wins start at mainkwt-sized cones (22-24k defeats, ~11 s vs >15 s
# flat). Single-check semantics (complete, stable) are unaffected.
PREFERRED_CONE_MIN_DEFEATS = 15_000


@dataclass
class _ConeTelemetry:
    """Diagnostics for the most recent cone-acceptance attempt (tests only)."""

    fired: bool | None = None
    semantics: str | None = None
    task: str | None = None
    conclusive: bool | None = None
    cone_argument_count: int | None = None
    total_argument_count: int | None = None
    scc_count: int | None = None
    engine: str | None = None
    notes: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.fired = None
        self.semantics = None
        self.task = None
        self.conclusive = None
        self.cone_argument_count = None
        self.total_argument_count = None
        self.scc_count = None
        self.engine = None
        self.notes = []


LAST_CONE = _ConeTelemetry()


def query_cone_arguments(
    framework: ArgumentationFramework,
    query: str,
) -> frozenset[str]:
    """Arguments of the query's SCC plus all its ancestor SCCs (BG&G05 Def 17).

    This set is closed under attackers: any attacker of a cone member lies in
    an SCC that reaches the query's SCC, hence in the cone.
    """
    sccs = _strongly_connected_components(framework.arguments, framework.defeats)
    scc_index_of: dict[str, int] = {}
    for index, scc in enumerate(sccs):
        for argument in scc:
            scc_index_of[argument] = index
    parents: list[set[int]] = [set() for _ in sccs]
    for attacker, target in framework.defeats:
        source, destination = scc_index_of[attacker], scc_index_of[target]
        if source != destination:
            parents[destination].add(source)
    reached = {scc_index_of[query]}
    frontier = deque(reached)
    while frontier:
        component = frontier.popleft()
        for parent in parents[component]:
            if parent not in reached:
                reached.add(parent)
                frontier.append(parent)
    return frozenset(argument for component in reached for argument in sccs[component])


def least_complete_closure(
    framework: ArgumentationFramework,
    admissible_seed: frozenset[str],
) -> frozenset[str]:
    """Least complete extension of ``framework`` containing ``admissible_seed``.

    Iterates the characteristic function from the seed (Dung's fundamental
    lemma). Used to lift cone-local complete witnesses to full-framework
    certificates: when the seed is a complete extension of an unattacked
    restriction ``AF|U``, the closure never adds a ``U`` argument (its
    attackers and their defenders all lie in ``U``), so the certificate still
    agrees with the cone choice on ``U``.
    """
    attackers_index = predecessors_index(framework.defeats)
    targets_index = successors_index(framework.defeats, nodes=framework.arguments)
    in_set: set[str] = set()
    out_set: set[str] = set()
    undefeated_attackers = {
        argument: len(attackers_index.get(argument, frozenset()))
        for argument in framework.arguments
    }
    newly_in = deque()
    for argument in admissible_seed:
        in_set.add(argument)
        newly_in.append(argument)
    for argument, count in undefeated_attackers.items():
        if count == 0 and argument not in in_set:
            in_set.add(argument)
            newly_in.append(argument)
    while newly_in:
        defender = newly_in.popleft()
        for defeated in targets_index.get(defender, frozenset()):
            if defeated in out_set:
                continue
            out_set.add(defeated)
            for target in targets_index.get(defeated, frozenset()):
                undefeated_attackers[target] -= 1
                if (
                    undefeated_attackers[target] == 0
                    and target not in in_set
                    and target not in out_set
                ):
                    in_set.add(target)
                    newly_in.append(target)
    return frozenset(in_set)


def solve_cone_acceptance(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    task: str,
    query: str,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> AcceptanceSuccess | None:
    """Decide DC/DS on the query's ancestor cone when that is provably sound.

    Returns ``None`` when the cone path does not apply (semantics/task not
    covered, the cone spans the framework) or is inconclusive (the one-sided
    stable rules); the caller must then use the flat path.
    """
    LAST_CONE.reset()
    if semantics not in CONE_SEMANTICS:
        return None
    if task not in {"credulous", "skeptical"}:
        return None
    if framework.attacks is not None and framework.attacks != framework.defeats:
        # A separate pre-preference attack layer makes conflict-freeness
        # range over attacks (Modgil & Prakken Def 14) while defense ranges
        # over defeats; the cone derivation covers pure Dung only.
        return None
    if semantics == "preferred" and task != "skeptical":
        # DC-PR keeps the flat path: it returns a full preferred witness,
        # which a cone-local solve cannot certify without downstream work.
        return None
    cone = query_cone_arguments(framework, query)
    if len(cone) >= len(framework.arguments):
        return None

    LAST_CONE.fired = True
    LAST_CONE.semantics = semantics
    LAST_CONE.task = task
    LAST_CONE.cone_argument_count = len(cone)
    LAST_CONE.total_argument_count = len(framework.arguments)
    LAST_CONE.engine = CONE_SAT_ENGINE
    cone_framework = _subframework(framework, cone)

    if semantics == "complete":
        if task == "skeptical":
            return _cone_grounded_membership(framework, cone_framework, query)
        return _cone_complete_credulous(
            framework,
            cone_framework,
            query,
            trace_sink=trace_sink,
            metadata=metadata,
            check_budget_seconds=check_budget_seconds,
        )
    if semantics == "preferred":
        if len(cone_framework.defeats) < PREFERRED_CONE_MIN_DEFEATS:
            LAST_CONE.notes.append("preferred cone below defeat threshold -> flat CDAS")
            return None
        LAST_CONE.conclusive = True
        return AcceptanceSuccess(
            answer=is_preferred_skeptically_accepted(
                cone_framework,
                query,
                trace_sink=trace_sink,
                metadata=metadata,
                check_budget_seconds=check_budget_seconds,
                engine=CONE_SAT_ENGINE,
            )
        )
    return _cone_stable(
        cone_framework,
        task,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )


def _task_constrained_extension(
    find_extension,
    cone_framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
    check_budget_seconds: float | None,
) -> frozenset[str] | None:
    """Cone extension refuting (skeptical) or witnessing (credulous) the query."""
    return find_extension(
        cone_framework,
        require_in=query if task == "credulous" else None,
        require_out=query if task == "skeptical" else None,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=CONE_SAT_ENGINE,
    )


def _cone_complete_credulous(
    framework: ArgumentationFramework,
    cone_framework: ArgumentationFramework,
    query: str,
    *,
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
    check_budget_seconds: float | None,
) -> AcceptanceSuccess:
    """DC-CO on the cone (equivalent to the full framework)."""
    LAST_CONE.conclusive = True
    extension = _task_constrained_extension(
        find_complete_extension,
        cone_framework,
        "credulous",
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    certificate = (
        None if extension is None else least_complete_closure(framework, extension)
    )
    return AcceptanceSuccess(answer=extension is not None, witness=certificate)


def _cone_grounded_membership(
    framework: ArgumentationFramework,
    cone_framework: ArgumentationFramework,
    query: str,
) -> AcceptanceSuccess:
    """DS-CO == grounded membership, decided polynomially on the cone.

    ``q`` is in every complete extension iff it is in the grounded (least
    complete) extension, and grounded is directional, so membership can be
    read off ``GE(AF|U) = GE(AF) cap U``. The NO counterexample is the full
    grounded extension itself (a complete extension avoiding ``q``).
    """
    LAST_CONE.conclusive = True
    LAST_CONE.notes.append("skeptical complete decided by grounded membership")
    if query in least_complete_closure(cone_framework, frozenset()):
        return AcceptanceSuccess(answer=True)
    return AcceptanceSuccess(
        answer=False,
        counterexample=least_complete_closure(framework, frozenset()),
    )


def _cone_stable(
    cone_framework: ArgumentationFramework,
    task: str,
    query: str,
    *,
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
    check_budget_seconds: float | None,
) -> AcceptanceSuccess | None:
    """One-sided stable rules (stable only weakly projects onto the cone).

    An unsat cone check is conclusive: DC-ST => NO (any full stable witness
    would project into the cone), DS-ST => YES (every full stable extension
    projects to a cone-stable one containing the query; vacuously YES when no
    stable extension exists at either level). A sat cone check is
    inconclusive because the cone extension may not extend downstream.
    """
    extension = _task_constrained_extension(
        find_stable_extension,
        cone_framework,
        task,
        query,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    if extension is None:
        LAST_CONE.conclusive = True
        return AcceptanceSuccess(answer=task == "skeptical")
    LAST_CONE.conclusive = False
    LAST_CONE.notes.append("cone stable check inconclusive -> flat fallback")
    return None


__all__ = [
    "CONE_SEMANTICS",
    "LAST_CONE",
    "least_complete_closure",
    "query_cone_arguments",
    "solve_cone_acceptance",
]
