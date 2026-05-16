"""Check that the dialectical chess workstream phases are executable in order."""

from __future__ import annotations

import re
from pathlib import Path


WORKSTREAM = Path("workstreams/dialectical-chess-engine.md")
PHASE_RE = re.compile(r"^### Phase (?P<number>\d+): (?P<title>.+)$")


def main() -> int:
    text = WORKSTREAM.read_text(encoding="utf-8").splitlines()
    phases = [
        (int(match.group("number")), match.group("title"))
        for line in text
        if (match := PHASE_RE.match(line))
    ]
    if not phases:
        raise SystemExit(f"no phases found in {WORKSTREAM}")

    expected = list(range(phases[0][0], phases[0][0] + len(phases)))
    actual = [number for number, _title in phases]
    if actual != expected:
        raise SystemExit(
            f"phase order mismatch in {WORKSTREAM}: expected {expected}, got {actual}"
        )
    if actual[0] != 0:
        raise SystemExit(f"{WORKSTREAM} must start at Phase 0, got Phase {actual[0]}")

    print(f"{WORKSTREAM}: phases {actual[0]}..{actual[-1]} are ordered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
