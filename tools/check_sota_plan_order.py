from __future__ import annotations

import argparse
import re
from collections import defaultdict, deque
from pathlib import Path


PHASE_HEADING = re.compile(r"^## Phase (?P<number>\d+): (?P<title>.+)$")
DEPENDENCY = re.compile(r"^- Phase (?P<phase>\d+) (?P<body>.+)$")


def parse_phase_headings(plan_text: str) -> dict[int, str]:
    phases: dict[int, str] = {}
    for line in plan_text.splitlines():
        match = PHASE_HEADING.match(line)
        if match:
            phases[int(match.group("number"))] = match.group("title")
    return phases


def parse_dependencies(plan_text: str) -> dict[int, set[int]]:
    dependencies: dict[int, set[int]] = defaultdict(set)
    for line in plan_text.splitlines():
        match = DEPENDENCY.match(line)
        if not match:
            continue
        phase = int(match.group("phase"))
        body = match.group("body")
        if "has no upstream dependencies" in body:
            dependencies[phase] = set()
        elif "depends on all of the above" in body:
            dependencies[phase] = set(range(0, phase))
        elif "depends on Phase" in body:
            for dep in re.findall(r"Phase (?P<major>\d+)(?:\.\d+)?", body):
                dependencies[phase].add(int(dep))
    return dict(dependencies)


def topological_order(phases: dict[int, str], dependencies: dict[int, set[int]]) -> list[int]:
    dependencies.setdefault(0, set())
    missing_dependency_rows = sorted(set(phases) - set(dependencies))
    if missing_dependency_rows:
        raise SystemExit(
            "Missing dependency rows for phases: "
            + ", ".join(str(phase) for phase in missing_dependency_rows)
        )

    unknown_deps = sorted({dep for deps in dependencies.values() for dep in deps if dep not in phases})
    if unknown_deps:
        raise SystemExit(
            "Dependency rows mention unknown phases: "
            + ", ".join(str(phase) for phase in unknown_deps)
        )

    dependents: dict[int, set[int]] = defaultdict(set)
    indegree = {phase: len(dependencies[phase]) for phase in phases}
    for phase, deps in dependencies.items():
        for dep in deps:
            dependents[dep].add(phase)

    ready = deque(sorted(phase for phase, count in indegree.items() if count == 0))
    order: list[int] = []
    while ready:
        phase = ready.popleft()
        order.append(phase)
        for dependent in sorted(dependents[phase]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)

    if len(order) != len(phases):
        cycle = sorted(phase for phase, count in indegree.items() if count)
        raise SystemExit(
            "Cycle or unsatisfied dependency among phases: "
            + ", ".join(str(phase) for phase in cycle)
        )

    return order


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()

    text = args.plan.read_text(encoding="utf-8")
    phases = parse_phase_headings(text)
    dependencies = parse_dependencies(text)
    order = topological_order(phases, dependencies)

    for phase in order:
        print(f"Phase {phase}: {phases[phase]}")


if __name__ == "__main__":
    main()
