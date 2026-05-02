"""Incremental SAT kernel for Dung abstract argumentation frameworks."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from argumentation.dung import ArgumentationFramework, _attackers_index, range_of


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
    metadata: Mapping[str, object] | None = None


SATTraceSink = Callable[[SATCheck], None]


class AfSatKernel:
    """Reusable SAT state for one Dung AF."""

    def __init__(
        self,
        framework: ArgumentationFramework,
        *,
        trace_sink: SATTraceSink | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata
        self.z3 = _load_z3()
        self.solver = self.z3.Solver()
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
        self.attackers_index = _attackers_index(framework.defeats)
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
            for attacker in sorted(self.attackers_index.get(argument, frozenset())):
                defenders = tuple(sorted(self.attackers_index.get(attacker, frozenset())))
                if defenders:
                    self.solver.add(
                        self.z3.Implies(
                            self.in_vars[argument],
                            self.z3.Or(*(self.in_vars[defender] for defender in defenders)),
                        )
                    )
                else:
                    self.solver.add(self.z3.Not(self.in_vars[argument]))
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

    def require_attacks_any(self, targets: frozenset[str]) -> None:
        self._validate(targets)
        attackers = frozenset(
            attacker
            for attacker, target in self.framework.defeats
            if target in targets
        )
        self.require_any_in(attackers)

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
        self.require_any_range(outside)

    def check(self, utility_name: str, assumptions: tuple[Any, ...] = ()) -> str:
        started = perf_counter()
        result_ref = self.solver.check(*assumptions)
        elapsed_ms = (perf_counter() - started) * 1000
        result = str(result_ref)
        model_size = None
        if result == "sat":
            model_size = len(self.model_extension())
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
                    metadata=self.metadata,
                )
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

    def _validate(self, arguments: frozenset[str]) -> None:
        unknown = sorted(arguments - self.framework.arguments)
        if unknown:
            raise ValueError(f"unknown arguments: {unknown!r}")


def find_stable_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
) -> frozenset[str] | None:
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_stable_coverage()
    problem.require_in(_optional_argument(framework, require_in))
    problem.require_out(_optional_argument(framework, require_out))
    if problem.check("stable_extension") != "sat":
        return None
    return problem.model_extension()


def find_complete_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
) -> frozenset[str] | None:
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_complete_labelling()
    return _complete_extension(
        problem,
        required_in=_optional_argument(framework, require_in),
        required_out=_optional_argument(framework, require_out),
        utility_name="complete_extension",
    )


def find_preferred_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
) -> frozenset[str] | None:
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_complete_labelling()
    required_in = _optional_argument(framework, require_in)
    required_out = _optional_argument(framework, require_out)
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
) -> bool:
    """Decide preferred skeptical acceptance using CDAS admissibility checks."""
    required_query = _optional_argument(framework, query)
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_admissible_labelling()
    seed = _admissible_extension(
        problem,
        required_in=required_query,
        utility_name="preferred_skeptical_seed",
    )
    if seed is None:
        return False

    covered: list[frozenset[str]] = []
    while True:
        attacker = _admissible_attacker_against_compatible_candidate(
            framework,
            required_in=required_query,
            excluded_subsets=covered,
            trace_sink=trace_sink,
            metadata=metadata,
        )
        if attacker is None:
            return True
        extended = _admissible_extension(
            problem,
            required_in=attacker | required_query,
            utility_name="preferred_skeptical_extend_attacker",
        )
        if extended is None:
            return False
        covered.append(extended)


def find_semi_stable_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
) -> frozenset[str] | None:
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_complete_labelling()
    problem.add_range_definition()
    return _range_maximal_extension(
        problem,
        framework,
        base="complete",
        required_in=_optional_argument(framework, require_in),
        required_out=_optional_argument(framework, require_out),
        seed_utility_name="semi_stable_seed",
        test_utility_name="semi_stable_range_maximality",
    )


def find_ideal_extension(
    framework: ArgumentationFramework,
    *,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
) -> frozenset[str]:
    preferred_super_core = frozenset(
        argument
        for argument in sorted(framework.arguments)
        if find_preferred_extension(
            framework,
            require_out=argument,
            trace_sink=trace_sink,
            metadata=metadata,
        )
        is None
    )
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_admissible_labelling()
    current = _admissible_extension(
        problem,
        required_out=framework.arguments - preferred_super_core,
        utility_name="ideal_seed",
    )
    if current is None:
        return frozenset()

    while True:
        outside = preferred_super_core - current
        if not outside:
            return current
        larger = _admissible_extension(
            problem,
            required_in=current,
            required_out=framework.arguments - preferred_super_core,
            require_any_in=outside,
            utility_name="ideal_grow_admissible",
        )
        if larger is None:
            return current
        if not current < larger:
            raise RuntimeError("SAT ideal growth did not produce a strict superset")
        current = larger


def find_stage_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
    trace_sink: SATTraceSink | None = None,
    metadata: Mapping[str, object] | None = None,
) -> frozenset[str] | None:
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
    problem.add_conflict_free()
    problem.add_range_definition()
    return _range_maximal_extension(
        problem,
        framework,
        base="conflict_free",
        required_in=_optional_argument(framework, require_in),
        required_out=_optional_argument(framework, require_out),
        seed_utility_name="stage_seed",
        test_utility_name="stage_range_maximality",
    )


def _complete_extension(
    problem: AfSatKernel,
    *,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    require_any_in: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
    excluded_exact: list[frozenset[str]] | None = None,
    utility_name: str,
) -> frozenset[str] | None:
    problem.solver.push()
    try:
        problem.require_in(required_in)
        problem.require_out(required_out)
        problem.require_any_in(require_any_in)
        problem.require_range(required_range)
        problem.require_any_range(require_any_range)
        for blocked in excluded_exact or []:
            problem.exclude_exact_extension(blocked)
        if problem.check(utility_name) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


def _admissible_extension(
    problem: AfSatKernel,
    *,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    require_any_in: frozenset[str] = frozenset(),
    utility_name: str,
) -> frozenset[str] | None:
    problem.solver.push()
    try:
        problem.require_in(required_in)
        problem.require_out(required_out)
        problem.require_any_in(require_any_in)
        if problem.check(utility_name) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


def _admissible_attacker_against_compatible_candidate(
    framework: ArgumentationFramework,
    *,
    required_in: frozenset[str],
    excluded_subsets: list[frozenset[str]],
    trace_sink: SATTraceSink | None,
    metadata: Mapping[str, object] | None,
) -> frozenset[str] | None:
    z3 = _load_z3()
    solver = z3.Solver()
    arguments = tuple(sorted(framework.arguments))
    attacker_vars = {
        argument: z3.Bool(f"af_cdas_attacker_{index}")
        for index, argument in enumerate(arguments)
    }
    candidate_vars = {
        argument: z3.Bool(f"af_cdas_candidate_{index}")
        for index, argument in enumerate(arguments)
    }

    _add_admissible_constraints(z3, solver, framework, attacker_vars)
    _add_admissible_constraints(z3, solver, framework, candidate_vars)
    for argument in sorted(required_in):
        solver.add(candidate_vars[argument])

    attack_pairs = [
        z3.And(attacker_vars[attacker], candidate_vars[target])
        for attacker, target in sorted(framework.defeats)
    ]
    solver.add(z3.Or(*attack_pairs) if attack_pairs else z3.BoolVal(False))

    for excluded in excluded_subsets:
        outside = framework.arguments - excluded
        if outside:
            solver.add(z3.Or(*(attacker_vars[argument] for argument in sorted(outside))))
        else:
            solver.add(z3.BoolVal(False))

    started = perf_counter()
    result_ref = solver.check()
    elapsed_ms = (perf_counter() - started) * 1000
    result = str(result_ref)
    extension = None
    if result == "sat":
        model = solver.model()
        extension = frozenset(
            argument
            for argument, variable in attacker_vars.items()
            if z3.is_true(model.evaluate(variable, model_completion=True))
        )
    if trace_sink is not None:
        trace_sink(
            SATCheck(
                utility_name="preferred_skeptical_adm_ext_att",
                result=result,
                elapsed_ms=elapsed_ms,
                assumptions_count=0,
                argument_count=len(framework.arguments),
                attack_count=len(framework.defeats),
                model_extension_size=None if extension is None else len(extension),
                metadata=metadata,
            )
        )
    return extension


def _add_admissible_constraints(
    z3,
    solver,
    framework: ArgumentationFramework,
    in_vars: Mapping[str, Any],
) -> None:
    conflict_relation = framework.attacks if framework.attacks is not None else framework.defeats
    for attacker, target in sorted(conflict_relation):
        solver.add(z3.Or(z3.Not(in_vars[attacker]), z3.Not(in_vars[target])))

    attackers_index = _attackers_index(framework.defeats)
    for argument in sorted(framework.arguments):
        for attacker in sorted(attackers_index.get(argument, frozenset())):
            defenders = tuple(sorted(attackers_index.get(attacker, frozenset())))
            if defenders:
                solver.add(
                    z3.Implies(
                        in_vars[argument],
                        z3.Or(*(in_vars[defender] for defender in defenders)),
                    )
                )
            else:
                solver.add(z3.Not(in_vars[argument]))


def _grow_preferred(
    problem: AfSatKernel,
    framework: ArgumentationFramework,
    seed: frozenset[str],
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
            utility_name="preferred_grow",
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
    blocked_candidates: list[frozenset[str]] = []
    while True:
        candidate = _base_extension(
            problem,
            base=base,
            required_in=required_in,
            required_out=required_out,
            excluded_exact=blocked_candidates,
            utility_name=seed_utility_name,
        )
        if candidate is None:
            return None
        candidate_range = range_of(candidate, framework.defeats)
        outside_range = framework.arguments - candidate_range
        if not outside_range:
            return candidate
        larger_range = _base_extension(
            problem,
            base=base,
            required_range=candidate_range,
            require_any_range=outside_range,
            utility_name=test_utility_name,
        )
        if larger_range is None:
            return candidate
        blocked_candidates.append(candidate)


def _base_extension(
    problem: AfSatKernel,
    *,
    base: str,
    required_in: frozenset[str] = frozenset(),
    required_out: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
    excluded_exact: list[frozenset[str]] | None = None,
    utility_name: str,
) -> frozenset[str] | None:
    if base == "complete":
        return _complete_extension(
            problem,
            required_in=required_in,
            required_out=required_out,
            required_range=required_range,
            require_any_range=require_any_range,
            excluded_exact=excluded_exact,
            utility_name=utility_name,
        )
    if base == "conflict_free":
        return _conflict_free_extension(
            problem,
            required_in=required_in,
            required_out=required_out,
            required_range=required_range,
            require_any_range=require_any_range,
            excluded_exact=excluded_exact,
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
    excluded_exact: list[frozenset[str]] | None = None,
    utility_name: str,
) -> frozenset[str] | None:
    problem.solver.push()
    try:
        problem.require_in(required_in)
        problem.require_out(required_out)
        problem.require_range(required_range)
        problem.require_any_range(require_any_range)
        for blocked in excluded_exact or []:
            problem.exclude_exact_extension(blocked)
        if problem.check(utility_name) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


def _optional_argument(
    framework: ArgumentationFramework,
    argument: str | None,
) -> frozenset[str]:
    if argument is None:
        return frozenset()
    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument!r}")
    return frozenset({argument})


def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("SAT solving requires z3-solver") from exc
    return z3


__all__ = [
    "AfSatKernel",
    "SATCheck",
    "SATTraceSink",
    "find_complete_extension",
    "find_ideal_extension",
    "find_preferred_extension",
    "find_semi_stable_extension",
    "find_stable_extension",
    "find_stage_extension",
    "is_preferred_skeptically_accepted",
]
