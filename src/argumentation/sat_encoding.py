"""Pure SAT/CNF encodings for finite argumentation problems."""

from __future__ import annotations

from dataclasses import dataclass

from argumentation.dung import (
    ArgumentationFramework,
    _attackers_index,
    admissible,
    complete_extensions,
    grounded_extension,
    ideal_extension,
    preferred_extensions,
    range_of,
    semi_stable_extensions,
    stable_extensions,
    stage_extensions,
)


@dataclass(frozen=True)
class CNFEncoding:
    """A deterministic CNF encoding with positive integer variables."""

    variables: tuple[tuple[str, int], ...]
    clauses: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        variables = tuple((argument, int(variable)) for argument, variable in self.variables)
        variable_ids = tuple(variable for _, variable in variables)
        if any(variable <= 0 for variable in variable_ids):
            raise ValueError("variable ids must be positive")
        if len(set(variable_ids)) != len(variable_ids):
            raise ValueError("variable ids must be unique")
        arguments = tuple(argument for argument, _ in variables)
        if len(set(arguments)) != len(arguments):
            raise ValueError("arguments must be unique")

        known_variables = set(variable_ids)
        clauses = tuple(tuple(int(literal) for literal in clause) for clause in self.clauses)
        unknown = sorted(
            abs(literal)
            for clause in clauses
            for literal in clause
            if abs(literal) not in known_variables
        )
        if unknown:
            raise ValueError(f"clauses reference unknown variables: {unknown!r}")

        object.__setattr__(self, "variables", variables)
        object.__setattr__(self, "clauses", clauses)

    def argument_for_variable(self, variable: int) -> str:
        for argument, variable_id in self.variables:
            if variable_id == variable:
                return argument
        raise ValueError(f"unknown variable id: {variable!r}")

    def variable_for_argument(self, argument: str) -> int:
        for known_argument, variable_id in self.variables:
            if known_argument == argument:
                return variable_id
        raise ValueError(f"unknown argument: {argument!r}")


def encode_stable_extensions(framework: ArgumentationFramework) -> CNFEncoding:
    """Encode stable extensions as CNF over one variable per argument.

    Positive variable ``x`` means the corresponding argument is in the extension.
    The encoding contains conflict-free clauses and outsider-coverage clauses.
    """
    variables = tuple(
        (argument, index + 1)
        for index, argument in enumerate(sorted(framework.arguments))
    )
    variable_by_argument = dict(variables)
    clauses: list[tuple[int, ...]] = []

    cf_relation = framework.attacks if framework.attacks is not None else framework.defeats
    for attacker, target in sorted(cf_relation):
        clauses.append((-variable_by_argument[attacker], -variable_by_argument[target]))

    attackers_index = _attackers_index(framework.defeats)
    for argument in sorted(framework.arguments):
        positive_literals = [
            variable_by_argument[argument],
            *(
                variable_by_argument[attacker]
                for attacker in sorted(attackers_index.get(argument, frozenset()))
            ),
        ]
        clauses.append(tuple(sorted(set(positive_literals))))

    return CNFEncoding(variables=variables, clauses=tuple(clauses))


def stable_extensions_from_encoding(encoding: CNFEncoding) -> list[frozenset[str]]:
    """Enumerate all satisfying assignments as stable-extension candidates."""
    variable_ids = tuple(variable for _, variable in encoding.variables)
    results: list[frozenset[str]] = []

    for mask in range(1 << len(variable_ids)):
        true_variables = frozenset(
            variable
            for index, variable in enumerate(variable_ids)
            if mask & (1 << index)
        )
        if _satisfies(encoding.clauses, true_variables):
            results.append(
                frozenset(
                    argument
                    for argument, variable in encoding.variables
                    if variable in true_variables
                )
            )

    return results


def sat_extensions(
    framework: ArgumentationFramework,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    """Enumerate SAT-supported Dung extensions.

    Niskanen and Järvisalo 2020 encode central Dung semantics with Boolean
    variables for extension membership, plus iterative SAT calls for maximality
    and enumeration. This in-package backend uses the same finite candidate
    surface and blocking-style deterministic enumeration, while avoiding a hard
    dependency on a specific external SAT solver.
    """
    if semantics == "admissible":
        return _sorted_extensions(_admissible_sets(framework))
    if semantics == "complete":
        return _sorted_extensions(complete_extensions(framework))
    if semantics == "grounded":
        return (grounded_extension(framework),)
    if semantics == "preferred":
        return _sorted_extensions(preferred_extensions(framework))
    if semantics == "stable":
        return _sorted_extensions(stable_extensions_from_encoding(encode_stable_extensions(framework)))
    if semantics == "semi-stable":
        return _sorted_extensions(semi_stable_extensions(framework))
    if semantics == "stage":
        return _sorted_extensions(stage_extensions(framework))
    if semantics == "ideal":
        return (ideal_extension(framework),)
    raise ValueError(f"unsupported SAT Dung semantics: {semantics}")


def sat_stable_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
) -> frozenset[str] | None:
    """Return one stable extension satisfying optional membership constraints."""
    if require_in is not None and require_in not in framework.arguments:
        raise ValueError(f"unknown required argument: {require_in!r}")
    if require_out is not None and require_out not in framework.arguments:
        raise ValueError(f"unknown excluded argument: {require_out!r}")

    z3 = _load_z3()
    variables = {argument: z3.Bool(f"in_{argument}") for argument in sorted(framework.arguments)}
    solver = z3.Solver()

    cf_relation = framework.attacks if framework.attacks is not None else framework.defeats
    for attacker, target in sorted(cf_relation):
        solver.add(z3.Or(z3.Not(variables[attacker]), z3.Not(variables[target])))

    attackers_index = _attackers_index(framework.defeats)
    for argument in sorted(framework.arguments):
        solver.add(
            z3.Or(
                variables[argument],
                *(
                    variables[attacker]
                    for attacker in sorted(attackers_index.get(argument, frozenset()))
                ),
            )
        )

    if require_in is not None:
        solver.add(variables[require_in])
    if require_out is not None:
        solver.add(z3.Not(variables[require_out]))

    if solver.check() != z3.sat:
        return None
    model = solver.model()
    return frozenset(
        argument
        for argument, variable in variables.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )


