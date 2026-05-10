"""Incremental SAT kernel for Dung abstract argumentation frameworks."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha1
from time import perf_counter
from typing import Any

from argumentation.dung import (
    ArgumentationFramework,
    _attackers_index,
    grounded_extension,
    range_of,
)


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
    return PreferredSkepticalTaskSolver(
        framework,
        trace_sink=trace_sink,
        metadata=metadata,
    ).decide(query)


class PreferredSkepticalTaskSolver:
    """CDAS-style skeptical preferred acceptance solver for one AF."""

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

    def decide(self, query: str) -> bool:
        required_query = _optional_argument(self.framework, query)
        shortcut = self._shortcut(query)
        if shortcut is not None:
            return shortcut

        super_core = PreferredSuperCoreSolver(
            self.framework,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
        ).compute()
        if required_query and required_query <= super_core:
            return True

        extension_problem = AfSatKernel(
            self.framework,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
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
            extended = _grow_preferred(
                extension_problem,
                self.framework,
                extended,
                utility_name="preferred_skeptical_extend_attacker_maximal",
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
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata

    def compute(self) -> frozenset[str]:
        problem = AfSatKernel(
            self.framework,
            trace_sink=self.trace_sink,
            metadata=self.metadata,
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

        current = current - _attacked_by(current, self.framework.defeats)
        while True:
            undefended_attackers = current - _attacked_by(current, self.framework.defeats)
            next_current = current - _attacked_by(undefended_attackers, self.framework.defeats)
            if next_current == current:
                return current
            current = next_current


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
    problem = AfSatKernel(framework, trace_sink=trace_sink, metadata=metadata)
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

    current = current - _attacked_by(current, framework.defeats)
    while True:
        undefended_attackers = current - _attacked_by(current, framework.defeats)
        next_current = current - _attacked_by(undefended_attackers, framework.defeats)
        if next_current == current:
            return current
        current = next_current


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
    required_range_size: int | None = None,
    required_range_size_at_least: int | None = None,
    excluded_exact: list[frozenset[str]] | None = None,
    excluded_range_subsets: list[frozenset[str]] | None = None,
    utility_name: str,
    loop_index: int | None = None,
    learned_count: int | None = None,
) -> frozenset[str] | None:
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
    ) -> None:
        self.framework = framework
        self.trace_sink = trace_sink
        self.metadata = metadata
        self.z3 = _load_z3()
        self.solver = self.z3.Solver()
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


def _attacked_by(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    return frozenset(target for attacker, target in defeats if attacker in arguments)


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


class RangeMaximalTaskSolver:
    """Exact range-maximal search for stage and semi-stable tasks."""

    shortcut_depth = 2
    shortcut_probe_limit = 24

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

    def _high_range_shortcut(
        self,
        *,
        required_in: frozenset[str],
        required_out: frozenset[str],
        excluded_range_subsets: list[frozenset[str]],
    ) -> frozenset[str] | None:
        arguments = tuple(self.problem.arguments)
        probes = 0
        for missing in _bounded_missing_sets(
            arguments,
            depth=self.shortcut_depth,
            limit=self.shortcut_probe_limit,
        ):
            required_range = frozenset(arguments) - missing
            kind = "full" if not missing else "high"
            witness = _base_extension(
                self.problem,
                base=self.base,
                required_in=required_in,
                required_out=required_out,
                required_range=required_range,
                excluded_range_subsets=excluded_range_subsets,
                utility_name=_range_shortcut_utility(self.seed_utility_name, kind),
            )
            probes += 1
            if witness is not None:
                return witness
            if probes >= self.shortcut_probe_limit:
                return None
        return None

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


def _max_range_utility(seed_utility_name: str, kind: str) -> str:
    if seed_utility_name.endswith("_seed"):
        return f"{seed_utility_name.removesuffix('_seed')}_max_range_{kind}"
    return f"{seed_utility_name}_max_range_{kind}"


def _range_shortcut_utility(seed_utility_name: str, kind: str) -> str:
    if seed_utility_name.endswith("_seed"):
        return f"{seed_utility_name.removesuffix('_seed')}_{kind}_range_shortcut"
    return f"{seed_utility_name}_{kind}_range_shortcut"


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
    problem.solver.push()
    try:
        problem.require_in(required_in)
        problem.require_out(required_out)
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
        ) != "sat":
            return None
        return problem.model_extension()
    finally:
        problem.solver.pop()


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

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(argument: str) -> bool:
        if argument in visiting:
            return False
        if argument in visited:
            return True
        visiting.add(argument)
        for target in outgoing.get(argument, []):
            if not visit(target):
                return False
        visiting.remove(argument)
        visited.add(argument)
        return True

    return all(visit(argument) for argument in framework.arguments)


def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("SAT solving requires z3-solver") from exc
    return z3


__all__ = [
    "AfSatKernel",
    "PreferredSkepticalTaskSolver",
    "PreferredSuperCoreSolver",
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
