"""Finite belief-level approximation for epistemic influence graphs.

The surface is deliberately narrower than Hunter et al.'s full epistemic graph
language: belief assignments are mappings from argument IDs to floats in
``[0, 1]``; constraints are interval bounds; and positive/negative influences
are checked directly over those assignments.  It does not implement general
epistemic formulas, multi-labelled arcs with dependency labels, probability
functions over possible worlds, or Potyka et al.'s linear-programming
satisfiability and entailment procedures.

References:
    Hunter, Polberg, and Thimm (2018-2020). Epistemic graphs for representing
    and reasoning with positive and negative influences of arguments.
    Potyka, Polberg, and Hunter (2019). Polynomial-time updates of epistemic
    states in a fragment of probabilistic epistemic argumentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum
from itertools import product
import re
from typing import Literal, Mapping, Sequence

from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import ProbabilisticAF


@dataclass(frozen=True)
class ArgumentTerm:
    name: str


@dataclass(frozen=True)
class NotTerm:
    term: Term


@dataclass(frozen=True)
class AndTerm:
    left: Term
    right: Term


@dataclass(frozen=True)
class OrTerm:
    left: Term
    right: Term


Term = ArgumentTerm | NotTerm | AndTerm | OrTerm


@dataclass(frozen=True)
class ProbabilityTerm:
    term: Term


@dataclass(frozen=True)
class OperationalFormula:
    terms: tuple[ProbabilityTerm, ...]
    operators: tuple[Literal["+", "-"], ...]

    def __post_init__(self) -> None:
        if not self.terms:
            raise ValueError("operational formula must contain at least one probability term")
        if len(self.operators) != len(self.terms) - 1:
            raise ValueError("operational formula operators must connect probability terms")


ComparisonOperator = Literal["=", "!=", "<", "<=", ">", ">="]


@dataclass(frozen=True)
class EpistemicAtom:
    formula: OperationalFormula
    operator: ComparisonOperator
    threshold: float

    def __post_init__(self) -> None:
        if self.operator not in {"=", "!=", "<", "<=", ">", ">="}:
            raise ValueError(f"unsupported epistemic comparison operator: {self.operator}")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("epistemic atom thresholds must lie in [0, 1]")


@dataclass(frozen=True)
class AtomFormula:
    atom: EpistemicAtom


@dataclass(frozen=True)
class NotFormula:
    formula: EpistemicFormula


@dataclass(frozen=True)
class AndFormula:
    left: EpistemicFormula
    right: EpistemicFormula


@dataclass(frozen=True)
class OrFormula:
    left: EpistemicFormula
    right: EpistemicFormula


EpistemicFormula = AtomFormula | NotFormula | AndFormula | OrFormula


@dataclass(frozen=True)
class ProbabilityFunction:
    """Belief distribution over all possible worlds of a finite argument set."""

    arguments: frozenset[str]
    probabilities: Mapping[frozenset[str], float]

    def __post_init__(self) -> None:
        arguments = frozenset(str(argument) for argument in self.arguments)
        normalized = {
            frozenset(str(argument) for argument in world): float(probability)
            for world, probability in self.probabilities.items()
        }
        worlds = frozenset(possible_worlds(arguments))
        if frozenset(normalized) != worlds:
            raise ValueError("probability function must assign all possible worlds exactly once")
        negative = sorted(world for world, probability in normalized.items() if probability < 0.0)
        if negative:
            raise ValueError(f"world probabilities must be nonnegative: {negative!r}")
        total = sum(normalized.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError("world probabilities must sum to 1")
        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "probabilities", normalized)


def possible_worlds(arguments: frozenset[str]) -> tuple[frozenset[str], ...]:
    """Return all possible worlds ordered by size and argument name."""
    ordered = sorted(arguments)
    worlds: list[frozenset[str]] = []
    for mask in range(1 << len(ordered)):
        worlds.append(
            frozenset(argument for index, argument in enumerate(ordered) if mask & (1 << index))
        )
    return tuple(sorted(worlds, key=lambda world: (len(world), tuple(sorted(world)))))


def term_satisfied(term: Term, world: frozenset[str]) -> bool:
    if isinstance(term, ArgumentTerm):
        return term.name in world
    if isinstance(term, NotTerm):
        return not term_satisfied(term.term, world)
    if isinstance(term, AndTerm):
        return term_satisfied(term.left, world) and term_satisfied(term.right, world)
    if isinstance(term, OrTerm):
        return term_satisfied(term.left, world) or term_satisfied(term.right, world)
    raise TypeError(f"unsupported term: {term!r}")


def term_probability(term: Term, distribution: ProbabilityFunction) -> float:
    """Return the sum of probabilities of worlds satisfying ``term``."""
    return sum(
        probability
        for world, probability in distribution.probabilities.items()
        if term_satisfied(term, world)
    )


def operational_value(
    formula: OperationalFormula,
    distribution: ProbabilityFunction,
) -> float:
    value = term_probability(formula.terms[0].term, distribution)
    for operator, probability_term in zip(formula.operators, formula.terms[1:], strict=True):
        term_value = term_probability(probability_term.term, distribution)
        if operator == "+":
            value += term_value
        else:
            value -= term_value
    return value


def evaluate_epistemic_formula(
    formula: EpistemicFormula,
    distribution: ProbabilityFunction,
) -> bool:
    if isinstance(formula, AtomFormula):
        return _compare(
            operational_value(formula.atom.formula, distribution),
            formula.atom.operator,
            formula.atom.threshold,
        )
    if isinstance(formula, NotFormula):
        return not evaluate_epistemic_formula(formula.formula, distribution)
    if isinstance(formula, AndFormula):
        return evaluate_epistemic_formula(formula.left, distribution) and evaluate_epistemic_formula(
            formula.right,
            distribution,
        )
    if isinstance(formula, OrFormula):
        return evaluate_epistemic_formula(formula.left, distribution) or evaluate_epistemic_formula(
            formula.right,
            distribution,
        )
    raise TypeError(f"unsupported epistemic formula: {formula!r}")


def induced_probability_labelling(distribution: ProbabilityFunction) -> dict[str, float]:
    """Return the argument-probability labelling induced by a belief distribution."""
    return {
        argument: term_probability(ArgumentTerm(argument), distribution)
        for argument in sorted(distribution.arguments)
    }


_TOKEN_RE = re.compile(r"\s*(<=|>=|!=|[A-Za-z_][A-Za-z0-9_]*|[0-9]+(?:\.[0-9]+)?|[()!&|+\-=<>])")


def parse_term(text: str) -> Term:
    parser = _TokenParser(text)
    term = parser.parse_or_term()
    parser.expect_end()
    return term


def write_term(term: Term) -> str:
    if isinstance(term, ArgumentTerm):
        return term.name
    if isinstance(term, NotTerm):
        inner = write_term(term.term)
        return f"!{inner}" if isinstance(term.term, ArgumentTerm) else f"!({inner})"
    if isinstance(term, AndTerm):
        return f"({write_term(term.left)} & {write_term(term.right)})"
    if isinstance(term, OrTerm):
        return f"({write_term(term.left)} | {write_term(term.right)})"
    raise TypeError(f"unsupported term: {term!r}")


def parse_epistemic_formula(text: str) -> EpistemicFormula:
    parser = _TokenParser(text)
    formula = parser.parse_or_formula()
    parser.expect_end()
    return formula


def write_epistemic_formula(formula: EpistemicFormula) -> str:
    if isinstance(formula, AtomFormula):
        return (
            f"{write_operational_formula(formula.atom.formula)} "
            f"{formula.atom.operator} {_format_number(formula.atom.threshold)}"
        )
    if isinstance(formula, NotFormula):
        inner = write_epistemic_formula(formula.formula)
        return f"!({inner})"
    if isinstance(formula, AndFormula):
        return f"({write_epistemic_formula(formula.left)} & {write_epistemic_formula(formula.right)})"
    if isinstance(formula, OrFormula):
        return f"({write_epistemic_formula(formula.left)} | {write_epistemic_formula(formula.right)})"
    raise TypeError(f"unsupported epistemic formula: {formula!r}")


def write_operational_formula(formula: OperationalFormula) -> str:
    parts = [f"p({write_term(formula.terms[0].term)})"]
    for operator, term in zip(formula.operators, formula.terms[1:], strict=True):
        parts.append(f"{operator} p({write_term(term.term)})")
    return " ".join(parts)


class _TokenParser:
    def __init__(self, text: str) -> None:
        self.tokens = _tokenize(text)
        self.index = 0

    def peek(self) -> str | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise ValueError("unexpected end of input")
        self.index += 1
        return token

    def take_if(self, token: str) -> bool:
        if self.peek() == token:
            self.index += 1
            return True
        return False

    def expect(self, token: str) -> None:
        actual = self.take()
        if actual != token:
            raise ValueError(f"expected {token!r}, got {actual!r}")

    def expect_end(self) -> None:
        if self.peek() is not None:
            raise ValueError(f"unexpected token: {self.peek()!r}")

    def parse_or_term(self) -> Term:
        term = self.parse_and_term()
        while self.take_if("|"):
            term = OrTerm(term, self.parse_and_term())
        return term

    def parse_and_term(self) -> Term:
        term = self.parse_not_term()
        while self.take_if("&"):
            term = AndTerm(term, self.parse_not_term())
        return term

    def parse_not_term(self) -> Term:
        if self.take_if("!"):
            return NotTerm(self.parse_not_term())
        if self.take_if("("):
            term = self.parse_or_term()
            self.expect(")")
            return term
        token = self.take()
        if not _is_identifier(token):
            raise ValueError(f"expected argument identifier, got {token!r}")
        return ArgumentTerm(token)

    def parse_or_formula(self) -> EpistemicFormula:
        formula = self.parse_and_formula()
        while self.take_if("|"):
            formula = OrFormula(formula, self.parse_and_formula())
        return formula

    def parse_and_formula(self) -> EpistemicFormula:
        formula = self.parse_not_formula()
        while self.take_if("&"):
            formula = AndFormula(formula, self.parse_not_formula())
        return formula

    def parse_not_formula(self) -> EpistemicFormula:
        if self.take_if("!"):
            return NotFormula(self.parse_not_formula())
        if self.take_if("("):
            formula = self.parse_or_formula()
            self.expect(")")
            return formula
        return AtomFormula(self.parse_atom())

    def parse_atom(self) -> EpistemicAtom:
        formula = self.parse_operational_formula()
        operator = self.take()
        if operator not in {"=", "!=", "<", "<=", ">", ">="}:
            raise ValueError(f"expected epistemic comparison operator, got {operator!r}")
        threshold = float(self.take())
        return EpistemicAtom(formula, operator, threshold)  # type: ignore[arg-type]

    def parse_operational_formula(self) -> OperationalFormula:
        terms = [self.parse_probability_term()]
        operators: list[Literal["+", "-"]] = []
        while self.peek() in {"+", "-"}:
            operator = self.take()
            operators.append(operator)  # type: ignore[arg-type]
            terms.append(self.parse_probability_term())
        return OperationalFormula(tuple(terms), tuple(operators))

    def parse_probability_term(self) -> ProbabilityTerm:
        token = self.take()
        if token != "p":
            raise ValueError(f"expected probability term, got {token!r}")
        self.expect("(")
        term = self.parse_or_term()
        self.expect(")")
        return ProbabilityTerm(term)


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    position = 0
    while position < len(text):
        match = _TOKEN_RE.match(text, position)
        if match is None:
            raise ValueError(f"invalid token near {text[position:]!r}")
        tokens.append(match.group(1))
        position = match.end()
    return tokens


def _is_identifier(token: str) -> bool:
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token) is not None


def _compare(left: float, operator: ComparisonOperator, right: float) -> bool:
    if operator == "=":
        return abs(left - right) <= 1e-12
    if operator == "!=":
        return abs(left - right) > 1e-12
    if operator == "<":
        return left < right
    if operator == "<=":
        return left <= right + 1e-12
    if operator == ">":
        return left > right
    if operator == ">=":
        return left + 1e-12 >= right
    raise ValueError(f"unsupported comparison operator: {operator}")


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)


class InfluenceKind(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EpistemicLabel(StrEnum):
    POSITIVE = "+"
    NEGATIVE = "-"
    DEPENDENT = "*"


@dataclass(frozen=True)
class Influence:
    source: str
    target: str
    kind: InfluenceKind


@dataclass(frozen=True)
class LabelledArc:
    source: str
    target: str
    labels: frozenset[EpistemicLabel]

    def __post_init__(self) -> None:
        labels = frozenset(EpistemicLabel(label) for label in self.labels)
        if not labels:
            raise ValueError("labelled epistemic arcs must have at least one label")
        object.__setattr__(self, "source", str(self.source))
        object.__setattr__(self, "target", str(self.target))
        object.__setattr__(self, "labels", labels)


@dataclass(frozen=True)
class LabelledEpistemicGraph:
    arguments: frozenset[str]
    arcs: frozenset[LabelledArc]

    def __post_init__(self) -> None:
        arguments = frozenset(str(argument) for argument in self.arguments)
        unknown = sorted(
            (arc.source, arc.target)
            for arc in self.arcs
            if arc.source not in arguments or arc.target not in arguments
        )
        if unknown:
            raise ValueError(f"labelled arcs must reference declared arguments: {unknown!r}")
        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "arcs", frozenset(self.arcs))

    def parents(self, argument: str) -> frozenset[str]:
        return frozenset(arc.source for arc in self.arcs if arc.target == argument)

    def parents_by_label(self, argument: str, label: EpistemicLabel) -> frozenset[str]:
        return frozenset(
            arc.source
            for arc in self.arcs
            if arc.target == argument and label in arc.labels
        )


class LinearRelation(Enum):
    LE = "<="
    GE = ">="
    EQ = "="


@dataclass(frozen=True)
class LinearAtomicConstraint:
    coefficients: Mapping[str, float]
    relation: LinearRelation
    constant: float

    def __post_init__(self) -> None:
        normalized = {
            str(argument): float(coefficient)
            for argument, coefficient in self.coefficients.items()
            if coefficient != 0.0
        }
        object.__setattr__(self, "coefficients", normalized)
        object.__setattr__(self, "constant", float(self.constant))

    def satisfied_by(self, labelling: Mapping[str, float]) -> bool:
        value = sum(
            coefficient * float(labelling[argument])
            for argument, coefficient in self.coefficients.items()
        )
        if self.relation == LinearRelation.LE:
            return value <= self.constant + 1e-12
        if self.relation == LinearRelation.GE:
            return value + 1e-12 >= self.constant
        if self.relation == LinearRelation.EQ:
            return abs(value - self.constant) <= 1e-12
        raise ValueError(f"unsupported linear relation: {self.relation}")


def coherence_attack_constraint(attacker: str, target: str) -> LinearAtomicConstraint:
    """Return Potyka's attack coherence constraint P(target) <= 1 - P(attacker)."""
    return LinearAtomicConstraint(
        {attacker: 1.0, target: 1.0},
        LinearRelation.LE,
        1.0,
    )


