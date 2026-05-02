from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TraceSummary:
    classification: str
    event_count: int
    event_counts_by_utility: dict[str, int]
    unique_fingerprints_by_utility: dict[str, int]
    max_learned_count: int | None
    last_loop_index: int | None
    terminal_status: str | None
    terminal_answer: str | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "event_count": self.event_count,
            "event_counts_by_utility": self.event_counts_by_utility,
            "unique_fingerprints_by_utility": self.unique_fingerprints_by_utility,
            "max_learned_count": self.max_learned_count,
            "last_loop_index": self.last_loop_index,
            "terminal_status": self.terminal_status,
            "terminal_answer": self.terminal_answer,
        }


def classify_trace(trace_path: Path, *, result_path: Path | None = None) -> TraceSummary:
    events = _read_json_lines(trace_path)
    terminal = _read_terminal_result(result_path)

    event_counts = Counter(
        str(event.get("utility_name", ""))
        for event in events
        if event.get("event") == "sat_check"
    )
    fingerprints: dict[str, set[str]] = defaultdict(set)
    learned_counts: list[int] = []
    loop_indexes: list[int] = []
    for event in events:
        if event.get("event") != "sat_check":
            continue
        utility_name = str(event.get("utility_name", ""))
        fingerprint = event.get("model_extension_fingerprint")
        if isinstance(fingerprint, str) and fingerprint:
            fingerprints[utility_name].add(fingerprint)
        learned_count = event.get("learned_count")
        if isinstance(learned_count, int):
            learned_counts.append(learned_count)
        loop_index = event.get("loop_index")
        if isinstance(loop_index, int):
            loop_indexes.append(loop_index)

    unique_counts = {
        utility_name: len(values)
        for utility_name, values in sorted(fingerprints.items())
    }
    event_counts_dict = {
        utility_name: count
        for utility_name, count in sorted(event_counts.items())
    }
    terminal_status = terminal.get("status") if terminal is not None else None
    terminal_answer = terminal.get("answer") if terminal is not None else None
    classification = _classify(
        event_counts=event_counts,
        unique_counts=unique_counts,
        terminal_status=terminal_status,
        terminal_answer=terminal_answer,
    )
    return TraceSummary(
        classification=classification,
        event_count=sum(event_counts.values()),
        event_counts_by_utility=event_counts_dict,
        unique_fingerprints_by_utility=unique_counts,
        max_learned_count=max(learned_counts) if learned_counts else None,
        last_loop_index=max(loop_indexes) if loop_indexes else None,
        terminal_status=terminal_status,
        terminal_answer=terminal_answer,
    )


def _classify(
    *,
    event_counts: Counter[str],
    unique_counts: dict[str, int],
    terminal_status: str | None,
    terminal_answer: str | None,
) -> str:
    attacker_checks = event_counts.get("preferred_skeptical_adm_ext_att", 0)
    extend_checks = event_counts.get("preferred_skeptical_extend_attacker", 0)
    unique_attackers = unique_counts.get("preferred_skeptical_adm_ext_att", 0)
    unique_witnesses = unique_counts.get("preferred_skeptical_extend_attacker", 0)

    if terminal_status == "solved" and terminal_answer == "false" and attacker_checks <= 1:
        return "quick-counterexample"
    if terminal_status == "timeout" and attacker_checks > 100:
        if unique_attackers == attacker_checks and unique_witnesses >= max(0, extend_checks - 1):
            return "unique-attacker-churn"
        return "repeated-attacker-churn"
    if terminal_status == "solved":
        return "solved"
    if terminal_status == "timeout":
        return "timeout"
    return "unknown"


def _read_json_lines(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        events.append(value)
    return events


def _read_terminal_result(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify streamed ICCMA SAT trace JSONL.")
    parser.add_argument("trace", type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args(argv)

    summary = classify_trace(args.trace, result_path=args.result)
    print(json.dumps(summary.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
