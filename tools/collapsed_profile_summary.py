from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


def parse_collapsed_line(line: str) -> tuple[list[str], int] | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        stack_text, count_text = stripped.rsplit(" ", 1)
        count = int(count_text)
    except ValueError:
        return None
    frames = [frame for frame in stack_text.split(";") if frame]
    if not frames:
        return None
    return frames, count


def hot_frames(lines: list[str]) -> dict[str, Counter[str]]:
    exclusive: Counter[str] = Counter()
    inclusive: Counter[str] = Counter()
    for line in lines:
        parsed = parse_collapsed_line(line)
        if parsed is None:
            continue
        frames, count = parsed
        exclusive[frames[-1]] += count
        for frame in set(frames):
            inclusive[frame] += count
    return {"exclusive": exclusive, "inclusive": inclusive}


def top_frames(counter: Counter[str], limit: int) -> list[tuple[str, int]]:
    """Top ``limit`` frames by samples, ties broken by frame name.

    ``Counter.most_common`` breaks ties by insertion order, which for counters
    built from ``set(frames)`` iteration is PYTHONHASHSEED-dependent; the
    frame-name secondary key keeps output deterministic across seeds.
    """
    ranked = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:limit]


def serializable_top(
    counter: Counter[str],
    limit: int,
    *,
    total_samples: int,
) -> list[dict[str, Any]]:
    return [
        {
            "samples": samples,
            "share": round(samples / total_samples, 6) if total_samples else 0.0,
            "frame": frame,
        }
        for frame, samples in top_frames(counter, limit)
    ]


def summarize(path: Path, *, limit: int) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    counters = hot_frames(lines)
    total_samples = sum(counters["exclusive"].values())
    return {
        "path": str(path),
        "total_samples": total_samples,
        "exclusive": serializable_top(
            counters["exclusive"],
            limit,
            total_samples=total_samples,
        ),
        "inclusive": serializable_top(
            counters["inclusive"],
            limit,
            total_samples=total_samples,
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize hot frames from a py-spy raw collapsed profile."
    )
    parser.add_argument("profile", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    print(json.dumps(summarize(args.profile, limit=args.limit), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
