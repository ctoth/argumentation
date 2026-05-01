from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import lzma
from pathlib import Path
import re
import shutil
import sys
import tarfile
import urllib.request
import zipfile


DATA_ROOT = Path("data") / "iccma"


@dataclass(frozen=True)
class ArchiveSpec:
    name: str
    file_name: str
    url: str
    size: int
    extract_dir: str
    md5: str | None = None


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


ARCHIVES_BY_YEAR: dict[str, dict[str, ArchiveSpec]] = {
    "2015": {
        "instances": ArchiveSpec(
            name="instances",
            file_name="iccma2015_benchmarks.zip",
            url="https://argumentationcompetition.org/2015/iccma2015_benchmarks.zip",
            size=154_720_338,
            extract_dir="instances",
        ),
        "results": ArchiveSpec(
            name="results",
            file_name="results_iccma2015_upd1.xlsx",
            url="https://argumentationcompetition.org/2015/results_iccma2015_upd1.xlsx",
            size=3_068_714,
            extract_dir="results",
        ),
    },
    "2017": {
        "results": ArchiveSpec(
            name="results",
            file_name="results.zip",
            url="https://argumentationcompetition.org/2017/results.zip",
            size=756_444,
            extract_dir="results",
        ),
        "benchmarks-a": ArchiveSpec(
            name="benchmarks-a",
            file_name="A.tar.gz",
            url="https://argumentationcompetition.org/2017/A.tar.gz",
            size=643_678_352,
            extract_dir="instances/A",
        ),
        "benchmarks-b": ArchiveSpec(
            name="benchmarks-b",
            file_name="B.tar.gz",
            url="https://argumentationcompetition.org/2017/B.tar.gz",
            size=746_949_596,
            extract_dir="instances/B",
        ),
        "benchmarks-c": ArchiveSpec(
            name="benchmarks-c",
            file_name="C.tar.gz",
            url="https://argumentationcompetition.org/2017/C.tar.gz",
            size=897_186_894,
            extract_dir="instances/C",
        ),
        "benchmarks-d": ArchiveSpec(
            name="benchmarks-d",
            file_name="D.tar.gz",
            url="https://argumentationcompetition.org/2017/D.tar.gz",
            size=643_678_644,
            extract_dir="instances/D",
        ),
        "benchmarks-t": ArchiveSpec(
            name="benchmarks-t",
            file_name="T.tar.gz",
            url="https://argumentationcompetition.org/2017/T.tar.gz",
            size=661_640_038,
            extract_dir="instances/T",
        ),
    },
    "2019": {
        "instances": ArchiveSpec(
            name="instances",
            file_name="iccma-instances.tar.gz",
            url="https://argumentationcompetition.org/2019/iccma-instances.tar.gz",
            size=176_529_641,
            extract_dir="instances",
        ),
    },
    "2021": {
        "instances": ArchiveSpec(
            name="instances",
            file_name="instances.tar.gz",
            url="https://argumentationcompetition.org/2021/instances.tar.gz",
            size=6_793_022_603,
            extract_dir="instances",
        ),
        "results-exact": ArchiveSpec(
            name="results-exact",
            file_name="ICCMA_2021_exact_track.csv",
            url="https://argumentationcompetition.org/2021/ICCMA_2021_exact_track.csv",
            size=5_014_337,
            extract_dir="results",
        ),
        "results-approximate": ArchiveSpec(
            name="results-approximate",
            file_name="ICCMA_2021_approximate_track.csv",
            url="https://argumentationcompetition.org/2021/ICCMA_2021_approximate_track.csv",
            size=501_124,
            extract_dir="results",
        ),
    },
    "2023": {
        "instances": ArchiveSpec(
            name="instances",
            file_name="iccma2023_benchmarks.zip",
            url=(
                "https://zenodo.org/api/records/8348039/files/"
                "iccma2023_benchmarks.zip/content"
            ),
            size=851_774_875,
            md5="f7382a5d5b8118253a9266d5465b5bed",
            extract_dir="instances",
        ),
        "results": ArchiveSpec(
            name="results",
            file_name="iccma2023_results.zip",
            url=(
                "https://zenodo.org/api/records/8348039/files/"
                "iccma2023_results.zip/content"
            ),
            size=448_400_865,
            md5="bdb5e5008e7393f4b52cdb19f33012ec",
            extract_dir="results",
        ),
    },
    "2025": {
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
    },
}


