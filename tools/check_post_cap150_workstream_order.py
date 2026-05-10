from __future__ import annotations

import re
import sys
from pathlib import Path


WORKSTREAM = Path("workstreams") / "post-cap150-solver-frontier.md"
EXPECTED_ORDER = (
    "Hard-row manifest and benchmark harness.",
    "ABA preferred exact CEGAR solver.",
    "ABA external ASP comparison.",
    "ABA grounded/reduct preprocessing.",
    "Stubborn ABA stable row analysis.",
    "AF ideal direct formulation.",
    "Cap-200 expansion.",
)


def ordered_workstreams(text: str) -> tuple[str, ...]:
    match = re.search(
        r"The dependency order is:\n\n(?P<body>(?:\d+\. .+\n)+)",
        text,
    )
    if match is None:
        raise ValueError("dependency order block not found")
    return tuple(
        re.sub(r"^\d+\. ", "", line).strip()
        for line in match.group("body").splitlines()
        if line.strip()
    )


def main() -> int:
    actual = ordered_workstreams(WORKSTREAM.read_text(encoding="utf-8"))
    if actual != EXPECTED_ORDER:
        print("post-cap150 workstream order mismatch", file=sys.stderr)
        print(f"expected: {EXPECTED_ORDER!r}", file=sys.stderr)
        print(f"actual:   {actual!r}", file=sys.stderr)
        return 1
    print("post-cap150 workstream order ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
