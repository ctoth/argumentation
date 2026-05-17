from __future__ import annotations

import argparse
from pathlib import Path

from tools import aba_shape_benchmark


DEFAULT_MANIFEST = Path("tests") / "manifests" / "aba-hard-bucket-targets.json"
DEFAULT_OUTPUT_JSON = Path("data") / "iccma" / "2025" / "runs" / "aba-hard-bucket-targets.json"
DEFAULT_OUTPUT_CSV = Path("data") / "iccma" / "2025" / "runs" / "aba-hard-bucket-targets.csv"
DEFAULT_PROFILE_DIR = Path("data") / "iccma" / "2025" / "profiles" / "aba-hard-bucket-targets"
DEFAULT_BACKENDS = ("auto", "asp", "sat")
DEFAULT_SUBTRACKS = ("SE-PR", "SE-ST")


def benchmark_args(args: argparse.Namespace) -> list[str]:
    command = [
        "--timeouts",
        str(args.manifest),
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
        "--profile-dir",
        str(args.profile_dir),
        "--profile-format",
        str(args.profile_format),
    ]
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
    parser.add_argument("--subtrack", action="append", default=list(DEFAULT_SUBTRACKS))
    parser.add_argument("--backend", action="append", default=list(DEFAULT_BACKENDS))
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument(
        "--profile-format",
        choices=["flamegraph", "raw", "speedscope", "chrometrace"],
        default="speedscope",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return aba_shape_benchmark.main(benchmark_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
