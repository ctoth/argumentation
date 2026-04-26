"""ICCMA-style abstract argumentation framework I/O."""

from __future__ import annotations

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


__all__ = ["parse_af", "write_af"]