def support_monotonic_constraint(supporter: str, target: str) -> LinearAtomicConstraint:
    """Return the support-dual monotonic constraint P(target) >= P(supporter)."""
    return LinearAtomicConstraint(
        {supporter: 1.0, target: -1.0},
        LinearRelation.LE,
        0.0,
    )


def constraints_satisfiable(
    arguments: frozenset[str],
    constraints: Sequence[LinearAtomicConstraint],
) -> bool:
    solver, variables = _linear_solver(arguments)
    for constraint in constraints:
        _add_linear_constraint(solver, variables, constraint)
    return str(solver.check()) == "sat"


def constraints_entail(
    arguments: frozenset[str],
    constraints: Sequence[LinearAtomicConstraint],
    conclusion: LinearAtomicConstraint,
) -> bool:
    solver, variables = _linear_solver(arguments)
    for constraint in constraints:
        _add_linear_constraint(solver, variables, constraint)
    _add_negated_linear_constraint(solver, variables, conclusion)
    return str(solver.check()) == "unsat"


def least_squares_update_labelling(
    arguments: frozenset[str],
    current: Mapping[str, float],
    constraints: Sequence[LinearAtomicConstraint],
) -> dict[str, float] | None:
    """Return a least-squares atomic labelling update, or ``None`` if unsatisfiable."""
    arguments = frozenset(str(argument) for argument in arguments)
    current = {str(argument): float(value) for argument, value in current.items()}
    missing = sorted(arguments - set(current))
    extra = sorted(set(current) - arguments)
    if missing or extra:
        raise ValueError(f"current labelling keys must match arguments: missing={missing!r}, extra={extra!r}")
    if any(value < 0.0 or value > 1.0 for value in current.values()):
        raise ValueError("current labelling values must lie in [0, 1]")
    if all(constraint.satisfied_by(current) for constraint in constraints):
        return {argument: current[argument] for argument in sorted(arguments)}
    if not constraints_satisfiable(arguments, constraints):
        return None

    projection_constraints = list(constraints)
    for argument in sorted(arguments):
        projection_constraints.append(
            LinearAtomicConstraint({argument: 1.0}, LinearRelation.GE, 0.0)
        )
        projection_constraints.append(
            LinearAtomicConstraint({argument: 1.0}, LinearRelation.LE, 1.0)
        )
    updated = _project_labelling(current, projection_constraints)
    return {argument: round(updated[argument], 12) for argument in sorted(arguments)}


