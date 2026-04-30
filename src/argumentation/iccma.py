"""ICCMA-style argumentation framework I/O."""

from __future__ import annotations

from argumentation.adf import (
    AcceptanceCondition,
    AbstractDialecticalFramework,
    parse_iccma_formula,
    write_iccma_formula,
)
from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.dung import ArgumentationFramework


def parse_af(text: str) -> ArgumentationFramework:
    """Parse the ICCMA ``p af n`` numeric AF format."""
    argument_count: int | None = None
    attacks: set[tuple[str, str]] = set()

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[:2] == ["p", "af"]:
            if argument_count is not None:
                raise ValueError("multiple p af header lines")
            if len(parts) != 3 or not parts[2].isdigit():
                raise ValueError("p af header must be: p af <n>")
            argument_count = int(parts[2])
            continue
        if argument_count is None:
            raise ValueError("ICCMA AF input must start with a p af header")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise ValueError(f"attack line {line_number} must contain two numeric ids")
        attacker, target = parts
        _validate_attack_id(attacker, argument_count, line_number)
        _validate_attack_id(target, argument_count, line_number)
        attacks.add((attacker, target))

    if argument_count is None:
        raise ValueError("ICCMA AF input must include a p af header")

    arguments = frozenset(str(index) for index in range(1, argument_count + 1))
    return ArgumentationFramework(arguments=arguments, defeats=frozenset(attacks))


def write_af(framework: ArgumentationFramework) -> str:
    """Write a framework in deterministic ICCMA ``p af n`` format."""
    argument_ids = _numeric_argument_ids(framework)
    expected = list(range(1, len(argument_ids) + 1))
    if argument_ids != expected:
        raise ValueError("ICCMA AF arguments must be numeric ids 1..n")

    lines = [f"p af {len(argument_ids)}"]
    for attacker, target in sorted(
        framework.defeats,
        key=lambda attack: (int(attack[0]), int(attack[1])),
    ):
        lines.append(f"{attacker} {target}")
    return "\n".join(lines) + "\n"


def parse_adf(text: str) -> AbstractDialecticalFramework:
    """Parse a compact ICCMA-style ``p adf`` text format."""
    statements: set[str] = set()
    links: set[tuple[str, str]] = set()
    conditions: dict[str, AcceptanceCondition] = {}
    seen_header = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=2)
        if parts[:2] == ["p", "adf"]:
            if seen_header:
                raise ValueError("multiple p adf header lines")
            seen_header = True
            continue
        if not seen_header:
            raise ValueError("ICCMA ADF input must start with a p adf header")
        if parts[0] == "s" and len(parts) == 2:
            statements.add(parts[1])
            continue
        if parts[0] == "l" and len(parts) == 3:
            links.add((parts[1], parts[2]))
            continue
        if parts[0] == "c" and len(parts) == 3:
            conditions[parts[1]] = parse_iccma_formula(parts[2])
            continue
        raise ValueError(f"invalid ADF line {line_number}: {line!r}")
    if not seen_header:
        raise ValueError("ICCMA ADF input must include a p adf header")
    return AbstractDialecticalFramework(
        statements=frozenset(statements),
        links=frozenset(links),
        acceptance_conditions=conditions,
    )


def write_adf(framework: AbstractDialecticalFramework) -> str:
    """Write a deterministic compact ICCMA-style ``p adf`` text format."""
    lines = ["p adf"]
    for statement in sorted(framework.statements):
        lines.append(f"s {statement}")
    for parent, child in sorted(framework.links):
        lines.append(f"l {parent} {child}")
    for statement in sorted(framework.statements):
        lines.append(
            f"c {statement} {write_iccma_formula(framework.acceptance_conditions[statement])}"
        )
    return "\n".join(lines) + "\n"


def parse_aba(text: str) -> ABAFramework:
    """Parse an ICCMA flat-ABA text format.

    ICCMA 2025 uses the official numeric ``p aba <n>`` format.  The legacy
    compact package-local ``p aba`` format is still accepted for existing
    fixtures.
    """
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[:2] == ["p", "aba"] and len(parts) == 3:
            return _parse_numeric_aba(text)
        if parts == ["p", "aba"]:
            return _parse_compact_aba(text)
        break
    raise ValueError("ICCMA ABA input must start with a p aba header")


def _parse_compact_aba(text: str) -> ABAFramework:
    """Parse a compact package-local ``p aba`` flat-ABA text format."""
    atoms: dict[str, Literal] = {}
    assumptions: set[Literal] = set()
    contraries: dict[Literal, Literal] = {}
    rules: set[Rule] = set()
    seen_header = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts == ["p", "aba"]:
            if seen_header:
                raise ValueError("multiple p aba header lines")
            seen_header = True
            continue
        if not seen_header:
            raise ValueError("ICCMA ABA input must start with a p aba header")
        if parts[0] == "a" and len(parts) == 2:
            assumptions.add(_aba_literal(atoms, parts[1]))
            continue
        if parts[0] == "c" and len(parts) == 3:
            contraries[_aba_literal(atoms, parts[1])] = _aba_literal(atoms, parts[2])
            continue
        if parts[0] == "r" and len(parts) >= 2:
            rules.add(
                Rule(
                    tuple(_aba_literal(atoms, item) for item in parts[2:]),
                    _aba_literal(atoms, parts[1]),
                    "strict",
                )
            )
            continue
        raise ValueError(f"invalid ABA line {line_number}: {line!r}")
    if not seen_header:
        raise ValueError("ICCMA ABA input must include a p aba header")
    language = frozenset(set(atoms.values()) | assumptions | set(contraries.values()))
    return ABAFramework(
        language=language,
        rules=frozenset(rules),
        assumptions=frozenset(assumptions),
        contrary=contraries,
    )


