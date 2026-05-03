# ICCMA data (multi-year)

`tools/iccma_data.py` prepares ICCMA benchmark archives across multiple
editions. Older self-hosted archives on `argumentationcompetition.org` are
verified by file size only (those pages do not publish checksums).
Zenodo-hosted 2023 and 2025 archives are verified by size and MD5.

For 2025-specific workflows including the official task matrix and the
native runner, see [`iccma-2025-data.md`](iccma-2025-data.md).

## Covered editions

- **ICCMA 2015** — benchmark zip + updated result spreadsheet.
- **ICCMA 2017** — detailed result zip + benchmark groups A, B, C, D, T.
- **ICCMA 2019** — instance tarball.
- **ICCMA 2021** — instance tarball + exact and approximate result CSVs.
- **ICCMA 2023** — Zenodo benchmark and raw-result zips
  (Zenodo record `8348039`).
- **ICCMA 2025** — Zenodo instance and raw-result zips
  (Zenodo records `17949380`, `18506390`).

The 2021 instance archive is ~6.8 GB. Fetch it intentionally rather than
as a casual smoke test. Downloads stream into a `.part` sidecar and rename
on completion; existing files are re-verified rather than re-downloaded.

## Outputs

The tool writes deterministically into `data/iccma/<year>/`:

```
data/iccma/<year>/
├── archives/    # downloaded archive files (verified by size and MD5)
├── extracted/   # safe-extracted contents (refuses traversal-unsafe members)
└── manifests/   # JSON manifests classifying each extracted instance
```

Use `--root <path>` to override the cache root (default `data/iccma`).

## Commands

List known archive metadata:

```powershell
uv run tools\iccma_data.py --year all list
uv run tools\iccma_data.py --year 2023 list --json
```

Fetch one or more archives (omit the archive name to fetch all archives for
the year):

```powershell
uv run tools\iccma_data.py --year 2019 fetch instances
uv run tools\iccma_data.py --year 2017 fetch
```

Extract a fetched archive (`--force` overwrites existing extraction):

```powershell
uv run tools\iccma_data.py --year 2017 extract benchmarks-a
uv run tools\iccma_data.py --year 2023 extract --force
```

Build a manifest from already-extracted files:

```powershell
uv run tools\iccma_data.py --year 2025 manifest --strict
```

`--strict` exits with status `1` if any row has `parse_status == "error"`.
Useful for CI integration.

End-to-end (fetch + extract + manifest, also strict):

```powershell
uv run tools\iccma_data.py --year 2023 all
```

## Manifest classification

The manifest pass classifies and stream-validates:

| Kind | Detected |
|---|---|
| `af` | numeric `p af <n>` AF files |
| `aba` | numeric `p aba <n>` flat-ABA files |
| `apx` | APX files with `arg(...)` / `att(...)` |
| `tgf` | TGF files |
| `compressed_apx`, `compressed_tgf` | `.apx.lzma` / `.tgf.lzma` (streamed through `lzma.open`) |
| `query_or_updates` | `.arg`, `.query`, `.apxm`, `.tgfm`, `.asm`, `_arg.lzma`, `_query.lzma` (skipped) |
| `dynamic_app` | `.py` dynamic-track applications (classified, not run) |

`__MACOSX/` archive metadata, `.csv` / `.xlsx` / `.xls` / `.results`
support artifacts are skipped. The tool never runs solvers.

## See also

- [`iccma-2025-data.md`](iccma-2025-data.md) — 2025-specific tool with a
  `tasks` subcommand and the native runner.
- `tools/iccma_run_selected.py`, `tools/iccma_run_timeout_rows.py`,
  `tools/iccma_timeout_corpus.py`, `tools/iccma_trace_classify.py` —
  selected-instance runners and timeout/trace diagnostics.