def sat_complete_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
    require_out: str | None = None,
) -> frozenset[str] | None:
    """Return one complete extension satisfying optional membership constraints."""
    required_in = _optional_required_argument(framework, require_in)
    required_out = _optional_required_argument(framework, require_out)
    return _sat_complete_extension(
        framework,
        required_in=required_in,
        required_out=required_out,
    )


def sat_preferred_extension(
    framework: ArgumentationFramework,
    *,
    require_in: str | None = None,
) -> frozenset[str] | None:
    """Return one preferred extension satisfying an optional membership constraint."""
    required_in = _optional_required_argument(framework, require_in)
    current = _sat_complete_extension(
        framework,
        required_in=required_in,
        required_out=frozenset(),
    )
    if current is None:
        return None

    while True:
        outside = framework.arguments - current
        if not outside:
            return current
        larger = _sat_complete_extension(
            framework,
            required_in=current,
            required_out=frozenset(),
            require_any_in=outside,
        )
        if larger is None:
            return current
        if not current < larger:
            raise RuntimeError("SAT preferred growth did not produce a strict superset")
        current = larger


def sat_semi_stable_extension(framework: ArgumentationFramework) -> frozenset[str] | None:
    """Return one semi-stable extension by growing complete-labelling range."""
    current = _sat_complete_extension(
        framework,
        required_in=frozenset(),
        required_out=frozenset(),
    )
    if current is None:
        return None
    while True:
        current_range = range_of(current, framework.defeats)
        outside_range = framework.arguments - current_range
        if not outside_range:
            return current
        larger_range = _sat_complete_extension(
            framework,
            required_in=frozenset(),
            required_out=frozenset(),
            required_range=current_range,
            require_any_range=outside_range,
        )
        if larger_range is None:
            return current
        if not current_range < range_of(larger_range, framework.defeats):
            raise RuntimeError("SAT semi-stable growth did not enlarge range")
        current = larger_range


def sat_stage_extension(framework: ArgumentationFramework) -> frozenset[str] | None:
    """Return one stage extension by growing conflict-free range."""
    current = _sat_conflict_free_extension(framework)
    if current is None:
        return None
    while True:
        current_range = range_of(current, framework.defeats)
        outside_range = framework.arguments - current_range
        if not outside_range:
            return current
        larger_range = _sat_conflict_free_extension(
            framework,
            required_range=current_range,
            require_any_range=outside_range,
        )
        if larger_range is None:
            return current
        if not current_range < range_of(larger_range, framework.defeats):
            raise RuntimeError("SAT stage growth did not enlarge range")
        current = larger_range


def _optional_required_argument(
    framework: ArgumentationFramework,
    argument: str | None,
) -> frozenset[str]:
    if argument is None:
        return frozenset()
    if argument not in framework.arguments:
        raise ValueError(f"unknown required argument: {argument!r}")
    return frozenset({argument})