def _parse_numeric_aba(text: str) -> ABAFramework:
    atom_count: int | None = None
    atoms: dict[str, Literal] = {}
    assumptions: set[Literal] = set()
    contraries: dict[Literal, Literal] = {}
    rules: set[Rule] = set()

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[:2] == ["p", "aba"]:
            if atom_count is not None:
                raise ValueError("multiple p aba header lines")
            if len(parts) != 3 or not parts[2].isdigit():
                raise ValueError("p aba header must be: p aba <n>")
            atom_count = int(parts[2])
            for index in range(1, atom_count + 1):
                _aba_literal(atoms, str(index))
            continue
        if atom_count is None:
            raise ValueError("ICCMA ABA input must start with a p aba header")
        if parts[0] == "a" and len(parts) == 2:
            assumptions.add(_aba_numeric_literal(atoms, parts[1], atom_count, line_number))
            continue
        if parts[0] == "c" and len(parts) == 3:
            contraries[
                _aba_numeric_literal(atoms, parts[1], atom_count, line_number)
            ] = _aba_numeric_literal(atoms, parts[2], atom_count, line_number)
            continue
        if parts[0] == "r" and len(parts) >= 2:
            rules.add(
                Rule(
                    tuple(
                        _aba_numeric_literal(atoms, item, atom_count, line_number)
                        for item in parts[2:]
                    ),
                    _aba_numeric_literal(atoms, parts[1], atom_count, line_number),
                    "strict",
                )
            )
            continue
        raise ValueError(f"invalid ABA line {line_number}: {line!r}")
    if atom_count is None:
        raise ValueError("ICCMA ABA input must include a p aba header")
    return ABAFramework(
        language=frozenset(atoms.values()),
        rules=frozenset(rules),
        assumptions=frozenset(assumptions),
        contrary=contraries,
    )


def write_aba(framework: ABAFramework) -> str:
    """Write a deterministic compact ICCMA-style ``p aba`` flat-ABA format."""
    lines = ["p aba"]
    for assumption in sorted(framework.assumptions, key=repr):
        lines.append(f"a {_aba_name(assumption)}")
    for assumption, contrary in sorted(framework.contrary.items(), key=lambda item: repr(item[0])):
        lines.append(f"c {_aba_name(assumption)} {_aba_name(contrary)}")
    for rule in sorted(framework.rules, key=lambda item: (_aba_name(item.consequent), tuple(map(_aba_name, item.antecedents)))):
        body = " ".join(_aba_name(antecedent) for antecedent in rule.antecedents)
        lines.append(f"r {_aba_name(rule.consequent)}" + (f" {body}" if body else ""))
    return "\n".join(lines) + "\n"


def write_numeric_aba(framework: ABAFramework) -> str:
    """Write the official numeric ICCMA 2025 ``p aba <n>`` flat-ABA format."""
    literals = sorted(framework.language, key=repr)
    ids = {literal: str(index) for index, literal in enumerate(literals, start=1)}
    lines = [f"p aba {len(literals)}"]
    for assumption in sorted(framework.assumptions, key=repr):
        lines.append(f"a {ids[assumption]}")
    for assumption, contrary in sorted(framework.contrary.items(), key=lambda item: repr(item[0])):
        lines.append(f"c {ids[assumption]} {ids[contrary]}")
    for rule in sorted(framework.rules, key=lambda item: (repr(item.consequent), tuple(map(repr, item.antecedents)))):
        body = " ".join(ids[antecedent] for antecedent in rule.antecedents)
        lines.append(f"r {ids[rule.consequent]}" + (f" {body}" if body else ""))
    return "\n".join(lines) + "\n"


def _validate_attack_id(value: str, argument_count: int, line_number: int) -> None:
    numeric = int(value)
    if numeric < 1 or numeric > argument_count:
        raise ValueError(
            f"attack line {line_number} references argument outside 1..{argument_count}"
        )


def _numeric_argument_ids(framework: ArgumentationFramework) -> list[int]:
    if not all(argument.isdigit() for argument in framework.arguments):
        raise ValueError("ICCMA AF arguments must be numeric ids")
    return sorted(int(argument) for argument in framework.arguments)


def _aba_literal(atoms: dict[str, Literal], name: str) -> Literal:
    if name not in atoms:
        atoms[name] = Literal(GroundAtom(name))
    return atoms[name]


def _aba_numeric_literal(
    atoms: dict[str, Literal],
    name: str,
    atom_count: int,
    line_number: int,
) -> Literal:
    if not name.isdigit():
        raise ValueError(f"ABA line {line_number} must contain numeric atom ids")
    numeric = int(name)
    if numeric < 1 or numeric > atom_count:
        raise ValueError(
            f"ABA line {line_number} references atom outside 1..{atom_count}"
        )
    return atoms[name]


def _aba_name(literal: Literal) -> str:
    if literal.negated or literal.atom.arguments:
        raise ValueError("compact ABA ICCMA format supports only nullary positive literals")
    return literal.atom.predicate


__all__ = [
    "parse_aba",
    "parse_adf",
    "parse_af",
    "write_aba",
    "write_adf",
    "write_af",
    "write_numeric_aba",
]
