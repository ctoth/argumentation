"""Serialization and ICCMA formula I/O for ADF acceptance conditions.

Polberg 2017's formula-AST representation makes acceptance conditions explicit,
serializable syntax trees. This module holds the JSON round-trip, the ICCMA
``c``-line formula reader/writer, and the hand-written recursive-descent parser
used to read those formulae back.
"""

from __future__ import annotations

from typing import Any, Mapping

from argumentation.frameworks.adf import (
    AcceptanceCondition,
    And,
    Atom,
    False_,
    Not,
    Or,
    True_,
    _And,
    _canonical,
    _Not,
    _Or,
)


def to_json(condition: AcceptanceCondition) -> dict[str, Any]:
    condition = _canonical(condition)
    if isinstance(condition, Atom):
        return {"op": "Atom", "parent": condition.parent}
    if isinstance(condition, _Not):
        return {"op": "Not", "child": to_json(condition.child)}
    if isinstance(condition, _And):
        return {
            "op": "And",
            "children": [to_json(child) for child in condition.children],
        }
    if isinstance(condition, _Or):
        return {
            "op": "Or",
            "children": [to_json(child) for child in condition.children],
        }
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
        return (
            "and("
            + ",".join(write_iccma_formula(child) for child in condition.children)
            + ")"
        )
    if isinstance(condition, _Or):
        return (
            "or("
            + ",".join(write_iccma_formula(child) for child in condition.children)
            + ")"
        )
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
            raise ValueError(f"unexpected formula suffix: {self.text[self.index :]!r}")

    def _name(self) -> str:
        self._skip_ws()
        start = self.index
        while self.index < len(self.text) and (
            self.text[self.index].isalnum() or self.text[self.index] == "_"
        ):
            self.index += 1
        if start == self.index:
            raise ValueError(f"expected formula token at {self.index}")
        return self.text[start : self.index]

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
    "from_json",
    "parse_iccma_formula",
    "to_json",
    "write_iccma_formula",
]
