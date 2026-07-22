from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.iccma2025_run_native import TASK_TO_SEMANTICS, infer_contest_tag
from tools.iccma_timeout_corpus import collect_timeout_rows, summarize_timeout_rows


DEFAULT_ROOT = Path("data") / "iccma" / "2025"
DEFAULT_DATA_ROOT = Path("data") / "iccma"
DEFAULT_TIMEOUT_MANIFEST = (
    Path("tests") / "manifests" / "iccma2025-cap200-timeouts.json"
)
DEFAULT_STALE_SUBTRACKS = ("SE-PR", "SE-ST")
TASK_PREFIXES = {
    "DC": "credulous-acceptance",
    "DS": "skeptical-acceptance",
    "SE": "single-extension",
}


@dataclass(frozen=True)
class WorkstreamConfig:
    root: Path
    data_root: Path
    timeout_manifest: Path
    label: str
    backend: str
    max_af_arguments: int
    max_aba_assumptions: int
    timeout_seconds: float
    replay_timeout_seconds: float
    stale_subtracks: tuple[str, ...]
    iccma_binary: str | None = None
    profile_workers_dir: Path | None = None
    profile_worker_subtracks: tuple[str, ...] = ()
    skip_stale_replay: bool = False
    skip_cap_run: bool = False


def build_replay_command(
    config: WorkstreamConfig,
    *,
    subtrack: str,
    output_path: Path,
) -> list[str]:
    command = [
        sys.executable,
        "tools/iccma_run_timeout_rows.py",
        "--timeouts",
        str(config.timeout_manifest),
        "--year",
        "2025",
        "--subtrack",
        subtrack,
        "--timeout-seconds",
        str(config.replay_timeout_seconds),
        "--backend",
        config.backend,
        "--data-root",
        str(config.data_root),
        "--output",
        str(output_path),
    ]
    if config.iccma_binary is not None:
        command.extend(["--iccma-binary", config.iccma_binary])
    return command


def build_cap_command(config: WorkstreamConfig, *, event_log_path: Path) -> list[str]:
    command = [
        sys.executable,
        "tools/iccma2025_run_native.py",
        "--root",
        str(config.root),
        "--backend",
        config.backend,
        "--max-af-arguments",
        str(config.max_af_arguments),
        "--max-aba-assumptions",
        str(config.max_aba_assumptions),
        "--timeout-seconds",
        str(config.timeout_seconds),
        "--label",
        config.label,
        "--event-log-path",
        str(event_log_path),
    ]
    if config.iccma_binary is not None:
        command.extend(["--iccma-binary", config.iccma_binary])
    if config.profile_workers_dir is not None:
        command.extend(["--profile-workers-dir", str(config.profile_workers_dir)])
        for subtrack in config.profile_worker_subtracks:
            command.extend(["--profile-worker-subtrack", subtrack])
    return command


def run_command(command: Sequence[str], *, stdout_path: Path, stderr_path: Path) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8") as stdout:
        with stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(
                list(command),
                stdout=stdout,
                stderr=stderr,
                check=False,
                text=True,
            )
    return completed.returncode


