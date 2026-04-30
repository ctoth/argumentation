from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import shutil
import sys
import urllib.request
import zipfile


DATA_ROOT = Path("data") / "iccma" / "2025"


@dataclass(frozen=True)
class ArchiveSpec:
    name: str
    file_name: str
    url: str
    size: int
    md5: str
    extract_dir: str


ARCHIVES = {
    "instances": ArchiveSpec(
        name="instances",
        file_name="ICCMA-2025-instances.zip",
        url=(
            "https://zenodo.org/api/records/17949380/files/"
            "ICCMA-2025-instances.zip/content"
        ),
        size=866_229_263,
        md5="5b3231eb3206b78494db2b451ac3ab55",
        extract_dir="instances",
    ),
    "results": ArchiveSpec(
        name="results",
        file_name="ICCMA-2025-results.zip",
        url=(
            "https://zenodo.org/api/records/18506390/files/"
            "ICCMA-2025-results.zip/content"
        ),
        size=1_351_761,
        md5="262ea63627603d8906737d32228296c2",
        extract_dir="results",
    ),
}


@dataclass(frozen=True)
class ManifestRow:
    archive: str
    relative_path: str
    kind: str
    parse_status: str
    size: int
    arguments_or_atoms: int | None = None
    attacks: int | None = None
    assumptions: int | None = None
    rules: int | None = None
    contraries: int | None = None
    error: str | None = None


MAIN_TRACK = [
    ("DC-CO", "af", "main", True, 1200),
    ("DC-ST", "af", "main", True, 1200),
    ("DC-SST", "af", "main", True, 1200),
    ("DS-PR", "af", "main", True, 1200),
    ("DS-ST", "af", "main", True, 1200),
    ("DS-SST", "af", "main", True, 1200),
    ("SE-PR", "af", "main", True, 1200),
    ("SE-ST", "af", "main", True, 1200),
    ("SE-SST", "af", "main", True, 1200),
    ("SE-ID", "af", "main", True, 1200),
]

HEURISTICS_TRACK = [
    ("DC-CO", "af", "heuristics", False, 60),
    ("DC-ST", "af", "heuristics", False, 60),
    ("DC-SST", "af", "heuristics", False, 60),
    ("DC-ID", "af", "heuristics", False, 60),
    ("DS-PR", "af", "heuristics", False, 60),
    ("DS-ST", "af", "heuristics", False, 60),
    ("DS-SST", "af", "heuristics", False, 60),
]

DYNAMIC_TRACK = [
    ("DC-CO", "dynamic", "dynamic", False, 1200),
    ("DS-PR", "dynamic", "dynamic", False, 1200),
    ("DC-ST", "dynamic", "dynamic", False, 1200),
    ("DS-ST", "dynamic", "dynamic", False, 1200),
]