def _linear_solver(arguments: frozenset[str]):
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("linear epistemic constraint reasoning requires z3-solver") from exc

    variables = {argument: z3.Real(argument) for argument in sorted(arguments)}
    solver = z3.Solver()
    for variable in variables.values():
        solver.add(variable >= 0, variable <= 1)
    return solver, variables


def _linear_expr(variables, constraint: LinearAtomicConstraint):
    expr = 0
    for argument, coefficient in constraint.coefficients.items():
        if argument not in variables:
            raise ValueError(f"constraint references unknown argument: {argument!r}")
        expr = expr + coefficient * variables[argument]
    return expr


def _add_linear_constraint(solver, variables, constraint: LinearAtomicConstraint) -> None:
    expr = _linear_expr(variables, constraint)
    if constraint.relation == LinearRelation.LE:
        solver.add(expr <= constraint.constant)
    elif constraint.relation == LinearRelation.GE:
        solver.add(expr >= constraint.constant)
    elif constraint.relation == LinearRelation.EQ:
        solver.add(expr == constraint.constant)
    else:
        raise ValueError(f"unsupported linear relation: {constraint.relation}")


def _add_negated_linear_constraint(solver, variables, constraint: LinearAtomicConstraint) -> None:
    expr = _linear_expr(variables, constraint)
    if constraint.relation == LinearRelation.LE:
        solver.add(expr > constraint.constant)
    elif constraint.relation == LinearRelation.GE:
        solver.add(expr < constraint.constant)
    elif constraint.relation == LinearRelation.EQ:
        solver.add(expr != constraint.constant)
    else:
        raise ValueError(f"unsupported linear relation: {constraint.relation}")


