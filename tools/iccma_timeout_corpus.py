from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


_YEAR_RE = re.compile(r"iccma-(\d{4})")
_INT_FIELDS = {"arguments_or_atoms", "attacks", "assumptions", "rules", "contraries"}


def _optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _year_from_path(path: Path) -> int:
    match = _YEAR_RE.search(str(path))
    if match is None:
        raise ValueError(f"cannot infer ICCMA year from CSV path: {path}")
    return int(match.group(1))


def collect_timeout_rows(csv_paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for csv_path in csv_paths:
        year = _year_from_path(csv_path)
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for source in reader:
                if source.get("status") != "timeout":
                    continue
                rows.append(
                    {
                        "arguments_or_atoms": _optional_int(source.get("arguments_or_atoms")),
                        "attacks": _optional_int(source.get("attacks")),
                        "backend": source.get("backend") or "",
                        "contraries": _optional_int(source.get("contraries")),
                        "elapsed_seconds": _optional_float(source.get("elapsed_seconds")),
                        "error": source.get("error") or "",
                        "instance": source.get("instance") or "",
                        "instance_kind": source.get("instance_kind") or "",
                        "reason": source.get("reason") or "",
                        "rules": _optional_int(source.get("rules")),
                        "source_csv": str(csv_path),
                        "status": source.get("status") or "",
                        "subtrack": source.get("subtrack") or "",
                        "track": source.get("track") or "",
                        "year": year,
                        "assumptions": _optional_int(source.get("assumptions")),
                    }
                )
    return rows


def summarize_timeout_rows(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    counts = Counter(
        (
            row.get("year"),
            row.get("track"),
            row.get("subtrack"),
            row.get("instance_kind"),
        )
        for row in materialized
    )
    by_group = [
        {
            "count": count,
            "instance_kind": instance_kind,
            "subtrack": subtrack,
            "track": track,
            "year": year,
        }
        for (year, track, subtrack, instance_kind), count in counts.items()
    ]
    by_group.sort(key=lambda row: (row["track"], row["year"], row["subtrack"], row["instance_kind"]))
    return {"by_group": by_group, "total_timeouts": len(materialized)}


def add_input_hashes(rows: Iterable[dict[str, Any]], input_root: Path) -> list[dict[str, Any]]:
    checked_rows: list[dict[str, Any]] = []
    for row in rows:
        checked = dict(row)
        source_csv = checked.pop("source_csv", None)
        if source_csv is None:
            source_csv = row.get("source_csv")
        instance = checked["instance"]
        if not isinstance(instance, str):
            raise TypeError(f"manifest row instance must be a string: {instance!r}")
        input_path = input_root / Path(instance)
        if not input_path.exists():
            raise FileNotFoundError(f"manifest input does not exist: {input_path}")
        checked["input_sha256"] = _sha256(input_path)
        checked_rows.append(checked)
    return checked_rows


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect ICCMA timeout rows from result CSVs.")
    parser.add_argument("--csv", action="append", dest="csv_paths", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--label", default="cap100-timeouts")
    parser.add_argument("--checked-manifest", type=Path)
    parser.add_argument("--input-root", type=Path)
    args = parser.parse_args(argv)

    rows = collect_timeout_rows(args.csv_paths)
    summary = summarize_timeout_rows(rows)
    rows_path = args.output_dir / f"{args.label}-timeouts.json"
    summary_path = args.output_dir / f"{args.label}-summary.json"
    _write_json(rows_path, rows)
    _write_json(summary_path, summary)
    result = {"summary": summary, "timeouts": str(rows_path), "summary_path": str(summary_path)}
    if args.checked_manifest is not None:
        if args.input_root is None:
            parser.error("--input-root is required with --checked-manifest")
        checked_rows = add_input_hashes(rows, args.input_root)
        _write_json(args.checked_manifest, checked_rows)
        result["checked_manifest"] = str(args.checked_manifest)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
