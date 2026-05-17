from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


CALIBRATION_ENV = "ARGUMENTATION_PERF_CALIBRATION"
ENABLE_ENV = "ARGUMENTATION_PERF_CONTRACTS"

FALLBACK_BUDGETS_SECONDS = {
    "python_integer_loop": 0.25,
    "aba_parse": 0.05,
    "aba_closure": 0.05,
    "aba_no_attack_preferred": 0.25,
    "aba_large_dense_stable_route": 0.5,
}

REFERENCE_MEDIANS_SECONDS = {
    "python_integer_loop": 0.02,
    "aba_parse": 0.002,
    "aba_closure": 0.001,
}


def perf_contracts_enabled() -> bool:
    return os.environ.get(ENABLE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def require_perf_contracts_enabled() -> None:
    if not perf_contracts_enabled():
        pytest.skip(f"set {ENABLE_ENV}=1 to enable wall-clock performance contracts")


def calibrated_budget(name: str, *, fallback_seconds: float | None = None) -> float:
    fallback = FALLBACK_BUDGETS_SECONDS.get(name, fallback_seconds)
    if fallback is None:
        raise KeyError(f"no fallback budget for performance contract {name!r}")
    calibration = load_calibration()
    if calibration is None:
        return fallback
    factor = machine_slowdown_factor(calibration)
    return max(fallback, fallback * factor)


def load_calibration() -> dict[str, Any] | None:
    path_text = os.environ.get(CALIBRATION_ENV)
    if not path_text:
        return None
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError(f"{CALIBRATION_ENV} points to missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def machine_slowdown_factor(calibration: dict[str, Any]) -> float:
    records = {
        str(record.get("name")): record
        for record in calibration.get("benchmarks", [])
        if record.get("status") == "ok"
    }
    factors: list[float] = []
    for name, reference in REFERENCE_MEDIANS_SECONDS.items():
        median = records.get(name, {}).get("median_seconds")
        if isinstance(median, (int, float)) and median > 0:
            factors.append(float(median) / reference)
    if not factors:
        return 1.0
    return max(1.0, sorted(factors)[len(factors) // 2])


def assert_elapsed_within_budget(elapsed_seconds: float, name: str) -> None:
    budget = calibrated_budget(name)
    assert elapsed_seconds <= budget, (
        f"{name} took {elapsed_seconds:.6f}s, above calibrated budget {budget:.6f}s"
    )