def _project_labelling(
    current: Mapping[str, float],
    constraints: Sequence[LinearAtomicConstraint],
) -> dict[str, float]:
    point = {argument: float(value) for argument, value in current.items()}
    for _ in range(10_000):
        max_violation = 0.0
        for constraint in constraints:
            violation = _constraint_violation(point, constraint)
            max_violation = max(max_violation, abs(violation))
            if abs(violation) <= 1e-12:
                continue
            norm = sum(coefficient * coefficient for coefficient in constraint.coefficients.values())
            if norm == 0.0:
                continue
            for argument, coefficient in constraint.coefficients.items():
                point[argument] = point[argument] - (violation / norm) * coefficient
        if max_violation <= 1e-10:
            break
    return point


def _constraint_violation(
    point: Mapping[str, float],
    constraint: LinearAtomicConstraint,
) -> float:
    value = sum(
        coefficient * float(point[argument])
        for argument, coefficient in constraint.coefficients.items()
    )
    if constraint.relation == LinearRelation.LE:
        return max(0.0, value - constraint.constant)
    if constraint.relation == LinearRelation.GE:
        return min(0.0, value - constraint.constant)
    if constraint.relation == LinearRelation.EQ:
        return value - constraint.constant
    raise ValueError(f"unsupported linear relation: {constraint.relation}")


