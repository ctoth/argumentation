"""Incremental SAT kernel for Dung abstract argumentation frameworks."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha1
from time import perf_counter
from typing import Any

from argumentation.core.dung import (
    ArgumentationFramework,
    grounded_extension,
    range_of,
)
from argumentation.core.finite import is_acyclic, predecessors_index
from argumentation.core.optional_deps import load_z3
from argumentation.core.preprocessing import simplify_af
from argumentation.core.reduct import SemanticReduct


class AfSatCheckTimeout(TimeoutError):
    """Z3 returned ``unknown`` on an AF SAT check (per-check budget exhausted).

    Mirrors the ABA ``ClingoSolveTimeout`` convention: budget exhaustion is a
    structured timeout signal, never a sat/unsat answer.
    """

    def __init__(
        self,
        utility_name: str,
        *,
        check_budget_seconds: float | None = None,
    ) -> None:
        self.utility_name = utility_name
        self.check_budget_seconds = check_budget_seconds
        budget = (
            f" (check budget {check_budget_seconds}s)"
            if check_budget_seconds is not None
            else ""
        )
        super().__init__(
            f"Z3 returned unknown on AF SAT check {utility_name!r}{budget}"
        )


def _apply_check_budget(solver: Any, check_budget_seconds: float | None) -> None:
    """Set the z3 per-check ``timeout`` parameter (milliseconds) when budgeted."""
    if check_budget_seconds is None:
        return
    solver.set("timeout", max(1, int(check_budget_seconds * 1000)))


def _make_solver(z3: Any, engine: str) -> Any:
    """Construct the Z3 solver object for ``engine`` ("smt" or "sat-core")."""
    if engine == "smt":
        return z3.Solver()
    if engine == "sat-core":
        return z3.Tactic("sat").solver()
    raise ValueError(f"unknown AF SAT engine: {engine!r}")


@dataclass(frozen=True)
class SATCheck:
    """Telemetry for one SAT solver check."""

    utility_name: str
    result: str
    elapsed_ms: float
    assumptions_count: int
    argument_count: int
    attack_count: int
    model_extension_size: int | None = None
    model_extension_fingerprint: str | None = None
    loop_index: int | None = None
    learned_count: int | None = None
    range_bound: int | None = None
    range_constraint: str | None = None
    metadata: Mapping[str, object] | None = None


SATTraceSink = Callable[[SATCheck], None]


@dataclass(frozen=True)
class StableUnsatExplanation:
    """Tracked-clause explanation surface for stable-extension SAT checks.

    The core returned by Z3 is not guaranteed minimal. It is still useful as a
    deterministic obstruction surface: it names which conflict-free, coverage,
    and requirement groups participated in one unsat proof.
    """

    status: str
    stable_exists: bool
    solver_result: str
    argument_count: int
    attack_count: int
    residual_argument_count: int
    residual_attack_count: int
    core_argument_ids: tuple[str, ...]
    core_attack_ids: tuple[tuple[str, str], ...]
    coverage_argument_ids: tuple[str, ...]
    requirement_argument_ids: tuple[str, ...]
    clause_group_count: int
    runtime_seconds: float
    simplification_fixed_in_count: int
    simplification_fixed_out_count: int
    model_extension_size: int | None = None
    model_extension_fingerprint: str | None = None
    metadata: Mapping[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "stable_exists": self.stable_exists,
            "solver_result": self.solver_result,
            "argument_count": self.argument_count,
            "attack_count": self.attack_count,
            "residual_argument_count": self.residual_argument_count,
            "residual_attack_count": self.residual_attack_count,
            "core_argument_ids": list(self.core_argument_ids),
            "core_attack_ids": [list(edge) for edge in self.core_attack_ids],
            "coverage_argument_ids": list(self.coverage_argument_ids),
            "requirement_argument_ids": list(self.requirement_argument_ids),
            "clause_group_count": self.clause_group_count,
            "runtime_seconds": self.runtime_seconds,
            "simplification_fixed_in_count": self.simplification_fixed_in_count,
            "simplification_fixed_out_count": self.simplification_fixed_out_count,
            "model_extension_size": self.model_extension_size,
            "model_extension_fingerprint": self.model_extension_fingerprint,
            "metadata": dict(self.metadata or {}),
        }


class AfSatKernel:
    """Reusable SAT state for one Dung AF.

    ``engine`` selects the Z3 solver core: ``"smt"`` (default, the general
    solver) or ``"sat-core"`` (the CDCL-style ``Tactic('sat')`` solver, which
    is orders of magnitude faster on the purely propositional labelling
    encodings but does not support pseudo-Boolean range constraints).
    """

    def __init__(
        self,
        framework: ArgumentationFramework,
        *,
        trace_sink: SATTraceSink | None = None,
        metadata: Mapping[str, object] | None = None,
        check_budget_seconds: float | None = None,
        engine: str = "smt",
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata
        self.check_budget_seconds = check_budget_seconds
        self.z3 = _load_z3()
        self.solver = _make_solver(self.z3, engine)
        _apply_check_budget(self.solver, check_budget_seconds)
        self.arguments = tuple(sorted(framework.arguments))
        self.in_vars = {
            argument: self.z3.Bool(f"af_in_{index}")
            for index, argument in enumerate(self.arguments)
        }
        self.out_vars = {
            argument: self.z3.Bool(f"af_out_{index}")
            for index, argument in enumerate(self.arguments)
        }
        self.range_vars = {
            argument: self.z3.Bool(f"af_range_{index}")
            for index, argument in enumerate(self.arguments)
        }
        self.attackers_index = predecessors_index(framework.defeats)
        self._added: set[str] = set()

    @property
    def conflict_relation(self) -> frozenset[tuple[str, str]]:
        return self.framework.attacks if self.framework.attacks is not None else self.framework.defeats

    def add_conflict_free(self) -> None:
        if "conflict_free" in self._added:
            return
        for attacker, target in sorted(self.conflict_relation):
            self.solver.add(
                self.z3.Or(
                    self.z3.Not(self.in_vars[attacker]),
                    self.z3.Not(self.in_vars[target]),
                )
            )
        self._added.add("conflict_free")

    def add_admissible_labelling(self) -> None:
        if "admissible" in self._added:
            return
        self.add_conflict_free()
        for argument in self.arguments:
            attackers = tuple(sorted(self.attackers_index.get(argument, frozenset())))
            self.solver.add(
                self.out_vars[argument]
                == (
                    self.z3.Or(*(self.in_vars[attacker] for attacker in attackers))
                    if attackers
                    else self.z3.BoolVal(False)
                )
            )
        for argument in self.arguments:
            for attacker in sorted(self.attackers_index.get(argument, frozenset())):
                self.solver.add(
                    self.z3.Implies(self.in_vars[argument], self.out_vars[attacker])
                )
        self._added.add("admissible")

    def add_complete_labelling(self) -> None:
        if "complete" in self._added:
            return
        for argument in self.arguments:
            self.solver.add(
                self.z3.Not(self.z3.And(self.in_vars[argument], self.out_vars[argument]))
            )

        for argument in self.arguments:
            attackers = tuple(sorted(self.attackers_index.get(argument, frozenset())))
            if attackers:
                self.solver.add(
                    self.in_vars[argument]
                    == self.z3.And(*(self.out_vars[attacker] for attacker in attackers))
                )
                self.solver.add(
                    self.out_vars[argument]
                    == self.z3.Or(*(self.in_vars[attacker] for attacker in attackers))
                )
            else:
                self.solver.add(self.in_vars[argument])
                self.solver.add(self.z3.Not(self.out_vars[argument]))

        self.add_conflict_free()
        self._added.add("complete")

    def add_stable_coverage(self) -> None:
        if "stable" in self._added:
            return
        self.add_conflict_free()
        for argument in self.arguments:
            attackers = tuple(sorted(self.attackers_index.get(argument, frozenset())))
            self.solver.add(
                self.z3.Or(
                    self.in_vars[argument],
                    *(self.in_vars[attacker] for attacker in attackers),
                )
            )
        self._added.add("stable")

    def add_range_definition(self) -> None:
        if "range" in self._added:
            return
        for argument in self.arguments:
            range_sources = [
                self.in_vars[argument],
                *(
                    self.in_vars[attacker]
                    for attacker in sorted(self.attackers_index.get(argument, frozenset()))
                ),
            ]
            self.solver.add(self.range_vars[argument] == self.z3.Or(*range_sources))
        self._added.add("range")

    def require_in(self, arguments: frozenset[str]) -> None:
        self._validate(arguments)
        for argument in sorted(arguments):
            self.solver.add(self.in_vars[argument])

    def require_out(self, arguments: frozenset[str]) -> None:
        self._validate(arguments)
        for argument in sorted(arguments):
            self.solver.add(self.z3.Not(self.in_vars[argument]))

    def require_any_in(self, arguments: frozenset[str]) -> None:
        self._validate(arguments)
        if arguments:
            self.solver.add(
                self.z3.Or(*(self.in_vars[argument] for argument in sorted(arguments)))
            )

    def require_range(self, arguments: frozenset[str]) -> None:
        self._validate(arguments)
        self.add_range_definition()
        for argument in sorted(arguments):
            self.solver.add(self.range_vars[argument])

    def require_any_range(self, arguments: frozenset[str]) -> None:
        self._validate(arguments)
        self.add_range_definition()
        if arguments:
            self.solver.add(
                self.z3.Or(*(self.range_vars[argument] for argument in sorted(arguments)))
            )

    def require_range_size_at_least(self, size: int) -> None:
        self._validate_range_size(size)
        self.add_range_definition()
        self.solver.add(
            self.z3.PbGe(
                [(self.range_vars[argument], 1) for argument in self.arguments],
                size,
            )
        )

    def require_range_size_exactly(self, size: int) -> None:
        self._validate_range_size(size)
        self.add_range_definition()
        self.solver.add(
            self.z3.PbEq(
                [(self.range_vars[argument], 1) for argument in self.arguments],
                size,
            )
        )

    def require_attacks_any(self, targets: frozenset[str]) -> None:
        self._validate(targets)
        attackers = frozenset(
            attacker
            for attacker, target in self.framework.defeats
            if target in targets
        )
        if attackers:
            self.require_any_in(attackers)
        else:
            self.solver.add(self.z3.BoolVal(False))

    def exclude_extension(self, extension: frozenset[str]) -> None:
        self._validate(extension)
        self.solver.add(
            self.z3.Or(*(self.z3.Not(self.in_vars[argument]) for argument in sorted(extension)))
        )

    def exclude_exact_extension(self, extension: frozenset[str]) -> None:
        self._validate(extension)
        literals = [
            self.z3.Not(self.in_vars[argument])
            for argument in sorted(extension)
        ]
        literals.extend(
            self.in_vars[argument]
            for argument in self.arguments
            if argument not in extension
        )
        self.solver.add(self.z3.Or(*literals))

    def exclude_range_subset(self, range_set: frozenset[str]) -> None:
        self._validate(range_set)
        self.add_range_definition()
        outside = self.framework.arguments - range_set
        if outside:
            self.require_any_range(outside)
        else:
            self.solver.add(self.z3.BoolVal(False))

    def check(
        self,
        utility_name: str,
        assumptions: tuple[Any, ...] = (),
        *,
        range_bound: int | None = None,
        range_constraint: str | None = None,
        loop_index: int | None = None,
        learned_count: int | None = None,
    ) -> str:
        started = perf_counter()
        result_ref = self.solver.check(*assumptions)
        elapsed_ms = (perf_counter() - started) * 1000
        result = str(result_ref)
        model_size = None
        model_fingerprint = None
        if result == "sat":
            extension = self.model_extension()
            model_size = len(extension)
            model_fingerprint = _extension_fingerprint(extension)
        if self.trace_sink is not None:
            self.trace_sink(
                SATCheck(
                    utility_name=utility_name,
                    result=result,
                    elapsed_ms=elapsed_ms,
                    assumptions_count=len(assumptions),
                    argument_count=len(self.framework.arguments),
                    attack_count=len(self.framework.defeats),
                    model_extension_size=model_size,
                    model_extension_fingerprint=model_fingerprint,
                    loop_index=loop_index,
                    learned_count=learned_count,
                    range_bound=range_bound,
                    range_constraint=range_constraint,
                    metadata=self.metadata,
                )
            )
        if result not in ("sat", "unsat"):
            raise AfSatCheckTimeout(
                utility_name,
                check_budget_seconds=self.check_budget_seconds,
            )
        return result

    def model_extension(self) -> frozenset[str]:
        model = self.solver.model()
        return frozenset(
            argument
            for argument, variable in self.in_vars.items()
            if self.z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def model_range(self) -> frozenset[str]:
        self.add_range_definition()
        model = self.solver.model()
        return frozenset(
            argument
            for argument, variable in self.range_vars.items()
            if self.z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def model_range_size(self) -> int:
        return len(self.model_range())

    def _validate(self, arguments: frozenset[str]) -> None:
        unknown = sorted(arguments - self.framework.arguments)
        if unknown:
            raise ValueError(f"unknown arguments: {unknown!r}")

    def _validate_range_size(self, size: int) -> None:
        if size < 0 or size > len(self.arguments):
            raise ValueError(f"range size {size!r} outside 0..{len(self.arguments)}")


@dataclass(frozen=True)
class _PreparedAfSat:
    residual: ArgumentationFramework
    reduct: SemanticReduct[ArgumentationFramework, str]
    required_in: frozenset[str]
    required_out: frozenset[str]

    def lift(self, extension: frozenset[str] | None) -> frozenset[str] | None:
        return None if extension is None else self.reduct.lift(extension)


def _prepare(
    framework: ArgumentationFramework,
    semantics: str,
    *,
    simplify: bool,
    require_in: str | None,
    require_out: str | None,
) -> _PreparedAfSat | None:
    """Apply the AF preprocessing layer to a single-extension finder.

    Returns ``None`` when the constraints are already unsatisfiable on the fixed
    part (e.g. ``require_in`` is forced OUT, or ``require_out`` is forced IN).
    """
    # Validate before simplifying so unknown arguments still raise.
    required_in = _optional_argument(framework, require_in)
    required_out = _optional_argument(framework, require_out)
    if not simplify:
        reduct = SemanticReduct(framework, framework, frozenset(), frozenset())
        return _PreparedAfSat(framework, reduct, required_in, required_out)
    reduct = simplify_af(framework, semantics=semantics)
    projection = reduct.project_requirements(
        required_in=required_in,
        required_out=required_out,
    )
    if projection is None:
        return None
    residual_required_in, residual_required_out = projection
    return _PreparedAfSat(
        reduct.residual,
        reduct,
        residual_required_in,
        residual_required_out,
    )


def find_stable_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
    engine: str = "smt",
) -> frozenset[str] | None:
    prepared = _prepare(
        framework, "stable", simplify=simplify, require_in=require_in, require_out=require_out
    )
    if prepared is None:
        return None
    problem = AfSatKernel(
        prepared.residual,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=engine,
    )
    problem.add_stable_coverage()
    problem.require_in(prepared.required_in)
    problem.require_out(prepared.required_out)
    if problem.check("stable_extension") != "sat":
        return None
    return prepared.lift(problem.model_extension())


def explain_stable_unsat(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    simplify: bool = True,
    metadata: Mapping[str, object] | None = None,
    check_budget_seconds: float | None = None,
) -> StableUnsatExplanation:
    """Return a tracked-clause explanation for stable-extension SAT/UNSAT.

    This is a diagnostic API, not a replacement for :func:`find_stable_extension`.
    It tracks stable constraints by semantic group and returns the solver's unsat
    core when the stable-extension encoding is UNSAT. The core is not guaranteed
    minimal, so callers should treat it as an obstruction surface rather than a
    smallest proof.
    """
    started = perf_counter()
    prepared = _prepare(
        framework, "stable", simplify=simplify, require_in=require_in, require_out=require_out
    )
    if prepared is None:
        return StableUnsatExplanation(
            status="unsat_preprocessing",
            stable_exists=False,
            solver_result="unsat",
            argument_count=len(framework.arguments),
            attack_count=len(framework.defeats),
            residual_argument_count=0,
            residual_attack_count=0,
            core_argument_ids=tuple(),
            core_attack_ids=tuple(),
            coverage_argument_ids=tuple(),
            requirement_argument_ids=tuple(sorted(arg for arg in (require_in, require_out) if arg is not None)),
            clause_group_count=0,
            runtime_seconds=perf_counter() - started,
            simplification_fixed_in_count=0,
            simplification_fixed_out_count=0,
            metadata=metadata,
        )

    residual = prepared.residual
    z3 = _load_z3()
    solver = z3.Solver()
    _apply_check_budget(solver, check_budget_seconds)
    arguments = tuple(sorted(residual.arguments))
    in_vars = {argument: z3.Bool(f"af_in_{index}") for index, argument in enumerate(arguments)}
    attackers_index = predecessors_index(residual.defeats)
    label_map: dict[str, tuple[str, object]] = {}

    def track(kind: str, payload: object, expression: object) -> None:
        label = z3.Bool(f"stable_{kind}_{len(label_map)}")
        label_map[str(label)] = (kind, payload)
        solver.assert_and_track(expression, label)

    conflict_relation = residual.attacks if residual.attacks is not None else residual.defeats
    for attacker, target in sorted(conflict_relation):
        track(
            "conflict",
            (attacker, target),
            z3.Or(z3.Not(in_vars[attacker]), z3.Not(in_vars[target])),
        )

    for argument in arguments:
        attackers = tuple(sorted(attackers_index.get(argument, frozenset())))
        track(
            "coverage",
            argument,
            z3.Or(in_vars[argument], *(in_vars[attacker] for attacker in attackers)),
        )

    for argument in sorted(prepared.required_in):
        track("require_in", argument, in_vars[argument])
    for argument in sorted(prepared.required_out):
        track("require_out", argument, z3.Not(in_vars[argument]))

    result_ref = solver.check()
    runtime_seconds = perf_counter() - started
    solver_result = str(result_ref)
    model_size = None
    model_fingerprint = None
    core_attacks: set[tuple[str, str]] = set()
    coverage_arguments: set[str] = set()
    requirement_arguments: set[str] = set()

    if solver_result == "sat":
        extension = frozenset(
            argument
            for argument, variable in in_vars.items()
            if z3.is_true(solver.model().evaluate(variable, model_completion=True))
        )
        lifted_extension = prepared.reduct.lift(extension)
        model_size = len(lifted_extension)
        model_fingerprint = _extension_fingerprint(lifted_extension)
    elif solver_result == "unsat":
        for item in solver.unsat_core():
            mapped = label_map.get(str(item))
            if mapped is None:
                continue
            kind, payload = mapped
            if kind == "conflict" and isinstance(payload, tuple) and len(payload) == 2:
                attacker, target = payload
                core_attacks.add((str(attacker), str(target)))
            elif kind == "coverage":
                coverage_arguments.add(str(payload))
            elif kind in {"require_in", "require_out"}:
                requirement_arguments.add(str(payload))

    core_arguments = set(coverage_arguments) | requirement_arguments
    for attacker, target in core_attacks:
        core_arguments.add(attacker)
        core_arguments.add(target)

    status = "sat" if solver_result == "sat" else ("unsat" if solver_result == "unsat" else "unknown")
    return StableUnsatExplanation(
        status=status,
        stable_exists=solver_result == "sat",
        solver_result=solver_result,
        argument_count=len(framework.arguments),
        attack_count=len(framework.defeats),
        residual_argument_count=len(residual.arguments),
        residual_attack_count=len(residual.defeats),
        core_argument_ids=tuple(sorted(core_arguments)),
        core_attack_ids=tuple(sorted(core_attacks)),
        coverage_argument_ids=tuple(sorted(coverage_arguments)),
        requirement_argument_ids=tuple(sorted(requirement_arguments)),
        clause_group_count=len(label_map),
        runtime_seconds=runtime_seconds,
        simplification_fixed_in_count=len(prepared.reduct.fixed_in),
        simplification_fixed_out_count=len(prepared.reduct.fixed_out),
        model_extension_size=model_size,
        model_extension_fingerprint=model_fingerprint,
        metadata=metadata,
    )


def find_complete_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
    engine: str = "smt",
) -> frozenset[str] | None:
    prepared = _prepare(
        framework, "complete", simplify=simplify, require_in=require_in, require_out=require_out
    )
    if prepared is None:
        return None
    problem = AfSatKernel(
        prepared.residual,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=engine,
    )
    problem.add_complete_labelling()
    extension = _complete_extension(
        problem,
        required_in=prepared.required_in,
        required_out=prepared.required_out,
        utility_name="complete_extension",
    )
    return prepared.lift(extension)


def find_preferred_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
) -> frozenset[str] | None:
    prepared = _prepare(
        framework, "preferred", simplify=simplify, require_in=require_in, require_out=require_out
    )
    if prepared is None:
        return None
    problem = AfSatKernel(
        prepared.residual,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    problem.add_complete_labelling()
    result = _find_preferred_extension_body(
        problem,
        prepared.residual,
        prepared.required_in,
        prepared.required_out,
    )
    return prepared.lift(result)


def _find_preferred_extension_body(
    problem: AfSatKernel,
    framework: ArgumentationFramework,
    required_in: frozenset[str],
    required_out: frozenset[str],
) -> frozenset[str] | None:
    current = _complete_extension(
        problem,
        required_in=required_in,
        required_out=required_out,
        utility_name="preferred_seed",
    )
    if current is None:
        return None
    if not required_out:
        return _grow_preferred(problem, framework, current)

    blocked_seeds: list[frozenset[str]] = []
    while True:
        preferred = _grow_preferred(problem, framework, current)
        if preferred is not None and required_out.isdisjoint(preferred):
            return preferred

        blocked_seeds.append(current)
        problem.solver.push()
        try:
            problem.require_in(required_in)
            problem.require_out(required_out)
            for blocked_seed in blocked_seeds:
                problem.exclude_exact_extension(blocked_seed)
            if problem.check("preferred_next_constrained_seed") != "sat":
                return None
            current = problem.model_extension()
        finally:
            problem.solver.pop()


def is_preferred_skeptically_accepted(
    framework: ArgumentationFramework,
    query: str,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
    engine: str = "smt",
) -> bool:
    """Decide preferred skeptical acceptance using CDAS admissibility checks."""
    _optional_argument(framework, query)
    if simplify:
        simplification = simplify_af(framework, semantics="preferred")
        if query in simplification.fixed_in:
            _emit_preprocessing_shortcut(
                framework, trace_sink, metadata, "preferred_skeptical_preprocessing_grounded_in", accepted=True
            )
            return True
        if query in simplification.fixed_out:
            _emit_preprocessing_shortcut(
                framework, trace_sink, metadata, "preferred_skeptical_preprocessing_forced_out", accepted=False
            )
            return False
        framework = simplification.residual
    return PreferredSkepticalTaskSolver(
        framework,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
        engine=engine,
    ).decide(query)


class PreferredSkepticalTaskSolver:
    """CDAS skeptical preferred acceptance solver for one AF.

    The decide loop is Algorithm 2 (CDAS) of Thimm/Cerutti/Vallati, IJCAI-21:
    seed = ``AdmExt(AF, {query})``; then repeat ``AdmExtAtt`` (an admissible
    attacker of an admissible query-superset, excluding attackers contained in
    any stored witness) -> unsat means accepted; ``AdmExt(attacker | {query})``
    -> unsat means rejected; otherwise store the extended witness. Complete
    extensions stand in for admissible ones (existence-equivalent via Dung's
    fundamental lemma). The shortcut ladder and the super-core precheck are
    answer-preserving additions in front of the paper's loop; the loop itself
    performs no ``AdmSup`` maximisation.
    """

    def __init__(
        self,
        framework: ArgumentationFramework,
        *,
        trace_sink: SATTraceSink | None = None,
        metadata: Mapping[str, object] | None = None,
        check_budget_seconds: float | None = None,
        engine: str = "smt",
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata
        self.check_budget_seconds = check_budget_seconds
        self.engine = engine

    def decide(self, query: str) -> bool:
        required_query = _optional_argument(self.framework, query)
        shortcut = self._shortcut(query)
        if shortcut is not None:
            return shortcut

        super_core = PreferredSuperCoreSolver(
            self.framework,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
            check_budget_seconds=self.check_budget_seconds,
            engine=self.engine,
        ).compute()
        if required_query and required_query <= super_core:
            return True

        extension_problem = AfSatKernel(
            self.framework,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
            check_budget_seconds=self.check_budget_seconds,
            engine=self.engine,
        )
        extension_problem.add_complete_labelling()
        seed = _complete_extension(
            extension_problem,
            required_in=required_query,
            utility_name="preferred_skeptical_seed",
        )
        if seed is None:
            return False

        attacker_problem = _PreferredSkepticalAttackerSolver(
            self.framework,
            required_in=required_query,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
            check_budget_seconds=self.check_budget_seconds,
            engine=self.engine,
        )
        loop_index = 0
        while True:
            attacker = attacker_problem.find_attacker(loop_index=loop_index)
            if attacker is None:
                return True
            extended = _complete_extension(
                extension_problem,
                required_in=attacker | required_query,
                utility_name="preferred_skeptical_extend_attacker",
                loop_index=loop_index,
                learned_count=attacker_problem.learned_count,
            )
            if extended is None:
                return False
            attacker_problem.learn_witness_region(extended, loop_index=loop_index)
            loop_index += 1

    def _shortcut(self, query: str) -> bool | None:
        if (query, query) in self.framework.defeats:
            self._emit_shortcut("preferred_skeptical_shortcut_self_attacking_query", False)
            return False
        attackers = self._attackers_of(query)
        if not attackers:
            self._emit_shortcut("preferred_skeptical_shortcut_unattacked_query", True)
            return True
        grounded = grounded_extension(self.framework)
        if query in grounded:
            self._emit_shortcut("preferred_skeptical_shortcut_grounded_in", True)
            return True
        if query in _attacked_by(grounded, self.framework.defeats):
            self._emit_shortcut("preferred_skeptical_shortcut_grounded_attacked", False)
            return False
        if _is_acyclic(self.framework):
            accepted = query in grounded_extension(self.framework)
            self._emit_shortcut("preferred_skeptical_shortcut_acyclic_grounded", accepted)
            return accepted
        return None

    def _attackers_of(self, query: str) -> frozenset[str]:
        return frozenset(
            attacker
            for attacker, target in self.framework.defeats
            if target == query
        )

    def _emit_shortcut(self, utility_name: str, accepted: bool) -> None:
        if self.trace_sink is None:
            return
        self.trace_sink(
            SATCheck(
                utility_name=utility_name,
                result="accepted" if accepted else "rejected",
                elapsed_ms=0.0,
                assumptions_count=0,
                argument_count=len(self.framework.arguments),
                attack_count=len(self.framework.defeats),
                metadata=self.metadata,
            )
        )


class PreferredSuperCoreSolver:
    """Conservative admissibility-backed core contained in every preferred extension."""

    def __init__(
        self,
        framework: ArgumentationFramework,
        *,
        trace_sink: SATTraceSink | None = None,
        metadata: Mapping[str, object] | None = None,
        check_budget_seconds: float | None = None,
        engine: str = "smt",
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata
        self.check_budget_seconds = check_budget_seconds
        self.engine = engine

    def compute(self) -> frozenset[str]:
        problem = AfSatKernel(
            self.framework,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
            check_budget_seconds=self.check_budget_seconds,
            engine=self.engine,
        )
        problem.add_admissible_labelling()
        current = self.framework.arguments
        while True:
            attacker = _admissible_attacker_of_set(
                problem,
                current,
                utility_name="preferred_super_core_admissible_attacker",
            )
            if attacker is None:
                break
            current = current - _attacked_by(attacker, self.framework.defeats)

        return _prune_to_admissible_subset(current, self.framework.defeats)


def find_semi_stable_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
) -> frozenset[str] | None:
    return _find_range_maximal_task_extension(
        framework,
        semantics="semi-stable",
        base="complete",
        label="semi_stable",
        require_in=require_in,
        require_out=require_out,
        trace_sink=trace_sink,
        metadata=metadata,
        simplify=simplify,
        check_budget_seconds=check_budget_seconds,
    )


def _find_range_maximal_task_extension(
    framework: ArgumentationFramework,
    *,
    semantics: str,
    base: str,
    label: str,
    require_in: str | None,
    require_out: str | None,
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
    simplify: bool,
    check_budget_seconds: float | None,
) -> frozenset[str] | None:
    """Shared preprocessing + fragment dispatch + range-maximal search.

    Both range-maximal semantics (semi-stable on the complete base, stage on
    the conflict-free base) run the same pipeline: semantics-aware
    simplification, the acyclic fragment dispatch, and only then the SAT
    kernel with the range-maximal CEGAR loop (which itself starts with the
    stable-first dispatch).
    """
    prepared = _prepare(
        framework, semantics, simplify=simplify, require_in=require_in, require_out=require_out
    )
    if prepared is None:
        return None
    handled, acyclic_answer = _acyclic_fragment_answer(
        prepared,
        utility_name=f"{label}_acyclic_grounded",
        trace_sink=trace_sink,
        metadata=metadata,
    )
    if handled:
        return prepared.lift(acyclic_answer)
    problem = AfSatKernel(
        prepared.residual,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    if base == "complete":
        problem.add_complete_labelling()
    elif base == "conflict_free":
        problem.add_conflict_free()
    else:
        raise ValueError(f"unknown SAT base semantics: {base!r}")
    problem.add_range_definition()
    extension = _range_maximal_extension(
        problem,
        prepared.residual,
        base=base,
        required_in=prepared.required_in,
        required_out=prepared.required_out,
        seed_utility_name=f"{label}_seed",
        test_utility_name=f"{label}_range_maximality",
    )
    return prepared.lift(extension)


def find_ideal_extension(
    framework: ArgumentationFramework,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
) -> frozenset[str]:
    if simplify:
        simplification = simplify_af(framework, semantics="ideal")
        if not simplification.is_trivial:
            residual_ideal = find_ideal_extension(
                simplification.residual,
                trace_sink=trace_sink,
                metadata=metadata,
                simplify=False,
                check_budget_seconds=check_budget_seconds,
            )
            return simplification.lift(residual_ideal)
    problem = AfSatKernel(
        framework,
        trace_sink=trace_sink,
        metadata=metadata,
        check_budget_seconds=check_budget_seconds,
    )
    problem.add_admissible_labelling()
    current = framework.arguments
    while True:
        attacker = _admissible_attacker_of_set(
            problem,
            current,
            utility_name="ideal_admissible_attacker",
        )
        if attacker is None:
            break
        current = current - _attacked_by(attacker, framework.defeats)

    return _prune_to_admissible_subset(current, framework.defeats)


def find_stage_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
    simplify: bool = True,
    check_budget_seconds: float | None = None,
) -> frozenset[str] | None:
    return _find_range_maximal_task_extension(
        framework,
        semantics="stage",
        base="conflict_free",
        label="stage",
        require_in=require_in,
        require_out=require_out,
        trace_sink=trace_sink,
        metadata=metadata,
        simplify=simplify,
        check_budget_seconds=check_budget_seconds,
    )


def _run_extension(
    problem: AfSatKernel,
    *,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    require_any_in: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
    required_range_size: int | None = None,
    required_range_size_at_least: int | None = None,
    excluded_exact: list[frozenset[str]] | None = None,
    excluded_range_subsets: list[frozenset[str]] | None = None,
    utility_name: str,
    loop_index: int | None = None,
    learned_count: int | None = None,
) -> frozenset[str] | None:
    """Push assumptions, check, and recover a model on the pre-encoded kernel.

    Shared push/require/check/pop orchestration for both the complete and
    conflict-free helpers. The base semantics (complete vs conflict-free) are
    established on ``problem`` *before* this runs, so this helper is agnostic to
    them: it only threads the per-call assumptions. ``require_any_in`` is a
    no-op when empty, and ``loop_index``/``learned_count`` only annotate the
    trace, so conflict-free callers that omit them are unaffected.
    """
    problem.solver.push()
    try:
        problem.require_in(required_in)
        problem.require_out(required_out)
        problem.require_any_in(require_any_in)
        problem.require_range(required_range)
        problem.require_any_range(require_any_range)
        range_bound, range_constraint = _apply_range_size_constraints(
            problem,
            required_range_size=required_range_size,
            required_range_size_at_least=required_range_size_at_least,
        )
        if range_bound is None and required_range:
            range_bound = len(required_range)
            range_constraint = "contains"
        for blocked in excluded_exact or []:
            problem.exclude_exact_extension(blocked)
        for blocked_range in excluded_range_subsets or []:
            problem.exclude_range_subset(blocked_range)
        if problem.check(
            utility_name,
            range_bound=range_bound,
            range_constraint=range_constraint,
            loop_index=loop_index,
            learned_count=learned_count,
        ) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


def _complete_extension(
    problem: AfSatKernel,
    *,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    require_any_in: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
    required_range_size: int | None = None,
    required_range_size_at_least: int | None = None,
    excluded_exact: list[frozenset[str]] | None = None,
    excluded_range_subsets: list[frozenset[str]] | None = None,
    utility_name: str,
    loop_index: int | None = None,
    learned_count: int | None = None,
) -> frozenset[str] | None:
    return _run_extension(
        problem,
        required_in=required_in,
        required_out=required_out,
        require_any_in=require_any_in,
        required_range=required_range,
        require_any_range=require_any_range,
        required_range_size=required_range_size,
        required_range_size_at_least=required_range_size_at_least,
        excluded_exact=excluded_exact,
        excluded_range_subsets=excluded_range_subsets,
        utility_name=utility_name,
        loop_index=loop_index,
        learned_count=learned_count,
    )


def _admissible_extension(
    problem: AfSatKernel,
    *,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    require_any_in: frozenset[str] = frozenset(),
    utility_name: str,
    loop_index: int | None = None,
    learned_count: int | None = None,
) -> frozenset[str] | None:
    problem.solver.push()
    try:
        problem.require_in(required_in)
        problem.require_out(required_out)
        problem.require_any_in(require_any_in)
        if problem.check(
            utility_name,
            loop_index=loop_index,
            learned_count=learned_count,
        ) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


def _admissible_attacker_of_set(
    problem: AfSatKernel,
    targets: frozenset[str],
    *,
    utility_name: str,
) -> frozenset[str] | None:
    if not targets:
        return None
    problem.solver.push()
    try:
        problem.require_attacks_any(targets)
        if problem.check(utility_name) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


class _PreferredSkepticalAttackerSolver:
    def __init__(
        self,
        framework: ArgumentationFramework,
        *,
        required_in: frozenset[str],
        trace_sink: SATTraceSink | None,
        metadata: Mapping[str, object] | None,
        check_budget_seconds: float | None = None,
        engine: str = "smt",
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata
        self.check_budget_seconds = check_budget_seconds
        self.z3 = _load_z3()
        self.solver = _make_solver(self.z3, engine)
        _apply_check_budget(self.solver, check_budget_seconds)
        self.arguments = tuple(sorted(framework.arguments))
        self.attacker_vars = {
            argument: self.z3.Bool(f"af_cdas_attacker_{index}")
            for index, argument in enumerate(self.arguments)
        }
        self.candidate_vars = {
            argument: self.z3.Bool(f"af_cdas_candidate_{index}")
            for index, argument in enumerate(self.arguments)
        }
        self.learned_count = 0

        _add_admissible_constraints(self.z3, self.solver, framework, self.attacker_vars)
        _add_admissible_constraints(self.z3, self.solver, framework, self.candidate_vars)
        for argument in sorted(required_in):
            self.solver.add(self.candidate_vars[argument])

        attack_pairs = [
            self.z3.And(self.attacker_vars[attacker], self.candidate_vars[target])
            for attacker, target in sorted(framework.defeats)
        ]
        self.solver.add(self.z3.Or(*attack_pairs) if attack_pairs else self.z3.BoolVal(False))

    def find_attacker(self, *, loop_index: int) -> frozenset[str] | None:
        started = perf_counter()
        result_ref = self.solver.check()
        elapsed_ms = (perf_counter() - started) * 1000
        result = str(result_ref)
        extension = None
        if result == "sat":
            extension = self.model_extension()
        if self.trace_sink is not None:
            self.trace_sink(
                SATCheck(
                    utility_name="preferred_skeptical_adm_ext_att",
                    result=result,
                    elapsed_ms=elapsed_ms,
                    assumptions_count=0,
                    argument_count=len(self.framework.arguments),
                    attack_count=len(self.framework.defeats),
                    model_extension_size=None if extension is None else len(extension),
                    model_extension_fingerprint=(
                        None if extension is None else _extension_fingerprint(extension)
                    ),
                    loop_index=loop_index,
                    learned_count=self.learned_count,
                    metadata=self.metadata,
                )
            )
        if result not in ("sat", "unsat"):
            raise AfSatCheckTimeout(
                "preferred_skeptical_adm_ext_att",
                check_budget_seconds=self.check_budget_seconds,
            )
        return extension

    def model_extension(self) -> frozenset[str]:
        model = self.solver.model()
        return frozenset(
            argument
            for argument, variable in self.attacker_vars.items()
            if self.z3.is_true(model.evaluate(variable, model_completion=True))
        )

    def learn_witness_region(self, extension: frozenset[str], *, loop_index: int) -> None:
        outside = self.framework.arguments - extension
        if outside:
            self.solver.add(
                self.z3.Or(*(self.attacker_vars[argument] for argument in sorted(outside)))
            )
        else:
            self.solver.add(self.z3.BoolVal(False))
        self.learned_count += 1
        if self.trace_sink is not None:
            self.trace_sink(
                SATCheck(
                    utility_name="preferred_skeptical_learn_witness_region",
                    result="learned",
                    elapsed_ms=0.0,
                    assumptions_count=0,
                    argument_count=len(self.framework.arguments),
                    attack_count=len(self.framework.defeats),
                    model_extension_size=len(extension),
                    model_extension_fingerprint=_extension_fingerprint(extension),
                    loop_index=loop_index,
                    learned_count=self.learned_count,
                    metadata=self.metadata,
                )
            )


def _emit_preprocessing_shortcut(
    framework: ArgumentationFramework,
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
    utility_name: str,
    *,
    accepted: bool,
) -> None:
    if trace_sink is None:
        return
    trace_sink(
        SATCheck(
            utility_name=utility_name,
            result="accepted" if accepted else "rejected",
            elapsed_ms=0.0,
            assumptions_count=0,
            argument_count=len(framework.arguments),
            attack_count=len(framework.defeats),
            metadata=metadata,
        )
    )


def _attacked_by(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    return frozenset(target for attacker, target in defeats if attacker in arguments)


def _attackers_of(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    return frozenset(attacker for attacker, target in defeats if target in arguments)


def _prune_to_admissible_subset(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    current = arguments - _attacked_by(arguments, defeats)
    while True:
        defended_attackers = _attacked_by(current, defeats)
        undefended_attackers = _attackers_of(current, defeats) - defended_attackers
        next_current = current - _attacked_by(undefended_attackers, defeats)
        if next_current == current:
            return current
        current = next_current


def _add_admissible_constraints(
    z3,
    solver,
    framework: ArgumentationFramework,
    in_vars: Mapping[str, Any],
) -> None:
    conflict_relation = framework.attacks if framework.attacks is not None else framework.defeats
    for attacker, target in sorted(conflict_relation):
        solver.add(z3.Or(z3.Not(in_vars[attacker]), z3.Not(in_vars[target])))

    attackers_index = predecessors_index(framework.defeats)
    defense_by_attacker: dict[str, Any] = {}
    undefended_attackers: set[str] = set()
    for argument in sorted(framework.arguments):
        defenders = tuple(sorted(attackers_index.get(argument, frozenset())))
        if defenders:
            defense_by_attacker[argument] = z3.Or(
                *(in_vars[defender] for defender in defenders)
            )
        else:
            undefended_attackers.add(argument)
    for argument in sorted(framework.arguments):
        attackers = tuple(sorted(attackers_index.get(argument, frozenset())))
        if not attackers:
            continue
        if any(attacker in undefended_attackers for attacker in attackers):
            solver.add(z3.Not(in_vars[argument]))
            continue
        defense_requirements = tuple(defense_by_attacker[attacker] for attacker in attackers)
        defended = (
            defense_requirements[0]
            if len(defense_requirements) == 1
            else z3.And(*defense_requirements)
        )
        solver.add(z3.Implies(in_vars[argument], defended))


def _grow_preferred(
    problem: AfSatKernel,
    framework: ArgumentationFramework,
    seed: frozenset[str],
    *,
    utility_name: str = "preferred_grow",
    loop_index: int | None = None,
    learned_count: int | None = None,
) -> frozenset[str] | None:
    current = seed
    while True:
        outside = framework.arguments - current
        if not outside:
            return current
        larger = _complete_extension(
            problem,
            required_in=current,
            require_any_in=outside,
            utility_name=utility_name,
            loop_index=loop_index,
            learned_count=learned_count,
        )
        if larger is None:
            return current
        if not current < larger:
            raise RuntimeError("SAT preferred growth did not produce a strict superset")
        current = larger


def _range_maximal_extension(
    problem: AfSatKernel,
    framework: ArgumentationFramework,
    *,
    base: str,
    required_in: frozenset[str],
    required_out: frozenset[str],
    seed_utility_name: str,
    test_utility_name: str,
) -> frozenset[str] | None:
    del framework
    return RangeMaximalTaskSolver(
        problem=problem,
        base=base,
        seed_utility_name=seed_utility_name,
        test_utility_name=test_utility_name,
    ).find_extension(
        required_in=required_in,
        required_out=required_out,
    )


def _emit_fragment_shortcut(
    trace_sink: SATTraceSink | None,
    framework: ArgumentationFramework,
    *,
    utility_name: str,
    extension: frozenset[str] | None,
    metadata: Mapping[str, object] | None,
) -> None:
    """Emit an oracle-free fragment-dispatch decision into the SAT trace."""
    if trace_sink is None:
        return
    trace_sink(
        SATCheck(
            utility_name=utility_name,
            result="sat" if extension is not None else "unsat",
            elapsed_ms=0.0,
            assumptions_count=0,
            argument_count=len(framework.arguments),
            attack_count=len(framework.defeats),
            model_extension_size=None if extension is None else len(extension),
            model_extension_fingerprint=(
                None if extension is None else _extension_fingerprint(extension)
            ),
            metadata=metadata,
        )
    )


def _acyclic_fragment_answer(
    prepared: _PreparedAfSat,
    *,
    utility_name: str,
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
) -> tuple[bool, frozenset[str] | None]:
    """Dvořák 2014 acyclic-fragment dispatch for semi-stable and stage tasks.

    Derivation (experiments/2026-07-02-af-sststg-shortcuts.md, Derivation 2):
    a finite acyclic AF is well-founded, so its grounded extension is the
    unique complete extension and is stable (Dung 1995, Theorem 30). Hence it
    is also the unique semi-stable extension, and — because a stable
    extension has full range, strictly dominating every other conflict-free
    range — the unique stage extension. Gated on the conflict relation
    equalling the defeat relation: ``grounded_extension`` is defeat-based
    while the kernel's conflict-freeness is attack-based, so the equalities
    above are only established for ``attacks is None or attacks == defeats``.

    Returns ``(handled, answer)``; when ``handled`` is False the caller must
    fall back to the range-maximal SAT loop.
    """
    residual = prepared.residual
    if residual.attacks is not None and residual.attacks != residual.defeats:
        return False, None
    if not _is_acyclic(residual):
        return False, None
    grounded = grounded_extension(residual)
    satisfied = (
        prepared.required_in <= grounded
        and prepared.required_out.isdisjoint(grounded)
    )
    answer = grounded if satisfied else None
    _emit_fragment_shortcut(
        trace_sink,
        residual,
        utility_name=utility_name,
        extension=answer,
        metadata=metadata,
    )
    return True, answer


class RangeMaximalTaskSolver:
    """Exact range-maximal search for stage and semi-stable tasks."""

    shortcut_depth = 2
    shortcut_probe_limit = 24
    dense_shortcut_probe_limit = 0

    def __init__(
        self,
        *,
        problem: AfSatKernel,
        base: str,
        seed_utility_name: str,
        test_utility_name: str,
    ) -> None:
        self.problem = problem
        self.base = base
        self.seed_utility_name = seed_utility_name
        self.test_utility_name = test_utility_name

    def find_extension(
        self,
        *,
        required_in: frozenset[str],
        required_out: frozenset[str],
    ) -> frozenset[str] | None:
        if required_in or required_out:
            feasible = _base_extension(
                self.problem,
                base=self.base,
                required_in=required_in,
                required_out=required_out,
                utility_name=self._base_feasibility_utility_name(),
            )
            if feasible is None:
                return None
        decided, stable_answer = self._stable_first(
            required_in=required_in,
            required_out=required_out,
        )
        if decided:
            return stable_answer
        blocked_ranges: list[frozenset[str]] = []
        while True:
            seed = self._seed_extension(
                required_in=required_in,
                required_out=required_out,
                excluded_range_subsets=blocked_ranges,
            )
            if seed is None:
                return None
            seed_range = range_of(seed, self.problem.framework.defeats)
            if self._is_range_maximal(seed_range):
                return seed
            blocked_ranges.append(seed_range)

    def _seed_extension(
        self,
        *,
        required_in: frozenset[str],
        required_out: frozenset[str],
        excluded_range_subsets: list[frozenset[str]],
    ) -> frozenset[str] | None:
        shortcut = self._high_range_shortcut(
            required_in=required_in,
            required_out=required_out,
            excluded_range_subsets=excluded_range_subsets,
        )
        if shortcut is not None:
            return shortcut

        max_range_size, _ = _max_range_size(
            self.problem,
            base=self.base,
            required_in=required_in,
            required_out=required_out,
            excluded_range_subsets=excluded_range_subsets,
            utility_name=_max_range_utility(self.seed_utility_name, "at_least"),
        )
        if max_range_size is None:
            return None
        return _base_extension(
            self.problem,
            base=self.base,
            required_in=required_in,
            required_out=required_out,
            required_range_size=max_range_size,
            excluded_range_subsets=excluded_range_subsets,
            utility_name=_max_range_utility(self.seed_utility_name, "exact"),
        )

    def _stable_first(
        self,
        *,
        required_in: frozenset[str],
        required_out: frozenset[str],
    ) -> tuple[bool, frozenset[str] | None]:
        """Dvořák 2014 stable-first dispatch for stage and semi-stable tasks.

        Derivation (experiments/2026-07-02-af-sststg-shortcuts.md,
        Derivation 1): a full-range base extension is exactly a stable
        extension, and when one exists the range-maximal base extensions are
        exactly the full-range ones. So a query-constrained full-range
        witness is a valid answer outright, and when only the unconstrained
        full-range probe succeeds the query answer is decided as ``None``.
        Unlike the bounded high-range probes this dispatch also runs in the
        dense-graph regime (``_shortcut_probe_limit() == 0``).

        Returns ``(decided, answer)``; when ``decided`` is False no stable
        extension exists and the caller falls back to the range-maximal loop.
        """
        full_range = frozenset(self.problem.arguments)
        witness = _base_extension(
            self.problem,
            base=self.base,
            required_in=required_in,
            required_out=required_out,
            required_range=full_range,
            utility_name=self._stable_first_utility_name("witness"),
        )
        if witness is not None:
            return True, witness
        if not required_in and not required_out:
            # The witness probe doubled as the unconstrained existence check:
            # no stable extension exists at all.
            return False, None
        unconstrained = _base_extension(
            self.problem,
            base=self.base,
            required_range=full_range,
            utility_name=self._stable_first_utility_name("global"),
        )
        if unconstrained is not None:
            # Stable extensions exist, so every range-maximal extension has
            # full range; the witness probe proved none satisfies the query.
            return True, None
        return False, None

    def _stable_first_utility_name(self, kind: str) -> str:
        return f"{_seed_label_base(self.seed_utility_name)}_stable_first_{kind}"

    def _high_range_shortcut(
        self,
        *,
        required_in: frozenset[str],
        required_out: frozenset[str],
        excluded_range_subsets: list[frozenset[str]],
    ) -> frozenset[str] | None:
        arguments = tuple(self.problem.arguments)
        probes = 0
        probe_limit = self._shortcut_probe_limit()
        for missing in _bounded_missing_sets(
            arguments,
            depth=self.shortcut_depth,
            limit=probe_limit + 1,
        ):
            if not missing:
                # The full-range (depth-0) probe is subsumed by the
                # stable-first dispatch in find_extension: once it fails,
                # later loop iterations only add blocking constraints, so it
                # can never succeed again.
                continue
            required_range = frozenset(arguments) - missing
            witness = _base_extension(
                self.problem,
                base=self.base,
                required_in=required_in,
                required_out=required_out,
                required_range=required_range,
                excluded_range_subsets=excluded_range_subsets,
                utility_name=_high_range_shortcut_utility(self.seed_utility_name),
            )
            probes += 1
            if witness is not None:
                return witness
            if probes >= probe_limit:
                return None
        return None

    def _shortcut_probe_limit(self) -> int:
        if (
            len(self.problem.arguments) >= 160
            and len(self.problem.framework.defeats) >= len(self.problem.arguments) * 8
        ):
            return self.dense_shortcut_probe_limit
        return self.shortcut_probe_limit

    def _base_feasibility_utility_name(self) -> str:
        return f"{_seed_label_base(self.seed_utility_name)}_base_feasibility"

    def _is_range_maximal(self, range_set: frozenset[str]) -> bool:
        outside = self.problem.framework.arguments - range_set
        if not outside:
            return True
        larger = _base_extension(
            self.problem,
            base=self.base,
            required_range=range_set,
            require_any_range=outside,
            utility_name=self.test_utility_name,
        )
        return larger is None


def _max_range_size(
    problem: AfSatKernel,
    *,
    base: str,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    excluded_range_subsets: list[frozenset[str]] | None = None,
    utility_name: str,
) -> tuple[int | None, frozenset[str] | None]:
    low = 0
    high = len(problem.arguments)
    best: int | None = None
    best_witness: frozenset[str] | None = None
    while low <= high:
        midpoint = (low + high) // 2
        candidate = _base_extension(
            problem,
            base=base,
            required_in=required_in,
            required_out=required_out,
            required_range_size_at_least=midpoint,
            excluded_range_subsets=excluded_range_subsets,
            utility_name=utility_name,
        )
        if candidate is None:
            high = midpoint - 1
        else:
            best = midpoint
            best_witness = candidate
            low = midpoint + 1
    return best, best_witness


def _bounded_missing_sets(
    arguments: tuple[str, ...],
    *,
    depth: int,
    limit: int,
) -> Iterable[frozenset[str]]:
    pending: deque[tuple[int, tuple[str, ...], int]] = deque([(0, (), 0)])
    yielded = 0
    while pending and yielded < limit:
        start, selected, selected_size = pending.popleft()
        if selected_size <= depth:
            yielded += 1
            yield frozenset(selected)
        if selected_size == depth:
            continue
        for index in range(start, len(arguments)):
            pending.append((index + 1, (*selected, arguments[index]), selected_size + 1))


def _seed_label_base(seed_utility_name: str) -> str:
    """Strip a trailing ``_seed`` from a telemetry utility-name label.

    Telemetry-only: the result feeds ``SATCheck.utility_name`` trace labels and
    has no effect on SAT semantics. ``str.removesuffix`` returns the string
    unchanged when the suffix is absent, matching the prior explicit-``endswith``
    branch byte-for-byte.
    """
    return seed_utility_name.removesuffix("_seed")


def _max_range_utility(seed_utility_name: str, kind: str) -> str:
    return f"{_seed_label_base(seed_utility_name)}_max_range_{kind}"


def _high_range_shortcut_utility(seed_utility_name: str) -> str:
    return f"{_seed_label_base(seed_utility_name)}_high_range_shortcut"


def _base_extension(
    problem: AfSatKernel,
    *,
    base: str,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
    required_range_size: int | None = None,
    required_range_size_at_least: int | None = None,
    excluded_exact: list[frozenset[str]] | None = None,
    excluded_range_subsets: list[frozenset[str]] | None = None,
    utility_name: str,
) -> frozenset[str] | None:
    if base == "complete":
        return _complete_extension(
            problem,
            required_in=required_in,
            required_out=required_out,
            required_range=required_range,
            require_any_range=require_any_range,
            required_range_size=required_range_size,
            required_range_size_at_least=required_range_size_at_least,
            excluded_exact=excluded_exact,
            excluded_range_subsets=excluded_range_subsets,
            utility_name=utility_name,
        )
    if base == "conflict_free":
        return _conflict_free_extension(
            problem,
            required_in=required_in,
            required_out=required_out,
            required_range=required_range,
            require_any_range=require_any_range,
            required_range_size=required_range_size,
            required_range_size_at_least=required_range_size_at_least,
            excluded_exact=excluded_exact,
            excluded_range_subsets=excluded_range_subsets,
            utility_name=utility_name,
        )
    raise ValueError(f"unknown SAT base semantics: {base!r}")


def _conflict_free_extension(
    problem: AfSatKernel,
    *,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
    required_range_size: int | None = None,
    required_range_size_at_least: int | None = None,
    excluded_exact: list[frozenset[str]] | None = None,
    excluded_range_subsets: list[frozenset[str]] | None = None,
    utility_name: str,
) -> frozenset[str] | None:
    return _run_extension(
        problem,
        required_in=required_in,
        required_out=required_out,
        required_range=required_range,
        require_any_range=require_any_range,
        required_range_size=required_range_size,
        required_range_size_at_least=required_range_size_at_least,
        excluded_exact=excluded_exact,
        excluded_range_subsets=excluded_range_subsets,
        utility_name=utility_name,
    )


def _apply_range_size_constraints(
    problem: AfSatKernel,
    *,
    required_range_size: int | None,
    required_range_size_at_least: int | None,
) -> tuple[int | None, str | None]:
    if required_range_size is not None and required_range_size_at_least is not None:
        raise ValueError("range size exact and lower-bound constraints are mutually exclusive")
    if required_range_size is not None:
        problem.require_range_size_exactly(required_range_size)
        return required_range_size, "exact"
    if required_range_size_at_least is not None:
        problem.require_range_size_at_least(required_range_size_at_least)
        return required_range_size_at_least, "at_least"
    return None, None


def _optional_argument(
    framework: ArgumentationFramework,
    argument: str | None,
) -> frozenset[str]:
    if argument is None:
        return frozenset()
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument!r}")
    return frozenset({argument})


def _extension_fingerprint(extension: frozenset[str]) -> str:
    digest = sha1()
    for argument in sorted(extension):
        digest.update(argument.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def _is_acyclic(framework: ArgumentationFramework) -> bool:
    outgoing: dict[str, list[str]] = {argument: [] for argument in framework.arguments}
    for attacker, target in framework.defeats:
        outgoing[attacker].append(target)
    return is_acyclic(outgoing)


def _load_z3():
    return load_z3("SAT solving")


__all__ = [
    "AfSatCheckTimeout",
    "AfSatKernel",
    "PreferredSkepticalTaskSolver",
    "PreferredSuperCoreSolver",
    "SATCheck",
    "SATTraceSink",
    "StableUnsatExplanation",
    "explain_stable_unsat",
    "find_complete_extension",
    "find_ideal_extension",
    "find_preferred_extension",
    "find_semi_stable_extension",
    "find_stable_extension",
    "find_stage_extension",
    "is_preferred_skeptically_accepted",
]
