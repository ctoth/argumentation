"""Reproducibly select a stratified sample of ICCMA-2025 timeout rows.

Input: the 2026-05-14 truth-run CSV (4243 solved / 1871 timeout at
--timeout-seconds 5). Output: a frozen manifest of (family, subtrack, instance)
triples covering the major family x task strata, for a realistic-budget rerun
at 600 s. Deterministic: within each stratum instances are sorted
lexicographically by relative_path and the first k are taken.

Run:  uv run python experiments/iccma-census/select_sample.py \
        --csv <truth-run.csv> --out experiments/iccma-census/sample-timeout-600s.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

# Witness columns in the truth-run CSV can exceed the default 128 KiB field cap.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# Family classifier keyed on the instance basename prefix. Order matters only
# in that each prefix is disjoint here.
FAMILY_PREFIXES = {
    "crusti_g2io": "crusti_g",
    "scc": "scc_",
    "ER": "ER_",
    "mainkwt": "mainkwt_",
    "abcgen": "abcgen_c",
    "aba": "aba_",
}

# Strata plan: (family, subtrack) -> number of timeout rows to take.
# Chosen to cover every named family across the named tasks (DS-PR, DS-SST,
# SE-SST, SE-ID, DC-ID, SE-PR, DC-CO, SE-ST) while staying in the 48-60 band.
# AF families (crusti_g2io/scc/ER/mainkwt) carry the DC/DS/SE-AF tasks;
# abcgen/aba are ABA-only (SE-PR/SE-ST).
STRATA = {
    ("crusti_g2io", "DS-PR"): 3,
    ("crusti_g2io", "DS-SST"): 2,
    ("crusti_g2io", "SE-SST"): 2,
    ("crusti_g2io", "SE-ID"): 2,
    ("crusti_g2io", "DC-CO"): 3,
    ("crusti_g2io", "SE-ST"): 2,
    ("scc", "DS-PR"): 3,
    ("scc", "DS-SST"): 2,
    ("scc", "SE-ID"): 2,
    ("scc", "DC-CO"): 3,
    ("scc", "SE-ST"): 2,
    ("ER", "DS-PR"): 3,
    ("ER", "DS-SST"): 2,
    ("ER", "SE-SST"): 2,
    ("ER", "SE-ID"): 2,
    ("ER", "DC-ID"): 2,
    ("ER", "SE-PR"): 2,
    ("mainkwt", "DS-PR"): 3,
    ("abcgen", "SE-PR"): 3,
    ("abcgen", "SE-ST"): 3,
    ("aba", "SE-PR"): 2,
    ("aba", "SE-ST"): 2,
}


def classify_family(relative_path: str) -> str | None:
    basename = relative_path.replace("\\", "/").rsplit("/", 1)[-1]
    for family, prefix in FAMILY_PREFIXES.items():
        if basename.startswith(prefix):
            return family
    return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select(csv_path: Path) -> dict:
    # bucket[(family, subtrack)] = sorted list of relative_paths that timed out
    buckets: dict[tuple[str, str], list[str]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["status"] != "timeout":
                continue
            family = classify_family(row["instance"])
            if family is None:
                continue
            buckets.setdefault((family, row["subtrack"]), []).append(row["instance"])

    entries: list[dict] = []
    stratum_report: list[dict] = []
    for (family, subtrack), k in sorted(STRATA.items()):
        available = sorted(set(buckets.get((family, subtrack), [])))
        picked = available[:k]
        stratum_report.append(
            {
                "family": family,
                "subtrack": subtrack,
                "requested": k,
                "available": len(available),
                "selected": len(picked),
            }
        )
        for instance in picked:
            entries.append({"family": family, "subtrack": subtrack, "instance": instance})

    return {
        "source_csv": csv_path.name,
        "source_csv_sha256": sha256(csv_path),
        "budget_seconds": 600,
        "selection": "timeout rows only; per stratum sort by relative_path, take first k",
        "total_selected": len(entries),
        "strata": stratum_report,
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest = select(args.csv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} ({manifest['total_selected']} rows)")
    for stratum in manifest["strata"]:
        if stratum["selected"] < stratum["requested"]:
            print(f"  WARN under-filled: {stratum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
