"""Check that the dialectical chess workstream phases are executable in order."""

from __future__ import annotations

import re
from pathlib import Path


WORKSTREAMS = (
    Path("workstreams/dialectical-chess-engine.md"),
    Path("workstreams/dialectical-chess-owned-movegen.md"),
    Path("workstreams/dialectical-chess-benchmarks.md"),
)
PHASE_RE = re.compile(r"^### Phase (?P<number>\d+): (?P<title>.+)$")


def main() -> int:
    for workstream in WORKSTREAMS:
        check_workstream(workstream)
    return 0


def check_workstream(workstream: Path) -> None:
    text = workstream.read_text(encoding="utf-8").splitlines()
    phases = [
        (int(match.group("number")), match.group("title"))
        for line in text
        if (match := PHASE_RE.match(line))
    ]
    if not phases:
        raise SystemExit(f"no phases found in {workstream}")

    expected = list(range(phases[0][0], phases[0][0] + len(phases)))
    actual = [number for number, _title in phases]
    if actual != expected:
        raise SystemExit(
            f"phase order mismatch in {workstream}: expected {expected}, got {actual}"
        )
    if actual[0] != 0:
        raise SystemExit(f"{workstream} must start at Phase 0, got Phase {actual[0]}")

    print(f"{workstream}: phases {actual[0]}..{actual[-1]} are ordered")


if __name__ == "__main__":
    raise SystemExit(main())
