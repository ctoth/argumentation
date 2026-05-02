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
    "sat_extensions",
    "stable_extensions_from_encoding",
]