@dataclass(frozen=True)
class BeliefConstraint:
    argument: str
    lower: float = 0.0
    upper: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.lower <= self.upper <= 1.0:
            raise ValueError("belief constraint bounds must satisfy 0 <= lower <= upper <= 1")


@dataclass(frozen=True)
class EpistemicGraph:
    arguments: frozenset[str]
    influences: frozenset[Influence] = frozenset()
    constraints: tuple[BeliefConstraint, ...] = ()

    def __post_init__(self) -> None:
        arguments = frozenset(self.arguments)
        unknown_influences = sorted(
            (influence.source, influence.target)
            for influence in self.influences
            if influence.source not in arguments or influence.target not in arguments
        )
        if unknown_influences:
            raise ValueError(f"influences must reference declared arguments: {unknown_influences!r}")
        unknown_constraints = sorted(
            constraint.argument
            for constraint in self.constraints
            if constraint.argument not in arguments
        )
        if unknown_constraints:
            raise ValueError(f"constraints must reference declared arguments: {unknown_constraints!r}")
        object.__setattr__(self, "arguments", arguments)
        object.__setattr__(self, "influences", frozenset(self.influences))
        object.__setattr__(self, "constraints", tuple(self.constraints))


def _constraint_by_argument(graph: EpistemicGraph) -> dict[str, BeliefConstraint]:
    constraints: dict[str, BeliefConstraint] = {}
    for constraint in graph.constraints:
        existing = constraints.get(constraint.argument)
        if existing is None:
            constraints[constraint.argument] = constraint
        else:
            constraints[constraint.argument] = BeliefConstraint(
                constraint.argument,
                lower=max(existing.lower, constraint.lower),
                upper=min(existing.upper, constraint.upper),
            )
    return constraints


