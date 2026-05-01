from __future__ import annotations

import argparse
import re
from pathlib import Path


PHASE_HEADING = re.compile(r"^## Phase (?P<number>\d+): (?P<title>.+)$")
ORDER_ITEM = re.compile(r"^(?P<ordinal>\d+)\. Phase (?P<number>\d+): (?P<title>.+)\.$")
ORDER_HEADER = "## Dependency-Sorted Execution Order"


def phase_headings(text: str) -> dict[int, str]:
    phases: dict[int, str] = {}
    for line in text.splitlines():
        match = PHASE_HEADING.match(line)
        if match:
            phases[int(match.group("number"))] = match.group("title")
    return phases


def listed_order(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    try:
        start = lines.index(ORDER_HEADER) + 1
    except ValueError as exc:
        raise SystemExit(f"missing {ORDER_HEADER!r}") from exc

    order: list[tuple[int, str]] = []
    for line in lines[start:]:
        if line.startswith("## ") and order:
            break
        match = ORDER_ITEM.match(line)
        if match:
            order.append((int(match.group("number")), match.group("title")))
    if not order:
        raise SystemExit("dependency-sorted execution order is empty")
    return order


def check(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    phases = phase_headings(text)
    order = listed_order(text)
    ordered_phase_numbers = [number for number, _ in order]

    if len(ordered_phase_numbers) != len(set(ordered_phase_numbers)):
        raise SystemExit("dependency-sorted execution order contains duplicate phases")
    if set(ordered_phase_numbers) != set(phases):
        missing = sorted(set(phases) - set(ordered_phase_numbers))
        extra = sorted(set(ordered_phase_numbers) - set(phases))
        raise SystemExit(f"phase order mismatch: missing={missing!r}, extra={extra!r}")

    for number, title in order:
        if phases[number] != title:
            raise SystemExit(
                f"phase {number} title mismatch: order={title!r}, heading={phases[number]!r}"
            )

    for number, title in order:
        print(f"Phase {number}: {title}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workstream", type=Path)
    args = parser.parse_args()
    check(args.workstream)


if __name__ == "__main__":
    main()
