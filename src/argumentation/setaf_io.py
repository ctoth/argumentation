"""Input and output formats for SETAFs.

The ASPARTIX SETAF format is an ASP fact format using ``arg/1``, ``att/2``,
and ``mem/2``. The compact ``p setaf`` helpers are package-local and are not
an ICCMA format.
"""

from __future__ import annotations

import re

from argumentation.setaf import SETAF


_ASPARTIX_FACT_RE = re.compile(
    r"^(?P<predicate>arg|att|mem)\((?P<body>[A-Za-z_][A-Za-z0-9_]*(?:,[A-Za-z_][A-Za-z0-9_]*)?)\)\.$"
)


def parse_aspartix_setaf(text: str) -> SETAF:
    """Parse the ASPARTIX SETAF ``arg/att/mem`` fact format."""
    arguments: set[str] = set()
    attack_targets: dict[str, str] = {}
    attack_members: dict[str, set[str]] = {}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue
        match = _ASPARTIX_FACT_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid ASPARTIX SETAF line {line_number}: {line!r}")

        predicate = match.group("predicate")
        parts = match.group("body").split(",")
        if predicate == "arg":
            if len(parts) != 1:
                raise ValueError(f"invalid arg/1 fact on line {line_number}: {line!r}")
            arguments.add(parts[0])
            continue
        if predicate == "att":
            if len(parts) != 2:
                raise ValueError(f"invalid att/2 fact on line {line_number}: {line!r}")
            attack_name, target = parts
            previous = attack_targets.setdefault(attack_name, target)
            if previous != target:
                raise ValueError(f"attack {attack_name!r} has multiple targets")
            continue
        if len(parts) != 2:
            raise ValueError(f"invalid mem/2 fact on line {line_number}: {line!r}")
        attack_name, member = parts
        attack_members.setdefault(attack_name, set()).add(member)

    unknown_attacks = sorted(set(attack_members) - set(attack_targets))
    if unknown_attacks:
        raise ValueError(f"mem facts reference unknown attack ids: {unknown_attacks!r}")

    attacks = frozenset(
        (frozenset(attack_members.get(attack_name, set())), target)
        for attack_name, target in attack_targets.items()
    )
    return SETAF(arguments=frozenset(arguments), attacks=attacks)


def write_aspartix_setaf(framework: SETAF) -> str:
    """Write deterministic ASPARTIX SETAF ``arg/att/mem`` facts."""
    lines: list[str] = []
    for argument in sorted(framework.arguments):
        lines.append(f"arg({argument}).")
    for index, (attackers, target) in enumerate(
        sorted(
            framework.attacks,
            key=lambda attack: (attack[1], tuple(sorted(attack[0]))),
        ),
        start=1,
    ):
        attack_name = f"r{index}"
        lines.append(f"att({attack_name},{target}).")
        for attacker in sorted(attackers):
            lines.append(f"mem({attack_name},{attacker}).")
    return "\n".join(lines) + "\n"


def parse_compact_setaf(text: str) -> SETAF:
    """Parse the package-local compact ``p setaf`` format."""
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
            raise ValueError("compact SETAF input must start with a p setaf header")
        if parts[0] == "arg" and len(parts) == 2:
            arguments.add(parts[1])
            continue
        if parts[0] == "att" and len(parts) >= 3:
            attacks.add((frozenset(parts[2:]), parts[1]))
            continue
        raise ValueError(f"invalid compact SETAF line {line_number}: {line!r}")
    if not seen_header:
        raise ValueError("compact SETAF input must include a p setaf header")
    return SETAF(arguments=frozenset(arguments), attacks=frozenset(attacks))


def write_compact_setaf(framework: SETAF) -> str:
    """Write the package-local compact ``p setaf`` format."""
    lines = ["p setaf"]
    for argument in sorted(framework.arguments):
        lines.append(f"arg {argument}")
    for attackers, target in sorted(
        framework.attacks,
        key=lambda attack: (attack[1], tuple(sorted(attack[0]))),
    ):
        lines.append("att " + target + " " + " ".join(sorted(attackers)))
    return "\n".join(lines) + "\n"


__all__ = [
    "parse_aspartix_setaf",
    "parse_compact_setaf",
    "write_aspartix_setaf",
    "write_compact_setaf",
]