def cap_output_paths(config: WorkstreamConfig) -> dict[str, Path]:
    output_dir = config.root / "runs"
    contest_tag = infer_contest_tag(config.root)
    stem = f"{contest_tag}-{config.label}"
    return {
        "json": output_dir / f"{stem}.json",
        "csv": output_dir / f"{stem}.csv",
        "summary": output_dir / f"{stem}-summary.json",
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def solver_class(instance_kind: object, subtrack: object) -> str:
    parts = str(subtrack).split("-", maxsplit=1)
    if len(parts) != 2:
        return f"{instance_kind}/unknown/{subtrack}"
    task_prefix, semantic_tag = parts
    task = TASK_PREFIXES.get(task_prefix, task_prefix.lower())
    semantics = TASK_TO_SEMANTICS.get(semantic_tag, semantic_tag.lower())
    return f"{instance_kind}/{task}/{semantics}"


def summarize_result_classes(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for item in results:
        source = item["source"]
        result = item["result"]
        class_name = solver_class(source.get("instance_kind"), source.get("subtrack"))
        bucket = buckets.setdefault(
            class_name, {"solver_class": class_name, "by_status": {}, "total": 0}
        )
        bucket["total"] += 1
        status = str(result.get("status"))
        bucket["by_status"][status] = bucket["by_status"].get(status, 0) + 1
    return sorted(buckets.values(), key=lambda item: item["solver_class"])


def summarize_timeout_classes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, int] = {}
    for row in rows:
        class_name = solver_class(row.get("instance_kind"), row.get("subtrack"))
        buckets[class_name] = buckets.get(class_name, 0) + 1
    return [
        {"solver_class": class_name, "timeouts": count}
        for class_name, count in sorted(buckets.items())
    ]


def summarize_fresh_timeouts(csv_path: Path) -> dict[str, Any]:
    if not csv_path.exists():
        return {
            "missing_csv": str(csv_path),
            "total_timeouts": None,
            "by_group": [],
            "by_solver_class": [],
        }
    rows = collect_timeout_rows([csv_path])
    summary = summarize_timeout_rows(rows)
    return summary | {"by_solver_class": summarize_timeout_classes(rows)}


def summarize_replay(output_path: Path) -> dict[str, Any]:
    if not output_path.exists():
        return {
            "missing_output": str(output_path),
            "total": None,
            "by_status": {},
            "by_solver_class": [],
        }
    payload = load_json(output_path)
    return payload["summary"] | {
        "by_solver_class": summarize_result_classes(payload["results"]),
    }


def execute_workstream(config: WorkstreamConfig) -> dict[str, Any]:
    runs_dir = config.root / "runs"
    logs_dir = runs_dir / f"{config.label}-logs"
    replays_dir = runs_dir / f"{config.label}-stale-timeout-replay"
    report_path = runs_dir / f"{config.label}-workstream.json"
    event_log_path = runs_dir / f"{config.label}-events.jsonl"

    commands: list[dict[str, Any]] = []
    replay_reports: list[dict[str, Any]] = []

    if not config.skip_stale_replay:
        for subtrack in config.stale_subtracks:
            output_path = replays_dir / f"{subtrack}.json"
            command = build_replay_command(
                config, subtrack=subtrack, output_path=output_path
            )
            stdout_path = logs_dir / f"replay-{subtrack}.stdout.log"
            stderr_path = logs_dir / f"replay-{subtrack}.stderr.jsonl"
            returncode = run_command(
                command, stdout_path=stdout_path, stderr_path=stderr_path
            )
            commands.append(
                {
                    "name": f"replay-{subtrack}",
                    "command": command,
                    "returncode": returncode,
                    "stdout": str(stdout_path),
                    "stderr": str(stderr_path),
                    "output": str(output_path),
                }
            )
            replay_reports.append(
                {
                    "subtrack": subtrack,
                    "summary": summarize_replay(output_path),
                    "output": str(output_path),
                }
            )

    cap_paths = cap_output_paths(config)
    if not config.skip_cap_run:
        command = build_cap_command(config, event_log_path=event_log_path)
        stdout_path = logs_dir / "cap.stdout.log"
        stderr_path = logs_dir / "cap.stderr.jsonl"
        returncode = run_command(
            command, stdout_path=stdout_path, stderr_path=stderr_path
        )
        commands.append(
            {
                "name": "cap-run",
                "command": command,
                "returncode": returncode,
                "stdout": str(stdout_path),
                "stderr": str(stderr_path),
                "event_log": str(event_log_path),
                "outputs": {key: str(path) for key, path in cap_paths.items()},
            }
        )

    report = {
        "config": {
            "backend": config.backend,
            "label": config.label,
            "max_aba_assumptions": config.max_aba_assumptions,
            "max_af_arguments": config.max_af_arguments,
            "replay_timeout_seconds": config.replay_timeout_seconds,
            "root": str(config.root),
            "stale_subtracks": list(config.stale_subtracks),
            "timeout_seconds": config.timeout_seconds,
            "timeout_manifest": str(config.timeout_manifest),
        },
        "commands": commands,
        "optimization_scope": {
            "benchmark_harness": "ICCMA 2025",
            "target": "general formal argumentation solver classes",
            "rule": "Use benchmark rows as reproducible pressure tests; keep speedups in reusable solvers, encodings, routing, preprocessing, or backend integrations.",
        },
        "fresh_cap": {
            "outputs": {key: str(path) for key, path in cap_paths.items()},
            "timeout_summary": summarize_fresh_timeouts(cap_paths["csv"]),
        },
        "stale_timeout_replay": replay_reports,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "report": str(report_path),
                "fresh_timeout_summary": report["fresh_cap"]["timeout_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return report


def parse_args(argv: list[str] | None = None) -> WorkstreamConfig:
    parser = argparse.ArgumentParser(
        description="Run the ICCMA 2025 post-router profiling and timeout-triage workstream."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument(
        "--timeout-manifest", type=Path, default=DEFAULT_TIMEOUT_MANIFEST
    )
    parser.add_argument("--label", default="post-router-cap200")
    parser.add_argument("--backend", default="auto")
    parser.add_argument("--max-af-arguments", type=int, default=200)
    parser.add_argument("--max-aba-assumptions", type=int, default=200)
    parser.add_argument("--timeout-seconds", type=float, default=25.0)
    parser.add_argument("--replay-timeout-seconds", type=float, default=30.0)
    parser.add_argument("--stale-subtrack", action="append", default=[])
    parser.add_argument("--iccma-binary")
    parser.add_argument("--profile-workers-dir", type=Path)
    parser.add_argument("--profile-worker-subtrack", action="append", default=[])
    parser.add_argument("--skip-stale-replay", action="store_true")
    parser.add_argument("--skip-cap-run", action="store_true")
    args = parser.parse_args(argv)
    return WorkstreamConfig(
        root=args.root,
        data_root=args.data_root,
        timeout_manifest=args.timeout_manifest,
        label=args.label,
        backend=args.backend,
        max_af_arguments=args.max_af_arguments,
        max_aba_assumptions=args.max_aba_assumptions,
        timeout_seconds=args.timeout_seconds,
        replay_timeout_seconds=args.replay_timeout_seconds,
        stale_subtracks=tuple(args.stale_subtrack) or DEFAULT_STALE_SUBTRACKS,
        iccma_binary=args.iccma_binary,
        profile_workers_dir=args.profile_workers_dir,
        profile_worker_subtracks=tuple(args.profile_worker_subtrack),
        skip_stale_replay=args.skip_stale_replay,
        skip_cap_run=args.skip_cap_run,
    )


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    report = execute_workstream(config)
    failed = [item for item in report["commands"] if item["returncode"] != 0]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