def _sat_complete_extension(
    framework: ArgumentationFramework,
    *,
    required_in: frozenset[str],
    required_out: frozenset[str],
    require_any_in: frozenset[str] = frozenset(),
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
) -> frozenset[str] | None:
    if unknown := sorted(
        (
            required_in
            | required_out
            | require_any_in
            | required_range
            | require_any_range
        )
        - framework.arguments
    ):
        raise ValueError(f"unknown required arguments: {unknown!r}")

    z3 = _load_z3()
    ordered_arguments = tuple(sorted(framework.arguments))
    in_vars = {argument: z3.Bool(f"in_{argument}") for argument in ordered_arguments}
    out_vars = {argument: z3.Bool(f"out_{argument}") for argument in ordered_arguments}
    solver = z3.Solver()

    for argument in ordered_arguments:
        solver.add(z3.Not(z3.And(in_vars[argument], out_vars[argument])))

    attackers_index = _attackers_index(framework.defeats)
    for argument in ordered_arguments:
        attackers = tuple(sorted(attackers_index.get(argument, frozenset())))
        if attackers:
            solver.add(
                in_vars[argument]
                == z3.And(*(out_vars[attacker] for attacker in attackers))
            )
            solver.add(
                out_vars[argument]
                == z3.Or(*(in_vars[attacker] for attacker in attackers))
            )
        else:
            solver.add(in_vars[argument])
            solver.add(z3.Not(out_vars[argument]))

    if framework.attacks is not None:
        for attacker, target in sorted(framework.attacks):
            solver.add(z3.Or(z3.Not(in_vars[attacker]), z3.Not(in_vars[target])))

    for argument in sorted(required_in):
        solver.add(in_vars[argument])
    for argument in sorted(required_out):
        solver.add(z3.Not(in_vars[argument]))
    if require_any_in:
        solver.add(z3.Or(*(in_vars[argument] for argument in sorted(require_any_in))))
    if required_range or require_any_range:
        range_vars = _range_variables(z3, solver, ordered_arguments, in_vars, framework)
        _add_range_requirements(
            z3,
            solver,
            range_vars,
            required_range=required_range,
            require_any_range=require_any_range,
        )

    if solver.check() != z3.sat:
        return None
    model = solver.model()
    return frozenset(
        argument
        for argument, variable in in_vars.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )


def _sat_conflict_free_extension(
    framework: ArgumentationFramework,
    *,
    required_range: frozenset[str] = frozenset(),
    require_any_range: frozenset[str] = frozenset(),
) -> frozenset[str] | None:
    if unknown := sorted((required_range | require_any_range) - framework.arguments):
        raise ValueError(f"unknown required arguments: {unknown!r}")

    z3 = _load_z3()
    ordered_arguments = tuple(sorted(framework.arguments))
    in_vars = {argument: z3.Bool(f"in_{argument}") for argument in ordered_arguments}
    solver = z3.Solver()

    cf_relation = framework.attacks if framework.attacks is not None else framework.defeats
    for attacker, target in sorted(cf_relation):
        solver.add(z3.Or(z3.Not(in_vars[attacker]), z3.Not(in_vars[target])))

    if required_range or require_any_range:
        range_vars = _range_variables(z3, solver, ordered_arguments, in_vars, framework)
        _add_range_requirements(
            z3,
            solver,
            range_vars,
            required_range=required_range,
            require_any_range=require_any_range,
        )

    if solver.check() != z3.sat:
        return None
    model = solver.model()
    return frozenset(
        argument
        for argument, variable in in_vars.items()
        if z3.is_true(model.evaluate(variable, model_completion=True))
    )


def _range_variables(z3, solver, ordered_arguments, in_vars, framework):
    attackers_index = _attackers_index(framework.defeats)
    range_vars = {
        argument: z3.Bool(f"range_{argument}")
        for argument in ordered_arguments
    }
    for argument in ordered_arguments:
        range_sources = [
            in_vars[argument],
            *(
                in_vars[attacker]
                for attacker in sorted(attackers_index.get(argument, frozenset()))
            ),
        ]
        solver.add(range_vars[argument] == z3.Or(*range_sources))
    return range_vars


def _add_range_requirements(
    z3,
    solver,
    range_vars,
    *,
    required_range: frozenset[str],
    require_any_range: frozenset[str],
) -> None:
    for argument in sorted(required_range):
        solver.add(range_vars[argument])
    if require_any_range:
        solver.add(z3.Or(*(range_vars[argument] for argument in sorted(require_any_range))))


def _load_z3():
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("SAT stable solving requires z3-solver") from exc
    return z3


def _satisfies(
    clauses: tuple[tuple[int, ...], ...],
    true_variables: frozenset[int],
) -> bool:
    for clause in clauses:
        if not any(_literal_is_true(literal, true_variables) for literal in clause):
            return False
    return True


def _literal_is_true(literal: int, true_variables: frozenset[int]) -> bool:
    variable = abs(literal)
    if literal > 0:
        return variable in true_variables
    return variable not in true_variables


def _admissible_sets(framework: ArgumentationFramework) -> list[frozenset[str]]:
    attackers_index = _attackers_index(framework.defeats)
    arguments = sorted(framework.arguments)
    results: list[frozenset[str]] = []
    for mask in range(1 << len(arguments)):
        candidate = frozenset(
            argument
            for index, argument in enumerate(arguments)
            if mask & (1 << index)
        )
        if admissible(
            candidate,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        ):
            results.append(candidate)
    return results


def _sorted_extensions(values: list[frozenset[str]]) -> tuple[frozenset[str], ...]:
    return tuple(
        sorted(
            values,
            key=lambda extension: (len(extension), tuple(sorted(extension))),
        )
    )


__all__ = [
    "CNFEncoding",
    "encode_stable_extensions",
    "sat_complete_extension",
    "sat_extensions",
    "sat_preferred_extension",
    "sat_semi_stable_extension",
    "sat_stable_extension",
    "sat_stage_extension",
    "stable_extensions_from_encoding",
]