ABA_TRACK = [
    ("DC-CO", "aba", "aba", False, 1200),
    ("DC-ST", "aba", "aba", False, 1200),
    ("DS-PR", "aba", "aba", False, 1200),
    ("DS-ST", "aba", "aba", False, 1200),
    ("SE-PR", "aba", "aba", False, 1200),
    ("SE-ST", "aba", "aba", False, 1200),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare ICCMA 2025 benchmark data.")
    parser.add_argument("--root", type=Path, default=DATA_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("archive", choices=[*ARCHIVES, "all"], default="all", nargs="?")

    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("archive", choices=[*ARCHIVES, "all"], default="all", nargs="?")
    extract_parser.add_argument("--force", action="store_true")

    manifest_parser = subparsers.add_parser("manifest")
    manifest_parser.add_argument("--strict", action="store_true")

    subparsers.add_parser("tasks")
    subparsers.add_parser("all")

    args = parser.parse_args(argv)
    root: Path = args.root
    if args.command == "fetch":
        fetch_archives(root, selected=args.archive)
    elif args.command == "extract":
        extract_archives(root, selected=args.archive, force=args.force)
    elif args.command == "manifest":
        rows = write_manifest(root)
        if args.strict and any(row.parse_status == "error" for row in rows):
            return 1
    elif args.command == "tasks":
        write_task_matrix(root)
    elif args.command == "all":
        fetch_archives(root, selected="all")
        extract_archives(root, selected="all", force=False)
        rows = write_manifest(root)
        write_task_matrix(root)
        if any(row.parse_status == "error" for row in rows):
            return 1
    return 0


def fetch_archives(root: Path, *, selected: str) -> None:
    archive_dir = root / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    for spec in _selected_archives(selected):
        target = archive_dir / spec.file_name
        if target.exists():
            verify_archive(target, spec)
            print(f"verified {target}")
            continue
        temp = target.with_suffix(target.suffix + ".part")
        print(f"downloading {spec.file_name}")
        download(spec.url, temp)
        temp.replace(target)
        verify_archive(target, spec)
        print(f"verified {target}")


def extract_archives(root: Path, *, selected: str, force: bool) -> None:
    archive_dir = root / "archives"
    extract_root = root / "extracted"
    extract_root.mkdir(parents=True, exist_ok=True)
    for spec in _selected_archives(selected):
        archive_path = archive_dir / spec.file_name
        verify_archive(archive_path, spec)
        target = extract_root / spec.extract_dir
        if target.exists() and force:
            shutil.rmtree(target)
        if target.exists() and any(target.iterdir()):
            print(f"already extracted {target}")
            continue
        target.mkdir(parents=True, exist_ok=True)
        print(f"extracting {archive_path} -> {target}")
        safe_extract_zip(archive_path, target)


def write_manifest(root: Path) -> list[ManifestRow]:
    rows = build_manifest(root)
    manifest_dir = root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_path = manifest_dir / "iccma-2025-manifest.json"
    csv_path = manifest_dir / "iccma-2025-manifest.csv"
    json_path.write_text(
        json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(asdict(row) for row in rows)
    errors = sum(1 for row in rows if row.parse_status == "error")
    print(f"wrote {json_path} and {csv_path}: {len(rows)} rows, {errors} errors")
    return rows


def write_task_matrix(root: Path) -> None:
    rows = [
        {
            "track": track,
            "subtrack": subtrack,
            "instance_kind": instance_kind,
            "certificate_required": certificate_required,
            "timeout_seconds": timeout_seconds,
        }
        for subtrack, instance_kind, track, certificate_required, timeout_seconds in (
            MAIN_TRACK + HEURISTICS_TRACK + DYNAMIC_TRACK + ABA_TRACK
        )
    ]
    manifest_dir = root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_path = manifest_dir / "iccma-2025-task-matrix.json"
    csv_path = manifest_dir / "iccma-2025-task-matrix.csv"
    json_path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {json_path} and {csv_path}: {len(rows)} rows")


def build_manifest(root: Path) -> list[ManifestRow]:
    rows: list[ManifestRow] = []
    extracted = root / "extracted"
    for archive_name in ("instances", "results"):
        base = extracted / archive_name
        if not base.exists():
            continue
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            relative = path.relative_to(base).as_posix()
            rows.append(classify_file(archive_name, relative, path))
    return rows


def classify_file(archive_name: str, relative: str, path: Path) -> ManifestRow:
    size = path.stat().st_size
    if archive_name == "results":
        return ManifestRow(archive_name, relative, "results", "skipped", size)
    header = first_payload_line(path)
    try:
        if header.startswith("p af "):
            arguments, attacks = scan_af_file(path)
            return ManifestRow(
                archive_name,
                relative,
                "af",
                "ok",
                size,
                arguments_or_atoms=arguments,
                attacks=attacks,
            )
        if header.startswith("p aba"):
            atoms, assumptions, rules, contraries = scan_aba_file(path)
            return ManifestRow(
                archive_name,
                relative,
                "aba",
                "ok",
                size,
                arguments_or_atoms=atoms,
                assumptions=assumptions,
                rules=rules,
                contraries=contraries,
            )
        if path.suffix.lower() == ".py":
            return ManifestRow(archive_name, relative, "dynamic_app", "skipped", size)
        return ManifestRow(archive_name, relative, "unknown", "skipped", size)
    except Exception as exc:
        return ManifestRow(archive_name, relative, "unknown", "error", size, error=str(exc))


def scan_af_file(path: Path) -> tuple[int, int]:
    argument_count: int | None = None
    attacks = 0
    for line_number, parts in iter_payload_parts(path):
        if parts[:2] == ["p", "af"]:
            if argument_count is not None:
                raise ValueError("multiple p af header lines")
            if len(parts) != 3 or not parts[2].isdigit():
                raise ValueError("p af header must be: p af <n>")
            argument_count = int(parts[2])
            continue
        if argument_count is None:
            raise ValueError("ICCMA AF input must start with a p af header")
        if len(parts) != 2:
            raise ValueError(f"attack line {line_number} must contain two numeric ids")
        validate_numeric_id(parts[0], argument_count, line_number, "attack")
        validate_numeric_id(parts[1], argument_count, line_number, "attack")
        attacks += 1
    if argument_count is None:
        raise ValueError("ICCMA AF input must include a p af header")
    return argument_count, attacks


def scan_aba_file(path: Path) -> tuple[int, int, int, int]:
    atom_count: int | None = None
    assumptions: set[int] = set()
    rule_heads: set[int] = set()
    rule_count = 0
    contraries: dict[int, int] = {}
    for line_number, parts in iter_payload_parts(path):
        if parts[:2] == ["p", "aba"]:
            if atom_count is not None:
                raise ValueError("multiple p aba header lines")
            if len(parts) != 3 or not parts[2].isdigit():
                raise ValueError("p aba header must be: p aba <n>")
            atom_count = int(parts[2])
            continue
        if atom_count is None:
            raise ValueError("ICCMA ABA input must start with a p aba header")
        if parts[0] == "a" and len(parts) == 2:
            assumptions.add(validate_numeric_id(parts[1], atom_count, line_number, "ABA"))
            continue
        if parts[0] == "c" and len(parts) == 3:
            source = validate_numeric_id(parts[1], atom_count, line_number, "ABA")
            target = validate_numeric_id(parts[2], atom_count, line_number, "ABA")
            contraries[source] = target
            continue
        if parts[0] == "r" and len(parts) >= 2:
            rule_heads.add(validate_numeric_id(parts[1], atom_count, line_number, "ABA"))
            for item in parts[2:]:
                validate_numeric_id(item, atom_count, line_number, "ABA")
            rule_count += 1
            continue
        raise ValueError(f"invalid ABA line {line_number}: {' '.join(parts)!r}")
    if atom_count is None:
        raise ValueError("ICCMA ABA input must include a p aba header")
    assumption_heads = assumptions & rule_heads
    if assumption_heads:
        raise ValueError(f"flat ABA rule heads cannot be assumptions: {sorted(assumption_heads)}")
    if set(contraries) != assumptions:
        raise ValueError("ABA contrary map must define exactly one contrary per assumption")
    return atom_count, len(assumptions), rule_count, len(contraries)


def iter_payload_parts(path: Path):
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            yield line_number, line.split()


def validate_numeric_id(value: str, maximum: int, line_number: int, label: str) -> int:
    if not value.isdigit():
        raise ValueError(f"{label} line {line_number} must contain numeric ids")
    numeric = int(value)
    if numeric < 1 or numeric > maximum:
        raise ValueError(f"{label} line {line_number} references id outside 1..{maximum}")
    return numeric


def first_payload_line(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line and not line.startswith("#"):
                return line
    return ""


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, target.open("wb") as handle:
        shutil.copyfileobj(response, handle, length=1024 * 1024)


def verify_archive(path: Path, spec: ArchiveSpec) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    actual_size = path.stat().st_size
    if actual_size != spec.size:
        raise ValueError(f"{path} has size {actual_size}, expected {spec.size}")
    actual_md5 = file_md5(path)
    if actual_md5 != spec.md5:
        raise ValueError(f"{path} has md5 {actual_md5}, expected {spec.md5}")


def file_md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract_zip(archive_path: Path, target: Path) -> None:
    root = target.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            destination = (target / member.filename).resolve()
            if root not in (destination, *destination.parents):
                raise ValueError(f"refusing unsafe zip member: {member.filename}")
        archive.extractall(target)


def _selected_archives(selected: str) -> list[ArchiveSpec]:
    if selected == "all":
        return list(ARCHIVES.values())
    return [ARCHIVES[selected]]


if __name__ == "__main__":
    sys.exit(main())
