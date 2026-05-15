from __future__ import annotations

from tools.speedscope_hot_frames import hot_frames, serializable_top


def test_hot_frames_counts_exclusive_and_inclusive_samples() -> None:
    payload = {
        "shared": {
            "frames": [
                {"name": "root", "file": "a.py", "line": 1},
                {"name": "slow", "file": "b.py", "line": 2},
                {"name": "leaf", "file": "c.py", "line": 3},
            ]
        },
        "profiles": [
            {
                "samples": [[0, 1], [0, 1, 2]],
                "weights": [0.5, 1.5],
            }
        ],
    }

    counters = hot_frames(payload)

    assert serializable_top(counters["exclusive"], 2) == [
        {"frame": "leaf (c.py:3)", "seconds": 1.5},
        {"frame": "slow (b.py:2)", "seconds": 0.5},
    ]
    assert serializable_top(counters["inclusive"], 1) == [
        {"frame": "root (a.py:1)", "seconds": 2.0},
    ]
