from __future__ import annotations

import argparse
import json
import multiprocessing
from pathlib import Path
import queue
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from argumentation import aba_sat
from argumentation.aba_preprocessing import simplify_aba
from argumentation.iccma import parse_aba


def _run_with_timeout(instance: Path, mode: str, *, timeout_seconds: float) -> dict[str, Any]:
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(target=_probe_worker, args=(str(instance), mode, result_queue))
    started = time.perf_counter()
    process.start()
    process.join(timeout_seconds)
    elapsed = time.perf_counter() - started
    if process.is_alive():
        process.kill()
        process.join()
        return {
            "status": "timeout",
            "elapsed_seconds": elapsed,
            "reason": f"timeout>{timeout_seconds}",
        }
    if process.exitcode != 0:
        return {
            "status": "error",
            "elapsed_seconds": elapsed,
            "reason": f"exit>{process.exitcode}",
        }
    try:
        payload = result_queue.get_nowait()
    except queue.Empty:
        return {
            "status": "error",
            "elapsed_seconds": elapsed,
            "reason": "no_result",
        }
    return {"elapsed_seconds": elapsed, **payload}


def _probe_worker(instance: str, mode: str, result_queue) -> None:
    try:
        framework = parse_aba(Path(instance).read_text(encoding="utf-8"))
        if mode == "simplify-stable":
            result = simplify_aba(framework, semantics="stable")
            result_queue.put(
                {
                    "status": "success",
                    "fixed_in": len(result.fixed_in),
                    "fixed_out": len(result.fixed_out),
                    "residual_assumptions": len(result.residual.assumptions),
                    "residual_language": len(result.residual.language),
                    "residual_rules": len(result.residual.rules),
                }
            )
            return
        if mode == "stable-production":
            witness = aba_sat.sat_stable_extension(framework)
        elif mode == "stable-ranked-direct":
            witness = aba_sat._sat_ranked_stable_extension(framework)
        elif mode == "preferred-production":
            witness = aba_sat.sat_support_extension(framework, "preferred")
        else:
            raise ValueError(f"unknown mode: {mode}")
        result_queue.put(
            {
                "status": "success",
                "witness_size": None if witness is None else len(witness),
            }
        )
    except BaseException as exc:
        result_queue.put(
            {
                "status": "error",
                "reason": f"{type(exc).__name__}: {exc}",
            }
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe production ABA ICCMA solve phases.")
    parser.add_argument("instance", type=Path)
    parser.add_argument(
        "--mode",
        choices=(
            "simplify-stable",
            "stable-production",
            "stable-ranked-direct",
            "preferred-production",
        ),
        required=True,
    )
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args(argv)

    payload = _run_with_timeout(
        args.instance,
        args.mode,
        timeout_seconds=args.timeout_seconds,
    )
    payload["mode"] = args.mode
    payload["instance"] = str(args.instance)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
