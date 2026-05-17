# /// script
# requires-python = ">=3.11"
# ///
"""Summarize dialectical chess tactical witness comparison artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("comparison_json", type=Path)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.comparison_json.read_text(encoding="utf-8"))
    text = render_summary(payload, args.comparison_json)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(text, encoding="utf-8")
    print(f"wrote {args.markdown_out}")
    return 0


def render_summary(payload: dict[str, Any], source: Path) -> str:
    lines = [
        "# Tactical Witness Delta Summary",
        "",
        f"Source: `{source}`.",
        "",
        "## Variant Totals",
        "",
        "| Variant | Solved | Hit Rate |",
        "| --- | ---: | ---: |",
    ]
    for name, totals in payload["variant_totals"].items():
        lines.append(
            "| `{name}` | {solved}/{total} | {hit_rate:.2f} |".format(
                name=name,
                solved=totals["solved"],
                total=totals["total"],
                hit_rate=totals["hit_rate"],
            )
        )

    lines.extend(["", "## Delta Totals", ""])
    lines.extend(
        [
            "| Pair | Changed | Left-only success | Right-only success |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for name, totals in payload["delta_totals"].items():
        lines.append(
            "| `{name}` | {changed} | {left_only} | {right_only} |".format(
                name=name,
                changed=totals["changed_decisions"],
                left_only=totals["left_only_success"],
                right_only=totals["right_only_success"],
            )
        )

    lines.extend(["", "## Regression Candidates", ""])
    lines.extend(
        [
            "| Pair | Puzzle | Expected | Left move | Right move | Left fork | Right fork | Left search | Right search |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in payload["positions"]:
        for pair_name, delta in entry["deltas"].items():
            if not delta["left_only_success"] and not delta["right_only_success"]:
                continue
            left_name, right_name = pair_name_to_variants(pair_name)
            left = entry["variants"][left_name]
            right = entry["variants"][right_name]
            lines.append(
                "| `{pair}` | `{puzzle}` | `{expected}` | `{left_move}` | `{right_move}` | {left_fork} | {right_fork} | {left_search} | {right_search} |".format(
                    pair=pair_name,
                    puzzle=entry["id"],
                    expected=", ".join(entry["expected_uci"]),
                    left_move=left["selected_uci"],
                    right_move=right["selected_uci"],
                    left_fork=labels(left["fork_reasons"]),
                    right_fork=labels(right["fork_reasons"]),
                    left_search=labels(left["search_reasons"]),
                    right_search=labels(right["search_reasons"]),
                )
            )
    return "\n".join(lines) + "\n"


def pair_name_to_variants(name: str) -> tuple[str, str]:
    mapping = {
        "fork_on_vs_fork_off": ("fork_on", "fork_off"),
        "fork_on_vs_search1": ("fork_on", "search1"),
        "search1_vs_search1_no_fork": ("search1", "search1_no_fork"),
        "fork_off_vs_search1_no_fork": ("fork_off", "search1_no_fork"),
    }
    return mapping[name]


def labels(items: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in items) or "-"


if __name__ == "__main__":
    raise SystemExit(main())
