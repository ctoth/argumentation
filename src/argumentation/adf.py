"""Abstract dialectical frameworks with operator-based semantics.

Brewka and Woltran 2010 define an ADF as statements, links, and acceptance
conditions. Brewka et al. 2013 recast ADF semantics through the three-valued
consensus operator. Polberg 2017 develops the formula-AST representation used
here: acceptance conditions are explicit, serializable syntax trees, not
callables.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from typing import Any, Mapping, TypeAlias

from argumentation.dung import ArgumentationFramework


class ThreeValued(StrEnum):
    T = "t"
    F = "f"
    U = "u"


class LinkType(StrEnum):
    SUPPORTING = "supporting"
    ATTACKING = "attacking"
    BOTH = "both"
    NEITHER = "neither"
    UNDEFINED = "undefined"


Interpretation: TypeAlias = frozenset[tuple[str, ThreeValued]]


class AcceptanceCondition:
    """Base class for serializable ADF acceptance-condition AST nodes."""

    def atoms(self) -> frozenset[str]:
        raise NotImplementedError

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        raise NotImplementedError


@dataclass(frozen=True, order=True)
class Atom(AcceptanceCondition):
    parent: str

    def atoms(self) -> frozenset[str]:
        return frozenset({self.parent})

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return assignment[self.parent]


@dataclass(frozen=True)
class _Not(AcceptanceCondition):
    child: AcceptanceCondition

    def atoms(self) -> frozenset[str]:
        return self.child.atoms()

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return not self.child.evaluate(assignment)


@dataclass(frozen=True)
class _And(AcceptanceCondition):
    children: tuple[AcceptanceCondition, ...]

    def atoms(self) -> frozenset[str]:
        return frozenset(atom for child in self.children for atom in child.atoms())

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return all(child.evaluate(assignment) for child in self.children)


@dataclass(frozen=True)
class _Or(AcceptanceCondition):
    children: tuple[AcceptanceCondition, ...]

    def atoms(self) -> frozenset[str]:
        return frozenset(atom for child in self.children for atom in child.atoms())

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return any(child.evaluate(assignment) for child in self.children)


@dataclass(frozen=True)
class True_(AcceptanceCondition):
    def atoms(self) -> frozenset[str]:
        return frozenset()

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return True


@dataclass(frozen=True)
class False_(AcceptanceCondition):
    def atoms(self) -> frozenset[str]:
        return frozenset()

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return False


def Not(child: AcceptanceCondition) -> AcceptanceCondition:
    child = _canonical(child)
    if isinstance(child, _Not):
        return child.child
    if isinstance(child, True_):
        return False_()
    if isinstance(child, False_):
        return True_()
    return _Not(child)


def And(children: tuple[AcceptanceCondition, ...] = ()) -> AcceptanceCondition:
    flattened: list[AcceptanceCondition] = []
    for child in children:
        canonical = _canonical(child)
        if isinstance(canonical, False_):
            return False_()
        if isinstance(canonical, True_):
            continue
        if isinstance(canonical, _And):
            flattened.extend(canonical.children)
        else:
            flattened.append(canonical)
    unique = tuple(sorted(set(flattened), key=_condition_sort_key))
    if not unique:
        return True_()
    if len(unique) == 1:
        return unique[0]
    return _And(unique)


def Or(children: tuple[AcceptanceCondition, ...] = ()) -> AcceptanceCondition:
    flattened: list[AcceptanceCondition] = []
    for child in children:
        canonical = _canonical(child)
        if isinstance(canonical, True_):
            return True_()
        if isinstance(canonical, False_):
            continue
        if isinstance(canonical, _Or):
            flattened.extend(canonical.children)
        else:
            flattened.append(canonical)
    unique = tuple(sorted(set(flattened), key=_condition_sort_key))
    if not unique:
        return False_()
    if len(unique) == 1:
        return unique[0]
    return _Or(unique)


@dataclass(frozen=True)
class AbstractDialecticalFramework:
    statements: frozenset[str]
    links: frozenset[tuple[str, str]]
    acceptance_conditions: Mapping[str, AcceptanceCondition]

    def __post_init__(self) -> None:
        statements = frozenset(self.statements)
        links = frozenset((str(parent), str(child)) for parent, child in self.links)
        if any(parent not in statements or child not in statements for parent, child in links):
            raise ValueError("ADF links must reference declared statements")
        if set(self.acceptance_conditions) != set(statements):
            raise ValueError("ADF acceptance_conditions must have one entry per statement")
        canonical_conditions = {
            statement: _canonical(condition)
            for statement, condition in self.acceptance_conditions.items()
        }
        for statement, condition in canonical_conditions.items():
            unknown = condition.atoms() - self.parents(statement)
            if unknown:
                raise ValueError(
                    f"acceptance condition for {statement!r} references non-parent atoms: "
                    f"{sorted(unknown)!r}"
                )
        object.__setattr__(self, "statements", statements)
        object.__setattr__(self, "links", links)
        object.__setattr__(self, "acceptance_conditions", canonical_conditions)

    def parents(self, statement: str) -> frozenset[str]:
        return frozenset(parent for parent, child in self.links if child == statement)


def interpretation_from_mapping(values: Mapping[str, ThreeValued]) -> Interpretation:
    return frozenset((statement, ThreeValued(value)) for statement, value in values.items())


def interpretation_to_mapping(interpretation: Interpretation) -> dict[str, ThreeValued]:
    return {statement: ThreeValued(value) for statement, value in interpretation}


def gamma(
    framework: AbstractDialecticalFramework,
    interpretation: Interpretation,
) -> Interpretation:
    values = interpretation_to_mapping(interpretation)
    result: dict[str, ThreeValued] = {}
    for statement in sorted(framework.statements):
        parents = sorted(framework.parents(statement))
        parent_values = {parent: values.get(parent, ThreeValued.U) for parent in parents}
        completions = _two_valued_completions(parent_values)
        evaluations = [
            framework.acceptance_conditions[statement].evaluate(completion)
            for completion in completions
        ]
        result[statement] = _meet_bool_values(evaluations)
    return interpretation_from_mapping(result)


def grounded_interpretation(framework: AbstractDialecticalFramework) -> Interpretation:
    current = interpretation_from_mapping(
        {statement: ThreeValued.U for statement in framework.statements}
    )
    while True:
        next_interpretation = gamma(framework, current)
        if next_interpretation == current:
            return current
        current = next_interpretation


def is_admissible(
    framework: AbstractDialecticalFramework,
    interpretation: Interpretation,
) -> bool:
    return _information_leq(interpretation, gamma(framework, interpretation))


def is_complete(
    framework: AbstractDialecticalFramework,
    interpretation: Interpretation,
) -> bool:
    return gamma(framework, interpretation) == interpretation


def admissible_interpretations(
    framework: AbstractDialecticalFramework,
) -> tuple[Interpretation, ...]:
    return tuple(
        interpretation
        for interpretation in _all_interpretations(framework.statements)
        if is_admissible(framework, interpretation)
    )


def complete_models(framework: AbstractDialecticalFramework) -> tuple[Interpretation, ...]:
    return tuple(
        interpretation
        for interpretation in _all_interpretations(framework.statements)
        if is_complete(framework, interpretation)
    )


def model_models(framework: AbstractDialecticalFramework) -> tuple[Interpretation, ...]:
    return tuple(
        interpretation
        for interpretation in complete_models(framework)
        if all(value is not ThreeValued.U for _, value in interpretation)
    )


def preferred_models(framework: AbstractDialecticalFramework) -> tuple[Interpretation, ...]:
    admissible = admissible_interpretations(framework)
    maximal = [
        interpretation
        for interpretation in admissible
        if not any(
            interpretation != other and _information_leq(interpretation, other)
            for other in admissible
        )
    ]
    return tuple(sorted(maximal, key=_interpretation_sort_key))


def stable_models(framework: AbstractDialecticalFramework) -> tuple[Interpretation, ...]:
    return model_models(framework)


def classify_link(
    framework: AbstractDialecticalFramework,
    parent: str,
    child: str,
) -> LinkType:
    if parent not in framework.statements or child not in framework.statements:
        raise ValueError("classify_link arguments must be declared statements")
    if (parent, child) not in framework.links:
        return LinkType.NEITHER
    polarity = _structural_polarity(framework.acceptance_conditions[child], parent, positive=True)
    if polarity == {True}:
        return LinkType.SUPPORTING
    if polarity == {False}:
        return LinkType.ATTACKING
    if polarity == {True, False}:
        return LinkType.BOTH
    return LinkType.NEITHER


def dung_to_adf(framework: ArgumentationFramework) -> AbstractDialecticalFramework:
    links = frozenset((attacker, target) for attacker, target in framework.defeats)
    conditions = {
        argument: And(
            tuple(Not(Atom(attacker)) for attacker, target in sorted(framework.defeats) if target == argument)
        )
        for argument in framework.arguments
    }
    return AbstractDialecticalFramework(
        statements=framework.arguments,
        links=links,
        acceptance_conditions=conditions,
    )


def adf_to_dung(framework: AbstractDialecticalFramework) -> ArgumentationFramework:
    defeats: set[tuple[str, str]] = set()
    for statement, condition in framework.acceptance_conditions.items():
        attackers = _dung_attackers_from_condition(condition)
        if attackers is None:
            raise ValueError("ADF is not in Dung-encoded conjunctive-negative form")
        defeats.update((attacker, statement) for attacker in attackers)
    return ArgumentationFramework(arguments=framework.statements, defeats=frozenset(defeats))


def to_json(condition: AcceptanceCondition) -> dict[str, Any]:
    condition = _canonical(condition)
    if isinstance(condition, Atom):
        return {"op": "Atom", "parent": condition.parent}
    if isinstance(condition, _Not):
        return {"op": "Not", "child": to_json(condition.child)}
    if isinstance(condition, _And):
        return {"op": "And", "children": [to_json(child) for child in condition.children]}
    if isinstance(condition, _Or):
        return {"op": "Or", "children": [to_json(child) for child in condition.children]}
    if isinstance(condition, True_):
        return {"op": "True"}
    if isinstance(condition, False_):
        return {"op": "False"}
    raise TypeError(f"unknown acceptance condition: {condition!r}")


def from_json(payload: Mapping[str, Any]) -> AcceptanceCondition:
    op = payload.get("op")
    if op == "Atom":
        return Atom(str(payload["parent"]))
    if op == "Not":
        return Not(from_json(payload["child"]))
    if op == "And":
        return And(tuple(from_json(child) for child in payload["children"]))
    if op == "Or":
        return Or(tuple(from_json(child) for child in payload["children"]))
    if op == "True":
        return True_()
    if op == "False":
        return False_()
    raise ValueError(f"unknown acceptance-condition JSON op: {op!r}")


def write_iccma_formula(condition: AcceptanceCondition) -> str:
    condition = _canonical(condition)
    if isinstance(condition, Atom):
        return condition.parent
    if isinstance(condition, _Not):
        return f"not({write_iccma_formula(condition.child)})"
    if isinstance(condition, _And):
        return "and(" + ",".join(write_iccma_formula(child) for child in condition.children) + ")"
    if isinstance(condition, _Or):
        return "or(" + ",".join(write_iccma_formula(child) for child in condition.children) + ")"
    if isinstance(condition, True_):
        return "true"
    if isinstance(condition, False_):
        return "false"
    raise TypeError(f"unknown acceptance condition: {condition!r}")


def parse_iccma_formula(text: str) -> AcceptanceCondition:
    parser = _FormulaParser(text)
    condition = parser.parse_condition()
    parser.expect_end()
    return condition


def _canonical(condition: AcceptanceCondition) -> AcceptanceCondition:
    if isinstance(condition, _Not):
        return Not(condition.child)
    if isinstance(condition, _And):
        return And(condition.children)
    if isinstance(condition, _Or):
        return Or(condition.children)
    return condition


def _condition_sort_key(condition: AcceptanceCondition) -> str:
    return write_iccma_formula(condition)


def _two_valued_completions(
    parent_values: Mapping[str, ThreeValued],
) -> list[dict[str, bool]]:
    unknown = [parent for parent, value in parent_values.items() if value is ThreeValued.U]
    fixed = {
        parent: value is ThreeValued.T
        for parent, value in parent_values.items()
        if value is not ThreeValued.U
    }
    completions: list[dict[str, bool]] = []
    for bits in product([False, True], repeat=len(unknown)):
        completion = dict(fixed)
        completion.update(dict(zip(unknown, bits, strict=True)))
        completions.append(completion)
    return completions or [fixed]


def _meet_bool_values(values: list[bool]) -> ThreeValued:
    if all(values):
        return ThreeValued.T
    if not any(values):
        return ThreeValued.F
    return ThreeValued.U


def _information_leq(left: Interpretation, right: Interpretation) -> bool:
    left_values = interpretation_to_mapping(left)
    right_values = interpretation_to_mapping(right)
    if set(left_values) != set(right_values):
        return False
    return all(
        left_value is ThreeValued.U or left_value == right_values[statement]
        for statement, left_value in left_values.items()
    )


def _all_interpretations(statements: frozenset[str]) -> tuple[Interpretation, ...]:
    ordered = sorted(statements)
    interpretations = [
        interpretation_from_mapping(dict(zip(ordered, values, strict=True)))
        for values in product(
            [ThreeValued.F, ThreeValued.U, ThreeValued.T],
            repeat=len(ordered),
        )
    ]
    return tuple(sorted(interpretations, key=_interpretation_sort_key))


def _interpretation_sort_key(interpretation: Interpretation) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((statement, value.value) for statement, value in interpretation))


def _structural_polarity(
    condition: AcceptanceCondition,
    parent: str,
    *,
    positive: bool,
) -> set[bool]:
    if isinstance(condition, Atom):
        return {positive} if condition.parent == parent else set()
    if isinstance(condition, _Not):
        return _structural_polarity(condition.child, parent, positive=not positive)
    if isinstance(condition, (_And, _Or)):
        result: set[bool] = set()
        for child in condition.children:
            result |= _structural_polarity(child, parent, positive=positive)
        return result
    return set()


def _dung_attackers_from_condition(condition: AcceptanceCondition) -> frozenset[str] | None:
    condition = _canonical(condition)
    if isinstance(condition, True_):
        return frozenset()
    if isinstance(condition, _Not) and isinstance(condition.child, Atom):
        return frozenset({condition.child.parent})
    if isinstance(condition, _And):
        attackers: set[str] = set()
        for child in condition.children:
            if not isinstance(child, _Not) or not isinstance(child.child, Atom):
                return None
            attackers.add(child.child.parent)
        return frozenset(attackers)
    return None


class _FormulaParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    def parse_condition(self) -> AcceptanceCondition:
        token = self._name()
        if token == "true":
            return True_()
        if token == "false":
            return False_()
        if token == "not":
            self._literal("(")
            child = self.parse_condition()
            self._literal(")")
            return Not(child)
        if token in {"and", "or"}:
            self._literal("(")
            children: list[AcceptanceCondition] = []
            if not self._peek(")"):
                while True:
                    children.append(self.parse_condition())
                    if self._peek(","):
                        self._literal(",")
                        continue
                    break
            self._literal(")")
            return And(tuple(children)) if token == "and" else Or(tuple(children))
        return Atom(token)

    def expect_end(self) -> None:
        self._skip_ws()
        if self.index != len(self.text):
            raise ValueError(f"unexpected formula suffix: {self.text[self.index:]!r}")

    def _name(self) -> str:
        self._skip_ws()
        start = self.index
        while self.index < len(self.text) and (
            self.text[self.index].isalnum() or self.text[self.index] == "_"
        ):
            self.index += 1
        if start == self.index:
            raise ValueError(f"expected formula token at {self.index}")
        return self.text[start:self.index]

    def _literal(self, value: str) -> None:
        self._skip_ws()
        if not self.text.startswith(value, self.index):
            raise ValueError(f"expected {value!r} at {self.index}")
        self.index += len(value)

    def _peek(self, value: str) -> bool:
        self._skip_ws()
        return self.text.startswith(value, self.index)

    def _skip_ws(self) -> None:
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1


__all__ = [
    "AcceptanceCondition",
    "AbstractDialecticalFramework",
    "And",
    "Atom",
    "False_",
    "Interpretation",
    "LinkType",
    "Not",
    "Or",
    "ThreeValued",
    "True_",
    "adf_to_dung",
    "admissible_interpretations",
    "classify_link",
    "complete_models",
    "dung_to_adf",
    "from_json",
    "gamma",
    "grounded_interpretation",
    "interpretation_from_mapping",
    "interpretation_to_mapping",
    "is_admissible",
    "is_complete",
    "model_models",
    "parse_iccma_formula",
    "preferred_models",
    "stable_models",
    "to_json",
    "write_iccma_formula",
]
