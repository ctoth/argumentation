# /// script
# requires-python = ">=3.11"
# ///
"""Summarize positional-on/off chess comparison artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()

    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in args.inputs]
    text = render_summary(payloads)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(text, encoding="utf-8")
    print(f"wrote {args.markdown_out}")
    return 0


def render_summary(payloads: list[dict[str, Any]]) -> str:
    lines = [
        "# Positional Reason Delta Summary",
        "",
        "Generated from positional-on/off comparison artifacts.",
        "",
        "## Runs",
        "",
        "| Selector | Depth | Total | Changed | On-only | Off-only | Both fail changed | Both solve changed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    harmful_families: Counter[str] = Counter()
    tactical_context: Counter[str] = Counter()
    regression_candidates: list[dict[str, Any]] = []

    for payload in payloads:
        settings = payload["settings"]
        lines.append(
            "| {selector} | {depth} | {total} | {changed} | {on_only} | {off_only} | {both_fail} | {both_solve} |".format(
                selector=settings["selector_mode"],
                depth=settings["dialectic_depth"],
                total=payload["total"],
                changed=payload["changed_decisions"],
                on_only=payload["solved_only_positional_on"],
                off_only=payload["solved_only_positional_off"],
                both_fail=payload["both_fail_changed"],
                both_solve=payload["both_solve_changed"],
            )
        )
        for entry in payload["positions"]:
            classification = entry["classification"]
            if classification["harmful_when"] != "positional_off_only_success":
                continue
            regression_candidates.append(entry)
            harmful_families.update(classification["positional_reason_families"])
            update_tactical_context(tactical_context, classification, entry)

    lines.extend(["", "## Harmful Positional Families", ""])
    if harmful_families:
        for family, count in harmful_families.most_common():
            lines.append(f"- `{family}`: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Tactical Context", ""])
    if tactical_context:
        for label, count in tactical_context.most_common():
            lines.append(f"- `{label}`: {count}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Regression Candidates",
            "",
            "| Selector | Puzzle | Rating | Expected | Positional on | Positional off | Families | On reply attacks | Off tactical markers |",
            "| --- | --- | ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in regression_candidates:
        classification = entry["classification"]
        lines.append(
            "| {selector} | `{puzzle}` | {rating} | `{expected}` | `{on_move}` | `{off_move}` | {families} | {attacks} | {markers} |".format(
                selector=entry["selector_mode"],
                puzzle=entry["id"],
                rating=entry["rating"],
                expected=", ".join(entry["expected_uci"]),
                on_move=entry["positional_on"]["selected_uci"],
                off_move=entry["positional_off"]["selected_uci"],
                families=", ".join(f"`{item}`" for item in classification["positional_reason_families"]) or "-",
                attacks=str(len(classification["positional_move_unresolved_reply_attacks"])),
                markers=", ".join(f"`{item}`" for item in classification["winning_move_tactical_markers"]) or "-",
            )
        )
    return "\n".join(lines) + "\n"


def update_tactical_context(
    counter: Counter[str],
    classification: dict[str, Any],
    entry: dict[str, Any],
) -> None:
    if classification["winning_move_tactical_markers"]:
        counter["winning_move_has_tactical_marker"] += 1
    if classification["positional_move_unresolved_reply_attacks"]:
        counter["positional_move_has_unresolved_reply_attack"] += 1
    if classification["positional_move_no_immediate_tactical_warrant"]:
        counter["positional_move_no_immediate_tactical_warrant"] += 1
    if entry["themes"]:
        for theme in entry["themes"]:
            if theme.startswith("mateIn"):
                counter[f"theme:{theme}"] += 1


if __name__ == "__main__":
    raise SystemExit(main())
