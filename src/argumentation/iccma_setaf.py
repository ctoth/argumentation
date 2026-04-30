"""Compact ICCMA-style I/O for SETAFs."""

from __future__ import annotations

from argumentation.setaf import SETAF


def parse_setaf(text: str) -> SETAF:
    """Parse a compact ``p setaf`` text format."""
    arguments: set[str] = set()
    attacks: set[tuple[frozenset[str], str]] = set()
    seen_header = False
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts == ["p", "setaf"]:
            if seen_header:
                raise ValueError("multiple p setaf header lines")
            seen_header = True
            continue
        if not seen_header:
            raise ValueError("ICCMA SETAF input must start with a p setaf header")
        if parts[0] == "arg" and len(parts) == 2:
            arguments.add(parts[1])
            continue
        if parts[0] == "att" and len(parts) >= 3:
            attacks.add((frozenset(parts[2:]), parts[1]))
            continue
        raise ValueError(f"invalid SETAF line {line_number}: {line!r}")
    if not seen_header:
        raise ValueError("ICCMA SETAF input must include a p setaf header")
    return SETAF(arguments=frozenset(arguments), attacks=frozenset(attacks))


def write_setaf(framework: SETAF) -> str:
    """Write a deterministic compact ``p setaf`` text format."""
    lines = ["p setaf"]
    for argument in sorted(framework.arguments):
        lines.append(f"arg {argument}")
    for attackers, target in sorted(
        framework.attacks,
        key=lambda attack: (attack[1], tuple(sorted(attack[0]))),
    ):
        lines.append("att " + target + " " + " ".join(sorted(attackers)))
    return "\n".join(lines) + "\n"


__all__ = ["parse_setaf", "write_setaf"]