APX_ARG_RE = re.compile(r"^arg\(([^(),\s]+)\)\.$")
APX_ATT_RE = re.compile(r"^att\(([^(),\s]+),([^(),\s]+)\)\.$")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare ICCMA benchmark data by year.")
    parser.add_argument("--root", type=Path, default=DATA_ROOT)
    parser.add_argument("--year", choices=[*ARCHIVES_BY_YEAR, "all"], required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--json", action="store_true")

    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("archive", nargs="?", default="all")

    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("archive", nargs="?", default="all")
    extract_parser.add_argument("--force", action="store_true")

    manifest_parser = subparsers.add_parser("manifest")
    manifest_parser.add_argument("--strict", action="store_true")

    subparsers.add_parser("all")
    args = parser.parse_args(argv)

    if args.command == "list":
        list_archives(args.root, args.year, json_output=args.json)
        return 0
    exit_code = 0
    for year in selected_years(args.year):
        year_root = args.root / year
        if args.command == "fetch":
            fetch_archives(year_root, archives_for_year(year), selected=args.archive)
        elif args.command == "extract":
            extract_archives(
                year_root,
                archives_for_year(year),
                selected=args.archive,
                force=args.force,
            )
        elif args.command == "manifest":
            rows = write_manifest(year_root, year)
            if args.strict and any(row.parse_status == "error" for row in rows):
                exit_code = 1
        elif args.command == "all":
            specs = archives_for_year(year)
            fetch_archives(year_root, specs, selected="all")
            extract_archives(year_root, specs, selected="all", force=False)
            rows = write_manifest(year_root, year)
            if any(row.parse_status == "error" for row in rows):
                exit_code = 1
    return exit_code


def list_archives(root: Path, year: str, *, json_output: bool) -> None:
    rows = [
        {"year": selected_year, **asdict(spec)}
        for selected_year in selected_years(year)
        for spec in archives_for_year(selected_year).values()
    ]
    if json_output:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return
    for row in rows:
        print(
            f"{row['year']} {row['name']}: {row['file_name']} "
            f"size={row['size']} md5={row['md5'] or 'unavailable'}"
        )


def fetch_archives(
    year_root: Path,
    specs: dict[str, ArchiveSpec],
    *,
    selected: str,
) -> None:
    archive_dir = year_root / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    for spec in selected_archives(specs, selected):
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


def extract_archives(
    year_root: Path,
    specs: dict[str, ArchiveSpec],
    *,
    selected: str,
    force: bool,
) -> None:
    archive_dir = year_root / "archives"
    extract_root = year_root / "extracted"
    extract_root.mkdir(parents=True, exist_ok=True)
    for spec in selected_archives(specs, selected):
        archive_path = archive_dir / spec.file_name
        verify_archive(archive_path, spec)
        target = extract_root / spec.extract_dir
        if is_plain_file_archive(archive_path):
            target.mkdir(parents=True, exist_ok=True)
            destination = target / archive_path.name
            if destination.exists() and not force:
                print(f"already extracted {destination}")
                continue
            if destination.exists() and force:
                destination.unlink()
            print(f"extracting {archive_path} -> {target}")
            safe_extract_archive(archive_path, target)
            continue
        if target.exists() and force:
            shutil.rmtree(target)
        if target.exists() and any(target.iterdir()):
            print(f"already extracted {target}")
            continue
        target.mkdir(parents=True, exist_ok=True)
        print(f"extracting {archive_path} -> {target}")
        safe_extract_archive(archive_path, target)


def write_manifest(year_root: Path, year: str) -> list[ManifestRow]:
    rows = build_manifest(year_root, archives_for_year(year))
    manifest_dir = year_root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_path = manifest_dir / f"iccma-{year}-manifest.json"
    csv_path = manifest_dir / f"iccma-{year}-manifest.csv"
    json_path.write_text(
        json.dumps([asdict(row) for row in rows], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(asdict(rows[0]).keys()) if rows else [field.name for field in ManifestRow.__dataclass_fields__.values()]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    errors = sum(1 for row in rows if row.parse_status == "error")
    print(f"wrote {json_path} and {csv_path}: {len(rows)} rows, {errors} errors")
    return rows


def build_manifest(
    year_root: Path,
    specs: dict[str, ArchiveSpec],
) -> list[ManifestRow]:
    rows: list[ManifestRow] = []
    extracted = year_root / "extracted"
    for spec in specs.values():
        base = extracted / spec.extract_dir
        if not base.exists():
            continue
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            relative = path.relative_to(base).as_posix()
            rows.append(classify_file(spec.name, relative, path))
    return rows


def classify_file(archive_name: str, relative: str, path: Path) -> ManifestRow:
    size = path.stat().st_size
    suffix = path.suffix.lower()
    name = path.name.lower()
    if path.name.startswith("._") or "__MACOSX/" in relative:
        return ManifestRow(archive_name, relative, "archive_metadata", "skipped", size)
    if archive_name.startswith("results") or suffix in {".csv", ".xlsx", ".xls", ".results"}:
        return ManifestRow(archive_name, relative, "results", "skipped", size)
    if (
        suffix in {".arg", ".query", ".apxm", ".tgfm", ".asm"}
        or name.endswith(("_arg.lzma", "_query.lzma"))
    ):
        return ManifestRow(archive_name, relative, "query_or_updates", "skipped", size)
    if name.endswith(".apx.lzma"):
        return ManifestRow(archive_name, relative, "compressed_apx", "skipped", size)
    if name.endswith(".tgf.lzma"):
        return ManifestRow(archive_name, relative, "compressed_tgf", "skipped", size)
    try:
        header = first_payload_line(path)
        if header.startswith("p af "):
            arguments, attacks = scan_numeric_af_file(path)
            return ManifestRow(archive_name, relative, "af", "ok", size, arguments, attacks)
        if header.startswith("p aba"):
            atoms, assumptions, rules, contraries = scan_numeric_aba_file(path)
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
        if looks_like_tgf(path, header):
            arguments, attacks = scan_tgf_file(path)
            return ManifestRow(archive_name, relative, "tgf", "ok", size, arguments, attacks)
        if looks_like_apx(path, header):
            arguments, attacks = scan_apx_file(path)
            return ManifestRow(archive_name, relative, "apx", "ok", size, arguments, attacks)
        if suffix == ".py":
            return ManifestRow(archive_name, relative, "dynamic_app", "skipped", size)
        return ManifestRow(archive_name, relative, "unknown", "skipped", size)
    except Exception as exc:
        return ManifestRow(archive_name, relative, "unknown", "error", size, error=str(exc))


def scan_numeric_af_file(path: Path) -> tuple[int, int]:
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


def scan_numeric_aba_file(path: Path) -> tuple[int, int, int, int]:
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


def scan_apx_file(path: Path) -> tuple[int, int]:
    arguments: set[str] = set()
    attacks = 0
    with open_text(path, errors="ignore") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith(("%", "#")):
                continue
            arg_match = APX_ARG_RE.match(line)
            if arg_match:
                arguments.add(arg_match.group(1))
                continue
            att_match = APX_ATT_RE.match(line)
            if att_match:
                arguments.add(att_match.group(1))
                arguments.add(att_match.group(2))
                attacks += 1
                continue
            raise ValueError(f"invalid APX line {line_number}: {line!r}")
    return len(arguments), attacks


def scan_tgf_file(path: Path) -> tuple[int, int]:
    arguments: set[str] = set()
    attacks = 0
    in_attacks = False
    with open_text(path, errors="ignore") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            if line == "#":
                in_attacks = True
                continue
            if not in_attacks:
                arguments.add(line.split(maxsplit=1)[0])
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f"invalid TGF attack line {line_number}: {line!r}")
            arguments.add(parts[0])
            arguments.add(parts[1])
            attacks += 1
    if not in_attacks:
        raise ValueError("TGF input must contain # separator")
    return len(arguments), attacks


def looks_like_apx(path: Path, header: str) -> bool:
    name = path.name.lower()
    return (
        path.suffix.lower() == ".apx"
        or name.endswith(".apx.lzma")
        or bool(APX_ARG_RE.match(header) or APX_ATT_RE.match(header))
    )


def looks_like_tgf(path: Path, header: str) -> bool:
    name = path.name.lower()
    return path.suffix.lower() == ".tgf" or name.endswith(".tgf.lzma") or header == "#" or header.isdigit()


def iter_payload_parts(path: Path):
    with open_text(path, errors="strict") as handle:
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
    with open_text(path, errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line and not line.startswith(("%", "#")):
                return line
    return ""


def open_text(path: Path, *, errors: str):
    if path.name.lower().endswith(".lzma"):
        return lzma.open(path, mode="rt", encoding="utf-8", errors=errors)
    return path.open("r", encoding="utf-8", errors=errors)


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
    if spec.md5 is None:
        return
    actual_md5 = file_md5(path)
    if actual_md5 != spec.md5:
        raise ValueError(f"{path} has md5 {actual_md5}, expected {spec.md5}")


def file_md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract_archive(archive_path: Path, target: Path) -> None:
    if archive_path.suffix.lower() == ".zip":
        safe_extract_zip(archive_path, target)
        return
    if archive_path.name.endswith((".tar.gz", ".tgz")):
        safe_extract_tar(archive_path, target)
        return
    shutil.copy2(archive_path, target / archive_path.name)


def is_plain_file_archive(path: Path) -> bool:
    return not (path.suffix.lower() == ".zip" or path.name.endswith((".tar.gz", ".tgz")))


def safe_extract_zip(archive_path: Path, target: Path) -> None:
    root = target.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            destination = (target / member.filename).resolve()
            if root not in (destination, *destination.parents):
                raise ValueError(f"refusing unsafe zip member: {member.filename}")
        archive.extractall(target)


def safe_extract_tar(archive_path: Path, target: Path) -> None:
    root = target.resolve()
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive.getmembers():
            destination = (target / member.name).resolve()
            if root not in (destination, *destination.parents):
                raise ValueError(f"refusing unsafe tar member: {member.name}")
        archive.extractall(target, filter="data")


def selected_archives(specs: dict[str, ArchiveSpec], selected: str) -> list[ArchiveSpec]:
    if selected == "all":
        return list(specs.values())
    if selected not in specs:
        valid = ", ".join([*specs, "all"])
        raise ValueError(f"unknown archive {selected!r}; expected one of: {valid}")
    return [specs[selected]]


def selected_years(year: str) -> list[str]:
    if year == "all":
        return list(ARCHIVES_BY_YEAR)
    return [year]


def archives_for_year(year: str) -> dict[str, ArchiveSpec]:
    return ARCHIVES_BY_YEAR[year]


if __name__ == "__main__":
    sys.exit(main())