def _validate_assignment(
    graph: EpistemicGraph,
    assignment: Mapping[str, float],
) -> dict[str, float]:
    missing = sorted(graph.arguments - set(assignment))
    extra = sorted(set(assignment) - graph.arguments)
    if missing or extra:
        raise ValueError(f"assignment keys must match graph arguments: missing={missing!r}, extra={extra!r}")
    normalized = {argument: float(value) for argument, value in assignment.items()}
    out_of_range = sorted(
        argument
        for argument, value in normalized.items()
        if not 0.0 <= value <= 1.0
    )
    if out_of_range:
        raise ValueError(f"assignment values must be in [0, 1]: {out_of_range!r}")
    return normalized


def belief_assignment_satisfies(
    graph: EpistemicGraph,
    assignment: Mapping[str, float],
) -> bool:
    """Return whether ``assignment`` satisfies graph constraints."""
    values = _validate_assignment(graph, assignment)
    constraints = _constraint_by_argument(graph)
    for argument, constraint in constraints.items():
        value = values[argument]
        if value < constraint.lower or value > constraint.upper:
            return False

    for influence in graph.influences:
        source = values[influence.source]
        target = values[influence.target]
        if influence.kind == InfluenceKind.POSITIVE and target < source:
            return False
        if influence.kind == InfluenceKind.NEGATIVE and target > 1.0 - source:
            return False
    return True


def enumerate_satisfying_assignments(
    graph: EpistemicGraph,
    *,
    levels: tuple[float, ...] = (0.0, 0.5, 1.0),
) -> tuple[dict[str, float], ...]:
    """Enumerate satisfying assignments over a finite belief grid."""
    if not levels:
        raise ValueError("levels must not be empty")
    if any(level < 0.0 or level > 1.0 for level in levels):
        raise ValueError("levels must lie in [0, 1]")
    ordered = sorted(graph.arguments)
    satisfying: list[dict[str, float]] = []
    for values in product(levels, repeat=len(ordered)):
        assignment = dict(zip(ordered, values, strict=True))
        if belief_assignment_satisfies(graph, assignment):
            satisfying.append(assignment)
    return tuple(satisfying)


def update_assignment(
    graph: EpistemicGraph,
    evidence: Mapping[str, float],
) -> dict[str, float]:
    """Update a belief assignment in the monotone influence fragment."""
    unknown = sorted(set(evidence) - graph.arguments)
    if unknown:
        raise ValueError(f"evidence references unknown arguments: {unknown!r}")
    assignment = {argument: 0.5 for argument in graph.arguments}
    for argument, value in evidence.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError("evidence values must lie in [0, 1]")
        assignment[argument] = float(value)

    changed = True
    while changed:
        changed = False
        for influence in sorted(
            graph.influences,
            key=lambda item: (item.source, item.target, item.kind.value),
        ):
            source = assignment[influence.source]
            target = assignment[influence.target]
            if influence.kind == InfluenceKind.POSITIVE and target < source:
                assignment[influence.target] = source
                changed = True
            elif influence.kind == InfluenceKind.NEGATIVE and target > 1.0 - source:
                assignment[influence.target] = 1.0 - source
                changed = True
    return {
        argument: round(assignment[argument], 12)
        for argument in sorted(graph.arguments)
    }


def project_to_constellation_praf(graph: EpistemicGraph) -> ProbabilisticAF:
    """Project influences to a constellation PrAF where the mapping is defined."""
    constraints = _constraint_by_argument(graph)
    p_args = {
        argument: constraints[argument].lower
        if argument in constraints and constraints[argument].lower > 0.0
        else constraints[argument].upper
        if argument in constraints
        else 1.0
        for argument in graph.arguments
    }
    defeats = frozenset(
        (influence.source, influence.target)
        for influence in graph.influences
        if influence.kind == InfluenceKind.NEGATIVE
    )
    supports = frozenset(
        (influence.source, influence.target)
        for influence in graph.influences
        if influence.kind == InfluenceKind.POSITIVE
    )
    return ProbabilisticAF(
        framework=ArgumentationFramework(arguments=graph.arguments, defeats=defeats),
        p_args=p_args,
        p_defeats={defeat: 1.0 for defeat in defeats},
        supports=supports,
        p_supports={support: 1.0 for support in supports},
    )
