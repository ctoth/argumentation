"""Build tests/manifests/iccma2025-frontier-v1.json from recal campaign artifacts.

Inputs:
- the 30-cell stratified sample (recal-sample.json) drawn from the 2025
  uncapped run's timeout rows,
- the timeout-recal 60s and 120s per-subtrack run files
  (iccma-2025-timeout-recal-{60,120}s-20260701-<SUBTRACK>.json).

Classification per (relative_path, subtrack) cell:
- melt:          solved in the 60s recal run (<= 60s budget),
- boundary_melt: still timeout at 60s but solved at 120s,
- hard:          timeout at 120s.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

TIMEOUT_TAGS = ("60s", "120s")
RUN_FILE_TEMPLATE = "iccma-2025-timeout-recal-{tag}-20260701-{subtrack}.json"


def load_run_rows(
    runs_dir: Path,
    subtracks: list[str],
) -> dict[str, dict[tuple[str, str], dict[str, Any]]]:
    indexed: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    for tag in TIMEOUT_TAGS:
        indexed[tag] = {}
        for subtrack in subtracks:
            path = runs_dir / RUN_FILE_TEMPLATE.format(tag=tag, subtrack=subtrack)
            for row in json.loads(path.read_text(encoding="utf-8")):
                indexed[tag][(str(row["instance"]), str(row["subtrack"]))] = row
    return indexed


def classify(
    r60: dict[str, Any] | None,
    r120: dict[str, Any] | None,
) -> str:
    if r60 is not None and r60.get("status") == "solved":
        return "melt"
    if r120 is not None and r120.get("status") == "solved":
        return "boundary_melt"
    if r120 is not None and r120.get("status") == "timeout":
        return "hard"
    raise ValueError(f"unclassifiable cell: 60s={r60!r} 120s={r120!r}")


def build_rows(
    sample: list[dict[str, Any]],
    runs: dict[str, dict[tuple[str, str], dict[str, Any]]],
    instances_root: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cell in sample:
        key = (str(cell["instance"]), str(cell["subtrack"]))
        r60 = runs["60s"].get(key)
        r120 = runs["120s"].get(key)
        recal_class = classify(r60, r120)
        detail = r60 or r120
        assert detail is not None
        instance_path = instances_root / Path(*key[0].split("/"))
        rows.append(
            {
                "year": 2025,
                "track": cell["track"],
                "subtrack": cell["subtrack"],
                "instance_kind": cell["instance_kind"],
                "relative_path": cell["instance"],
                "family": cell["family"],
                "arguments_or_atoms": cell["arguments_or_atoms"],
                "attacks": cell["attacks"],
                "assumptions": cell["assumptions"],
                "rules": cell["rules"],
                "contraries": detail.get("contraries"),
                "recal_class": recal_class,
                "recal_prior_status": cell["prior_status"],
                "recal_prior_elapsed_seconds": cell["prior_elapsed_seconds"],
                "recal_60s_status": None if r60 is None else r60.get("status"),
                "recal_60s_elapsed_seconds": None
                if r60 is None
                else r60.get("elapsed_seconds"),
                "recal_120s_status": None if r120 is None else r120.get("status"),
                "recal_120s_elapsed_seconds": None
                if r120 is None
                else r120.get("elapsed_seconds"),
                "input_sha256": sha256(instance_path),
            }
        )
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the frontier-v1 manifest.")
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, required=True)
    parser.add_argument("--instances-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = json.loads(args.sample.read_text(encoding="utf-8"))
    sample = payload["sample"]
    runs = load_run_rows(args.runs_dir, payload["subtracks"])
    rows = build_rows(sample, runs, args.instances_root)
    rows.sort(key=lambda row: (row["subtrack"], row["relative_path"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    by_class: dict[str, int] = {}
    for row in rows:
        by_class[row["recal_class"]] = by_class.get(row["recal_class"], 0) + 1
    print(
        json.dumps({"rows": len(rows), "by_class": by_class}, indent=2, sort_keys=True)
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
