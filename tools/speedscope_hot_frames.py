from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


def frame_label(frame: dict[str, Any]) -> str:
    name = str(frame.get("name") or "<unknown>")
    file = str(frame.get("file") or "<unknown>")
    line = frame.get("line")
    if line is None:
        return f"{name} ({file})"
    return f"{name} ({file}:{line})"


def sample_weight(profile: dict[str, Any], sample_index: int) -> float:
    weights = profile.get("weights")
    if isinstance(weights, list) and sample_index < len(weights):
        return float(weights[sample_index])
    samples = profile.get("samples")
    if not isinstance(samples, list) or not samples:
        return 0.0
    start = float(profile.get("startValue") or 0.0)
    end = float(profile.get("endValue") or 0.0)
    return (end - start) / len(samples)


def hot_frames(payload: dict[str, Any]) -> dict[str, Counter[str]]:
    frames = payload["shared"]["frames"]
    exclusive: Counter[str] = Counter()
    inclusive: Counter[str] = Counter()
    for profile in payload.get("profiles", []):
        samples = profile.get("samples")
        if not isinstance(samples, list):
            continue
        for index, stack in enumerate(samples):
            if not stack:
                continue
            weight = sample_weight(profile, index)
            exclusive[frame_label(frames[stack[-1]])] += weight
            for frame_index in set(stack):
                inclusive[frame_label(frames[frame_index])] += weight
    return {"exclusive": exclusive, "inclusive": inclusive}


def serializable_top(counter: Counter[str], limit: int) -> list[dict[str, Any]]:
    return [
        {"seconds": round(seconds, 6), "frame": frame}
        for frame, seconds in counter.most_common(limit)
    ]


def summarize(path: Path, *, limit: int) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    counters = hot_frames(payload)
    return {
        "path": str(path),
        "exclusive": serializable_top(counters["exclusive"], limit),
        "inclusive": serializable_top(counters["inclusive"], limit),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize hot frames from a speedscope JSON file."
    )
    parser.add_argument("profile", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    print(
        json.dumps(summarize(args.profile, limit=args.limit), indent=2, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
