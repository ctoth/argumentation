# /// script
# requires-python = ">=3.11"
# ///
"""Summarize dialectical chess experiment matrix artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix_json", type=Path)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.matrix_json.read_text(encoding="utf-8"))
    text = render_summary(payload, args.matrix_json)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(text, encoding="utf-8")
    print(f"wrote {args.markdown_out}")
    return 0


def render_summary(payload: dict[str, Any], source: Path) -> str:
    runs = sorted(
        payload["runs"],
        key=lambda run: (-run["solved"], run["elapsed_ms"], run["name"]),
    )
    by_name = {run["name"]: run for run in payload["runs"]}
    lines = [
        "# Dialectical Chess Matrix Summary",
        "",
        f"Source: `{source}`.",
        "",
        f"Total elapsed ms: `{payload.get('elapsed_ms')}`.",
        "",
        "## Sorted Rows",
        "",
        "| Case | Solved | Hit Rate | Elapsed ms |",
        "| --- | ---: | ---: | ---: |",
    ]
    for run in runs:
        lines.append(
            "| `{name}` | {solved}/{total} | {hit_rate:.2f} | {elapsed:.2f} |".format(
                name=run["name"],
                solved=run["solved"],
                total=run["total"],
                hit_rate=run["hit_rate"],
                elapsed=run["elapsed_ms"],
            )
        )

    lines.extend(["", "## Positional Gates", ""])
    for left_name, right_name in (
        ("argument_d2", "argument_d2_no_positional"),
        ("optimizer_d2", "optimizer_d2_no_positional"),
    ):
        left = by_name[left_name]
        right = by_name[right_name]
        status = "pass" if left["solved"] >= right["solved"] else "fail"
        delta = left["solved"] - right["solved"]
        lines.append(
            f"- `{left_name}` versus `{right_name}`: {status}, delta `{delta}` "
            f"({left['solved']}/{left['total']} vs {right['solved']}/{right['total']})."
        )

    sample = payload.get("sample", {})
    if sample:
        lines.extend(["", "## Sample", ""])
        lines.append(f"- total: `{sample.get('total')}`")
        lines.append(f"- line move counts: `{sample.get('line_move_counts')}`")
        lines.append(f"- mate theme counts: `{sample.get('mate_theme_counts')}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
