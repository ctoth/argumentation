from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import aba_shape_benchmark


DEFAULT_MANIFEST = Path("tests") / "manifests" / "aba-hard-bucket-targets.json"
DEFAULT_OUTPUT_JSON = Path("data") / "iccma" / "2025" / "runs" / "aba-hard-bucket-targets.json"
DEFAULT_OUTPUT_CSV = Path("data") / "iccma" / "2025" / "runs" / "aba-hard-bucket-targets.csv"
DEFAULT_PROFILE_DIR = Path("data") / "iccma" / "2025" / "profiles" / "aba-hard-bucket-targets"
DEFAULT_PROFILE_DURATION_SECONDS = 25.0
DEFAULT_BACKENDS = ("auto", "asp", "sat")
DEFAULT_SUBTRACKS = ("SE-PR", "SE-ST")


def benchmark_args(args: argparse.Namespace, *, manifest: Path | None = None) -> list[str]:
    manifest_path = args.manifest if manifest is None else manifest
    command = [
        "--timeouts",
        str(manifest_path),
        "--year",
        str(args.year),
        "--instance-kind",
        "aba",
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--output-json",
        str(args.output_json),
        "--output-csv",
        str(args.output_csv),
    ]
    if not args.no_profile:
        command.extend(
            [
                "--profile-dir",
                str(args.profile_dir),
                "--profile-format",
                str(args.profile_format),
                "--profile-duration-seconds",
                str(args.profile_duration_seconds),
            ]
        )
    for subtrack in args.subtrack:
        command.extend(["--subtrack", subtrack])
    for backend in args.backend:
        command.extend(["--backend", backend])
    return command


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the ABA hard-bucket target/control manifest through the shape benchmark."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument(
        "--target-id",
        action="append",
        default=[],
        help="Diagnostic filter for manifest target/control ids; defaults to the full manifest.",
    )
    parser.add_argument("--subtrack", action="append", default=list(DEFAULT_SUBTRACKS))
    parser.add_argument("--backend", action="append", default=list(DEFAULT_BACKENDS))
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument(
        "--profile-duration-seconds",
        type=float,
        default=DEFAULT_PROFILE_DURATION_SECONDS,
    )
    parser.add_argument(
        "--profile-format",
        choices=["flamegraph", "raw", "speedscope", "chrometrace"],
        default="speedscope",
    )
    parser.add_argument(
        "--no-profile",
        action="store_true",
        help="Disable py-spy profiling for benchmark gates that only need status.",
    )
    return parser.parse_args(argv)


def selected_manifest(args: argparse.Namespace) -> Path:
    if not args.target_id:
        return args.manifest
    requested = set(args.target_id)
    rows = json.loads(args.manifest.read_text(encoding="utf-8"))
    selected = [row for row in rows if row.get("target_id") in requested]
    found = {row.get("target_id") for row in selected}
    missing = sorted(requested - found)
    if missing:
        raise SystemExit(f"unknown hard-bucket target id(s): {', '.join(missing)}")
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    manifest = args.output_json.with_suffix(".manifest.json")
    manifest.write_text(json.dumps(selected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return aba_shape_benchmark.main(benchmark_args(args, manifest=selected_manifest(args)))


if __name__ == "__main__":
    raise SystemExit(main())
